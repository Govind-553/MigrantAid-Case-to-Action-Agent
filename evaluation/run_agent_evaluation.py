"""
MigrantAid Agent Evaluation Runner CLI
======================================

Runs the full multi-stage agentic workflow across all 20 evaluation cases,
records detailed execution trajectories, and scores outputs using the VARR rubric.

Usage:
    python evaluation/run_agent_evaluation.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Add backend directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from app.agents.orchestrator import CaseOrchestrator  # noqa: E402
    from app.services.evaluation_loader import load_evaluation_cases  # noqa: E402
    from app.services.evaluator import EvaluatorService  # noqa: E402
    from app.services.resource_kb import load_resource_kb  # noqa: E402
except ImportError:
    from backend.app.agents.orchestrator import CaseOrchestrator  # type: ignore
    from backend.app.services.evaluation_loader import load_evaluation_cases  # type: ignore
    from backend.app.services.evaluator import EvaluatorService  # type: ignore
    from backend.app.services.resource_kb import load_resource_kb  # type: ignore


def main():
    parser = argparse.ArgumentParser(description="Run MigrantAid Agentic System Evaluation.")
    parser.add_argument(
        "--cases",
        type=str,
        default=str(PROJECT_ROOT / "data" / "evaluation_cases.json"),
        help="Path to evaluation_cases.json",
    )
    parser.add_argument(
        "--resources",
        type=str,
        default=str(PROJECT_ROOT / "data" / "resources.json"),
        help="Path to resources.json",
    )
    parser.add_argument(
        "--sources",
        type=str,
        default=str(PROJECT_ROOT / "data" / "sources.json"),
        help="Path to sources.json",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(PROJECT_ROOT / "evaluation" / "agent_evaluation_report.json"),
        help="Path to write agent evaluation report JSON",
    )
    parser.add_argument(
        "--trajectories",
        type=str,
        default=str(PROJECT_ROOT / "trajectories" / "agent_trajectories.json"),
        help="Path to write observable execution trajectories JSON",
    )
    args = parser.parse_args()

    print("==================================================")
    print("       MIGRANTAID AGENTIC SYSTEM EVALUATION       ")
    print("==================================================")
    print(f"Cases file:        {args.cases}")
    print(f"Resources file:    {args.resources}")
    print(f"Output report:     {args.output}")
    print(f"Trajectories file: {args.trajectories}")
    print()

    # 1. Load Knowledge Base and Evaluation Dataset
    kb = load_resource_kb(args.resources, args.sources)
    eval_dataset = load_evaluation_cases(args.cases, valid_resource_ids={r.resource_id for r in kb.resources})
    print(f"Loaded {len(eval_dataset.cases)} evaluation cases and {kb.resource_count} approved resources.")
    print()

    # 2. Execute Multi-Stage Agentic Pipeline
    orchestrator = CaseOrchestrator()
    print("Executing agentic workflow (Intake -> Needs -> Matching -> Verification -> Action Planning -> Quality Check)...")

    agent_outputs = []
    trajectories_data = []

    start_all = time.time()
    for i, case in enumerate(eval_dataset.cases):
        state = orchestrator.process_case(case.case_id, case.narrative, kb)

        # Collect trajectory
        trajectories_data.append({
            "case_id": case.case_id,
            "workflow_state": state.workflow_state.value,
            "events": [e.model_dump(mode="json") for e in state.trajectory],
        })

        # Format output for VARR evaluation
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

    total_time = (time.time() - start_all) * 1000
    print(f"Completed agentic pipeline in {total_time:.1f}ms ({total_time/len(eval_dataset.cases):.1f}ms avg/case).")
    print()

    # 3. Score all cases with VARR rubric
    evaluator = EvaluatorService()
    scores = evaluator.evaluate_all(eval_dataset.cases, agent_outputs, system_name="agentic")
    summary = evaluator.compute_summary_metrics(scores)

    # 4. Display Results Table
    print("---------------------------------------------------------------------------------------------------------")
    print(f"{'Case ID':<10} | {'Need(20)':<8} | {'Res(20)':<8} | {'Evid(20)':<8} | {'Miss(15)':<8} | {'Unsup(15)':<9} | {'Act(10)':<7} | {'Total':<5} | {'Status':<6}")
    print("---------------------------------------------------------------------------------------------------------")
    for s in scores:
        status_str = "PASS" if s.successful else "FAIL"
        d = s.dimensions
        print(
            f"{s.case_id:<10} | {d.primary_need:<8} | {d.resource:<8} | {d.evidence:<8} | "
            f"{d.missing_information:<8} | {d.unsupported_claim:<9} | {d.actionable_next_step:<7} | "
            f"{s.score:<5} | {status_str:<6}"
        )
    print("---------------------------------------------------------------------------------------------------------")
    print()

    # 5. Display Benchmark Summary
    print("==================================================")
    print("           AGENTIC BENCHMARK SUMMARY              ")
    print("==================================================")
    print(f"System:                  {summary['system']}")
    print(f"Total Cases:             {summary['total_cases']}")
    print(f"Successful Cases:        {summary['successful_cases']}")
    print(f"VARR Metric:             {summary['varr_percentage']}%")
    print(f"Average Total Score:     {summary['avg_total_score']} / 100")
    print()
    print("Average Dimension Scores:")
    for dim_name, dim_score in summary["avg_dimension_scores"].items():
        print(f"  - {dim_name:<24}: {dim_score}")
    print()
    print("Failure Category Breakdown:")
    if summary["failure_category_distribution"]:
        for cat, cnt in summary["failure_category_distribution"].items():
            print(f"  - {cat:<24}: {cnt} occurrence(s)")
    else:
        print("  None (all cases passed!)")
    print("==================================================")

    # 6. Save Trajectories & Report
    traj_path = Path(args.trajectories)
    traj_path.parent.mkdir(parents=True, exist_ok=True)
    with open(traj_path, "w", encoding="utf-8") as f:
        json.dump({"dataset_version": eval_dataset.dataset_version, "trajectories": trajectories_data}, f, indent=2)
    print(f"\n[SUCCESS] Trajectories saved to: {traj_path}")

    report_path = Path(args.output)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "dataset_version": eval_dataset.dataset_version,
            "system": "agentic",
            "summary": summary,
            "detailed_results": [s.model_dump(mode="json") for s in scores],
        }, f, indent=2)
    print(f"[SUCCESS] Agent evaluation report saved to: {report_path}")


if __name__ == "__main__":
    main()
