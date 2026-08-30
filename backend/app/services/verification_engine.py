"""
Deterministic Requirement Verification Engine
==============================================

Evaluates structured case facts against approved resource requirements
using strict comparison rules.

Core design invariants enforced here:
- UNKNOWN != SATISFIED. Missing facts or unknown status NEVER promote to satisfied.
- Contradictions are explicitly detected and flagged as 'conflict'.
- Geographic scope is validated.
- Every satisfied requirement generates a traceable EvidenceItem.
- Categorizes overall MatchStatus strictly based on requirement outcomes.
"""

from __future__ import annotations

import logging
from typing import Any

from app.schemas.domain import (
    CaseProfile,
    EvidenceItem,
    FactStatus,
    MatchStatus,
    RequirementEvaluation,
    RequirementImportance,
    RequirementOperator,
    RequirementStatus,
    Resource,
    VerificationResult,
    VerificationWarning,
    VerifiedRecommendation,
)

logger = logging.getLogger("migrantaid")


class VerificationEngine:
    """Deterministic rule-based requirement evaluator."""

    @staticmethod
    def _normalize_value(val: Any) -> Any:
        """Normalize string values for safe, case-insensitive comparison."""
        if isinstance(val, str):
            return val.strip().lower()
        return val

    @classmethod
    def evaluate_operator(
        cls,
        operator: RequirementOperator,
        case_val: Any,
        expected_val: Any,
    ) -> bool:
        """Evaluate a single operator condition safely without arbitrary execution."""
        norm_case = cls._normalize_value(case_val)
        norm_exp = cls._normalize_value(expected_val)

        # Handle boolean strings e.g. "true" == True
        if isinstance(expected_val, bool) and isinstance(case_val, str):
            norm_case = norm_case in ("true", "yes", "1")
        elif isinstance(case_val, bool) and isinstance(expected_val, str):
            norm_exp = norm_exp in ("true", "yes", "1")

        try:
            if operator == RequirementOperator.equals:
                return norm_case == norm_exp

            elif operator == RequirementOperator.not_equals:
                return norm_case != norm_exp

            elif operator == RequirementOperator.contains:
                if isinstance(norm_case, (list, set, tuple)):
                    return norm_exp in [cls._normalize_value(x) for x in norm_case]
                elif isinstance(norm_case, str) and isinstance(norm_exp, str):
                    return norm_exp in norm_case or norm_case in norm_exp
                return False

            elif operator == RequirementOperator.in_:
                if isinstance(expected_val, (list, set, tuple)):
                    return norm_case in [cls._normalize_value(x) for x in expected_val]
                elif isinstance(norm_exp, str) and isinstance(norm_case, str):
                    return norm_case in norm_exp
                return False

            elif operator == RequirementOperator.not_in:
                if isinstance(expected_val, (list, set, tuple)):
                    return norm_case not in [cls._normalize_value(x) for x in expected_val]
                elif isinstance(norm_exp, str) and isinstance(norm_case, str):
                    return norm_case not in norm_exp
                return True

            elif operator == RequirementOperator.greater_than:
                return float(case_val) > float(expected_val)

            elif operator == RequirementOperator.less_than:
                return float(case_val) < float(expected_val)

            elif operator == RequirementOperator.greater_or_equal:
                return float(case_val) >= float(expected_val)

            elif operator == RequirementOperator.less_or_equal:
                return float(case_val) <= float(expected_val)

            elif operator == RequirementOperator.exists:
                return case_val is not None and bool(case_val)

        except (ValueError, TypeError) as e:
            logger.debug(f"Operator evaluation failed for {operator} on ({case_val}, {expected_val}): {e}")
            return False

        return False

    def evaluate_resource(
        self,
        profile: CaseProfile,
        resource: Resource,
    ) -> tuple[MatchStatus, list[RequirementEvaluation], list[EvidenceItem], list[str], list[VerificationWarning]]:
        """
        Evaluate a case profile against a single resource.

        Returns:
            (match_status, evaluations, evidence_items, missing_info_fields, warnings)
        """
        evaluations: list[RequirementEvaluation] = []
        evidence_items: list[EvidenceItem] = []
        missing_info_fields: list[str] = []
        warnings: list[VerificationWarning] = []

        has_conflict = False
        has_critical_fail = False
        has_critical_unknown = False
        has_critical_satisfied = False

        # 1. Check geographic scope if location is known
        loc_fact = profile.get_fact("location") or profile.get_fact("city")
        if loc_fact and loc_fact.value:
            case_loc = self._normalize_value(loc_fact.value)
            res_cities = [self._normalize_value(c) for c in resource.geography.cities]
            if res_cities and case_loc not in res_cities:
                warnings.append(
                    VerificationWarning(
                        code="GEOGRAPHY_MISMATCH",
                        message=f"Case location '{loc_fact.value}' does not match resource cities {resource.geography.cities}",
                        severity="warning",
                    )
                )

        # 2. Check if case has unresolved contradictions affecting this domain
        if profile.contradictions:
            for contradiction in profile.contradictions:
                warnings.append(
                    VerificationWarning(
                        code="CONTRADICTION_PRESENT",
                        message=f"Unresolved contradiction in case: {contradiction.description}",
                        severity="warning",
                    )
                )

        # 3. Evaluate each resource requirement
        for req in resource.requirements:
            fact = profile.get_fact(req.field)

            # Fact is absent or unknown -> UNKNOWN
            if fact is None or fact.status == FactStatus.unknown or fact.value is None:
                evaluations.append(
                    RequirementEvaluation(
                        requirement_id=req.requirement_id,
                        field=req.field,
                        status=RequirementStatus.unknown,
                        case_fact_value=None,
                        required_value=req.value,
                        evidence_text=f"No evidence available for requirement '{req.field}' (operator: {req.operator.value} {req.value})",
                    )
                )
                missing_info_fields.append(req.field)
                if req.importance == RequirementImportance.critical:
                    has_critical_unknown = True
                continue

            # Fact is conflicting -> CONFLICT
            if fact.status == FactStatus.conflicting:
                evaluations.append(
                    RequirementEvaluation(
                        requirement_id=req.requirement_id,
                        field=req.field,
                        status=RequirementStatus.conflict,
                        case_fact_value=fact.value,
                        required_value=req.value,
                        evidence_text=f"Conflicting facts detected for requirement '{req.field}'",
                    )
                )
                has_conflict = True
                continue

            # Evaluate operator
            is_satisfied = self.evaluate_operator(req.operator, fact.value, req.value)

            if is_satisfied:
                evaluations.append(
                    RequirementEvaluation(
                        requirement_id=req.requirement_id,
                        field=req.field,
                        status=RequirementStatus.satisfied,
                        case_fact_value=fact.value,
                        required_value=req.value,
                        evidence_text=f"Fact '{req.field}'={fact.value} satisfies requirement ({req.operator.value} {req.value})",
                    )
                )
                evidence_items.append(
                    EvidenceItem(
                        case_fact_id=req.field,
                        requirement_id=req.requirement_id,
                        result=RequirementStatus.satisfied,
                        evidence=f"Case fact '{req.field}' has value '{fact.value}', which satisfies requirement {req.requirement_id}",
                        source=fact.source,
                    )
                )
                if req.importance == RequirementImportance.critical:
                    has_critical_satisfied = True
            else:
                evaluations.append(
                    RequirementEvaluation(
                        requirement_id=req.requirement_id,
                        field=req.field,
                        status=RequirementStatus.not_satisfied,
                        case_fact_value=fact.value,
                        required_value=req.value,
                        evidence_text=f"Fact '{req.field}'={fact.value} does NOT satisfy requirement ({req.operator.value} {req.value})",
                    )
                )
                if req.importance == RequirementImportance.critical:
                    has_critical_fail = True

        # 4. Classify overall MatchStatus
        if has_conflict or (profile.contradictions and has_critical_satisfied):
            final_status = MatchStatus.conflict_detected
        elif has_critical_fail:
            final_status = MatchStatus.not_supported_by_available_evidence
        elif has_critical_unknown:
            final_status = MatchStatus.insufficient_information
        elif has_critical_satisfied or not resource.requirements:
            # All critical satisfied; check if any optional are unknown
            if missing_info_fields:
                final_status = MatchStatus.potential_match
            else:
                final_status = MatchStatus.strong_match
        else:
            final_status = MatchStatus.no_verified_match

        return final_status, evaluations, evidence_items, missing_info_fields, warnings

    def verify_recommendation(
        self,
        profile: CaseProfile,
        resource: Resource,
    ) -> tuple[VerificationResult, VerifiedRecommendation]:
        """Produce full VerificationResult and VerifiedRecommendation objects."""
        status, evals, evidence, missing, warnings = self.evaluate_resource(profile, resource)

        passed = status in (MatchStatus.strong_match, MatchStatus.potential_match)
        unsupported = []
        if status == MatchStatus.not_supported_by_available_evidence:
            unsupported.append(f"Resource {resource.resource_id} requirements not met by case facts.")

        v_result = VerificationResult(
            resource_id=resource.resource_id,
            passed=passed,
            final_status=status,
            warnings=warnings,
            unsupported_claims=unsupported,
            unresolved_requirements=missing,
            contradictions_detected=[c.description for c in profile.contradictions],
            human_review_required=True,
        )

        rec = VerifiedRecommendation(
            resource_id=resource.resource_id,
            resource_name=resource.name,
            status=status,
            evidence=evidence,
            requirement_evaluations=evals,
            missing_information=missing,
            verification_warnings=warnings,
            human_review_required=True,
            source_id=resource.source_id,
            dataset_version=resource.dataset_version,
        )

        return v_result, rec
