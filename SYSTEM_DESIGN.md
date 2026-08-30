# MigrantAid --- System Design Document

## 1. Purpose

This document defines the technical architecture and runtime behavior of
MigrantAid.

The implementation agent must use this document together with:

-   `PROJECT_REQUIREMENTS.md`
-   `USER_FLOW.md`
-   `FEATURES.md`
-   `TECH_STACK.md`

The system is an **agentic workflow**, not a single chatbot.

## 2. High-Level Architecture

``` text
┌─────────────────────────────┐
│       Community Worker      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│         Web / UI Layer      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Case Orchestrator     │
└──────────────┬──────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌───────────────┐
│ Intake      │  │ Case Memory   │
│ Agent       │  │ / State Store │
└──────┬──────┘  └───────────────┘
       │
       ▼
┌─────────────────────────────┐
│      Needs Assessment       │
│            Agent            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Resource Retrieval / Match  │◄─────────┐
│            Agent            │          │
└──────────────┬──────────────┘          │
               │                         │
               ▼                         │
┌─────────────────────────────┐          │
│ Eligibility & Evidence      │          │
│ Verification Agent          │          │
└──────────────┬──────────────┘          │
               │                         │
               ▼                         │
┌─────────────────────────────┐          │
│ Action Planning Agent       │          │
└──────────────┬──────────────┘          │
               │                         │
               ▼                         │
┌─────────────────────────────┐          │
│ Quality / Safety Checker    │          │
└──────────────┬──────────────┘          │
               │                         │
               ▼                         │
┌─────────────────────────────┐          │
│       Human Review          │          │
└──────────────┬──────────────┘          │
               │                         │
               ▼                         │
┌─────────────────────────────┐          │
│ Final Case-to-Action Packet │          │
└─────────────────────────────┘          │
                                         │
                     ┌───────────────────┴────────────┐
                     │ Approved Resource Knowledge    │
                     │ Base + Source Metadata         │
                     └────────────────────────────────┘
```

## 3. Architectural Principles

### 3.1 Orchestrated workflow

The orchestrator controls the sequence and state transitions.

### 3.2 Structured outputs

Every agent must return a validated structured object rather than
free-form prose wherever possible.

### 3.3 Evidence before recommendation

The system should retrieve and compare evidence before producing the
final recommendation.

### 3.4 Explicit uncertainty

Unknown information must remain unknown.

### 3.5 Human-in-the-loop

Consequential actions stop at a human review checkpoint.

### 3.6 Deterministic business logic where possible

Rules such as:

-   schema validation;
-   required fields;
-   evidence presence;
-   confidence thresholds;
-   status transitions;

should be implemented with normal code rather than relying entirely on
an LLM.

### 3.7 LLMs for interpretation and synthesis

Use the model for:

-   understanding messy language;
-   extracting structured facts;
-   semantic matching;
-   summarization;
-   generating focused questions;
-   explaining evidence.

Do not use the model as the sole source of truth for resource
requirements.

## 4. Core Components

### 4.1 Frontend

Responsibilities:

-   case creation;
-   case progress;
-   agent activity;
-   evidence display;
-   recommendations;
-   warnings;
-   human review;
-   evaluation dashboard.

The UI must prioritize clarity over visual complexity.

### 4.2 API/Application Layer

Responsibilities:

-   receive requests;
-   validate inputs;
-   create/update cases;
-   invoke orchestrator;
-   expose results;
-   manage evaluation runs.

### 4.3 Orchestrator

The orchestrator manages:

``` text
CASE_CREATED
→ INTAKE_COMPLETE
→ NEEDS_ASSESSED
→ RESOURCES_RETRIEVED
→ EVIDENCE_VERIFIED
→ ACTION_PLAN_READY
→ QUALITY_CHECKED
→ HUMAN_REVIEW
→ COMPLETED
```

If a stage fails, the orchestrator should record the failure and either
retry safely or move the case to `NEEDS_HUMAN_ATTENTION`.

## 5. Agent Specifications

### Agent A --- Intake Agent

#### Input

Natural-language case description.

#### Tasks

-   extract facts;
-   identify missing information;
-   normalize terminology;
-   preserve uncertainty;
-   identify contradictions already present.

#### Output

`CaseProfile`.

#### Must not

-   invent personal facts;
-   declare eligibility;
-   fabricate documents.

------------------------------------------------------------------------

### Agent B --- Needs Assessment Agent

#### Input

`CaseProfile`.

#### Tasks

-   identify immediate needs;
-   identify secondary needs;
-   prioritize needs;
-   explain why each need was identified.

#### Output

`NeedsAssessment`.

------------------------------------------------------------------------

### Agent C --- Resource Matching Agent

#### Input

`CaseProfile` + `NeedsAssessment` + approved resource records.

#### Tasks

-   retrieve candidates;
-   compare relevant requirements;
-   rank candidates;
-   identify missing information.

#### Output

`ResourceMatch[]`.

#### Must not

-   treat semantic similarity as proof of eligibility;
-   recommend resources without a source/reference.

------------------------------------------------------------------------

### Agent D --- Evidence Verification Agent

#### Input

`CaseProfile` + `NeedsAssessment` + `ResourceMatch[]`.

#### Tasks

-   verify each recommendation against available evidence;
-   detect unsupported claims;
-   detect contradictions;
-   identify unresolved requirements;
-   downgrade uncertain matches.

#### Output

`VerifiedRecommendation[]`.

------------------------------------------------------------------------

### Agent E --- Action Planning Agent

#### Input

verified recommendations and unresolved requirements.

#### Tasks

-   prioritize actions;
-   identify prerequisites;
-   order steps;
-   prepare a concise caseworker plan.

#### Output

`ActionPlan`.

------------------------------------------------------------------------

### Agent F --- Quality/Safety Checker

This can be implemented as a specialized agent or a hybrid agent +
deterministic validation layer.

#### Tasks

-   ensure no unsupported eligibility statement is presented as fact;
-   ensure every recommendation has evidence;
-   ensure missing critical information is surfaced;
-   ensure the output contains human-review status;
-   check for policy/safety violations.

#### Output

`QualityReport`.

## 6. Agent Communication

Use typed schemas.

Example conceptual case object:

``` json
{
  "case_id": "CASE-001",
  "facts": [
    {
      "field": "employment_status",
      "value": "unemployed",
      "status": "explicit",
      "source": "user_input"
    }
  ],
  "needs": [],
  "documents": [],
  "constraints": [],
  "contradictions": []
}
```

Example recommendation:

``` json
{
  "resource_id": "RES-001",
  "status": "potential_match",
  "supporting_evidence": [
    {
      "case_fact": "employment_status",
      "resource_requirement": "..."
    }
  ],
  "missing_information": [
    "current_household_income"
  ],
  "source_id": "SRC-001",
  "human_review_required": true
}
```

## 7. Knowledge Base

The resource knowledge base is the system's controlled source of
resource information.

### Resource record

``` text
resource_id
name
category
geography
description
requirements[]
required_documents[]
service_steps[]
contact_information
source_id
source_url_or_reference
verified_at
status
notes
```

### Source record

``` text
source_id
publisher
title
reference
retrieved_at
verification_status
notes
```

For the hackathon MVP, use public/approved or synthetic resource data.
Do not depend on uncontrolled live data for the core evaluation.

## 8. Retrieval Strategy

Recommended pipeline:

``` text
Needs + case constraints
        ↓
Structured filters
        ↓
Semantic retrieval
        ↓
Top candidate resources
        ↓
Requirement comparison
        ↓
Verification
```

Use structured filtering before semantic ranking whenever practical.

This reduces irrelevant matches.

## 9. Memory and State

Case memory should preserve:

-   original case input;
-   normalized facts;
-   questions asked;
-   answers;
-   identified needs;
-   retrieved resources;
-   evidence;
-   verification results;
-   reviewer actions;
-   final plan.

The system should not persist unnecessary sensitive data.

For the hackathon, synthetic case IDs are preferred.

## 10. Human Review State

The reviewer view must show:

``` text
CASE SUMMARY
        ↓
RECOMMENDATIONS
        ↓
EVIDENCE
        ↓
MISSING INFORMATION
        ↓
WARNINGS
        ↓
PROPOSED ACTIONS
        ↓
[Approve] [Modify] [Request Information]
```

No external consequential action should occur from the prototype.

## 11. Error Handling

### Agent failure

-   record failed stage;
-   retry only when the retry has a clear reason;
-   otherwise surface human attention required.

### Invalid structured output

-   validate;
-   attempt constrained retry;
-   reject if still invalid.

### Missing resource data

Return:

``` text
No verified resource match found from the approved dataset.
```

Do not fill the gap with fabricated information.

### Conflicting case facts

Surface the conflict.

Example:

``` text
Potential conflict:
Employment status is described as "unemployed"
but household income information indicates current employment.

Human clarification required.
```

## 12. Observability

For every evaluation run, record:

-   case ID;
-   workflow stage;
-   agent;
-   input/output schema;
-   tool/resource calls;
-   retries;
-   verification result;
-   final result;
-   latency;
-   cost where available.

Sensitive information must not be logged.

## 13. Evaluation Architecture

``` text
Evaluation Cases
      │
      ├──────────────► Baseline Runner
      │
      └──────────────► Agentic Runner
                              │
                              ▼
                         Scoring Layer
                              │
                              ▼
                    Results + Error Analysis
```

The scorer must apply the same rubric to both systems.

## 14. Security and Privacy

-   Keep credentials in environment variables.
-   Never commit `.env`.
-   Provide `.env.example`.
-   Use synthetic cases for the public repository.
-   Avoid unnecessary personal data fields.
-   Sanitize logs.
-   Treat resource-source URLs as data, not executable instructions.

## 15. Design Decision: Why Multiple Agents?

The architecture should justify each agent by a specific failure mode.

Example:

``` text
Baseline failure:
Messy input causes important facts to be missed.
→ Add Intake Agent.

Baseline failure:
Correct resources are found but missing requirements are ignored.
→ Add Verification Agent.

Baseline failure:
Recommendations are plausible but unsupported.
→ Add Evidence Verification.

Baseline failure:
Correct recommendations are presented as an overwhelming list.
→ Add Action Planning.
```

These are hypotheses initially. The final changelog must reflect actual
experimental evidence.

## 16. MVP Simplification Rule

If a separate agent does not measurably improve the workflow, remove it.

A smaller reliable architecture is preferred over a larger decorative
multi-agent architecture.
