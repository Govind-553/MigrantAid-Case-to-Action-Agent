# MigrantAid --- Project Requirement Document

## 1. Document Purpose

This document is the implementation contract for MigrantAid.

The development agent must read this document before writing application
code and implement the project requirements in the order defined here.

MigrantAid is an **agentic case-to-action assistant for community
workers who support migrant workers**. It is not a generic chatbot and
it must not present itself as an authority that approves, rejects, or
guarantees a person's eligibility for a benefit or service.

The project is designed for the Micro1 Agentic Workflows Hackathon. The
hackathon asks teams to select a specific meaningful problem, identify
the bottleneck, use agents purposefully, demonstrate improvement over a
fair baseline, and make the result reproducible.

## 2. Hackathon Alignment

The solution must explicitly address the four questions:

1.  **Who has the problem?**
    -   Primary user: community workers, NGO volunteers,
        migrant-resource-centre workers, or similar frontline helpers.
    -   Beneficiary: migrant workers and their families.
2.  **What bottleneck makes it worth solving?**
    -   A worker's situation is usually expressed as an incomplete,
        messy real-world story.
    -   The caseworker must turn that story into structured needs,
        search relevant approved resources, compare requirements,
        identify missing information/documents, verify evidence, and
        create an actionable next-step plan.
    -   This is repetitive, multi-step work and can lead to missed
        information, inconsistent recommendations, or unsupported
        conclusions.
3.  **Does the agent solve it well?**
    -   The final workflow must be evaluated against a simple baseline
        using the same cases.
    -   The system must demonstrate measurable improvement.
4.  **Can another person reproduce the result?**
    -   A clean-environment setup guide, fixed evaluation cases,
        baseline implementation, final implementation, expected outputs,
        versions, approximate runtime, and approximate cost must be
        documented.

## 3. Product Vision

### Product statement

> Turn a migrant worker's incomplete real-world situation into a
> structured, evidence-backed, human-reviewable action plan for a
> community worker.

### Product principles

-   **Human-first:** optimize the workflow of the community worker
    rather than replacing them.
-   **Evidence-first:** every recommendation must be traceable to
    approved resource data and/or explicit case evidence.
-   **Uncertainty-aware:** the system must distinguish facts,
    assumptions, potential matches, missing information, and verified
    information.
-   **No autonomous consequential decisions:** the system recommends and
    prepares; a qualified human reviews consequential outputs.
-   **Reproducible:** all evaluation claims must be generated from
    documented, repeatable experiments.
-   **Purposeful agents:** each agent must exist because a specific
    workflow problem justifies it.
-   **Minimal sufficient complexity:** do not add agents, tools, memory,
    or orchestration merely to make the architecture look sophisticated.

## 4. Target User

### Primary user

A frontline community worker who assists migrant workers.

The worker may need to:

-   understand a beneficiary's situation;
-   identify immediate and secondary needs;
-   locate potentially relevant resources;
-   determine what information is missing;
-   organize supporting documents;
-   prepare an action plan;
-   explain uncertainty to the beneficiary;
-   record a case for follow-up.

### Beneficiary

A migrant worker and, where relevant, their household.

### Important boundary

The MVP is an **assistive casework system**. It must not claim to
replace a government authority, NGO caseworker, legal professional, or
other qualified decision-maker.

## 5. Problem Definition

### Current workflow

A simplified manual workflow is:

``` text
Beneficiary explains situation
        ↓
Community worker asks questions
        ↓
Worker interprets needs
        ↓
Worker searches multiple information sources
        ↓
Worker compares requirements
        ↓
Worker identifies missing documents/information
        ↓
Worker decides what to investigate next
        ↓
Worker prepares instructions or referrals
        ↓
Worker follows up
```

### Core bottlenecks

1.  Unstructured case information.
2.  Fragmented resource information.
3.  Eligibility/requirement interpretation.
4.  Missing or contradictory case information.
5.  Weak evidence traceability.
6.  Repetitive case preparation.
7.  Inconsistent quality between workers.
8.  Time spent searching and assembling information.

## 6. Product Scope

### In scope for MVP

-   Create a case from natural-language input.
-   Extract structured case facts.
-   Identify immediate and secondary needs.
-   Identify missing information.
-   Search an approved resource knowledge base.
-   Match resources to case facts.
-   Compare resource requirements with available case evidence.
-   Flag contradictions and uncertainty.
-   Produce an evidence-backed recommendation list.
-   Produce a prioritized action plan.
-   Produce a human-reviewable case summary.
-   Show source/evidence traceability.
-   Store case state during the workflow.
-   Provide an evaluation mode for baseline vs agent comparison.
-   Capture representative agent trajectories.

### Explicitly out of scope for MVP

-   Automatically applying for or submitting benefits.
-   Automatically approving or rejecting eligibility.
-   Financial transactions.
-   Medical diagnosis or treatment decisions.
-   Legal representation.
-   Autonomous communication that creates consequential commitments.
-   Scraping arbitrary websites without a controlled data policy.
-   Storing real beneficiaries' sensitive personal information for the
    hackathon demo.
-   Presenting model confidence as a legally valid eligibility decision.

## 7. Functional Requirements

### FR-01 --- Case intake

The system shall accept a natural-language case description.

It shall extract, where available:

-   current location;
-   origin/location history;
-   employment status;
-   income information;
-   household composition;
-   dependents;
-   immediate needs;
-   longer-term needs;
-   available documents;
-   missing documents mentioned explicitly;
-   constraints;
-   other relevant facts.

The system must preserve uncertainty instead of inventing missing
values.

### FR-02 --- Case normalization

The system shall convert extracted information into a structured case
object.

Each field should carry enough metadata to distinguish:

-   explicitly provided;
-   inferred;
-   unknown;
-   conflicting.

### FR-03 --- Needs assessment

The system shall classify needs into categories such as:

-   immediate/basic needs;
-   employment/income;
-   documentation;
-   housing;
-   education;
-   other categories supported by the approved dataset.

The category taxonomy must be configurable.

### FR-04 --- Missing-information detection

The system shall identify information that is necessary to evaluate a
potential resource but is absent from the case.

It must ask focused follow-up questions rather than asking for every
possible field.

### FR-05 --- Resource retrieval

The system shall retrieve candidate resources from an approved resource
knowledge base.

Each resource record should contain:

-   resource ID;
-   resource name;
-   service category;
-   geographic scope;
-   eligibility/requirements text;
-   required documents;
-   contact/action information where available;
-   source;
-   source date or verification date;
-   status;
-   notes.

### FR-06 --- Resource matching

The system shall compare case facts against resource requirements.

It must classify matches using controlled states such as:

-   `potential_match`;
-   `strong_match`;
-   `insufficient_information`;
-   `not_supported_by_available_evidence`;
-   `conflict_detected`.

The exact labels can be refined during implementation, but the system
must not collapse uncertainty into a binary eligible/not-eligible
answer.

### FR-07 --- Evidence traceability

Every recommended resource must show:

-   why it was retrieved;
-   which case facts support the recommendation;
-   which resource requirements are satisfied by those facts;
-   which requirements remain unknown;
-   source/reference ID;
-   verification status.

### FR-08 --- Verification

A dedicated verification stage shall inspect the draft recommendation
before it is shown as final.

It shall check:

-   unsupported claims;
-   missing evidence;
-   contradictory facts;
-   stale/unverified resource records;
-   inappropriate certainty;
-   missing required fields;
-   recommendation/resource mismatch.

### FR-09 --- Action planning

The system shall create a prioritized action plan.

Each action should include:

-   action;
-   priority;
-   reason;
-   prerequisite;
-   responsible human role where relevant;
-   evidence/reference;
-   unresolved uncertainty.

### FR-10 --- Human review

The final case packet shall contain a visible human-review state.

The reviewer must be able to:

-   approve;
-   modify;
-   request more information;
-   reject a recommendation;
-   mark a case for follow-up.

For the hackathon prototype, consequential actions must remain
simulated.

### FR-11 --- Case summary

The system shall generate a concise case summary suitable for a
community worker.

The summary must clearly separate:

-   known facts;
-   identified needs;
-   potential resources;
-   missing information;
-   warnings;
-   proposed next steps.

### FR-12 --- Evaluation mode

The application shall support a repeatable evaluation pipeline that can
run:

-   baseline;
-   final agentic solution;
-   same evaluation cases;
-   same scoring rubric.

The evaluation shall produce machine-readable results.

## 8. Non-Functional Requirements

### NFR-01 --- Reliability

The system must prefer an explicit `unknown` or `needs verification`
state over an unsupported assertion.

### NFR-02 --- Explainability

Recommendations must be traceable to case evidence and approved resource
records.

### NFR-03 --- Reproducibility

A second developer must be able to run the project from a clean
environment using the README.

### NFR-04 --- Privacy

Use synthetic or approved anonymous data for the demo and evaluation.

No secrets, API keys, or private beneficiary records may be committed.

### NFR-05 --- Safety

The UI must make it clear that recommendations are assistive and subject
to human review.

### NFR-06 --- Performance

The MVP should provide a complete case result within a practical demo
time. Actual runtime must be measured and documented rather than
guessed.

### NFR-07 --- Cost visibility

The evaluation must record approximate model/tool cost per case where
measurable.

## 9. Primary Success Metric

### Verified Actionable Resolution Rate (VARR)

A case is successful only when the final workflow:

1.  identifies the primary need correctly;
2.  identifies an appropriate candidate resource;
3.  provides supporting evidence;
4.  avoids unsupported eligibility claims;
5.  identifies critical missing information;
6.  provides an actionable next step.

Report:

``` text
VARR = successfully resolved cases / total evaluated cases
```

The exact scoring rubric for a successful case must be frozen before the
final evaluation.

## 10. Secondary Metrics

Measure where practical:

-   resource-match accuracy;
-   missing-information detection rate;
-   unsupported-recommendation rate;
-   evidence-traceability rate;
-   human time per case;
-   end-to-end latency;
-   cost per case;
-   reviewer correction rate.

## 11. Baseline Requirement

The baseline must represent a reasonable simple way of handling the same
task.

Recommended baseline:

``` text
Single general-purpose LLM
+
same approved resource knowledge base
+
single structured prompt
```

The baseline must receive the same evaluation cases and equivalent
relevant information.

Do not give the final solution hidden information that the baseline does
not receive unless the difference is explicitly documented.

## 12. Evaluation Requirements

Target at least 15--20 evaluation cases.

The dataset should contain:

-   ordinary cases;
-   incomplete cases;
-   multi-need cases;
-   ambiguous cases;
-   contradictory cases;
-   cases with no good match;
-   cases with several possible matches;
-   at least one deliberately challenging case.

The evaluation must report all cases, not only successful ones.

## 13. Improvement Changelog

Maintain an `IMPROVEMENT_CHANGELOG.md` in the root directory.

Each iteration must record:

-   problem/failure observed;
-   change attempted;
-   reason for the change;
-   evaluation result;
-   decision: keep, revise, or remove;
-   lesson learned.

Do not invent improvements after the fact.

## 14. Agent Trajectories

Representative trajectories must show:

-   initial agent instruction;
-   inputs;
-   tool calls;
-   tool responses;
-   intermediate reasoning/output relevant to the workflow;
-   retries;
-   verification;
-   human checkpoint;
-   final result.

Do not expose secrets or private data.

## 15. Definition of Done

MigrantAid is MVP-complete when:

-   all core functional requirements are implemented;
-   baseline and final workflows run on the same evaluation set;
-   the primary metric is calculated;
-   results are stored;
-   evidence traceability works;
-   human review is visible;
-   synthetic/approved data are used;
-   representative trajectories are captured;
-   setup and reproduction instructions work from a clean environment;
-   no unsupported eligibility decisions are presented as facts;
-   the project can be demonstrated end-to-end within the hackathon
    video constraints.

## 16. Implementation Order

The development agent must follow this order unless a documented
technical dependency requires otherwise:

1.  Create project skeleton.
2.  Define schemas and controlled vocabularies.
3.  Create synthetic evaluation dataset.
4.  Create approved resource dataset.
5.  Implement baseline.
6.  Implement intake.
7.  Implement needs assessment.
8.  Implement retrieval and matching.
9.  Implement evidence verification.
10. Implement action planning.
11. Implement human-review state.
12. Implement case summary.
13. Implement evaluation runner.
14. Run baseline.
15. Analyze baseline failures.
16. Add/revise agent capabilities based on evidence.
17. Run final evaluation.
18. Capture trajectories.
19. Build/refine UI.
20. Finalize documentation and reproduction guide.

## 17. Critical Implementation Rule

Do not build a complex multi-agent architecture before establishing the
baseline and evaluation cases.

The architecture must evolve from observed failures.

The goal is not to maximize the number of agents. The goal is to
maximize reliable improvement for the target user.
