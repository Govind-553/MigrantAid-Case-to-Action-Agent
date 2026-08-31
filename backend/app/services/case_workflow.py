"""
Case Workflow & State Management Service
========================================

Manages persistent in-memory case state, fact updates, re-verification,
and human caseworker review decisions.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.agents.orchestrator import CaseOrchestrator
from app.db.repository import CaseRepository
from app.schemas.domain import (
    AgentEvent,
    AgentEventType,
    CaseFact,
    CaseProfile,
    CaseState,
    CaseWorkflowState,
    HumanReview,
    HumanReviewDecision,
)
from app.services.resource_kb import ResourceKB, load_resource_kb

logger = logging.getLogger("migrantaid")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESOURCES_PATH = DATA_DIR / "resources.json"
SOURCES_PATH = DATA_DIR / "sources.json"


class CaseWorkflowService:
    """Manages active cases, fact edits, re-verification, and review lifecycle with PostgreSQL persistence."""

    def __init__(self, kb: ResourceKB | None = None):
        self.kb = kb or load_resource_kb(RESOURCES_PATH, SOURCES_PATH)
        self.orchestrator = CaseOrchestrator()
        self.repo = CaseRepository()
        self._cases: dict[str, CaseState] = {}
        self._case_counter = 1

    def create_case(self, narrative: str, case_id: str | None = None) -> CaseState:
        """Create a new case from raw narrative, execute the agentic workflow, and persist state."""
        if not case_id:
            case_id = f"CASE-LIVE-{self._case_counter:03d}"
            self._case_counter += 1

        logger.info(f"Creating case {case_id}")
        case_state = self.orchestrator.process_case(case_id, narrative, self.kb)
        self._cases[case_id] = case_state

        try:
            self.repo.save_case(case_state)
        except Exception as e:
            logger.error(f"Failed to persist case {case_id} to database: {e!s}")

        return case_state

    def get_case(self, case_id: str) -> CaseState | None:
        """Retrieve full state for a given case ID from database or memory cache."""
        try:
            db_case = self.repo.get_case(case_id)
            if db_case:
                self._cases[case_id] = db_case
                return db_case
        except Exception as e:
            logger.warning(f"Database lookup failed for case {case_id}: {e!s}. Falling back to memory.")

        return self._cases.get(case_id)

    def list_cases(self) -> list[dict[str, Any]]:
        """List summary info for all cases from database or memory cache."""
        try:
            db_list = self.repo.list_cases()
            if db_list:
                return db_list
        except Exception as e:
            logger.warning(f"Database list failed: {e!s}. Falling back to memory cache.")

        summaries = []
        for cid, state in self._cases.items():
            primary_need = state.needs_assessment.primary_need.category.value if state.needs_assessment and state.needs_assessment.primary_need else "unknown"
            summaries.append({
                "case_id": cid,
                "workflow_state": state.workflow_state.value,
                "primary_need": primary_need,
                "verified_recommendations_count": len(state.verified_recommendations),
                "created_at": state.created_at.isoformat(),
                "updated_at": state.updated_at.isoformat(),
                "has_missing_info": bool(state.profile.missing_information) if state.profile else False,
                "has_contradictions": bool(state.profile.contradictions) if state.profile else False,
            })
        return summaries

    def update_case_facts(self, case_id: str, updated_facts: list[CaseFact]) -> CaseState | None:
        """Update case facts (e.g. from caseworker corrections) and re-run downstream pipeline."""
        state = self.get_case(case_id)
        if not state or not state.profile:
            return None

        logger.info(f"Updating facts for case {case_id} and re-running verification...")

        # Update profile with new facts
        new_profile = CaseProfile(
            case_id=case_id,
            narrative=state.profile.narrative,
            facts=updated_facts,
            missing_information=[],  # Re-evaluate
            contradictions=state.profile.contradictions,
            workflow_state=CaseWorkflowState.intake_processing,
        )

        # Log fact update event
        state.trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="human_fact_edit",
                agent="Caseworker",
                event_type=AgentEventType.human_checkpoint,
                output_summary=f"Caseworker updated {len(updated_facts)} facts. Re-running matching & verification.",
            )
        )

        # Re-run pipeline with updated profile
        new_state = self.orchestrator.process_case(
            case_id=case_id,
            narrative=state.profile.narrative,
            kb=self.kb,
            initial_profile=new_profile,
        )

        # Preserve previous trajectory
        new_state.trajectory = state.trajectory + new_state.trajectory
        self._cases[case_id] = new_state

        try:
            self.repo.save_case(new_state)
        except Exception as e:
            logger.error(f"Failed to save updated facts for case {case_id} to database: {e!s}")

        return new_state

    def submit_human_review(
        self,
        case_id: str,
        decision: HumanReviewDecision,
        reviewer_notes: str | None = None,
        modified_recommendation_ids: list[str] | None = None,
        rejected_recommendation_ids: list[str] | None = None,
    ) -> CaseState | None:
        """Record human review decision and transition workflow state."""
        state = self.get_case(case_id)
        if not state:
            return None

        logger.info(f"Submitting human review for case {case_id}: decision={decision.value}")

        now = datetime.now(timezone.utc)
        review = HumanReview(
            case_id=case_id,
            decision=decision,
            reviewer_notes=reviewer_notes,
            reviewed_at=now,
            modified_recommendation_ids=modified_recommendation_ids or [],
            rejected_recommendation_ids=rejected_recommendation_ids or [],
            follow_up_required=(decision == HumanReviewDecision.request_information),
        )

        state.human_review = review
        state.updated_at = now

        # Transition workflow state based on decision
        # IMPORTANT: 'approved' decision means the caseworker approved REFERRALS for
        # progression — it does NOT mean the beneficiary has been determined eligible.
        # Eligibility conditions may still be unresolved (UNKNOWN).
        if decision == HumanReviewDecision.approved:
            state.workflow_state = CaseWorkflowState.referrals_approved
        elif decision == HumanReviewDecision.modified:
            state.workflow_state = CaseWorkflowState.modified
        elif decision == HumanReviewDecision.request_information:
            state.workflow_state = CaseWorkflowState.more_information_required
        elif decision == HumanReviewDecision.rejected:
            state.workflow_state = CaseWorkflowState.completed

        state.trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="human_review",
                agent="Caseworker",
                event_type=AgentEventType.human_checkpoint,
                output_summary=(
                    f"Caseworker decision: Referrals approved for progression. "
                    f"Eligibility: Pending — unresolved conditions may remain. "
                    f"Notes: {reviewer_notes or 'None'}"
                ) if decision == HumanReviewDecision.approved else (
                    f"Caseworker review completed: decision={decision.value}. "
                    f"Notes: {reviewer_notes or 'None'}"
                ),
            )
        )

        self._cases[case_id] = state

        try:
            self.repo.save_case(state)
        except Exception as e:
            logger.error(f"Failed to save human review for case {case_id} to database: {e!s}")

        return state


# Singleton service instance
workflow_service = CaseWorkflowService()

