# Initial Evaluation Cases

This document defines the first three evaluation cases before implementation begins. The goal is to establish observable production-readiness failures and a clean control case that can be evaluated consistently by both the baseline and the advanced workflow.

## Design Principles

Each case should be:

- small enough to understand and reproduce quickly;
- realistic enough to require engineering judgment;
- deterministic under its verification procedure;
- independent of external services;
- safe to execute locally;
- paired with hidden ground truth;
- identical for baseline and advanced evaluation.

The agent sees the code and normal project instructions. It does **not** see `evals/ground_truth.yaml`.

---

## Case 01 — Partial Transaction Failure

### User Scenario

A backend service creates an order and then writes an associated audit or ledger record. The two writes represent one business operation and should be atomic from the user's perspective.

### Intended Defect

The implementation commits the first write before attempting the second. If the second operation fails, the order remains persisted even though the overall operation failed.

### Why It Matters

This is the kind of change that can look correct on the happy path and may pass basic endpoint tests, while leaving production data in an inconsistent state under partial failure.

### Minimal Shape

```text
case_01/
├── src/
│   ├── app.py
│   ├── db.py
│   └── orders.py
└── tests/
    ├── test_happy_path.py
    └── test_transaction_consistency.py
```

A lightweight SQLite-backed service is sufficient. The service should perform two related writes through the same business operation.

### Failure Injection

The verification test forces the second write to fail after the first write has occurred.

### Expected Observable Behavior

Before the defect is fixed:

1. the operation returns or raises a failure;
2. the first record still exists;
3. the related second record does not exist;
4. the state-consistency invariant fails.

### Ground-Truth Finding

The relevant finding is not merely "database error handling could be better." It must identify that the business operation is non-atomic and can leave partial persisted state.

### Verification Contract

Provisional command:

```bash
pytest evals/cases/case_01/tests/test_transaction_consistency.py -q
```

Expected pre-fix result: failing test demonstrating partial persisted state.

### Non-Findings

The case should not intentionally contain unrelated security, authentication, performance, or style defects.

---

## Case 02 — Duplicate Side Effect on Retry

### User Scenario

A backend endpoint accepts a request that creates a business side effect, such as charging a payment, creating a payout, or issuing a credit.

### Intended Defect

The same logical request can be delivered more than once. The implementation has no durable idempotency mechanism, so retrying the request executes the side effect again.

### Why It Matters

Retries are normal in distributed systems. A request may be repeated because of a timeout even when the original operation succeeded. Code that is correct for one request can therefore be unsafe in production.

### Minimal Shape

```text
case_02/
├── src/
│   ├── app.py
│   ├── db.py
│   └── payments.py
└── tests/
    ├── test_single_request.py
    └── test_idempotency.py
```

No real payment provider is required. The external side effect should be represented by a deterministic local fake or persisted charge record.

### Failure Injection

Send the same logical request twice with the same idempotency key or request identifier.

### Expected Observable Behavior

Before the defect is fixed:

1. the first request succeeds;
2. the retry also succeeds;
3. two business side effects are recorded for one logical operation;
4. the idempotency invariant fails.

### Ground-Truth Finding

A valid finding should identify the duplicate side-effect path and explain that a retry can execute the business action twice because the request identity is not persisted and checked atomically.

### Verification Contract

Provisional command:

```bash
pytest evals/cases/case_02/tests/test_idempotency.py -q
```

Expected pre-fix result: failing test showing two side effects for one logical request.

### Non-Findings

The case should not intentionally include transaction inconsistency, authorization failure, or unrelated validation issues.

---

## Case 03 — Clean Idempotent Implementation

### User Scenario

A backend endpoint performs the same class of retryable business operation as Case 02, but the implementation contains a correct idempotency mechanism.

### Intended Ground Truth

No material production-readiness defect is present for the behavior under evaluation.

### Why It Matters

An agent that reports a long list of plausible risks can score well on defective-only cases while being unusable for a real senior engineer. This case measures whether the reviewer can recognize when the relevant invariant is already protected.

### Minimal Shape

```text
case_03/
├── src/
│   ├── app.py
│   ├── db.py
│   └── payments.py
└── tests/
    ├── test_single_request.py
    ├── test_idempotency.py
    └── test_conflicting_request.py
```

### Safety Mechanism

The implementation should persist an idempotency key together with enough request information to distinguish a legitimate retry from a conflicting reuse of the same key. The check and side effect should occur within a safe transactional boundary appropriate for the local test environment.

### Expected Observable Behavior

1. the first request creates exactly one side effect;
2. replaying the same logical request returns the previous result without creating another side effect;
3. reusing the same key for materially different input is rejected deterministically;
4. all invariant tests pass.

### Ground-Truth Finding

`expected_status: ready`

There are no expected material findings for the scoped behavior. Speculative concerns without concrete evidence count against precision.

### Verification Contract

Provisional command:

```bash
pytest evals/cases/case_03/tests -q
```

Expected result: all tests pass.

### Non-Findings

The evaluator should not reward a report for merely naming hypothetical race conditions, SQL injection, missing retries, or transaction risks unless the submitted case actually contains evidence for them.

---

## Acceptance Before Implementation

These cases become executable only after their code and tests are written. Before we implement the baseline agent, each case must satisfy the following:

1. Case 01 reliably fails only the intended transaction-consistency invariant.
2. Case 02 reliably fails only the intended idempotency invariant.
3. Case 03 passes its invariant suite and contains no deliberately planted defect.
4. All cases run locally without network access or private credentials.
5. Ground truth remains outside the agent-visible case directory during scored runs.
6. The exact verification commands are stable and documented.

Once these conditions hold, the three-case slice can be used to validate the evaluator and baseline protocol before expanding the dataset.
