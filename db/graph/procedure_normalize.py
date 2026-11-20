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
    """
    Chuẩn hóa một bản ghi procedure record:
    1. Làm sạch text các trường metadata, procedure, jurisdiction, source, version_control.
    2. Chuẩn hóa documents (giữ bat_buoc, ma_giay_to, so_luong, ten_giay_to).
    3. Chuẩn hóa execution_methods.
    4. Trích xuất các quan hệ Graph giữa các Procedure (prerequisites, next_steps, part_of, sub_procedures).
    5. Xử lý chuẩn relations.legal_bases và relations.related_benefits.
    """
    normalized = copy.deepcopy(record)
    procedure = normalized.setdefault("procedure", {})
    jurisdiction = normalized.setdefault("jurisdiction", {})
    source = normalized.setdefault("source", {})
    relations_data = normalized.setdefault("relations", {})

    # 1. Metadata root
    normalized["id"] = clean_text(normalized.get("id"))
    normalized["national_code"] = clean_text(normalized.get("national_code"))
    normalized["domain"] = clean_text(normalized.get("domain"))
    normalized["procedure_type"] = clean_text(normalized.get("procedure_type"))
    normalized["life_event"] = [clean_text(x) for x in normalized.get("life_event", []) if x]
    normalized["target_audience"] = [clean_text(x) for x in normalized.get("target_audience", []) if x]
    normalized["normalization_version"] = "procedure-normalize-v2"

    # 2. Chi tiết procedure
    for key in ("name", "eligibility", "authority", "online_portal_url"):
        if key in procedure:
            procedure[key] = clean_text(procedure[key])

    if "steps" in procedure and isinstance(procedure["steps"], list):
        procedure["steps"] = [clean_text(step) for step in procedure["steps"] if clean_text(step)]

    # Chuẩn hóa documents
    if "documents" in procedure and isinstance(procedure["documents"], list):
        clean_docs = []
        for doc in procedure["documents"]:
            if isinstance(doc, dict):
                clean_docs.append({
                    "ten_giay_to": clean_text(doc.get("ten_giay_to")),
                    "so_luong": clean_text(doc.get("so_luong")),
                    "bat_buoc": bool(doc.get("bat_buoc", False)),
                    "ma_giay_to": clean_text(doc.get("ma_giay_to"))
                })
        procedure["documents"] = clean_docs

    # Chuẩn hóa execution_methods
    if "execution_methods" in procedure and isinstance(procedure["execution_methods"], list):
        clean_methods = []
        for m in procedure["execution_methods"]:
            if isinstance(m, dict):
                clean_methods.append({
                    "method": clean_text(m.get("method")),
                    "processing_time": clean_text(m.get("processing_time")),
                    "fee": clean_text(m.get("fee")),
                    "description": clean_text(m.get("description"))
                })
        procedure["execution_methods"] = clean_methods

    # 3. Jurisdiction & Source
    for key in ("level", "location"):
        if key in jurisdiction:
            jurisdiction[key] = clean_text(jurisdiction[key])

    for key in ("url", "name", "effective_date", "last_updated"):
        if key in source:
            source[key] = clean_text(source[key])

    # 4. Version control (Quản lý phiên bản & hiệu lực)
    if "version_control" in normalized and isinstance(normalized["version_control"], dict):
        vc = normalized["version_control"]
        normalized["version_control"] = {
            "proposal_number": clean_text(vc.get("proposal_number")),
            "state": clean_text(vc.get("state", "ACTIVE")),
            "raw_id": clean_text(vc.get("raw_id"))
        }

    # 5. Quan hệ đồ thị (Knowledge Graph Edges)
    source_id = normalized["id"]
    edges = []

    # 5a. Quan hệ Procedure <-> Procedure (prerequisites, next_steps, part_of, sub_procedures)
    procedure_rel_types = ["prerequisites", "next_steps", "sub_procedures", "part_of"]
    for rel_type in procedure_rel_types:
        targets = relations_data.get(rel_type, [])
        clean_targets = []
        for target in targets:
            target_id = clean_text(target)
            if not target_id:
                continue
            clean_targets.append(target_id)
            status = "resolved" if target_id in valid_ids else "unresolved"
            edges.append({
                "source_id": source_id,
                "target_id": target_id,
                "relation_type": rel_type,
                "resolution_status": status,
            })
        relations_data[rel_type] = clean_targets

    # 5b. Căn cứ pháp lý (legal_bases): giữ nguyên mảng object [{"name": ..., "code": ...}]
    if "legal_bases" in relations_data and isinstance(relations_data["legal_bases"], list):
        clean_legal_bases = []
        for lb in relations_data["legal_bases"]:
            if isinstance(lb, dict):
                clean_legal_bases.append({
                    "name": clean_text(lb.get("name")),
                    "code": clean_text(lb.get("code"))
                })
        relations_data["legal_bases"] = clean_legal_bases

    # 5c. Quyền lợi liên quan (related_benefits): giữ nguyên mảng object hoặc ID
    if "related_benefits" in relations_data and isinstance(relations_data["related_benefits"], list):
        clean_benefits = []
        for ben in relations_data["related_benefits"]:
            if isinstance(ben, dict):
                clean_benefits.append({
                    "law_section_id": clean_text(ben.get("law_section_id")),
                    "scope": clean_text(ben.get("scope", "subtree")),
                    "note": clean_text(ben.get("note", ""))
                })
            elif isinstance(ben, str):
                target_id = clean_text(ben)
                if target_id:
                    clean_benefits.append(target_id)
        relations_data["related_benefits"] = clean_benefits

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
