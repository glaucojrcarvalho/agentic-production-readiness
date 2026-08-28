# Iteration 1 — Implementation Boundary

## Purpose

Iteration 1 tests one architectural change only: separate broad defect discovery from strict finding admission.

To keep the experiment interpretable, the first implementation uses **two model stages**, not three independent agents:

```text
case
  |
  v
Stage A: candidate reviewer
  |
  | candidate review
  v
Stage B: admission critic + consolidator
  |
  | admission report
  v
final review
```

The critic and consolidator are combined into one second-pass model call. A third model call would add cost and latency without testing a distinct hypothesis yet.

## Stage A — Candidate Reviewer

### Input

The candidate reviewer receives:

- exactly one `evals/cases/case_XX` directory;
- `schemas/review.schema.json`;
- the frozen canonical taxonomy through that schema;
- `prompts/candidate_review.md`.

It must not receive:

- `evals/ground_truth.yaml`;
- `evals/verify_cases.py`;
- results from other cases;
- baseline scores or known failure categories for the current case.

### Tools

It may:

- inspect files within the case directory;
- run safe local commands and tests scoped to the case;
- create temporary local probes outside the case when needed for verification, provided the case itself is not modified.

### Output

Stage A returns JSON matching `schemas/review.schema.json`.

At this boundary the object is a **candidate review**, not a human-facing final verdict. Findings may be broader than what Stage B ultimately admits.

## Stage B — Admission Critic + Consolidator

### Input

The admission stage receives:

- the same case directory available to Stage A;
- the candidate review JSON from Stage A;
- `schemas/review.schema.json`;
- `schemas/admission.schema.json`;
- `prompts/finding_admission.md`.

It does not receive hidden ground truth, hidden verification helpers, baseline scores, or outputs from other cases.

### Responsibilities

For every candidate finding, Stage B must decide whether it deserves human attention.

It may inspect code and tests and may rerun or construct safe probes to challenge the candidate evidence.

It must then:

1. admit or reject every candidate;
2. explain the admission decision using evidence, scope, materiality, and root cause;
3. merge admitted candidates that represent the same root cause;
4. preserve independent defects even when they share a category;
5. produce a final review that matches `schemas/review.schema.json`.

Stage B is not asked to search broadly for new defects. Its role is to adjudicate Stage A's candidates. If it discovers that a candidate understates its own demonstrated root cause, it may strengthen that finding, but it should not introduce unrelated findings that Stage A never raised.

## Why Two Calls

The baseline used one general-purpose review call. Iteration 1 adds one explicit second-pass judgment boundary.

This keeps the causal change small:

```text
baseline:    discover + decide in one pass
iteration 1: discover first, decide second
```

If precision improves while recall remains 1.0, the result supports the hypothesis that finding admission deserves a separate reasoning step.

If it does not improve, we can change or remove this stage before adding more agents.

## Intermediate Admission Report

Stage B returns an object matching `schemas/admission.schema.json`.

The report contains:

- `case_id`;
- one adjudication record for every Stage A candidate;
- any merge groups;
- `final_review`, which must itself satisfy `schemas/review.schema.json`.

The adjudication records exist for experiment visibility and trajectory analysis. Only `final_review` is passed to the existing evaluator.

## Candidate Identity

Candidate findings are identified by their zero-based position in Stage A's `findings` array.

Example:

```text
candidate 0
candidate 1
candidate 2
```

This avoids changing the frozen final review schema merely to add internal IDs.

## Admission Outcomes

Every candidate receives exactly one outcome:

- `admit` — survives as an independent final finding;
- `reject` — excluded from the final human-facing review;
- `merge` — materially valid but consolidated into another admitted candidate because both share one root cause.

A merge record must point to the target candidate index.

## Rejection Reasons

The admission report uses a bounded reason taxonomy for rejected candidates:

- `unsupported` — evidence does not establish the claimed behavior;
- `out_of_scope` — depends on unsupported callers, infrastructure, or requirements;
- `not_material` — real behavior but not material enough for production-readiness reporting;
- `hardening_only` — best-practice improvement without a concrete demonstrated defect;
- `duplicate_root_cause` — valid observation already captured by a stronger finding;
- `other` — requires a specific explanation.

These reasons are diagnostic only and are not part of the benchmark scoring taxonomy.

## Final Decision Rule

The final review must use the existing rule:

- `not_ready` if one or more admitted findings remain;
- `ready` if no admitted findings remain.

Rejected findings may not force `not_ready`.

## Storage Layout

Iteration 1 should preserve both intermediate and final artifacts:

```text
evals/results/iteration_1/
  case_01/
    candidates.json
    admission.json
    final.json
  case_02/
    candidates.json
    admission.json
    final.json
  ...
```

For compatibility with the current evaluator, the runner may additionally materialize or copy the twelve `final.json` objects into a flat scoring directory such as:

```text
evals/results/iteration_1_scored/case_01.json
...
```

The evaluator itself remains unchanged.

## Experimental Controls

For every case:

- use a fresh model context for Stage A;
- use a fresh model context for Stage B;
- Stage B receives Stage A's JSON explicitly rather than conversation memory;
- use the same model/configuration across all twelve cases when possible;
- keep both prompts frozen once the Iteration 1 scored run begins;
- record runtime, model identifier, and token/cost information when available;
- retain representative transcripts for both stages.

## Implementation Order

1. Freeze the two prompts.
2. Add and validate the admission schema.
3. Implement deterministic artifact validation/extraction.
4. Implement the two-stage runner.
5. Smoke-test on non-scored development copies or a single diagnostic run.
6. Freeze the runner and prompts.
7. Run all twelve cases from fresh contexts.
8. Score only the extracted final reviews with the existing evaluator.

No ground-truth or case-fixture changes should be made in response to Iteration 1 outputs unless a genuine benchmark defect is independently established and documented.
