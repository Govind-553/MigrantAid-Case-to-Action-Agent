"""
Tests for the health check endpoint and basic application startup.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthCheck:
    def test_health_check_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_ok_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_check_content_type(self, client):
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]


class TestErrorHandling:
    def test_not_found_returns_404(self, client):
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_not_found_returns_json(self, client):
        response = client.get("/nonexistent-endpoint")
        assert "detail" in response.json()
