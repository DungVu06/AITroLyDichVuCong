"""Kiểm tra citation và các ràng buộc an toàn của câu trả lời."""

from __future__ import annotations

import re

from rag.core.schemas import AnswerValidationResult, RAGResponse, ValidationIssue


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
                severity="error",
                message="Dòng chứa claim hoặc số liệu nhưng không có citation.",
                excerpt=excerpt,
            )
        )
    return issues


def validate_answer(response: RAGResponse) -> AnswerValidationResult:
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
                severity="error",
                message="Câu trả lời không có citation.",
            )
        )

    for procedure_id in missing_procedures:
        issues.append(
            ValidationIssue(
                code="missing_procedure_citation",
                severity="error",
                message=f"Thiếu citation cho thủ tục {procedure_id}.",
                excerpt=procedure_id,
            )
        )

    if response.benefits and not any(value.startswith("LAW_") for value in cited_ids):
        issues.append(
            ValidationIssue(
                code="missing_legal_citation",
                severity="error",
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
