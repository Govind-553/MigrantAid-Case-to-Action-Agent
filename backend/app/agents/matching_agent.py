"""
Resource Matching & Verification Agent
======================================

Retrieves approved resources from the Resource Knowledge Base matching
assessed needs, and verifies eligibility using the deterministic VerificationEngine.
"""

from __future__ import annotations

import logging

from app.schemas.domain import (
    CaseProfile,
    MatchStatus,
    NeedsAssessment,
    ResourceMatch,
    VerificationResult,
    VerifiedRecommendation,
)
from app.services.resource_kb import ResourceKB
from app.services.verification_engine import VerificationEngine

logger = logging.getLogger("migrantaid")


class MatchingAgent:
    """Agent responsible for candidate resource retrieval and verification integration."""

    def __init__(self):
        self.verifier = VerificationEngine()

    def match_and_verify(
        self,
        profile: CaseProfile,
        assessment: NeedsAssessment,
        kb: ResourceKB,
    ) -> tuple[list[ResourceMatch], list[VerifiedRecommendation], list[VerificationResult]]:
        """
        Retrieve candidate resources for all identified needs and evaluate them against case facts.

        Returns:
            (resource_matches, verified_recommendations, verification_results)
        """
        logger.info(f"MatchingAgent running for case: {profile.case_id}")
        matches: list[ResourceMatch] = []
        verified_recs: list[VerifiedRecommendation] = []
        verification_results: list[VerificationResult] = []

        seen_resource_ids: set[str] = set()

        for need in assessment.needs:
            # 1. Retrieve candidates by category
            candidates = kb.get_resources_by_category(need.category.value)

            for resource in candidates:
                if resource.resource_id in seen_resource_ids:
                    continue
                seen_resource_ids.add(resource.resource_id)

                # 2. Run deterministic verification engine
                v_result, v_rec = self.verifier.verify_recommendation(profile, resource)

                # 3. Compute retrieval relevance score (0.0 to 1.0)
                relevance_score = 0.9 if need.priority.value in ("immediate", "high") else 0.7

                # 4. Build ResourceMatch
                status, evals, evidence, missing, warnings = self.verifier.evaluate_resource(profile, resource)
                match = ResourceMatch(
                    resource_id=resource.resource_id,
                    resource_name=resource.name,
                    status=status,
                    requirement_evaluations=evals,
                    missing_information=missing,
                    supporting_evidence=evidence,
                    retrieval_reasons=[f"Category match: {need.category.value}", f"Priority: {need.priority.value}"],
                    source_id=resource.source_id,
                    human_review_required=True,
                    retrieval_score=relevance_score,
                )

                matches.append(match)
                verified_recs.append(v_rec)
                verification_results.append(v_result)

        # Sort recommendations: strong_match -> potential_match -> insufficient_information -> others
        status_priority = {
            MatchStatus.strong_match: 0,
            MatchStatus.potential_match: 1,
            MatchStatus.insufficient_information: 2,
            MatchStatus.conflict_detected: 3,
            MatchStatus.not_supported_by_available_evidence: 4,
            MatchStatus.no_verified_match: 5,
        }

        verified_recs.sort(key=lambda r: status_priority.get(r.status, 99))

        return matches, verified_recs, verification_results
