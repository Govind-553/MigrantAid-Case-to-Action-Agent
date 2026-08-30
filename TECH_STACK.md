# MigrantAid --- Tech Stack Requirements

## 1. Purpose

This document defines the recommended technical stack for the MigrantAid
hackathon MVP.

The stack should prioritize:

1.  fast implementation;
2.  reproducibility;
3.  clear agent orchestration;
4.  structured outputs;
5.  evaluation;
6.  low unnecessary infrastructure;
7.  easy local setup;
8.  a polished demo.

Do not introduce infrastructure that does not directly improve the
project.

## 2. Recommended Stack

### Frontend

**Next.js + React + TypeScript**

Use for:

-   case intake;
-   case review;
-   workflow progress;
-   recommendation cards;
-   evidence display;
-   human review;
-   evaluation dashboard.

### Styling

**Tailwind CSS**

Use a clean, professional interface.

Avoid excessive animations and decorative AI visuals.

### Backend

**Python + FastAPI**

Use for:

-   API;
-   agent orchestration;
-   schemas;
-   evaluation;
-   knowledge-base access;
-   case state.

Python is preferred because the evaluation and agent workflow can remain
in one environment.

### Data Validation

**Pydantic**

All agent outputs that cross component boundaries should use typed
schemas.

### Database

For the MVP, choose one of:

-   **SQLite** for simplest local reproduction;
-   **PostgreSQL** if the selected deployment requires a persistent
    hosted database.

Default to SQLite unless a clear requirement justifies PostgreSQL.

### Vector Search

Use a lightweight local/vector solution only if semantic retrieval is
required.

Possible options:

-   Chroma;
-   FAISS;
-   pgvector if PostgreSQL is already required.

Do not introduce a vector database if structured filtering plus a small
approved dataset is sufficient.

### LLM

Use a model/API that supports:

-   structured output;
-   reliable tool/function calling where needed;
-   reasonable latency;
-   documented pricing.

The exact provider/model should be configured through environment
variables.

Do not hard-code model credentials.

### Embeddings

Only required if semantic retrieval materially improves matching.

If used, configure the embedding model through environment variables.

### Agent Orchestration

Prefer a simple explicit Python orchestrator first.

A framework may be introduced if it genuinely improves:

-   state management;
-   tool use;
-   retries;
-   trajectory capture;
-   reproducibility.

Do not use an agent framework merely because the project is called
"agentic."

### Testing

Use:

-   `pytest` for backend/unit tests;
-   schema validation tests;
-   evaluation tests;
-   representative end-to-end tests.

### Code Quality

Use:

-   `ruff`;
-   `black` or a consistent formatter;
-   type hints;
-   clear module boundaries.

### Package Management

Use one reproducible method such as:

-   `uv`;
-   or `pip` + `requirements.txt`.

The final project must document exact commands.

### Environment

Recommended:

``` text
Python 3.11+
Node.js 20+
```

Pin exact versions used in the final submission.

If implementation requires different versions, document the actual
tested versions.

## 3. Suggested Repository Structure

``` text
migrantaid/
│
├── README.md
├── PROJECT_REQUIREMENTS.md
├── SYSTEM_DESIGN.md
├── USER_FLOW.md
├── FEATURES.md
├── TECH_STACK.md
├── IMPROVEMENT_CHANGELOG.md
├── REPRODUCTION_GUIDE.md
│
├── .env.example
├── .gitignore
├── docker-compose.yml              # optional
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── agents/
│   │   ├── orchestration/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── retrieval/
│   │   ├── verification/
│   │   └── config/
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
│
├── data/
│   ├── resources.json
│   ├── sources.json
│   └── evaluation_cases.json
│
├── baseline/
│   └── baseline_runner.py
│
├── evaluation/
│   ├── run_evaluation.py
│   ├── scoring.py
│   └── results/
│
├── trajectories/
│
└── scripts/
    ├── seed_data.py
    └── validate_environment.py
```

The final repository may differ, but any deviation should make the
project simpler or more maintainable.

## 4. Environment Variables

Example:

``` text
LLM_API_KEY=
LLM_MODEL=
EMBEDDING_MODEL=
DATABASE_URL=
APP_ENV=development
```

Do not commit actual values.

Provide `.env.example`.

## 5. Agent Interface Requirements

Each agent should expose a predictable interface.

Conceptually:

``` python
class Agent:
    name: str

    def run(self, state: CaseState) -> AgentResult:
        ...
```

Prefer asynchronous execution only when it provides a real benefit.

Keep interfaces simple enough that the evaluation runner can invoke
them.

## 6. Structured Schemas

Recommended core schemas:

``` text
CaseProfile
CaseFact
NeedsAssessment
Resource
ResourceRequirement
ResourceMatch
EvidenceItem
VerifiedRecommendation
ActionItem
ActionPlan
QualityReport
HumanReview
CaseState
EvaluationResult
```

Schemas should reject invalid states.

Example:

``` text
VerifiedRecommendation
- resource_id: required
- status: required
- evidence: at least one item unless status indicates no match
- human_review_required: boolean
```

## 7. Knowledge Base Requirements

The knowledge base must be versioned.

Recommended:

``` text
data/resources.json
data/sources.json
```

Each evaluation run should record the dataset version.

Do not silently change resource records between baseline and final
evaluation.

## 8. Retrieval Requirements

The retrieval layer must:

1.  apply structured filters when possible;
2.  retrieve candidates;
3.  return resource IDs;
4.  preserve source metadata;
5.  never invent resource records.

Recommended result:

``` json
{
  "resource_id": "RES-001",
  "score": 0.87,
  "retrieval_reasons": [
    "service category match",
    "geographic match"
  ]
}
```

A retrieval score is not an eligibility score.

## 9. LLM Prompt Requirements

Prompts must be stored in version-controlled files where practical.

Example:

``` text
backend/app/agents/prompts/
├── intake.txt
├── needs_assessment.txt
├── matching.txt
├── verification.txt
├── action_planning.txt
└── quality_check.txt
```

Prompts must instruct the model to:

-   return structured data;
-   preserve unknowns;
-   avoid unsupported claims;
-   cite resource IDs;
-   distinguish facts from inference;
-   request clarification when needed.

## 10. Tool Requirements

Tools should be narrow and auditable.

Possible tools:

``` text
search_resources
get_resource
get_source
save_case
update_case
record_review
```

Avoid giving an agent unrestricted access to arbitrary system
operations.

## 11. Logging and Trajectories

Store structured trajectory events.

Example:

``` json
{
  "case_id": "CASE-001",
  "agent": "verification_agent",
  "event": "tool_call",
  "tool": "get_resource",
  "resource_id": "RES-001",
  "timestamp": "..."
}
```

Do not store secrets or unnecessary personal information.

## 12. Testing Strategy

### Unit tests

Test:

-   schemas;
-   resource filtering;
-   requirement comparison;
-   scoring;
-   status transitions.

### Integration tests

Test:

``` text
case input
→ intake
→ assessment
→ retrieval
→ verification
→ plan
```

### Evaluation tests

Use the fixed evaluation dataset.

Never modify the test set to make the system look better after seeing
results without documenting the change.

## 13. Baseline Technology

The baseline should use the same core model family where practical.

Recommended:

``` text
case description
+
resource dataset
+
one prompt
→
final response
```

No specialized verification agent.

No multi-stage orchestration.

No hidden additional information.

This makes the comparison meaningful.

## 14. Evaluation Output

Produce:

``` text
evaluation/results/
├── baseline_results.json
├── agent_results.json
├── comparison.csv
├── summary.json
└── error_analysis.md
```

Summary should include:

-   number of cases;
-   primary metric;
-   secondary metrics;
-   baseline;
-   final;
-   absolute change;
-   relative change where useful;
-   failures.

## 15. Reproducibility Requirements

A clean developer must be able to:

``` bash
git clone <repository>
cd migrantaid

# install dependencies
# configure environment
# seed data
# run tests
# run baseline
# run final evaluation
# start application
```

The actual commands used must be documented in `REPRODUCTION_GUIDE.md`.

## 16. Local Development

Recommended development startup:

``` text
Frontend → localhost
Backend  → localhost
Database → local SQLite
```

If a hosted model API is required, only the model call should leave the
local environment.

## 17. Deployment

Deployment is optional for the evaluation unless required by the
hackathon environment.

If deployed:

-   frontend can use a modern web hosting platform;
-   backend can use a simple Python-compatible service;
-   database can remain local for demo if persistence is not required.

Do not add Kubernetes, microservices, queues, or complex cloud
infrastructure unless a demonstrated requirement exists.

## 18. Security Requirements

Must include:

-   `.gitignore`;
-   `.env.example`;
-   no API keys in code;
-   input validation;
-   safe logging;
-   no sensitive demo data;
-   controlled tool permissions.

## 19. Cost Tracking

For every evaluation run, record where possible:

``` text
model
input tokens
output tokens
estimated cost
latency
```

The final README should report approximate cost per evaluation case.

Actual measured values are preferred over estimates.

## 20. Recommended Implementation Sequence

### Stage 1 --- Foundation

-   create repository;
-   create backend/frontend;
-   configure environment;
-   create schemas.

### Stage 2 --- Data

-   create synthetic evaluation cases;
-   create approved resource records;
-   version the data.

### Stage 3 --- Baseline

-   implement baseline;
-   run baseline;
-   record failures.

### Stage 4 --- Agents

Implement only the agents justified by observed failures:

1.  Intake;
2.  Needs;
3.  Matching;
4.  Verification;
5.  Action Planning;
6.  Quality/Safety.

### Stage 5 --- Evaluation

-   run final system;
-   score same cases;
-   compare;
-   analyze failures.

### Stage 6 --- Product UI

-   polish case workflow;
-   evidence display;
-   human review;
-   final packet.

### Stage 7 --- Submission

-   trajectories;
-   changelog;
-   reproduction guide;
-   demo video;
-   final results.

## 21. Technology Selection Rule

If a simpler technology can achieve the same requirement with better
reproducibility, choose the simpler technology.

The judges reward purposeful engineering choices, not technology count.
