"""Khởi tạo và import dữ liệu cơ bản vào Neo4j.

Phạm vi:
    - Tạo constraint/index cơ bản.
    - Import các node Procedure, LifeEvent, Step, RequiredDocument,
      LawDocument và LawSection.
    - Import cấu trúc section và dẫn chiếu section-to-section đã resolve.

Cách dùng:
    python neo4j_import.py --init-only
    python neo4j_import.py

Cấu hình trong .env:
    NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=mat_khau_cua_ban
    NEO4J_DATABASE=neo4j
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

try:
    from neo4j import Driver, GraphDatabase
except ImportError as exc:  # pragma: no cover - thông báo thân thiện khi thiếu dependency
    raise SystemExit(
        "Chưa cài neo4j driver. Hãy chạy: pip install neo4j"
    ) from exc


ROOT_DIR = Path(__file__).resolve().parents[1]


def load_dotenv(path: Path = ROOT_DIR / ".env") -> None:
    """Đọc .env đơn giản, không bắt buộc cài thêm python-dotenv."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def as_text(value: Any) -> str:
    return str(value or "").strip()


def as_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [as_text(item) for item in value if as_text(item)]


def read_json_files(directory: Path, pattern: str) -> list[dict[str, Any]]:
    records = []
    for path in sorted(directory.glob(pattern)):
        with path.open("r", encoding="utf-8") as handle:
            records.append(json.load(handle))
    return records


def build_nodes(
    procedure_dir: Path, law_dir: Path
) -> dict[str, list[dict[str, Any]]]:
    procedures: list[dict[str, Any]] = []
    life_events: dict[str, dict[str, Any]] = {}
    steps: list[dict[str, Any]] = []
    required_documents: list[dict[str, Any]] = []
    authorities: dict[str, dict[str, Any]] = {}
    jurisdictions: dict[str, dict[str, Any]] = {}
    sources: dict[str, dict[str, Any]] = {}
    laws: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []
    law_section_edges: list[dict[str, Any]] = []
    section_parent_edges: list[dict[str, Any]] = []
    law_citations: list[dict[str, Any]] = []

    for record in read_json_files(procedure_dir, "*.json"):
        procedure = record.get("procedure") or {}
        procedure_id = as_text(record.get("id"))
        if not procedure_id:
            continue

        authority_name = as_text(procedure.get("authority"))
        jurisdiction = record.get("jurisdiction") or {}
        location = as_text(jurisdiction.get("location"))
        jurisdiction_level = as_text(jurisdiction.get("level"))
        source = record.get("source") or {}

        procedures.append(
            {
                "id": procedure_id,
                "national_code": as_text(record.get("national_code")),
                "name": as_text(procedure.get("name")),
                "eligibility": as_text(procedure.get("eligibility")),
                "domain": as_text(record.get("domain")),
                "procedure_type": as_text(record.get("procedure_type")),
                "life_events": as_list(record.get("life_event")),
                "target_audience": as_list(record.get("target_audience")),
                "authority": authority_name,
                "jurisdiction_level": jurisdiction_level,
                "location": location,
                "source_url": as_text(source.get("url")),
                "source_name": as_text(source.get("name")),
                "effective_date": as_text(source.get("effective_date")),
                "last_updated": as_text(source.get("last_updated")),
            }
        )

        for event in as_list(record.get("life_event")):
            life_events.setdefault(event, {"id": event, "name": event})

        if authority_name:
            authorities.setdefault(
                authority_name,
                {"id": authority_name, "name": authority_name},
            )

        jurisdiction_id = "|".join(
            item for item in (jurisdiction_level, location) if item
        )
        if jurisdiction_id:
            jurisdictions.setdefault(
                jurisdiction_id,
                {
                    "id": jurisdiction_id,
                    "level": jurisdiction_level,
                    "location": location,
                },
            )

        source_id = as_text(source.get("url")) or procedure_id
        sources.setdefault(
            source_id,
            {
                "id": source_id,
                "name": as_text(source.get("name")),
                "url": as_text(source.get("url")),
            },
        )

        for index, step_text in enumerate(procedure.get("steps") or [], 1):
            step_text = as_text(step_text)
            if step_text:
                steps.append(
                    {
                        "id": f"{procedure_id}:step:{index:04d}",
                        "procedure_id": procedure_id,
                        "order": index,
                        "text": step_text,
                    }
                )

        for index, document in enumerate(procedure.get("documents") or [], 1):
            if not isinstance(document, dict):
                continue
            name = as_text(document.get("ten_giay_to"))
            if name:
                required_documents.append(
                    {
                        "id": f"{procedure_id}:document:{index:04d}",
                        "procedure_id": procedure_id,
                        "name": name,
                        "quantity": as_text(document.get("so_luong")),
                    }
                )

    for record in read_json_files(law_dir, "LAW_*.json"):
        content = record.get("content") or {}
        source = record.get("source") or {}
        law_id = as_text(record.get("id"))
        if not law_id:
            continue

        laws.append(
            {
                "id": law_id,
                "title": as_text(content.get("title")),
                "document_type": as_text(content.get("document_type")),
                "document_number": as_text(content.get("document_number")),
                "issuing_authority": as_text(content.get("issuing_authority")),
                "issued_date_raw": as_text(content.get("issued_date_raw")),
                "effective_date_raw": as_text(content.get("effective_date_raw")),
                "validity_raw": as_text(content.get("validity_raw")),
                "life_events": as_list(record.get("life_event")),
                "domain": as_text(record.get("domain")),
                "jurisdiction_level": as_text(
                    (record.get("jurisdiction") or {}).get("level")
                ),
                "location": as_text((record.get("jurisdiction") or {}).get("location")),
                "source_url": as_text(source.get("url")),
                "crawled_at": as_text(source.get("crawled_at")),
            }
        )

        for index, section in enumerate(content.get("sections") or []):
            if not isinstance(section, dict):
                continue
            section_id = as_text(section.get("normalized_id")) or f"{law_id}:section:{index:04d}"
            sections.append(
                {
                    "id": section_id,
                    "law_id": law_id,
                    "order": index,
                    "heading": as_text(section.get("heading")),
                    "level": as_text(section.get("level")),
                    "text": as_text(section.get("text")),
                    "marker": as_text(section.get("marker")),
                    "structural_path": as_text(section.get("structural_path")),
                    "section_label": {
                        "chapter": "LawChapter",
                        "part": "LawPart",
                        "section": "LawSectionGroup",
                        "article": "LawArticle",
                        "subsection": "LawSubsection",
                        "point": "LawPoint",
                    }.get(as_text(section.get("level")), "LawSectionOther"),
                }
            )
            law_section_edges.append(
                {"law_id": law_id, "section_id": section_id, "order": index}
            )
            parent_section_id = as_text(section.get("parent_section_id"))
            if parent_section_id:
                section_parent_edges.append(
                    {"section_id": section_id, "parent_section_id": parent_section_id}
                )

            for relation in section.get("related_laws") or []:
                if not isinstance(relation, dict):
                    continue
                if relation.get("resolution_status") != "resolved_section":
                    continue
                for target_section_id in as_list(relation.get("target_section_ids")):
                    law_citations.append(
                        {
                            "source_section_id": section_id,
                            "target_section_id": target_section_id,
                            "relation_type": as_text(relation.get("relation_type")),
                            "referenced_location": as_text(
                                relation.get("referenced_location")
                            ),
                        }
                    )

    return {
        "procedures": procedures,
        "life_events": list(life_events.values()),
        "steps": steps,
        "required_documents": required_documents,
        "authorities": list(authorities.values()),
        "jurisdictions": list(jurisdictions.values()),
        "sources": list(sources.values()),
        "laws": laws,
        "sections": sections,
        "law_section_edges": law_section_edges,
        "section_parent_edges": section_parent_edges,
        "law_citations": law_citations,
    }


SCHEMA_QUERIES = [
    "CREATE CONSTRAINT procedure_id_unique IF NOT EXISTS FOR (n:Procedure) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT life_event_id_unique IF NOT EXISTS FOR (n:LifeEvent) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT step_id_unique IF NOT EXISTS FOR (n:Step) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT required_document_id_unique IF NOT EXISTS FOR (n:RequiredDocument) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT law_id_unique IF NOT EXISTS FOR (n:LawDocument) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT section_id_unique IF NOT EXISTS FOR (n:LawSection) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT authority_id_unique IF NOT EXISTS FOR (n:Authority) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT jurisdiction_id_unique IF NOT EXISTS FOR (n:Jurisdiction) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT source_id_unique IF NOT EXISTS FOR (n:Source) REQUIRE n.id IS UNIQUE",
    "CREATE INDEX procedure_name IF NOT EXISTS FOR (n:Procedure) ON (n.name)",
    "CREATE INDEX law_document_number IF NOT EXISTS FOR (n:LawDocument) ON (n.document_number)",
]


IMPORT_QUERIES = {
    "procedures": """
        UNWIND $rows AS row
        MERGE (n:Procedure {id: row.id})
        SET n += row
    """,
    "life_events": """
        UNWIND $rows AS row
        MERGE (n:LifeEvent {id: row.id})
        SET n += row
    """,
    "steps": """
        UNWIND $rows AS row
        MERGE (n:Step {id: row.id})
        SET n += row
    """,
    "required_documents": """
        UNWIND $rows AS row
        MERGE (n:RequiredDocument {id: row.id})
        SET n += row
    """,
    "authorities": """
        UNWIND $rows AS row
        MERGE (n:Authority {id: row.id})
        SET n += row
    """,
    "jurisdictions": """
        UNWIND $rows AS row
        MERGE (n:Jurisdiction {id: row.id})
        SET n += row
    """,
    "sources": """
        UNWIND $rows AS row
        MERGE (n:Source {id: row.id})
        SET n += row
    """,
    "laws": """
        UNWIND $rows AS row
        MERGE (n:LawDocument {id: row.id})
        SET n += row
    """,
    "sections": """
        UNWIND $rows AS row
        MERGE (n:LawSection {id: row.id})
        SET n += row
        FOREACH (_ IN CASE WHEN row.section_label = "LawChapter" THEN [1] ELSE [] END |
            SET n:LawChapter)
        FOREACH (_ IN CASE WHEN row.section_label = "LawPart" THEN [1] ELSE [] END |
            SET n:LawPart)
        FOREACH (_ IN CASE WHEN row.section_label = "LawSectionGroup" THEN [1] ELSE [] END |
            SET n:LawSectionGroup)
        FOREACH (_ IN CASE WHEN row.section_label = "LawArticle" THEN [1] ELSE [] END |
            SET n:LawArticle)
        FOREACH (_ IN CASE WHEN row.section_label = "LawSubsection" THEN [1] ELSE [] END |
            SET n:LawSubsection)
        FOREACH (_ IN CASE WHEN row.section_label = "LawPoint" THEN [1] ELSE [] END |
            SET n:LawPoint)
    """,
    "law_section_edges": """
        UNWIND $rows AS row
        MATCH (law:LawDocument {id: row.law_id})
        MATCH (section:LawSection {id: row.section_id})
        MERGE (law)-[r:HAS_SECTION]->(section)
        SET r.order = row.order
    """,
    "section_parent_edges": """
        UNWIND $rows AS row
        MATCH (section:LawSection {id: row.section_id})
        MATCH (parent:LawSection {id: row.parent_section_id})
        MERGE (section)-[:PARENT_SECTION]->(parent)
    """,
    "law_citations": """
        UNWIND $rows AS row
        MATCH (source:LawSection {id: row.source_section_id})
        MATCH (target:LawSection {id: row.target_section_id})
        MERGE (source)-[r:CITES {relation_type: row.relation_type}]->(target)
        SET r.referenced_location = row.referenced_location,
            r.source = "parsed_section"
    """,
}


def init_schema(driver: Driver, database: str) -> None:
    with driver.session(database=database) as session:
        for query in SCHEMA_QUERIES:
            session.run(query).consume()


def import_nodes(driver: Driver, database: str, nodes: dict[str, list[dict[str, Any]]]) -> None:
    with driver.session(database=database) as session:
        for node_type, rows in nodes.items():
            if not rows:
                continue
            session.run(IMPORT_QUERIES[node_type], rows=rows).consume()
            print(f"Imported {len(rows):>5} {node_type}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--init-only",
        action="store_true",
        help="Chỉ tạo constraint/index, không import dữ liệu",
    )
    parser.add_argument(
        "--procedure-dir",
        type=Path,
        default=ROOT_DIR / "data" / "procedure",
    )
    parser.add_argument(
        "--law-dir",
        type=Path,
        default=ROOT_DIR / "data" / "law" / "normalized_records",
    )
    args = parser.parse_args()

    load_dotenv()
    uri = os.getenv("NEO4J_URI", "")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")
    database = os.getenv("NEO4J_DATABASE", "neo4j")

    if not uri:
        raise SystemExit(
            "Thiếu NEO4J_URI. Hãy copy URI trong Neo4j Aura > Connect > Drivers vào .env."
        )
    if not password:
        raise SystemExit(
            "Thiếu NEO4J_PASSWORD. Hãy điền thông tin kết nối trong file .env."
        )

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        driver.verify_connectivity()
        print(f"Đã kết nối Neo4j: {uri} / database={database}")
        init_schema(driver, database)
        print("Đã tạo constraint/index cơ bản.")

        if not args.init_only:
            nodes = build_nodes(args.procedure_dir, args.law_dir)
            import_nodes(driver, database, nodes)
            print("Hoàn tất import node và relationship pháp luật đã resolve.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
