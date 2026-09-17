"""Truy vấn quan hệ thủ tục và căn cứ lợi ích trong Neo4j."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from db.neo4j_client import Neo4jClient
from rag.core.schemas import (
    BenefitGraphRelation,
    GraphRetrievalResult,
    LegalEvidence,
    ProcedureEvidence,
    ProcedureGraphRelation,
    RetrievedChunk,
)


PROCEDURE_QUERY = """
MATCH (source:Procedure)
WHERE source.id IN $procedure_ids
OPTIONAL MATCH (source)-[relation:REQUIRES|NEXT_STEP|PART_OF|HAS_SUB_PROCEDURE]
               ->(target:Procedure)
RETURN properties(source) AS source,
       type(relation) AS relationship_type,
       properties(target) AS target
ORDER BY source.id, relationship_type, target.id
"""


PROCEDURE_NODES_QUERY = """
MATCH (procedure:Procedure)
WHERE procedure.id IN $procedure_ids
RETURN properties(procedure) AS procedure
ORDER BY procedure.id
"""


BENEFIT_QUERY = """
MATCH (procedure:Procedure)-[relation:RELATED_TO_BENEFIT]->(anchor:LawSection)
WHERE procedure.id IN $procedure_ids
MATCH (section:LawSection)-[:PARENT_SECTION*0..6]->(anchor)
OPTIONAL MATCH (law:LawDocument)-[:HAS_SECTION]->(section)
RETURN procedure.id AS procedure_id,
       properties(relation) AS relation,
       properties(anchor) AS anchor,
       properties(section) AS section,
       properties(law) AS law
ORDER BY procedure.id, section.law_id, section.order
"""


LAW_EVIDENCE_QUERY = """
UNWIND $sections AS requested
MATCH (section:LawSection)
WHERE section.law_id = requested.law_id
  AND section.order = requested.section_order
OPTIONAL MATCH (law:LawDocument)-[:HAS_SECTION]->(section)
RETURN requested.score AS retrieval_score,
       properties(section) AS section,
       properties(law) AS law
ORDER BY retrieval_score DESC
"""


def _procedure(node: dict[str, Any]) -> ProcedureEvidence:
    procedure_id = str(node.get("id", ""))
    return ProcedureEvidence(
        procedure_id=procedure_id,
        name=str(node.get("name") or procedure_id),
        authority=node.get("authority"),
        eligibility=node.get("eligibility"),
        source_url=node.get("source_url"),
    )


class GraphRetriever:
    def __init__(self, client: Neo4jClient) -> None:
        self.client = client

    def retrieve(
        self,
        procedure_ids: Iterable[str],
        *,
        include_benefits: bool,
    ) -> GraphRetrievalResult:
        ids = list(dict.fromkeys(value for value in procedure_ids if value))
        if not ids:
            return GraphRetrievalResult()

        expanded_ids = set(ids)
        rows = []
        for _ in range(4):
            rows = self.client.query(
                PROCEDURE_QUERY,
                {"procedure_ids": sorted(expanded_ids)},
            )
            discovered_ids = set(expanded_ids)
            for row in rows:
                if row["source"]:
                    discovered_ids.add(str(row["source"].get("id", "")))
                if row["target"]:
                    discovered_ids.add(str(row["target"].get("id", "")))
            discovered_ids.discard("")
            if discovered_ids == expanded_ids:
                break
            expanded_ids = discovered_ids
        procedures: dict[str, ProcedureEvidence] = {}
        relations: list[ProcedureGraphRelation] = []

        for row in rows:
            source = _procedure(row["source"])
            procedures[source.procedure_id] = source
            if row["relationship_type"] and row["target"]:
                target = _procedure(row["target"])
                procedures[target.procedure_id] = target
                relations.append(
                    ProcedureGraphRelation(
                        source_id=source.procedure_id,
                        relationship_type=row["relationship_type"],
                        target=target,
                    )
                )

        benefits: list[BenefitGraphRelation] = []
        if include_benefits:
            benefit_rows = self.client.query(BENEFIT_QUERY, {"procedure_ids": ids})
            for row in benefit_rows:
                relation = row["relation"] or {}
                anchor = row["anchor"] or {}
                section = row["section"] or {}
                law = row["law"] or {}
                benefits.append(
                    BenefitGraphRelation(
                        procedure_id=row["procedure_id"],
                        benefit_id=relation.get("benefit_id"),
                        anchor_section_id=anchor.get("id"),
                        title=anchor.get("heading"),
                        note=relation.get("note"),
                        evidence=LegalEvidence(
                            law_id=str(section.get("law_id", "")),
                            law_title=law.get("title"),
                            validity=law.get("validity_raw"),
                            section_id=str(section.get("id", "")),
                            section_order=section.get("order"),
                            heading=section.get("heading"),
                            text=section.get("text"),
                            source_url=law.get("source_url"),
                            relation_scope=relation.get("scope"),
                        ),
                    )
                )

        return GraphRetrievalResult(
            procedures=list(procedures.values()),
            procedure_relations=relations,
            benefit_relations=benefits,
        )

    def retrieve_procedure_nodes(
        self,
        procedure_ids: Iterable[str],
    ) -> GraphRetrievalResult:
        ids = list(dict.fromkeys(value for value in procedure_ids if value))
        if not ids:
            return GraphRetrievalResult()
        rows = self.client.query(PROCEDURE_NODES_QUERY, {"procedure_ids": ids})
        return GraphRetrievalResult(
            procedures=[_procedure(row["procedure"]) for row in rows]
        )

    def retrieve_law_evidence(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[LegalEvidence]:
        sections = []
        seen = set()
        for chunk in chunks:
            section_order = chunk.metadata.get("section_index")
            key = (chunk.doc_id, section_order)
            if not chunk.doc_id or section_order is None or key in seen:
                continue
            seen.add(key)
            sections.append(
                {
                    "law_id": chunk.doc_id,
                    "section_order": section_order,
                    "score": chunk.score,
                }
            )
        if not sections:
            return []

        rows = self.client.query(LAW_EVIDENCE_QUERY, {"sections": sections})
        evidence = []
        for row in rows:
            section = row["section"] or {}
            law = row["law"] or {}
            evidence.append(
                LegalEvidence(
                    law_id=str(section.get("law_id", "")),
                    law_title=law.get("title"),
                    validity=law.get("validity_raw"),
                    section_id=str(section.get("id", "")),
                    section_order=section.get("order"),
                    heading=section.get("heading"),
                    text=section.get("text"),
                    source_url=law.get("source_url"),
                    retrieval_score=row.get("retrieval_score"),
                )
            )
        return evidence
