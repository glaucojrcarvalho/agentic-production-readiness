# Canonical Defect Taxonomy

This taxonomy is frozen before the scored baseline runs so that baseline and advanced solutions are evaluated against the same defect categories.

Each finding must use exactly one canonical category. The category should describe the primary production-readiness failure mode, not merely a broad symptom.

## Categories

### `transaction_consistency`
Use when one logical business operation can leave partial, internally inconsistent persisted state because related writes are not committed or rolled back atomically.

Examples:
- an order is committed but its required ledger/audit record is not;
- one half of a multi-write business operation persists after failure.

### `idempotency`
Use when repeating the same logical request can execute a business side effect more than once, or when request identity is not safely reused or rejected.

Examples:
- a retry creates a duplicate charge;
- the same idempotency key can create multiple side effects.

### `concurrency`
Use for correctness failures caused by overlapping execution, race conditions, lost updates, unsafe shared state, or missing synchronization.

### `authorization`
Use when an actor can access or mutate data or operations outside the permissions they should have.

### `retry_policy`
Use when retry behavior itself is unsafe or incorrect, such as retrying non-retryable failures, causing retry storms, or applying backoff incorrectly. If the primary defect is duplicate execution of one logical request, prefer `idempotency`.

### `error_handling`
Use when failures are swallowed, misreported, converted to misleading success, or otherwise handled in a way that creates a concrete production risk.

### `state_transition`
Use when the system allows an invalid lifecycle or domain-state transition, skips required transitions, or leaves state-machine invariants broken.

### `performance`
Use when there is concrete evidence of a production-impacting efficiency defect, such as N+1 queries, unbounded work, or a clearly unsafe algorithmic/resource pattern.

### `time_handling`
Use for concrete correctness failures involving time zones, daylight-saving transitions, timestamps, clock assumptions, expiry, or temporal ordering.

### `validation`
Use when invalid or conflicting input is accepted in a way that creates a material correctness or reliability risk.

### `other`
Use only when a material production-readiness defect is well supported by evidence but does not fit any canonical category above. The claim must describe the defect precisely.

## Selection Rules

1. Choose the most specific category that matches the primary failure mode.
2. Do not create new category names during a scored run.
3. Do not use a broader category when a more specific canonical category applies.
4. A single underlying defect should normally produce one finding, even if it has several consequences.
5. `other` is a fallback, not a substitute for uncertainty.
6. If no material defect is found, return `decision: "ready"` with an empty findings array.

## Evaluation Rule

For the initial evaluation slice, finding categories are matched exactly against hidden ground-truth categories. This is fair only because the same frozen taxonomy is provided to both baseline and advanced systems before scored runs.
