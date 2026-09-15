"""Chuẩn hóa procedure records và resolve các thủ tục, lợi ích liên quan.

Input mặc định:
    data/procedure/records/PROC_*.json

Output mặc định:
    data/procedure/normalized_records/PROC_*.json
    data/procedure/normalized_relation_report.json
    data/procedure/procedure_relations.json
"""

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parents[2]


def clean_text(value: Any) -> str:
    """Gộp whitespace và bỏ dấu chấm/khoảng trắng thừa cuối chuỗi."""
    if value is None:
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text.rstrip(".;, ")


def remove_raw_fields(value: Any) -> Any:
    """Xóa đệ quy mọi field có hậu tố _raw sau khi đã chuẩn hóa."""
    if isinstance(value, dict):
        return {
            key: remove_raw_fields(item)
            for key, item in value.items()
            if not key.endswith("_raw")
        }
    if isinstance(value, list):
        return [remove_raw_fields(item) for item in value]
    return value


def normalize_record(
    record: dict[str, Any],
    valid_ids: set[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    normalized = copy.deepcopy(record)
    procedure = normalized.setdefault("procedure", {})
    jurisdiction = normalized.setdefault("jurisdiction", {})
    source = normalized.setdefault("source", {})

    normalized["domain"] = clean_text(normalized.get("domain"))
    normalized["procedure_type"] = clean_text(normalized.get("procedure_type"))
    normalized["life_event"] = [clean_text(x) for x in normalized.get("life_event", [])]
    normalized["target_audience"] = [clean_text(x) for x in normalized.get("target_audience", [])]
    normalized["normalization_version"] = "procedure-normalize-v1"

    for key in ("name", "eligibility", "authority", "online_portal_url"):
        if key in procedure:
            procedure[key] = clean_text(procedure[key])

    if "steps" in procedure:
        procedure["steps"] = [clean_text(step) for step in procedure["steps"]]

    for key in ("level", "location"):
        if key in jurisdiction:
            jurisdiction[key] = clean_text(jurisdiction[key])

    for key in ("url", "name", "effective_date", "last_updated"):
        if key in source:
            source[key] = clean_text(source[key])

    relations_data = normalized.get("relations", {})
    relation_types = ["prerequisites", "next_steps", "sub_procedures", "part_of", "related_benefits"]
    
    source_id = clean_text(normalized.get("id"))
    edges = []

    for rel_type in relation_types:
        targets = relations_data.get(rel_type, [])
        for target in targets:
            target_id = clean_text(target)
            if not target_id:
                continue

            # Các ID thuộc loại Benefit (BEN_) thường sẽ được đưa sang một entity khác,
            # tạm thời xem như là resolved nếu có prefix BEN_ hoặc nằm trong valid_ids
            status = "resolved" if target_id in valid_ids or target_id.startswith("BEN_") else "unresolved"

            edge = {
                "source_id": source_id,
                "target_id": target_id,
                "relation_type": rel_type,
                "resolution_status": status,
            }
            edges.append(edge)

    return remove_raw_fields(normalized), edges


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT_DIR / "data/procedure/records")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT_DIR / "data/procedure/normalized_records",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT_DIR / "data/procedure/normalized_relation_report.json",
    )
    parser.add_argument(
        "--relations",
        type=Path,
        default=ROOT_DIR / "data/procedure/procedure_relations.json",
    )
    args = parser.parse_args()

    files = sorted(args.input_dir.glob("PROC_*.json"))
    # Thêm fallback nếu thư mục records không có
    if not files and (ROOT_DIR / "data/procedure").exists():
        files = sorted((ROOT_DIR / "data/procedure").glob("PROC_*.json"))

    if not files:
        raise SystemExit(f"Không tìm thấy PROC_*.json trong {args.input_dir}")

    records = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    valid_ids = {clean_text(record.get("id")) for record in records if record.get("id")}

    args.output_dir.mkdir(parents=True, exist_ok=True)
    all_relations = []
    resolved = unresolved = 0

    for record in records:
        normalized, edges = normalize_record(record, valid_ids)
        output_path = args.output_dir / f"{normalized['id']}.json"
        output_path.write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        all_relations.extend(edges)
        resolved += sum(1 for e in edges if e["resolution_status"] == "resolved")
        unresolved += sum(1 for e in edges if e["resolution_status"] == "unresolved")

    # Báo cáo tổng thể tất cả các relation
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(all_relations, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Lọc lại chỉ ghi các relation đã được resolve để dùng cho neo4j
    deduped_edges = []
    seen = set()
    for edge in all_relations:
        key = (edge["source_id"], edge["target_id"], edge["relation_type"])
        if key not in seen:
            seen.add(key)
            if edge["resolution_status"] == "resolved":
                deduped_edges.append(edge)

    args.relations.parent.mkdir(parents=True, exist_ok=True)
    args.relations.write_text(
        json.dumps(deduped_edges, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Đã chuẩn hóa {len(records)} records vào: {args.output_dir}")
    print(f"Tham chiếu: {len(all_relations)} | resolved={resolved} | unresolved={unresolved}")
    print(f"Báo cáo: {args.report}")
    print(f"Relations: {args.relations}")


if __name__ == "__main__":
    main()
