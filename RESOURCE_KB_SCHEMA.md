# MigrantAid — Resource Knowledge Base Schema

## 1. Purpose

The resource knowledge base is the controlled source of information used by MigrantAid when finding and comparing support resources.

The model must not invent resource records.

---

## 2. Design Principles

1. Every resource has a stable ID.
2. Every resource has provenance.
3. Requirements are represented separately from descriptive text.
4. Geographic scope is explicit.
5. Required documents are explicit.
6. Verification status is explicit.
7. Resource data is versioned.
8. A retrieval score is not an eligibility decision.
9. Unknown requirements remain unknown.
10. Stale/unverified resources must be visibly flagged.

---

## 3. Resource Record

Recommended structure:

```json
{
  "resource_id": "RES-001",
  "name": "Example Employment Support Centre",
  "category": "employment",
  "geography": {
    "country": "India",
    "state": "Maharashtra",
    "cities": ["Pune"]
  },
  "description": "Example employment support service.",
  "requirements": [
    {
      "requirement_id": "REQ-001",
      "field": "employment_status",
      "operator": "equals",
      "value": "unemployed",
      "importance": "critical",
      "evidence_required": true
    }
  ],
  "required_documents": [
    {
      "document": "identity_document",
      "required": true
    }
  ],
  "service_steps": [
    "Confirm requirements",
    "Contact centre",
    "Complete intake"
  ],
  "contact_information": {
    "phone": "SYNTHETIC",
    "website": "SYNTHETIC"
  },
  "source_id": "SRC-001",
  "verified_at": "2026-08-01",
  "status": "verified",
  "dataset_version": "v1.0",
  "notes": ""
}
```

The example values are placeholders and must not be treated as real services.

---

## 4. Required Fields

### `resource_id`

Unique stable identifier.

Example:

```text
RES-001
```

### `name`

Human-readable resource name.

### `category`

Controlled category.

Recommended initial values:

```text
basic_support
employment
housing
documentation
education
financial_assistance
transport
health_navigation
other
```

### `geography`

Defines where the resource operates.

### `requirements`

Structured conditions used for comparison.

### `required_documents`

Documents needed for the resource workflow.

### `source_id`

References a source record.

### `verified_at`

Date the record was last verified.

### `status`

Recommended:

```text
verified
unverified
needs_review
inactive
```

---

## 5. Requirement Schema

A requirement should contain:

```text
requirement_id
field
operator
value
importance
evidence_required
source_reference
```

Supported operators may include:

```text
equals
not_equals
contains
in
not_in
greater_than
less_than
greater_or_equal
less_or_equal
exists
```

Do not allow arbitrary executable expressions from resource data.

---

## 6. Requirement Evaluation

A requirement can resolve to:

```text
satisfied
not_satisfied
unknown
conflict
not_applicable
```

Example:

```text
Case:
employment_status = unemployed

Requirement:
employment_status equals unemployed

Result:
satisfied
```

If the case has no employment information:

```text
Result:
unknown
```

The system must not convert `unknown` into `satisfied`.

---

## 7. Evidence Mapping

Every important recommendation should map case evidence to resource requirements.

Example:

```json
{
  "case_fact_id": "FACT-004",
  "requirement_id": "REQ-001",
  "result": "satisfied",
  "evidence": "Case narrative states the worker recently lost employment.",
  "source": "user_input"
}
```

---

## 8. Source Record

Recommended structure:

```json
{
  "source_id": "SRC-001",
  "publisher": "Synthetic Dataset",
  "title": "Example Resource Record",
  "reference": "SYNTHETIC-001",
  "retrieved_at": "2026-08-01",
  "verification_status": "verified",
  "dataset_version": "v1.0",
  "notes": "Synthetic resource for hackathon evaluation."
}
```

For real public sources, add:

- publisher;
- title;
- source URL/reference;
- retrieval date;
- verification date;
- relevant section/page if applicable.

---

## 9. Resource Matching Rules

### Strong match

Use only when:

- relevant requirements are satisfied by available evidence;
- no critical requirement is unknown;
- no contradiction is present;
- resource status is verified.

### Potential match

Use when:

- the resource is relevant;
- one or more non-final conditions remain unresolved;
- the evidence is not enough for a stronger conclusion.

### Insufficient information

Use when:

- a critical requirement cannot be evaluated.

### Conflict detected

Use when:

- case evidence contradicts itself;
- or case evidence conflicts with a requirement.

### No verified match

Use when:

- no resource in the approved dataset can be responsibly recommended.

---

## 10. Retrieval vs Eligibility

These are separate concepts.

```text
Retrieval:
"Is this resource relevant enough to inspect?"

Eligibility/requirement assessment:
"Does the available evidence support the resource requirements?"
```

A high retrieval score must never be presented as proof of eligibility.

---

## 11. Resource Versioning

Every evaluation must record:

```text
resource_dataset_version
```

Baseline and final must use the same version.

---

## 12. Initial Resource Dataset

The synthetic resource dataset is stored in:

```text
data/resources.json
```

The initial dataset should be deliberately sufficient to test:

- clear matches;
- potential matches;
- missing requirements;
- multiple candidates;
- no-match cases;
- contradictory cases.

