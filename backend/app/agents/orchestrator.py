"""
Case-to-Action Agent Orchestrator
=================================

Orchestrates the multi-stage agentic workflow:
Intake → Needs Assessment → Retrieval & Verification → Action Planning → Quality Check → Human Review Gate.

Records a complete observable execution trajectory of AgentEvents.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from app.agents.action_planner import ActionPlanningAgent
from app.agents.intake_agent import IntakeAgent
from app.agents.matching_agent import MatchingAgent
from app.agents.needs_agent import NeedsAssessmentAgent
from app.agents.quality_agent import QualityAgent
from app.schemas.domain import (
    AgentEvent,
    AgentEventType,
    CaseProfile,
    CaseState,
    CaseWorkflowState,
    HumanReview,
    HumanReviewDecision,
)
from app.services.resource_kb import ResourceKB

logger = logging.getLogger("migrantaid")


class CaseOrchestrator:
    """Orchestrator driving the end-to-end case-to-action pipeline."""

    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.intake_agent = IntakeAgent(api_key=api_key, model_name=model_name)
        self.needs_agent = NeedsAssessmentAgent()
        self.matching_agent = MatchingAgent()
        self.action_planner = ActionPlanningAgent()
        self.quality_agent = QualityAgent()

    def process_case(
        self,
        case_id: str,
        narrative: str,
        kb: ResourceKB,
        initial_profile: CaseProfile | None = None,
    ) -> CaseState:
        """
        Execute the full end-to-end agentic workflow on a case narrative.

        Returns:
            A fully populated CaseState with all intermediate artifacts and trajectory.
        """
        pipeline_start = time.time()
        logger.info(f"CaseOrchestrator starting pipeline for case: {case_id}")
        trajectory: list[AgentEvent] = []

        # --- Stage 1: Intake & Fact Extraction ---
        s1_start = time.time()
        trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="intake",
                agent="IntakeAgent",
                event_type=AgentEventType.stage_start,
                input_summary=f"Case narrative ({len(narrative)} chars)",
            )
        )

        if initial_profile:
            profile = initial_profile
        else:
            profile = self.intake_agent.process(case_id, narrative)

        s1_latency = (time.time() - s1_start) * 1000
        trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="intake",
                agent="IntakeAgent",
                event_type=AgentEventType.stage_complete,
                output_summary=f"Extracted {len(profile.facts)} facts, {len(profile.missing_information)} missing fields, {len(profile.contradictions)} contradictions",
                latency_ms=s1_latency,
            )
        )

        # --- Stage 2: Needs Assessment ---
        s2_start = time.time()
        trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="needs_assessment",
                agent="NeedsAssessmentAgent",
                event_type=AgentEventType.stage_start,
                input_summary=f"Case profile with {len(profile.facts)} facts",
            )
        )

        needs_assessment = self.needs_agent.assess(profile)
        s2_latency = (time.time() - s2_start) * 1000

        trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="needs_assessment",
                agent="NeedsAssessmentAgent",
                event_type=AgentEventType.stage_complete,
                output_summary=f"Identified {len(needs_assessment.needs)} needs: {[n.category.value for n in needs_assessment.needs]}",
                latency_ms=s2_latency,
            )
        )

        # --- Stage 3: Retrieval & Verification ---
        s3_start = time.time()
        trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="matching_and_verification",
                agent="MatchingAgent",
                event_type=AgentEventType.stage_start,
                input_summary=f"Needs: {[n.category.value for n in needs_assessment.needs]}",
            )
        )

        matches, verified_recs, v_results = self.matching_agent.match_and_verify(
            profile, needs_assessment, kb
        )
        s3_latency = (time.time() - s3_start) * 1000

        trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="matching_and_verification",
                agent="MatchingAgent",
                event_type=AgentEventType.stage_complete,
                output_summary=f"Retrieved and verified {len(verified_recs)} recommendations: {[f'{r.resource_id}({r.status.value})' for r in verified_recs]}",
                latency_ms=s3_latency,
            )
        )

        # --- Stage 4: Action Planning ---
        s4_start = time.time()
        trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="action_planning",
                agent="ActionPlanningAgent",
                event_type=AgentEventType.stage_start,
                input_summary=f"Verified recommendations count: {len(verified_recs)}",
            )
        )

        action_plan = self.action_planner.plan(profile, needs_assessment, verified_recs)
        s4_latency = (time.time() - s4_start) * 1000

        trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="action_planning",
                agent="ActionPlanningAgent",
                event_type=AgentEventType.stage_complete,
                output_summary=f"Generated action plan with {len(action_plan.actions)} sequential steps",
                latency_ms=s4_latency,
            )
        )

        # --- Stage 5: Quality & Safety Check ---
        s5_start = time.time()
        trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="quality_check",
                agent="QualityAgent",
                event_type=AgentEventType.stage_start,
                input_summary="Auditing recommendations for evidence backing and safety",
            )
        )

        quality_report = self.quality_agent.check(profile, verified_recs)
        s5_latency = (time.time() - s5_start) * 1000

        trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="quality_check",
                agent="QualityAgent",
                event_type=AgentEventType.stage_complete,
                output_summary=f"Quality check passed={quality_report.passed}, safe_to_present={quality_report.safe_to_present}, issues={len(quality_report.issues)}",
                latency_ms=s5_latency,
            )
        )

        # --- Stage 6: Human Review Checkpoint ---
        human_review = HumanReview(
            case_id=case_id,
            decision=HumanReviewDecision.pending,
            follow_up_required=bool(profile.missing_information or profile.contradictions),
        )

        trajectory.append(
            AgentEvent(
                case_id=case_id,
                stage="human_review",
                agent="HumanReviewGate",
                event_type=AgentEventType.human_checkpoint,
                output_summary="Case prepared and awaiting frontline human caseworker review.",
            )
        )

        total_latency = (time.time() - pipeline_start) * 1000
        logger.info(f"CaseOrchestrator completed case {case_id} in {total_latency:.1f}ms")

        # Determine workflow state
        if not quality_report.passed:
            workflow_state = CaseWorkflowState.needs_human_attention
        elif profile.missing_information or profile.contradictions:
            workflow_state = CaseWorkflowState.follow_up_required
        else:
            workflow_state = CaseWorkflowState.action_plan_ready

        return CaseState(
            case_id=case_id,
            profile=profile,
            needs_assessment=needs_assessment,
            resource_matches=matches,
            verified_recommendations=verified_recs,
            action_plan=action_plan,
            quality_report=quality_report,
            human_review=human_review,
            workflow_state=workflow_state,
            trajectory=trajectory,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
