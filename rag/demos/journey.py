"""Demo pipeline đến bước tạo hành trình thủ tục."""

from __future__ import annotations

import argparse
import json
import sys

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

    parser = argparse.ArgumentParser(description="Demo RAG đến journey builder.")
    parser.add_argument("text", help="Câu hỏi của người dùng")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    query = preprocess_query(UserQuery(text=args.text))
    state = understand_query(query)
    plan = route_query(query, state)

    with QdrantVectorClient.from_env() as qdrant:
        vector_result = VectorRetriever(qdrant).retrieve_from_plan(
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
    print(
        json.dumps(
            {
                "seed_procedure_ids": seed_ids,
                "journey": [item.model_dump(mode="json") for item in journey],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
