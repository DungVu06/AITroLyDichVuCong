"""Hiển thị journey và evidence từ chính pipeline ứng dụng."""
import argparse
import json
import sys

from rag.engine import build_context


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Xem context và journey của pipeline.")
    parser.add_argument("text", help="Câu hỏi người dùng")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    context = build_context(args.text, limit=args.limit)
    print(json.dumps(context.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
