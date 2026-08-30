"""
Case Persistence Repository
============================
Provides transaction-safe atomic persistence and retrieval of CaseState domain models using psycopg3.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.db.connection import get_db_connection
from app.schemas.domain import (
    ActionItem,
    ActionPlan,
    ActionPriority,
    AgentEvent,
    AgentEventType,
    CaseFact,
    CaseProfile,
    CaseState,
    CaseWorkflowState,
    EvidenceItem,
    FactStatus,
    HumanReview,
    HumanReviewDecision,
    MatchStatus,
    Need,
    NeedCategory,
    NeedPriority,
    NeedsAssessment,
    RequirementEvaluation,
    RequirementStatus,
    VerifiedRecommendation,
)


logger = logging.getLogger("migrantaid")


class CaseRepository:
    """Handles PostgreSQL storage and retrieval for MigrantAid case lifecycle."""

    def save_case(self, state: CaseState) -> None:
        """Persist or update full CaseState in a single database transaction."""
        case_id = state.case_id
        narrative = state.profile.narrative if state.profile else ""
        workflow_state = state.workflow_state.value
        created_at = state.created_at
        updated_at = datetime.now(timezone.utc)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # 1. Upsert into cases
                cur.execute(
                    """
                    INSERT INTO cases (id, narrative, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        narrative = EXCLUDED.narrative,
                        status = EXCLUDED.status,
                        updated_at = EXCLUDED.updated_at;
                    """,
                    (case_id, narrative, workflow_state, created_at, updated_at),
                )

                # 2. Persist Case Facts
                cur.execute("DELETE FROM case_facts WHERE case_id = %s;", (case_id,))
                if state.profile and state.profile.facts:
                    for fact in state.profile.facts:
                        val_json = json.dumps(fact.value)
                        cur.execute(
                            """
                            INSERT INTO case_facts (case_id, field, value, status, source, notes)
                            VALUES (%s, %s, %s::jsonb, %s, %s, %s);
                            """,
                            (
                                case_id,
                                fact.field,
                                val_json,
                                fact.status.value,
                                fact.source,
                                fact.notes,
                            ),
                        )

                # 3. Persist Case Needs
                cur.execute("DELETE FROM case_needs WHERE case_id = %s;", (case_id,))
                if state.needs_assessment and state.needs_assessment.needs:
                    for need in state.needs_assessment.needs:
                        refs_json = json.dumps(need.evidence_references)
                        cur.execute(
                            """
                            INSERT INTO case_needs (case_id, category, priority, reason, evidence_references)
                            VALUES (%s, %s, %s, %s, %s::jsonb);
                            """,
                            (
                                case_id,
                                need.category.value,
                                need.priority.value,
                                need.reason,
                                refs_json,
                            ),
                        )

                # 4. Persist Recommendations & Verification Results
                cur.execute("DELETE FROM resource_recommendations WHERE case_id = %s;", (case_id,))
                for rec in state.verified_recommendations:
                    need_cat = None
                    if state.needs_assessment and state.needs_assessment.primary_need:
                        need_cat = state.needs_assessment.primary_need.category.value

                    cur.execute(
                        """
                        INSERT INTO resource_recommendations (
                            case_id, resource_id, resource_name, need_category,
                            retrieval_score, status, source_id, human_review_required
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id;
                        """,
                        (
                            case_id,
                            rec.resource_id,
                            rec.resource_name,
                            need_cat,
                            0.9,  # Default heuristic retrieval score
                            rec.status.value,
                            rec.source_id,
                            rec.human_review_required,
                        ),
                    )
                    rec_id_row = cur.fetchone()
                    if rec_id_row:
                        rec_db_id = rec_id_row[0]
                        for req_eval in rec.requirement_evaluations:
                            cf_val = json.dumps(req_eval.case_fact_value) if req_eval.case_fact_value is not None else None
                            rq_val = json.dumps(req_eval.required_value) if req_eval.required_value is not None else None
                            cur.execute(
                                """
                                INSERT INTO verification_results (
                                    recommendation_id, requirement_id, field, status,
                                    evidence_text, case_fact_value, required_value
                                )
                                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb);
                                """,
                                (
                                    rec_db_id,
                                    req_eval.requirement_id,
                                    req_eval.field,
                                    req_eval.status.value,
                                    req_eval.evidence_text,
                                    cf_val,
                                    rq_val,
                                ),
                            )

                # 5. Persist Action Plan Items
                cur.execute("DELETE FROM action_plan_items WHERE case_id = %s;", (case_id,))
                if state.action_plan and state.action_plan.actions:
                    for action in state.action_plan.actions:
                        cur.execute(
                            """
                            INSERT INTO action_plan_items (
                                case_id, step, priority, action, reason,
                                prerequisite, responsible_role, evidence_reference, unresolved_uncertainty
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                            """,
                            (
                                case_id,
                                action.step,
                                action.priority.value,
                                action.action,
                                action.reason,
                                action.prerequisite,
                                action.responsible_role,
                                action.evidence_reference,
                                action.unresolved_uncertainty,
                            ),
                        )

                # 6. Persist Human Review
                if state.human_review:
                    rev = state.human_review
                    cur.execute(
                        """
                        INSERT INTO human_reviews (
                            case_id, decision, reviewer_notes, reviewed_at,
                            modified_recommendation_ids, rejected_recommendation_ids, follow_up_required, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (case_id) DO UPDATE SET
                            decision = EXCLUDED.decision,
                            reviewer_notes = EXCLUDED.reviewer_notes,
                            reviewed_at = EXCLUDED.reviewed_at,
                            modified_recommendation_ids = EXCLUDED.modified_recommendation_ids,
                            rejected_recommendation_ids = EXCLUDED.rejected_recommendation_ids,
                            follow_up_required = EXCLUDED.follow_up_required,
                            updated_at = CURRENT_TIMESTAMP;
                        """,
                        (
                            case_id,
                            rev.decision.value,
                            rev.reviewer_notes,
                            rev.reviewed_at,
                            json.dumps(rev.modified_recommendation_ids),
                            json.dumps(rev.rejected_recommendation_ids),
                            rev.follow_up_required,
                        ),
                    )

                # 7. Persist Trajectory Events
                cur.execute("DELETE FROM trajectory_events WHERE case_id = %s;", (case_id,))
                for evt in state.trajectory:
                    cur.execute(
                        """
                        INSERT INTO trajectory_events (
                            case_id, stage, agent, event_type, input_summary,
                            output_summary, tool_call, tool_response_summary,
                            verification_result, error_message, retry_count, latency_ms, timestamp, metadata
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb);
                        """,
                        (
                            case_id,
                            evt.stage,
                            evt.agent,
                            evt.event_type.value,
                            evt.input_summary,
                            evt.output_summary,
                            evt.tool_call,
                            evt.tool_response_summary,
                            evt.verification_result,
                            evt.error_message,
                            evt.retry_count,
                            evt.latency_ms,
                            evt.timestamp,
                            json.dumps(evt.metadata or {}),
                        ),
                    )

        logger.info(f"Successfully persisted case {case_id} to database.")

    def get_case(self, case_id: str) -> CaseState | None:
        """Retrieve full CaseState by case_id."""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # 1. Fetch case row
                cur.execute(
                    "SELECT id, narrative, status, created_at, updated_at FROM cases WHERE id = %s;",
                    (case_id,),
                )
                case_row = cur.fetchone()
                if not case_row:
                    return None

                cid, narrative, status_str, created_at, updated_at = case_row
                wf_state = CaseWorkflowState(status_str)

                # 2. Fetch Facts
                cur.execute(
                    "SELECT field, value, status, source, notes FROM case_facts WHERE case_id = %s ORDER BY id;",
                    (case_id,),
                )
                fact_rows = cur.fetchall()
                facts: list[CaseFact] = []
                for f_field, f_val, f_status, f_source, f_notes in fact_rows:
                    facts.append(
                        CaseFact(
                            field=f_field,
                            value=f_val,
                            status=FactStatus(f_status),
                            source=f_source or "user_input",
                            notes=f_notes,
                        )
                    )

                profile = CaseProfile(
                    case_id=case_id,
                    narrative=narrative,
                    facts=facts,
                    missing_information=[],
                    contradictions=[],
                    workflow_state=wf_state,
                    created_at=created_at,
                    updated_at=updated_at,
                )

                # 3. Fetch Needs
                cur.execute(
                    "SELECT category, priority, reason, evidence_references FROM case_needs WHERE case_id = %s ORDER BY id;",
                    (case_id,),
                )
                need_rows = cur.fetchall()
                needs: list[Need] = []
                for n_cat, n_pri, n_reason, n_refs in need_rows:
                    needs.append(
                        Need(
                            category=NeedCategory(n_cat),
                            priority=NeedPriority(n_pri),
                            reason=n_reason,
                            evidence_references=n_refs if isinstance(n_refs, list) else [],
                        )
                    )
                needs_assessment = NeedsAssessment(case_id=case_id, needs=needs) if needs else None

                # 4. Fetch Recommendations & Verification Results
                cur.execute(
                    """
                    SELECT id, resource_id, resource_name, status, source_id, human_review_required
                    FROM resource_recommendations
                    WHERE case_id = %s ORDER BY id;
                    """,
                    (case_id,),
                )
                rec_rows = cur.fetchall()
                verified_recs: list[VerifiedRecommendation] = []

                for r_id_db, r_id, r_name, r_status, r_source, r_human_req in rec_rows:
                    cur.execute(
                        """
                        SELECT requirement_id, field, status, evidence_text, case_fact_value, required_value
                        FROM verification_results
                        WHERE recommendation_id = %s ORDER BY id;
                        """,
                        (r_id_db,),
                    )
                    vr_rows = cur.fetchall()
                    req_evals: list[RequirementEvaluation] = []
                    evidence_list: list[EvidenceItem] = []

                    for v_req_id, v_field, v_status, v_ev_text, v_cf_val, v_rq_val in vr_rows:
                        req_status = RequirementStatus(v_status)
                        req_evals.append(
                            RequirementEvaluation(
                                requirement_id=v_req_id,
                                field=v_field,
                                status=req_status,
                                evidence_text=v_ev_text,
                                case_fact_value=v_cf_val,
                                required_value=v_rq_val,
                            )
                        )
                        if req_status == RequirementStatus.satisfied:
                            evidence_list.append(
                                EvidenceItem(
                                    case_fact_id=v_field,
                                    requirement_id=v_req_id,
                                    result=req_status,
                                    evidence=v_ev_text or f"Requirement '{v_req_id}' satisfied.",
                                )
                            )

                    rec_match_status = MatchStatus(r_status)
                    verified_recs.append(
                        VerifiedRecommendation(
                            resource_id=r_id,
                            resource_name=r_name or r_id,
                            status=rec_match_status,
                            evidence=evidence_list,
                            requirement_evaluations=req_evals,
                            missing_information=[],
                            verification_warnings=[],
                            human_review_required=r_human_req,
                            source_id=r_source or "SRC-001",
                        )
                    )

                # 5. Fetch Action Plan
                cur.execute(
                    """
                    SELECT step, priority, action, reason, prerequisite, responsible_role, evidence_reference, unresolved_uncertainty
                    FROM action_plan_items
                    WHERE case_id = %s ORDER BY step;
                    """,
                    (case_id,),
                )
                act_rows = cur.fetchall()
                action_items: list[ActionItem] = []
                for step, priority, action, reason, prereq, role, ev_ref, un_unc in act_rows:
                    action_items.append(
                        ActionItem(
                            step=step,
                            priority=ActionPriority(priority),
                            action=action,
                            reason=reason,
                            prerequisite=prereq,
                            responsible_role=role,
                            evidence_reference=ev_ref,
                            unresolved_uncertainty=un_unc,
                        )
                    )
                action_plan = ActionPlan(case_id=case_id, actions=action_items) if action_items else None

                # 6. Fetch Human Review
                cur.execute(
                    """
                    SELECT decision, reviewer_notes, reviewed_at, modified_recommendation_ids, rejected_recommendation_ids, follow_up_required
                    FROM human_reviews WHERE case_id = %s;
                    """,
                    (case_id,),
                )
                hr_row = cur.fetchone()
                human_review: HumanReview | None = None
                if hr_row:
                    h_dec, h_notes, h_at, h_mod, h_rej, h_fu = hr_row
                    human_review = HumanReview(
                        case_id=case_id,
                        decision=HumanReviewDecision(h_dec),
                        reviewer_notes=h_notes,
                        reviewed_at=h_at,
                        modified_recommendation_ids=h_mod if isinstance(h_mod, list) else [],
                        rejected_recommendation_ids=h_rej if isinstance(h_rej, list) else [],
                        follow_up_required=h_fu,
                    )

                # 7. Fetch Trajectory Events
                cur.execute(
                    """
                    SELECT stage, agent, event_type, input_summary, output_summary, tool_call, tool_response_summary, verification_result, error_message, retry_count, latency_ms, timestamp, metadata
                    FROM trajectory_events WHERE case_id = %s ORDER BY id;
                    """,
                    (case_id,),
                    )
                evt_rows = cur.fetchall()
                trajectory: list[AgentEvent] = []
                for (
                    e_stage, e_agent, e_type, e_in, e_out, e_tc, e_tr, e_vr, e_err, e_retry, e_lat, e_ts, e_meta
                ) in evt_rows:
                    trajectory.append(
                        AgentEvent(
                            case_id=case_id,
                            stage=e_stage,
                            agent=e_agent,
                            event_type=AgentEventType(e_type),
                            input_summary=e_in,
                            output_summary=e_out,
                            tool_call=e_tc,
                            tool_response_summary=e_tr,
                            verification_result=e_vr,
                            error_message=e_err,
                            retry_count=e_retry or 0,
                            latency_ms=e_lat,
                            timestamp=e_ts,
                            metadata=e_meta if isinstance(e_meta, dict) else {},
                        )
                    )

                return CaseState(
                    case_id=case_id,
                    profile=profile,
                    needs_assessment=needs_assessment,
                    verified_recommendations=verified_recs,
                    action_plan=action_plan,
                    human_review=human_review,
                    workflow_state=wf_state,
                    trajectory=trajectory,
                    created_at=created_at,
                    updated_at=updated_at,
                )

    def list_cases(self) -> list[dict[str, Any]]:
        """List metadata summaries for all persisted cases."""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.id, c.status, c.created_at, c.updated_at,
                           (SELECT category FROM case_needs WHERE case_id = c.id ORDER BY id LIMIT 1) as primary_need,
                           (SELECT COUNT(*) FROM resource_recommendations WHERE case_id = c.id) as rec_count
                    FROM cases c
                    ORDER BY c.created_at DESC;
                    """
                )
                rows = cur.fetchall()
                summaries = []
                for cid, status_str, created_at, updated_at, primary_need, rec_count in rows:
                    summaries.append(
                        {
                            "case_id": cid,
                            "workflow_state": status_str,
                            "primary_need": primary_need or "unknown",
                            "verified_recommendations_count": rec_count or 0,
                            "created_at": created_at.isoformat() if created_at else "",
                            "updated_at": updated_at.isoformat() if updated_at else "",
                            "has_missing_info": False,
                            "has_contradictions": False,
                        }
                    )
                return summaries
