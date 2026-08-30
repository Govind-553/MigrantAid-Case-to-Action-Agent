"""
Evaluation Service and VARR Scorer
==================================

Implements the 6-dimension VARR scoring rubric and failure categorization
defined in EVALUATION_DATASET_SPEC.md.

Dimensions:
1. Primary need identified correctly (20 pts)
2. Appropriate resource identified (20 pts)
3. Evidence supports recommendation (20 pts)
4. Critical missing information identified (15 pts)
5. No unsupported eligibility claim (15 pts)
6. Actionable next step (10 pts)

Success Threshold:
- Total score >= 80
- Evidence score >= 15/20
- Unsupported-claim score = 15/15
- Actionable next step present
"""

from __future__ import annotations

import logging
from typing import Any

from app.schemas.domain import (
    EvaluationDimensions,
    EvaluationResult,
    FailureCategory,
)
from app.services.evaluation_loader import EvaluationCase

logger = logging.getLogger("migrantaid")


class ScoredCaseEvaluation:
    """Wrapper holding a case, system output, dimensions, and computed result."""

    def __init__(
        self,
        case: EvaluationCase,
        output: dict[str, Any],
        system_name: str = "baseline",
    ):
        self.case = case
        self.output = output
        self.system_name = system_name
        self.dimensions = EvaluationDimensions()
        self.failure_categories: list[FailureCategory] = []
        self.scoring_notes: list[str] = []

    def evaluate(self) -> EvaluationResult:
        """Run all dimension evaluations and return an EvaluationResult."""
        self._score_primary_need()
        self._score_resource_identification()
        self._score_evidence_support()
        self._score_missing_information()
        self._score_unsupported_claim()
        self._score_actionable_next_step()

        total_score = self.dimensions.total

        # Success threshold check:
        # total >= 80, evidence >= 15, unsupported == 15, actionable_step > 0
        is_successful = (
            total_score >= 80
            and self.dimensions.evidence >= 15
            and self.dimensions.unsupported_claim == 15
            and self.dimensions.actionable_next_step >= 5
        )

        latency_ms = float(self.output.get("latency_ms", 0.0))

        return EvaluationResult(
            case_id=self.case.case_id,
            system=self.system_name,
            score=total_score,
            successful=is_successful,
            dimensions=self.dimensions,
            failure_categories=self.failure_categories,
            latency_ms=latency_ms,
            model_calls=1,
            notes="; ".join(self.scoring_notes) if self.scoring_notes else None,
        )

    def _score_primary_need(self):
        """Dimension 1: Primary need identified correctly (max 20 pts)."""
        pred_need = str(self.output.get("primary_need", "")).lower().strip()
        expected_needs = [n.lower().strip() for n in self.case.known_needs]

        if not expected_needs:
            # Case has no specific expected need (rare/fallback)
            self.dimensions.primary_need = 20
            return

        if pred_need in expected_needs:
            # Full match
            self.dimensions.primary_need = 20
        elif pred_need != "other" and any(n in pred_need or pred_need in n for n in expected_needs):
            # Partial / sub-category match
            self.dimensions.primary_need = 10
            self.failure_categories.append(FailureCategory.NEED_MISS)
            self.scoring_notes.append(f"Partial primary need match: predicted '{pred_need}', expected one of {expected_needs}")
        else:
            self.dimensions.primary_need = 0
            self.failure_categories.append(FailureCategory.NEED_MISS)
            self.scoring_notes.append(f"Primary need miss: predicted '{pred_need}', expected one of {expected_needs}")

    def _score_resource_identification(self):
        """Dimension 2: Appropriate resource identified (max 20 pts)."""
        raw_pred = self.output.get("recommended_resource_ids", [])
        if isinstance(raw_pred, str):
            pred_rids = [raw_pred] if raw_pred else []
        elif isinstance(raw_pred, list):
            pred_rids = [str(r).strip() for r in raw_pred if str(r).strip()]
        else:
            pred_rids = []

        expected_rids = set(self.case.expected_resource_ids)
        expected_status = self.case.expected_resource_status.lower()

        # Handle cases where no match or insufficient information is expected
        if not expected_rids or "insufficient_information" in expected_status or "no_match" in expected_status:
            if not pred_rids or "insufficient" in str(self.output.get("eligibility_assessment", "")).lower():
                self.dimensions.resource = 20
            elif set(pred_rids) == expected_rids:
                # Identified the relevant resource to investigate
                self.dimensions.resource = 15
            else:
                self.dimensions.resource = 5
                self.failure_categories.append(FailureCategory.RETRIEVAL_MISS)
                self.scoring_notes.append(f"Over-recommended resources for insufficient-info case: {pred_rids}")
            return

        # Case expects specific resources
        matched = set(pred_rids).intersection(expected_rids)
        if set(pred_rids) == expected_rids:
            self.dimensions.resource = 20
        elif matched:
            ratio = len(matched) / len(expected_rids)
            self.dimensions.resource = int(20 * ratio)
            self.failure_categories.append(FailureCategory.RETRIEVAL_MISS)
            self.scoring_notes.append(f"Partial resource match: identified {list(matched)} of {list(expected_rids)}")
        else:
            self.dimensions.resource = 0
            self.failure_categories.append(FailureCategory.RETRIEVAL_MISS)
            self.scoring_notes.append(f"Resource miss: identified {pred_rids}, expected {list(expected_rids)}")

    def _score_evidence_support(self):
        """Dimension 3: Evidence supports recommendation (max 20 pts)."""
        evidence_text = str(self.output.get("evidence_text", "") or self.output.get("eligibility_assessment", ""))
        pred_rids = self.output.get("recommended_resource_ids", [])
        if not isinstance(pred_rids, list):
            pred_rids = [pred_rids] if pred_rids else []

        if not pred_rids:
            # If no resource was recommended and that was correct
            if not self.case.expected_resource_ids or "insufficient" in self.case.expected_resource_status:
                self.dimensions.evidence = 20
            else:
                self.dimensions.evidence = 10
            return

        # Check if evidence mentions actual facts or just gives generic statements
        has_specific_evidence = any(
            str(val).lower() in evidence_text.lower()
            for key, val in self.case.known_facts.items()
            if isinstance(val, (str, int)) and len(str(val)) > 2
        )

        # Baseline outputs often provide a generic "Beneficiary appears likely eligible" without specific fact mapping
        if "appears likely eligible" in evidence_text and not has_specific_evidence:
            # Naive unverified statement
            self.dimensions.evidence = 5
            self.failure_categories.append(FailureCategory.EVIDENCE_MISS)
            self.scoring_notes.append("Generic eligibility claim lacking structured evidence mapping")
        elif has_specific_evidence:
            self.dimensions.evidence = 20
        elif len(evidence_text) > 30:
            self.dimensions.evidence = 15
        else:
            self.dimensions.evidence = 0
            self.failure_categories.append(FailureCategory.EVIDENCE_MISS)
            self.scoring_notes.append("No traceable evidence provided for recommendation")

    def _score_missing_information(self):
        """Dimension 4: Critical missing information identified (max 15 pts)."""
        expected_missing = set(self.case.critical_missing_information)
        pred_missing = set(self.output.get("missing_information", []))

        if not expected_missing:
            # Case has no missing information
            if not pred_missing:
                self.dimensions.missing_information = 15
            else:
                # Raised unnecessary missing info questions
                self.dimensions.missing_information = 10
            return

        # Case expects specific missing info to be caught
        matched = set()
        for p in pred_missing:
            p_clean = p.lower().replace("_", " ")
            p_words = set(p_clean.split())
            for exp in expected_missing:
                exp_clean = exp.lower().replace("_", " ")
                exp_words = set(exp_clean.split())
                overlap = exp_words.intersection(p_words) - {"or", "and", "the", "of", "in", "to", "a", "for", "is"}
                if exp_clean in p_clean or p_clean in exp_clean or len(overlap) >= 2 or (len(exp_words) == 1 and bool(overlap)) or ("document" in exp_clean and "document" in p_clean):
                    matched.add(exp)

        if matched == expected_missing:
            self.dimensions.missing_information = 15
        elif matched:
            self.dimensions.missing_information = int(15 * (len(matched) / len(expected_missing)))
            self.failure_categories.append(FailureCategory.MISSING_INFO_MISS)
            self.scoring_notes.append(f"Partially identified missing info: {list(matched)} of {list(expected_missing)}")
        else:
            self.dimensions.missing_information = 0
            self.failure_categories.append(FailureCategory.MISSING_INFO_MISS)
            self.scoring_notes.append(f"Failed to identify critical missing info: expected {list(expected_missing)}")

    def _score_unsupported_claim(self):
        """Dimension 5: No unsupported eligibility claim (max 15 pts)."""
        # Critical rule: Never convert unknown eligibility into eligible
        # If the case has critical missing info or contradictions, declaring unconditional eligibility is an unsupported claim
        eligibility_text = str(self.output.get("eligibility_assessment", "")).lower()

        has_critical_missing = bool(self.case.critical_missing_information)
        has_contradictions = bool(self.case.contradictions)

        claimed_eligible = "likely eligible" in eligibility_text or "is eligible" in eligibility_text or "qualifies" in eligibility_text

        if (has_critical_missing or has_contradictions) and claimed_eligible:
            # Declared eligibility despite missing information or contradictions!
            self.dimensions.unsupported_claim = 0
            self.failure_categories.append(FailureCategory.UNSUPPORTED_CLAIM)
            if has_contradictions:
                self.failure_categories.append(FailureCategory.CONTRADICTION_MISS)
            self.scoring_notes.append("Unsupported eligibility claim: declared eligible despite unresolved missing info/contradictions")
        elif "insufficient" in eligibility_text or "requires confirmation" in eligibility_text or "unknown" in eligibility_text or not claimed_eligible:
            self.dimensions.unsupported_claim = 15
        else:
            self.dimensions.unsupported_claim = 15

    def _score_actionable_next_step(self):
        """Dimension 6: Actionable next step (max 10 pts)."""
        next_step = str(self.output.get("next_step", "")).strip()

        if not next_step:
            self.dimensions.actionable_next_step = 0
            self.failure_categories.append(FailureCategory.ACTION_PLAN_MISS)
            self.scoring_notes.append("Missing actionable next step")
            return

        # Check if next step is meaningful and specific (>= 15 chars)
        if len(next_step) >= 15:
            # Bonus check: if missing info exists, does next step ask for it?
            if self.case.critical_missing_information and ("ask" in next_step.lower() or "confirm" in next_step.lower() or "verify" in next_step.lower()):
                self.dimensions.actionable_next_step = 10
            elif not self.case.critical_missing_information:
                self.dimensions.actionable_next_step = 10
            else:
                self.dimensions.actionable_next_step = 6
        else:
            self.dimensions.actionable_next_step = 4
            self.scoring_notes.append(f"Vague or too brief next step: '{next_step}'")


class EvaluatorService:
    """Service to evaluate a complete set of outputs against the evaluation dataset."""

    def evaluate_case(
        self,
        case: EvaluationCase,
        output: dict[str, Any],
        system_name: str = "baseline"
    ) -> EvaluationResult:
        """Evaluate a single case output."""
        evaluator = ScoredCaseEvaluation(case, output, system_name=system_name)
        return evaluator.evaluate()

    def evaluate_all(
        self,
        cases: list[EvaluationCase],
        outputs: list[dict[str, Any]],
        system_name: str = "baseline"
    ) -> list[EvaluationResult]:
        """Evaluate outputs for all cases, matched by case_id."""
        outputs_by_id = {o["case_id"]: o for o in outputs if "case_id" in o}
        results = []

        for case in cases:
            out = outputs_by_id.get(case.case_id, {})
            if not out:
                logger.warning(f"No output found for case_id {case.case_id} during evaluation")
            res = self.evaluate_case(case, out, system_name=system_name)
            results.append(res)

        return results

    def compute_summary_metrics(self, results: list[EvaluationResult]) -> dict[str, Any]:
        """Compute aggregate benchmark metrics including VARR and secondary metrics."""
        if not results:
            return {"varr": 0.0, "total_cases": 0, "successful_cases": 0}

        total = len(results)
        successful = sum(1 for r in results if r.successful)
        varr = (successful / total) * 100.0

        avg_score = sum(r.score for r in results) / total
        avg_primary_need = sum(r.dimensions.primary_need for r in results) / total
        avg_resource = sum(r.dimensions.resource for r in results) / total
        avg_evidence = sum(r.dimensions.evidence for r in results) / total
        avg_missing_info = sum(r.dimensions.missing_information for r in results) / total
        avg_unsupported_claim = sum(r.dimensions.unsupported_claim for r in results) / total
        avg_actionable_step = sum(r.dimensions.actionable_next_step for r in results) / total
        avg_latency = sum(r.latency_ms for r in results) / total

        # Failure category counts
        failure_counts: dict[str, int] = {}
        for r in results:
            for cat in r.failure_categories:
                cat_str = cat.value if hasattr(cat, "value") else str(cat)
                failure_counts[cat_str] = failure_counts.get(cat_str, 0) + 1

        return {
            "system": results[0].system if results else "unknown",
            "total_cases": total,
            "successful_cases": successful,
            "varr_percentage": round(varr, 1),
            "avg_total_score": round(avg_score, 1),
            "avg_dimension_scores": {
                "primary_need": round(avg_primary_need, 1),
                "resource": round(avg_resource, 1),
                "evidence": round(avg_evidence, 1),
                "missing_information": round(avg_missing_info, 1),
                "unsupported_claim": round(avg_unsupported_claim, 1),
                "actionable_next_step": round(avg_actionable_step, 1),
            },
            "failure_category_distribution": failure_counts,
            "avg_latency_ms": round(avg_latency, 1),
        }
