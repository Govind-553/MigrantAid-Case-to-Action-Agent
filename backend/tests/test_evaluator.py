"""
Phase 5: Evaluation Service Unit and Integration Tests
=====================================================

Tests for the 6-dimension VARR scorer:
- scoring each dimension accurately
- checking the success threshold rule
- failure category attribution
- summary metrics computation
- integration with baseline outputs
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.schemas.domain import (
    EvaluationDimensions,
    EvaluationResult,
    FailureCategory,
)
from app.services.evaluation_loader import EvaluationCase, load_evaluation_cases
from app.services.evaluator import EvaluatorService, ScoredCaseEvaluation
from app.services.resource_kb import load_resource_kb

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESOURCES_PATH = DATA_DIR / "resources.json"
SOURCES_PATH = DATA_DIR / "sources.json"
EVAL_CASES_PATH = DATA_DIR / "evaluation_cases.json"
BASELINE_RESULTS_PATH = PROJECT_ROOT / "baseline" / "baseline_results.json"


@pytest.fixture(scope="module")
def resource_kb():
    return load_resource_kb(RESOURCES_PATH, SOURCES_PATH)


@pytest.fixture(scope="module")
def eval_dataset(resource_kb):
    valid_ids = {r.resource_id for r in resource_kb.resources}
    return load_evaluation_cases(EVAL_CASES_PATH, valid_resource_ids=valid_ids)


@pytest.fixture
def evaluator_service():
    return EvaluatorService()


class TestDimensionScoring:
    def test_primary_need_exact_match(self):
        case = EvaluationCase(
            case_id="TEST-001",
            title="Test",
            narrative="Worker lost job.",
            known_needs=["employment", "basic_support"],
        )
        output = {"case_id": "TEST-001", "primary_need": "employment"}
        scorer = ScoredCaseEvaluation(case, output)
        scorer._score_primary_need()
        assert scorer.dimensions.primary_need == 20

    def test_primary_need_miss(self):
        case = EvaluationCase(
            case_id="TEST-001",
            title="Test",
            narrative="Worker lost job.",
            known_needs=["employment"],
        )
        output = {"case_id": "TEST-001", "primary_need": "transport"}
        scorer = ScoredCaseEvaluation(case, output)
        scorer._score_primary_need()
        assert scorer.dimensions.primary_need == 0
        assert FailureCategory.NEED_MISS in scorer.failure_categories

    def test_resource_exact_match(self):
        case = EvaluationCase(
            case_id="TEST-001",
            title="Test",
            narrative="Worker needs employment.",
            expected_resource_ids=["RES-EMP-001"],
            expected_resource_status="potential_or_strong_match",
        )
        output = {"case_id": "TEST-001", "recommended_resource_ids": ["RES-EMP-001"]}
        scorer = ScoredCaseEvaluation(case, output)
        scorer._score_resource_identification()
        assert scorer.dimensions.resource == 20

    def test_resource_miss(self):
        case = EvaluationCase(
            case_id="TEST-001",
            title="Test",
            narrative="Worker needs employment.",
            expected_resource_ids=["RES-EMP-001"],
            expected_resource_status="potential_or_strong_match",
        )
        output = {"case_id": "TEST-001", "recommended_resource_ids": ["RES-HOUS-001"]}
        scorer = ScoredCaseEvaluation(case, output)
        scorer._score_resource_identification()
        assert scorer.dimensions.resource == 0
        assert FailureCategory.RETRIEVAL_MISS in scorer.failure_categories

    def test_unsupported_claim_penalized_on_missing_info(self):
        case = EvaluationCase(
            case_id="TEST-002",
            title="Missing income",
            narrative="Family needs housing help.",
            critical_missing_information=["current_household_income"],
        )
        output = {
            "case_id": "TEST-002",
            "eligibility_assessment": "Beneficiary appears likely eligible for housing support.",
        }
        scorer = ScoredCaseEvaluation(case, output)
        scorer._score_unsupported_claim()
        assert scorer.dimensions.unsupported_claim == 0
        assert FailureCategory.UNSUPPORTED_CLAIM in scorer.failure_categories

    def test_unsupported_claim_not_penalized_when_acknowledging_missing_info(self):
        case = EvaluationCase(
            case_id="TEST-002",
            title="Missing income",
            narrative="Family needs housing help.",
            critical_missing_information=["current_household_income"],
        )
        output = {
            "case_id": "TEST-002",
            "eligibility_assessment": "Insufficient information to determine eligibility; household income is unknown.",
        }
        scorer = ScoredCaseEvaluation(case, output)
        scorer._score_unsupported_claim()
        assert scorer.dimensions.unsupported_claim == 15

    def test_actionable_next_step_scored(self):
        case = EvaluationCase(case_id="TEST-001", title="Test", narrative="Worker needs help.")
        output = {"case_id": "TEST-001", "next_step": "Visit the local employment center to submit an application."}
        scorer = ScoredCaseEvaluation(case, output)
        scorer._score_actionable_next_step()
        assert scorer.dimensions.actionable_next_step == 10


class TestEvaluatorSummaryMetrics:
    def test_compute_summary_metrics(self, evaluator_service: EvaluatorService):
        dims_pass = EvaluationDimensions(primary_need=20, resource=20, evidence=20, missing_information=15, unsupported_claim=15, actionable_next_step=10)
        dims_fail = EvaluationDimensions(primary_need=10, resource=0, evidence=5, missing_information=0, unsupported_claim=0, actionable_next_step=5)

        res_pass = EvaluationResult(case_id="CASE-001", system="baseline", score=100, successful=True, dimensions=dims_pass)
        res_fail = EvaluationResult(case_id="CASE-002", system="baseline", score=20, successful=False, dimensions=dims_fail, failure_categories=[FailureCategory.RETRIEVAL_MISS, FailureCategory.UNSUPPORTED_CLAIM])

        summary = evaluator_service.compute_summary_metrics([res_pass, res_fail])

        assert summary["total_cases"] == 2
        assert summary["successful_cases"] == 1
        assert summary["varr_percentage"] == 50.0
        assert summary["avg_total_score"] == 60.0
        assert summary["failure_category_distribution"]["RETRIEVAL_MISS"] == 1
        assert summary["failure_category_distribution"]["UNSUPPORTED_CLAIM"] == 1


class TestBaselineEvaluationIntegration:
    def test_evaluate_baseline_results(self, evaluator_service: EvaluatorService, eval_dataset):
        assert BASELINE_RESULTS_PATH.exists(), "baseline_results.json should exist"
        with open(BASELINE_RESULTS_PATH, encoding="utf-8") as f:
            data = json.load(f)

        scores = evaluator_service.evaluate_all(eval_dataset.cases, data["results"], system_name="baseline")
        assert len(scores) == 20

        summary = evaluator_service.compute_summary_metrics(scores)
        assert summary["total_cases"] == 20
        assert isinstance(summary["varr_percentage"], float)
        assert summary["avg_total_score"] > 0
        # The baseline is expected to fail on several cases (e.g. missing info & contradiction cases)
        assert len(summary["failure_category_distribution"]) > 0
