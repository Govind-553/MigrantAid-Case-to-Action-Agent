"""
MigrantAid REST API Routes
==========================

Provides endpoints for case intake, facts review & correction, resource browsing,
human caseworker review, and evaluation benchmarks.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas.domain import (
    CaseFact,
    CaseState,
    HumanReviewDecision,
)
from app.services.case_workflow import workflow_service
from app.services.evaluation_loader import load_evaluation_cases
from app.services.evaluator import EvaluatorService
from app.services.resource_kb import load_resource_kb

router = APIRouter(prefix="/api", tags=["MigrantAid API"])

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EVAL_CASES_PATH = DATA_DIR / "evaluation_cases.json"
BASELINE_REPORT_PATH = PROJECT_ROOT / "evaluation" / "baseline_evaluation_report.json"
AGENT_REPORT_PATH = PROJECT_ROOT / "evaluation" / "agent_evaluation_report.json"


# --- Request/Response DTOs ---

class CreateCaseRequest(BaseModel):
    narrative: str = Field(..., min_length=5, description="Natural-language case narrative")
    case_id: str | None = Field(default=None, description="Optional custom case ID")


class UpdateFactsRequest(BaseModel):
    facts: list[CaseFact] = Field(..., description="List of corrected case facts")


class SubmitReviewRequest(BaseModel):
    decision: HumanReviewDecision = Field(..., description="Human review decision")
    reviewer_notes: str | None = Field(default=None, description="Caseworker notes or instructions")
    modified_recommendation_ids: list[str] = Field(default_factory=list)
    rejected_recommendation_ids: list[str] = Field(default_factory=list)


# --- Case Management Endpoints ---

@router.post("/cases", response_model=CaseState, status_code=status.HTTP_201_CREATED)
async def create_case(req: CreateCaseRequest):
    """Submit a case narrative, trigger the multi-agent pipeline, and return the complete CaseState."""
    try:
        case_state = workflow_service.create_case(req.narrative, req.case_id)
        return case_state
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process case: {e!s}",
        ) from e


@router.get("/cases")
async def list_cases():
    """List summary metadata for all active cases."""
    return {"cases": workflow_service.list_cases()}


@router.get("/cases/{case_id}", response_model=CaseState)
async def get_case(case_id: str):
    """Retrieve full CaseState for a specific case."""
    case = workflow_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found.")
    return case


@router.put("/cases/{case_id}/facts", response_model=CaseState)
async def update_case_facts(case_id: str, req: UpdateFactsRequest):
    """Caseworker edits/corrects facts, triggering automated re-verification and updated action plan."""
    updated = workflow_service.update_case_facts(case_id, req.facts)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found.")
    return updated


@router.post("/cases/{case_id}/review", response_model=CaseState)
async def submit_case_review(case_id: str, req: SubmitReviewRequest):
    """Submit a human caseworker review checkpoint decision (Approve, Modify, Request Info, Reject)."""
    updated = workflow_service.submit_human_review(
        case_id=case_id,
        decision=req.decision,
        reviewer_notes=req.reviewer_notes,
        modified_recommendation_ids=req.modified_recommendation_ids,
        rejected_recommendation_ids=req.rejected_recommendation_ids,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found.")
    return updated


# --- Resource Knowledge Base Endpoints ---

@router.get("/resources")
async def list_resources():
    """List all approved resources in the knowledge base."""
    kb = workflow_service.kb
    return {
        "dataset_version": kb.dataset_version,
        "resource_count": kb.resource_count,
        "resources": [r.model_dump() for r in kb.resources],
    }


@router.get("/resources/{resource_id}")
async def get_resource(resource_id: str):
    """Retrieve specific resource details."""
    resource = workflow_service.kb.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Resource '{resource_id}' not found.")
    return resource.model_dump()


# --- Evaluation & Benchmark Endpoints ---

@router.get("/evaluation/baseline")
async def get_baseline_evaluation():
    """Retrieve official baseline benchmark evaluation report."""
    if not BASELINE_REPORT_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baseline evaluation report not found. Run baseline evaluation first.",
        )
    with open(BASELINE_REPORT_PATH, encoding="utf-8") as f:
        return json.load(f)


@router.get("/evaluation/agent")
async def get_agent_evaluation():
    """Run or retrieve the agentic system evaluation against the 20 ground-truth cases."""
    if AGENT_REPORT_PATH.exists():
        with open(AGENT_REPORT_PATH, encoding="utf-8") as f:
            return json.load(f)

    # If not yet pre-generated, execute dynamically
    eval_dataset = load_evaluation_cases(
        EVAL_CASES_PATH, valid_resource_ids={r.resource_id for r in workflow_service.kb.resources}
    )

    agent_outputs = []
    for case in eval_dataset.cases:
        state = workflow_service.orchestrator.process_case(case.case_id, case.narrative, workflow_service.kb)
        # Convert state into evaluation output shape
        recommended_rids = [
            r.resource_id for r in state.verified_recommendations
            if r.status.value in ("strong_match", "potential_match", "insufficient_information", "conflict_detected")
        ]
        primary_need = state.needs_assessment.primary_need.category.value if state.needs_assessment and state.needs_assessment.primary_need else "other"
        missing = state.profile.missing_information if state.profile else []
        next_step = state.action_plan.actions[0].action if state.action_plan and state.action_plan.actions else ""
        
        evidence_snippets = []
        status_snippets = []
        for r in state.verified_recommendations:
            status_snippets.append(f"{r.resource_id}: {r.status.value}")
            for ev in r.evidence:
                evidence_snippets.append(ev.evidence)
            for req_eval in r.requirement_evaluations:
                if req_eval.evidence_text:
                    evidence_snippets.append(req_eval.evidence_text)
        
        evidence_text = "; ".join(evidence_snippets) if evidence_snippets else "Verified eligibility requirements using case evidence."
        eligibility_assessment = "; ".join(status_snippets) if status_snippets else "No verified resource match found in approved dataset."

        agent_outputs.append({
            "case_id": case.case_id,
            "primary_need": primary_need,
            "recommended_resource_ids": recommended_rids,
            "eligibility_assessment": eligibility_assessment,
            "evidence_text": evidence_text,
            "missing_information": missing,
            "next_step": next_step,
            "latency_ms": sum(e.latency_ms or 0.0 for e in state.trajectory),
        })

    evaluator = EvaluatorService()
    scores = evaluator.evaluate_all(eval_dataset.cases, agent_outputs, system_name="agentic")
    summary = evaluator.compute_summary_metrics(scores)

    report_dict = {
        "dataset_version": eval_dataset.dataset_version,
        "system": "agentic",
        "summary": summary,
        "detailed_results": [s.model_dump(mode="json") for s in scores],
    }

    # Cache report
    AGENT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AGENT_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)

    return report_dict


@router.get("/evaluation/comparison")
async def get_evaluation_comparison():
    """Retrieve side-by-side benchmark comparison between baseline and agentic systems."""
    baseline_report = await get_baseline_evaluation()
    agent_report = await get_agent_evaluation()

    return {
        "dataset_version": baseline_report.get("dataset_version", "v1.0"),
        "total_cases": 20,
        "baseline_summary": baseline_report.get("summary", {}),
        "agentic_summary": agent_report.get("summary", {}),
        "improvements": {
            "varr_delta_percentage": agent_report["summary"]["varr_percentage"] - baseline_report["summary"]["varr_percentage"],
            "score_delta": agent_report["summary"]["avg_total_score"] - baseline_report["summary"]["avg_total_score"],
        },
    }
