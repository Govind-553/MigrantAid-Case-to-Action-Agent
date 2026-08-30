"""
MigrantAid Baseline Runner CLI
==============================

Executes the single-prompt baseline against all evaluation cases and saves
the structured outputs for evaluation scoring.

Usage:
    python baseline/baseline_runner.py [--offline] [--output baseline/baseline_results.json]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.config import logger  # noqa: E402
from app.services.baseline import BaselineService  # noqa: E402
from app.services.evaluation_loader import load_evaluation_cases  # noqa: E402
from app.services.resource_kb import load_resource_kb  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Run MigrantAid baseline on evaluation cases.")
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
        default=str(PROJECT_ROOT / "baseline" / "baseline_results.json"),
        help="Path to write baseline output JSON",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force offline simulated mode without making external API calls",
    )
    args = parser.parse_args()

    print("==================================================")
    print("           MIGRANTAID BASELINE RUNNER             ")
    print("==================================================")
    print(f"Cases file:     {args.cases}")
    print(f"Resources file: {args.resources}")
    print(f"Sources file:   {args.sources}")
    print(f"Output file:    {args.output}")
    print(f"Offline mode:   {args.offline}")
    print()

    # 1. Load Resource Knowledge Base
    print("Loading approved resources knowledge base...")
    kb = load_resource_kb(args.resources, args.sources)
    print(f"Loaded {kb.resource_count} resources from {kb.source_count} sources.")

    # 2. Load Evaluation Cases
    print("Loading evaluation cases...")
    eval_dataset = load_evaluation_cases(args.cases, valid_resource_ids={r.resource_id for r in kb.resources})
    print(f"Loaded {len(eval_dataset.cases)} evaluation cases.")
    print()

    # 3. Execute Baseline
    service = BaselineService()
    print(f"Executing baseline using model: {service.model_name} (live LLM active: {service._has_live_llm and not args.offline})...")
    outputs = service.run_all(eval_dataset.cases, kb, force_offline=args.offline)

    # 4. Save results to output JSON
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_dict = {
        "dataset_version": eval_dataset.dataset_version,
        "system": "baseline",
        "model": service.model_name,
        "case_count": len(outputs),
        "total_latency_ms": sum(o.latency_ms for o in outputs),
        "avg_latency_ms": sum(o.latency_ms for o in outputs) / len(outputs) if outputs else 0.0,
        "results": [o.model_dump() for o in outputs],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_dict, f, indent=2)

    print()
    print("--------------------------------------------------------------------------------")
    print(f"{'Case ID':<10} | {'Primary Need':<18} | {'Recommended Resources':<25} | {'Latency':<8}")
    print("--------------------------------------------------------------------------------")
    for o in outputs:
        res_str = ", ".join(o.recommended_resource_ids) if o.recommended_resource_ids else "None"
        print(f"{o.case_id:<10} | {o.primary_need:<18} | {res_str:<25} | {o.latency_ms:.1f}ms")
    print("--------------------------------------------------------------------------------")
    print()
    print(f"[SUCCESS] Baseline execution complete. Output saved to: {output_path}")
    print("==================================================")


if __name__ == "__main__":
    main()
