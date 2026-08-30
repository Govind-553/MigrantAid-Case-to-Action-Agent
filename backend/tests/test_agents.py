"""
Phase 6 & 7: Agent Pipeline Unit and Integration Tests
=====================================================

Tests for:
- IntakeAgent
- NeedsAssessmentAgent
- MatchingAgent
- ActionPlanningAgent
- QualityAgent
- CaseOrchestrator (end-to-end multi-agent execution)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.agents.action_planner import ActionPlanningAgent
from app.agents.intake_agent import IntakeAgent
from app.agents.matching_agent import MatchingAgent
from app.agents.needs_agent import NeedsAssessmentAgent
from app.agents.orchestrator import CaseOrchestrator
from app.agents.quality_agent import QualityAgent
from app.schemas.domain import (
    CaseProfile,
    CaseState,
    CaseWorkflowState,
    FactStatus,
    MatchStatus,
    NeedCategory,
)
from app.services.evaluation_loader import load_evaluation_cases
from app.services.resource_kb import load_resource_kb

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESOURCES_PATH = DATA_DIR / "resources.json"
SOURCES_PATH = DATA_DIR / "sources.json"
EVAL_CASES_PATH = DATA_DIR / "evaluation_cases.json"


@pytest.fixture(scope="module")
def resource_kb():
    return load_resource_kb(RESOURCES_PATH, SOURCES_PATH)


@pytest.fixture(scope="module")
def eval_dataset(resource_kb):
    valid_ids = {r.resource_id for r in resource_kb.resources}
    return load_evaluation_cases(EVAL_CASES_PATH, valid_resource_ids=valid_ids)


class TestIntakeAgent:
    def test_extract_explicit_facts(self):
        agent = IntakeAgent()
        narrative = "A migrant worker in Pune recently lost his job. He has two children and says the household currently has no other income."
        profile = agent.process("CASE-001", narrative, force_heuristic=True)

        assert isinstance(profile, CaseProfile)
        assert profile.case_id == "CASE-001"
        assert profile.has_explicit_fact("location")
        assert profile.get_fact("location").value == "Pune"
        assert profile.get_fact("employment_status").value == "unemployed"
        assert profile.get_fact("other_household_income").value is False

    def test_detect_contradiction(self):
        agent = IntakeAgent()
        narrative = "The worker says he lost his job and is unemployed, but also mentions he works part-time casual shifts."
        profile = agent.process("CASE-008", narrative, force_heuristic=True)

        assert len(profile.contradictions) > 0
        emp_fact = profile.get_fact("employment_status")
        assert emp_fact is not None
        assert emp_fact.status == FactStatus.conflicting


class TestNeedsAssessmentAgent:
    def test_assess_employment_and_basic_needs(self):
        agent = IntakeAgent()
        profile = agent.process(
            "CASE-001",
            "A migrant worker in Pune recently lost his job. He has two children and says the household currently has no other income.",
            force_heuristic=True,
        )

        needs_agent = NeedsAssessmentAgent()
        assessment = needs_agent.assess(profile)

        categories = [n.category for n in assessment.needs]
        assert NeedCategory.employment in categories
        assert NeedCategory.basic_support in categories
        assert assessment.primary_need is not None


class TestMatchingAndVerificationAgent:
    def test_match_and_verify_strong_match(self, resource_kb):
        agent = IntakeAgent()
        profile = agent.process(
            "CASE-001",
            "A migrant worker in Pune recently lost his job. He has two children and says the household currently has no other income. He has an identity document.",
            force_heuristic=True,
        )

        needs_agent = NeedsAssessmentAgent()
        assessment = needs_agent.assess(profile)

        matching_agent = MatchingAgent()
        matches, recs, v_results = matching_agent.match_and_verify(profile, assessment, resource_kb)

        assert len(recs) > 0
        strong_matches = [r for r in recs if r.status == MatchStatus.strong_match]
        assert len(strong_matches) > 0
        assert strong_matches[0].resource_id == "RES-EMP-001"
        assert len(strong_matches[0].evidence) > 0


class TestActionPlanningAgent:
    def test_plan_generates_sequential_steps(self, resource_kb):
        intake = IntakeAgent()
        profile = intake.process(
            "CASE-001",
            "A migrant worker in Pune recently lost his job. He has an identity document.",
            force_heuristic=True,
        )
        assessment = NeedsAssessmentAgent().assess(profile)
        matches, recs, _ = MatchingAgent().match_and_verify(profile, assessment, resource_kb)

        planner = ActionPlanningAgent()
        plan = planner.plan(profile, assessment, recs)

        assert len(plan.actions) > 0
        step_numbers = [a.step for a in plan.actions]
        assert step_numbers == list(range(1, len(plan.actions) + 1))


class TestQualityAgent:
    def test_quality_check_passes_on_grounded_recommendations(self, resource_kb):
        intake = IntakeAgent()
        profile = intake.process("CASE-001", "A worker in Pune lost his job.", force_heuristic=True)
        assessment = NeedsAssessmentAgent().assess(profile)
        _, recs, _ = MatchingAgent().match_and_verify(profile, assessment, resource_kb)

        quality = QualityAgent()
        report = quality.check(profile, recs)

        assert report.passed is True
        assert report.human_review_enforced is True


class TestEndToEndCaseOrchestrator:
    def test_full_orchestrator_pipeline(self, resource_kb, eval_dataset):
        orchestrator = CaseOrchestrator()
        case_0 = eval_dataset.cases[0]

        state = orchestrator.process_case(case_0.case_id, case_0.narrative, resource_kb)

        assert isinstance(state, CaseState)
        assert state.case_id == case_0.case_id
        assert state.profile is not None
        assert state.needs_assessment is not None
        assert len(state.verified_recommendations) > 0
        assert state.action_plan is not None
        assert state.quality_report is not None
        assert state.human_review is not None
        assert len(state.trajectory) >= 6  # All 6 stages logged events

    def test_orchestrator_on_all_20_cases(self, resource_kb, eval_dataset):
        orchestrator = CaseOrchestrator()
        for case in eval_dataset.cases:
            state = orchestrator.process_case(case.case_id, case.narrative, resource_kb)
            assert state.case_id == case.case_id
            assert len(state.trajectory) > 0
            assert state.action_plan is not None
