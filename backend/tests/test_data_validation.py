"""
Phase 3: Data Validation Tests
===============================

Tests that the synthetic dataset files (resources.json, sources.json,
evaluation_cases.json) pass schema validation and referential integrity checks.

These tests use the REAL data files in data/ — this is intentional.
If the data changes in ways that break the schemas, these tests catch it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.schemas.domain import NeedCategory, Resource, Source
from app.services.evaluation_loader import (
    DataLoadError,
    EvaluationCase,
    EvaluationDataset,
    load_evaluation_cases,
)
from app.services.resource_kb import ResourceKB, load_resource_kb

# Resolve data directory relative to project root
# test file: backend/tests/test_data_validation.py
# parents:   backend/tests/ -> backend/ -> project_root/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESOURCES_PATH = DATA_DIR / "resources.json"
SOURCES_PATH = DATA_DIR / "sources.json"
EVAL_CASES_PATH = DATA_DIR / "evaluation_cases.json"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def resource_kb() -> ResourceKB:
    """Load the full resource KB once for this test module."""
    return load_resource_kb(RESOURCES_PATH, SOURCES_PATH)


@pytest.fixture(scope="module")
def eval_dataset(resource_kb: ResourceKB) -> EvaluationDataset:
    """Load the eval dataset with cross-referencing against the KB."""
    valid_ids = {r.resource_id for r in resource_kb.resources}
    return load_evaluation_cases(EVAL_CASES_PATH, valid_resource_ids=valid_ids)


# ---------------------------------------------------------------------------
# Resource KB validation
# ---------------------------------------------------------------------------


class TestResourceKBLoading:
    def test_resources_file_exists(self):
        assert RESOURCES_PATH.exists(), f"resources.json not found at {RESOURCES_PATH}"

    def test_sources_file_exists(self):
        assert SOURCES_PATH.exists(), f"sources.json not found at {SOURCES_PATH}"

    def test_resources_load_successfully(self, resource_kb: ResourceKB):
        assert resource_kb.resource_count > 0

    def test_sources_load_successfully(self, resource_kb: ResourceKB):
        assert resource_kb.source_count > 0

    def test_all_resource_ids_are_unique(self, resource_kb: ResourceKB):
        ids = [r.resource_id for r in resource_kb.resources]
        assert len(ids) == len(set(ids)), "Duplicate resource IDs detected"

    def test_all_source_ids_are_unique(self, resource_kb: ResourceKB):
        ids = [s.source_id for s in resource_kb.sources]
        assert len(ids) == len(set(ids)), "Duplicate source IDs detected"

    def test_every_resource_references_valid_source(self, resource_kb: ResourceKB):
        source_ids = {s.source_id for s in resource_kb.sources}
        for resource in resource_kb.resources:
            assert resource.source_id in source_ids, (
                f"Resource {resource.resource_id} references unknown source: {resource.source_id}"
            )

    def test_every_resource_has_a_category(self, resource_kb: ResourceKB):
        for resource in resource_kb.resources:
            assert resource.category is not None
            assert isinstance(resource.category, NeedCategory)

    def test_every_resource_has_nonempty_name(self, resource_kb: ResourceKB):
        for resource in resource_kb.resources:
            assert resource.name.strip(), f"Resource {resource.resource_id} has empty name"

    def test_every_resource_has_geography_country(self, resource_kb: ResourceKB):
        for resource in resource_kb.resources:
            assert resource.geography.country.strip(), (
                f"Resource {resource.resource_id} has empty geography.country"
            )

    def test_lookup_by_id_works(self, resource_kb: ResourceKB):
        first = resource_kb.resources[0]
        found = resource_kb.get_resource(first.resource_id)
        assert found is not None
        assert found.resource_id == first.resource_id

    def test_lookup_nonexistent_returns_none(self, resource_kb: ResourceKB):
        assert resource_kb.get_resource("NONEXISTENT-ID") is None

    def test_get_resources_by_category(self, resource_kb: ResourceKB):
        employment = resource_kb.get_resources_by_category("employment")
        for r in employment:
            assert r.category == NeedCategory.employment


class TestResourceKBErrorHandling:
    def test_missing_resources_file_raises_error(self, tmp_path: Path):
        with pytest.raises(DataLoadError, match="not found"):
            load_resource_kb(tmp_path / "missing.json", SOURCES_PATH)

    def test_missing_sources_file_raises_error(self, tmp_path: Path):
        with pytest.raises(DataLoadError, match="not found"):
            load_resource_kb(RESOURCES_PATH, tmp_path / "missing.json")

    def test_malformed_json_raises_error(self, tmp_path: Path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{invalid json", encoding="utf-8")
        with pytest.raises(DataLoadError, match="Invalid JSON"):
            load_resource_kb(bad_file, SOURCES_PATH)

    def test_missing_resources_key_raises_error(self, tmp_path: Path):
        no_key = tmp_path / "no_key.json"
        no_key.write_text('{"dataset_version": "v1.0"}', encoding="utf-8")
        with pytest.raises(DataLoadError, match="missing 'resources' key"):
            load_resource_kb(no_key, SOURCES_PATH)

    def test_duplicate_resource_ids_raises_error(self, tmp_path: Path):
        dup_resources = tmp_path / "dup.json"
        dup_data = {
            "dataset_version": "v1.0",
            "resources": [
                {
                    "resource_id": "RES-DUP",
                    "name": "Dup1",
                    "category": "employment",
                    "geography": {"country": "India"},
                    "source_id": "SRC-EMP-A",
                },
                {
                    "resource_id": "RES-DUP",
                    "name": "Dup2",
                    "category": "employment",
                    "geography": {"country": "India"},
                    "source_id": "SRC-EMP-A",
                },
            ],
        }
        dup_resources.write_text(json.dumps(dup_data), encoding="utf-8")
        with pytest.raises(DataLoadError, match="Duplicate resource_id"):
            load_resource_kb(dup_resources, SOURCES_PATH)


# ---------------------------------------------------------------------------
# Evaluation dataset validation
# ---------------------------------------------------------------------------


class TestEvaluationCasesLoading:
    def test_eval_cases_file_exists(self):
        assert EVAL_CASES_PATH.exists(), f"evaluation_cases.json not found at {EVAL_CASES_PATH}"

    def test_eval_dataset_loads_successfully(self, eval_dataset: EvaluationDataset):
        assert len(eval_dataset.cases) > 0

    def test_case_count_matches_declared(self, eval_dataset: EvaluationDataset):
        assert eval_dataset.case_count == len(eval_dataset.cases)

    def test_all_case_ids_are_unique(self, eval_dataset: EvaluationDataset):
        ids = [c.case_id for c in eval_dataset.cases]
        assert len(ids) == len(set(ids)), "Duplicate case IDs detected"

    def test_every_case_has_narrative(self, eval_dataset: EvaluationDataset):
        for case in eval_dataset.cases:
            assert case.narrative.strip(), f"Case {case.case_id} has empty narrative"

    def test_every_case_has_known_facts(self, eval_dataset: EvaluationDataset):
        for case in eval_dataset.cases:
            assert len(case.known_facts) > 0, f"Case {case.case_id} has no known_facts"

    def test_every_known_need_is_valid_category(self, eval_dataset: EvaluationDataset):
        valid = {c.value for c in NeedCategory}
        for case in eval_dataset.cases:
            for need in case.known_needs:
                assert need in valid, (
                    f"Case {case.case_id}: unknown need category '{need}'"
                )

    def test_expected_resource_ids_reference_real_resources(
        self, eval_dataset: EvaluationDataset, resource_kb: ResourceKB
    ):
        """Already validated at load time, but re-assert for clarity."""
        valid_ids = {r.resource_id for r in resource_kb.resources}
        for case in eval_dataset.cases:
            for rid in case.expected_resource_ids:
                assert rid in valid_ids, (
                    f"Case {case.case_id}: expected_resource_id '{rid}' not in KB"
                )

    def test_contradiction_cases_have_contradictions(self, eval_dataset: EvaluationDataset):
        """Cases categorized as 'contradiction' should have contradiction entries."""
        contradiction_cases = [
            c for c in eval_dataset.cases if "contradiction" in c.category
        ]
        for case in contradiction_cases:
            assert len(case.contradictions) > 0, (
                f"Case {case.case_id} is categorized 'contradiction' but has none"
            )


class TestEvaluationLoaderErrorHandling:
    def test_missing_file_raises_error(self, tmp_path: Path):
        with pytest.raises(DataLoadError, match="not found"):
            load_evaluation_cases(tmp_path / "missing.json")

    def test_malformed_json_raises_error(self, tmp_path: Path):
        bad = tmp_path / "bad.json"
        bad.write_text("{nope", encoding="utf-8")
        with pytest.raises(DataLoadError, match="Invalid JSON"):
            load_evaluation_cases(bad)

    def test_missing_cases_key_raises_error(self, tmp_path: Path):
        no_key = tmp_path / "no_key.json"
        no_key.write_text('{"dataset_version": "v1.0"}', encoding="utf-8")
        with pytest.raises(DataLoadError, match="missing 'cases' key"):
            load_evaluation_cases(no_key)

    def test_invalid_need_category_raises_error(self, tmp_path: Path):
        bad_case = tmp_path / "bad_need.json"
        data = {
            "dataset_version": "v1.0",
            "case_count": 1,
            "cases": [
                {
                    "case_id": "BAD-001",
                    "title": "Bad",
                    "narrative": "Some narrative",
                    "known_facts": {"location": "Pune"},
                    "known_needs": ["teleportation"],  # Invalid category
                }
            ],
        }
        bad_case.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(DataLoadError, match="validation failed"):
            load_evaluation_cases(bad_case)

    def test_bad_expected_resource_cross_ref_raises_error(self, tmp_path: Path):
        case_file = tmp_path / "cross_ref.json"
        data = {
            "dataset_version": "v1.0",
            "case_count": 1,
            "cases": [
                {
                    "case_id": "XREF-001",
                    "title": "Cross ref test",
                    "narrative": "Some narrative",
                    "known_facts": {"location": "Pune"},
                    "known_needs": ["employment"],
                    "expected_resource_ids": ["NONEXISTENT-RES"],
                }
            ],
        }
        case_file.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(DataLoadError, match="not found in resource KB"):
            load_evaluation_cases(case_file, valid_resource_ids={"RES-EMP-001"})
