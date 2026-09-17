"""Gom quyền lợi và khử trùng căn cứ pháp luật từ graph."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from rag.core.schemas import BenefitEvidence, EligibilityStatus, GraphRetrievalResult, LegalEvidence


def _clean_title(title: str) -> str:
    return re.sub(r"^\s*[IVXLCDM]+\s*[.\-:]?\s*", "", title, flags=re.IGNORECASE).strip()


def _group_key(title: str, fallback: str) -> str:
    normalized = unicodedata.normalize("NFC", _clean_title(title)).casefold()
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized or fallback


@dataclass
class _BenefitGroup:
    title: str
    procedure_id: str
    evidence: dict[tuple[str, str], LegalEvidence] = field(default_factory=dict)


def resolve_benefits(graph: GraphRetrievalResult) -> list[BenefitEvidence]:
    groups: dict[str, _BenefitGroup] = {}

    for relation in graph.benefit_relations:
        raw_title = relation.title or relation.evidence.law_title or "Quyền lợi liên quan"
        title = _clean_title(raw_title)
        fallback = relation.benefit_id or relation.anchor_section_id or relation.evidence.law_id
        key = _group_key(title, fallback)
        group = groups.setdefault(
            key,
            _BenefitGroup(title=title, procedure_id=relation.procedure_id),
        )
        evidence_key = (relation.evidence.law_id, relation.evidence.section_id)
        group.evidence[evidence_key] = relation.evidence

    return [
        BenefitEvidence(
            related_procedure_id=group.procedure_id,
            title=group.title,
            eligibility_status=EligibilityStatus.UNKNOWN,
            reason=(
                "Có căn cứ liên quan trong graph nhưng chưa đủ dữ kiện "
                "để kết luận người dùng đáp ứng điều kiện hưởng."
            ),
            legal_evidence=sorted(
                group.evidence.values(),
                key=lambda item: (item.law_id, item.section_order or -1),
            ),
        )
        for group in groups.values()
    ]
