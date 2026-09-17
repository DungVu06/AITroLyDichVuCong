"""Demo pipeline đến bước lấy chi tiết cho các thủ tục trong journey."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

from db.neo4j_client import Neo4jClient
from db.qdrant_client import QdrantVectorClient
from rag.pipeline.journey import build_journey
from rag.pipeline.preprocessing import preprocess_query
from rag.pipeline.query_understanding import understand_query
from rag.retrieval.graph import GraphRetriever
from rag.retrieval.vector import VectorRetriever
from rag.pipeline.routing import route_query
from rag.core.schemas import UserQuery


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Demo RAG đến procedure details.")
    parser.add_argument("text", help="Câu hỏi của người dùng")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--per-type-limit", type=int, default=3)
    args = parser.parse_args()

    query = preprocess_query(UserQuery(text=args.text))
    state = understand_query(query)
    plan = route_query(query, state)

    with QdrantVectorClient.from_env() as qdrant:
        retriever = VectorRetriever(qdrant)
        vector_result = retriever.retrieve_from_plan(
            plan,
            procedure_limit=args.limit,
            law_limit=args.limit,
        )
        seed_ids = list(
            dict.fromkeys(chunk.doc_id for chunk in vector_result["procedures"])
        )

        with Neo4jClient.from_env() as neo4j:
            graph_result = GraphRetriever(neo4j).retrieve(
                seed_ids,
                include_benefits=plan.include_benefits,
            )

        journey = build_journey(graph_result, seed_ids)
        journey_ids = {item.procedure_id for item in journey}
        journey_procedures = [
            item
            for item in graph_result.procedures
            if item.procedure_id in journey_ids
        ]
        details = retriever.retrieve_procedure_details(
            journey_procedures,
            query=query.normalized_text,
            chunk_types=plan.procedure_chunk_types,
            per_type_limit=args.per_type_limit,
        )

    output = []
    for procedure in details:
        counts = Counter(chunk.chunk_type for chunk in procedure.chunks)
        first_by_type = {}
        for chunk in procedure.chunks:
            first_by_type.setdefault(chunk.chunk_type, chunk.text)
        output.append(
            {
                "procedure_id": procedure.procedure_id,
                "name": procedure.name,
                "chunk_counts": dict(counts),
                "sample_by_type": first_by_type,
            }
        )

    print(json.dumps({"procedure_details": output}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
