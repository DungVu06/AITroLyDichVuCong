"""Kiểm tra citation và các ràng buộc an toàn của câu trả lời."""

from __future__ import annotations

import re

from rag.core.schemas import AnswerContext, AnswerValidationResult, RAGResponse, ValidationIssue


CITATION_PATTERN = re.compile(r"【([^】]+)】")
QUANTITATIVE_PATTERN = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:ngày|tháng|năm|VNĐ|lần|bản|tuổi)\b"
    r"|ngày làm việc|miễn phí|bản chính|bản sao",
    re.IGNORECASE,
)
LEGAL_CLAIM_PATTERN = re.compile(
    r"theo quy định|có trách nhiệm|\bphải\b|được hưởng|trợ cấp",
    re.IGNORECASE,
)
UNCERTAINTY_TERMS = (
    "có thể",
    "chưa đủ dữ kiện",
    "chưa xác định",
    "không thể kết luận",
    "chưa thể kết luận",
)
TECHNICAL_TERMS = ("vector", "graph", "chunk", "rag", "answer_context")


def _uncited_claim_issues(answer: str) -> list[ValidationIssue]:
    issues = []
    seen = set()
    for raw_line in answer.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or CITATION_PATTERN.search(line):
            continue
        claim_text = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", line)
        claim_text = re.sub(r"`[^`]+`", "", claim_text)
        if not (
            QUANTITATIVE_PATTERN.search(claim_text)
            or LEGAL_CLAIM_PATTERN.search(claim_text)
        ):
            continue
        excerpt = line[:240]
        if excerpt in seen:
            continue
        seen.add(excerpt)
        issues.append(
            ValidationIssue(
                code="uncited_claim",
                severity="warning",
                message="Dòng chứa claim hoặc số liệu nhưng không có citation.",
                excerpt=excerpt,
            )
        )
    return issues


def validate_answer(response: RAGResponse, context: AnswerContext | None = None) -> AnswerValidationResult:
    answer = response.answer_markdown
    cited_ids = list(dict.fromkeys(CITATION_PATTERN.findall(answer)))
    allowed_ids = {source.source_id for source in response.sources}
    unknown_ids = sorted(set(cited_ids) - allowed_ids)
    missing_procedures = sorted(
        item.procedure_id
        for item in response.journey
        if item.procedure_id not in cited_ids
    )
    issues = _uncited_claim_issues(answer)

    if context:
        topic_types = {"steps": "step_item", "documents": "document_item",
                       "processing_time": "execution_methods", "fees": "execution_methods"}
        requested = set(context.query_state.procedure_ids)
        topics = context.query_state.topics
        # Contract requirements below are claim-level checks. Do not trigger a
        # fallback just because query understanding supplied a broad topic
        # label whose entire chunk category was not cited.
        if not context.contract.requirements:
            for procedure in context.procedure_evidence:
                if procedure.procedure_id not in requested:
                    continue
                for kind in {topic_types[t] for t in topics if t in topic_types}:
                    candidates = {c.chunk_id for c in procedure.chunks if c.chunk_type == kind}
                    if candidates and candidates.isdisjoint(cited_ids):
                        issues.append(ValidationIssue(
                            code="missing_requested_evidence", severity="warning",
                            message=f"Chưa trích nguồn {kind} cho {procedure.name}.",
                        ))

        for requirement in context.contract.requirements:
            if requirement.relation_type:
                candidates = {
                    relation.citation_id
                    for relation in context.relation_evidence
                    if relation.source_id == requirement.procedure_id
                    and relation.relationship_type == requirement.relation_type
                    and (requirement.target_procedure_id is None
                         or relation.target_id == requirement.target_procedure_id)
                }
            else:
                candidates = {
                    chunk.chunk_id
                    for procedure in context.procedure_evidence
                    for chunk in procedure.chunks
                    if chunk.chunk_id
                    and procedure.procedure_id == requirement.procedure_id
                    and chunk.chunk_type == requirement.chunk_type
                    and (requirement.step_number is None or chunk.step_number == requirement.step_number)
                    and not any(term.casefold() in chunk.text.casefold()
                                for term in requirement.excluded_terms)
                    and all(term.casefold() in chunk.text.casefold()
                            for term in requirement.required_terms)
                }
            if candidates and candidates.isdisjoint(cited_ids):
                issues.append(ValidationIssue(
                    code="missing_contract_evidence",
                    severity="warning",
                    message=(
                        f"Thiếu evidence bắt buộc cho: {requirement.label}."
                    ),
                    excerpt=requirement.claim_id,
                ))
            elif not candidates:
                issues.append(ValidationIssue(
                    code="unavailable_contract_evidence",
                    severity="warning",
                    message=(
                        f"Không truy xuất được evidence bắt buộc cho: {requirement.label}."
                    ),
                    excerpt=requirement.claim_id,
                ))

        for procedure_id, expected_steps in context.contract.required_step_numbers.items():
            for step_number in expected_steps:
                candidates = {
                    chunk.chunk_id
                    for procedure in context.procedure_evidence
                    for chunk in procedure.chunks
                    if procedure.procedure_id == procedure_id
                    and chunk.chunk_type == "step_item"
                    and chunk.step_number == step_number
                    and chunk.chunk_id
                }
                if not candidates:
                    issues.append(ValidationIssue(
                        code="missing_step_evidence",
                        severity="error",
                        message=(f"Thiếu evidence cho bước {step_number} của {procedure_id}."),
                    ))
                elif candidates.isdisjoint(cited_ids):
                    issues.append(ValidationIssue(
                        code="missing_step_citation",
                        severity="warning",
                        message=(f"Câu trả lời chưa nêu bước {step_number} của {procedure_id}."),
                    ))

    for source_id in unknown_ids:
        issues.append(
            ValidationIssue(
                code="unknown_citation",
                severity="error",
                message=f"Citation không tồn tại trong sources: {source_id}",
                excerpt=source_id,
            )
        )

    if response.sources and not cited_ids:
        issues.append(
            ValidationIssue(
                code="missing_citations",
                severity="warning",
                message="Câu trả lời không có citation.",
            )
        )

    for procedure_id in missing_procedures:
        issues.append(
            ValidationIssue(
                code="missing_procedure_citation",
                severity="warning",
                message=f"Thiếu citation cho thủ tục {procedure_id}.",
                excerpt=procedure_id,
            )
        )

    if any(b.legal_evidence for b in response.benefits) and not any(value.startswith("LAW_") for value in cited_ids):
        issues.append(
            ValidationIssue(
                code="missing_legal_citation",
                severity="warning",
                message="Có quyền lợi nhưng không trích dẫn section pháp luật.",
            )
        )

    has_unknown_benefit = any(
        benefit.eligibility_status in {"unknown", "possibly_eligible"}
        for benefit in response.benefits
    )
    if has_unknown_benefit and not any(term in answer.casefold() for term in UNCERTAINTY_TERMS):
        issues.append(
            ValidationIssue(
                code="missing_benefit_uncertainty",
                severity="error",
                message="Quyền lợi chưa xác định nhưng câu trả lời không nêu sự không chắc chắn.",
            )
        )

    needs_validity_warning = any(
        "trạng thái hiệu lực" in warning.casefold() for warning in response.warnings
    )
    if needs_validity_warning and "hiệu lực" not in answer.casefold():
        issues.append(
            ValidationIssue(
                code="missing_legal_validity_warning",
                severity="error",
                message="Câu trả lời chưa hiển thị cảnh báo thiếu trạng thái hiệu lực luật.",
            )
        )

    for term in TECHNICAL_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", answer, re.IGNORECASE):
            issues.append(
                ValidationIssue(
                    code="technical_term_exposed",
                    severity="warning",
                    message=f"Câu trả lời hiển thị thuật ngữ kỹ thuật: {term}",
                    excerpt=term,
                )
            )

    return AnswerValidationResult(
        is_valid=not any(issue.severity == "error" for issue in issues),
        issues=issues,
        cited_source_ids=cited_ids,
        unknown_citation_ids=unknown_ids,
        missing_procedure_citations=missing_procedures,
    )


def repair_procedure_citations(
    response: RAGResponse,
    validation: AnswerValidationResult,
) -> RAGResponse:
    """Sửa claim thiếu nguồn khi section hiện tại xác định rõ procedure ID."""
    uncited_excerpts = {
        issue.excerpt
        for issue in validation.issues
        if issue.code == "uncited_claim" and issue.excerpt
    }
    procedure_ids = {item.procedure_id for item in response.journey}
    current_procedure_id: str | None = None
    repaired_lines = []

    for line in response.answer_markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            found_ids = [
                procedure_id
                for procedure_id in procedure_ids
                if procedure_id in stripped
            ]
            current_procedure_id = found_ids[0] if found_ids else None

        is_flagged = any(stripped.startswith(excerpt) for excerpt in uncited_excerpts)
        if (
            is_flagged
            and current_procedure_id
            and not CITATION_PATTERN.search(stripped)
        ):
            line = f"{line} 【{current_procedure_id}】"
        repaired_lines.append(line)

    markdown = "\n".join(repaired_lines)
    if any(
        issue.code == "missing_legal_validity_warning"
        for issue in validation.issues
    ):
        markdown += (
            "\n\n> **Lưu ý:** Dữ liệu nguồn chưa cung cấp trạng thái hiệu lực "
            "của một số văn bản pháp luật."
        )
    return response.model_copy(update={"answer_markdown": markdown})
