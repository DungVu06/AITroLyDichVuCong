"""Demo pipeline đến bước Gemini sinh câu trả lời."""

from __future__ import annotations

import argparse
import json
import sys

from rag.demos.context import create_context
from rag.generation.answer import generate_answer


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Demo RAG answer generation.")
    parser.add_argument("text", help="Câu hỏi của người dùng")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    response = generate_answer(create_context(args.text, args.limit))
    print(json.dumps(response.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
