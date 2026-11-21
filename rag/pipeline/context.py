"""Gom và rút gọn evidence thành context có cấu trúc cho LLM."""

from __future__ import annotations

from collections import defaultdict

from rag.core.schemas import (
    AnswerContext,
    AnswerContract,
    BenefitEvidence,
    JourneyItem,
    LegalEvidence,
    ProcedureEvidence,
    QueryState,
    ResponseRules,
    RetrievedChunk,
    UserQuery,
)


PROCEDURE_CHUNK_LIMITS = {
    "document_item": 4,
    "step_item": 8,
    # A split execution section can keep the authority in one chunk and the
    # time limit in the next. Retaining three preserves that pair while still
    # bounding the prompt.
    "execution_methods": 3,
    "eligibility": 3,
    "note_item": 2,
}


def derive_decision_questions(
    query: UserQuery,
    procedures: list[ProcedureEvidence],
) -> list[str]:
    """Ask only for facts that select a conditional path in retrieved evidence."""
    user_text = query.text.casefold()
    evidence = "\n".join(
        chunk.text.casefold()
        for procedure in procedures
        for chunk in procedure.chunks
    )
    rules = (
        (
            ("người làm chứng", "giấy cam đoan"),
            ("người làm chứng",),
            "Khi sinh tại nhà, có người làm chứng có thể xác nhận việc sinh không?",
        ),
        (
            ("công chứng hoặc chứng thực",),
            ("công chứng", "chứng thực"),
            "Hợp đồng thuê, mượn hoặc ở nhờ đã được công chứng hoặc chứng thực chưa?",
        ),
        (
            ("ý kiến đồng ý", "chủ sở hữu"),
            ("chủ sở hữu đồng ý", "chủ nhà đồng ý", "ý kiến đồng ý"),
            "Chủ sở hữu chỗ ở hợp pháp đã đồng ý bằng văn bản cho đăng ký thường trú chưa?",
        ),
    )
    questions = [
        question
        for triggers, known_markers, question in rules
        if all(trigger in evidence for trigger in triggers)
        and not any(marker in user_text for marker in known_markers)
    ]
    return list(dict.fromkeys(questions))[:3]


def _shorten_chunk(chunk: RetrievedChunk, max_chars: int = 1_500) -> RetrievedChunk:
    text = chunk.text.strip()
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "…"
    return chunk.model_copy(update={"text": text, "metadata": {}})


def _compact_procedure(procedure: ProcedureEvidence) -> ProcedureEvidence:
    counts: dict[str, int] = defaultdict(int)
    chunks = []
    for chunk in procedure.chunks:
        chunk_type = chunk.chunk_type or ""
        limit = PROCEDURE_CHUNK_LIMITS.get(chunk_type, 0)
        if counts[chunk_type] >= limit:
            continue
        chunks.append(_shorten_chunk(chunk))
        counts[chunk_type] += 1
    return procedure.model_copy(update={"chunks": chunks})


def _compact_benefit(
    benefit: BenefitEvidence,
    per_law_limit: int = 4,
) -> BenefitEvidence:
    counts: dict[str, int] = defaultdict(int)
    evidence = []
    for item in benefit.legal_evidence:
        if not (item.text or "").strip() and not item.validity:
            continue
        if counts[item.law_id] >= per_law_limit:
            continue
        evidence.append(item)
        counts[item.law_id] += 1
    return benefit.model_copy(update={"legal_evidence": evidence})


def build_answer_context(
    *,
    query: UserQuery,
    query_state: QueryState,
    journey: list[JourneyItem],
    procedure_evidence: list[ProcedureEvidence],
    benefits: list[BenefitEvidence],
    legal_evidence: list[LegalEvidence] | None = None,
    response_rules: ResponseRules | None = None,
    contract: AnswerContract | None = None,
) -> AnswerContext:
    """Build the only structured payload passed to answer generation."""
    journey_order = {item.procedure_id: index for index, item in enumerate(journey)}
    compact_procedures = [_compact_procedure(item) for item in procedure_evidence]
    compact_procedures.sort(
        key=lambda item: journey_order.get(item.procedure_id, len(journey_order))
    )

    return AnswerContext(
        query=query,
        query_state=query_state,
        journey=journey,
        procedure_evidence=compact_procedures,
        benefits=[_compact_benefit(item) for item in benefits],
        legal_evidence=legal_evidence or [],
        required_follow_up_questions=list(dict.fromkeys([
            *((contract or AnswerContract()).required_follow_up_questions),
            *derive_decision_questions(query, compact_procedures),
        ]))[:3],
        contract=contract or AnswerContract(),
        response_rules=response_rules or ResponseRules(),
    )
