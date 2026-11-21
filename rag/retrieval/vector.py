"""Bước 5: tìm procedure/law chunks trong Qdrant."""

from __future__ import annotations

import re
from typing import Any

import httpx
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse

from db.qdrant_client import QdrantVectorClient
from rag.retrieval.embedding import QueryEmbedder
from rag.core.schemas import (
    EvidenceRequirement,
    ProcedureEvidence,
    RetrievedChunk,
    RetrievalPlan,
)


DETAIL_QUERY_HINTS = {
    "document_item": "hồ sơ giấy tờ cần cho tình huống được hỏi",
    "step_item": "trình tự các bước thực hiện",
    "execution_methods": "cách thức thực hiện thời gian giải quyết lệ phí",
    "note_item": "lưu ý quan trọng cho trường hợp thông thường",
}


def _rank_detail_chunks(
    chunks: list[RetrievedChunk],
    chunk_type: str,
    limit: int,
    query: str = "",
) -> list[RetrievedChunk]:
    # Some split steps contain only the repeated procedure title and step label.
    usable = [item for item in chunks if item.text.strip() and not (
        chunk_type == "step_item" and item.text.rstrip().endswith(":")
        and "\n" not in item.text.strip()
    )]
    # Fuse semantic order with exact phrases in the body. The repeated document
    # title is identical across a procedure and should not influence the ranking.
    if query and len(usable) > limit:
        def phrases(text: str) -> set[tuple[str, str]]:
            words = re.findall(r"\w+", text.casefold())
            return set(zip(words, words[1:]))

        query_terms = phrases(query)
        def overlap(item: RetrievedChunk) -> int:
            body = item.text.partition("\n")[2] or item.text
            return len(phrases(body) & query_terms)

        lexical = sorted(usable, key=overlap, reverse=True)
        phrase_rank = {item.point_id: rank for rank, item in enumerate(lexical, 1) if overlap(item)}
        def relevance(pair: tuple[int, RetrievedChunk]) -> float:
            rank, item = pair
            score = 1 / (12 + rank)
            if item.point_id in phrase_rank:
                score += 1 / (12 + phrase_rank[item.point_id])
            return score
        usable = [item for _, item in sorted(enumerate(usable, 1), key=relevance, reverse=True)]
    ranked = usable[:limit]
    if chunk_type == "step_item":
        def source_order(item: RetrievedChunk) -> tuple[int, int]:
            match = re.search(r"_c(\d+)_s(\d+)$", item.chunk_id or "")
            return (int(match[1]), int(match[2])) if match else (0, 0)
        ranked.sort(key=source_order)
    return ranked


def payload_matches(
    payload: dict[str, Any],
    metadata_filters: dict[str, Any],
    chunk_types: list[str] | None,
) -> bool:
    """Lọc payload tại client vì database hiện chưa có payload index."""
    for key, expected in metadata_filters.items():
        actual = payload.get(key)
        if isinstance(actual, list):
            expected_values = expected if isinstance(expected, list) else [expected]
            if not any(value in actual for value in expected_values):
                return False
        elif isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False

    return not chunk_types or payload.get("chunk_type") in chunk_types


class VectorRetriever:
    def __init__(
        self,
        client: QdrantVectorClient,
        embedder: QueryEmbedder | None = None,
    ) -> None:
        self.client = client
        self.embedder = embedder or QueryEmbedder()
        self.used_local = False

    def _points(self, collection_name: str, query_vector: list[float], limit: int):
        if not self.used_local:
            try:
                return self.client.search(collection_name=collection_name, query_vector=query_vector,
                                          limit=limit, query_filter=None)
            except ResponseHandlingException as exc:
                if not isinstance(exc.source, httpx.NetworkError | httpx.TimeoutException):
                    raise
                self.used_local = True
            except UnexpectedResponse as exc:
                # A freshly-created Cloud project has no collections until an
                # import runs. The bundled chunks still provide a usable demo.
                if exc.status_code != 404 or "doesn't exist" not in str(exc):
                    raise
                self.used_local = True
        return self.embedder.local_index.search(collection_name, query_vector, limit, self.embedder)

    def search(
        self,
        collection: str,
        query: str,
        metadata_filters: dict[str, Any],
        chunk_types: list[str] | None = None,
        limit: int = 10,
    ) -> list[RetrievedChunk]:
        vector = self.embedder.encode(query)
        # Lấy dư kết quả để lọc tại client. Khi Qdrant có payload index, phần
        # này có thể chuyển lại thành server-side filter để tối ưu hiệu năng.
        fetch_limit = max(limit * 10, 50)
        points = self._points(
            collection_name=collection,
            query_vector=vector,
            limit=fetch_limit,
        )

        chunks = []
        for point in points:
            payload = dict(point.payload or {})
            if not payload_matches(payload, metadata_filters, chunk_types):
                continue
            text = str(payload.pop("text", ""))
            chunks.append(
                RetrievedChunk(
                    collection=collection,
                    point_id=str(point.id),
                    doc_id=str(payload.get("doc_id", "")),
                    chunk_id=payload.get("chunk_id"),
                    chunk_type=payload.get("chunk_type"),
                    text=text,
                    score=float(point.score) if point.score is not None else None,
                    metadata=payload,
                )
            )
            if len(chunks) >= limit:
                break
        return chunks

    def retrieve_from_plan(
        self,
        plan: RetrievalPlan,
        procedure_limit: int = 10,
        law_limit: int = 10,
    ) -> dict[str, list[RetrievedChunk]]:
        result: dict[str, list[RetrievedChunk]] = {
            "procedures": [],
            "laws": [],
        }

        if plan.use_procedure_vector_search and plan.procedure_query:
            result["procedures"] = self.search(
                collection="procedures",
                query=plan.procedure_query,
                metadata_filters=plan.qdrant_filters,
                chunk_types=plan.procedure_chunk_types,
                limit=procedure_limit,
            )

        if plan.use_law_vector_search and plan.law_query:
            result["laws"] = self.search(
                collection="laws",
                query=plan.law_query,
                metadata_filters=plan.qdrant_filters,
                limit=law_limit,
            )

        return result

    def retrieve_procedure_details(
        self,
        procedures: list[ProcedureEvidence],
        *,
        query: str,
        chunk_types: list[str],
        per_type_limit: int = 3,
        required_evidence: list[EvidenceRequirement] | None = None,
    ) -> list[ProcedureEvidence]:
        """Xếp hạng chi tiết theo tình huống rồi lọc đúng procedure ID."""
        procedure_ids = {procedure.procedure_id for procedure in procedures}
        grouped: dict[str, dict[str, list[RetrievedChunk]]] = {
            procedure_id: {chunk_type: [] for chunk_type in chunk_types}
            for procedure_id in procedure_ids
        }

        for chunk_type in chunk_types:
            detail_query = f"{query}. {DETAIL_QUERY_HINTS.get(chunk_type, chunk_type)}"
            points = self._points(
                collection_name="procedures",
                query_vector=self.embedder.encode(detail_query),
                limit=1000,
            )
            for point in points:
                payload = dict(point.payload or {})
                procedure_id = str(payload.get("doc_id", ""))
                actual_type = str(payload.get("chunk_type", ""))
                if procedure_id not in grouped or actual_type != chunk_type:
                    continue
                bucket = grouped[procedure_id][actual_type]
                text = str(payload.pop("text", ""))
                bucket.append(
                    RetrievedChunk(
                        collection="procedures",
                        point_id=str(point.id),
                        doc_id=procedure_id,
                        chunk_id=payload.get("chunk_id"),
                        chunk_type=actual_type,
                        text=text,
                        score=float(point.score) if point.score is not None else None,
                        metadata=payload,
                    )
                )

        requirements = required_evidence or []

        def required_chunks(
            procedure_id: str,
            chunk_type: str,
            available: list[RetrievedChunk],
        ) -> list[RetrievedChunk]:
            """Always retain chunks that prove an AnswerContract claim.

            Semantic ranking is still used for general context, but it must not
            displace a conditional document, precedence rule, or time limit.
            """
            required = [
                requirement
                for requirement in requirements
                if requirement.procedure_id == procedure_id
                and requirement.chunk_type == chunk_type
                and not requirement.relation_type
            ]
            result = []
            for requirement in required:
                matches = [
                    item for item in available
                    if all(term.casefold() in item.text.casefold() for term in requirement.required_terms)
                ]
                if matches:
                    result.append(matches[0])
            return list({item.point_id: item for item in result}.values())

        enriched = []
        for procedure in procedures:
            chunks: list[RetrievedChunk] = []
            for chunk_type in chunk_types:
                available = grouped[procedure.procedure_id][chunk_type]
                forced = required_chunks(procedure.procedure_id, chunk_type, available)
                ranked = _rank_detail_chunks(available, chunk_type, per_type_limit, query)
                merged = list({item.point_id: item for item in [*forced, *ranked]}.values())
                if chunk_type == "step_item":
                    merged.sort(key=lambda item: item.chunk_id or "")
                chunks.extend(merged)
            enriched.append(procedure.model_copy(update={"chunks": chunks}))
        return enriched
