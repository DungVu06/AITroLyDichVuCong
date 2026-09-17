"""Gom và xếp hành trình thủ tục từ kết quả graph."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from rag.core.schemas import (
    GraphRetrievalResult,
    JourneyCategory,
    JourneyItem,
    JourneyStatus,
)


def _candidate_ids(graph: GraphRetrievalResult) -> list[str]:
    sub_procedures = [
        relation.target.procedure_id
        for relation in graph.procedure_relations
        if relation.relationship_type == "HAS_SUB_PROCEDURE"
    ]
    if sub_procedures:
        return list(dict.fromkeys(sub_procedures))
    return [procedure.procedure_id for procedure in graph.procedures]


def build_journey(
    graph: GraphRetrievalResult,
    seed_procedure_ids: Iterable[str],
    completed_procedure_ids: Iterable[str] = (),
) -> list[JourneyItem]:
    """Tạo priority theo tầng phụ thuộc; cùng priority có thể làm song song."""
    candidate_ids = _candidate_ids(graph)
    candidate_set = set(candidate_ids)
    seed_set = set(seed_procedure_ids)
    completed_set = set(completed_procedure_ids)
    procedures = {item.procedure_id: item for item in graph.procedures}
    dependencies: dict[str, set[str]] = defaultdict(set)

    for relation in graph.procedure_relations:
        source_id = relation.source_id
        target_id = relation.target.procedure_id
        if source_id not in candidate_set or target_id not in candidate_set:
            continue
        if relation.relationship_type == "REQUIRES":
            dependencies[source_id].add(target_id)
        elif relation.relationship_type == "NEXT_STEP":
            dependencies[target_id].add(source_id)

    priorities = {procedure_id: 1 for procedure_id in candidate_ids}
    for _ in candidate_ids:
        changed = False
        for procedure_id in candidate_ids:
            deps = dependencies[procedure_id]
            if not deps:
                continue
            new_priority = max(priorities[dep] for dep in deps) + 1
            if new_priority > priorities[procedure_id]:
                priorities[procedure_id] = new_priority
                changed = True
        if not changed:
            break

    journey: list[JourneyItem] = []
    for procedure_id in candidate_ids:
        procedure = procedures[procedure_id]
        depends_on = sorted(dependencies[procedure_id])
        is_direct_match = procedure_id in seed_set
        journey.append(
            JourneyItem(
                procedure_id=procedure_id,
                name=procedure.name,
                priority=priorities[procedure_id],
                category=(
                    JourneyCategory.REQUIRED
                    if is_direct_match
                    else JourneyCategory.RECOMMENDED
                ),
                status=(
                    JourneyStatus.COMPLETED
                    if procedure_id in completed_set
                    else JourneyStatus.UNKNOWN
                ),
                reason=(
                    "Khớp trực tiếp với tình huống người dùng."
                    if is_direct_match
                    else "Thủ tục liên quan trong hành trình từ graph."
                ),
                depends_on=depends_on,
            )
        )

    return sorted(journey, key=lambda item: (item.priority, item.procedure_id))
