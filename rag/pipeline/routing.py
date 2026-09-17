"""Bước 4: chọn chiến lược truy xuất dựa trên intent và query state."""

from __future__ import annotations

from rag.core.schemas import (
    Intent,
    PreprocessedQuery,
    QueryState,
    RetrievalPlan,
    RetrievalStrategy,
)


ALL_PROCEDURE_CHUNK_TYPES = [
    "document_item",
    "step_item",
    "execution_methods",
    "note_item",
]

TOPIC_TO_CHUNK_TYPE = {
    "documents": "document_item",
    "steps": "step_item",
    "fees": "execution_methods",
    "processing_time": "execution_methods",
    "online_method": "execution_methods",
    "execution_methods": "execution_methods",
    "notes": "note_item",
}


def procedure_chunk_types(topics: list[str]) -> list[str]:
    """Đổi topic tổng quát thành loại chunk thực tế trong Qdrant."""
    selected = [
        TOPIC_TO_CHUNK_TYPE[topic]
        for topic in topics
        if topic in TOPIC_TO_CHUNK_TYPE
    ]
    return list(dict.fromkeys(selected)) or list(ALL_PROCEDURE_CHUNK_TYPES)


def route_query(query: PreprocessedQuery, state: QueryState) -> RetrievalPlan:
    """Tạo retrieval plan bằng quy tắc, không gọi thêm LLM."""
    intent = state.intent

    # Bảo vệ trường hợp LLM nhận ra sự kiện nhưng để intent là unknown.
    if intent == Intent.UNKNOWN and state.life_event:
        intent = Intent.PROCEDURE_JOURNEY

    base_filters = {"life_event": state.life_event} if state.life_event else {}
    needs_clarification = bool(state.missing_facts)
    retrieval_query = " ".join(
        value
        for value in (
            query.normalized_text,
            state.target,
            state.life_event.replace("_", " ") if state.life_event else None,
        )
        if value
    )

    if intent == Intent.OUT_OF_SCOPE:
        return RetrievalPlan(
            strategy=RetrievalStrategy.OUT_OF_SCOPE,
            needs_clarification=False,
        )

    if intent == Intent.UNKNOWN:
        return RetrievalPlan(
            strategy=RetrievalStrategy.CLARIFICATION,
            needs_clarification=True,
        )

    if intent == Intent.PROCEDURE_JOURNEY:
        return RetrievalPlan(
            strategy=RetrievalStrategy.JOURNEY_FIRST,
            procedure_query=retrieval_query,
            procedure_chunk_types=procedure_chunk_types(state.topics),
            qdrant_filters=base_filters,
            use_procedure_vector_search=True,
            use_graph_traversal=True,
            include_benefits=True,
            include_legal_evidence=True,
            use_law_vector_search=False,
            needs_clarification=needs_clarification,
        )

    if intent == Intent.PROCEDURE_DETAIL:
        include_benefits = "benefits" in state.topics
        return RetrievalPlan(
            strategy=RetrievalStrategy.PROCEDURE_DETAIL,
            procedure_query=retrieval_query,
            procedure_chunk_types=procedure_chunk_types(state.topics),
            qdrant_filters=base_filters,
            use_procedure_vector_search=True,
            use_graph_traversal=include_benefits,
            include_benefits=include_benefits,
            include_legal_evidence=include_benefits,
            use_law_vector_search=False,
            needs_clarification=needs_clarification,
        )

    if intent == Intent.NEXT_STEP:
        return RetrievalPlan(
            strategy=RetrievalStrategy.GRAPH_NEXT_STEPS,
            procedure_query=retrieval_query,
            procedure_chunk_types=procedure_chunk_types(state.topics),
            qdrant_filters=base_filters,
            use_procedure_vector_search=True,
            use_graph_traversal=True,
            needs_clarification=needs_clarification,
        )

    if intent == Intent.BENEFIT_CHECK:
        return RetrievalPlan(
            strategy=RetrievalStrategy.BENEFIT_FIRST,
            procedure_query=retrieval_query,
            procedure_chunk_types=procedure_chunk_types(state.topics),
            qdrant_filters=base_filters,
            use_procedure_vector_search=True,
            use_graph_traversal=True,
            include_benefits=True,
            include_legal_evidence=True,
            use_law_vector_search=False,
            needs_clarification=needs_clarification,
        )

    if intent == Intent.ELIGIBILITY_CHECK:
        include_benefits = "benefits" in state.topics
        return RetrievalPlan(
            strategy=RetrievalStrategy.PROCEDURE_DETAIL,
            procedure_query=retrieval_query,
            procedure_chunk_types=procedure_chunk_types(state.topics),
            qdrant_filters=base_filters,
            use_procedure_vector_search=True,
            use_graph_traversal=True,
            include_benefits=include_benefits,
            include_legal_evidence=include_benefits,
            use_law_vector_search=False,
            needs_clarification=needs_clarification,
        )

    return RetrievalPlan(
        strategy=RetrievalStrategy.LAW_SEARCH,
        law_query=retrieval_query,
        qdrant_filters=base_filters,
        include_legal_evidence=True,
        use_law_vector_search=True,
        needs_clarification=needs_clarification,
    )


