"""Quan sát query state và kế hoạch truy xuất tương ứng."""

from __future__ import annotations

import argparse
import json
import sys

from rag.core.schemas import UserQuery
from rag.pipeline.preprocessing import preprocess_query
from rag.pipeline.query_understanding import understand_query
from rag.pipeline.routing import route_query


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Demo query understanding + router.")
    parser.add_argument("text", help="Câu hỏi của người dùng")
    args = parser.parse_args()

    query = preprocess_query(UserQuery(text=args.text))
    state = understand_query(query)
    plan = route_query(query, state)
    print(
        json.dumps(
            {
                "query_state": state.model_dump(mode="json"),
                "retrieval_plan": plan.model_dump(mode="json"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
