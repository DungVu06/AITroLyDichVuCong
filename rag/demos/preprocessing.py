"""Quan sát kết quả chuẩn hóa câu hỏi đầu vào."""

from __future__ import annotations

import argparse
import sys

from rag.core.schemas import UserQuery
from rag.pipeline.preprocessing import preprocess_query


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Demo tiền xử lý câu hỏi RAG.")
    parser.add_argument("text", help="Câu hỏi cần chuẩn hóa")
    parser.add_argument("--conversation-id", default=None)
    args = parser.parse_args()

    query = UserQuery(text=args.text, conversation_id=args.conversation_id)
    print(preprocess_query(query).model_dump_json(indent=2))


if __name__ == "__main__":
    main()
