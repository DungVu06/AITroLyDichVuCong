"""Demo pipeline đến bước truy xuất vector, chưa dùng Neo4j."""

from __future__ import annotations

import argparse
import json
import sys

from db.qdrant_client import QdrantVectorClient
from rag.pipeline.preprocessing import preprocess_query
from rag.pipeline.query_understanding import understand_query
from rag.retrieval.vector import VectorRetriever
from rag.pipeline.routing import route_query
from rag.core.schemas import UserQuery


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Demo RAG đến Qdrant retrieval.")
    parser.add_argument("text", help="Câu hỏi của người dùng")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    query = preprocess_query(UserQuery(text=args.text))
    state = understand_query(query)
    plan = route_query(query, state)

    with QdrantVectorClient.from_env() as client:
        retrieved = VectorRetriever(client).retrieve_from_plan(
            plan,
            procedure_limit=args.limit,
            law_limit=args.limit,
        )

    print(
        json.dumps(
            {
                "query_state": state.model_dump(mode="json"),
                "retrieval_plan": plan.model_dump(mode="json"),
                "retrieved": {
                    name: [chunk.model_dump(mode="json") for chunk in chunks]
                    for name, chunks in retrieved.items()
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
