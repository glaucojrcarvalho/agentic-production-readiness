# Baseline Reviewer Specification

This document locks the baseline before advanced workflow experiments begin.

## Purpose

The baseline represents a reasonable simple way to review a backend change with a coding agent. It is intentionally capable enough to be fair, but it does not use custom orchestration, specialized verification stages, memory, critic loops, or task-specific skills.

The advanced system must beat this baseline on the same fixed evaluation cases.

## Baseline Unit

One general-purpose coding agent receives one evaluation case at a time.

For each case, the agent may:

- inspect any file inside the selected case directory;
- inspect the tests inside that case directory;
- run local commands needed to understand the case, including pytest;
- reason over runtime output;
- produce one final structured review.

The agent may not:

- read `evals/ground_truth.yaml`;
- inspect another evaluation case while reviewing the selected case;
- receive hints about the planted defect category;
- use a second reviewer, critic, verifier, or judge agent;
- use persistent memory from prior cases;
- receive human feedback during the scored run.

## Prompt

The exact baseline prompt is stored in `prompts/baseline_review.md` and is frozen for the initial scored slice.

If the prompt is changed later, the change must be recorded as an experiment and the baseline must be rerun on all scored cases.

## Output Contract

The final answer must be valid JSON matching `schemas/review.schema.json`.

The shared shape is:

```json
{
  "case_id": "case_01",
  "decision": "not_ready",
  "findings": [
    {
      "category": "transaction_consistency",
      "severity": "high",
      "claim": "The operation can leave partial persisted state.",
      "evidence": [
        "tests/test_transaction_consistency.py fails because the order remains after the audit write fails"
      ],
      "verified": true,
      "confidence": 0.95
    }
  ],
  "uncertainties": []
}
```

## Decision Semantics

- `ready`: no material production-readiness defect was identified for the scoped behavior.
- `not_ready`: at least one material defect was identified that should block deployment until addressed.

A `ready` decision may still include non-blocking observations, but the initial evaluator scores material defect findings only.

## Finding Semantics

A finding should describe one concrete production-readiness defect.

Broad statements such as "there may be concurrency problems" do not count as valid matches unless they identify the actual failure path represented in ground truth.

Evidence should be inspectable by a human and tied to the submitted case, for example:

- a specific code path;
- a failing test and observed state;
- runtime output;
- a reproducible command;
- a concrete configuration or dependency fact.

## Baseline Execution Record

Every scored run must retain:

- case id;
- model/agent name and version if available;
- exact prompt version;
- allowed tools;
- start/end timestamps;
- raw trajectory or transcript;
- final JSON output;
- runtime;
- approximate cost when available;
- whether the run completed successfully.

These artifacts become part of the hackathon agent trajectories and reproduction evidence.

## Fairness Rule

The baseline and advanced solution receive the same case contents and the same production-readiness goal. Any additional tools, context, execution privileges, or orchestration used by the advanced system must be documented as part of the experiment rather than hidden.

## Initial Scored Slice

The first baseline run uses exactly:

- `case_01` — partial transaction failure;
- `case_02` — duplicate side effect on retry;
- `case_03` — clean idempotent implementation.

The purpose of this slice is to validate the full review-and-score pipeline before expanding to 10 or more cases.
