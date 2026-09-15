"""Tạo relation JSON từ relations.related_benefit để import vào Neo4j.

Input:
    data/procedure/normalized_records/PROC_*.json
    data/law/normalized_records/LAW_*.json

Mỗi related_benefit có thể là chuỗi section ID hoặc object:

    "related_benefit": [
      "LAW_VBPL_xxx/part:B/section:I"
    ]

Hoặc:

    "related_benefit": [
      {
        "law_section_id": "LAW_VBPL_xxx/part:B/section:I",
        "scope": "subtree",
        "note": "Chế độ trợ cấp liên quan"
      }
    ]

Chuỗi đơn giản mặc định có scope ``subtree``. Script chỉ ghi các relation
đã resolve vào file output dùng cho Neo4j; mọi lỗi vẫn được ghi vào report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
VALID_SCOPES = {"self", "subtree"}


def clean(value: Any) -> str:
    return str(value or "").strip()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"JSON phải là object: {path}")
    return data


def read_records(directory: Path, pattern: str) -> list[dict[str, Any]]:
    return [read_json(path) for path in sorted(directory.glob(pattern))]


def build_section_index(
    law_records: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    """Trả về index section_id -> metadata và law_id -> title."""
    sections: dict[str, dict[str, str]] = {}
    laws: dict[str, str] = {}

    for record in law_records:
        law_id = clean(record.get("id"))
        content = record.get("content") or {}
        if not law_id or not isinstance(content, dict):
            continue
        laws[law_id] = clean(content.get("title"))

        for section in content.get("sections") or []:
            if not isinstance(section, dict):
                continue
            section_id = clean(section.get("normalized_id"))
            if not section_id:
                continue
            sections[section_id] = {
                "law_id": law_id,
                "heading": clean(section.get("heading")),
                "level": clean(section.get("level")),
            }

    return sections, laws


def parse_related_benefit(item: Any) -> tuple[str, str, str, str]:
    """Lấy (section_id, scope, note, benefit_id) từ một annotation."""
    if isinstance(item, str):
        return clean(item), "subtree", "", ""

    if not isinstance(item, dict):
        return "", "", "", ""

    section_id = clean(
        item.get("law_section_id")
        or item.get("section_id")
        or item.get("target_section_id")
    )
    scope = clean(item.get("scope")) or "subtree"
    note = clean(item.get("note"))
    benefit_id = clean(item.get("benefit_id"))
    return section_id, scope, note, benefit_id


def create_relations(
    procedure_dir: Path,
    law_dir: Path,
    output_path: Path,
    report_path: Path,
) -> tuple[int, int, int]:
    procedures = read_records(procedure_dir, "PROC_*.json")
    law_records = read_records(law_dir, "LAW_*.json")
    if not procedures:
        raise SystemExit(f"Không tìm thấy PROC_*.json trong {procedure_dir}")
    if not law_records:
        raise SystemExit(f"Không tìm thấy LAW_*.json trong {law_dir}")

    section_index, _law_index = build_section_index(law_records)
    report: list[dict[str, Any]] = []
    resolved: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for record in procedures:
        procedure_id = clean(record.get("id"))
        relations = record.get("relations") or {}
        annotations = relations.get("related_benefit", []) if isinstance(relations, dict) else []

        if not isinstance(annotations, list):
            report.append(
                {
                    "procedure_id": procedure_id,
                    "relation_type": "related_benefit",
                    "resolution_status": "invalid_format",
                    "message": "relations.related_benefit phải là array",
                }
            )
            continue

        for index, item in enumerate(annotations):
            section_id, scope, note, benefit_id = parse_related_benefit(item)
            base = {
                "source_id": procedure_id,
                "target_section_id": section_id,
                "relation_type": "related_benefit",
                "scope": scope,
                "source": "manual",
                "note": note,
            }
            if benefit_id:
                base["benefit_id"] = benefit_id

            if not procedure_id:
                base.update(
                    resolution_status="invalid_procedure_id",
                    annotation_index=index,
                )
                report.append(base)
                continue
            if not section_id:
                base.update(
                    resolution_status="missing_section_id",
                    annotation_index=index,
                )
                report.append(base)
                continue
            if scope not in VALID_SCOPES:
                base.update(
                    resolution_status="invalid_scope",
                    annotation_index=index,
                    message=f"scope phải là một trong {sorted(VALID_SCOPES)}",
                )
                report.append(base)
                continue
            if section_id not in section_index:
                base.update(
                    resolution_status="unresolved_section",
                    annotation_index=index,
                )
                report.append(base)
                continue

            section_meta = section_index[section_id]
            relation_key = (procedure_id, section_id)
            if relation_key in seen:
                base.update(
                    resolution_status="duplicate",
                    law_id=section_meta["law_id"],
                    annotation_index=index,
                )
                report.append(base)
                continue

            seen.add(relation_key)
            base.update(
                {
                    "law_id": section_meta["law_id"],
                    "section_heading": section_meta["heading"],
                    "section_level": section_meta["level"],
                    "resolution_status": "resolved",
                }
            )
            report.append(base)
            resolved.append(base)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(resolved, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    unresolved_count = sum(
        1 for item in report if item.get("resolution_status") != "resolved"
    )
    return len(report), len(resolved), unresolved_count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--procedure-dir",
        type=Path,
        default=ROOT_DIR / "data" / "procedure" / "normalized_records",
    )
    parser.add_argument(
        "--law-dir",
        type=Path,
        default=ROOT_DIR / "data" / "law" / "normalized_records",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT_DIR / "data" / "relations" / "related_benefit_relations.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT_DIR
        / "data"
        / "relations"
        / "related_benefit_relation_report.json",
    )
    args = parser.parse_args()

    total, resolved, unresolved = create_relations(
        args.procedure_dir,
        args.law_dir,
        args.output,
        args.report,
    )
    print(f"Đã xử lý {total} related_benefit annotation.")
    print(f"Resolved: {resolved} | unresolved/invalid/duplicate: {unresolved}")
    print(f"Relations dùng cho Neo4j: {args.output}")
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
