# MigrantAid — Evaluation Dataset Specification

## 1. Purpose

This specification defines the fixed evaluation set and scoring process for comparing:

- the simple baseline;
- the final MigrantAid agentic workflow.

The evaluation must measure whether the workflow solves the target problem better, not merely whether it produces longer or more impressive text.

---

## 2. Dataset Policy

The dataset is synthetic.

No real person's sensitive information should be included.

Every case has a stable:

```text
case_id
```

Do not change case IDs between baseline and final evaluation.

---

## 3. Required Case Mix

The initial evaluation set contains **20 cases**.

| Category | Minimum |
|---|---:|
| Ordinary / straightforward | 4 |
| Incomplete information | 4 |
| Multi-need | 3 |
| Ambiguous | 3 |
| Contradictory | 2 |
| No verified match | 2 |
| Multiple possible matches | 2 |
| Deliberately challenging | 2 |

A case may belong to more than one category.

---

## 4. Required Case Fields

Each case must contain:

```text
case_id
title
category
difficulty
narrative
known_facts
known_needs
critical_missing_information
contradictions
expected_resource_ids
expected_resource_status
expected_actions
scoring_notes
```

---

## 5. Ground Truth Policy

Ground truth should be written by the dataset author before the final system is evaluated.

Ground truth may identify:

- the primary need;
- secondary needs;
- relevant resource IDs;
- required missing information;
- expected safety/uncertainty behavior;
- acceptable next steps.

Ground truth should not force a single wording.

---

## 6. Primary Metric — VARR

A case receives a maximum of 100 points across six dimensions:

| Dimension | Points |
|---|---:|
| Primary need identified correctly | 20 |
| Appropriate resource identified | 20 |
| Evidence supports recommendation | 20 |
| Critical missing information identified | 15 |
| No unsupported eligibility claim | 15 |
| Actionable next step | 10 |
| **Total** | **100** |

### Success threshold

A case is considered successfully resolved when:

- total score >= 80;
- evidence score >= 15/20;
- unsupported-claim score = 15/15;
- an appropriate action is present.

Then:

```text
VARR = successful cases / total cases
```

This threshold must be frozen before the final comparison.

---

## 7. Secondary Scoring

### Resource-match accuracy

```text
correct relevant resource decisions
/
cases where a resource decision is expected
```

### Missing-information detection

Measure whether critical missing facts are identified.

### Unsupported-recommendation rate

```text
recommendations lacking adequate evidence
/
total recommendations
```

Lower is better.

### Evidence-traceability rate

```text
recommendations with traceable evidence
/
total recommendations
```

### Reviewer correction rate

Percentage of recommendations requiring meaningful human correction.

### Efficiency

Record:

- latency;
- model calls;
- approximate token usage;
- approximate cost.

---

## 8. Fair Baseline

The baseline must use:

- same cases;
- same resource dataset;
- equivalent case information;
- same model family where practical.

Recommended baseline:

```text
SYSTEM:
You are a community support assistant.

INPUT:
Case narrative + approved resource records.

TASK:
Recommend relevant resources and next steps.

OUTPUT:
A concise recommendation.
```

The baseline should not have access to the final system's hidden intermediate state.

---

## 9. Final System Evaluation

The final system receives the same narrative and approved resource dataset.

Its additional processing is the workflow being tested:

```text
Intake
→ Needs
→ Retrieval/Matching
→ Verification
→ Action Planning
→ Quality Check
```

---

## 10. Blind Scoring

Where practical, score baseline and final outputs without showing the evaluator which system produced them.

This reduces evaluator bias.

---

## 11. Error Analysis Categories

Every failed or partially successful case should be assigned one or more failure categories:

```text
INTAKE_MISS
NEED_MISS
RETRIEVAL_MISS
MATCHING_MISS
MISSING_INFO_MISS
EVIDENCE_MISS
CONTRADICTION_MISS
UNSUPPORTED_CLAIM
ACTION_PLAN_MISS
HUMAN_REVIEW_MISS
RESOURCE_DATA_LIMITATION
OTHER
```

---

## 12. Challenging Cases

At least two cases should be designed to expose a meaningful baseline weakness.

A strong challenging case has this pattern:

```text
Plausible surface match
+
hidden/missing requirement
+
enough information to detect uncertainty
```

The expected behavior is not necessarily "find the answer."

The expected behavior may be:

> recognize that the evidence is insufficient and ask the right question.

---

## 13. Evaluation Output Schema

Conceptual result:

```json
{
  "case_id": "CASE-CHALLENGE-001",
  "system": "agentic",
  "score": 92,
  "successful": true,
  "dimensions": {
    "primary_need": 20,
    "resource": 20,
    "evidence": 18,
    "missing_information": 15,
    "unsupported_claim": 15,
    "actionable_next_step": 4
  },
  "failure_categories": [],
  "latency_ms": 0,
  "estimated_cost": 0
}
```

The values above are an example schema, not actual evaluation results.

---

## 14. Dataset Freeze

Before final evaluation:

```text
Dataset version:
Freeze date:
Number of cases:
Number of resources:
Scoring rubric version:
```

After freezing:

- do not edit ground truth to improve scores;
- do not remove difficult cases;
- document any correction as a dataset-version change;
- rerun both baseline and final when the dataset changes.

---

## 15. Initial Dataset

The first 20 synthetic cases are stored in:

```text
data/evaluation_cases.json
```

The case descriptions and ground-truth expectations are intentionally varied to test:

- incomplete information;
- ambiguity;
- contradictions;
- multi-need situations;
- multiple candidate resources;
- absence of a verified match;
- evidence-aware behavior.
