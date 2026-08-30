"""
MigrantAid System Comparison CLI
================================

Produces a side-by-side benchmark comparison between the Baseline System
and the Agentic System.

Usage:
    python evaluation/compare_systems.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASELINE_REPORT_PATH = PROJECT_ROOT / "evaluation" / "baseline_evaluation_report.json"
AGENT_REPORT_PATH = PROJECT_ROOT / "evaluation" / "agent_evaluation_report.json"


def main():
    parser = argparse.ArgumentParser(description="Compare Baseline vs Agentic system benchmarks.")
    parser.add_argument(
        "--baseline",
        type=str,
        default=str(BASELINE_REPORT_PATH),
        help="Path to baseline evaluation report JSON",
    )
    parser.add_argument(
        "--agent",
        type=str,
        default=str(AGENT_REPORT_PATH),
        help="Path to agent evaluation report JSON",
    )
    args = parser.parse_args()

    b_path = Path(args.baseline)
    a_path = Path(args.agent)

    if not b_path.exists():
        print(f"[ERROR] Baseline report not found: {b_path}. Run baseline evaluation first.")
        sys.exit(1)
    if not a_path.exists():
        print(f"[ERROR] Agent report not found: {a_path}. Run agent evaluation first.")
        sys.exit(1)

    with open(b_path, encoding="utf-8") as f:
        b_data = json.load(f)
    with open(a_path, encoding="utf-8") as f:
        a_data = json.load(f)

    b_sum = b_data.get("summary", {})
    a_sum = a_data.get("summary", {})

    print("================================================================================")
    print("                MIGRANTAID: BASELINE VS AGENTIC COMPARISON                      ")
    print("================================================================================")
    print(f"{'Metric':<35} | {'Baseline System':<18} | {'Agentic System':<18} | {'Delta':<10}")
    print("--------------------------------------------------------------------------------")
    b_varr = b_sum.get("varr_percentage", 0.0)
    a_varr = a_sum.get("varr_percentage", 0.0)
    varr_delta = a_varr - b_varr
    print(f"{'VARR (Verified Actionable Rate)':<35} | {b_varr:>16.1f}% | {a_varr:>16.1f}% | {varr_delta:>+8.1f}%")

    b_tot = b_sum.get("avg_total_score", 0.0)
    a_tot = a_sum.get("avg_total_score", 0.0)
    tot_delta = a_tot - b_tot
    print(f"{'Average Total Score (out of 100)':<35} | {b_tot:>17.1f} | {a_tot:>17.1f} | {tot_delta:>+9.1f}")

    b_succ = b_sum.get("successful_cases", 0)
    a_succ = a_sum.get("successful_cases", 0)
    print(f"{'Successful Cases (out of 20)':<35} | {b_succ:>17} | {a_succ:>17} | {a_succ - b_succ:>+9}")
    print("--------------------------------------------------------------------------------")

    # Dimension Scores
    print("\n--- Dimension Score Breakdown (Average Points) ---")
    dims = ["primary_need", "resource", "evidence", "missing_information", "unsupported_claim", "actionable_next_step"]
    for dim in dims:
        b_d = b_sum.get("avg_dimension_scores", {}).get(dim, 0.0)
        a_d = a_sum.get("avg_dimension_scores", {}).get(dim, 0.0)
        delta = a_d - b_d
        label = dim.replace("_", " ").title()
        print(f"{label:<35} | {b_d:>17.1f} | {a_d:>17.1f} | {delta:>+9.1f}")

    print("--------------------------------------------------------------------------------")

    # Failure Category Comparison
    print("\n--- Failure Category Occurrences (Lower is Better) ---")
    b_fail = b_sum.get("failure_category_distribution", {})
    a_fail = a_sum.get("failure_category_distribution", {})
    all_cats = sorted(set(list(b_fail.keys()) + list(a_fail.keys())))
    for cat in all_cats:
        b_cnt = b_fail.get(cat, 0)
        a_cnt = a_fail.get(cat, 0)
        diff = a_cnt - b_cnt
        print(f"{cat:<35} | {b_cnt:>17} | {a_cnt:>17} | {diff:>+9}")

    print("================================================================================")


if __name__ == "__main__":
    main()
