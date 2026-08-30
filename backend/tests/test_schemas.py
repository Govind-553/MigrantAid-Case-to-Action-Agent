"""
Unit tests for MigrantAid domain schemas.

Covers:
- Valid object construction
- Invalid object rejection (missing fields, wrong types)
- Critical invariant: unknown != satisfied
- Critical invariant: conflicting states are representable
- Critical invariant: strong_match requires evidence
- Critical invariant: failed quality report cannot be safe_to_present
- Critical invariant: successful evaluation requires threshold
- Malformed resource records are rejected
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.domain import (
    ActionItem,
    ActionPlan,
    ActionPriority,
    AgentEvent,
    AgentEventType,
    CaseFact,
    CaseProfile,
    CaseWorkflowState,
    Contradiction,
    EvaluationDimensions,
    EvaluationResult,
    EvidenceItem,
    FactStatus,
    FailureCategory,
    HumanReview,
    HumanReviewDecision,
    MatchStatus,
    Need,
    NeedCategory,
    NeedPriority,
    NeedsAssessment,
    QualityIssue,
    QualityReport,
    RequiredDocument,
    RequirementEvaluation,
    RequirementImportance,
    RequirementOperator,
    RequirementStatus,
    Resource,
    ResourceGeography,
    ResourceMatch,
    ResourceRequirement,
    ResourceStatus,
    VerifiedRecommendation,
)

# ---------------------------------------------------------------------------
# Fixtures: valid minimal objects for reuse
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_case_fact():
    return CaseFact(
        field="employment_status",
        value="unemployed",
        status=FactStatus.explicit,
        source="user_input",
    )


@pytest.fixture
def valid_case_profile(valid_case_fact):
    return CaseProfile(
        case_id="CASE-001",
        narrative="A migrant worker recently lost his job in Pune.",
        facts=[valid_case_fact],
        workflow_state=CaseWorkflowState.draft,
    )


@pytest.fixture
def valid_resource():
    return Resource(
        resource_id="RES-EMP-001",
        name="Synthetic Employment Support Centre A",
        category=NeedCategory.employment,
        geography=ResourceGeography(country="India", state="Maharashtra", cities=["Pune"]),
        requirements=[
            ResourceRequirement(
                requirement_id="REQ-EMP-A-1",
                field="employment_status",
                operator=RequirementOperator.equals,
                value="unemployed",
                importance=RequirementImportance.critical,
                evidence_required=True,
            )
        ],
        required_documents=[RequiredDocument(document="identity_document", required=True)],
        source_id="SRC-EMP-A",
        verified_at="2026-08-01",
        status=ResourceStatus.verified,
        dataset_version="v1.0",
    )


@pytest.fixture
def valid_evidence_item():
    return EvidenceItem(
        case_fact_id="employment_status",
        requirement_id="REQ-EMP-A-1",
        result=RequirementStatus.satisfied,
        evidence="Case narrative explicitly states the worker is unemployed.",
        source="user_input",
    )


@pytest.fixture
def valid_requirement_eval_satisfied():
    return RequirementEvaluation(
        requirement_id="REQ-EMP-A-1",
        field="employment_status",
        status=RequirementStatus.satisfied,
        evidence_text="employment_status == 'unemployed'",
        case_fact_value="unemployed",
        required_value="unemployed",
    )


# ---------------------------------------------------------------------------
# CaseFact tests
# ---------------------------------------------------------------------------

class TestCaseFact:
    def test_valid_explicit_fact(self, valid_case_fact):
        assert valid_case_fact.field == "employment_status"
        assert valid_case_fact.status == FactStatus.explicit

    def test_valid_unknown_fact(self):
        fact = CaseFact(
            field="household_income",
            value=None,
            status=FactStatus.unknown,
            source="user_input",
        )
        assert fact.status == FactStatus.unknown
        assert fact.value is None

    def test_unknown_fact_value_is_none(self):
        """Unknown status must be representable with None value."""
        fact = CaseFact(field="income", value=None, status=FactStatus.unknown, source="user_input")
        assert fact.value is None

    def test_conflicting_fact_is_valid(self):
        """Conflicting status is a valid, representable state."""
        fact = CaseFact(
            field="employment_status",
            value="conflicting_unemployed_and_part_time",
            status=FactStatus.conflicting,
            source="user_input",
        )
        assert fact.status == FactStatus.conflicting

    def test_missing_field_raises_error(self):
        with pytest.raises(ValidationError):
            CaseFact(value="unemployed", status=FactStatus.explicit, source="user_input")  # type: ignore[call-arg]

    def test_missing_status_raises_error(self):
        with pytest.raises(ValidationError):
            CaseFact(field="employment_status", value="unemployed", source="user_input")  # type: ignore[call-arg]

    def test_empty_field_name_raises_error(self):
        with pytest.raises(ValidationError):
            CaseFact(field="", value="unemployed", status=FactStatus.explicit, source="user_input")

    def test_invalid_status_raises_error(self):
        with pytest.raises(ValidationError):
            CaseFact(field="employment_status", value="unemployed", status="maybe", source="user_input")


# ---------------------------------------------------------------------------
# CaseProfile tests
# ---------------------------------------------------------------------------

class TestCaseProfile:
    def test_valid_profile(self, valid_case_profile):
        assert valid_case_profile.case_id == "CASE-001"
        assert len(valid_case_profile.facts) == 1
        assert valid_case_profile.workflow_state == CaseWorkflowState.draft

    def test_empty_case_id_raises_error(self):
        with pytest.raises(ValidationError):
            CaseProfile(case_id="", narrative="Some description")

    def test_empty_narrative_raises_error(self):
        with pytest.raises(ValidationError):
            CaseProfile(case_id="CASE-001", narrative="")

    def test_get_fact_returns_matching_fact(self, valid_case_profile):
        fact = valid_case_profile.get_fact("employment_status")
        assert fact is not None
        assert fact.value == "unemployed"

    def test_get_fact_returns_none_for_missing_field(self, valid_case_profile):
        fact = valid_case_profile.get_fact("household_income")
        assert fact is None

    def test_has_explicit_fact_returns_true_for_explicit(self, valid_case_profile):
        assert valid_case_profile.has_explicit_fact("employment_status") is True

    def test_has_explicit_fact_returns_false_for_unknown(self):
        profile = CaseProfile(
            case_id="CASE-002",
            narrative="Description",
            facts=[CaseFact(field="income", value=None, status=FactStatus.unknown, source="user_input")],
        )
        assert profile.has_explicit_fact("income") is False

    def test_contradictions_are_representable(self):
        profile = CaseProfile(
            case_id="CASE-008",
            narrative="Worker says unemployed but also mentions part-time work.",
            contradictions=[
                Contradiction(
                    description="Employment status conflict",
                    fact_a="employment_status=unemployed",
                    fact_b="part_time_work=true",
                )
            ],
        )
        assert len(profile.contradictions) == 1
        assert profile.contradictions[0].fact_a == "employment_status=unemployed"


# ---------------------------------------------------------------------------
# RequirementEvaluation — UNKNOWN != SATISFIED invariant
# ---------------------------------------------------------------------------

class TestRequirementEvaluation:
    def test_satisfied_with_value(self, valid_requirement_eval_satisfied):
        assert valid_requirement_eval_satisfied.status == RequirementStatus.satisfied

    def test_unknown_with_no_value_is_valid(self):
        """unknown + None case_fact_value is valid and must not be promoted to satisfied."""
        req_eval = RequirementEvaluation(
            requirement_id="REQ-EMP-B-2",
            field="secondary_document",
            status=RequirementStatus.unknown,
            case_fact_value=None,
        )
        assert req_eval.status == RequirementStatus.unknown

    def test_unknown_with_present_value_raises_error(self):
        """INVARIANT: If a value is present, status must not be unknown."""
        with pytest.raises(ValidationError, match="status=unknown must not be set"):
            RequirementEvaluation(
                requirement_id="REQ-EMP-B-2",
                field="secondary_document",
                status=RequirementStatus.unknown,
                case_fact_value="some_value",  # Value present but status=unknown — invalid
            )

    def test_unknown_is_distinct_from_not_satisfied(self):
        unknown = RequirementEvaluation(
            requirement_id="REQ-1", field="income", status=RequirementStatus.unknown, case_fact_value=None
        )
        not_sat = RequirementEvaluation(
            requirement_id="REQ-1",
            field="income",
            status=RequirementStatus.not_satisfied,
            case_fact_value="50000",
            required_value="0",
        )
        assert unknown.status != not_sat.status
        assert unknown.status != RequirementStatus.satisfied

    def test_conflict_status_is_representable(self):
        req_eval = RequirementEvaluation(
            requirement_id="REQ-1",
            field="employment_status",
            status=RequirementStatus.conflict,
            evidence_text="Case says both unemployed and part-time",
        )
        assert req_eval.status == RequirementStatus.conflict

    def test_missing_requirement_id_raises_error(self):
        with pytest.raises(ValidationError):
            RequirementEvaluation(field="employment_status", status=RequirementStatus.satisfied)  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Resource tests
# ---------------------------------------------------------------------------

class TestResource:
    def test_valid_resource(self, valid_resource):
        assert valid_resource.resource_id == "RES-EMP-001"
        assert valid_resource.status == ResourceStatus.verified
        assert len(valid_resource.requirements) == 1

    def test_blank_resource_id_raises_error(self):
        with pytest.raises(ValidationError):
            Resource(
                resource_id="   ",
                name="Some Resource",
                category=NeedCategory.employment,
                geography=ResourceGeography(country="India"),
                source_id="SRC-001",
            )

    def test_empty_resource_id_raises_error(self):
        with pytest.raises(ValidationError):
            Resource(
                resource_id="",
                name="Some Resource",
                category=NeedCategory.employment,
                geography=ResourceGeography(country="India"),
                source_id="SRC-001",
            )

    def test_invalid_category_raises_error(self):
        with pytest.raises(ValidationError):
            Resource(
                resource_id="RES-001",
                name="Resource",
                category="invalid_category",  # Not in NeedCategory enum
                geography=ResourceGeography(country="India"),
                source_id="SRC-001",
            )

    def test_invalid_status_raises_error(self):
        with pytest.raises(ValidationError):
            Resource(
                resource_id="RES-001",
                name="Resource",
                category=NeedCategory.employment,
                geography=ResourceGeography(country="India"),
                source_id="SRC-001",
                status="active",  # Not a valid ResourceStatus
            )

    def test_resource_without_requirements_is_valid(self, valid_resource):
        """Resources with zero requirements are allowed (rare but valid)."""
        r = Resource(
            resource_id="RES-TEST",
            name="Open Resource",
            category=NeedCategory.other,
            geography=ResourceGeography(country="India"),
            source_id="SRC-TEST",
        )
        assert r.requirements == []

    def test_missing_source_id_raises_error(self):
        with pytest.raises(ValidationError):
            Resource(
                resource_id="RES-001",
                name="Resource",
                category=NeedCategory.employment,
                geography=ResourceGeography(country="India"),
            )


# ---------------------------------------------------------------------------
# ResourceMatch tests
# ---------------------------------------------------------------------------

class TestResourceMatch:
    def test_valid_potential_match(self, valid_evidence_item):
        match = ResourceMatch(
            resource_id="RES-EMP-001",
            status=MatchStatus.potential_match,
            supporting_evidence=[valid_evidence_item],
            source_id="SRC-EMP-A",
            retrieval_reasons=["category match", "geographic match"],
        )
        assert match.status == MatchStatus.potential_match
        assert match.human_review_required is True

    def test_retrieval_score_is_not_eligibility(self):
        """A retrieval_score of 0.99 does NOT mean eligible."""
        match = ResourceMatch(
            resource_id="RES-EMP-001",
            status=MatchStatus.potential_match,
            source_id="SRC-EMP-A",
            retrieval_score=0.99,
        )
        assert match.retrieval_score == 0.99
        # status is still potential_match, not strong_match
        assert match.status == MatchStatus.potential_match

    def test_retrieval_score_out_of_range_raises_error(self):
        with pytest.raises(ValidationError):
            ResourceMatch(
                resource_id="RES-EMP-001",
                status=MatchStatus.potential_match,
                source_id="SRC-EMP-A",
                retrieval_score=1.5,  # > 1.0
            )

    def test_no_verified_match_is_valid(self):
        match = ResourceMatch(
            resource_id="RES-EMP-001",
            status=MatchStatus.no_verified_match,
            source_id="SRC-EMP-A",
        )
        assert match.status == MatchStatus.no_verified_match


# ---------------------------------------------------------------------------
# VerifiedRecommendation — strong_match requires evidence invariant
# ---------------------------------------------------------------------------

class TestVerifiedRecommendation:
    def test_strong_match_with_evidence_is_valid(self, valid_evidence_item):
        rec = VerifiedRecommendation(
            resource_id="RES-EMP-001",
            status=MatchStatus.strong_match,
            evidence=[valid_evidence_item],
            source_id="SRC-EMP-A",
        )
        assert rec.status == MatchStatus.strong_match

    def test_strong_match_without_evidence_raises_error(self):
        """INVARIANT: strong_match requires at least one evidence item."""
        with pytest.raises(ValidationError, match="strong_match recommendation requires"):
            VerifiedRecommendation(
                resource_id="RES-EMP-001",
                status=MatchStatus.strong_match,
                evidence=[],  # empty — must fail
                source_id="SRC-EMP-A",
            )

    def test_potential_match_without_evidence_is_valid(self):
        """potential_match does not require evidence items (they may be missing)."""
        rec = VerifiedRecommendation(
            resource_id="RES-EMP-001",
            status=MatchStatus.potential_match,
            evidence=[],
            source_id="SRC-EMP-A",
        )
        assert rec.status == MatchStatus.potential_match

    def test_missing_source_id_raises_error(self):
        with pytest.raises(ValidationError):
            VerifiedRecommendation(
                resource_id="RES-EMP-001",
                status=MatchStatus.potential_match,
            )


# ---------------------------------------------------------------------------
# ActionPlan tests
# ---------------------------------------------------------------------------

class TestActionPlan:
    def test_valid_action_plan(self):
        plan = ActionPlan(
            case_id="CASE-001",
            actions=[
                ActionItem(step=1, priority=ActionPriority.high, action="Confirm income", reason="Required for RES-BASIC-001"),
                ActionItem(step=2, priority=ActionPriority.medium, action="Review employment resource", reason="Potential match found"),
            ],
        )
        assert len(plan.actions) == 2
        assert plan.actions[0].step == 1

    def test_non_sequential_steps_raise_error(self):
        with pytest.raises(ValidationError, match="sequential"):
            ActionPlan(
                case_id="CASE-001",
                actions=[
                    ActionItem(step=1, priority=ActionPriority.high, action="Step 1", reason="Reason"),
                    ActionItem(step=3, priority=ActionPriority.high, action="Step 3", reason="Reason"),  # skipped 2
                ],
            )

    def test_empty_action_plan_is_valid(self):
        plan = ActionPlan(case_id="CASE-001", actions=[])
        assert plan.actions == []

    def test_action_step_zero_raises_error(self):
        with pytest.raises(ValidationError):
            ActionItem(step=0, priority=ActionPriority.high, action="Step 0", reason="Invalid step")

    def test_action_missing_reason_raises_error(self):
        with pytest.raises(ValidationError):
            ActionItem(step=1, priority=ActionPriority.high, action="Do something")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# QualityReport tests
# ---------------------------------------------------------------------------

class TestQualityReport:
    def test_passed_report_can_be_safe(self):
        report = QualityReport(
            case_id="CASE-001",
            passed=True,
            safe_to_present=True,
        )
        assert report.safe_to_present is True

    def test_failed_report_cannot_be_safe(self):
        """INVARIANT: A failed quality report must not be marked safe_to_present."""
        with pytest.raises(ValidationError, match="safe_to_present cannot be True"):
            QualityReport(
                case_id="CASE-001",
                passed=False,
                safe_to_present=True,  # Must fail
            )

    def test_failed_report_not_safe_is_valid(self):
        report = QualityReport(
            case_id="CASE-001",
            passed=False,
            safe_to_present=False,
            issues=[QualityIssue(code="UNSUPPORTED_CLAIM", message="Eligibility claimed without evidence")],
        )
        assert report.safe_to_present is False
        assert len(report.issues) == 1


# ---------------------------------------------------------------------------
# HumanReview tests
# ---------------------------------------------------------------------------

class TestHumanReview:
    def test_pending_review_without_timestamp_is_valid(self):
        review = HumanReview(case_id="CASE-001", decision=HumanReviewDecision.pending)
        assert review.decision == HumanReviewDecision.pending
        assert review.reviewed_at is None

    def test_decided_review_requires_timestamp(self):
        """INVARIANT: A non-pending decision must have reviewed_at."""
        with pytest.raises(ValidationError, match="reviewed_at must be set"):
            HumanReview(
                case_id="CASE-001",
                decision=HumanReviewDecision.approved,
                reviewed_at=None,  # Must fail
            )

    def test_approved_review_with_timestamp_is_valid(self):
        review = HumanReview(
            case_id="CASE-001",
            decision=HumanReviewDecision.approved,
            reviewed_at=datetime.now(tz=timezone.utc),
        )
        assert review.decision == HumanReviewDecision.approved

    def test_modified_review_tracks_changed_ids(self):
        review = HumanReview(
            case_id="CASE-001",
            decision=HumanReviewDecision.modified,
            reviewed_at=datetime.now(tz=timezone.utc),
            modified_recommendation_ids=["RES-EMP-001"],
        )
        assert "RES-EMP-001" in review.modified_recommendation_ids


# ---------------------------------------------------------------------------
# EvaluationResult tests
# ---------------------------------------------------------------------------

class TestEvaluationResult:
    def _make_dims(self, primary=20, resource=20, evidence=20, missing=15, unsupported=15, action=10):
        return EvaluationDimensions(
            primary_need=primary,
            resource=resource,
            evidence=evidence,
            missing_information=missing,
            unsupported_claim=unsupported,
            actionable_next_step=action,
        )

    def test_valid_successful_result(self):
        dims = self._make_dims()
        result = EvaluationResult(
            case_id="CASE-001",
            system="baseline",
            score=100,
            successful=True,
            dimensions=dims,
        )
        assert result.score == 100
        assert result.successful is True

    def test_score_must_match_dimension_sum(self):
        dims = self._make_dims()  # total = 100
        with pytest.raises(ValidationError, match="does not match sum of dimensions"):
            EvaluationResult(
                case_id="CASE-001",
                system="baseline",
                score=90,  # Mismatch: dims total 100
                successful=True,
                dimensions=dims,
            )

    def test_successful_requires_score_80(self):
        dims = self._make_dims(primary=15, resource=15, evidence=15, missing=10, unsupported=15, action=5)
        # total = 75
        with pytest.raises(ValidationError, match="total score >= 80"):
            EvaluationResult(
                case_id="CASE-001",
                system="baseline",
                score=75,
                successful=True,  # Must fail: score < 80
                dimensions=dims,
            )

    def test_successful_requires_evidence_15(self):
        dims = self._make_dims(evidence=14, action=6)  # total = 90 but evidence < 15
        with pytest.raises(ValidationError, match="evidence score >= 15"):
            EvaluationResult(
                case_id="CASE-001",
                system="baseline",
                score=90,
                successful=True,
                dimensions=dims,
            )

    def test_successful_requires_unsupported_claim_15(self):
        # dims: 20+20+15+15+14+6 = 90; score=90 so mismatch check passes,
        # but unsupported_claim=14 < 15 so successful=True must still fail
        dims = self._make_dims(primary=20, resource=20, evidence=15, missing=15, unsupported=14, action=6)
        with pytest.raises(ValidationError, match="unsupported_claim score = 15"):
            EvaluationResult(
                case_id="CASE-001",
                system="baseline",
                score=90,
                successful=True,
                dimensions=dims,
            )

    def test_failed_result_with_low_score_is_valid(self):
        dims = self._make_dims(primary=10, resource=0, evidence=5, missing=5, unsupported=10, action=0)
        # total = 30
        result = EvaluationResult(
            case_id="CASE-009",
            system="baseline",
            score=30,
            successful=False,
            dimensions=dims,
            failure_categories=[FailureCategory.RETRIEVAL_MISS, FailureCategory.EVIDENCE_MISS],
        )
        assert result.successful is False
        assert FailureCategory.RETRIEVAL_MISS in result.failure_categories

    def test_dimension_total_property(self):
        dims = self._make_dims(primary=10, resource=10, evidence=15, missing=10, unsupported=15, action=5)
        assert dims.total == 65

    def test_dimension_out_of_range_raises_error(self):
        with pytest.raises(ValidationError):
            EvaluationDimensions(primary_need=25)  # max is 20

    def test_invalid_system_name_is_accepted(self):
        """system field is a free string — no enum constraint."""
        dims = self._make_dims(primary=5, resource=0, evidence=0, missing=0, unsupported=15, action=0)
        result = EvaluationResult(
            case_id="CASE-001",
            system="experimental_v2",
            score=20,
            successful=False,
            dimensions=dims,
        )
        assert result.system == "experimental_v2"


# ---------------------------------------------------------------------------
# NeedsAssessment tests
# ---------------------------------------------------------------------------

class TestNeedsAssessment:
    def test_primary_need_returns_highest_priority(self):
        assessment = NeedsAssessment(
            case_id="CASE-001",
            needs=[
                Need(category=NeedCategory.employment, priority=NeedPriority.high, reason="Unemployed"),
                Need(category=NeedCategory.housing, priority=NeedPriority.immediate, reason="Behind on rent"),
            ],
        )
        primary = assessment.primary_need
        assert primary is not None
        assert primary.priority == NeedPriority.immediate
        assert primary.category == NeedCategory.housing

    def test_empty_needs_returns_none(self):
        assessment = NeedsAssessment(case_id="CASE-001", needs=[])
        assert assessment.primary_need is None


# ---------------------------------------------------------------------------
# AgentEvent tests
# ---------------------------------------------------------------------------

class TestAgentEvent:
    def test_valid_agent_event(self):
        event = AgentEvent(
            case_id="CASE-001",
            stage="intake",
            agent="intake_agent",
            event_type=AgentEventType.stage_complete,
            output_summary="Extracted 5 facts",
            latency_ms=450.0,
        )
        assert event.event_type == AgentEventType.stage_complete
        assert event.retry_count == 0

    def test_negative_retry_count_raises_error(self):
        with pytest.raises(ValidationError):
            AgentEvent(
                case_id="CASE-001",
                stage="intake",
                agent="intake_agent",
                event_type=AgentEventType.retry,
                retry_count=-1,
            )

    def test_negative_latency_raises_error(self):
        with pytest.raises(ValidationError):
            AgentEvent(
                case_id="CASE-001",
                stage="intake",
                agent="intake_agent",
                event_type=AgentEventType.stage_start,
                latency_ms=-100.0,
            )
