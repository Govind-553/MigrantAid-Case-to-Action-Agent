# MigrantAid — Case-to-Action Assistant Reproduction Guide

## 1. Goal

This document provides step-by-step instructions to reproduce the complete MigrantAid project:
1. Environment setup and validation.
2. Synthetic ground-truth datasets (cases, resources, sources).
3. Monolithic single-prompt baseline execution & VARR evaluation.
4. Multi-agent architecture execution with deterministic verification engine.
5. Benchmark metrics comparison (VARR, 6-dimension scoring, failure category reductions).
6. Full Next.js caseworker UI & evaluation dashboard.
7. Agent trajectory logs.

---

## 2. Tested Environment Specifications

```text
Python Version:        3.9.13 (with eval_type_backport for modern type hints)
Node.js Version:       v22.18.0
npm Version:            10.9.3
OS:                    Windows 11 Home (64-bit, PowerShell)
Backend Framework:     FastAPI 0.115.8 (Uvicorn 0.34.0)
Frontend Framework:    Next.js 14.2.35 (React 18.3.1, Tailwind CSS 3.4.17)
LLM Provider:          Google Gemini (gemini-1.5-flash / gemini-2.5-flash)
Database:              SQLite 3 (`migrantaid.db` via SQLAlchemy 2.0.38)
Resource Dataset:      v1.0 (6 approved synthetic resources)
Evaluation Dataset:    v1.0 (20 fixed ground-truth benchmark cases)
```

---

## 3. Clone & Environment Setup

### 3.1 Repository Navigation

```powershell
git clone https://github.com/user/MigrantAid-Case-to-Action-Agent.git
cd MigrantAid-Case-to-Action-Agent
```

### 3.2 Backend Setup & Dependencies

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3.3 Frontend Setup & Build Verification

```powershell
cd ..\frontend
npm install
npm run build
```

---

## 4. Environment Configuration & Validation

### 4.1 `.env` Configuration

Ensure `.env` exists in the repository root (copied from `.env.example`):

```env
LLM_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=models/text-embedding-004
DATABASE_URL=sqlite:///./migrantaid.db
APP_ENV=development
LOG_LEVEL=INFO
```

### 4.2 Validate Environment & Dataset Schema

From `backend/`:

```powershell
.venv\Scripts\python ..\scripts\validate_environment.py
.venv\Scripts\python ..\scripts\validate_data.py
```

Expected Output:
```text
[SUCCESS] Python Version: Detected 3.9.13 (Required >= 3.9.0)
[SUCCESS] .env File Presence: Found .env file
[SUCCESS] Data File & JSON Check: evaluation_cases.json: Found and valid JSON
[SUCCESS] Data File & JSON Check: resources.json: Found and valid JSON
[SUCCESS] Data File & JSON Check: sources.json: Found and valid JSON
Result: ENVIRONMENT IS VALID
```

---

## 5. Automated Unit & Integration Testing

Run all 148 automated backend pytest test cases across domain models, verification engine, intake agent, needs agent, matching agent, action planner, quality safety gate, case workflow, and REST API:

```powershell
cd backend
.venv\Scripts\pytest -v
```

Expected Output:
```text
=================== 148 passed in 1.42s ===================
```

---

## 6. Reproducing the Baseline (Iteration 0)

Execute the monolithic single-prompt baseline across all 20 evaluation cases:

```powershell
.venv\Scripts\python ..\baseline\baseline_runner.py
```

Outputs:
- Baseline outputs saved to: `baseline/baseline_results.json`

Evaluate the baseline against the VARR rubric:

```powershell
.venv\Scripts\python ..\evaluation\run_evaluation.py
```

Outputs:
- Baseline evaluation report saved to: `evaluation/baseline_evaluation_report.json`
- Baseline VARR: **0.0%**, Average Score: **40.5 / 100**.

---

## 7. Reproducing the Multi-Agent System (Iteration 1)

Execute the multi-agent agentic workflow (Intake -> Needs -> Retrieval -> Deterministic Verification -> Action Planning -> Quality Audit) over all 20 cases:

```powershell
.venv\Scripts\python ..\evaluation\run_agent_evaluation.py
```

Outputs:
- Agent evaluation report saved to: `evaluation/agent_evaluation_report.json`
- Execution trajectories saved to: `trajectories/agent_trajectories.json`
- Agentic VARR: **40.0%**, Average Score: **76.7 / 100**.

---

## 8. Reproducing the System Comparison Report

Run side-by-side comparative benchmarking CLI:

```powershell
.venv\Scripts\python ..\evaluation\compare_systems.py
```

Measured Comparison Output:
```text
================================================================================
                MIGRANTAID: BASELINE VS AGENTIC COMPARISON                      
================================================================================
Metric                              | Baseline System    | Agentic System     | Delta     
--------------------------------------------------------------------------------
VARR (Verified Actionable Rate)     |              0.0% |             40.0% |    +40.0%
Average Total Score (out of 100)    |              40.5 |              76.7 |     +36.2
Successful Cases (out of 20)        |                 0 |                 8 |        +8
--------------------------------------------------------------------------------

--- Dimension Score Breakdown (Average Points) ---
Primary Need                        |              12.0 |              19.0 |      +7.0
Resource                            |               7.6 |               8.8 |      +1.2
Evidence                            |               5.0 |              16.5 |     +11.5
Missing Information                 |               4.2 |               7.5 |      +3.3
Unsupported Claim                   |               4.5 |              15.0 |     +10.5
Actionable Next Step                |               7.2 |               9.8 |      +2.6
--------------------------------------------------------------------------------

--- Failure Category Occurrences (Lower is Better) ---
CONTRADICTION_MISS                  |                 2 |                 0 |        -2
EVIDENCE_MISS                       |                20 |                 0 |       -20
MISSING_INFO_MISS                   |                14 |                10 |        -4
NEED_MISS                           |                 8 |                 1 |        -7
RETRIEVAL_MISS                      |                18 |                14 |        -4
UNSUPPORTED_CLAIM                   |                14 |                 0 |       -14
================================================================================
```

---

## 9. Running the Interactive Full-Stack Application

### 9.1 Start FastAPI Backend Server

In Terminal 1 (`backend/`):

```powershell
.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify backend health check at: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 9.2 Start Next.js Frontend Caseworker UI

In Terminal 2 (`frontend/`):

```powershell
npm run dev
```

Open Caseworker Dashboard at: [http://localhost:3000](http://localhost:3000)

Features available in UI:
1. **Case Intake & Preset Selector**: Load pre-configured evaluation cases or type custom stories.
2. **Extracted Facts & Contradictions Editor**: View explicit vs inferred facts, edit values, and click **Save & Re-verify**.
3. **Needs Assessment View**: Prioritized needs with supporting fact references.
4. **Verified Recommendations & Traceable Evidence**: Deterministic requirement evaluations with status badges (Strong Match, Potential Match, Insufficient Info, Conflict).
5. **Sequential Action Plan**: Role-assigned step-by-step checklist.
6. **Human-in-the-Loop Review Gate**: Approve, Modify, Request Info, or Reject referrals with caseworker notes.
7. **Observable Agent Trajectory Log**: Step-by-step event timeline with latencies.
8. **VARR Benchmark Dashboard**: Live comparison tab fetching metrics from `GET /api/evaluation/comparison`.

---

## 10. Summary of Evaluation Metrics

```text
Evaluation Dataset:                 20 Ground-Truth Synthetic Cases
Approved Resources Dataset:         6 Verified Resources
Baseline VARR:                      0.0%
MigrantAid Agentic VARR:            40.0%
Absolute VARR Gain:                 +40.0%
Average Total Score Gain:           +36.2 points (76.7 / 100 vs 40.5 / 100)
Evidence Traceability Score:        16.5 / 20 (+11.5 pts)
Unsupported Claim Score:            15.0 / 15 (100% compliant, 0 false claims)
Contradiction Detection Misses:     0 occurrences (reduced from 2)
Average Execution Latency:          ~1.7ms (offline simulation) / ~2.5s (live API pipeline)
```

---

## 11. Clean-Environment Verification Record

```text
Fresh Environment Tested:           YES
Date:                               2026-08-30
OS:                                 Windows 11 Home (PowerShell)
Python:                             3.9.13
Node.js:                            v22.18.0
Result:                             All 148 tests passing, baseline VARR 0.0%, agentic VARR 40.0%, Next.js build clean.
```
