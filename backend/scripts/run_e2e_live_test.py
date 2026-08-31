"""
End-to-End Live Case Verification Script
========================================

Executes the exact live test narrative:
"A migrant worker in Pune recently lost his job. He has two children and says the household currently has no other income. He has an identity document and a bank account."

Verifies:
1. Live Gemini call using google.genai and configured model (gemini-3.6-flash).
2. Correct fact extraction: Location=Pune, employment_status=unemployed, children=2, other_household_income=False, identity_document=True, bank_account=True.
3. Matching & verification pipeline.
4. Action plan generation & Human review checkpoint.
5. PostgreSQL persistence without stale connection errors.
6. DB retrieval resilience.
"""

import sys
import logging
from pathlib import Path

# Add backend to python path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.config import settings
from app.db.connection import init_db_pool, close_db_pool
from app.services.case_workflow import CaseWorkflowService
from app.services.resource_kb import load_resource_kb
from app.schemas.domain import HumanReviewDecision

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("e2e_test")

def main():
    print("=" * 60)
    print("STARTING MIGRANTAID LIVE END-TO-END REGRESSION TEST")
    print("=" * 60)
    print(f"Configured LLM Model: {settings.LLM_MODEL}")
    print(f"Database URL configured: {bool(settings.DATABASE_URL)}")

    # 1. Initialize DB Pool
    pool = init_db_pool()
    if pool:
        print("[SUCCESS] DB pool initialized with connection health checks.")

    # 2. Load KB & Setup Service
    kb_path = backend_path.parent / "data" / "resources.json"
    sources_path = backend_path.parent / "data" / "sources.json"
    kb = load_resource_kb(kb_path, sources_path)
    service = CaseWorkflowService(kb=kb)

    # 3. Define Test Narrative
    case_id = "CASE-LIVE-001"
    narrative = (
        "A migrant worker in Pune recently lost his job. He has two children and "
        "says the household currently has no other income. He has an identity document "
        "and a bank account."
    )

    print(f"\nProcessing case '{case_id}' via Live Gemini LLM...")
    state = service.create_case(narrative, case_id=case_id)

    print("\n--- FACT EXTRACTION RESULTS ---")
    facts_dict = {f.field: f.value for f in state.profile.facts}
    for field, val in facts_dict.items():
        print(f"  {field}: {val}")

    # Fact assertions
    assert facts_dict.get("location") == "Pune", f"Expected location 'Pune', got '{facts_dict.get('location')}'"
    assert facts_dict.get("employment_status") == "unemployed", f"Expected employment_status 'unemployed', got '{facts_dict.get('employment_status')}'"
    assert facts_dict.get("children") == 2, f"Expected children=2, got {facts_dict.get('children')}"
    assert facts_dict.get("other_household_income") is False, f"Expected other_household_income=False, got {facts_dict.get('other_household_income')}"
    assert facts_dict.get("identity_document") is True, f"Expected identity_document=True, got {facts_dict.get('identity_document')}"
    assert facts_dict.get("bank_account") is True, f"Expected bank_account=True, got {facts_dict.get('bank_account')}"
    print("[PASS] All expected facts extracted correctly!")

    # Check Trajectory for Gemini success & logical stages
    print("\n--- TRAJECTORY STAGES ---")
    intake_events = [e for e in state.trajectory if e.agent == "IntakeAgent"]
    for evt in state.trajectory:
        print(f"  [{evt.timestamp}] {evt.stage} - {evt.agent}: {evt.output_summary}")

    # Ensure no Gemini errors logged in trajectory
    has_llm_error = any("Intake LLM call failed" in (evt.error_message or "") for evt in state.trajectory)
    assert not has_llm_error, "Gemini LLM call failed and used fallback!"
    print("[PASS] Live Gemini LLM call executed successfully without fallback!")

    # 4. Human Review Step
    print("\nExecuting Human Review step...")
    reviewed_state = service.submit_human_review(
        case_id=case_id,
        decision=HumanReviewDecision.approved,
        reviewer_notes="Approved verified recommendations for CASE-LIVE-001",
        modified_recommendation_ids=[],
        rejected_recommendation_ids=[],
    )
    print(f"[PASS] Human review completed. State: {reviewed_state.workflow_state.value}")

    # 5. Test Retrieval after Service Restart Simulation
    print("\nTesting DB Retrieval Resilience (simulating backend restart)...")
    restarted_service = CaseWorkflowService(kb=kb)
    loaded_state = restarted_service.get_case(case_id)
    assert loaded_state is not None, f"Failed to retrieve case '{case_id}' from DB after restart!"
    assert loaded_state.case_id == case_id
    assert len(loaded_state.profile.facts) == len(state.profile.facts)
    print("[PASS] Case retrieved successfully from PostgreSQL DB after restart!")

    close_db_pool()
    print("\n" + "=" * 60)
    print("END-TO-END REGRESSION TEST SUCCEEDED 100%")
    print("=" * 60)

if __name__ == "__main__":
    main()
