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

Expected Iteration 1 aggregate:

```text
true positives = 11
false positives = 1
false negatives = 0
precision = 0.9166666666666666
recall = 1.0
F1 = 0.9565217391304348
decision accuracy = 1.0
evidence-grounded finding rate = 1.0
```

Compare the result to the frozen baseline:

```text
precision = 0.786
recall = 1.000
F1 = 0.880
decision accuracy = 1.000
evidence-grounded finding rate = 1.000
```

## Smoke Test

Run the deterministic runner tests:

```bash
python -m pytest tests/test_iteration_1_runner.py -q
```

The current clean-checkout result is four passing runner tests.

Do not use `python -m pytest -q` as a green/red project-health gate. The benchmark deliberately contains planted defects. In particular, the invariant tests in `case_01` and `case_02` are expected to fail against their defective implementations; on the verified clean checkout the full benchmark tree reports two expected failures and 27 passing tests.

## Clean Checkout

On Ubuntu/Debian, bootstrap with `python3` because the global `python` alias may not exist before virtual-environment activation:

```bash
git clone https://github.com/glaucojrcarvalho/agentic-production-readiness.git apr-check
cd apr-check
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest tests/test_iteration_1_runner.py -q
python -m iteration_1.runner materialize-scored
python evals/evaluator.py evals/results/iteration_1_scored
```

This procedure was verified from a fresh clone with Python 3.14.4.

Do not change prompts, schemas, runner semantics, or case fixtures after the scored Iteration 1 run unless a genuine benchmark defect is independently established and documented.
