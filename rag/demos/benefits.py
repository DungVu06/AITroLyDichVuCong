"""Demo pipeline đến bước gom quyền lợi và căn cứ luật."""

from __future__ import annotations

import argparse
import json
import sys

from db.neo4j_client import Neo4jClient
from db.qdrant_client import QdrantVectorClient
from rag.pipeline.benefits import resolve_benefits
from rag.pipeline.preprocessing import preprocess_query
from rag.pipeline.query_understanding import understand_query
from rag.retrieval.graph import GraphRetriever
from rag.retrieval.vector import VectorRetriever
from rag.pipeline.routing import route_query
from rag.core.schemas import UserQuery


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Demo RAG đến benefit resolver.")
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

    seed_ids = list(dict.fromkeys(chunk.doc_id for chunk in vector_result["procedures"]))
    with Neo4jClient.from_env() as neo4j:
        graph = GraphRetriever(neo4j).retrieve(
            seed_ids,
            include_benefits=plan.include_benefits,
        )

    benefits = resolve_benefits(graph)
    output = []
    for benefit in benefits:
        output.append(
            {
                "title": benefit.title,
                "eligibility_status": benefit.eligibility_status,
                "reason": benefit.reason,
                "related_procedure_id": benefit.related_procedure_id,
                "evidence_count": len(benefit.legal_evidence),
                "laws": sorted(
                    {
                        (item.law_id, item.law_title, item.validity)
                        for item in benefit.legal_evidence
                    }
                ),
                "sample_sections": [
                    {
                        "section_id": item.section_id,
                        "heading": item.heading,
                        "text": item.text,
                    }
                    for item in benefit.legal_evidence[:3]
                ],
            }
        )

    print(json.dumps({"benefits": output}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
