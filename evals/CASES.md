# Evaluation Cases

This document defines the evaluation dataset used to compare the frozen baseline reviewer with later agentic workflows.

## Design Principles

Each case should be:

- small enough to understand and reproduce quickly;
- realistic enough to require engineering judgment;
- deterministic under its verification procedure;
- independent of external services;
- safe to execute locally;
- paired with hidden ground truth;
- identical for baseline and advanced evaluation.

During scored runs, the reviewer may inspect only the requested case directory plus the review schema. It must not inspect `evals/ground_truth.yaml` or `evals/verify_cases.py`.

## Harness Slice

The first three cases validated the evaluator and baseline protocol:

| Case | Ground truth | Purpose |
|---|---|---|
| `case_01` | `transaction_consistency` | partial persisted state after failure |
| `case_02` | `idempotency` | duplicate side effect on retry |
| `case_03` | ready | bounded clean idempotent control |

The frozen baseline scored 1.0 precision, recall, F1, decision accuracy, and evidence-grounded finding rate on this slice. Because that left no headroom for improvement, the slice is retained but is not sufficient by itself for the final comparison.

## Expanded Suite

The dataset is expanded to twelve cases before any advanced workflow is optimized.

| Case | Expected status | Primary challenge |
|---|---|---|
| `case_01` | defective | transaction consistency |
| `case_02` | defective | idempotency |
| `case_03` | ready | clean control |
| `case_04` | defective | concurrent inventory oversubscription |
| `case_05` | defective | cross-tenant authorization boundary |
| `case_06` | defective | retrying permanent failures |
| `case_07` | defective | swallowed failure reported as success |
| `case_08` | defective | N+1-style query amplification |
| `case_09` | defective | invalid terminal-state transition |
| `case_10` | defective | timezone-offset comparison error |
| `case_11` | ready | replay-safe clean webhook control |
| `case_12` | defective | composite authorization + idempotency defects |

## Difficulty Controls

Cases 04–12 are intentionally different from the initial harness slice:

- visible tests mainly exercise normal behavior rather than naming the planted defect;
- deterministic verifier probes live outside the case directory and are not visible to the reviewer during scored runs;
- several defects require reasoning about boundaries not covered by the visible happy-path test;
- there are two true-negative controls (`case_03` and `case_11`) to measure false positives;
- `case_12` requires multiple findings from one change.

`case_03` and `case_11` contain bounded contracts because earlier harness experiments showed that a clean control must state what behavior is actually supported; otherwise an agent can discover real but unintended requirements and invalidate the ground truth.

## Verification

The original three cases retain their existing pytest verification procedures. Cases 04–12 use deterministic probes in `evals/verify_cases.py`, for example:

```bash
python evals/verify_cases.py case_04
python evals/verify_cases.py case_12
```

These probes are for benchmark construction and ground-truth validation. They are outside the reviewer-visible scope during baseline and final scored runs.

## Scored-Run Protocol

For every case:

1. start a fresh agent session;
2. use the same frozen review prompt and schema;
3. change only the case path and output path;
4. do not reveal ground truth or hidden verifier probes;
5. save the JSON result and representative trajectory;
6. score all cases with the same evaluator.

The expanded baseline must be completed before changing the reviewer architecture. Later improvements are driven only by observed baseline failure modes.
