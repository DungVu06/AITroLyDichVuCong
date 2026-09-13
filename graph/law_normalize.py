"""Chuẩn hóa law records và resolve các văn bản được dẫn chiếu.

Input mặc định:
    data/law/records/LAW_*.json

Output mặc định:
    data/law/normalized_records/LAW_*.json
    data/law/normalized_relation_report.json
    data/law/law_relations.json

Không sửa file trong records/. Với mỗi related_laws, script bổ sung:
    - target_document_id: id của LawDocument nếu đã crawl được
    - target_section_ids: section đích nếu dẫn chiếu nêu rõ mục/điều/khoản
    - resolution_status: chỉ `resolved_section` mới đủ điều kiện tạo edge graph
    - reference_key: khóa ổn định cho tham chiếu chưa resolve
    - document_id / normalized_document_number / normalized_issued_date
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]


def clean_text(value: Any) -> str:
    """Gộp whitespace và bỏ dấu chấm/khoảng trắng thừa cuối chuỗi."""
    if value is None:
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text.rstrip(".;, ")


def normalize_number(value: Any) -> str:
    """Chuẩn hóa số hiệu nhưng không đổi thứ tự token pháp lý."""
    text = clean_text(value).upper()
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[.]+$", "", text)
    text = text.replace("–", "-").replace("—", "-")
    return text


def number_key(value: Any) -> str:
    """Khóa so khớp: 21-LB/TT và 21/TT-LB cùng thành 21|LB|TT."""
    tokens = re.findall(r"\d+|[A-ZĐ]+", normalize_number(value))
    numeric = [token for token in tokens if token.isdigit()]
    alphabetic = sorted(token for token in tokens if not token.isdigit())
    return "|".join(numeric + alphabetic)


def normalize_type(value: Any) -> str:
    return clean_text(value).casefold()


def parse_date(value: Any) -> str | None:
    """Đổi một số dạng ngày phổ biến trong record sang YYYY-MM-DD."""
    text = clean_text(value)
    if not text:
        return None

    match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
    if match:
        day, month, year = map(int, match.groups())
        return safe_date(year, month, day)

    match = re.search(
        r"(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})",
        text,
        re.IGNORECASE,
    )
    if match:
        day, month, year = map(int, match.groups())
        return safe_date(year, month, day)
    return None


def safe_date(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def reference_key(reference: dict[str, Any]) -> str:
    document_type = normalize_type(reference.get("document_type"))
    document_number = normalize_number(reference.get("document_number"))
    # Không đưa ngày vào khóa chính: cùng một văn bản thường được dẫn chiếu
    # nhiều lần, có lần ghi ngày và có lần không ghi ngày.
    return "|".join((document_type, number_key(document_number)))


def reference_id(reference: dict[str, Any]) -> str:
    digest = hashlib.sha1(reference_key(reference).encode("utf-8")).hexdigest()[:16]
    return f"LAWREF_{digest}"


LEVEL_RANK = {
    "chapter": 1,
    "part": 2,
    "section": 3,
    "article": 4,
    "subsection": 5,
    "point": 6,
    "subpoint": 7,
}


def infer_section_level(heading: Any, fallback_level: Any) -> str:
    """Chuẩn hóa level theo ký hiệu heading khi ký hiệu không mơ hồ.

    Một số record crawl cũ từng ghi ``a)`` là ``part`` hoặc ``section``.
    Với các ký hiệu chuẩn, heading đáng tin cậy hơn level cũ. Các heading
    không có ký hiệu rõ ràng vẫn giữ fallback để không làm mất cấu trúc.
    """
    text = clean_text(heading)
    if re.match(r"^CHƯƠNG\s+[IVXLCDM0-9]+", text, re.IGNORECASE):
        return "chapter"
    if re.match(r"^(?:MỤC\s+)?[IVXL]+[.)\-–](?:\s|$)", text, re.IGNORECASE):
        return "section"
    if re.match(r"^Điều\s+\d+", text, re.IGNORECASE):
        return "article"
    if re.match(r"^(?:[a-zđ]|\d+)\.\d+[.)](?:\s|$)", text, re.IGNORECASE):
        return "subpoint"
    if re.match(r"^[A-HĐ][.)\-–](?:\s|$)", text):
        return "part"
    if re.match(r"^\d+[.)\-–](?:\s|$)", text):
        return "subsection"
    if re.match(r"^[a-zđ][.)\-–](?:\s|$)", text, re.IGNORECASE):
        return "point"
    return clean_text(fallback_level) or "unknown"


def section_marker(heading: Any, level: Any, fallback_order: int) -> str:
    """Lấy ký hiệu pháp lý của heading: A, II, 12, a..."""
    text = clean_text(heading)
    level = clean_text(level)
    patterns = {
        "chapter": r"^CHƯƠNG\s+([IVXLCDM0-9]+)",
        "section": r"^(?:MỤC\s+)?([IVXL]+)[.)\-–]?(?:\s|$)",
        "article": r"^Điều\s+(\d+)",
        "part": r"^([A-HĐ])[.)\-–](?:\s|$)",
        "subsection": r"^(\d+)[.)\-–](?:\s|$)",
        "point": r"^([a-zđ])[.)\-–](?:\s|$)",
        "subpoint": r"^((?:[a-zđ]|\d+)\.\d+)[.)](?:\s|$)",
    }
    match = re.search(patterns.get(level, r"$^"), text, re.IGNORECASE)
    marker = match.group(1) if match else str(fallback_order + 1)
    return marker.upper() if level in {"chapter", "part", "section"} else marker.lower()


def build_section_hierarchy(
    law_id: str, sections: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Tạo section ID có đường dẫn phân cấp và parent_section_id ổn định."""
    hierarchy: list[dict[str, Any]] = []
    stack: list[dict[str, Any]] = []
    used_paths: dict[str, int] = {}

    for order, section in enumerate(sections):
        level = infer_section_level(section.get("heading"), section.get("level"))
        rank = LEVEL_RANK.get(level, 99)
        marker = section_marker(section.get("heading"), level, order)
        while stack and LEVEL_RANK.get(stack[-1]["level"], 99) >= rank:
            stack.pop()
        parent_id = stack[-1]["id"] if stack else None
        base_id = f"{parent_id}/{level}:{marker}" if parent_id else f"{law_id}/{level}:{marker}"
        occurrence = used_paths.get(base_id, 0) + 1
        used_paths[base_id] = occurrence
        section_id = base_id if occurrence == 1 else f"{base_id}~{occurrence}"
        item = {
            "id": section_id,
            "parent_section_id": parent_id,
            "structural_path": section_id.removeprefix(law_id + "/"),
            "level": level,
            "marker": marker,
            "order": order,
        }
        hierarchy.append(item)
        stack.append(item)
    return hierarchy


def law_lookup(
    records: list[dict[str, Any]], hierarchy_by_record: dict[str, list[dict[str, Any]]]
) -> dict[str, list[dict[str, Any]]]:
    """Tạo lookup theo số hiệu và kèm cấu trúc section của văn bản đích."""
    lookup: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        content = record.get("content") or {}
        law_id = clean_text(record.get("id"))
        document_number = normalize_number(content.get("document_number"))
        document_number_key = number_key(document_number)
        if law_id and document_number_key:
            lookup.setdefault(document_number_key, []).append(
                {
                    "record_id": law_id,
                    "document_id": document_number,
                    "document_type": normalize_type(content.get("document_type")),
                    "sections": hierarchy_by_record.get(law_id, []),
                }
            )
    return lookup


def parse_reference_location(value: Any) -> list[tuple[str, str]]:
    """Tách 'Khoản 1 Điều 2' hoặc 'Điều 3, Điều 4' thành các locator."""
    pattern = re.compile(
        r"\b(chương|mục|điều|khoản|điểm)\s+([A-Za-zÀ-ỹ0-9]+)", re.IGNORECASE
    )
    return [
        (kind.casefold(), marker.upper() if kind.casefold() in {"chương", "mục"} else marker.lower())
        for kind, marker in pattern.findall(clean_text(value))
    ]


def target_levels(location_kind: str) -> set[str]:
    return {
        "chương": {"chapter"},
        # "mục A" thường dẫn tới A./B. (part), nhưng cũng hỗ trợ Mục I.
        "mục": {"part", "section"},
        "điều": {"article"},
        "khoản": {"subsection"},
        "điểm": {"point"},
    }.get(location_kind, set())


def resolve_target_sections(
    target: dict[str, Any], referenced_location: Any
) -> tuple[list[str], str]:
    """Resolve locator sang section đích; không đoán khi thiếu locator."""
    locations = parse_reference_location(referenced_location)
    if not locations:
        return [], "location_missing"

    sections = target.get("sections") or []
    # Nếu locator cùng loại (Điều 3, Điều 4...), mỗi locator là một target.
    kinds = {kind for kind, _ in locations}
    if len(kinds) == 1:
        wanted = locations
        constraints: list[tuple[str, str]] = []
    else:
        # Khoản 1 Điều 2: target là cấp sâu nhất (Khoản), Điều là ràng buộc cha.
        deepest_rank = max(
            (max((LEVEL_RANK[level] for level in target_levels(kind)), default=0)
             for kind, _ in locations),
            default=0,
        )
        wanted = [
            location for location in locations
            if max((LEVEL_RANK.get(level, 0) for level in target_levels(location[0])), default=0) == deepest_rank
        ]
        constraints = [location for location in locations if location not in wanted]

    resolved: list[str] = []
    for kind, marker in wanted:
        candidates = [
            item for item in sections
            if item.get("level") in target_levels(kind) and item.get("marker") == marker
        ]
        for constraint_kind, constraint_marker in constraints:
            candidates = [
                item for item in candidates
                if any(
                    f"/{level}:{constraint_marker}" in item.get("id", "")
                    for level in target_levels(constraint_kind)
                )
            ]
        if len(candidates) != 1:
            return [], "ambiguous" if candidates else "location_not_found"
        resolved.append(candidates[0]["id"])
    return list(dict.fromkeys(resolved)), "resolved"


def normalize_reference(
    reference: dict[str, Any],
    source_record_id: str,
    source_section_id: str,
    relation_index: int,
    lookup: dict[str, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    normalized = {
        key: (clean_text(value) if isinstance(value, str) else copy.deepcopy(value))
        for key, value in reference.items()
    }
    document_type = clean_text(reference.get("document_type"))
    document_number = normalize_number(reference.get("document_number"))
    candidates = lookup.get(number_key(document_number), [])
    same_type = [
        candidate
        for candidate in candidates
        if candidate["document_type"] == normalize_type(document_type)
    ]
    candidates = same_type or candidates
    target = candidates[0] if len(candidates) == 1 else None
    target_document_id = target["record_id"] if target else None
    target_document_number = target["document_id"] if target else None
    referenced_location = clean_text(reference.get("referenced_location"))
    target_section_ids: list[str] = []
    section_status = "not_attempted"
    if target:
        target_section_ids, section_status = resolve_target_sections(
            target, referenced_location
        )

    # Không tạo cạnh văn bản tự dẫn chiếu chung chung. Nếu có locator và trỏ
    # sang section khác trong cùng văn bản thì vẫn giữ quan hệ section-to-section.
    if target_document_id == source_record_id and not target_section_ids:
        return None
    if source_section_id in target_section_ids:
        return None

    if target_section_ids:
        status = "resolved_section"
        method = "document_number+referenced_location"
    elif target:
        status = f"document_resolved_{section_status}"
        method = "document_number"
    else:
        status = "ambiguous_document" if candidates else "unresolved_document"
        method = None

    normalized.update(
        {
            "document_type": document_type,
            "document_number": clean_text(reference.get("document_number")),
            "normalized_document_number": document_number,
            "document_number_key": number_key(document_number),
            "issued_date_raw": clean_text(reference.get("issued_date_raw")),
            "normalized_issued_date": parse_date(reference.get("issued_date_raw")),
            "referenced_location": referenced_location,
            "relation_type": clean_text(reference.get("relation_type")),
            "reference_key": reference_key(reference),
            "reference_id": reference_id(reference),
            "target_document_id": target_document_id,
            "target_document_number": target_document_number,
            "target_section_ids": target_section_ids,
            "resolution_status": status,
            "resolution_method": method,
            "source_section_id": source_section_id,
            "relation_index": relation_index,
        }
    )
    return normalized


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


def compact_relation(item: dict[str, Any]) -> dict[str, Any]:
    """Tạo relation section-to-section, dùng trực tiếp cho importer Neo4j."""
    compact = {
        "source_section_id": item["source_section_id"],
        "relation_type": item.get("relation_type", ""),
        "referenced_location": item.get("referenced_location", ""),
        "resolution_status": item.get("resolution_status", "unresolved"),
    }
    if item.get("target_document_id"):
        compact["target_document_id"] = item["target_document_id"]
    if item.get("target_section_ids"):
        compact["target_section_ids"] = item["target_section_ids"]
    elif not item.get("target_document_id"):
        compact.update(
            {
                "reference_id": item.get("reference_id"),
                "document_type": item.get("document_type", ""),
                "document_number": item.get("document_number", ""),
            }
        )
    return compact


def deduplicate_relations(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Gộp cùng một relation bị parser nhận diện lặp trong một section."""
    result: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in items:
        target = "|".join(item.get("target_section_ids") or [])
        target = target or item.get("target_document_id") or item.get("reference_id") or ""
        key = (
            item.get("source_section_id", ""),
            target,
            item.get("relation_type", ""),
        )
        if key not in result:
            result[key] = dict(item)
            continue

        current_location = result[key].get("referenced_location", "")
        new_location = item.get("referenced_location", "")
        locations = [location for location in (current_location, new_location) if location]
        result[key]["referenced_location"] = "; ".join(
            dict.fromkeys(locations)
        )
    return list(result.values())


def expand_section_edges(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Đổi một dẫn chiếu nhiều đích thành các edge section-to-section riêng."""
    result: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in items:
        for target_section_id in item.get("target_section_ids") or []:
            edge = {
                "source_section_id": item["source_section_id"],
                "target_section_id": target_section_id,
                "relation_type": item.get("relation_type", ""),
                "referenced_location": item.get("referenced_location", ""),
                "resolution_status": "resolved_section",
            }
            key = (
                edge["source_section_id"],
                edge["target_section_id"],
                edge["relation_type"],
            )
            if key not in result:
                result[key] = edge
    return list(result.values())


def normalize_record(
    record: dict[str, Any],
    lookup: dict[str, list[dict[str, Any]]],
    hierarchy: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    normalized = copy.deepcopy(record)
    # Quan hệ pháp luật được lưu tại từng section trong ``content.sections``.
    # Không giữ block relations ở cấp văn bản vì block này không còn được dùng.
    normalized.pop("relations", None)
    content = normalized.setdefault("content", {})
    source = normalized.setdefault("source", {})
    jurisdiction = normalized.setdefault("jurisdiction", {})

    # Chuẩn hóa các field text phổ biến nhưng vẫn giữ các field *_raw.
    for key in ("title", "document_type", "document_number", "issuing_authority", "validity_raw"):
        if key in content:
            content[key] = clean_text(content[key])
    for key in ("level", "location"):
        if key in jurisdiction:
            jurisdiction[key] = clean_text(jurisdiction[key])
    for key in ("url", "name"):
        if key in source:
            source[key] = clean_text(source[key])

    content["issued_date"] = parse_date(content.get("issued_date_raw"))
    content["effective_date"] = parse_date(content.get("effective_date_raw"))
    content["document_number_normalized"] = normalize_number(content.get("document_number"))
    content["document_number_key"] = number_key(content["document_number_normalized"])
    content["document_id"] = content["document_number_normalized"] or clean_text(
        normalized.get("id")
    )
    normalized["document_id"] = content["document_id"]
    normalized["life_event"] = [clean_text(x) for x in normalized.get("life_event", [])]
    normalized["domain"] = clean_text(normalized.get("domain"))
    normalized["normalization_version"] = "law-normalize-v2"

    report_rows: list[dict[str, Any]] = []
    for section_index, section in enumerate(content.get("sections") or []):
        structure = hierarchy[section_index]
        section_id = structure["id"]
        section["heading"] = clean_text(section.get("heading"))
        section["level"] = structure["level"]
        section["text"] = clean_text(section.get("text"))
        section["normalized_id"] = section_id
        section["parent_section_id"] = structure["parent_section_id"]
        section["structural_path"] = structure["structural_path"]
        section["marker"] = structure["marker"]

        relation_items = []
        for relation_index, relation in enumerate(section.get("related_laws") or []):
            if not isinstance(relation, dict):
                continue
            item = normalize_reference(
                relation,
                clean_text(normalized.get("id")),
                section_id,
                relation_index,
                lookup,
            )
            if item is None:
                continue
            relation_items.append(compact_relation(item))
            report_rows.append(item)
        section["related_laws"] = deduplicate_relations(relation_items)

    return remove_raw_fields(normalized), [
        remove_raw_fields(row) for row in report_rows
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT_DIR / "data/law/records")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT_DIR / "data/law/normalized_records",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT_DIR / "data/law/normalized_relation_report.json",
    )
    parser.add_argument(
        "--relations",
        type=Path,
        default=ROOT_DIR / "data/law/law_relations.json",
    )
    args = parser.parse_args()

    files = sorted(args.input_dir.glob("LAW_*.json"))
    if not files:
        raise SystemExit(f"Không tìm thấy LAW_*.json trong {args.input_dir}")

    records = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    hierarchy_by_record = {
        clean_text(record.get("id")): build_section_hierarchy(
            clean_text(record.get("id")), record.get("content", {}).get("sections") or []
        )
        for record in records
        if clean_text(record.get("id"))
    }
    lookup = law_lookup(records, hierarchy_by_record)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    report: list[dict[str, Any]] = []
    resolved_section = document_only = unresolved = ambiguous = 0
    for record in records:
        law_id = clean_text(record.get("id"))
        normalized, rows = normalize_record(
            record, lookup, hierarchy_by_record[law_id]
        )
        output_path = args.output_dir / f"{normalized['id']}.json"
        output_path.write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        report.extend(rows)
        resolved_section += sum(
            row["resolution_status"] == "resolved_section" for row in rows
        )
        document_only += sum(
            row["resolution_status"].startswith("document_resolved_") for row in rows
        )
        unresolved += sum(
            row["resolution_status"] == "unresolved_document" for row in rows
        )
        ambiguous += sum("ambiguous" in row["resolution_status"] for row in rows)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    # Graph chỉ nhận cạnh chính xác section -> section. Các trường hợp chỉ
    # resolve được tới document được giữ trong report để bổ sung locator sau.
    resolved_relations = deduplicate_relations([
        compact_relation(row)
        for row in report
        if row["resolution_status"] == "resolved_section"
    ])
    relations = expand_section_edges(resolved_relations)
    args.relations.parent.mkdir(parents=True, exist_ok=True)
    args.relations.write_text(
        json.dumps(relations, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Đã chuẩn hóa {len(records)} records vào: {args.output_dir}")
    print(
        f"Tham chiếu: {len(report)} | resolved_section={resolved_section} | "
        f"document_only={document_only} | unresolved={unresolved} | ambiguous={ambiguous}"
    )
    print(f"Báo cáo: {args.report}")
    print(f"Relations: {args.relations}")


if __name__ == "__main__":
    main()
