"""Bước 5: tìm procedure/law chunks trong Qdrant."""

from __future__ import annotations

from typing import Any

from db.qdrant_client import QdrantVectorClient
from rag.retrieval.embedding import QueryEmbedder
from rag.core.schemas import ProcedureEvidence, RetrievedChunk, RetrievalPlan


DETAIL_QUERY_HINTS = {
    "document_item": "hồ sơ giấy tờ phổ biến cần chuẩn bị",
    "step_item": "trình tự các bước thực hiện",
    "execution_methods": "cách thức thực hiện thời gian giải quyết lệ phí",
    "note_item": "lưu ý quan trọng cho trường hợp thông thường",
}


def _rank_detail_chunks(
    chunks: list[RetrievedChunk],
    chunk_type: str,
    limit: int,
) -> list[RetrievedChunk]:
    if chunk_type != "document_item":
        return chunks[:limit]

    def document_rank(chunk: RetrievedChunk) -> tuple[bool, bool, float]:
        text = chunk.text.casefold()
        item = text.rsplit("\n- ", 1)[-1].lstrip().removeprefix("- ").lstrip()
        conditional = item.startswith("trường hợp") or " trong trường hợp " in item
        zero_quantity = "số lượng: 0" in text or "bản chính: 0" in text
        return conditional, zero_quantity, -(chunk.score or 0.0)

    return sorted(chunks, key=document_rank)[:limit]


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
        points = self.client.search(
            collection_name=collection,
            query_vector=vector,
            limit=fetch_limit,
            query_filter=None,
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
    ) -> list[ProcedureEvidence]:
        """Xếp hạng chi tiết theo tình huống rồi lọc đúng procedure ID."""
        procedure_ids = {procedure.procedure_id for procedure in procedures}
        grouped: dict[str, dict[str, list[RetrievedChunk]]] = {
            procedure_id: {chunk_type: [] for chunk_type in chunk_types}
            for procedure_id in procedure_ids
        }

        for chunk_type in chunk_types:
            detail_query = f"{query}. {DETAIL_QUERY_HINTS.get(chunk_type, chunk_type)}"
            points = self.client.search(
                collection_name="procedures",
                query_vector=self.embedder.encode(detail_query),
                limit=1000,
                query_filter=None,
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

        enriched = []
        for procedure in procedures:
            chunks = [
                chunk
                for chunk_type in chunk_types
                for chunk in _rank_detail_chunks(
                    grouped[procedure.procedure_id][chunk_type],
                    chunk_type,
                    per_type_limit,
                )
            ]
            enriched.append(procedure.model_copy(update={"chunks": chunks}))
        return enriched
