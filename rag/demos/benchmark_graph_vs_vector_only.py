"""CLI benchmark: Graph-RAG versus vector-only RAG on five fixed demo cases.

Run from repository root:
    .\\.venv\\Scripts\\python.exe -m rag.demos.benchmark_graph_vs_vector_only

The control arm retains the same Qdrant retrieval, answer contract, prompt and
validator.  It disables Neo4j and the bundled graph snapshot, so relation,
dependency and graph-expanded benefit/law evidence are unavailable by design.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rag.engine import RAGEngine


ROOT = Path(__file__).resolve().parent
CASES_PATH = ROOT / "graph_vs_vector_only_cases.json"
RESULTS_DIR = ROOT / "results"
CITATION = re.compile(r"【([^】]+)】")
MODES = ("graph", "vector_only")


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    title: str
    question: str
    required_citations: list[str]
    required_term_groups: list[list[str]]
    forbidden_citations: list[str]
    forbidden_term_groups: list[list[str]] = field(default_factory=list)


@dataclass
class ApiCall:
    elapsed_seconds: float
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None


class GeminiUsageRecorder:
    """Records actual returned Gemini usage without changing production code."""

    def __init__(self, min_interval_seconds: float) -> None:
        self.min_interval_seconds = min_interval_seconds
        self.calls: list[ApiCall] = []
        self._last_request_at = 0.0
        self._original_client: Any = None
        self._genai: Any = None

    def __enter__(self) -> "GeminiUsageRecorder":
        from google import genai

        self._genai = genai
        self._original_client = genai.Client
        recorder = self
        original_client = self._original_client

        class InteractionsProxy:
            def __init__(self, interactions: Any) -> None:
                self._interactions = interactions

            def create(self, *args: Any, **kwargs: Any) -> Any:
                remaining = recorder.min_interval_seconds - (time.perf_counter() - recorder._last_request_at)
                if remaining > 0:
                    time.sleep(remaining)
                started = time.perf_counter()
                try:
                    return self._record(self._interactions.create(*args, **kwargs), started)
                finally:
                    recorder._last_request_at = time.perf_counter()

            @staticmethod
            def _usage_value(usage: Any, field: str) -> int | None:
                value = getattr(usage, field, None) if usage is not None else None
                return int(value) if isinstance(value, int) else None

            def _record(self, response: Any, started: float) -> Any:
                usage = getattr(response, "usage", None)
                recorder.calls.append(
                    ApiCall(
                        elapsed_seconds=round(time.perf_counter() - started, 4),
                        input_tokens=self._usage_value(usage, "total_input_tokens"),
                        output_tokens=self._usage_value(usage, "total_output_tokens"),
                        total_tokens=self._usage_value(usage, "total_tokens"),
                    )
                )
                return response

            def __getattr__(self, name: str) -> Any:
                return getattr(self._interactions, name)

        class ClientProxy:
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                self._client = original_client(*args, **kwargs)
                self.interactions = InteractionsProxy(self._client.interactions)

            def __getattr__(self, name: str) -> Any:
                return getattr(self._client, name)

        genai.Client = ClientProxy
        return self

    def __exit__(self, *_: object) -> None:
        if self._genai is not None and self._original_client is not None:
            self._genai.Client = self._original_client

    def mark(self) -> int:
        return len(self.calls)

    def summary_since(self, mark: int) -> dict[str, int | float | None]:
        calls = self.calls[mark:]
        def total(field: str) -> int | None:
            values = [getattr(call, field) for call in calls]
            return sum(value for value in values if value is not None) if any(value is not None for value in values) else None
        return {
            "api_calls": len(calls),
            "api_elapsed_seconds": round(sum(call.elapsed_seconds for call in calls), 3),
            "input_tokens": total("input_tokens"),
            "output_tokens": total("output_tokens"),
            "total_tokens": total("total_tokens"),
        }


def load_cases(path: Path) -> list[BenchmarkCase]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [BenchmarkCase(**row) for row in rows]


def evaluate(case: BenchmarkCase, answer: str, warnings: list[str]) -> dict[str, Any]:
    citations = set(CITATION.findall(answer))
    normalized = answer.casefold()
    missing_citations = [item for item in case.required_citations if item not in citations]
    matched_groups = [
        next((term for term in group if term.casefold() in normalized), None)
        for group in case.required_term_groups
    ]
    missing_term_groups = [
        group for group, matched in zip(case.required_term_groups, matched_groups) if matched is None
    ]
    forbidden_citations = [item for item in case.forbidden_citations if item in citations]
    matched_forbidden_groups = [
        next((term for term in group if term.casefold() in normalized), None)
        for group in case.forbidden_term_groups
    ]
    forbidden_terms = [
        group for group, matched in zip(case.forbidden_term_groups, matched_forbidden_groups)
        if matched is not None
    ]
    fallback = any("câu trả lời dự phòng" in warning.casefold() for warning in warnings)
    checks = (len(case.required_citations) + len(case.required_term_groups)
              + len(case.forbidden_citations) + len(case.forbidden_term_groups))
    passed = (
        len(case.required_citations) - len(missing_citations)
        + len(case.required_term_groups) - len(missing_term_groups)
        + len(case.forbidden_citations) - len(forbidden_citations)
        + len(case.forbidden_term_groups) - len(forbidden_terms)
    )
    return {
        "score": round(100 * passed / checks, 1) if checks else 100.0,
        "citations": sorted(citations),
        "missing_citations": missing_citations,
        "missing_term_groups": missing_term_groups,
        "forbidden_citations": forbidden_citations,
        "forbidden_terms": forbidden_terms,
        "fallback": fallback,
        "passed_checks": passed,
        "total_checks": checks,
    }


def run_case(
    engine: RAGEngine,
    case: BenchmarkCase,
    recorder: GeminiUsageRecorder,
) -> dict[str, Any]:
    mark = recorder.mark()
    started = time.perf_counter()
    try:
        response = engine.run(case.question, conversation_id=None)
        elapsed = round(time.perf_counter() - started, 3)
        result = {
            "status": "ok",
            "latency_seconds": elapsed,
            "answer": response.answer_markdown,
            "warnings": response.warnings,
            "sources": [item.source_id for item in response.sources],
        }
        result.update(evaluate(case, response.answer_markdown, response.warnings))
    except Exception as exc:  # report a failed arm/case instead of aborting all ten runs
        result = {
            "status": "error",
            "latency_seconds": round(time.perf_counter() - started, 3),
            "error": f"{type(exc).__name__}: {exc}",
            "answer": "",
            "warnings": [],
            "sources": [],
            "score": 0.0,
            "citations": [],
            "missing_citations": case.required_citations,
            "missing_term_groups": case.required_term_groups,
            "forbidden_citations": [],
            "forbidden_terms": [],
            "fallback": False,
            "passed_checks": 0,
            "total_checks": (len(case.required_citations) + len(case.required_term_groups)
                             + len(case.forbidden_citations) + len(case.forbidden_term_groups)),
        }
    result["usage"] = recorder.summary_since(mark)
    return result


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok_rows = [row for row in rows if row["status"] == "ok"]
    def mean(field: str) -> float | None:
        return round(statistics.mean(row[field] for row in ok_rows), 3) if ok_rows else None
    def sum_usage(field: str) -> int | None:
        values = [row["usage"][field] for row in rows]
        return sum(value for value in values if value is not None) if any(value is not None for value in values) else None
    return {
        "completed_cases": len(ok_rows),
        "mean_score": mean("score"),
        "mean_latency_seconds": mean("latency_seconds"),
        "total_api_calls": sum(row["usage"]["api_calls"] for row in rows),
        "total_input_tokens": sum_usage("input_tokens"),
        "total_output_tokens": sum_usage("output_tokens"),
        "total_tokens": sum_usage("total_tokens"),
    }


def errors_by_mode(results: dict[str, list[dict[str, Any]]]) -> dict[str, Counter[str]]:
    grouped: dict[str, Counter[str]] = {}
    for mode, rows in results.items():
        counter: Counter[str] = Counter()
        for row in rows:
            if row["status"] == "error":
                counter[f"run_error: {row['error']}"] += 1
            for citation in row["missing_citations"]:
                counter[f"missing_citation: {citation}"] += 1
            for terms in row["missing_term_groups"]:
                counter[f"missing_content: {' | '.join(terms)}"] += 1
            for citation in row["forbidden_citations"]:
                counter[f"forbidden_citation: {citation}"] += 1
            for terms in row.get("forbidden_terms", []):
                counter[f"forbidden_content: {' | '.join(terms)}"] += 1
            if row["fallback"]:
                counter["fallback_answer"] += 1
        grouped[mode] = counter
    return grouped


def render_evaluation(payload: dict[str, Any]) -> str:
    lines = [
        "# Yêu cầu cải tiến 3 — Đối chứng Graph-RAG và RAG không đồ thị",
        "",
        f"- Thời điểm UTC: {payload['created_at']}",
        f"- Model: `{payload['model']}`",
        f"- Dataset: 5 ca cố định trong `rag/demos/graph_vs_vector_only_cases.json`.",
        "- Control arm bỏ toàn bộ Neo4j/SnapshotGraph; các thành phần còn lại được giữ nguyên.",
        "- Theo phạm vi thử đã chốt: đối chứng Graph-RAG với RAG không đồ thị; không có arm tra cứu thủ công.",
        "- Token chỉ được ghi khi Gemini trả `interaction.usage`; `N/A` nghĩa là API không trả usage, không phải 0 token.",
        "",
        "## Bảng kết quả đối chứng",
        "",
        "| Ca | Graph score | Vector-only score | Graph latency (s) | Vector latency (s) | Graph API/token | Vector API/token |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    graph_rows = {row["case_id"]: row for row in payload["results"]["graph"]}
    vector_rows = {row["case_id"]: row for row in payload["results"]["vector_only"]}
    for case in payload["cases"]:
        graph = graph_rows.get(case["id"])
        vector = vector_rows.get(case["id"])
        def cell(row: dict[str, Any]) -> str:
            usage = row["usage"]
            tokens = usage["total_tokens"] if usage["total_tokens"] is not None else "N/A"
            return f"{usage['api_calls']} / {tokens}"
        def score(row: dict[str, Any] | None) -> str:
            return f"{row['score']:.1f}" if row else "N/A"
        def latency(row: dict[str, Any] | None) -> str:
            return f"{row['latency_seconds']:.3f}" if row else "N/A"
        lines.append(
            f"| {case['id']} – {case['title']} | {score(graph)} | {score(vector)} | "
            f"{latency(graph)} | {latency(vector)} | {cell(graph) if graph else 'N/A'} | {cell(vector) if vector else 'N/A'} |"
        )
    lines += ["", "## Tổng hợp", "", "| Chỉ số | Graph-RAG | Vector-only |", "|---|---:|---:|"]
    graph_summary = payload["summary"]["graph"]
    vector_summary = payload["summary"]["vector_only"]
    for label, field in (
        ("Ca hoàn tất", "completed_cases"),
        ("Điểm trung bình / 100", "mean_score"),
        ("Latency trung bình (s)", "mean_latency_seconds"),
        ("Tổng Gemini calls", "total_api_calls"),
        ("Input tokens", "total_input_tokens"),
        ("Output tokens", "total_output_tokens"),
        ("Total tokens", "total_tokens"),
    ):
        left, right = graph_summary[field], vector_summary[field]
        lines.append(f"| {label} | {left if left is not None else 'N/A'} | {right if right is not None else 'N/A'} |")
    lines += ["", "## Lỗi điển hình theo rubric", ""]
    for mode in MODES:
        lines.append(f"### {mode}")
        errors = payload["typical_errors"][mode]
        if not errors:
            lines.append("- Không có lỗi rubric trong lượt chạy này.")
        else:
            lines.extend(f"- `{error}`: {count} ca" for error, count in errors)
        lines.append("")
    lines += [
        "## Phạm vi và giới hạn thử",
        "",
        "- Chỉ 5 tình huống demo sinh con; không đại diện toàn bộ thủ tục hành chính.",
        "- Mỗi arm chạy một lần mỗi ca. Kết quả sinh ngôn ngữ của LLM có dao động; muốn kết luận ổn định phải lặp nhiều vòng và lấy trung bình.",
        "- Accuracy ở đây là rubric evidence/nội dung định trước, không phải phán quyết pháp lý toàn diện hay đánh giá bởi chuyên gia.",
        "- Latency gồm LLM, embedding, Qdrant và (ở arm graph) Neo4j; môi trường mạng làm số đo thay đổi.",
        "- `vector_only` vẫn dùng cùng contract và evidence retrieval để cô lập đóng góp của graph; đây không phải baseline RAG tối giản hoàn toàn.",
        "- Không tự kiểm tra website nguồn hay cập nhật hiệu lực văn bản trong benchmark này.",
        "",
    ]
    return "\n".join(lines)


def render_answer_log(payload: dict[str, Any]) -> str:
    """Create a human-readable audit trail for all five questions and both arms."""
    lines = [
        "# Nhật ký 10 câu trả lời — Graph-RAG vs RAG không đồ thị",
        "",
        f"- Thời điểm chạy UTC: {payload['created_at']}",
        f"- Model: `{payload['model']}`",
        "- Mỗi ca được chạy độc lập; không mang hội thoại từ ca trước.",
        "- Câu trả lời dưới đây là output nguyên văn đã được lưu từ 10 lượt chạy.",
        "",
    ]
    by_mode = {
        mode: {row["case_id"]: row for row in payload["results"].get(mode, [])}
        for mode in MODES
    }
    display_names = {"graph": "Graph-RAG", "vector_only": "RAG không đồ thị (vector-only)"}
    for case in payload["cases"]:
        lines.extend([f"## {case['id']} — {case['title']}", "", "### Câu hỏi", "", case["question"], ""])
        lines.extend([
            "### Rubric đối chiếu",
            "",
            f"- Citation bắt buộc: {', '.join(f'`{item}`' for item in case['required_citations']) or 'Không có'}.",
            f"- Nội dung cần có: {'; '.join(' / '.join(group) for group in case['required_term_groups']) or 'Không có'}.",
            f"- Citation không được xuất hiện: {', '.join(f'`{item}`' for item in case['forbidden_citations']) or 'Không có'}.",
            f"- Nội dung không được khẳng định: {'; '.join(' / '.join(group) for group in case.get('forbidden_term_groups', [])) or 'Không có'}.",
            "",
        ])
        for mode in MODES:
            row = by_mode[mode].get(case["id"])
            lines.extend([f"### Trả lời — {display_names[mode]}", ""])
            if not row:
                lines.extend(["Không chạy arm này.", ""])
                continue
            if row["status"] == "error":
                lines.extend([f"**Lỗi run:** `{row['error']}`", ""])
                continue
            # A model occasionally emits escaped newlines inside a JSON string.
            # Decode only that presentation artifact in the human audit file.
            lines.extend([row["answer"].replace("\\n", "\n"), ""])
            usage = row["usage"]
            lines.extend([
                "#### Quan sát benchmark",
                "",
                f"- Điểm rubric: **{row['score']:.1f}/100** ({row['passed_checks']}/{row['total_checks']} checks).",
                f"- Latency end-to-end: **{row['latency_seconds']:.3f}s**.",
                f"- Gemini: **{usage['api_calls']} calls**, input `{usage['input_tokens'] if usage['input_tokens'] is not None else 'N/A'}`, output `{usage['output_tokens'] if usage['output_tokens'] is not None else 'N/A'}`, total `{usage['total_tokens'] if usage['total_tokens'] is not None else 'N/A'}` tokens.",
                f"- Citation bị thiếu theo rubric: {', '.join(f'`{item}`' for item in row['missing_citations']) or 'Không có'}.",
                f"- Citation sai/không được phép: {', '.join(f'`{item}`' for item in row['forbidden_citations']) or 'Không có'}.",
                f"- Fallback: {'Có' if row['fallback'] else 'Không'}.",
            ])
            if row["warnings"]:
                lines.append(f"- Warning: {' | '.join(row['warnings'])}.")
            lines.append("")
        lines.extend(["---", ""])
    return "\n".join(lines)


def write_artifacts(payload: dict[str, Any], output_dir: Path, stem: str) -> tuple[Path, Path]:
    """Keep raw JSON and export separate answer and evaluation Markdown files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    answers_path = output_dir / f"{stem}_answers.md"
    evaluation_path = output_dir / f"{stem}_evaluation.md"
    answers_path.write_text(render_answer_log(payload), encoding="utf-8")
    evaluation_path.write_text(render_evaluation(payload), encoding="utf-8")
    return answers_path, evaluation_path


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Đối chứng Graph-RAG và vector-only RAG trên 5 ca demo.")
    parser.add_argument("--cases", type=Path, default=CASES_PATH, help="File JSON chứa 5 ca và rubric.")
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR, help="Thư mục tạo report JSON/Markdown mới.")
    parser.add_argument("--min-api-interval", type=float, default=4.2, help="Khoảng cách tối thiểu giữa Gemini calls (mặc định 4.2 giây).")
    parser.add_argument("--mode", choices=("both", *MODES), default="both", help="Chạy cả hai arm hoặc chỉ một arm để debug.")
    parser.add_argument("--render-existing", type=Path, help="Chỉ render Markdown từ JSON benchmark đã có; không gọi API.")
    args = parser.parse_args()
    if args.render_existing:
        payload = json.loads(args.render_existing.read_text(encoding="utf-8"))
        answers_path, evaluation_path = write_artifacts(
            payload,
            args.output_dir,
            args.render_existing.stem,
        )
        print(f"Đã lưu 10 câu hỏi/đáp: {answers_path}")
        print(f"Đã lưu bảng đánh giá: {evaluation_path}")
        return
    if args.min_api_interval < 0:
        parser.error("--min-api-interval phải >= 0")
    cases = load_cases(args.cases)
    modes = MODES if args.mode == "both" else (args.mode,)
    results: dict[str, list[dict[str, Any]]] = {}
    with GeminiUsageRecorder(args.min_api_interval) as recorder:
        for mode in modes:
            print(f"\n=== {mode} ===")
            engine = RAGEngine(retrieval_mode=mode)
            results[mode] = []
            for case in cases:
                print(f"{mode} {case.id}: ", end="", flush=True)
                row = run_case(engine, case, recorder)
                row["case_id"] = case.id
                row["case_title"] = case.title
                results[mode].append(row)
                print(f"{row['status']}; score={row['score']:.1f}; latency={row['latency_seconds']:.3f}s")

    # Keep report shape stable when an operator deliberately runs just one arm.
    for mode in MODES:
        results.setdefault(mode, [])
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": os.environ.get("GEMINI_QUERY_MODEL", "gemini-3.5-flash-lite"),
        "cases": [asdict(case) for case in cases],
        "results": results,
        "summary": {mode: aggregate(results[mode]) for mode in MODES},
        "typical_errors": {mode: errors_by_mode(results)[mode].most_common() for mode in MODES},
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = args.output_dir / f"graph_vs_vector_only_{stamp}.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    answers_path, evaluation_path = write_artifacts(payload, args.output_dir, json_path.stem)
    print(f"\nĐã lưu 10 câu hỏi/đáp: {answers_path}")
    print(f"Đã lưu bảng đánh giá: {evaluation_path}")
    print(f"Đã lưu dữ liệu chi tiết: {json_path}")


if __name__ == "__main__":
    main()
