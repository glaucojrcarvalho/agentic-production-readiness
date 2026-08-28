# Iteration 1 Runbook

This runbook covers the deterministic artifact pipeline around the two fresh model stages defined in `docs/ITERATION_1_IMPLEMENTATION.md`.

## 1. Stage A — Candidate Review

Run a fresh candidate-review session for one case using `prompts/candidate_review.md`.

Save only the JSON result to:

```text
evals/results/iteration_1/case_XX/candidates.json
```

Validate it before starting Stage B:

```bash
python -m iteration_1.runner validate-candidates \
  case_XX \
  evals/results/iteration_1/case_XX/candidates.json
```

Do not continue if validation fails.

## 2. Stage B — Admission Critic + Consolidator

Start a new model context. Give it:

- the same `evals/cases/case_XX` directory;
- `prompts/finding_admission.md`;
- `schemas/review.schema.json`;
- `schemas/admission.schema.json`;
- the validated `candidates.json` from Stage A.

Do not expose `evals/ground_truth.yaml`, `evals/verify_cases.py`, other case outputs, baseline scores, or expected defect categories.

Save only the Stage B JSON result to:

```text
evals/results/iteration_1/case_XX/admission.json
```

## 3. Validate and Finalize

Run:

```bash
python -m iteration_1.runner finalize \
  case_XX \
  evals/results/iteration_1/case_XX/candidates.json \
  evals/results/iteration_1/case_XX/admission.json
```

The runner validates structural and semantic invariants, including:

- case IDs match;
- every candidate is adjudicated exactly once;
- merge targets are admitted candidates;
- merge groups agree with merge adjudications;
- final decision agrees with the final findings array;
- final output matches `schemas/review.schema.json`.

On success it writes:

```text
evals/results/iteration_1/case_XX/final.json
evals/results/iteration_1_scored/case_XX.json
```

## 4. Score the Full Iteration

After all twelve cases have valid final artifacts:

```bash
python -m iteration_1.runner materialize-scored
python evals/evaluator.py evals/results/iteration_1_scored
```

Compare the result to the frozen baseline:

```text
precision = 0.786
recall = 1.000
F1 = 0.880
decision accuracy = 1.000
evidence-grounded finding rate = 1.000
```

## Smoke Test Before Scored Runs

Before starting the twelve scored cases, run the deterministic runner tests:

```bash
python -m pytest tests/test_iteration_1_runner.py -q
```

Do not change prompts, schemas, runner semantics, or case fixtures after the scored Iteration 1 run begins unless a genuine benchmark defect is independently established and documented.
