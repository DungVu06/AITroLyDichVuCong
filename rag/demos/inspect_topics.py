"""Chạy TC01 và TC05, lưu context thực tế cùng kết quả benchmark."""
import json
import sys
from pathlib import Path

import rag.engine as engine_module
from rag.demos.benchmark_graph_vs_vector_only import CASES_PATH, GeminiUsageRecorder, load_cases, run_case
from rag.engine import RAGEngine


def main():
    round_id = sys.argv[1]
    selected_ids = set(sys.argv[2:]) or {"TC01", "TC05"}
    cases = [case for case in load_cases(CASES_PATH) if case.id in selected_ids]
    engine = RAGEngine()
    original = engine_module.build_context
    captured = {}

    def capture(*args, **kwargs):
        context = original(*args, **kwargs)
        captured["context"] = context.model_dump(mode="json")
        return context

    engine_module.build_context = capture
    results = {}
    with GeminiUsageRecorder(4.2) as recorder:
        for case in cases:
            captured.clear()
            print("RUN", round_id, case.id, flush=True)
            result = run_case(engine, case, recorder)
            result["context"] = captured.get("context")
            results[case.id] = result
            print("RESULT", case.id, json.dumps({k: v for k, v in result.items() if k != "context"}, ensure_ascii=False), flush=True)
    path = Path("rag/demos/results") / f"topic_inspection_{round_id}.json"
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SAVED", path, flush=True)


if __name__ == "__main__":
    main()
