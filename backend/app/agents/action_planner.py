"""
Action Planning Agent
=====================

Generates a prioritized, sequential, grounded ActionPlan for the caseworker
and beneficiary based on verified recommendations, missing facts, and contradictions.
"""

from __future__ import annotations

import logging

from app.schemas.domain import (
    ActionItem,
    ActionPlan,
    ActionPriority,
    CaseProfile,
    MatchStatus,
    NeedsAssessment,
    VerifiedRecommendation,
)

logger = logging.getLogger("migrantaid")


class ActionPlanningAgent:
    """Agent responsible for preparing step-by-step caseworker action plans."""

    def plan(
        self,
        profile: CaseProfile,
        assessment: NeedsAssessment,
        recommendations: list[VerifiedRecommendation],
    ) -> ActionPlan:
        """Construct a sequential ActionPlan with prioritized steps."""
        logger.info(f"ActionPlanningAgent generating plan for case: {profile.case_id}")
        actions: list[ActionItem] = []
        step_counter = 1

        # 1. Immediate step for contradictions
        if profile.contradictions:
            for c in profile.contradictions:
                actions.append(
                    ActionItem(
                        step=step_counter,
                        priority=ActionPriority.critical,
                        action=f"Clarify conflicting information with beneficiary: {c.description}",
                        reason="Unresolved contradictions prevent safe resource referral.",
                        responsible_role="caseworker",
                        unresolved_uncertainty=c.description,
                    )
                )
                step_counter += 1

        # 2. Critical steps for missing information
        all_missing: set[str] = set(profile.missing_information)
        for r in recommendations:
            if r.status == MatchStatus.insufficient_information:
                all_missing.update(r.missing_information)

        if all_missing:
            for m in sorted(all_missing):
                field_label = m.replace("_", " ")
                actions.append(
                    ActionItem(
                        step=step_counter,
                        priority=ActionPriority.high,
                        action=f"Confirm beneficiary's {field_label}",
                        reason=f"Field '{field_label}' is required to evaluate eligibility for pending support resources.",
                        responsible_role="caseworker",
                        unresolved_uncertainty=f"Unconfirmed {field_label}",
                    )
                )
                step_counter += 1

        # 3. Steps for verified strong or potential matches
        verified_matches = [
            r for r in recommendations if r.status in (MatchStatus.strong_match, MatchStatus.potential_match)
        ]

        if verified_matches:
            for rec in verified_matches:
                actions.append(
                    ActionItem(
                        step=step_counter,
                        priority=ActionPriority.high if rec.status == MatchStatus.strong_match else ActionPriority.medium,
                        action=f"Review verified resource '{rec.resource_name or rec.resource_id}' with beneficiary",
                        reason=f"Evidence satisfies core prerequisites for {rec.resource_id}.",
                        prerequisite=f"Step {step_counter - 1}" if step_counter > 1 else None,
                        responsible_role="caseworker",
                        evidence_reference=rec.resource_id,
                    )
                )
                step_counter += 1

                actions.append(
                    ActionItem(
                        step=step_counter,
                        priority=ActionPriority.medium,
                        action=f"Assist beneficiary in contacting {rec.resource_name or rec.resource_id} and submitting application",
                        reason="Initiate official service intake with the service provider.",
                        prerequisite=f"Step {step_counter - 1}",
                        responsible_role="caseworker_and_beneficiary",
                        evidence_reference=rec.resource_id,
                    )
                )
                step_counter += 1

        # 4. Fallback if no specific steps could be generated
        if not actions:
            actions.append(
                ActionItem(
                    step=1,
                    priority=ActionPriority.medium,
                    action="Conduct detailed intake follow-up interview with beneficiary",
                    reason="Gather additional case context to identify suitable assistance programmes.",
                    responsible_role="caseworker",
                )
            )

        return ActionPlan(
            case_id=profile.case_id,
            actions=actions,
            plan_notes=f"Action plan containing {len(actions)} sequential step(s).",
        )
