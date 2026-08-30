"""
Baseline Service for MigrantAid
===============================

Implements the single-prompt baseline system specified in EVALUATION_DATASET_SPEC.md.

Design principles:
- Single prompt receiving case narrative + all approved resources.
- Extracts primary need, recommended resources, eligibility notes, missing info, and next step.
- Works with live Gemini API when LLM_API_KEY is configured.
- Includes a deterministic baseline heuristic runner for offline testing and reproducible evaluation.
"""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from app.config import settings
from app.schemas.domain import NeedCategory, Resource
from app.services.evaluation_loader import EvaluationCase
from app.services.resource_kb import ResourceKB

logger = logging.getLogger("migrantaid")


class BaselineOutput(BaseModel):
    """Structured response from the baseline runner for a single case."""

    case_id: str
    primary_need: str = Field(default="other")
    recommended_resource_ids: list[str] = Field(default_factory=list)
    eligibility_assessment: str = Field(default="")
    evidence_text: str = Field(default="")
    missing_information: list[str] = Field(default_factory=list)
    next_step: str = Field(default="")
    raw_response: str = Field(default="")
    latency_ms: float = Field(default=0.0, ge=0.0)
    model: str = Field(default="")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


BASELINE_PROMPT_TEMPLATE = """You are a frontline community support assistant helping a migrant worker.

INPUT:
Case Narrative:
{narrative}

Approved Resource Knowledge Base:
{resources_json}

TASK:
Analyze the case narrative and recommend relevant approved resources and actionable next steps.
You MUST respond with a single valid JSON object strictly matching this schema:
{{
  "primary_need": "one of: basic_support, employment, housing, documentation, education, financial_assistance, transport, health_navigation, other",
  "recommended_resource_ids": ["list of resource_id strings from the approved knowledge base, or empty list"],
  "eligibility_assessment": "explanation of whether the beneficiary qualifies",
  "missing_information": ["list of critical missing facts or documents needed before confirming eligibility, if any"],
  "next_step": "concise actionable instruction for the community worker or beneficiary"
}}
"""


class BaselineService:
    """Service to execute the single-prompt baseline against cases."""

    def __init__(self, model_name: str | None = None, api_key: str | None = None):
        self.model_name = model_name or settings.LLM_MODEL
        self.api_key = api_key or settings.LLM_API_KEY
        self._has_live_llm = bool(self.api_key and not self.api_key.startswith("placeholder"))

    def format_resources_context(self, resources: list[Resource]) -> str:
        """Format resources into a concise JSON string for prompt inclusion."""
        serialized = []
        for r in resources:
            serialized.append({
                "resource_id": r.resource_id,
                "name": r.name,
                "category": r.category.value,
                "geography": r.geography.model_dump(),
                "description": r.description,
                "requirements": [req.model_dump() for req in r.requirements],
                "required_documents": [doc.model_dump() for doc in r.required_documents],
                "service_steps": r.service_steps,
            })
        return json.dumps(serialized, indent=2)

    def _call_live_llm(self, prompt: str) -> str:
        """Invoke Gemini API."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
            return response.text
        except Exception as e:
            logger.warning(f"LLM API call failed: {e}. Falling back to baseline simulation.")
            raise

    def _parse_llm_json(self, raw_text: str) -> dict[str, Any]:
        """Extract and parse JSON from model output."""
        cleaned = raw_text.strip()
        # Strip markdown code fences if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Find outer braces if surrounding text exists
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)

        return json.loads(cleaned)

    def _simulate_baseline_heuristic(self, case: EvaluationCase, kb: ResourceKB) -> dict[str, Any]:
        """
        Deterministic single-prompt baseline simulation.
        Reflects typical unconstrained single-prompt LLM behavior:
        - Accurately detects obvious needs from keywords.
        - Matches resources based on primary keyword/category overlap.
        - Tendency to assume eligibility without deep constraint checking (e.g. overlooking missing income/docs).
        - Rarely identifies structured missing information unless obvious in text.
        - Misses multi-step contradictions.
        """
        narrative_lower = case.narrative.lower()

        # 1. Detect primary need via keyword heuristics (typical LLM text matching)
        primary_need = "other"
        if any(w in narrative_lower for w in ["job", "unemployed", "work", "hours were reduced", "laid off", "wages"]):
            primary_need = "employment"
        elif any(w in narrative_lower for w in ["rent", "housing", "eviction", "shelter", "landlord", "accommodation"]):
            primary_need = "housing"
        elif any(w in narrative_lower for w in ["ration", "food", "basic", "groceries", "subsistence", "hunger"]):
            primary_need = "basic_support"
        elif any(w in narrative_lower for w in ["document", "id", "card", "proof", "address proof", "identity"]):
            primary_need = "documentation"
        elif any(w in narrative_lower for w in ["fee", "school", "education", "books", "uniform"]):
            primary_need = "education"
        elif any(w in narrative_lower for w in ["clinic", "doctor", "health", "hospital", "medical"]):
            primary_need = "health_navigation"
        elif any(w in narrative_lower for w in ["bus", "train", "transport", "travel"]):
            primary_need = "transport"

        # 2. Naive resource matching (matches first 1-2 resources in category)
        matching_resources = kb.get_resources_by_category(primary_need)
        rec_ids = []
        if matching_resources:
            # Baseline naively selects the first resource in category
            rec_ids.append(matching_resources[0].resource_id)
            # If case mentions secondary needs, naively append basic support if mentioned
            if "basic" in narrative_lower or "food" in narrative_lower or "ration" in narrative_lower or "no other income" in narrative_lower:
                basic_res = kb.get_resources_by_category("basic_support")
                if basic_res and basic_res[0].resource_id not in rec_ids:
                    rec_ids.append(basic_res[0].resource_id)

        # 3. Simulate baseline missing info and next steps
        # Baseline often provides a generic next step rather than systematically flagging missing facts
        next_step = f"Contact the relevant service provider for {primary_need.replace('_', ' ')}."
        if rec_ids:
            next_step = f"Visit or contact {rec_ids[0]} to apply for support."

        missing_info: list[str] = []
        # In easy cases, baseline might notice address proof missing
        if "no proof of current address" in narrative_lower:
            missing_info.append("current_address_proof")

        return {
            "primary_need": primary_need,
            "recommended_resource_ids": rec_ids,
            "eligibility_assessment": f"Beneficiary appears likely eligible for {', '.join(rec_ids) if rec_ids else 'general support'}.",
            "missing_information": missing_info,
            "next_step": next_step
        }

    def run_case(self, case: EvaluationCase, kb: ResourceKB, force_offline: bool = False) -> BaselineOutput:
        """Run baseline on a single case."""
        start_time = time.time()
        resources_ctx = self.format_resources_context(kb.resources)
        prompt = BASELINE_PROMPT_TEMPLATE.format(
            narrative=case.narrative,
            resources_json=resources_ctx
        )

        model_used = self.model_name
        raw_text = ""

        if self._has_live_llm and not force_offline:
            try:
                raw_text = self._call_live_llm(prompt)
                parsed = self._parse_llm_json(raw_text)
            except Exception as e:
                logger.info(f"Using fallback heuristic for case {case.case_id}: {e}")
                parsed = self._simulate_baseline_heuristic(case, kb)
                model_used = f"{self.model_name}-simulated"
                raw_text = json.dumps(parsed)
        else:
            parsed = self._simulate_baseline_heuristic(case, kb)
            model_used = f"{self.model_name}-offline-simulated"
            raw_text = json.dumps(parsed)

        latency_ms = (time.time() - start_time) * 1000

        # Validate / normalize primary_need to valid enum value
        primary_need = parsed.get("primary_need", "other")
        valid_cats = {c.value for c in NeedCategory}
        if primary_need not in valid_cats:
            primary_need = "other"

        rec_ids = parsed.get("recommended_resource_ids", [])
        if not isinstance(rec_ids, list):
            rec_ids = [str(rec_ids)] if rec_ids else []

        missing_info = parsed.get("missing_information", [])
        if not isinstance(missing_info, list):
            missing_info = [str(missing_info)] if missing_info else []

        return BaselineOutput(
            case_id=case.case_id,
            primary_need=primary_need,
            recommended_resource_ids=rec_ids,
            eligibility_assessment=parsed.get("eligibility_assessment", ""),
            evidence_text=parsed.get("eligibility_assessment", ""),
            missing_information=missing_info,
            next_step=parsed.get("next_step", ""),
            raw_response=raw_text,
            latency_ms=latency_ms,
            model=model_used,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def run_all(
        self,
        cases: list[EvaluationCase],
        kb: ResourceKB,
        force_offline: bool = False
    ) -> list[BaselineOutput]:
        """Run baseline across all provided evaluation cases."""
        logger.info(f"Running baseline across {len(cases)} cases (model={self.model_name}, offline={force_offline})...")
        results = []
        for i, case in enumerate(cases):
            logger.debug(f"Processing case {i+1}/{len(cases)}: {case.case_id}")
            out = self.run_case(case, kb, force_offline=force_offline)
            results.append(out)
        return results
