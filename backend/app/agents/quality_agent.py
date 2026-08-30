"""
Quality & Safety Guardrails Agent
=================================

Performs pre-presentation verification to ensure no unsupported claims,
unverified referrals, or missing evidence escape to the frontline worker.
"""

from __future__ import annotations

import logging

from app.schemas.domain import (
    CaseProfile,
    MatchStatus,
    QualityIssue,
    QualityReport,
    VerifiedRecommendation,
)

logger = logging.getLogger("migrantaid")


class QualityAgent:
    """Safety guardrail agent enforcing evidence completeness and human review gates."""

    def check(
        self,
        profile: CaseProfile,
        recommendations: list[VerifiedRecommendation],
    ) -> QualityReport:
        """Run safety audits on case state before presenting to frontline caseworkers."""
        logger.info(f"QualityAgent running safety check on case: {profile.case_id}")
        issues: list[QualityIssue] = []
        unsupported_claims_detected = False
        missing_evidence_flagged = False

        # 1. Audit Contradictions
        if profile.contradictions:
            for c in profile.contradictions:
                issues.append(
                    QualityIssue(
                        code="UNRESOLVED_CONTRADICTION",
                        message=f"Case narrative contains an unresolved contradiction: {c.description}",
                        severity="warning",
                    )
                )

        # 2. Audit Recommendations for Evidence Backing
        for rec in recommendations:
            if rec.status == MatchStatus.strong_match and not rec.evidence:
                unsupported_claims_detected = True
                issues.append(
                    QualityIssue(
                        code="UNSUPPORTED_STRONG_MATCH",
                        message=f"Recommendation {rec.resource_id} marked as strong_match without evidence",
                        severity="error",
                        affected_resource_id=rec.resource_id,
                    )
                )

            if rec.status == MatchStatus.insufficient_information and rec.missing_information:
                missing_evidence_flagged = True
                issues.append(
                    QualityIssue(
                        code="INCOMPLETE_INFORMATION_FLAGGED",
                        message=f"Resource {rec.resource_id} requires confirmation of {rec.missing_information}",
                        severity="info",
                        affected_resource_id=rec.resource_id,
                    )
                )

            if rec.status == MatchStatus.conflict_detected:
                issues.append(
                    QualityIssue(
                        code="RESOURCE_CONFLICT_DETECTED",
                        message=f"Resource {rec.resource_id} cannot be recommended due to conflicting case facts",
                        severity="warning",
                        affected_resource_id=rec.resource_id,
                    )
                )

        # Determine pass/fail: errors fail the check; warnings are recorded for human attention
        has_errors = any(i.severity == "error" for i in issues)
        passed = not has_errors
        safe_to_present = passed  # If no critical errors, safe for human caseworker review

        return QualityReport(
            case_id=profile.case_id,
            passed=passed,
            issues=issues,
            unsupported_claims_detected=unsupported_claims_detected,
            missing_evidence_flagged=missing_evidence_flagged,
            human_review_enforced=True,
            safe_to_present=safe_to_present,
        )
