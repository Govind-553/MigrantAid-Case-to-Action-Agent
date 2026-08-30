# MigrantAid --- User Flow Document

## 1. Purpose

This document defines the complete user journey from case creation to
human-reviewed action plan.

The primary user is a community worker assisting a migrant worker.

## 2. Primary User Journey

``` text
START
  ↓
Community worker opens MigrantAid
  ↓
Create new case
  ↓
Enter beneficiary situation in natural language
  ↓
System extracts structured case information
  ↓
Worker reviews/corrects extracted facts
  ↓
System identifies needs
  ↓
System identifies missing critical information
  ↓
Worker answers focused follow-up questions
  ↓
System searches approved resource knowledge base
  ↓
System produces candidate matches
  ↓
Evidence verification
  ↓
System flags uncertainty/contradictions
  ↓
Action planning
  ↓
Quality/safety check
  ↓
Human review
  ↓
Worker approves/modifies/request information
  ↓
Final case-to-action packet
  ↓
Case saved for follow-up
  ↓
END
```

## 3. Detailed Flow

### Step 1 --- Create Case

UI:

``` text
New Case

Describe the person's situation:
[................................................]
[................................................]

[Start Case Analysis]
```

The input should allow a worker to write naturally.

Example:

> "A worker came to Pune from Bihar for work. He lost his job recently
> and has two children. He has Aadhaar and a bank account but is unsure
> what support is available."

Do not require the worker to understand a complicated form before using
the system.

------------------------------------------------------------------------

### Step 2 --- Intake Processing

The Intake Agent converts the narrative into structured information.

UI:

``` text
Extracted Information

Location:
Pune

Origin:
Bihar

Employment:
Recently unemployed

Household:
Two children

Documents:
Aadhaar
Bank account

Unknown:
Current household income
Other household income
```

The worker can edit facts.

Buttons:

``` text
[Confirm Information]
[Edit]
[Add Information]
```

The workflow should not proceed with an invented value.

------------------------------------------------------------------------

### Step 3 --- Needs Assessment

The Needs Assessment Agent identifies likely needs.

Example:

``` text
Priority Needs

1. Immediate/basic support
   Reason: reported loss of income

2. Employment assistance
   Reason: recently unemployed

3. Documentation assistance
   Reason: some potentially relevant information is missing
```

The worker can correct the classification.

------------------------------------------------------------------------

### Step 4 --- Focused Questions

The system should ask only questions that can change the result.

Example:

``` text
Before searching for resources, we need:

1. Does anyone else in the household currently earn income?
2. What is the approximate current household income?
3. Which documents are currently available?
```

The purpose is not to collect unnecessary personal information.

------------------------------------------------------------------------

### Step 5 --- Resource Matching

The system searches the approved resource dataset.

UI:

``` text
Potential Resources

Resource A
Match: Strong
Reason: requirements appear consistent with case facts
Missing: current income confirmation
Source: SRC-001

Resource B
Match: Potential
Reason: geographic/service conditions appear relevant
Missing: required document confirmation
Source: SRC-008
```

Each result must be traceable.

------------------------------------------------------------------------

### Step 6 --- Verification

The verification stage checks the recommendations.

UI:

``` text
Verification

✓ Source available
✓ Case evidence found
✓ Requirement comparison completed
⚠ Current income not verified
✓ No contradiction detected

Recommendation status:
HUMAN REVIEW REQUIRED
```

If verification fails:

``` text
Recommendation withheld

Reason:
The available case information does not support the required condition.

Action:
Ask for clarification or investigate another resource.
```

------------------------------------------------------------------------

### Step 7 --- Action Planning

The Action Planning Agent creates an ordered plan.

Example:

``` text
Recommended Next Steps

1. Confirm current household income
   Priority: High
   Why: required to resolve an eligibility uncertainty

2. Review Resource A with the caseworker
   Priority: High
   Why: current evidence suggests a potential match

3. Collect missing document
   Priority: Medium
   Why: required by Resource A

4. Follow up on employment assistance
   Priority: Medium
```

------------------------------------------------------------------------

### Step 8 --- Quality/Safety Check

Before human review, the system performs a final check.

``` text
Final Quality Check

✓ No unsupported eligibility claims
✓ Recommendations have sources
✓ Missing information is visible
✓ Conflicting facts checked
✓ Human review required
✓ No external action triggered
```

------------------------------------------------------------------------

### Step 9 --- Human Review

The community worker sees:

``` text
CASE REVIEW

Situation
Needs
Potential Resources
Evidence
Missing Information
Warnings
Action Plan

[Approve Plan]
[Modify]
[Request More Information]
[Reject Recommendation]
```

The worker remains responsible for the consequential decision.

------------------------------------------------------------------------

### Step 10 --- Final Case Packet

The system produces:

``` text
CASE-001

SUMMARY
...

PRIORITY NEEDS
...

POTENTIAL RESOURCES
...

EVIDENCE
...

MISSING INFORMATION
...

WARNINGS
...

APPROVED NEXT STEPS
...

FOLLOW-UP
...
```

## 4. Alternative User Flows

### 4.1 Incomplete case

``` text
Input
 ↓
Insufficient facts
 ↓
Ask focused questions
 ↓
User supplies answers
 ↓
Continue workflow
```

If the worker cannot provide the information:

``` text
Status:
Insufficient information

Recommended action:
Human follow-up required.
```

### 4.2 Contradictory case

``` text
Input
 ↓
Contradiction detected
 ↓
Pause recommendation
 ↓
Show conflicting facts
 ↓
Ask worker to clarify
 ↓
Continue
```

### 4.3 No matching resource

``` text
Input
 ↓
Needs identified
 ↓
Search approved database
 ↓
No verified match
 ↓
Tell worker no verified match was found
 ↓
Suggest additional information or human investigation
```

Never fabricate a match.

### 4.4 Multiple possible matches

``` text
Several candidates
 ↓
Rank by evidence strength
 ↓
Show differences
 ↓
Highlight missing information
 ↓
Human chooses next action
```

## 5. Challenging Demonstration Flow

The demo should include one case designed to expose a baseline failure.

Example:

``` text
Case description
 ↓
Baseline immediately recommends a resource
 ↓
MigrantAid detects a missing requirement
 ↓
Verification agent flags uncertainty
 ↓
System asks one targeted question
 ↓
Caseworker receives a safer recommendation
```

The exact challenging case should be finalized after baseline
experiments reveal a meaningful failure mode.

## 6. Evaluation User Flow

For evaluation, the user should not manually operate every case.

``` text
Evaluation dataset
      ↓
Baseline runner
      ↓
Baseline outputs
      ↓
Final agent runner
      ↓
Agent outputs
      ↓
Same scorer
      ↓
Metrics
      ↓
Error analysis
      ↓
Changelog
```

## 7. UI State Model

Recommended case states:

``` text
DRAFT
INTAKE_PROCESSING
INTAKE_REVIEW
NEEDS_ASSESSMENT
FOLLOW_UP_REQUIRED
RESOURCE_MATCHING
VERIFICATION
ACTION_PLAN_READY
QUALITY_CHECK
HUMAN_REVIEW
APPROVED
MODIFIED
MORE_INFORMATION_REQUIRED
COMPLETED
FAILED
```

## 8. User Experience Rules

1.  Never hide uncertainty.
2.  Never make the worker search through long AI-generated paragraphs
    when structured information will do.
3.  Show evidence close to the recommendation.
4.  Show why the system is asking a question.
5.  Keep human approval visible.
6.  Avoid alarming or authoritative language.
7.  Use plain language.
8.  Make it easy to correct an extracted fact.
9.  Never imply that a potential match is a guaranteed benefit.
10. Keep the final case packet concise enough for real casework.

## 9. Demo Flow

The 5-minute demonstration should follow:

``` text
0:00–0:30
Problem + user

0:30–1:00
Current/manual workflow + baseline

1:00–3:30
One realistic MigrantAid execution

3:30–4:15
Challenging case / failure caught by verification

4:15–4:45
Measured comparison

4:45–5:00
Main improvement + learned insight
```

This follows the hackathon's requested video structure.
