# MigrantAid — Case-to-Action Assistant

> **An evidence-backed case-to-action assistant for community workers supporting migrant workers.**

MigrantAid helps a frontline community worker turn an incomplete, messy description of a migrant worker's situation into a structured, evidence-backed, human-reviewable action plan.

It is designed as an **assistive workflow**, not as an autonomous authority that approves benefits, rejects applications, gives legal decisions, or guarantees eligibility.

---

## Benchmark Results (Baseline vs Agentic)

| Metric | Baseline (Single-Prompt LLM) | MigrantAid Multi-Agent | Improvement (Delta) |
|---|---|---|---|
| **VARR (Verified Actionable Rate)** | **0.0%** | **40.0%** | **+40.0%** |
| **Average Total Score (out of 100)** | **40.5** | **76.7** | **+36.2 pts** |
| **Primary Need Score (out of 20)** | 12.0 | 19.0 | +7.0 pts |
| **Resource Identification Score (out of 20)** | 7.6 | 8.8 | +1.2 pts |
| **Evidence Traceability Score (out of 20)** | 5.0 | 16.5 | +11.5 pts |
| **Missing Info Detection Score (out of 15)** | 4.2 | 7.5 | +3.3 pts |
| **No Unsupported Claims Score (out of 15)** | 4.5 | 15.0 | +10.5 pts (100% compliant) |
| **Actionable Step Score (out of 10)** | 7.2 | 9.8 | +2.6 pts |
| **Unsupported Claim Penalties** | 14 cases | **0 cases** | **-100% false claims** |
| **Evidence Miss Penalties** | 20 cases | **0 cases** | **-100% ungrounded assertions** |
| **Contradiction Misses** | 2 cases | **0 cases** | **-100% missed contradictions** |

---

## Core Workflow

```text
Case Narrative Input
      ↓
Intake Agent ─────────────→ Structured Facts & Provenance + Contradictions
      ↓
Needs Agent ──────────────→ Categorized & Prioritized Needs
      ↓
Matching Agent ───────────→ Retrived Approved Resources
      ↓
Verification Engine ──────→ Deterministic Operator Check (UNKNOWN != SATISFIED)
      ↓
Action Planning Agent ────→ Sequential Step-by-Step Action Plan
      ↓
Quality Agent ────────────→ Pre-Presentation Safety & Guardrail Audit
      ↓
Human Review Gate ────────→ Caseworker Approve / Modify / Request Info / Reject
      ↓
Final Action Packet
```

---

## Target User & Product Boundary

### Primary User
Frontline community workers, NGO caseworkers, migrant resource center staff.

### Human Responsibility
MigrantAid prepares and verifies information for human review. A qualified human caseworker remains responsible for consequential decisions.

### Strict Product Rules
MigrantAid does **NOT**:
- Convert unknown eligibility into eligible (`UNKNOWN != SATISFIED`).
- Guarantee eligibility or grant benefits autonomously.
- Fabricate resources or source citations.
- Strip evidence references or present unverified claims.

---

## Quickstart Guide

### 1. Environment Validation

```powershell
cd backend
.venv\Scripts\python ..\scripts\validate_environment.py
```

### 2. Run Automated Test Suite (148 tests)

```powershell
.venv\Scripts\pytest -v
```

### 3. Execute Baseline & Agent Evaluation

```powershell
# Monolithic Baseline
.venv\Scripts\python ..\baseline\baseline_runner.py
.venv\Scripts\python ..\evaluation\run_evaluation.py

# Multi-Agent Pipeline
.venv\Scripts\python ..\evaluation\run_agent_evaluation.py

# Side-by-Side Comparison
.venv\Scripts\python ..\evaluation\compare_systems.py
```

### 4. Run Full-Stack Application

**Backend (FastAPI):**
```powershell
cd backend
.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend (Next.js):**
```powershell
cd frontend
npm run dev
```

Open Caseworker Dashboard at: [http://localhost:3000](http://localhost:3000)

---

## System Architecture Documents

1. [`AGENTS.md`](file:///c:/Users/choud/MigrantAid-Case-to-Action-Agent/AGENTS.md) — System rules and architectural principles.
2. [`PROJECT_REQUIREMENTS.md`](file:///c:/Users/choud/MigrantAid-Case-to-Action-Agent/PROJECT_REQUIREMENTS.md) — Product requirements and domain boundaries.
3. [`SYSTEM_DESIGN.md`](file:///c:/Users/choud/MigrantAid-Case-to-Action-Agent/SYSTEM_DESIGN.md) — Detailed agentic architecture, verification engine, and schemas.
4. [`EVALUATION_DATASET_SPEC.md`](file:///c:/Users/choud/MigrantAid-Case-to-Action-Agent/EVALUATION_DATASET_SPEC.md) — VARR scoring formula and 6 dimension rubrics.
5. [`IMPROVEMENT_CHANGELOG.md`](file:///c:/Users/choud/MigrantAid-Case-to-Action-Agent/IMPROVEMENT_CHANGELOG.md) — Iteration history and evidence-backed changes.
6. [`REPRODUCTION_GUIDE.md`](file:///c:/Users/choud/MigrantAid-Case-to-Action-Agent/REPRODUCTION_GUIDE.md) — Verified reproduction guide.
