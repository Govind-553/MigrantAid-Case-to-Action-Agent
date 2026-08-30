"""
Phase 6 & 7: Verification Engine Unit Tests
==========================================

Tests the deterministic VerificationEngine:
- all 10 comparison operators
- UNKNOWN != SATISFIED invariant enforcement
- conflict detection
- MatchStatus categorization
"""

from __future__ import annotations

import pytest

from app.schemas.domain import (
    CaseFact,
    CaseProfile,
    Contradiction,
    FactStatus,
    MatchStatus,
    NeedCategory,
    RequirementImportance,
    RequirementOperator,
    RequirementStatus,
    Resource,
    ResourceGeography,
    ResourceRequirement,
)
from app.services.verification_engine import VerificationEngine


@pytest.fixture
def engine():
    return VerificationEngine()


@pytest.fixture
def sample_resource():
    return Resource(
        resource_id="RES-TEST-001",
        name="Test Resource",
        category=NeedCategory.employment,
        geography=ResourceGeography(country="India", state="Maharashtra", cities=["Pune"]),
        requirements=[
            ResourceRequirement(
                requirement_id="REQ-1",
                field="employment_status",
                operator=RequirementOperator.equals,
                value="unemployed",
                importance=RequirementImportance.critical,
            ),
            ResourceRequirement(
                requirement_id="REQ-2",
                field="location",
                operator=RequirementOperator.equals,
                value="Pune",
                importance=RequirementImportance.critical,
            ),
        ],
        source_id="SRC-TEST",
    )


class TestOperatorEvaluations:
    def test_equals_operator(self, engine: VerificationEngine):
        assert engine.evaluate_operator(RequirementOperator.equals, "unemployed", "unemployed") is True
        assert engine.evaluate_operator(RequirementOperator.equals, "UNEMPLOYED", "unemployed") is True
        assert engine.evaluate_operator(RequirementOperator.equals, "employed", "unemployed") is False

    def test_not_equals_operator(self, engine: VerificationEngine):
        assert engine.evaluate_operator(RequirementOperator.not_equals, "employed", "unemployed") is True
        assert engine.evaluate_operator(RequirementOperator.not_equals, "unemployed", "unemployed") is False

    def test_contains_operator(self, engine: VerificationEngine):
        assert engine.evaluate_operator(RequirementOperator.contains, "pune, mumbai", "pune") is True
        assert engine.evaluate_operator(RequirementOperator.contains, ["pune", "mumbai"], "pune") is True
        assert engine.evaluate_operator(RequirementOperator.contains, "delhi", "pune") is False

    def test_in_operator(self, engine: VerificationEngine):
        assert engine.evaluate_operator(RequirementOperator.in_, "pune", ["pune", "mumbai"]) is True
        assert engine.evaluate_operator(RequirementOperator.in_, "delhi", ["pune", "mumbai"]) is False

    def test_not_in_operator(self, engine: VerificationEngine):
        assert engine.evaluate_operator(RequirementOperator.not_in, "delhi", ["pune", "mumbai"]) is True
        assert engine.evaluate_operator(RequirementOperator.not_in, "pune", ["pune", "mumbai"]) is False

    def test_numeric_comparisons(self, engine: VerificationEngine):
        assert engine.evaluate_operator(RequirementOperator.greater_than, 5, 2) is True
        assert engine.evaluate_operator(RequirementOperator.greater_than, 2, 5) is False
        assert engine.evaluate_operator(RequirementOperator.less_than, 2, 5) is True
        assert engine.evaluate_operator(RequirementOperator.greater_or_equal, 5, 5) is True
        assert engine.evaluate_operator(RequirementOperator.less_or_equal, 5, 5) is True

    def test_exists_operator(self, engine: VerificationEngine):
        assert engine.evaluate_operator(RequirementOperator.exists, "yes", None) is True
        assert engine.evaluate_operator(RequirementOperator.exists, True, None) is True
        assert engine.evaluate_operator(RequirementOperator.exists, None, None) is False


class TestVerificationEngineInvariants:
    def test_unknown_fact_never_promotes_to_satisfied(self, engine: VerificationEngine, sample_resource: Resource):
        """CRITICAL INVARIANT: Missing facts must produce RequirementStatus.unknown, NOT satisfied."""
        profile = CaseProfile(
            case_id="CASE-UNKNOWN",
            narrative="No details given.",
            facts=[
                CaseFact(field="location", value="Pune", status=FactStatus.explicit, source="user_input")
                # employment_status is completely absent!
            ],
        )

        status, evals, evidence, missing, warnings = engine.evaluate_resource(profile, sample_resource)

        assert status == MatchStatus.insufficient_information
        emp_eval = next(e for e in evals if e.field == "employment_status")
        assert emp_eval.status == RequirementStatus.unknown
        assert "employment_status" in missing

    def test_all_satisfied_produces_strong_match(self, engine: VerificationEngine, sample_resource: Resource):
        profile = CaseProfile(
            case_id="CASE-SATISFIED",
            narrative="Unemployed worker in Pune.",
            facts=[
                CaseFact(field="employment_status", value="unemployed", status=FactStatus.explicit, source="user_input"),
                CaseFact(field="location", value="Pune", status=FactStatus.explicit, source="user_input"),
            ],
        )

        status, evals, evidence, missing, warnings = engine.evaluate_resource(profile, sample_resource)

        assert status == MatchStatus.strong_match
        assert len(evidence) == 2
        assert all(e.status == RequirementStatus.satisfied for e in evals)
        assert len(missing) == 0

    def test_conflict_produces_conflict_detected_status(self, engine: VerificationEngine, sample_resource: Resource):
        profile = CaseProfile(
            case_id="CASE-CONFLICT",
            narrative="Worker lost job but works part-time.",
            facts=[
                CaseFact(field="employment_status", value="conflicting", status=FactStatus.conflicting, source="user_input"),
                CaseFact(field="location", value="Pune", status=FactStatus.explicit, source="user_input"),
            ],
            contradictions=[
                Contradiction(description="Employment conflict", fact_a="lost job", fact_b="part-time")
            ],
        )

        status, evals, evidence, missing, warnings = engine.evaluate_resource(profile, sample_resource)

        assert status == MatchStatus.conflict_detected

    def test_failed_critical_requirement_produces_not_supported(self, engine: VerificationEngine, sample_resource: Resource):
        profile = CaseProfile(
            case_id="CASE-FAIL",
            narrative="Employed worker in Pune.",
            facts=[
                CaseFact(field="employment_status", value="employed", status=FactStatus.explicit, source="user_input"),
                CaseFact(field="location", value="Pune", status=FactStatus.explicit, source="user_input"),
            ],
        )

        status, evals, evidence, missing, warnings = engine.evaluate_resource(profile, sample_resource)

        assert status == MatchStatus.not_supported_by_available_evidence
