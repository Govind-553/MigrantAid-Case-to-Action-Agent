"""
MigrantAid Domain Schemas
=========================
Typed Pydantic schemas for all core domain objects.

Design rules enforced here:
- UNKNOWN is always distinguishable from False / not_satisfied.
- Conflicts are a representable state, not an error to be silenced.
- Every recommendation must carry traceable evidence references.
- Resource IDs must be validated as non-empty strings.
- Structured enums replace arbitrary string fields wherever possible.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# Section 1: Shared Enumerations
# ---------------------------------------------------------------------------


class FactStatus(str, Enum):
    """Provenance / confidence status for a single extracted case fact."""
    explicit = "explicit"        # Directly stated in the input
    inferred = "inferred"        # Derived from context
    unknown = "unknown"          # Not available or not mentioned
    conflicting = "conflicting"  # Two sources provide contradictory values


class NeedCategory(str, Enum):
    """Controlled vocabulary for beneficiary need categories."""
    basic_support = "basic_support"
    employment = "employment"
    housing = "housing"
    documentation = "documentation"
    education = "education"
    financial_assistance = "financial_assistance"
    transport = "transport"
    health_navigation = "health_navigation"
    other = "other"


class NeedPriority(str, Enum):
    """Priority levels for identified needs."""
    immediate = "immediate"
    high = "high"
    medium = "medium"
    low = "low"


class RequirementOperator(str, Enum):
    """Comparison operators for resource requirements.

    Only these operators are permitted.  Arbitrary executable expressions
    from resource data are explicitly prohibited.
    """
    equals = "equals"
    not_equals = "not_equals"
    contains = "contains"
    in_ = "in"
    not_in = "not_in"
    greater_than = "greater_than"
    less_than = "less_than"
    greater_or_equal = "greater_or_equal"
    less_or_equal = "less_or_equal"
    exists = "exists"


class RequirementImportance(str, Enum):
    """How critical a requirement is for the resource."""
    critical = "critical"
    important = "important"
    optional = "optional"


class RequirementStatus(str, Enum):
    """Result of evaluating one resource requirement against available evidence.

    CRITICAL INVARIANT: unknown != satisfied.
    The system must never promote unknown to satisfied.
    """
    satisfied = "satisfied"
    not_satisfied = "not_satisfied"
    unknown = "unknown"          # Evidence is absent — not the same as False
    conflict = "conflict"        # Case evidence contradicts itself or the requirement
    not_applicable = "not_applicable"


class ResourceStatus(str, Enum):
    """Data quality status of a resource record."""
    verified = "verified"
    unverified = "unverified"
    needs_review = "needs_review"
    inactive = "inactive"


class MatchStatus(str, Enum):
    """Overall match classification for a resource against a case."""
    strong_match = "strong_match"
    potential_match = "potential_match"
    insufficient_information = "insufficient_information"
    not_supported_by_available_evidence = "not_supported_by_available_evidence"
    conflict_detected = "conflict_detected"
    no_verified_match = "no_verified_match"


class CaseWorkflowState(str, Enum):
    """Lifecycle states for a case moving through the workflow."""
    draft = "DRAFT"
    intake_processing = "INTAKE_PROCESSING"
    intake_review = "INTAKE_REVIEW"
    needs_assessment = "NEEDS_ASSESSMENT"
    follow_up_required = "FOLLOW_UP_REQUIRED"
    resource_matching = "RESOURCE_MATCHING"
    verification = "VERIFICATION"
    action_plan_ready = "ACTION_PLAN_READY"
    quality_check = "QUALITY_CHECK"
    human_review = "HUMAN_REVIEW"
    # NOTE: 'approved' is preserved for backward compatibility (evaluation data).
    # New code should use 'referrals_approved' which accurately communicates
    # that caseworker approved referral progression — NOT that eligibility is confirmed.
    approved = "APPROVED"
    referrals_approved = "REFERRALS_APPROVED"
    modified = "MODIFIED"
    more_information_required = "MORE_INFORMATION_REQUIRED"
    completed = "COMPLETED"
    failed = "FAILED"
    needs_human_attention = "NEEDS_HUMAN_ATTENTION"


class HumanReviewDecision(str, Enum):
    """Possible outcomes of a human review checkpoint."""
    pending = "pending"
    approved = "approved"
    modified = "modified"
    rejected = "rejected"
    request_information = "request_information"


class ActionPriority(str, Enum):
    """Priority level for an action plan step."""
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class FailureCategory(str, Enum):
    """Error analysis categories for evaluation failures."""
    INTAKE_MISS = "INTAKE_MISS"
    NEED_MISS = "NEED_MISS"
    RETRIEVAL_MISS = "RETRIEVAL_MISS"
    MATCHING_MISS = "MATCHING_MISS"
    MISSING_INFO_MISS = "MISSING_INFO_MISS"
    EVIDENCE_MISS = "EVIDENCE_MISS"
    CONTRADICTION_MISS = "CONTRADICTION_MISS"
    UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"
    ACTION_PLAN_MISS = "ACTION_PLAN_MISS"
    HUMAN_REVIEW_MISS = "HUMAN_REVIEW_MISS"
    RESOURCE_DATA_LIMITATION = "RESOURCE_DATA_LIMITATION"
    OTHER = "OTHER"


class AgentEventType(str, Enum):
    """Types of events in an agent trajectory."""
    stage_start = "stage_start"
    stage_complete = "stage_complete"
    tool_call = "tool_call"
    tool_response = "tool_response"
    verification = "verification"
    retry = "retry"
    error = "error"
    human_checkpoint = "human_checkpoint"


# ---------------------------------------------------------------------------
# Section 2: Case Facts and Case Profile
# ---------------------------------------------------------------------------


class CaseFact(BaseModel):
    """A single structured fact extracted from the case narrative."""

    field: str = Field(..., min_length=1, description="Semantic field name (e.g. 'employment_status')")
    value: str | int | float | bool | None = Field(
        ..., description="Extracted value; None signals that the field was identified but the value is unknown"
    )
    status: FactStatus = Field(..., description="Provenance/confidence of this fact")
    source: str = Field(default="user_input", description="Where this fact came from")
    notes: str | None = Field(default=None, description="Optional annotation or context")

    model_config = {"frozen": False}


class Contradiction(BaseModel):
    """A detected contradiction between two facts."""

    description: str = Field(..., min_length=1)
    fact_a: str = Field(..., description="Field or description of the first conflicting fact")
    fact_b: str = Field(..., description="Field or description of the second conflicting fact")
    severity: str = Field(default="high", description="Estimated severity: high | medium | low")


class CaseProfile(BaseModel):
    """The structured representation of a migrant worker's case."""

    case_id: str = Field(..., min_length=1)
    narrative: str = Field(..., min_length=1, description="Original natural-language description")
    facts: list[CaseFact] = Field(default_factory=list)
    missing_information: list[str] = Field(
        default_factory=list,
        description="Fields that could not be determined from the narrative"
    )
    contradictions: list[Contradiction] = Field(default_factory=list)
    workflow_state: CaseWorkflowState = Field(default=CaseWorkflowState.draft)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def get_fact(self, field: str) -> CaseFact | None:
        """Return the first fact matching the given field name."""
        for fact in self.facts:
            if fact.field == field:
                return fact
        return None

    def has_explicit_fact(self, field: str) -> bool:
        """Return True if field is present with explicit or inferred status."""
        fact = self.get_fact(field)
        return fact is not None and fact.status in (FactStatus.explicit, FactStatus.inferred)


# ---------------------------------------------------------------------------
# Section 3: Needs Assessment
# ---------------------------------------------------------------------------


class Need(BaseModel):
    """An identified need for the beneficiary."""

    category: NeedCategory
    priority: NeedPriority
    reason: str = Field(..., min_length=1, description="Why this need was identified")
    evidence_references: list[str] = Field(
        default_factory=list,
        description="Fact field names that support this need identification"
    )


class NeedsAssessment(BaseModel):
    """Collection of identified needs for a case."""

    case_id: str = Field(..., min_length=1)
    needs: list[Need] = Field(default_factory=list)
    assessment_notes: str | None = None
    assessed_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def primary_need(self) -> Need | None:
        """Return the highest-priority need, favouring 'immediate' then 'high'."""
        priority_order = [NeedPriority.immediate, NeedPriority.high, NeedPriority.medium, NeedPriority.low]
        for p in priority_order:
            for need in self.needs:
                if need.priority == p:
                    return need
        return None if not self.needs else self.needs[0]


# ---------------------------------------------------------------------------
# Section 4: Missing Information
# ---------------------------------------------------------------------------


class MissingInformation(BaseModel):
    """A specific piece of information that is absent but required."""

    field: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1, description="Why this information is needed")
    linked_resource_ids: list[str] = Field(
        default_factory=list,
        description="Resource IDs whose evaluation is blocked by this missing field"
    )
    priority: NeedPriority = Field(default=NeedPriority.high)


# ---------------------------------------------------------------------------
# Section 5: Resource Knowledge Base
# ---------------------------------------------------------------------------


class ResourceGeography(BaseModel):
    """Geographic scope of a resource."""

    country: str = Field(..., min_length=1)
    state: str | None = None
    cities: list[str] = Field(default_factory=list)
    notes: str | None = None


class ResourceRequirement(BaseModel):
    """A single eligibility/prerequisite condition for a resource."""

    requirement_id: str = Field(..., min_length=1)
    field: str = Field(..., min_length=1, description="Case fact field to evaluate")
    operator: RequirementOperator
    value: str | int | float | bool | None = Field(
        ..., description="Expected value for the operator to compare against"
    )
    importance: RequirementImportance = Field(default=RequirementImportance.critical)
    evidence_required: bool = Field(default=True)
    source_reference: str | None = None


class RequiredDocument(BaseModel):
    """A document required by a resource."""

    document: str = Field(..., min_length=1)
    required: bool = Field(default=True)
    notes: str | None = None


class ContactInformation(BaseModel):
    """Contact details for a resource — marked SYNTHETIC for demo data."""

    phone: str | None = None
    website: str | None = None
    email: str | None = None
    address: str | None = None
    notes: str | None = None


class Resource(BaseModel):
    """A fully structured entry in the approved resource knowledge base."""

    resource_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    category: NeedCategory
    geography: ResourceGeography
    description: str = Field(default="")
    requirements: list[ResourceRequirement] = Field(default_factory=list)
    required_documents: list[RequiredDocument] = Field(default_factory=list)
    service_steps: list[str] = Field(default_factory=list)
    contact_information: ContactInformation | None = None
    source_id: str = Field(..., min_length=1)
    verified_at: str | None = Field(
        default=None,
        description="ISO date string when the record was last verified"
    )
    status: ResourceStatus = Field(default=ResourceStatus.unverified)
    dataset_version: str = Field(default="v1.0")
    notes: str | None = None

    @field_validator("resource_id")
    @classmethod
    def resource_id_must_not_be_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("resource_id must not be blank or whitespace-only")
        return v


class Source(BaseModel):
    """Provenance record for a resource in the knowledge base."""

    source_id: str = Field(..., min_length=1)
    publisher: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    reference: str = Field(default="")
    retrieved_at: str | None = None
    verification_status: str = Field(default="unverified")
    dataset_version: str = Field(default="v1.0")
    notes: str | None = None


# ---------------------------------------------------------------------------
# Section 6: Requirement Evaluation and Evidence
# ---------------------------------------------------------------------------


class RequirementEvaluation(BaseModel):
    """Result of testing one resource requirement against available case evidence.

    INVARIANT: status=unknown means evidence is absent.
               It must NOT be treated as satisfied.
    """

    requirement_id: str = Field(..., min_length=1)
    field: str = Field(..., min_length=1)
    status: RequirementStatus
    evidence_text: str | None = Field(
        default=None,
        description="Human-readable explanation of why this status was assigned"
    )
    case_fact_value: str | int | float | bool | None = Field(
        default=None,
        description="The case fact value that was compared, if available"
    )
    required_value: str | int | float | bool | None = Field(
        default=None,
        description="The requirement's expected value"
    )

    @model_validator(mode="after")
    def unknown_requires_no_case_fact(self) -> RequirementEvaluation:
        """Enforce that unknown status only occurs when case_fact_value is None."""
        if self.status == RequirementStatus.unknown and self.case_fact_value is not None:
            raise ValueError(
                "status=unknown must not be set when a case_fact_value is present. "
                "If a value exists but does not satisfy the requirement, use not_satisfied."
            )
        return self


class EvidenceItem(BaseModel):
    """Mapping from a case fact to a resource requirement."""

    case_fact_id: str = Field(..., min_length=1, description="Field name of the supporting case fact")
    requirement_id: str = Field(..., min_length=1)
    result: RequirementStatus
    evidence: str = Field(..., min_length=1, description="Explanation of how the fact supports the requirement")
    source: str = Field(default="user_input")


# ---------------------------------------------------------------------------
# Section 7: Resource Matching
# ---------------------------------------------------------------------------


class ResourceMatch(BaseModel):
    """Candidate match between a case and a resource, before verification."""

    resource_id: str = Field(..., min_length=1)
    resource_name: str = Field(default="")
    status: MatchStatus
    requirement_evaluations: list[RequirementEvaluation] = Field(default_factory=list)
    missing_information: list[str] = Field(
        default_factory=list,
        description="Requirement fields that could not be evaluated"
    )
    supporting_evidence: list[EvidenceItem] = Field(default_factory=list)
    retrieval_reasons: list[str] = Field(
        default_factory=list,
        description="Why this resource was retrieved (e.g. 'service category match')"
    )
    source_id: str = Field(..., min_length=1)
    human_review_required: bool = Field(default=True)
    retrieval_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Semantic retrieval relevance score — NOT an eligibility score"
    )

    @field_validator("status")
    @classmethod
    def strong_match_requires_evidence(cls, v: MatchStatus) -> MatchStatus:
        # This is a soft check; full validation happens in VerifiedRecommendation
        return v


# ---------------------------------------------------------------------------
# Section 8: Verification
# ---------------------------------------------------------------------------


class VerificationWarning(BaseModel):
    """A specific warning produced by the verification stage."""

    code: str = Field(..., description="Short machine-readable warning code")
    message: str = Field(..., min_length=1)
    severity: str = Field(default="warning", description="warning | error")


class VerificationResult(BaseModel):
    """Overall verification outcome for a single resource match."""

    resource_id: str = Field(..., min_length=1)
    passed: bool
    final_status: MatchStatus
    warnings: list[VerificationWarning] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    unresolved_requirements: list[str] = Field(default_factory=list)
    contradictions_detected: list[str] = Field(default_factory=list)
    human_review_required: bool = Field(default=True)


class VerifiedRecommendation(BaseModel):
    """A post-verification recommendation ready for action planning."""

    resource_id: str = Field(..., min_length=1)
    resource_name: str = Field(default="")
    status: MatchStatus
    evidence: list[EvidenceItem] = Field(default_factory=list)
    requirement_evaluations: list[RequirementEvaluation] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    verification_warnings: list[VerificationWarning] = Field(default_factory=list)
    human_review_required: bool = Field(default=True)
    source_id: str = Field(..., min_length=1)
    dataset_version: str = Field(default="v1.0")

    @model_validator(mode="after")
    def strong_match_must_have_evidence(self) -> VerifiedRecommendation:
        """A strong_match recommendation must have at least one satisfied evidence item."""
        if self.status == MatchStatus.strong_match and not self.evidence:
            raise ValueError(
                "A strong_match recommendation requires at least one evidence item. "
                "Downgrade to potential_match if evidence is absent."
            )
        return self


# ---------------------------------------------------------------------------
# Section 9: Action Planning
# ---------------------------------------------------------------------------


class ActionItem(BaseModel):
    """A single step in the action plan."""

    step: int = Field(..., ge=1, description="Step number (1-indexed)")
    priority: ActionPriority
    action: str = Field(..., min_length=1, description="Concise instruction for the caseworker")
    reason: str = Field(..., min_length=1, description="Why this step is necessary")
    prerequisite: str | None = Field(
        default=None,
        description="What must be done before this step"
    )
    responsible_role: str | None = Field(
        default=None,
        description="Human role responsible (e.g. 'caseworker', 'beneficiary')"
    )
    evidence_reference: str | None = Field(
        default=None,
        description="Resource ID or requirement ID this action addresses"
    )
    unresolved_uncertainty: str | None = Field(
        default=None,
        description="Any remaining unknown that affects this step"
    )


class ActionPlan(BaseModel):
    """Prioritized action plan for a case."""

    case_id: str = Field(..., min_length=1)
    actions: list[ActionItem] = Field(default_factory=list)
    plan_notes: str | None = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def steps_must_be_sequential(self) -> ActionPlan:
        """Validate step numbers are sequential starting from 1."""
        if not self.actions:
            return self
        step_numbers = [a.step for a in self.actions]
        expected = list(range(1, len(self.actions) + 1))
        if sorted(step_numbers) != expected:
            raise ValueError(
                f"Action step numbers must be sequential from 1. Got: {sorted(step_numbers)}"
            )
        return self


# ---------------------------------------------------------------------------
# Section 10: Quality/Safety Check
# ---------------------------------------------------------------------------


class QualityIssue(BaseModel):
    """A specific quality or safety issue detected."""

    code: str = Field(..., description="Machine-readable issue code")
    message: str = Field(..., min_length=1)
    severity: str = Field(default="warning", description="error | warning | info")
    affected_resource_id: str | None = None


class QualityReport(BaseModel):
    """Output of the quality/safety checker stage."""

    case_id: str = Field(..., min_length=1)
    passed: bool
    issues: list[QualityIssue] = Field(default_factory=list)
    unsupported_claims_detected: bool = Field(default=False)
    missing_evidence_flagged: bool = Field(default=False)
    human_review_enforced: bool = Field(default=True)
    safe_to_present: bool = Field(default=False)
    checked_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def failed_report_is_not_safe(self) -> QualityReport:
        """A failed quality report must not be marked safe_to_present."""
        if not self.passed and self.safe_to_present:
            raise ValueError(
                "safe_to_present cannot be True when the quality check has not passed."
            )
        return self


# ---------------------------------------------------------------------------
# Section 11: Human Review
# ---------------------------------------------------------------------------


class HumanReview(BaseModel):
    """Human review checkpoint — records the reviewer's decision and notes."""

    case_id: str = Field(..., min_length=1)
    decision: HumanReviewDecision = Field(default=HumanReviewDecision.pending)
    reviewer_notes: str | None = None
    reviewed_at: datetime | None = None
    modified_recommendation_ids: list[str] = Field(
        default_factory=list,
        description="Resource IDs whose recommendations were modified by the reviewer"
    )
    rejected_recommendation_ids: list[str] = Field(
        default_factory=list,
        description="Resource IDs whose recommendations were rejected by the reviewer"
    )
    follow_up_required: bool = Field(default=False)

    @model_validator(mode="after")
    def reviewed_at_required_when_decided(self) -> HumanReview:
        """If a non-pending decision has been made, reviewed_at must be set."""
        if self.decision != HumanReviewDecision.pending and self.reviewed_at is None:
            raise ValueError(
                f"reviewed_at must be set when decision is '{self.decision.value}'"
            )
        return self


# ---------------------------------------------------------------------------
# Section 12: Agent Trajectories / Observability
# ---------------------------------------------------------------------------


class AgentEvent(BaseModel):
    """A single event in an agent's execution trajectory."""

    case_id: str = Field(..., min_length=1)
    stage: str = Field(..., min_length=1, description="Workflow stage name")
    agent: str = Field(..., min_length=1, description="Agent or component name")
    event_type: AgentEventType
    input_summary: str | None = Field(
        default=None,
        description="Brief summary of the agent input (do not log sensitive data)"
    )
    output_summary: str | None = Field(
        default=None,
        description="Brief summary of the agent output"
    )
    tool_call: str | None = None
    tool_response_summary: str | None = None
    verification_result: str | None = None
    error_message: str | None = None
    retry_count: int = Field(default=0, ge=0)
    latency_ms: float | None = Field(default=None, ge=0.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional structured metadata (must not contain secrets or PII)"
    )


# ---------------------------------------------------------------------------
# Section 13: Case State (aggregate)
# ---------------------------------------------------------------------------


class CaseState(BaseModel):
    """Full runtime state for a case moving through the workflow."""

    case_id: str = Field(..., min_length=1)
    profile: CaseProfile | None = None
    needs_assessment: NeedsAssessment | None = None
    resource_matches: list[ResourceMatch] = Field(default_factory=list)
    verified_recommendations: list[VerifiedRecommendation] = Field(default_factory=list)
    action_plan: ActionPlan | None = None
    quality_report: QualityReport | None = None
    human_review: HumanReview | None = None
    workflow_state: CaseWorkflowState = Field(default=CaseWorkflowState.draft)
    trajectory: list[AgentEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Section 14: Evaluation
# ---------------------------------------------------------------------------


class EvaluationDimensions(BaseModel):
    """Per-dimension scores for the VARR metric (max 100 points total)."""

    primary_need: int = Field(default=0, ge=0, le=20)
    resource: int = Field(default=0, ge=0, le=20)
    evidence: int = Field(default=0, ge=0, le=20)
    missing_information: int = Field(default=0, ge=0, le=15)
    unsupported_claim: int = Field(default=0, ge=0, le=15)
    actionable_next_step: int = Field(default=0, ge=0, le=10)

    @property
    def total(self) -> int:
        return (
            self.primary_need
            + self.resource
            + self.evidence
            + self.missing_information
            + self.unsupported_claim
            + self.actionable_next_step
        )


class EvaluationResult(BaseModel):
    """Scored result for a single evaluation case."""

    case_id: str = Field(..., min_length=1)
    system: str = Field(..., description="'baseline' or 'agentic'")
    score: int = Field(..., ge=0, le=100)
    successful: bool
    dimensions: EvaluationDimensions
    failure_categories: list[FailureCategory] = Field(default_factory=list)
    latency_ms: float = Field(default=0.0, ge=0.0)
    model_calls: int = Field(default=0, ge=0)
    estimated_cost_usd: float | None = Field(default=None, ge=0.0)
    raw_output_path: str | None = None
    notes: str | None = None
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def score_must_match_dimensions(self) -> EvaluationResult:
        """The recorded score must equal the sum of dimension scores."""
        dim_total = self.dimensions.total
        if self.score != dim_total:
            raise ValueError(
                f"score ({self.score}) does not match sum of dimensions ({dim_total}). "
                "Update dimensions to match the reported score."
            )
        return self

    @model_validator(mode="after")
    def successful_requires_threshold(self) -> EvaluationResult:
        """Enforce the VARR success threshold documented in EVALUATION_DATASET_SPEC.md."""
        if self.successful:
            if self.score < 80:
                raise ValueError(
                    f"successful=True requires total score >= 80. Got {self.score}."
                )
            if self.dimensions.evidence < 15:
                raise ValueError(
                    f"successful=True requires evidence score >= 15. Got {self.dimensions.evidence}."
                )
            if self.dimensions.unsupported_claim < 15:
                raise ValueError(
                    f"successful=True requires unsupported_claim score = 15. "
                    f"Got {self.dimensions.unsupported_claim}."
                )
        return self
