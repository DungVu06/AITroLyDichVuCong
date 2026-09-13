"""Kiểm tra, in cây và cập nhật lại section trong data/law/records.

Mặc định script chỉ audit. Dùng --apply để tạo lại content.sections từ
content.full_text, đồng thời in cấu trúc đề mục của từng văn bản.

Ví dụ:
    venv/bin/python audit_law_sections.py
    venv/bin/python audit_law_sections.py --apply
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from crawl_law import classify_legal_heading, split_legal_sections, validate_section_split


ROOT_DIR = Path(__file__).resolve().parent
LEVEL_RANK = {
    "chapter": 1,
    "part": 2,
    "section": 3,
    "article": 4,
    "subsection": 5,
    "point": 6,
    "subpoint": 7,
}


def clean(value: Any) -> str:
    return str(value or "").strip()


def embedded_headings(sections: list[dict[str, Any]]) -> list[tuple[int, str]]:
    """Tìm heading còn bị dính trong text của một section khác."""
    found: list[tuple[int, str]] = []
    for index, section in enumerate(sections):
        for line in clean(section.get("text")).splitlines():
            if classify_legal_heading(line):
                found.append((index, line.strip()))
    return found


ROMAN_MARKER_RE = re.compile(r"^([IVXL]+)[.)\-–]\s+")
ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50}


def roman_to_int(marker: str) -> int:
    total = 0
    previous = 0
    for char in reversed(marker):
        value = ROMAN_VALUES[char]
        if value < previous:
            total -= value
        else:
            total += value
            previous = value
    return total


def hierarchy_warnings(sections: list[dict[str, Any]]) -> list[str]:
    """Phát hiện đề mục La Mã bị quay lại I trong cùng một phần cha.

    Đây thường là dấu hiệu heading cấp cao (ví dụ `B.`) đã thiếu ngay trong
    full_text nguồn; parser không nên tự đoán và chèn một heading không có.
    """
    warnings: list[str] = []
    stack: list[tuple[int, str]] = []
    last_roman_by_parent: dict[tuple[str, ...], int] = {}

    for index, section in enumerate(sections):
        level = clean(section.get("level"))
        rank = LEVEL_RANK.get(level, 99)
        while stack and stack[-1][0] >= rank:
            stack.pop()

        heading = clean(section.get("heading"))
        marker_match = ROMAN_MARKER_RE.match(heading)
        if level == "section" and marker_match:
            parent_key = tuple(item[1] for item in stack if item[0] < rank)
            marker = marker_match.group(1)
            value = roman_to_int(marker)
            previous = last_roman_by_parent.get(parent_key)
            if previous is not None and value <= previous:
                parent_label = " > ".join(parent_key) or "<root>"
                warnings.append(
                    f"section[{index}] {heading}: số La Mã quay lại sau "
                    f"{previous} dưới {parent_label}; có thể thiếu heading cấp cao"
                )
            last_roman_by_parent[parent_key] = value

        stack.append((rank, heading))
    return warnings


def render_tree(sections: list[dict[str, Any]]) -> list[str]:
    """Dựng cây dựa trên cấp heading đã parser nhận diện."""
    lines: list[str] = []
    stack: list[int] = []
    for section in sections:
        level = clean(section.get("level"))
        rank = LEVEL_RANK.get(level, 99)
        while stack and stack[-1] >= rank:
            stack.pop()
        lines.append(f"{'  ' * len(stack)}{clean(section.get('heading'))} [{level}]")
        stack.append(rank)
    return lines


def audit_record(path: Path, apply: bool) -> tuple[bool, bool]:
    """Audit một record, trả về (đạt kiểm tra, đã thay đổi file)."""
    record = json.loads(path.read_text(encoding="utf-8"))
    content = record.get("content") or {}
    full_text = clean(content.get("full_text"))
    if not full_text:
        print(f"[FAIL] {path.name}: thiếu content.full_text")
        return False, False

    previous = content.get("sections") or []
    sections = split_legal_sections(full_text)
    validation = validate_section_split(full_text, sections)
    embedded = embedded_headings(sections)
    hierarchy_issues = hierarchy_warnings(sections)
    passed = validation["is_lossless"] and not embedded and not hierarchy_issues

    status = "PASS" if passed else "FAIL"
    print(
        f"\n[{status}] {path.name} | stored={len(previous)} -> parsed={len(sections)} "
        f"| lossless={validation['is_lossless']} | embedded_heading={len(embedded)} "
        f"| hierarchy_warning={len(hierarchy_issues)}"
    )
    print(f"  {clean(content.get('title'))}")
    for line in render_tree(sections):
        print(f"  {line}")
    for section_index, heading in embedded:
        print(f"  WARNING section[{section_index}] còn heading trong text: {heading}")
    for warning in hierarchy_issues:
        print(f"  WARNING {warning}")

    changed = previous != sections
    if apply and changed:
        content["sections"] = sections
        record["content"] = content
        path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("  UPDATED content.sections")
    return passed, changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--records-dir",
        type=Path,
        default=ROOT_DIR / "data" / "law" / "records",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Ghi lại content.sections đã tách vào từng record",
    )
    args = parser.parse_args()

    paths = sorted(args.records_dir.glob("LAW_*.json"))
    if not paths:
        raise SystemExit(f"Không tìm thấy LAW_*.json trong {args.records_dir}")

    passed = changed = 0
    for path in paths:
        is_valid, is_changed = audit_record(path, args.apply)
        passed += int(is_valid)
        changed += int(is_changed)

    print(f"\nTổng kết: {passed}/{len(paths)} file đạt kiểm tra.")
    if args.apply:
        print(f"Đã cập nhật section của {changed} file.")
    if passed != len(paths):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
