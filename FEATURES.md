# MigrantAid --- Features List

## 1. Feature Prioritization

Features are divided into:

-   **P0 --- Required for MVP**
-   **P1 --- Important if time permits**
-   **P2 --- Future enhancement**

The implementation agent must finish P0 before spending significant
effort on P1/P2.

------------------------------------------------------------------------

# P0 --- MVP Features

## F-001 --- Case Creation

**Priority:** P0

Create a new case using a natural-language description.

### Acceptance criteria

-   User can enter a free-form case description.
-   System creates a unique case ID.
-   Original input is preserved.
-   Case starts in a valid state.

------------------------------------------------------------------------

## F-002 --- Structured Case Extraction

**Priority:** P0

Extract structured facts from the case description.

### Acceptance criteria

-   Extracted fields are displayed.
-   Unknown fields remain unknown.
-   User can edit extracted values.
-   Each important fact has a source/status.

------------------------------------------------------------------------

## F-003 --- Case Fact Review

**Priority:** P0

Allow the community worker to verify or correct extracted facts.

### Acceptance criteria

-   Facts can be edited.
-   Changes are stored.
-   The workflow uses the corrected values.

------------------------------------------------------------------------

## F-004 --- Needs Assessment

**Priority:** P0

Identify and prioritize the beneficiary's needs.

### Acceptance criteria

-   Needs are categorized.
-   Each need has a reason.
-   Needs can be reviewed by the worker.

------------------------------------------------------------------------

## F-005 --- Missing Information Detection

**Priority:** P0

Detect information that is important to the next stage.

### Acceptance criteria

-   System does not ask for every possible field.
-   Questions are linked to a specific unresolved requirement.
-   Worker can provide answers or mark information unavailable.

------------------------------------------------------------------------

## F-006 --- Approved Resource Knowledge Base

**Priority:** P0

Provide a controlled dataset of resources.

### Acceptance criteria

Every resource has:

-   unique ID;
-   description;
-   category;
-   geographic scope;
-   requirements;
-   documents;
-   source;
-   verification metadata.

------------------------------------------------------------------------

## F-007 --- Resource Retrieval

**Priority:** P0

Retrieve relevant candidate resources.

### Acceptance criteria

-   Results are relevant to identified needs.
-   Retrieval uses the approved dataset.
-   Each result has a resource ID.

------------------------------------------------------------------------

## F-008 --- Resource Matching

**Priority:** P0

Compare candidate resources with case facts.

### Acceptance criteria

-   Matching considers requirements.
-   Missing information is surfaced.
-   Potential matches are not presented as guaranteed eligibility.

------------------------------------------------------------------------

## F-009 --- Evidence Mapping

**Priority:** P0

Connect recommendations to evidence.

### Acceptance criteria

Each recommendation displays:

-   case evidence;
-   requirement;
-   source;
-   unresolved requirements.

------------------------------------------------------------------------

## F-010 --- Verification Agent

**Priority:** P0

Verify draft recommendations.

### Acceptance criteria

The verifier can detect:

-   unsupported claims;
-   missing evidence;
-   contradictions;
-   insufficient information;
-   unverified resource records.

------------------------------------------------------------------------

## F-011 --- Uncertainty Labels

**Priority:** P0

Show controlled statuses such as:

-   Potential match
-   Strong match
-   Insufficient information
-   Conflict detected
-   Human verification required

### Acceptance criteria

No ambiguous status is silently converted into "eligible."

------------------------------------------------------------------------

## F-012 --- Action Plan Generation

**Priority:** P0

Generate prioritized next steps.

### Acceptance criteria

Each step has:

-   priority;
-   action;
-   reason;
-   prerequisite if any.

------------------------------------------------------------------------

## F-013 --- Human Review

**Priority:** P0

Provide a review checkpoint.

### Acceptance criteria

Worker can:

-   approve;
-   modify;
-   request information;
-   reject a recommendation.

External consequential actions are simulated only.

------------------------------------------------------------------------

## F-014 --- Case Summary

**Priority:** P0

Generate a concise professional summary.

### Acceptance criteria

Summary contains:

-   situation;
-   needs;
-   recommendations;
-   evidence;
-   missing information;
-   warnings;
-   next steps.

------------------------------------------------------------------------

## F-015 --- Case History

**Priority:** P0

Maintain workflow state and important case events.

### Acceptance criteria

The system can show:

-   original input;
-   corrections;
-   questions;
-   answers;
-   recommendations;
-   verification;
-   reviewer decision.

------------------------------------------------------------------------

## F-016 --- Baseline Runner

**Priority:** P0

Run the simple baseline independently.

### Acceptance criteria

-   Baseline uses the same evaluation cases.
-   Baseline outputs are saved.
-   Baseline can be rerun.

------------------------------------------------------------------------

## F-017 --- Agent Evaluation Runner

**Priority:** P0

Run the final system on the same evaluation cases.

### Acceptance criteria

-   Results are machine-readable.
-   All cases are included.
-   Failed cases are retained.

------------------------------------------------------------------------

## F-018 --- Evaluation Scoring

**Priority:** P0

Calculate the primary metric and secondary metrics.

### Acceptance criteria

-   Same rubric is applied to baseline and final.
-   Results can be exported.
-   Raw outputs are retained for error analysis.

------------------------------------------------------------------------

## F-019 --- Agent Trajectory Capture

**Priority:** P0

Capture representative execution traces.

### Acceptance criteria

Trajectory includes:

-   agent;
-   input;
-   action/tool call;
-   output;
-   verification;
-   retry if any;
-   human checkpoint.

------------------------------------------------------------------------

## F-020 --- Safety and Data Controls

**Priority:** P0

Protect the project and demo data.

### Acceptance criteria

-   No secrets committed.
-   Synthetic/approved evaluation data.
-   No unnecessary sensitive fields.
-   Human-review warning is visible.

------------------------------------------------------------------------

# P1 --- Important Enhancements

## F-101 --- Multi-language Input

Allow caseworkers to enter cases in multiple supported languages.

The first version should only add this after the core workflow is
stable.

## F-102 --- Document Checklist

Display a checklist of:

``` text
Available
Missing
Needs verification
Not applicable
```

## F-103 --- Case Follow-Up

Allow a case to be marked for follow-up with a simulated date/status.

## F-104 --- Resource Freshness Indicator

Display whether a resource record is:

-   verified;
-   due for review;
-   unverified.

## F-105 --- Evaluation Dashboard

Show:

-   baseline vs final;
-   primary metric;
-   secondary metrics;
-   per-case failures;
-   latency;
-   cost.

## F-106 --- Reviewer Feedback Capture

Record why a reviewer changed or rejected an AI recommendation.

This can support future improvement experiments.

## F-107 --- Export Case Packet

Export the final case summary to a clean human-readable document.

------------------------------------------------------------------------

# P2 --- Future Features

These must not delay the hackathon MVP.

## F-201 --- Resource Data Update Pipeline

Automated controlled updates to the knowledge base.

## F-202 --- Organization-Specific Workflows

Allow NGOs to configure their own resource taxonomy and case fields.

## F-203 --- Multilingual Voice Intake

Voice-to-case workflow for workers who prefer speaking.

## F-204 --- Longitudinal Case Memory

Track cases over extended periods with appropriate privacy controls.

## F-205 --- Resource Feedback Loop

Use verified human outcomes to evaluate recommendation quality over
time.

------------------------------------------------------------------------

# 2. Features Explicitly Avoided

The following should not be implemented as core product features:

-   automatic benefit approval;
-   automatic benefit rejection;
-   autonomous legal advice;
-   medical diagnosis;
-   autonomous application submission;
-   financial transactions;
-   unverified "guaranteed eligibility";
-   generic open-ended chatbot as the primary interface;
-   arbitrary web scraping presented as authoritative data.

------------------------------------------------------------------------

# 3. Feature-to-Agent Mapping

  Feature                 Agent/Component
  ----------------------- ------------------------------------
  Case creation           UI/API
  Structured extraction   Intake Agent
  Needs assessment        Needs Agent
  Resource retrieval      Retrieval component
  Resource matching       Matching Agent
  Evidence mapping        Verification Agent
  Uncertainty             Verification + deterministic rules
  Action plan             Action Planning Agent
  Quality check           Quality/Safety layer
  Human review            UI + case state
  Case memory             State store
  Evaluation              Evaluation runner
  Trajectories            Observability layer

------------------------------------------------------------------------

# 4. Feature Development Rule

Every feature must answer:

> "What user bottleneck does this remove?"

If the answer is unclear, the feature should not be added to the MVP.

------------------------------------------------------------------------

# 5. MVP Demo Features

The minimum demo must show:

1.  Create case.
2.  Extract facts.
3.  Review facts.
4.  Identify needs.
5.  Detect missing information.
6.  Retrieve resources.
7.  Match resources.
8.  Show evidence.
9.  Verify recommendations.
10. Produce action plan.
11. Human review.
12. Show final case packet.
13. Show baseline vs final evaluation result.
14. Show one challenging case.
