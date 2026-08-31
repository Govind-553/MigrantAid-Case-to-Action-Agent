"""
Unit tests for Gemini Integration with google.genai SDK
========================================================

Verifies:
- Migration to google.genai SDK.
- Settings reads LLM_MODEL correctly.
- IntakeAgent initializes Gemini client and generates content.
- LLM API call failure safely falls back to deterministic heuristic.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from app.agents.intake_agent import IntakeAgent
from app.config import settings
from app.schemas.domain import CaseProfile
from app.services.baseline import BaselineService


class TestGeminiIntegration:
    def test_sdk_import_and_config(self):
        """Verify that google.genai SDK can be imported and settings model is read."""
        from google import genai

        assert hasattr(genai, "Client")
        assert settings.LLM_MODEL == os.getenv("LLM_MODEL", "gemini-3.6-flash")

    def test_intake_agent_with_live_llm(self):
        """Verify IntakeAgent invokes google.genai Client successfully when configured."""
        if not settings.LLM_API_KEY or settings.LLM_API_KEY.startswith("placeholder"):
            pytest.skip("LLM_API_KEY not configured for live LLM test.")

        agent = IntakeAgent()
        assert agent._has_llm is True

        narrative = "A migrant worker in Pune recently lost his job. He has two children and says the household currently has no other income. He has an identity document and a bank account."
        profile = agent.process("CASE-LIVE-TEST-001", narrative, force_heuristic=False)

        assert isinstance(profile, CaseProfile)
        assert profile.case_id == "CASE-LIVE-TEST-001"
        assert profile.has_explicit_fact("location")
        assert profile.get_fact("location").value == "Pune"
        assert profile.get_fact("children").value == 2

    def test_intake_agent_llm_fallback_on_error(self):
        """Verify that IntakeAgent falls back to deterministic heuristic if LLM fails."""
        agent = IntakeAgent(api_key="invalid_test_key", model_name="gemini-3.6-flash")

        with patch("google.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.models.generate_content.side_effect = Exception("API Error")
            mock_client_cls.return_value = mock_client

            narrative = "A migrant worker in Pune recently lost his job. He has two children."
            profile = agent.process("CASE-FALLBACK-001", narrative, force_heuristic=False)

            assert isinstance(profile, CaseProfile)
            assert profile.get_fact("children").value == 2
            assert profile.get_fact("location").value == "Pune"

    def test_baseline_service_live_llm(self):
        """Verify BaselineService uses google.genai Client."""
        if not settings.LLM_API_KEY or settings.LLM_API_KEY.startswith("placeholder"):
            pytest.skip("LLM_API_KEY not configured.")

        service = BaselineService()
        assert service._has_live_llm is True
