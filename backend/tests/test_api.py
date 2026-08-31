"""
REST API Endpoints Unit and Integration Tests
=============================================

Tests all FastAPI routes for case management, fact corrections,
human reviews, resource catalog, and evaluation comparison benchmarks.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestCaseEndpoints:
    def test_create_case_success(self, client: TestClient):
        payload = {
            "narrative": "A migrant worker in Pune recently lost his job. He has two children and says the household currently has no other income. He has an identity document.",
            "case_id": "CASE-TEST-001",
        }
        response = client.post("/api/cases", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["case_id"] == "CASE-TEST-001"
        assert data["profile"]["case_id"] == "CASE-TEST-001"
        assert len(data["profile"]["facts"]) > 0
        assert len(data["needs_assessment"]["needs"]) > 0
        assert len(data["verified_recommendations"]) > 0
        assert len(data["action_plan"]["actions"]) > 0
        assert data["quality_report"]["passed"] is True
        assert len(data["trajectory"]) > 0

    def test_get_case_success(self, client: TestClient):
        # Retrieve previously created case
        response = client.get("/api/cases/CASE-TEST-001")
        assert response.status_code == 200
        assert response.json()["case_id"] == "CASE-TEST-001"

    def test_get_nonexistent_case_returns_404(self, client: TestClient):
        response = client.get("/api/cases/NONEXISTENT-CASE-999")
        assert response.status_code == 404

    def test_list_cases(self, client: TestClient):
        response = client.get("/api/cases")
        assert response.status_code == 200
        data = response.json()
        assert "cases" in data
        assert len(data["cases"]) > 0

    def test_update_case_facts_triggers_reverification(self, client: TestClient):
        # Update facts on CASE-TEST-001
        updated_facts = [
            {"field": "employment_status", "value": "employed", "status": "explicit", "source": "caseworker_edit"},
            {"field": "location", "value": "Pune", "status": "explicit", "source": "caseworker_edit"},
        ]
        response = client.put("/api/cases/CASE-TEST-001/facts", json={"facts": updated_facts})
        assert response.status_code == 200
        data = response.json()

        # Check that facts updated
        fact_fields = [f["field"] for f in data["profile"]["facts"]]
        assert "employment_status" in fact_fields
        # Trajectory should include human edit event
        agents = [e["agent"] for e in data["trajectory"]]
        assert "Caseworker" in agents

    def test_submit_human_review_approval(self, client: TestClient):
        payload = {
            "decision": "approved",
            "reviewer_notes": "All documents verified by frontline supervisor.",
        }
        response = client.post("/api/cases/CASE-TEST-001/review", json=payload)
        assert response.status_code == 200
        data = response.json()

        # When a caseworker approves referrals, the workflow state must use
        assert data["workflow_state"] == "REFERRALS_APPROVED"
        assert data["human_review"]["decision"] == "approved"
        assert data["human_review"]["reviewed_at"] is not None
        assert data["human_review"]["reviewer_notes"] == "All documents verified by frontline supervisor."



class TestResourceEndpoints:
    def test_list_resources(self, client: TestClient):
        response = client.get("/api/resources")
        assert response.status_code == 200
        data = response.json()
        assert data["resource_count"] > 0
        assert len(data["resources"]) > 0

    def test_get_resource_by_id(self, client: TestClient):
        response = client.get("/api/resources/RES-EMP-001")
        assert response.status_code == 200
        data = response.json()
        assert data["resource_id"] == "RES-EMP-001"
        assert data["category"] == "employment"

    def test_get_nonexistent_resource_returns_404(self, client: TestClient):
        response = client.get("/api/resources/NONEXISTENT-RES")
        assert response.status_code == 404


class TestEvaluationEndpoints:
    def test_get_baseline_evaluation(self, client: TestClient):
        response = client.get("/api/evaluation/baseline")
        assert response.status_code == 200
        data = response.json()
        assert data["system"] == "baseline"
        assert "summary" in data
        assert data["summary"]["total_cases"] == 20

    def test_get_agent_evaluation(self, client: TestClient):
        response = client.get("/api/evaluation/agent")
        assert response.status_code == 200
        data = response.json()
        assert data["system"] == "agentic"
        assert "summary" in data
        assert data["summary"]["varr_percentage"] > 0.0

    def test_get_evaluation_comparison(self, client: TestClient):
        response = client.get("/api/evaluation/comparison")
        assert response.status_code == 200
        data = response.json()
        assert "baseline_summary" in data
        assert "agentic_summary" in data
        assert "improvements" in data
        assert data["improvements"]["varr_delta_percentage"] >= 0.0
