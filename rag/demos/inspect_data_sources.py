"""Kiểm tra read-only dữ liệu RAG đang có trong Qdrant và Neo4j.

Chạy từ thư mục gốc dự án:

    python -m rag.demos.inspect_data_sources

Script không tạo, cập nhật hoặc xóa dữ liệu. Thông tin nhạy cảm trong `.env`
không được in ra màn hình.
"""

from __future__ import annotations

import json
import sys
from typing import Any


EXPECTED_COLLECTIONS = ("procedures", "laws")
EXPECTED_NODE_LABELS = ("Procedure", "LawDocument", "LawSection")
EXPECTED_RELATIONSHIPS = (
    "REQUIRES",
    "NEXT_STEP",
    "PART_OF",
    "HAS_SUB_PROCEDURE",
    "RELATED_TO_BENEFIT",
    "HAS_SECTION",
    "PARENT_SECTION",
    "CITES",
)


def print_json(title: str, value: Any) -> None:
    """In dữ liệu dễ đọc; ``default=str`` hỗ trợ kiểu Date của Neo4j."""
    print(f"\n=== {title} ===")
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def vector_config_summary(collection_info: Any) -> Any:
    """Chuyển cấu hình vector của Qdrant thành dữ liệu có thể in JSON."""
    vectors = collection_info.config.params.vectors
    if hasattr(vectors, "model_dump"):
        return vectors.model_dump(mode="json")
    if isinstance(vectors, dict):
        return {
            name: config.model_dump(mode="json")
            if hasattr(config, "model_dump")
            else str(config)
            for name, config in vectors.items()
        }
    return str(vectors)


def inspect_qdrant() -> dict[str, Any]:
    """Đọc collection metadata và một payload mẫu của mỗi collection cần dùng."""
    from db.qdrant_client import QdrantVectorClient

    with QdrantVectorClient.from_env() as wrapper:
        response = wrapper.verify_connectivity()
        available = sorted(item.name for item in response.collections)
        collections: dict[str, Any] = {}

        for name in EXPECTED_COLLECTIONS:
            if name not in available:
                collections[name] = {"exists": False}
                continue

            info = wrapper.client.get_collection(collection_name=name)
            points, _next_page = wrapper.client.scroll(
                collection_name=name,
                limit=1,
                with_payload=True,
                with_vectors=False,
            )
            sample = points[0] if points else None
            payload = dict(sample.payload or {}) if sample else None
            payload_fields = sorted(payload) if payload else []
            if payload and "text" in payload:
                text = str(payload.pop("text") or "")
                payload["text_length"] = len(text)
                payload["text_preview"] = text[:500]
            collections[name] = {
                "exists": True,
                "points_count": info.points_count,
                "vectors_count": getattr(info, "vectors_count", None),
                "vector_config": vector_config_summary(info),
                "sample_point_id": str(sample.id) if sample else None,
                "sample_payload": payload,
                "sample_payload_fields": payload_fields,
            }

        return {
            "available_collections": available,
            "expected_collections": collections,
        }


def inspect_neo4j() -> dict[str, Any]:
    """Đọc schema, số lượng và node mẫu trong Neo4j."""
    from db.neo4j_client import Neo4jClient

    with Neo4jClient.from_env() as client:
        client.verify_connectivity()

        labels = client.query("CALL db.labels() YIELD label RETURN label ORDER BY label")
        relationship_types = client.query(
            "CALL db.relationshipTypes() YIELD relationshipType "
            "RETURN relationshipType ORDER BY relationshipType"
        )
        node_counts = client.query(
            "MATCH (n) UNWIND labels(n) AS label "
            "RETURN label, count(*) AS count ORDER BY label"
        )
        relationship_counts = client.query(
            "MATCH ()-[r]->() "
            "RETURN type(r) AS relationship_type, count(*) AS count "
            "ORDER BY relationship_type"
        )

        node_samples = {
            label: client.query(
                f"MATCH (n:{label}) RETURN properties(n) AS properties LIMIT 1"
            )
            for label in EXPECTED_NODE_LABELS
        }
        journey_sample = client.query(
            "MATCH (root:Procedure {id: $root_id}) "
            "OPTIONAL MATCH (root)-[r]->(target) "
            "RETURN root.id AS root_id, root.name AS root_name, "
            "type(r) AS relationship_type, target.id AS target_id, "
            "target.name AS target_name "
            "ORDER BY relationship_type, target_id",
            {"root_id": "PROC_3_000722"},
        )
        benefit_sample = client.query(
            "MATCH (procedure:Procedure)-[r:RELATED_TO_BENEFIT]->"
            "(section:LawSection) "
            "RETURN procedure.id AS procedure_id, section.id AS section_id, "
            "section.law_id AS law_id, section.order AS section_order, "
            "section.heading AS heading, properties(r) AS relationship_properties "
            "LIMIT 10"
        )

        available_labels = {row["label"] for row in labels}
        available_relationships = {
            row["relationshipType"] for row in relationship_types
        }
        return {
            "available_labels": sorted(available_labels),
            "missing_expected_labels": sorted(
                set(EXPECTED_NODE_LABELS) - available_labels
            ),
            "available_relationship_types": sorted(available_relationships),
            "missing_expected_relationship_types": sorted(
                set(EXPECTED_RELATIONSHIPS) - available_relationships
            ),
            "node_counts": node_counts,
            "relationship_counts": relationship_counts,
            "node_samples": node_samples,
            "birth_journey_sample": journey_sample,
            "benefit_relation_sample": benefit_sample,
        }


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    print("Kiểm tra dữ liệu RAG ở chế độ read-only.")

    try:
        print_json("QDRANT", inspect_qdrant())
    except Exception as exc:
        print_json(
            "QDRANT ERROR",
            {"type": type(exc).__name__, "message": str(exc)},
        )

    try:
        print_json("NEO4J", inspect_neo4j())
    except Exception as exc:
        print_json(
            "NEO4J ERROR",
            {"type": type(exc).__name__, "message": str(exc)},
        )


if __name__ == "__main__":
    main()
