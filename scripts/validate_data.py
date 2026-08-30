"""
Standalone CLI tool to validate all data files:
- data/resources.json
- data/sources.json
- data/evaluation_cases.json
"""

import sys
from pathlib import Path

# Add backend to sys.path so we can import app modules
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.services.resource_kb import load_resource_kb, DataLoadError  # noqa: E402
from app.services.evaluation_loader import load_evaluation_cases  # noqa: E402


def main():
    print("==================================================")
    print("          MIGRANTAID DATA VALIDATION              ")
    print("==================================================")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    data_dir = PROJECT_ROOT / "data"
    resources_path = data_dir / "resources.json"
    sources_path = data_dir / "sources.json"
    eval_cases_path = data_dir / "evaluation_cases.json"

    has_errors = False

    # 1. Validate Resource Knowledge Base
    print("Validating Resource Knowledge Base (resources.json + sources.json)...")
    try:
        kb = load_resource_kb(resources_path, sources_path)
        print(f"[SUCCESS] Resource KB valid: {kb.resource_count} resources, {kb.source_count} sources (version: {kb.dataset_version})")
    except DataLoadError as e:
        print(f"[FAILED] Resource KB validation failed: {e}")
        has_errors = True
        kb = None

    # 2. Validate Evaluation Dataset
    print()
    print("Validating Evaluation Dataset (evaluation_cases.json)...")
    try:
        valid_rids = {r.resource_id for r in kb.resources} if kb else None
        eval_dataset = load_evaluation_cases(eval_cases_path, valid_resource_ids=valid_rids)
        print(f"[SUCCESS] Evaluation dataset valid: {len(eval_dataset.cases)} cases (version: {eval_dataset.dataset_version}, status: {eval_dataset.status})")
    except DataLoadError as e:
        print(f"[FAILED] Evaluation dataset validation failed: {e}")
        has_errors = True

    print()
    print("==================================================")
    if has_errors:
        print("Result: DATA VALIDATION FAILED")
        sys.exit(1)
    else:
        print("Result: ALL DATA FILES ARE VALID")
        sys.exit(0)


if __name__ == "__main__":
    main()
