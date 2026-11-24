"""Gom và xếp hành trình thủ tục từ kết quả graph."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from db.graph.procedure_normalize import CARD_REQUESTED
from rag.core.schemas import (
    GraphRetrievalResult,
    JourneyCategory,
    JourneyItem,
    JourneyStatus,
    RelationEvidence,
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


def select_workflow(
    graph: GraphRetrievalResult, workflow_id: str, identity_card_requested: bool | None,
) -> GraphRetrievalResult:
    relations = [
        edge for edge in graph.procedure_relations
        if edge.workflow_id == workflow_id and edge.evidence_record_id and edge.evidence_step
        and (edge.condition is None or (
            edge.condition == CARD_REQUESTED and identity_card_requested is not False
        ))
    ]
    included = {workflow_id} | {
        edge.target.procedure_id for edge in relations
        if edge.relationship_type == "HAS_SUB_PROCEDURE" and edge.source_id == workflow_id
    }
    return graph.model_copy(update={
        "procedures": [procedure for procedure in graph.procedures if procedure.procedure_id in included],
        "procedure_relations": [
            edge for edge in relations
            if edge.source_id in included and edge.target.procedure_id in included
        ],
        "benefit_relations": [edge for edge in graph.benefit_relations if edge.procedure_id in included],
    })


def workflow_transfer_evidence(graph: GraphRetrievalResult) -> list[RelationEvidence]:
    evidence = []
    for edge in graph.procedure_relations:
        if edge.relationship_type != "NEXT_STEP" or not (
            edge.workflow_id and edge.transferred_result and edge.evidence_record_id and edge.evidence_step
        ):
            continue
        target = edge.target.procedure_id
        text = f"Hệ thống tự chuyển {edge.transferred_result} để xử lý thủ tục {edge.target.name.lower()}."
        if edge.condition == CARD_REQUESTED:
            text += " Nhánh này chỉ áp dụng khi người đại diện hợp pháp đề nghị cấp thẻ lúc nộp hồ sơ trực tuyến."
        else:
            text += " Người dân không phải tự chuyển giấy tờ này giữa các cơ quan trong gói liên thông."
        evidence.append(RelationEvidence(
            source_id=edge.source_id,
            relationship_type=edge.relationship_type,
            target_id=target,
            citation_id=f"REL:{edge.source_id}:{edge.relationship_type}:{target}",
            text=text,
            evidence_record_id=edge.evidence_record_id,
            evidence_step=edge.evidence_step,
            transferred_result=edge.transferred_result,
        ))
    return evidence


def build_journey(
    graph: GraphRetrievalResult,
    seed_procedure_ids: Iterable[str],
    completed_procedure_ids: Iterable[str] = (),
    *,
    workflow_id: str | None = None,
    identity_card_requested: bool | None = None,
) -> list[JourneyItem]:
    """Tạo priority theo tầng phụ thuộc; cùng priority có thể làm song song."""
    if workflow_id:
        graph = select_workflow(graph, workflow_id, identity_card_requested)
    candidate_ids = _candidate_ids(graph)
    optional_ids = {
        edge.target.procedure_id for edge in graph.procedure_relations
        if edge.relationship_type == "HAS_SUB_PROCEDURE" and edge.condition == CARD_REQUESTED
    }
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
        if (
            relation.workflow_id != workflow_id
            or not relation.evidence_record_id
            or not relation.evidence_step
        ):
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
        optional = procedure_id in optional_ids and identity_card_requested is not True
        category = JourneyCategory.RECOMMENDED
        reason = "Thủ tục liên quan trong hành trình."
        if optional:
            category = JourneyCategory.OPTIONAL
            reason = "Chỉ áp dụng khi người đại diện đề nghị cấp thẻ lúc nộp hồ sơ liên thông."
        elif is_direct_match:
            category = JourneyCategory.REQUIRED
            reason = "Khớp trực tiếp với tình huống người dùng."
        journey.append(
            JourneyItem(
                procedure_id=procedure_id,
                name=procedure.name,
                priority=priorities[procedure_id],
                category=category,
                status=(
                    JourneyStatus.COMPLETED
                    if procedure_id in completed_set
                    else JourneyStatus.UNKNOWN
                ),
                reason=reason,
                depends_on=depends_on,
            )
        )

    return sorted(journey, key=lambda item: (item.priority, item.procedure_id))
