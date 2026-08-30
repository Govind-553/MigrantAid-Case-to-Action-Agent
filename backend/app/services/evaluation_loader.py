"""
Evaluation Case Loader
======================

Loads and validates evaluation_cases.json — the ground-truth dataset
used to score system performance.

Design rules:
- Each case must have a unique case_id.
- expected_resource_ids must reference resources in the KB.
- known_needs must be valid NeedCategory values.
- Contradictions are preserved (they are intentional test data).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.schemas.domain import NeedCategory
from app.services.resource_kb import DataLoadError

logger = logging.getLogger("migrantaid")


class EvaluationCase(BaseModel):
    """Schema for a single evaluation case from evaluation_cases.json."""

    case_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    category: list[str] = Field(default_factory=list)
    difficulty: str = Field(default="medium")
    narrative: str = Field(..., min_length=1)
    known_facts: dict[str, Any] = Field(default_factory=dict)
    known_needs: list[str] = Field(default_factory=list)
    critical_missing_information: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    expected_resource_ids: list[str] = Field(default_factory=list)
    expected_resource_status: str = Field(default="")
    expected_actions: list[str] = Field(default_factory=list)
    scoring_notes: str = Field(default="")

    @field_validator("known_needs", mode="before")
    @classmethod
    def validate_known_needs(cls, v: list[str]) -> list[str]:
        valid_categories = {c.value for c in NeedCategory}
        for need in v:
            if need not in valid_categories:
                raise ValueError(
                    f"Unknown need category: '{need}'. "
                    f"Valid categories: {sorted(valid_categories)}"
                )
        return v


class EvaluationDataset(BaseModel):
    """Wrapper for the full evaluation_cases.json file."""

    dataset_version: str = Field(default="unknown")
    status: str = Field(default="")
    case_count: int = Field(default=0, ge=0)
    freeze_status: str = Field(default="NOT_FROZEN")
    cases: list[EvaluationCase] = Field(default_factory=list)


def load_evaluation_cases(
    eval_cases_path: str | Path,
    valid_resource_ids: set[str] | None = None,
) -> EvaluationDataset:
    """Load and validate the evaluation dataset.

    Args:
        eval_cases_path: Path to evaluation_cases.json
        valid_resource_ids: Optional set of known resource IDs for cross-referencing.
            If provided, expected_resource_ids in each case are validated.

    Returns:
        A validated EvaluationDataset.

    Raises:
        DataLoadError: If the file is missing, malformed, or contains invalid cases.
    """
    eval_cases_path = Path(eval_cases_path)
    errors: list[str] = []

    if not eval_cases_path.exists():
        raise DataLoadError(f"Evaluation cases file not found: {eval_cases_path}")

    try:
        with open(eval_cases_path, encoding="utf-8") as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as e:
        raise DataLoadError(f"Invalid JSON in evaluation cases file: {e}") from e

    if "cases" not in raw_data:
        raise DataLoadError("evaluation_cases.json missing 'cases' key")

    # --- Parse cases ---
    try:
        dataset = EvaluationDataset(**raw_data)
    except ValidationError as e:
        raise DataLoadError(f"Evaluation dataset schema validation failed: {e}") from e

    # --- Check case_count matches actual ---
    if dataset.case_count != len(dataset.cases):
        errors.append(
            f"Declared case_count ({dataset.case_count}) does not match "
            f"actual number of cases ({len(dataset.cases)})"
        )

    # --- Check for duplicate case_ids ---
    seen_ids: set[str] = set()
    for case in dataset.cases:
        if case.case_id in seen_ids:
            errors.append(f"Duplicate case_id: {case.case_id}")
        seen_ids.add(case.case_id)

    # --- Cross-reference expected_resource_ids against KB ---
    if valid_resource_ids is not None:
        for case in dataset.cases:
            for rid in case.expected_resource_ids:
                if rid not in valid_resource_ids:
                    errors.append(
                        f"Case {case.case_id}: expected_resource_id '{rid}' "
                        f"not found in resource KB"
                    )

    if errors:
        error_msg = f"Evaluation data validation failed with {len(errors)} error(s):\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        logger.error(error_msg)
        raise DataLoadError(error_msg, errors=errors)

    logger.info(
        f"Evaluation dataset loaded: {len(dataset.cases)} cases, "
        f"version={dataset.dataset_version}, status={dataset.status}"
    )

    return dataset
