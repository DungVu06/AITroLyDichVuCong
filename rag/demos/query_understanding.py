"""Quan sát intent và facts do Gemini trích xuất."""

from __future__ import annotations

import argparse
import sys

from rag.core.schemas import UserQuery
from rag.pipeline.preprocessing import preprocess_query
from rag.pipeline.query_understanding import understand_query


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Demo Gemini hiểu câu hỏi.")
    parser.add_argument("text", help="Câu hỏi của người dùng")
    parser.add_argument("--conversation-id", default=None)
    args = parser.parse_args()

    query = UserQuery(text=args.text, conversation_id=args.conversation_id)
    print(understand_query(preprocess_query(query)).model_dump_json(indent=2))


if __name__ == "__main__":
    main()
