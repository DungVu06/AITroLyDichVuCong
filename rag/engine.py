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
from rag.core.conversation import InMemoryConversationStore
from rag.core.transcript import ConversationTranscriptStore
from rag.generation.answer import filter_sources_to_citations, generate_answer, refine_answer
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
    AnswerContract,
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
    limit: int = 20,
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
    # Retrieval starts from the analyzed request and retrieved records.
    # The contract is populated from retrieved evidence below.
    contract = AnswerContract(procedure_ids=list(state.procedure_ids))
    catalog = procedure_catalog()
    requested = [item for item in state.procedure_ids if item in catalog]
    workflow_id = None
    contract_resolved = False
    with QdrantVectorClient.from_env() as qdrant:
        retriever = VectorRetriever(qdrant, embedder=embedder)
        vector_result = retriever.retrieve_from_plan(
            plan,
            procedure_limit=limit,
            law_limit=limit,
        )
        # Rank procedure candidates by their best chunk rank. Explicitly
        # identified procedures remain first, followed by vector candidates.
        ranked_ids = list(dict.fromkeys(
            chunk.doc_id for chunk in vector_result["procedures"] if chunk.doc_id in catalog
        ))
        seed_ids = list(dict.fromkeys([*requested, *ranked_ids]))
        if requested and not state.asks_about_dependencies:
            seed_ids = requested
        elif not state.asks_about_dependencies:
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

        # Rank workflows using graph membership and vector candidate rank.
        # Expand related workflows only for dependency questions or explicitly
        # selected workflows, so a simple detail query stays focused.
        if retrieval_mode == "graph":
            workflow_members = {}
            for edge in graph.procedure_relations:
                if edge.relationship_type == "HAS_SUB_PROCEDURE":
                    workflow_members.setdefault(edge.source_id, set()).add(edge.target.procedure_id)
                elif edge.relationship_type == "PART_OF":
                    workflow_members.setdefault(edge.target.procedure_id, set()).add(edge.source_id)
            candidates = []
            for candidate, members in workflow_members.items():
                explicit = candidate in requested
                overlap = len(members.intersection(requested))
                if not explicit and not (state.asks_about_dependencies and overlap):
                    continue
                vector_rank = ranked_ids.index(candidate) if candidate in ranked_ids else len(ranked_ids)
                candidates.append((explicit, overlap, -vector_rank, candidate))
            if candidates:
                workflow_id = max(candidates)[-1]
                contract.workflow_id = workflow_id

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
        contract.enforce_step_sequence = "steps" in state.topics

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
        sequence_procedures = (
            [procedure for procedure in procedures if procedure.procedure_id == workflow_id]
            if workflow_id else procedures
        )
        required_step_numbers = {
            procedure.procedure_id: sorted({
                chunk.step_number
                for chunk in procedure.chunks
                if chunk.chunk_type == "step_item" and chunk.step_number is not None
            })
            for procedure in sequence_procedures
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
        ]
    return context


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
    try:
        return refine_answer(response, context)
    except Exception:
        logging.getLogger(__name__).exception("Không thể đối chiếu câu trả lời bằng LLM")
        response.warnings.append("Chưa thể đối chiếu câu trả lời với nguồn. Vui lòng kiểm tra lại các thông tin trước khi sử dụng.")
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
        limit: int = 20,
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
        uncertain_benefit_ids = {
            benefit.related_procedure_id
            for benefit in response.benefits
            if benefit.eligibility_status.value in {"unknown", "possibly_eligible"}
        }
        if (response.follow_up_questions or context.query_state.missing_facts
                or uncertain_benefit_ids or response.needs_authority_confirmation):
            relevant_ids = set(context.query_state.procedure_ids) | uncertain_benefit_ids
            if not relevant_ids:
                relevant_ids = {item.procedure_id for item in response.journey}
            authorities = [
                f"{procedure.name}: {procedure.authority}"
                for procedure in context.procedure_evidence
                if procedure.procedure_id in relevant_ids and procedure.authority
                and context.query_state.intent.value != "benefit_check"
            ]
            if authorities:
                response.warnings.append(
                    "Nếu chưa đủ thông tin để xác định trường hợp của bạn, hãy kiểm tra với "
                    "cơ quan có thẩm quyền. Cơ quan ghi trong dữ liệu thủ tục: "
                    + "; ".join(dict.fromkeys(authorities)) + "."
                )
            else:
                response.warnings.append(
                    "Nếu chưa đủ thông tin để xác định trường hợp của bạn, hãy kiểm tra "
                    "với cơ quan có thẩm quyền. Dữ liệu chưa xác định được cơ quan liên hệ."
                )
        response = filter_sources_to_citations(response, context)

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
    limit: int = 20,
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
    parser.add_argument("--limit", type=int, default=20)
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
