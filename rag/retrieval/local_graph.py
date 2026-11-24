"""Read the four graph retrieval queries against the local import snapshot."""

from collections import defaultdict

from db.graph.neo4j_import import build_nodes
from rag.retrieval.catalog import DATA
from rag.retrieval.graph import BENEFIT_QUERY, LAW_EVIDENCE_QUERY, PROCEDURE_NODES_QUERY, PROCEDURE_QUERY


class SnapshotGraph:
    def __init__(self):
        data = build_nodes(DATA / "procedure/normalized_records", DATA / "law/normalized_records",
                           DATA / "benefit_relation/related_benefit_relations.json")
        self.procedures = {p["id"]: p for p in data["procedures"]}
        self.sections = {s["id"]: s for s in data["sections"]}
        self.by_order = {(s["law_id"], s["order"]): s for s in data["sections"]}
        self.laws = {l["id"]: l for l in data["laws"]}
        self.edges = defaultdict(list)
        for bucket, kind in (("procedure_requires", "REQUIRES"), ("procedure_next_steps", "NEXT_STEP"),
                             ("procedure_part_of", "PART_OF"), ("procedure_sub_procedures", "HAS_SUB_PROCEDURE")):
            for edge in data[bucket]:
                target = self.procedures.get(edge["target_id"])
                if target:
                    self.edges[edge["source_id"]].append((kind, target, edge["properties"]))
        self.children = defaultdict(list)
        for edge in data["section_parent_edges"]:
            self.children[edge["parent_section_id"]].append(edge["section_id"])
        self.benefits = data["procedure_related_benefits"]

    def query(self, statement, parameters):
        ids = parameters.get("procedure_ids", [])
        if statement == PROCEDURE_NODES_QUERY:
            return [{"procedure": self.procedures[i]} for i in ids if i in self.procedures]
        if statement == PROCEDURE_QUERY:
            return [
                {"source": self.procedures[i], "relationship_type": kind, "target": target, "relation": relation}
                for i in ids if i in self.procedures
                for kind, target, relation in self.edges.get(i, [(None, None, None)])
            ]
        if statement == LAW_EVIDENCE_QUERY:
            rows = []
            for req in parameters["sections"]:
                section = self.by_order.get((req["law_id"], req["section_order"]))
                if section:
                    rows.append(dict(section=section, law=self.laws[req["law_id"]], retrieval_score=req["score"]))
            return rows
        if statement != BENEFIT_QUERY:
            raise ValueError("Unsupported snapshot query")
        rows = []
        for edge in self.benefits:
            anchor = self.sections.get(edge["target_section_id"])
            if not anchor or edge["source_id"] not in ids:
                continue
            level = [anchor["id"]]
            for _ in range(7):
                for key in level:
                    section = self.sections[key]
                    rows.append(dict(section=section, anchor=anchor, law=self.laws[section["law_id"]],
                                     procedure_id=edge["source_id"], relation=edge))
                level = [child for key in level for child in self.children[key]]
                if not level:
                    break
        return rows
