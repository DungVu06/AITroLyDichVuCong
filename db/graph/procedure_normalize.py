"""Chuẩn hóa procedure records và resolve các thủ tục, lợi ích liên quan.

Input mặc định:
    data/procedure/records/PROC_*.json

Output mặc định:
    data/procedure/normalized_records/PROC_*.json
    data/procedure/normalized_relation_report.json (chỉ khi yêu cầu --report)
"""

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]


BIRTH = "PROC_1_001193"
RESIDENCE = "PROC_1_116788"
HEALTH = "PROC_1_014137"
CARD = "PROC_1_116410"
LINKED = "PROC_3_000722"
CARD_REQUESTED = "identity_card_requested"
LINKED_CARD_STEP = 5

# These references describe the local linked-service record. The text guards
# prevent a reordered or changed crawl from silently publishing an old edge.
LINKED_STEP_TERMS = {
    1: ("lựa chọn dịch vụ công liên thông", "nộp hồ sơ"),
    4: ("bản điện tử giấy khai sinh", "đăng ký thường trú", "bảo hiểm xã hội"),
    LINKED_CARD_STEP: ("có đề nghị cấp thẻ căn cước", "thông báo kết quả giải quyết đăng ký thường trú"),
}
LINKED_DEPENDENCIES = (
    (BIRTH, RESIDENCE, 4, "Giấy khai sinh điện tử"),
    (BIRTH, HEALTH, 4, "Giấy khai sinh điện tử"),
    (RESIDENCE, CARD, LINKED_CARD_STEP, "Thông báo kết quả đăng ký thường trú"),
)


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



def verify_procedure_relations(
    records: dict[str, dict[str, Any]],
    declared_edges: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Validate and qualify the graph against the normalized local records."""
    linked = records.get(LINKED, {})
    steps = linked.get("procedure", {}).get("steps", [])
    members = set(linked.get("relations", {}).get("sub_procedures", []))
    member_steps = {BIRTH: 1, RESIDENCE: 4, HEALTH: 4, CARD: LINKED_CARD_STEP}
    dependencies = {
        key: (step, result, target)
        for source, target, step, result in LINKED_DEPENDENCIES
        for key in ((source, target, "next_steps"), (target, source, "prerequisites"))
    }

    # A dependency written in the procedure text can be absent from the
    # legacy relations arrays, as with residence before the optional card.
    keys = {
        (edge["source_id"], edge["target_id"], edge["relation_type"])
        for edge in declared_edges
    }
    declared_edges = [
        *declared_edges,
        *(
            {"source_id": source, "target_id": target, "relation_type": kind}
            for source, target, kind in dependencies
            if (source, target, kind) not in keys and source in members and target in members
        ),
    ]
    report = []
    published = []
    seen = set()
    for edge in declared_edges:
        source = edge["source_id"]
        target = edge["target_id"]
        kind = edge["relation_type"]
        key = (source, target, kind)
        row = dict(edge, resolution_status="resolved")
        step = None
        result = None
        member = None
        if key in seen:
            row.update(resolution_status="duplicate", reason="Cạnh bị khai báo trùng.")
        elif source not in records or target not in records:
            row.update(resolution_status="unresolved", reason="Thiếu bản ghi cho ID của cạnh.")
        elif key in dependencies and source in members and target in members:
            step, result, member = dependencies[key]
        elif kind == "sub_procedures" and source == LINKED:
            member = target
            step = member_steps.get(member)
        elif kind == "part_of" and target == LINKED:
            member = source
            step = member_steps.get(member)
        elif kind in {"prerequisites", "next_steps"}:
            row.update(
                resolution_status="unverified",
                reason="Bản ghi chưa xác nhận quan hệ này trong phạm vi áp dụng.",
            )

        if step:
            terms = LINKED_STEP_TERMS[step]
            if step > len(steps) or not all(term in steps[step - 1].casefold() for term in terms):
                row.update(
                    resolution_status="unverified",
                    reason=f"{LINKED} Bước {step} thiếu nội dung xác nhận cạnh.",
                )
            else:
                row.update(workflow_id=LINKED, evidence_record_id=LINKED, evidence_step=step)
                if member == CARD:
                    row["condition"] = CARD_REQUESTED
                if result:
                    row["transferred_result"] = result
        elif member:
            row.update(resolution_status="unverified", reason="Chưa xác định bước của thủ tục thành phần.")

        seen.add(key)
        report.append(row)
        if row["resolution_status"] == "resolved":
            published.append(row)

    validate_dependency_cycles(set(records), published)
    return published, report


def validate_dependency_cycles(procedure_ids: set[str], edges: list[dict[str, Any]]) -> None:
    """Check the directed dependencies while ignoring membership and inverse duplicates."""
    remaining: dict[str, set[str]] = {procedure_id: set() for procedure_id in procedure_ids}
    for row in edges:
        source, target = row["source_id"], row["target_id"]
        if row["relation_type"] == "prerequisites":
            remaining[source].add(target)
        elif row["relation_type"] == "next_steps":
            remaining[target].add(source)
    while remaining:
        ready = {node for node, prerequisites in remaining.items() if not prerequisites}
        if not ready:
            raise ValueError(f"Chu trình phụ thuộc giữa các thủ tục: {', '.join(sorted(remaining))}")
        remaining = {
            node: prerequisites - ready for node, prerequisites in remaining.items() if node not in ready
        }

def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT_DIR / "data/procedure/records")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT_DIR / "data/procedure/normalized_records",
    )
    parser.add_argument("--report", type=Path, help="Đường dẫn JSON báo cáo, nếu cần rà soát")
    args = parser.parse_args()

    files = sorted(args.input_dir.glob("PROC_*.json"))
    if not files and (ROOT_DIR / "data/procedure").exists():
        files = sorted((ROOT_DIR / "data/procedure").glob("PROC_*.json"))

    if not files:
        raise SystemExit(f"Không tìm thấy PROC_*.json trong {args.input_dir}")

    records = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    valid_ids = {clean_text(record.get("id")) for record in records if record.get("id")}

    normalized_records = {}
    declared_edges = []
    for record in records:
        normalized, edges = normalize_record(record, valid_ids)
        procedure_id = normalized["id"]
        if not procedure_id or procedure_id in normalized_records:
            raise ValueError(f"ID thủ tục để trống hoặc trùng: {procedure_id!r}")
        normalized_records[procedure_id] = normalized
        declared_edges.extend(edges)

    published, report = verify_procedure_relations(normalized_records, declared_edges)
    for normalized in normalized_records.values():
        normalized["relations"]["resolved_edges"] = []
    for edge in published:
        source = normalized_records[edge["source_id"]]
        source["relations"]["resolved_edges"].append({
            key: value for key, value in edge.items() if key != "source_id"
        })
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for procedure_id, normalized in normalized_records.items():
        output_path = args.output_dir / f"{procedure_id}.json"
        output_path.write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Báo cáo: {args.report}")

    print(f"Đã chuẩn hóa {len(records)} records vào: {args.output_dir}")
    print(f"Tham chiếu: {len(report)} | đã xác nhận={len(published)} | cần kiểm tra={len(report) - len(published)}")


if __name__ == "__main__":
    main()
