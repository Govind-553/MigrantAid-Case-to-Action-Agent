"""
Phase 4: Baseline Service Unit and Integration Tests
===================================================

Tests that the single-prompt baseline:
- formats prompt context correctly
- parses model responses reliably
- produces valid BaselineOutput structures for all 20 cases
- can be executed offline and via CLI
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.schemas.domain import NeedCategory
from app.services.baseline import BaselineOutput, BaselineService
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


@pytest.fixture
def baseline_service():
    return BaselineService()


class TestBaselinePromptAndFormatting:
    def test_format_resources_context(self, baseline_service: BaselineService, resource_kb):
        formatted = baseline_service.format_resources_context(resource_kb.resources)
        assert isinstance(formatted, str)
        parsed = json.loads(formatted)
        assert len(parsed) == resource_kb.resource_count
        assert "resource_id" in parsed[0]
        assert "category" in parsed[0]
        assert "requirements" in parsed[0]


class TestBaselineJSONParsing:
    def test_parse_clean_json(self, baseline_service: BaselineService):
        raw = '{"primary_need": "employment", "recommended_resource_ids": ["RES-001"]}'
        parsed = baseline_service._parse_llm_json(raw)
        assert parsed["primary_need"] == "employment"
        assert parsed["recommended_resource_ids"] == ["RES-001"]

    def test_parse_markdown_codeblock_json(self, baseline_service: BaselineService):
        raw = '```json\n{"primary_need": "housing", "recommended_resource_ids": []}\n```'
        parsed = baseline_service._parse_llm_json(raw)
        assert parsed["primary_need"] == "housing"

    def test_parse_json_with_surrounding_commentary(self, baseline_service: BaselineService):
        raw = 'Here is the analysis:\n{"primary_need": "basic_support", "next_step": "apply"}\nHope this helps!'
        parsed = baseline_service._parse_llm_json(raw)
        assert parsed["primary_need"] == "basic_support"
        assert parsed["next_step"] == "apply"


class TestBaselineExecution:
    def test_run_single_case_offline(self, baseline_service: BaselineService, eval_dataset, resource_kb):
        case_0 = eval_dataset.cases[0]
        output = baseline_service.run_case(case_0, resource_kb, force_offline=True)

        assert isinstance(output, BaselineOutput)
        assert output.case_id == case_0.case_id
        assert output.primary_need in {c.value for c in NeedCategory}
        assert output.latency_ms >= 0.0
        assert output.raw_response != ""

    def test_run_all_20_cases_offline(self, baseline_service: BaselineService, eval_dataset, resource_kb):
        outputs = baseline_service.run_all(eval_dataset.cases, resource_kb, force_offline=True)

        assert len(outputs) == 20
        case_ids = [o.case_id for o in outputs]
        assert case_ids == [c.case_id for c in eval_dataset.cases]

    def test_baseline_preserves_case_identities(self, baseline_service: BaselineService, eval_dataset, resource_kb):
        outputs = baseline_service.run_all(eval_dataset.cases, resource_kb, force_offline=True)
        for i, o in enumerate(outputs):
            assert o.case_id == eval_dataset.cases[i].case_id


class TestBaselineRunnerCLI:
    def test_baseline_runner_saves_valid_json(self, tmp_path: Path, eval_dataset, resource_kb):
        out_file = tmp_path / "baseline_out.json"
        service = BaselineService()
        outputs = service.run_all(eval_dataset.cases, resource_kb, force_offline=True)

        results_dict = {
            "dataset_version": eval_dataset.dataset_version,
            "system": "baseline",
            "model": service.model_name,
            "case_count": len(outputs),
            "total_latency_ms": sum(o.latency_ms for o in outputs),
            "avg_latency_ms": sum(o.latency_ms for o in outputs) / len(outputs) if outputs else 0.0,
            "results": [o.model_dump() for o in outputs],
        }

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(results_dict, f, indent=2)

        assert out_file.exists()
        with open(out_file, encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["system"] == "baseline"
        assert loaded["case_count"] == 20
        assert len(loaded["results"]) == 20
