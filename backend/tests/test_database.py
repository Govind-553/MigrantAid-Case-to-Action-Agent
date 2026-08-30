"""
Database Persistence Test Suite
===============================
Tests PostgreSQL database connection, entity persistence, full case retrieval,
restart resilience, and error handling.
"""

import uuid
from datetime import datetime, timezone
import pytest

from app.db.connection import check_db_connection
from app.db.repository import CaseRepository
from app.schemas.domain import (
    ActionItem,
    ActionPlan,
    ActionPriority,
    AgentEvent,
    AgentEventType,
    CaseFact,
    CaseProfile,
    CaseState,
    CaseWorkflowState,
    EvidenceItem,
    FactStatus,
    HumanReview,
    HumanReviewDecision,
    MatchStatus,
    Need,
    NeedCategory,
    NeedPriority,
    NeedsAssessment,
    RequirementEvaluation,
    RequirementStatus,
    VerifiedRecommendation,
)
from app.services.case_workflow import CaseWorkflowService



@pytest.fixture
def repo():
    return CaseRepository()


@pytest.fixture
def sample_case_state():
    cid = f"TEST-CASE-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc)

    profile = CaseProfile(
        case_id=cid,
        narrative="Test migrant worker needs emergency housing and legal support.",
        facts=[
            CaseFact(field="location_country", value="Singapore", status=FactStatus.explicit, source="user_input"),
            CaseFact(field="age", value=30, status=FactStatus.explicit, source="user_input"),
            CaseFact(field="employment_status", value="unemployed", status=FactStatus.inferred, source="user_input"),
        ],
        missing_information=["work_pass_type"],
        workflow_state=CaseWorkflowState.intake_review,
        created_at=now,
        updated_at=now,
    )

    needs = NeedsAssessment(
        case_id=cid,
        needs=[
            Need(
                category=NeedCategory.housing,
                priority=NeedPriority.immediate,
                reason="Lacks safe shelter",
                evidence_references=["location_country"],
            ),
            Need(
                category=NeedCategory.employment,
                priority=NeedPriority.high,
                reason="Unemployed and requires job assistance",
                evidence_references=["employment_status"],
            ),
        ],
        assessed_at=now,
    )

    verified_recs = [
        VerifiedRecommendation(
            resource_id="RES-HOUSING-001",
            resource_name="Emergency Shelter Centre",
            status=MatchStatus.strong_match,
            evidence=[
                EvidenceItem(
                    case_fact_id="location_country",
                    requirement_id="REQ-SG-LOC",
                    result=RequirementStatus.satisfied,
                    evidence="Country is Singapore",
                )
            ],
            requirement_evaluations=[
                RequirementEvaluation(
                    requirement_id="REQ-SG-LOC",
                    field="location_country",
                    status=RequirementStatus.satisfied,
                    evidence_text="Country is Singapore",
                    case_fact_value="Singapore",
                    required_value="Singapore",
                )
            ],
            human_review_required=True,
            source_id="SRC-001",
        )
    ]


    action_plan = ActionPlan(
        case_id=cid,
        actions=[
            ActionItem(
                step=1,
                priority=ActionPriority.critical,
                action="Contact shelter immediately",
                reason="High priority housing need",
                responsible_role="caseworker",
            )
        ],
        generated_at=now,
    )

    human_review = HumanReview(
        case_id=cid,
        decision=HumanReviewDecision.approved,
        reviewer_notes="Verified facts and approved shelter recommendation.",
        reviewed_at=now,
        modified_recommendation_ids=[],
        rejected_recommendation_ids=[],
        follow_up_required=False,
    )

    trajectory = [
        AgentEvent(
            case_id=cid,
            stage="intake",
            agent="IntakeAgent",
            event_type=AgentEventType.stage_complete,
            output_summary="Extracted facts successfully",
            latency_ms=120.0,
            timestamp=now,
        )
    ]

    return CaseState(
        case_id=cid,
        profile=profile,
        needs_assessment=needs,
        verified_recommendations=verified_recs,
        action_plan=action_plan,
        human_review=human_review,
        workflow_state=CaseWorkflowState.approved,
        trajectory=trajectory,
        created_at=now,
        updated_at=now,
    )


def test_database_connection():
    """Verify database connection health check."""
    assert check_db_connection() is True


def test_full_case_persistence_and_retrieval(repo, sample_case_state):
    """Verify saving and retrieving all entities: Facts, Needs, Recommendations, Verification, Action Plan, Human Review, Trajectory."""
    cid = sample_case_state.case_id

    # 1. Save case
    repo.save_case(sample_case_state)

    # 2. Retrieve case
    loaded = repo.get_case(cid)
    assert loaded is not None
    assert loaded.case_id == cid
    assert loaded.profile is not None
    assert loaded.profile.narrative == sample_case_state.profile.narrative
    assert len(loaded.profile.facts) == 3
    assert loaded.profile.facts[0].field == "location_country"
    assert loaded.profile.facts[0].value == "Singapore"

    # Needs
    assert loaded.needs_assessment is not None
    assert len(loaded.needs_assessment.needs) == 2
    assert loaded.needs_assessment.needs[0].category == NeedCategory.housing

    # Recommendations & Verification
    assert len(loaded.verified_recommendations) == 1
    assert loaded.verified_recommendations[0].resource_id == "RES-HOUSING-001"
    assert len(loaded.verified_recommendations[0].requirement_evaluations) == 1
    assert loaded.verified_recommendations[0].requirement_evaluations[0].status == RequirementStatus.satisfied

    # Action Plan
    assert loaded.action_plan is not None
    assert len(loaded.action_plan.actions) == 1
    assert loaded.action_plan.actions[0].action == "Contact shelter immediately"

    # Human Review
    assert loaded.human_review is not None
    assert loaded.human_review.decision == HumanReviewDecision.approved
    assert loaded.human_review.reviewer_notes == "Verified facts and approved shelter recommendation."

    # Trajectory
    assert len(loaded.trajectory) == 1
    assert loaded.trajectory[0].agent == "IntakeAgent"


def test_case_retrieval_after_backend_restart(sample_case_state):
    """Verify that case persists across service restarts (clearing in-memory cache)."""
    service = CaseWorkflowService()
    cid = sample_case_state.case_id

    # Save via service
    service.repo.save_case(sample_case_state)

    # Simulate restart by creating a new service instance with empty in-memory cache
    restarted_service = CaseWorkflowService()
    assert cid not in restarted_service._cases

    # Retrieve from DB via restarted service
    restarted_case = restarted_service.get_case(cid)
    assert restarted_case is not None
    assert restarted_case.case_id == cid
    assert restarted_case.profile.narrative == sample_case_state.profile.narrative


def test_list_cases_persistence(repo, sample_case_state):
    """Verify case summary listing retrieves persisted case metadata."""
    repo.save_case(sample_case_state)
    summaries = repo.list_cases()
    assert len(summaries) > 0
    match = next((s for s in summaries if s["case_id"] == sample_case_state.case_id), None)
    assert match is not None
    assert match["workflow_state"] == "APPROVED"
