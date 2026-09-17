"""Gọi Gemini để diễn đạt câu trả lời từ AnswerContext đã kiểm soát."""

from __future__ import annotations

import re
from pathlib import Path

from rag.core.config import GeminiSettings
from rag.core.schemas import (
    AnswerContext,
    AnswerDraft,
    AnswerRepairDraft,
    AnswerValidationResult,
    BenefitEvidence,
    EligibilityStatus,
    RAGResponse,
    SourceReference,
)


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "answer_generation.md"


def build_answer_prompt(context: AnswerContext) -> str:
    instructions = PROMPT_PATH.read_text(encoding="utf-8").strip()
    context_json = context.model_dump_json(indent=2, exclude_none=True)
    return f"{instructions}\n\nANSWER_CONTEXT:\n{context_json}"


def _collect_sources(context: AnswerContext) -> list[SourceReference]:
    sources: dict[tuple[str, str], SourceReference] = {}
    for procedure in context.procedure_evidence:
        key = ("procedure", procedure.procedure_id)
        sources[key] = SourceReference(
            source_type="procedure",
            source_id=procedure.procedure_id,
            title=procedure.name,
            url=procedure.source_url,
        )
        for chunk in procedure.chunks:
            if not chunk.chunk_id:
                continue
            chunk_key = ("procedure_chunk", chunk.chunk_id)
            sources[chunk_key] = SourceReference(
                source_type="procedure_chunk",
                source_id=chunk.chunk_id,
                title=f"{procedure.name} – {chunk.chunk_type or 'chi tiết'}",
                url=procedure.source_url,
            )

    legal_items = list(context.legal_evidence)
    for benefit in context.benefits:
        legal_items.extend(benefit.legal_evidence)
    for item in legal_items:
        key = ("law_section", item.section_id)
        sources[key] = SourceReference(
            source_type="law_section",
            source_id=item.section_id,
            title=item.heading or item.law_title or item.section_id,
            url=item.source_url,
        )
    return list(sources.values())


def _build_warnings(
    context: AnswerContext,
    benefits: list[BenefitEvidence],
) -> list[str]:
    legal_items = list(context.legal_evidence)
    for benefit in benefits:
        legal_items.extend(benefit.legal_evidence)

    warnings = []
    if legal_items and any(not (item.validity or "").strip() for item in legal_items):
        warnings.append(
            "Dữ liệu nguồn chưa cung cấp trạng thái hiệu lực của một số văn bản pháp luật."
        )
    if any(benefit.eligibility_status == "unknown" for benefit in benefits):
        warnings.append("Chưa đủ dữ kiện để kết luận điều kiện hưởng quyền lợi.")
    return warnings


def _apply_benefit_assessments(
    context: AnswerContext,
    draft: AnswerDraft,
) -> tuple[list[BenefitEvidence], list[str]]:
    assessments = {
        item.title.casefold().strip(): item for item in draft.benefit_assessments
    }
    questions = list(draft.follow_up_questions)
    benefits = []

    for benefit in context.benefits:
        assessment = assessments.get(benefit.title.casefold().strip())
        updated = benefit
        if assessment:
            status = assessment.eligibility_status
            missing_validity = any(
                not (item.validity or "").strip()
                for item in benefit.legal_evidence
            )
            reason = assessment.reason
            if missing_validity and status == EligibilityStatus.ELIGIBLE:
                status = EligibilityStatus.POSSIBLY_ELIGIBLE
                reason += " Chưa thể kết luận chắc chắn vì thiếu trạng thái hiệu lực văn bản."
            elif missing_validity and status == EligibilityStatus.NOT_ELIGIBLE:
                status = EligibilityStatus.UNKNOWN
                reason += " Chưa thể loại trừ quyền lợi vì thiếu trạng thái hiệu lực văn bản."
            updated = benefit.model_copy(
                update={
                    "eligibility_status": status,
                    "reason": reason,
                    "missing_facts": assessment.missing_facts,
                }
            )
            questions.extend(assessment.follow_up_questions)

        if updated.eligibility_status in {
            EligibilityStatus.UNKNOWN,
            EligibilityStatus.POSSIBLY_ELIGIBLE,
        } and not questions:
            if updated.missing_facts:
                for fact in updated.missing_facts:
                    readable = fact.replace("_", " ")
                    questions.append(f"Bạn có thể cho biết thêm về {readable} không?")
            else:
                questions.append(
                    f"Bạn có thể cung cấp thêm thông tin để kiểm tra điều kiện "
                    f"hưởng {updated.title} không?"
                )
        benefits.append(updated)

    return benefits, list(dict.fromkeys(questions))[:3]


def _ensure_procedure_citations(markdown: str, context: AnswerContext) -> str:
    """Gắn citation xác định nếu model chỉ hiển thị procedure ID dạng code."""
    result = markdown
    for item in context.journey:
        citation = f"【{item.procedure_id}】"
        if citation in result:
            continue
        code_id = f"`{item.procedure_id}`"
        if code_id in result:
            result = result.replace(code_id, f"{code_id} {citation}", 1)
            continue
        result = re.sub(
            re.escape(item.name),
            lambda match: f"{match.group(0)} {citation}",
            result,
            count=1,
        )
    return result


def _normalize_citations(markdown: str) -> str:
    """Tách trường hợp model gộp nhiều source ID trong một cặp ngoặc."""
    def replace_combined(match: re.Match[str]) -> str:
        source_ids = [value.strip() for value in match.group(1).split(",")]
        return "".join(f"【{value}】" for value in source_ids if value)

    return re.sub(r"【([^】]*,[^】]*)】", replace_combined, markdown)


def generate_answer(
    context: AnswerContext,
    settings: GeminiSettings | None = None,
) -> RAGResponse:
    try:
        from google import genai
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Thiếu google-genai. Hãy cài bằng: pip install google-genai"
        ) from exc

    active_settings = settings or GeminiSettings.from_env()
    client = genai.Client(api_key=active_settings.api_key)
    interaction = client.interactions.create(
        model=active_settings.model,
        input=build_answer_prompt(context),
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": AnswerDraft.model_json_schema(),
        },
    )
    if not interaction.output_text:
        raise RuntimeError("Gemini không trả về câu trả lời.")
    draft = AnswerDraft.model_validate_json(interaction.output_text)
    answer_markdown = _ensure_procedure_citations(draft.answer_markdown, context)
    answer_markdown = _normalize_citations(answer_markdown)
    benefits, follow_up_questions = _apply_benefit_assessments(context, draft)
    return RAGResponse(
        answer_markdown=answer_markdown,
        journey=context.journey,
        benefits=benefits,
        follow_up_questions=follow_up_questions,
        sources=_collect_sources(context),
        warnings=_build_warnings(context, benefits),
    )


def repair_answer_with_gemini(
    response: RAGResponse,
    validation: AnswerValidationResult,
    context: AnswerContext,
    settings: GeminiSettings | None = None,
) -> RAGResponse:
    """Gọi repair tối đa một lần khi Python không thể sửa chắc chắn."""
    try:
        from google import genai
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Thiếu google-genai. Hãy cài bằng: pip install google-genai"
        ) from exc

    instructions = (
        PROMPT_PATH.parent / "answer_repair.md"
    ).read_text(encoding="utf-8").strip()
    prompt = (
        f"{instructions}\n\n"
        f"VALIDATION_ISSUES:\n{validation.model_dump_json(indent=2)}\n\n"
        f"ORIGINAL_ANSWER:\n{response.answer_markdown}\n\n"
        f"ANSWER_CONTEXT:\n{context.model_dump_json(indent=2, exclude_none=True)}"
    )
    active_settings = settings or GeminiSettings.from_env()
    client = genai.Client(api_key=active_settings.api_key)
    interaction = client.interactions.create(
        model=active_settings.model,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": AnswerRepairDraft.model_json_schema(),
        },
    )
    if not interaction.output_text:
        return response
    draft = AnswerRepairDraft.model_validate_json(interaction.output_text)
    markdown = _ensure_procedure_citations(draft.answer_markdown, context)
    markdown = _normalize_citations(markdown)
    return response.model_copy(update={"answer_markdown": markdown})
