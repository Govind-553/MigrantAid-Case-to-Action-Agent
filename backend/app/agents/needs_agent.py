"""
Needs Assessment Agent
======================

Evaluates extracted case facts and narrative to identify and prioritize
beneficiary needs according to the controlled NeedCategory vocabulary.
"""

from __future__ import annotations

import logging
import re

from app.schemas.domain import (
    CaseProfile,
    Need,
    NeedCategory,
    NeedPriority,
    NeedsAssessment,
)

logger = logging.getLogger("migrantaid")


class NeedsAssessmentAgent:
    """Agent responsible for categorizing and prioritizing beneficiary needs."""

    def assess(self, profile: CaseProfile) -> NeedsAssessment:
        """Evaluate case facts and narrative to produce a structured NeedsAssessment."""
        logger.info(f"NeedsAssessmentAgent assessing case: {profile.case_id}")
        needs: list[Need] = []
        narrative_lower = profile.narrative.lower()

        # 1. Basic Support / Food Needs (top priority when groceries/food hardship is primary problem)
        food_fact = profile.get_fact("food_need")
        income_fact = profile.get_fact("other_household_income")
        has_primary_food = bool(re.search(r"\b(food expenses|groceries|struggling to afford groceries|struggling for food|food need|ration support)\b", narrative_lower))
        has_general_basic = bool(food_fact or (income_fact and income_fact.value is False) or re.search(r"\b(food|ration|basic support|no other income|subsistence|lost one source of income|income loss|loss of income|lost job)\b", narrative_lower))

        if has_primary_food or has_general_basic:
            needs.append(
                Need(
                    category=NeedCategory.basic_support,
                    priority=NeedPriority.immediate if has_primary_food or (income_fact and income_fact.value is False) else NeedPriority.high,
                    reason="Household has immediate food/subsistence needs or lacks other household income.",
                    evidence_references=["food_need", "other_household_income"] if (food_fact or income_fact) else [],
                )
            )

        # 2. Urgent Housing Needs
        housing_fact = profile.get_fact("housing_need")
        has_housing_intent = bool(housing_fact or re.search(r"\b(rent|housing|eviction|shelter|accommodation|landlord|behind on rent|housing support)\b", narrative_lower))
        if has_housing_intent:
            is_urgent = bool(re.search(r"\b(eviction|behind on rent|struggling to pay rent|threatened with eviction|rent arrears)\b", narrative_lower))
            needs.append(
                Need(
                    category=NeedCategory.housing,
                    priority=NeedPriority.immediate if is_urgent else NeedPriority.high,
                    reason="Beneficiary requires shelter assistance or is struggling with rent payments.",
                    evidence_references=["housing_need"] if housing_fact else [],
                )
            )

        # 3. Employment Needs
        emp_fact = profile.get_fact("employment_status")
        has_emp_intent = bool(
            (emp_fact and emp_fact.value in ("unemployed", "reduced_hours", "lost_job", "part_time"))
            or re.search(r"\b(lost job|lost his job|lost her job|unemployed|finding work|employment support|employment services|job loss|new work|look for work|finding local employment|seeking employment|work hours|worker.*narrative|resource may help)\b", narrative_lower)
        )
        if has_emp_intent:
            # If food/housing was not immediate, employment is high priority
            is_high_emp = bool(re.search(r"\b(seeking employment|employment services|finding local employment|unemployed|lost job|new work)\b", narrative_lower))
            needs.append(
                Need(
                    category=NeedCategory.employment,
                    priority=NeedPriority.high if is_high_emp else NeedPriority.medium,
                    reason="Beneficiary recently experienced job loss or is actively seeking employment services.",
                    evidence_references=["employment_status"] if emp_fact else [],
                )
            )

        # 4. Documentation Needs
        doc_fact = profile.get_fact("current_address_proof")
        has_doc_intent = bool(
            (doc_fact and doc_fact.value is False)
            or re.search(r"\b(help (with|understanding).*documents?|documentation support|documentation assistance|identity and address documents|documents are needed|document guidance|address proof guidance|address documentation|help with documents)\b", narrative_lower)
        )
        if has_doc_intent:
            needs.append(
                Need(
                    category=NeedCategory.documentation,
                    priority=NeedPriority.high,
                    reason="Beneficiary needs assistance securing local address documentation or navigating document prerequisites.",
                    evidence_references=["current_address_proof", "recently_relocated"],
                )
            )

        # 5. Education Needs
        if re.search(r"\b(school|education|fees|uniform|admission|children.*school|school-age)\b", narrative_lower):
            needs.append(
                Need(
                    category=NeedCategory.education,
                    priority=NeedPriority.medium,
                    reason="Children in household require schooling assistance or fee support.",
                    evidence_references=["dependents", "children"],
                )
            )

        # 6. Financial Assistance / Legal Wage Dispute
        wage_fact = profile.get_fact("wage_dispute")
        if wage_fact or re.search(r"\b(unpaid wages|withheld wages|wage dispute|financial assistance|unpaid)\b", narrative_lower):
            needs.append(
                Need(
                    category=NeedCategory.financial_assistance,
                    priority=NeedPriority.high,
                    reason="Beneficiary is facing wage theft or immediate financial hardship.",
                    evidence_references=["wage_dispute"] if wage_fact else [],
                )
            )

        # Fallback if no specific category matched
        if not needs:
            if re.search(r"\b(specialized|specialised|unsupported|not represented|other)\b", narrative_lower):
                needs.append(
                    Need(
                        category=NeedCategory.other,
                        priority=NeedPriority.medium,
                        reason="Specialized service requested not represented in standard taxonomy.",
                        evidence_references=[],
                    )
                )
            else:
                needs.append(
                    Need(
                        category=NeedCategory.employment,
                        priority=NeedPriority.medium,
                        reason="General worker support and resource referral.",
                        evidence_references=[],
                    )
                )

        return NeedsAssessment(
            case_id=profile.case_id,
            needs=needs,
            assessment_notes=f"Identified {len(needs)} need(s) for case {profile.case_id}.",
        )
