"""Gom và rút gọn evidence thành context có cấu trúc cho LLM."""

from __future__ import annotations

from collections import defaultdict

from rag.core.schemas import (
    AnswerContext,
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
    "document_item": 3,
    "step_item": 2,
    "execution_methods": 1,
    "note_item": 1,
}


def _shorten_chunk(chunk: RetrievedChunk, max_chars: int = 1_500) -> RetrievedChunk:
    text = chunk.text.strip()
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "…"
    return chunk.model_copy(update={"text": text})


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
        if not (item.text or "").strip():
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
        response_rules=response_rules or ResponseRules(),
    )
