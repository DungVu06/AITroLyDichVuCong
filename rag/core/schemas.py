"""Schema dữ liệu trao đổi giữa các bước trong RAG engine."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Base model không chấp nhận field ngoài schema."""

    model_config = ConfigDict(extra="forbid")


class Intent(StrEnum):
    PROCEDURE_JOURNEY = "procedure_journey"
    PROCEDURE_DETAIL = "procedure_detail"
    NEXT_STEP = "next_step"
    BENEFIT_CHECK = "benefit_check"
    ELIGIBILITY_CHECK = "eligibility_check"
    LEGAL_QUESTION = "legal_question"
    OUT_OF_SCOPE = "out_of_scope"
    UNKNOWN = "unknown"


class RetrievalStrategy(StrEnum):
    CLARIFICATION = "clarification"
    JOURNEY_FIRST = "journey_first"
    PROCEDURE_DETAIL = "procedure_detail"
    GRAPH_NEXT_STEPS = "graph_next_steps"
    BENEFIT_FIRST = "benefit_first"
    LAW_SEARCH = "law_search"
    OUT_OF_SCOPE = "out_of_scope"


class JourneyCategory(StrEnum):
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class JourneyStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    UNKNOWN = "unknown"


class EligibilityStatus(StrEnum):
    ELIGIBLE = "eligible"
    POSSIBLY_ELIGIBLE = "possibly_eligible"
    NOT_ELIGIBLE = "not_eligible"
    UNKNOWN = "unknown"


class UserQuery(StrictModel):
    text: str = Field(min_length=1)
    conversation_id: str | None = None


class PreprocessedQuery(StrictModel):
    raw_text: str
    normalized_text: str = Field(min_length=1)
    conversation_id: str | None = None


class MissingFact(StrictModel):
    name: str
    reason: str
    question: str | None = None


class QueryState(StrictModel):
    """Kết quả Gemini trích xuất từ câu hỏi người dùng."""

    life_event: str | None = None
    intent: Intent = Intent.UNKNOWN
    topics: list[str] = Field(default_factory=list)
    target: str | None = None
    facts: dict[str, Any] = Field(default_factory=dict)
    missing_facts: list[MissingFact] = Field(default_factory=list)


class ConversationState(StrictModel):
    conversation_id: str
    query_state: QueryState
    pending_questions: list[str] = Field(default_factory=list)
    turn_count: int = Field(default=1, ge=1)


class RetrievalPlan(StrictModel):
    """Kế hoạch do router Python tạo; không phải output trực tiếp của LLM."""

    strategy: RetrievalStrategy
    procedure_query: str | None = None
    law_query: str | None = None
    procedure_ids: list[str] = Field(default_factory=list)
    procedure_chunk_types: list[str] = Field(default_factory=list)
    qdrant_filters: dict[str, Any] = Field(default_factory=dict)
    use_procedure_vector_search: bool = False
    use_graph_traversal: bool = False
    include_benefits: bool = False
    include_legal_evidence: bool = False
    use_law_vector_search: bool = False
    needs_clarification: bool = False


class RetrievedChunk(StrictModel):
    collection: str
    point_id: str
    doc_id: str
    chunk_id: str | None = None
    chunk_type: str | None = None
    text: str
    score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProcedureEvidence(StrictModel):
    procedure_id: str
    name: str
    authority: str | None = None
    eligibility: str | None = None
    source_url: str | None = None
    vector_score: float | None = None
    chunks: list[RetrievedChunk] = Field(default_factory=list)


class LegalEvidence(StrictModel):
    law_id: str
    law_title: str | None = None
    validity: str | None = None
    section_id: str
    section_order: int | None = None
    heading: str | None = None
    text: str | None = None
    source_url: str | None = None
    relation_scope: str | None = None
    retrieval_score: float | None = None


class ProcedureGraphRelation(StrictModel):
    source_id: str
    relationship_type: str
    target: ProcedureEvidence


class BenefitGraphRelation(StrictModel):
    procedure_id: str
    benefit_id: str | None = None
    anchor_section_id: str | None = None
    title: str | None = None
    note: str | None = None
    evidence: LegalEvidence


class GraphRetrievalResult(StrictModel):
    procedures: list[ProcedureEvidence] = Field(default_factory=list)
    procedure_relations: list[ProcedureGraphRelation] = Field(default_factory=list)
    benefit_relations: list[BenefitGraphRelation] = Field(default_factory=list)


class JourneyItem(StrictModel):
    procedure_id: str
    name: str
    priority: int = Field(ge=1)
    category: JourneyCategory
    status: JourneyStatus = JourneyStatus.UNKNOWN
    reason: str | None = None
    depends_on: list[str] = Field(default_factory=list)


class BenefitEvidence(StrictModel):
    related_procedure_id: str
    title: str
    eligibility_status: EligibilityStatus = EligibilityStatus.UNKNOWN
    reason: str | None = None
    missing_facts: list[str] = Field(default_factory=list)
    legal_evidence: list[LegalEvidence] = Field(default_factory=list)


class ResponseRules(StrictModel):
    demo_scope: str | None = None
    must_cite_claims: bool = True
    must_not_invent_procedures: bool = True
    must_mark_uncertain_benefits: bool = True


class AnswerContext(StrictModel):
    query: UserQuery
    query_state: QueryState
    journey: list[JourneyItem] = Field(default_factory=list)
    procedure_evidence: list[ProcedureEvidence] = Field(default_factory=list)
    benefits: list[BenefitEvidence] = Field(default_factory=list)
    legal_evidence: list[LegalEvidence] = Field(default_factory=list)
    response_rules: ResponseRules = Field(default_factory=ResponseRules)


class SourceReference(StrictModel):
    source_type: str
    source_id: str
    title: str
    url: str | None = None


class BenefitAssessmentDraft(StrictModel):
    title: str
    eligibility_status: EligibilityStatus
    reason: str
    missing_facts: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list, max_length=3)


class AnswerDraft(StrictModel):
    """Phần duy nhất do Gemini sinh ở bước tạo câu trả lời."""

    answer_markdown: str = Field(min_length=1)
    follow_up_questions: list[str] = Field(default_factory=list, max_length=3)
    benefit_assessments: list[BenefitAssessmentDraft] = Field(default_factory=list)


class AnswerRepairDraft(StrictModel):
    answer_markdown: str = Field(min_length=1)


class RAGResponse(StrictModel):
    answer_markdown: str
    journey: list[JourneyItem] = Field(default_factory=list)
    benefits: list[BenefitEvidence] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    sources: list[SourceReference] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ValidationIssue(StrictModel):
    code: str
    severity: Literal["error", "warning"]
    message: str
    excerpt: str | None = None


class AnswerValidationResult(StrictModel):
    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    cited_source_ids: list[str] = Field(default_factory=list)
    unknown_citation_ids: list[str] = Field(default_factory=list)
    missing_procedure_citations: list[str] = Field(default_factory=list)
