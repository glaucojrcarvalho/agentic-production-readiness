# Evaluation Fixtures

The first evaluation slice contains three intentionally small backend cases. They exist to validate the scoring protocol before the dataset is expanded or the advanced agent is implemented.

## Setup

From a clean checkout:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
```

## Verification

Run each case independently so its local `src` package is isolated.

### Case 01 — partial transaction failure

Happy path:

```bash
pytest evals/cases/case_01/tests/test_happy_path.py -q
```

Expected: pass.

Production invariant:

```bash
pytest evals/cases/case_01/tests/test_transaction_consistency.py -q
```

Expected: fail. The failed operation leaves the order persisted without its related audit record.

### Case 02 — duplicate side effect on retry

Single request:

```bash
pytest evals/cases/case_02/tests/test_single_request.py -q
```

Expected: pass.

Production invariant:

```bash
pytest evals/cases/case_02/tests/test_idempotency.py -q
```

Expected: fail. Replaying the same logical request creates a second charge.

### Case 03 — clean idempotent implementation

```bash
pytest evals/cases/case_03/tests -q
```

Expected: all tests pass.

The implementation should create one charge, replay the original result for an identical request, and reject conflicting reuse of an idempotency key.

## Evaluation Isolation

`evals/ground_truth.yaml` is evaluator metadata and must not be included in the filesystem or context exposed to a reviewer agent during a scored run. The reviewer receives only the selected case directory plus the common review task and explicitly allowed tools.

The baseline and advanced workflow must receive the same case contents. Any difference in model, tools, execution privileges, context, or resource budget must be recorded in the experiment artifacts.

## Why Some Tests Intentionally Fail

Cases 01 and 02 are defect fixtures. Their invariant tests encode the behavior a production-safe implementation should satisfy, so the tests fail until the planted defect is fixed. A failing invariant is evidence for the evaluator; it is not a broken fixture.

Case 03 is the clean control. It protects the evaluation from rewarding reviewers that raise plausible but unsupported findings on every case.
