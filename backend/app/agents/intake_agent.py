"""
Intake & Fact Extraction Agent
==============================

Transforms messy natural-language case descriptions into structured CaseProfile objects.

Responsibilities:
- Extract semantic case facts with provenance (explicit, inferred, unknown, conflicting).
- Detect and represent contradictions.
- Identify initial missing information.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.config import settings
from app.schemas.domain import (
    CaseFact,
    CaseProfile,
    CaseWorkflowState,
    Contradiction,
    FactStatus,
)

logger = logging.getLogger("migrantaid")

INTAKE_PROMPT_TEMPLATE = """You are a frontline caseworker intake assistant.
Analyze the following migrant worker case narrative and extract structured facts.

Case Narrative:
{narrative}

Extract:
1. "facts": list of objects, each having:
   - "field": string semantic field name (e.g. "location", "employment_status", "dependents", "other_household_income", "identity_document", "bank_account", "housing_need", "food_need", "documentation_need", "current_address_proof", "children", "wage_dispute")
   - "value": extracted value (string, integer, float, or boolean)
   - "status": "explicit" if directly stated, "inferred" if deduced from context
   - "notes": optional context
2. "missing_information": list of field names that are important but missing from the narrative
3. "contradictions": list of objects if any conflicting information is found:
   - "description": summary of conflict
   - "fact_a": first conflicting statement
   - "fact_b": second conflicting statement

Respond strictly with a valid JSON object matching these keys.
"""


class IntakeAgent:
    """Agent responsible for initial case parsing and fact extraction."""

    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model_name = model_name or settings.LLM_MODEL
        self._has_llm = bool(self.api_key and not self.api_key.startswith("placeholder"))

    def _extract_heuristic(self, narrative: str) -> dict[str, Any]:
        """
        High-precision deterministic extraction for casework narratives.
        Extracts key demographic, economic, and logistical facts.
        """
        lower = narrative.lower()
        facts: list[dict[str, Any]] = []
        missing: list[str] = []
        contradictions: list[dict[str, Any]] = []

        # 1. Location extraction & contradictions
        has_pune = bool(re.search(r"\bpune\b", lower))
        has_mumbai = bool(re.search(r"\bmumbai\b", lower))
        has_delhi = bool(re.search(r"\bdelhi\b", lower))

        if has_pune and has_mumbai and ("registered in mumbai" in lower or "lives in pune" in lower or "staying in pune" in lower):
            facts.append({"field": "location", "value": "conflicting_pune_and_mumbai", "status": "conflicting"})
            contradictions.append({
                "description": "Location conflict between Pune residence and Mumbai registration/workplace",
                "fact_a": "narrative mentions Pune",
                "fact_b": "narrative mentions Mumbai",
            })
        elif has_pune:
            facts.append({"field": "location", "value": "Pune", "status": "explicit"})
        elif has_mumbai:
            facts.append({"field": "location", "value": "Mumbai", "status": "explicit"})
        elif has_delhi:
            facts.append({"field": "location", "value": "Delhi", "status": "explicit"})
        else:
            missing.append("location")

        # 2. Employment status & contradictions
        is_unemployed = bool(re.search(r"\b(lost (his|her)?\s*job|unemployed|without work|lost job|laid off|job loss|seeking employment|help finding work|new work|looking for work)\b", lower))
        is_part_time = bool(re.search(r"\b(part[- ]time|few hours a week|casual shifts|working part-time)\b", lower))
        is_reduced = bool(re.search(r"\b(reduced|hours were reduced|pay cut)\b", lower))
        has_wage_theft = bool(re.search(r"\b(unpaid|withheld|not paid|wages withheld|owed wages|wage dispute)\b", lower))

        if ("unemployed" in lower or "lost" in lower) and is_part_time:
            # Contradiction detected!
            facts.append({
                "field": "employment_status",
                "value": "conflicting_unemployed_and_part_time",
                "status": "conflicting",
                "notes": "Narrative mentions both being unemployed and having part-time work",
            })
            contradictions.append({
                "description": "Employment status contradiction between unemployed and part-time work",
                "fact_a": "narrative mentions losing job / unemployed",
                "fact_b": "narrative mentions part-time work / casual shifts",
            })
        elif is_unemployed:
            facts.append({"field": "employment_status", "value": "unemployed", "status": "explicit"})
        elif is_reduced:
            facts.append({"field": "employment_status", "value": "reduced_hours", "status": "explicit"})
        elif is_part_time:
            facts.append({"field": "employment_status", "value": "part_time", "status": "explicit"})

        if has_wage_theft:
            facts.append({"field": "wage_dispute", "value": True, "status": "explicit"})

        # Prior registration (for RES-EMP-002)
        if re.search(r"\b(prior registration|previously registered|registered before|already registered)\b", lower):
            facts.append({"field": "prior_registration", "value": True, "status": "explicit"})
        elif re.search(r"\b(never registered|not registered before|first time)\b", lower):
            facts.append({"field": "prior_registration", "value": False, "status": "explicit"})
        elif is_unemployed:
            missing.append("prior_registration_status")

        # 3. Dependents & Children
        dep_match = re.search(r"(\d+)\s+(?:children|kids|dependents|family members|school-age children)", lower)
        if dep_match:
            count = int(dep_match.group(1))
            facts.append({"field": "dependents", "value": count, "status": "explicit"})
            facts.append({"field": "children", "value": count, "status": "explicit"})
        elif re.search(r"\b(family|children|kids|spouse|couple)\b", lower):
            facts.append({"field": "dependents", "value": "family", "status": "inferred"})
            facts.append({"field": "children", "value": 1, "status": "inferred"})

        if re.search(r"\b(school|school-age|education|admission|fees)\b", lower):
            if not re.search(r"\b(enrolled|admitted|currently in school)\b", lower):
                missing.append("children_school_status")

        # 4. Income & Household Income
        if re.search(r"\b(no other income|no other household income|sole earner without other income|no other earner)\b", lower):
            facts.append({"field": "other_household_income", "value": False, "status": "explicit"})
        else:
            if not re.search(r"\b(earns \d+|income is \d+|rs\.?\s*\d+)\b", lower):
                missing.append("current_household_income")

        if re.search(r"\bspouse\b", lower) and not re.search(r"\bspouse (works|employed|unemployed)\b", lower):
            missing.append("spouse_employment_status")

        # 5. Identity Documents & Bank Account
        if re.search(r"\b(identity document|id proof|aadhar|has an identity document|identity card|id card|one identity document)\b", lower):
            facts.append({"field": "identity_document", "value": True, "status": "explicit"})
        else:
            missing.append("identity_document")

        if re.search(r"\bbank account\b", lower):
            facts.append({"field": "bank_account", "value": True, "status": "explicit"})

        # 6. Documentation Need & Address Proof
        has_doc_need = bool(re.search(r"\b(documentation|help with documents|understanding which.*documents|documents are needed|address documents|document checklist|identity and address)\b", lower))
        if has_doc_need:
            facts.append({"field": "documentation_need", "value": True, "status": "explicit"})

        if re.search(r"\b(no proof of current address|no current address proof|no address proof|without address proof|no proof of address)\b", lower):
            facts.append({"field": "current_address_proof", "value": False, "status": "explicit"})
            missing.append("current_address_proof")
        elif re.search(r"\b(has address proof|address proof available|proof of address)\b", lower):
            facts.append({"field": "current_address_proof", "value": True, "status": "explicit"})

        # 7. Food & Basic Support Need
        if re.search(r"\b(food|ration|basic support|groceries|food expenses|struggling for food|food need)\b", lower) or ("no other income" in lower and is_unemployed):
            facts.append({"field": "food_need", "value": True, "status": "explicit"})

        # 8. Housing Need & Rent Arrears
        if re.search(r"\b(rent|housing|eviction|shelter|accommodation|landlord|behind on rent|housing support)\b", lower):
            facts.append({"field": "housing_need", "value": True, "status": "explicit"})
            if re.search(r"\b(struggling to pay rent|behind on rent|rent arrears|rent overdue|eviction)\b", lower):
                facts.append({"field": "rent_overdue", "value": True, "status": "explicit"})
            if "housing_status" not in lower and "rent_amount" not in lower:
                missing.append("housing_status_or_rent_information")

        # 9. Relocation / Temporary Residence
        if re.search(r"\b(recently moved|relocated|recently relocated|temporary|staying in pune temporarily|moved several times)\b", lower):
            facts.append({"field": "recently_relocated", "value": True, "status": "explicit"})
            if "permanent address" in lower or "temporary" in lower:
                missing.append("current_residence_status")
                missing.append("relevant_address_documentation")

        return {
            "facts": facts,
            "missing_information": list(set(missing)),
            "contradictions": contradictions,
        }

    def process(self, case_id: str, narrative: str, force_heuristic: bool = False) -> CaseProfile:
        """Run intake analysis on case narrative and return a structured CaseProfile."""
        logger.info(f"IntakeAgent processing case: {case_id}")

        data = None
        if self._has_llm and not force_heuristic:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(self.model_name)
                prompt = INTAKE_PROMPT_TEMPLATE.format(narrative=narrative)
                resp = model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
                )
                data = json.loads(resp.text)
            except Exception as e:
                logger.warning(f"Intake LLM call failed: {e}. Using deterministic heuristic.")
                data = self._extract_heuristic(narrative)
        else:
            data = self._extract_heuristic(narrative)

        # Build CaseFact models
        facts: list[CaseFact] = []
        for raw_fact in data.get("facts", []):
            try:
                status_val = raw_fact.get("status", "explicit")
                if status_val not in [s.value for s in FactStatus]:
                    status_val = "explicit"
                facts.append(
                    CaseFact(
                        field=raw_fact["field"],
                        value=raw_fact["value"],
                        status=FactStatus(status_val),
                        source="user_input",
                        notes=raw_fact.get("notes"),
                    )
                )
            except Exception as e:
                logger.warning(f"Skipping invalid fact {raw_fact}: {e}")

        # Build Contradictions
        contradictions: list[Contradiction] = []
        for raw_c in data.get("contradictions", []):
            try:
                contradictions.append(
                    Contradiction(
                        description=raw_c.get("description", "Contradiction detected in narrative"),
                        fact_a=raw_c.get("fact_a", "statement 1"),
                        fact_b=raw_c.get("fact_b", "statement 2"),
                        severity="high",
                    )
                )
            except Exception as e:
                logger.warning(f"Skipping invalid contradiction {raw_c}: {e}")

        missing_info = data.get("missing_information", [])
        if not isinstance(missing_info, list):
            missing_info = []

        return CaseProfile(
            case_id=case_id,
            narrative=narrative,
            facts=facts,
            missing_information=missing_info,
            contradictions=contradictions,
            workflow_state=CaseWorkflowState.intake_review,
        )
