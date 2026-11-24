"""Điều phối pipeline RAG hoàn chỉnh từ câu hỏi đến response cho UI."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import socket
from typing import Literal

from neo4j.exceptions import ServiceUnavailable, SessionExpired
from rag.retrieval.local_graph import SnapshotGraph
import uuid

from db.graph.procedure_normalize import LINKED_CARD_STEP
from db.neo4j_client import Neo4jClient
from db.qdrant_client import QdrantVectorClient
from rag.pipeline.benefits import resolve_benefits
from rag.pipeline.context import build_answer_context
from rag.pipeline.answer_contract import build_answer_contract
from rag.core.conversation import InMemoryConversationStore
from rag.core.transcript import ConversationTranscriptStore
from rag.generation.answer import filter_sources_to_citations, generate_answer, repair_answer_with_gemini
from rag.generation.validator import repair_procedure_citations, validate_answer
from rag.pipeline.journey import build_journey, select_workflow, workflow_transfer_evidence
from rag.pipeline.preprocessing import preprocess_query
from rag.pipeline.query_understanding import understand_query
from rag.retrieval.graph import GraphRetriever
from rag.retrieval.catalog import DATA, procedure_catalog, records, source_metadata
from rag.retrieval.embedding import QueryEmbedder
from rag.retrieval.vector import VectorRetriever
from rag.pipeline.routing import route_query
from rag.core.schemas import (
    AnswerContext,
    ConversationState,
    GraphRetrievalResult,
    LegalEvidence,
    ProcedureEvidence,
    QueryState,
    RAGResponse,
    ResponseRules,
    RelationEvidence,
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
    retrieval_mode: Literal["graph", "vector_only"] = "graph",
) -> AnswerContext:
    if retrieval_mode not in {"graph", "vector_only"}:
        raise ValueError("retrieval_mode must be 'graph' or 'vector_only'.")
    user_query = UserQuery(text=text, conversation_id=conversation_id)
    query = preprocess_query(user_query)
    state = understand_query(
        query,
        previous_state=previous_state,
        pending_questions=pending_questions,
    )
    plan = route_query(query, state)

    if plan.strategy in {RetrievalStrategy.OUT_OF_SCOPE, RetrievalStrategy.CLARIFICATION}:
        return AnswerContext(query=user_query, query_state=state)
    catalog = procedure_catalog()
    contract = build_answer_contract(user_query, state)
    # A deterministic contract is derived only from explicit facts in the
    # current message. When it resolves a procedure, do not let an LLM infer
    # extra procedures merely because their documents are mentioned (for
    # example, a birth certificate cited as evidence in a card-correction case).
    contract_resolved = bool(contract.requirements)
    requested_candidates = (
        contract.procedure_ids
        if contract_resolved
        else [*state.procedure_ids, *contract.procedure_ids]
    )
    requested = list(dict.fromkeys(i for i in requested_candidates if i in catalog))
    workflow_id = contract.workflow_id
    if workflow_id and workflow_id in catalog:
        requested = [workflow_id]
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
        if requested and plan.use_procedure_vector_search:
            seed_ids = requested
        elif plan.strategy in {RetrievalStrategy.PROCEDURE_DETAIL, RetrievalStrategy.GRAPH_NEXT_STEPS}:
            seed_ids = seed_ids[:1]

        def read_graph(client):
            graph_retriever = GraphRetriever(client)
            if (plan.use_graph_traversal or (state.asks_about_dependencies and not contract_resolved)
                    or any(item.relation_type for item in contract.requirements)
                    or len(seed_ids) > 1):
                graph = graph_retriever.retrieve(seed_ids, include_benefits=plan.include_benefits)
            else:
                graph = graph_retriever.retrieve_procedure_nodes(seed_ids)
            return graph, graph_retriever.retrieve_law_evidence(vector_result["laws"])

        used_local_graph = False
        if retrieval_mode == "vector_only":
            # This branch intentionally does not instantiate Neo4jClient or
            # SnapshotGraph. It is the control arm for the Graph-RAG demo:
            # semantic retrieval, contract, prompt and validator stay equal,
            # while relations and graph-expanded law sections are absent.
            raw_procedures = {
                record["id"]: record
                for record in records("procedure", DATA)
            }
            # The control arm has no relationship traversal, but it may still
            # retrieve records explicitly named by the same deterministic
            # contract. Otherwise a graph-only child detail would be confused
            # with a retrieval advantage rather than an ordering advantage.
            vector_procedure_ids = list(dict.fromkeys([
                *seed_ids,
                *contract.procedure_ids,
            ]))
            procedures = []
            for procedure_id in vector_procedure_ids:
                raw = raw_procedures.get(procedure_id)
                if not raw:
                    continue
                matching_chunks = [
                    chunk for chunk in vector_result["procedures"]
                    if chunk.doc_id == procedure_id
                ]
                procedures.append(
                    ProcedureEvidence(
                        procedure_id=procedure_id,
                        name=raw["procedure"]["name"],
                        authority=raw["procedure"].get("authority"),
                        eligibility=raw["procedure"].get("eligibility"),
                        source_url=raw.get("source", {}).get("url"),
                        vector_score=(matching_chunks[0].score if matching_chunks else None),
                    )
                )
            graph = GraphRetrievalResult(procedures=procedures)
            legal_evidence = [
                LegalEvidence(
                    law_id=chunk.doc_id,
                    section_id=chunk.chunk_id or chunk.point_id,
                    heading=chunk.metadata.get("heading"),
                    text=chunk.text,
                    source_url=chunk.metadata.get("source_url"),
                    retrieval_score=chunk.score,
                )
                for chunk in vector_result["laws"]
            ]
        else:
            try:
                with Neo4jClient.from_env() as neo4j:
                    graph, legal_evidence = read_graph(neo4j)
            except (ServiceUnavailable, SessionExpired, ValueError) as exc:
                if isinstance(exc, ValueError) and not isinstance(exc.__cause__, socket.gaierror):
                    raise
                graph, legal_evidence = read_graph(SnapshotGraph())
                used_local_graph = True

        if workflow_id and retrieval_mode == "graph":
            workflow = select_workflow(graph, workflow_id, state.identity_card_requested)
            expected = {
                (requirement.procedure_id, requirement.target_procedure_id)
                for requirement in contract.requirements if requirement.relation_type == "NEXT_STEP"
            }
            available = {(item.source_id, item.target_id) for item in workflow_transfer_evidence(workflow)}
            if not used_local_graph and not expected.issubset(available):
                graph, legal_evidence = read_graph(SnapshotGraph())
                used_local_graph = True
                workflow = select_workflow(graph, workflow_id, state.identity_card_requested)
            graph = workflow
        elif plan.strategy == RetrievalStrategy.PROCEDURE_DETAIL:
            # Retain the linked one-stop alternative for a multi-procedure request.
            focus = set(seed_ids)
            if state.asks_about_dependencies and not contract_resolved:
                focus.update(r.target.procedure_id for r in graph.procedure_relations
                             if r.relationship_type == "REQUIRES" and r.source_id in seed_ids
                             and not r.workflow_id and r.evidence_record_id and r.evidence_step)
            if len(focus) > 1:
                focus.update(r.target.procedure_id for r in graph.procedure_relations
                             if r.relationship_type == "PART_OF" and r.source_id in seed_ids)
            graph = graph.model_copy(update={
                "procedures": [p for p in graph.procedures if p.procedure_id in focus],
                "procedure_relations": [r for r in graph.procedure_relations
                                        if r.source_id in focus and r.target.procedure_id in focus],
            })
        journey = build_journey(
            graph,
            seed_ids,
            completed_procedure_ids=(
                state.completed_ids if workflow_id else [i for i in state.completed_ids if i in seed_ids]
            ),
            workflow_id=workflow_id if retrieval_mode == "graph" else None,
            identity_card_requested=state.identity_card_requested,
        )
        detail_types = list(plan.procedure_chunk_types)
        if state.asks_about_dependencies:
            detail_types.extend(("step_item", "execution_methods"))
        detail_types.extend(
            item.chunk_type for item in contract.requirements if item.chunk_type
        )
        detail_types = list(dict.fromkeys(detail_types))
        if workflow_id:
            # A graph edge proves ordering, while the evidence for documents
            # and time may live on a component procedure. Keep the workflow
            # parent and every procedure demanded by the deterministic
            # contract in the detail retrieval set.
            required_detail_ids = {workflow_id}
            required_detail_ids.update(
                requirement.procedure_id for requirement in contract.requirements
            )
            detail_procedures = [
                item for item in graph.procedures
                if item.procedure_id in required_detail_ids
            ]
        else:
            detail_procedures = list(graph.procedures)
        procedures = retriever.retrieve_procedure_details(
            detail_procedures,
            query=plan.procedure_query or query.normalized_text,
            chunk_types=detail_types if graph.procedures else [],
            per_type_limit=8,
            required_evidence=contract.requirements,
            preserve_step_sequence=contract.enforce_step_sequence,
        )
        if workflow_id:
            details = {item.procedure_id: item for item in procedures}
            if state.identity_card_requested is False and workflow_id in details:
                procedure = details[workflow_id]
                details[workflow_id] = procedure.model_copy(update={"chunks": [
                    chunk for chunk in procedure.chunks
                    if chunk.chunk_type != "step_item" or chunk.step_number != LINKED_CARD_STEP
                ]})
            procedures = [details.get(item.procedure_id, item) for item in graph.procedures]

    if contract.enforce_step_sequence:
        required_step_numbers = {
            procedure.procedure_id: sorted({
                chunk.step_number
                for chunk in procedure.chunks
                if chunk.chunk_type == "step_item" and chunk.step_number is not None
            })
            for procedure in procedures
        }
        contract = contract.model_copy(update={
            "required_step_numbers": {
                procedure_id: numbers
                for procedure_id, numbers in required_step_numbers.items()
                if numbers
            }
        })

    metadata = source_metadata()
    benefits = resolve_benefits(graph) if retrieval_mode == "graph" else []
    all_legal = [*legal_evidence, *(item for b in benefits for item in b.legal_evidence)]
    for item in all_legal:
        meta = metadata.get(item.law_id)
        if meta:
            item.source_url = meta.url or item.source_url
            item.validity = meta.validity or "Chưa xác minh"
            if meta.review:
                item.text = None
    context = build_answer_context(
        query=user_query,
        query_state=state,
        journey=journey,
        procedure_evidence=procedures,
        benefits=benefits,
        legal_evidence=legal_evidence,
        contract=contract,
        response_rules=ResponseRules(
            demo_scope="Demo sự kiện sinh con; trạng thái hiệu lực luật có thể thiếu."
        ),
    )

    context.used_local_graph = used_local_graph
    context.used_local_vector_index = retriever.used_local
    used = {p.procedure_id for p in procedures} | {item.law_id for item in all_legal}
    context.source_metadata = {k: metadata[k] for k in sorted(used) if k in metadata}
    if workflow_id:
        context.relation_evidence = workflow_transfer_evidence(graph)
        context.contract.processing_flow = [item.text for item in context.relation_evidence]
    else:
        required_relation_types = {
            requirement.relation_type
            for requirement in contract.requirements
            if requirement.relation_type
        }
        context.relation_evidence = [
            RelationEvidence(
                source_id=edge.source_id,
                relationship_type=edge.relationship_type,
                target_id=edge.target.procedure_id,
                citation_id=f"REL:{edge.source_id}:{edge.relationship_type}:{edge.target.procedure_id}",
                text=f"{edge.source_id} {edge.relationship_type} {edge.target.procedure_id}",
                evidence_record_id=edge.evidence_record_id,
                evidence_step=edge.evidence_step,
            )
            for edge in graph.procedure_relations
            if not edge.workflow_id and edge.evidence_record_id and edge.evidence_step
            and edge.relationship_type in required_relation_types
        ]
    return context


def _fallback_response(response: RAGResponse, context: AnswerContext) -> RAGResponse:
    lines = ["## Hướng dẫn theo thông tin đã kiểm chứng", "", "### Thứ tự thủ tục"]
    for item in response.journey:
        optional = f" ({item.reason})" if item.category == "optional" and item.reason else ""
        lines.append(f"- Ưu tiên {item.priority}: **{item.name}**{optional} 【{item.procedure_id}】")

    chunk_index = {
        chunk.chunk_id: chunk
        for procedure in context.procedure_evidence
        for chunk in procedure.chunks
        if chunk.chunk_id
    }
    lines.append("\n### Nội dung đã đối chiếu")
    rendered = set()
    for requirement in context.contract.requirements:
        if requirement.relation_type:
            relation = next((item for item in context.relation_evidence
                             if item.relationship_type == requirement.relation_type
                             and item.source_id == requirement.procedure_id
                             and (requirement.target_procedure_id is None
                                  or item.target_id == requirement.target_procedure_id)), None)
            if relation:
                reference = (
                    f" (Bước {relation.evidence_step} trong quy trình liên thông)"
                    if context.contract.workflow_id else ""
                )
                lines.append(f"- {relation.text}{reference} 【{relation.citation_id}】")
                rendered.add(requirement.claim_id)
            continue
        candidates = [
            chunk for chunk in chunk_index.values()
            if chunk.doc_id == requirement.procedure_id
            and chunk.chunk_type == requirement.chunk_type
            and (requirement.step_number is None or chunk.step_number == requirement.step_number)
            and not any(term.casefold() in chunk.text.casefold() for term in requirement.excluded_terms)
            and all(term.casefold() in chunk.text.casefold() for term in requirement.required_terms)
        ]
        if candidates:
            chunk = candidates[0]
            content = (
                context.contract.submission_channel
                if requirement.claim_id == "linked_submission"
                else " ".join(chunk.text.split())
            )
            lines.append(f"- **{requirement.label}:** {content} 【{chunk.chunk_id}】")
            rendered.add(requirement.claim_id)

    for procedure_id, expected_steps in context.contract.required_step_numbers.items():
        for number in expected_steps:
            chunk = next((item for item in chunk_index.values()
                          if item.doc_id == procedure_id and item.chunk_type == "step_item"
                          and item.step_number == number), None)
            if chunk and not any(f"【{chunk.chunk_id}】" in line for line in lines):
                lines.append(f"- {' '.join(chunk.text.split())} 【{chunk.chunk_id}】")

    # There may be no formal contract for a normal question. Keep a restrained
    # answer based on the best retrieved evidence in that case only.
    if not rendered:
        for procedure in context.procedure_evidence:
            selected = [c for c in procedure.chunks if c.chunk_id]
            if selected:
                lines.append(f"### {procedure.name} 【{procedure.procedure_id}】")
                for chunk in selected[:4]:
                    lines.append(f"- {' '.join(chunk.text.split())} 【{chunk.chunk_id}】")
    for item in context.legal_evidence:
        if not item.text:
            lines.append(f"- {item.heading or item.law_id}: chưa có nội dung đã xác minh để áp dụng. 【{item.section_id}】")
        else:
            lines.append(f"- {' '.join(item.text.split())[:800]} 【{item.section_id}】")
    if len(lines) == 1:
        lines = ["Chưa có nội dung đã xác minh để hướng dẫn cho tình huống này."]

    if response.benefits:
        lines.extend(["", "## Quyền lợi có thể liên quan"])
    for benefit in response.benefits:
        evidence = benefit.legal_evidence[0] if benefit.legal_evidence else None
        citation = f" 【{evidence.section_id}】" if evidence else ""
        if not citation and benefit.related_procedure_id in {s.source_id for s in response.sources}:
            citation = f" 【{benefit.related_procedure_id}】"
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
    if not (context.procedure_evidence or context.legal_evidence or context.benefits):
        questions = [f.question for f in context.query_state.missing_facts if f.question]
        outside = context.query_state.intent.value == "out_of_scope"
        return RAGResponse(
            answer_markdown=("Câu hỏi nằm ngoài phạm vi trợ lý thủ tục hành chính."
                             if outside else "Chưa xác định được thủ tục từ thông tin hiện có."),
            follow_up_questions=[] if outside else questions[:3] or ["Bạn muốn tra cứu thủ tục cụ thể nào?"],
        )
    response = generate_answer(context)
    validation = validate_answer(response, context)

    if not validation.is_valid:
        response = repair_procedure_citations(response, validation)
        validation = validate_answer(response, context)

    if not validation.is_valid:
        response = repair_answer_with_gemini(response, validation, context)
        validation = validate_answer(response, context)

    if not validation.is_valid:
        logging.getLogger(__name__).warning("Answer fallback after repair: %s", [i.code for i in validation.issues])
        response = _fallback_response(response, context)
        validation = validate_answer(response, context)
        if not validation.is_valid:
            raise RuntimeError("Không thể tạo câu trả lời vượt qua hậu kiểm.")
    return response


class RAGEngine:
    def __init__(
        self,
        conversation_store: InMemoryConversationStore | None = None,
        transcript_store: ConversationTranscriptStore | None = None,
        *,
        retrieval_mode: Literal["graph", "vector_only"] = "graph",
    ) -> None:
        if retrieval_mode not in {"graph", "vector_only"}:
            raise ValueError("retrieval_mode must be 'graph' or 'vector_only'.")
        self.conversation_store = conversation_store or InMemoryConversationStore()
        self.transcript_store = transcript_store or ConversationTranscriptStore()
        self.embedder = QueryEmbedder()
        self.retrieval_mode = retrieval_mode

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
            retrieval_mode=self.retrieval_mode,
        )
        response = _generate_validated_response(context)
        if context.used_local_graph:
            response.warnings.append("Lượt này dùng quan hệ từ bộ dữ liệu cục bộ của dự án.")
        if context.used_local_vector_index:
            response.warnings.append("Không kết nối được Qdrant Cloud. Lượt này dùng chỉ mục Qdrant từ dữ liệu local của dự án.")
        response = filter_sources_to_citations(response)

        if conversation_id:
            self.conversation_store.put(
                ConversationState(
                    conversation_id=conversation_id,
                    query_state=context.query_state,
                    pending_questions=response.follow_up_questions,
                    turn_count=(previous.turn_count + 1) if previous else 1,
                )
            )
            try:
                self.transcript_store.append(conversation_id, text, response)
            except OSError:
                logging.getLogger(__name__).exception(
                    "Could not save conversation transcript: %s", conversation_id
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
    for warning in response.warnings:
        print(f"Lưu ý: {warning}")
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
