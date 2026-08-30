"""
MigrantAid Evaluation Runner CLI
================================

Scores outputs (baseline or agentic) against the 20 ground-truth evaluation cases
using the 6-dimension VARR rubric.

Usage:
    python evaluation/run_evaluation.py --results baseline/baseline_results.json --output evaluation/baseline_evaluation_report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add backend directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.services.evaluation_loader import load_evaluation_cases  # noqa: E402
from app.services.evaluator import EvaluatorService  # noqa: E402
from app.services.resource_kb import load_resource_kb  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Evaluate MigrantAid system outputs against ground truth.")
    parser.add_argument(
        "--results",
        type=str,
        default=str(PROJECT_ROOT / "baseline" / "baseline_results.json"),
        help="Path to results JSON file containing model outputs",
    )
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
        default=str(PROJECT_ROOT / "evaluation" / "baseline_evaluation_report.json"),
        help="Path to write evaluation report JSON",
    )
    parser.add_argument(
        "--system",
        type=str,
        default="",
        help="Override system name (defaults to system name declared in results JSON)",
    )
    args = parser.parse_args()

    print("==================================================")
    print("           MIGRANTAID EVALUATION RUNNER           ")
    print("==================================================")
    print(f"Results file:   {args.results}")
    print(f"Cases file:     {args.cases}")
    print(f"Output file:    {args.output}")
    print()

    # 1. Load results JSON
    results_path = Path(args.results)
    if not results_path.exists():
        print(f"[FAILED] Results file not found at: {results_path}")
        print("Please run the baseline or agent workflow first to generate outputs.")
        sys.exit(1)

    with open(results_path, encoding="utf-8") as f:
        results_data = json.load(f)

    outputs = results_data.get("results", [])
    system_name = args.system or results_data.get("system", "unknown")
    print(f"Loaded {len(outputs)} outputs for system '{system_name}'.")

    # 2. Load Evaluation Cases
    kb = load_resource_kb(args.resources, args.sources)
    eval_dataset = load_evaluation_cases(args.cases, valid_resource_ids={r.resource_id for r in kb.resources})
    print(f"Loaded {len(eval_dataset.cases)} evaluation cases.")
    print()

    # 3. Score all cases
    evaluator = EvaluatorService()
    scores = evaluator.evaluate_all(eval_dataset.cases, outputs, system_name=system_name)
    summary = evaluator.compute_summary_metrics(scores)

    # 4. Display Results Breakdown Table
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

    # 5. Display Summary Metrics
    print("==================================================")
    print("                 BENCHMARK SUMMARY                ")
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

    # 6. Save detailed report
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_dict = {
        "dataset_version": eval_dataset.dataset_version,
        "system": system_name,
        "summary": summary,
        "detailed_results": [s.model_dump(mode="json") for s in scores],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)

    print(f"\n[SUCCESS] Detailed evaluation report saved to: {output_path}")


if __name__ == "__main__":
    main()
