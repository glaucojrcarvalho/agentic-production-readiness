# Case 03 Production Contract

Case 03 is the clean-control evaluation case. Its implementation is expected to be production-ready within the bounded contract below.

## Supported behavior

- `process_payment` owns the payment transaction.
- The supplied connection must not already have an active transaction.
- `request_id` must be a non-empty string.
- `amount_cents` must be a positive integer number of cents; booleans and fractional values are invalid.
- Payment and idempotency state persist across independent connections and process lifecycles.
- Replaying the same `request_id` with the same amount returns the original charge.
- Reusing the same `request_id` with different request data raises an idempotency conflict.
- Concurrent duplicate requests must produce one durable charge and replay the winning result rather than duplicate the side effect.
- The charge row and idempotency record are committed atomically.

## Explicit non-goals

- Composing `process_payment` inside a caller-owned transaction is not supported.
- External payment-provider behavior is outside this fixture; the business side effect is represented by the durable `charges` row.
- Authorization is outside this case because no API or identity boundary is present.

The clean-control ground truth is `ready` only when the supplied implementation satisfies this contract without material production-readiness defects in scope.
