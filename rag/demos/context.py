"""Demo pipeline đến bước tạo AnswerContext cho Gemini."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

from rag.engine import build_context


def create_context(text: str, limit: int = 5):
    return build_context(text, limit=limit)


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Demo RAG đến AnswerContext.")
    parser.add_argument("text", help="Câu hỏi của người dùng")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--full", action="store_true", help="In toàn bộ context")
    args = parser.parse_args()
    context = create_context(args.text, args.limit)

    if args.full:
        output = context.model_dump(mode="json")
    else:
        context_json = context.model_dump_json()
        output = {
            "query_state": context.query_state.model_dump(mode="json"),
            "journey_count": len(context.journey),
            "procedures": [
                {
                    "procedure_id": procedure.procedure_id,
                    "chunk_counts": dict(
                        Counter(chunk.chunk_type for chunk in procedure.chunks)
                    ),
                    "context_characters": sum(
                        len(chunk.text) for chunk in procedure.chunks
                    ),
                }
                for procedure in context.procedure_evidence
            ],
            "benefits": [
                {
                    "title": benefit.title,
                    "eligibility_status": benefit.eligibility_status,
                    "evidence_count": len(benefit.legal_evidence),
                }
                for benefit in context.benefits
            ],
            "response_rules": context.response_rules.model_dump(mode="json"),
            "total_context_characters": len(context_json),
        }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
