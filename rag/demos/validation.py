"""Demo pipeline đến bước hậu kiểm câu trả lời."""

from __future__ import annotations

import argparse
import json
import sys

from rag.demos.context import create_context
from rag.generation.answer import generate_answer
from rag.generation.validator import validate_answer


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Demo RAG answer validation.")
    parser.add_argument("text", help="Câu hỏi của người dùng")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    response = generate_answer(create_context(args.text, args.limit))
    validation = validate_answer(response)
    print(
        json.dumps(
            {
                "answer_markdown": response.answer_markdown,
                "validation": validation.model_dump(mode="json"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
