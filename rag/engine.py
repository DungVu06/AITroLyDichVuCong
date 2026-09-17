"""Điều phối pipeline RAG hoàn chỉnh từ câu hỏi đến response cho UI."""

from __future__ import annotations

import argparse
import json
import sys
import uuid

from db.neo4j_client import Neo4jClient
from db.qdrant_client import QdrantVectorClient
from rag.pipeline.benefits import resolve_benefits
from rag.pipeline.context import build_answer_context
from rag.core.conversation import InMemoryConversationStore
from rag.generation.answer import generate_answer, repair_answer_with_gemini
from rag.generation.validator import repair_procedure_citations, validate_answer
from rag.pipeline.journey import build_journey
from rag.pipeline.preprocessing import preprocess_query
from rag.pipeline.query_understanding import understand_query
from rag.retrieval.graph import GraphRetriever
from rag.retrieval.embedding import QueryEmbedder
from rag.retrieval.vector import VectorRetriever
from rag.pipeline.routing import route_query
from rag.core.schemas import (
    AnswerContext,
    ConversationState,
    QueryState,
    RAGResponse,
    ResponseRules,
    RetrievalStrategy,
    UserQuery,
)


def build_context(
    text: str,
    *,
    conversation_id: str | None = None,
    limit: int = 5,
    previous_state: QueryState | None = None,
    pending_questions: list[str] | None = None,
    embedder: QueryEmbedder | None = None,
) -> AnswerContext:
    user_query = UserQuery(text=text, conversation_id=conversation_id)
    query = preprocess_query(user_query)
    state = understand_query(
        query,
        previous_state=previous_state,
        pending_questions=pending_questions,
    )
    plan = route_query(query, state)

    with QdrantVectorClient.from_env() as qdrant:
        retriever = VectorRetriever(qdrant, embedder=embedder)
        vector_result = retriever.retrieve_from_plan(
            plan,
            procedure_limit=limit,
            law_limit=limit,
        )
        seed_ids = list(
            dict.fromkeys(chunk.doc_id for chunk in vector_result["procedures"])
        )
        if plan.strategy in {
            RetrievalStrategy.PROCEDURE_DETAIL,
            RetrievalStrategy.GRAPH_NEXT_STEPS,
        }:
            seed_ids = seed_ids[:1]

        with Neo4jClient.from_env() as neo4j:
            graph_retriever = GraphRetriever(neo4j)
            if plan.use_graph_traversal:
                graph = graph_retriever.retrieve(
                    seed_ids,
                    include_benefits=plan.include_benefits,
                )
            else:
                graph = graph_retriever.retrieve_procedure_nodes(seed_ids)
            legal_evidence = graph_retriever.retrieve_law_evidence(
                vector_result["laws"]
            )

        journey = build_journey(
            graph,
            seed_ids,
            completed_procedure_ids=(
                seed_ids if state.intent.value == "next_step" else []
            ),
        )
        journey_ids = {item.procedure_id for item in journey}
        procedures = retriever.retrieve_procedure_details(
            [item for item in graph.procedures if item.procedure_id in journey_ids],
            query=plan.procedure_query or query.normalized_text,
            chunk_types=plan.procedure_chunk_types,
            per_type_limit=3,
        )

    return build_answer_context(
        query=user_query,
        query_state=state,
        journey=journey,
        procedure_evidence=procedures,
        benefits=resolve_benefits(graph),
        legal_evidence=legal_evidence,
        response_rules=ResponseRules(
            demo_scope="Demo sự kiện sinh con; trạng thái hiệu lực luật có thể thiếu."
        ),
    )


def _fallback_response(response: RAGResponse) -> RAGResponse:
    lines = ["## Thứ tự thủ tục"]
    for item in response.journey:
        lines.append(
            f"- Ưu tiên {item.priority}: **{item.name}** 【{item.procedure_id}】"
        )

    if response.benefits:
        lines.extend(["", "## Quyền lợi có thể liên quan"])
    for benefit in response.benefits:
        evidence = benefit.legal_evidence[0] if benefit.legal_evidence else None
        citation = f" 【{evidence.section_id}】" if evidence else ""
        lines.append(
            f"- **{benefit.title}** có thể liên quan, nhưng chưa đủ dữ kiện "
            f"để kết luận điều kiện hưởng.{citation}"
        )

    warnings = list(response.warnings)
    warnings.append("Đã dùng câu trả lời dự phòng vì hậu kiểm bản chi tiết không đạt.")
    if any("trạng thái hiệu lực" in warning.casefold() for warning in warnings):
        lines.extend(
            [
                "",
                "> **Lưu ý:** Dữ liệu nguồn chưa cung cấp trạng thái hiệu lực "
                "của một số văn bản pháp luật.",
            ]
        )
    return response.model_copy(
        update={"answer_markdown": "\n".join(lines), "warnings": warnings}
    )


def _generate_validated_response(context: AnswerContext) -> RAGResponse:
    response = generate_answer(context)
    validation = validate_answer(response)

    if not validation.is_valid:
        response = repair_procedure_citations(response, validation)
        validation = validate_answer(response)

    if not validation.is_valid:
        response = repair_answer_with_gemini(response, validation, context)
        validation = validate_answer(response)

    if not validation.is_valid:
        response = _fallback_response(response)
        validation = validate_answer(response)
        if not validation.is_valid:
            raise RuntimeError("Không thể tạo câu trả lời vượt qua hậu kiểm.")
    return response


class RAGEngine:
    def __init__(
        self,
        conversation_store: InMemoryConversationStore | None = None,
    ) -> None:
        self.conversation_store = conversation_store or InMemoryConversationStore()
        self.embedder = QueryEmbedder()

    def clear_conversation(self, conversation_id: str) -> None:
        self.conversation_store.clear(conversation_id)

    def run(
        self,
        text: str,
        *,
        conversation_id: str | None = None,
        limit: int = 5,
    ) -> RAGResponse:
        previous = (
            self.conversation_store.get(conversation_id)
            if conversation_id
            else None
        )
        context = build_context(
            text,
            conversation_id=conversation_id,
            limit=limit,
            previous_state=previous.query_state if previous else None,
            pending_questions=previous.pending_questions if previous else None,
            embedder=self.embedder,
        )
        response = _generate_validated_response(context)

        if conversation_id:
            self.conversation_store.put(
                ConversationState(
                    conversation_id=conversation_id,
                    query_state=context.query_state,
                    pending_questions=response.follow_up_questions,
                    turn_count=(previous.turn_count + 1) if previous else 1,
                )
            )
        return response


_DEFAULT_ENGINE = RAGEngine()


def run_rag(
    text: str,
    *,
    conversation_id: str | None = None,
    limit: int = 5,
) -> RAGResponse:
    return _DEFAULT_ENGINE.run(
        text,
        conversation_id=conversation_id,
        limit=limit,
    )


def _print_readable(response: RAGResponse) -> None:
    print(response.answer_markdown)
    if response.follow_up_questions:
        print("\n## Cần bạn cung cấp thêm")
        for question in response.follow_up_questions:
            print(f"- {question}")


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Chạy RAG engine hoàn chỉnh.")
    parser.add_argument("text", nargs="?", help="Câu hỏi hoặc tình huống của người dùng")
    parser.add_argument("--conversation-id", default=None)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="In payload JSON cho UI")
    parser.add_argument("--interactive", action="store_true", help="Hội thoại nhiều lượt")
    args = parser.parse_args()

    if args.interactive:
        engine = RAGEngine()
        conversation_id = args.conversation_id or str(uuid.uuid4())
        text = args.text
        while True:
            if not text:
                text = input("Bạn: ").strip()
            if text.casefold() in {"exit", "quit", "thoát"}:
                break
            response = engine.run(
                text,
                conversation_id=conversation_id,
                limit=args.limit,
            )
            print("\nTrợ lý:")
            _print_readable(response)
            print()
            text = None
        return

    if not args.text:
        parser.error("Cần truyền text hoặc dùng --interactive.")
    response = run_rag(
        args.text,
        conversation_id=args.conversation_id,
        limit=args.limit,
    )
    if args.json:
        print(json.dumps(response.model_dump(mode="json"), ensure_ascii=False, indent=2))
    else:
        _print_readable(response)


if __name__ == "__main__":
    main()
