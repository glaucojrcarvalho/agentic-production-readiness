# Improvement Changelog

This file records the evolution from baseline to final solution.

Every meaningful experiment should answer four questions:

1. What did we observe?
2. What did we change and why?
3. What evidence changed?
4. Did we keep, revise, or remove the change?

Do not rewrite history. Failed experiments and removed components belong here when they taught us something useful.

## Evaluation Metrics

Primary metric:

- Production Defect Detection F1

Secondary metrics:

- precision;
- recall;
- false-positive rate;
- evidence-grounded finding rate;
- human review time;
- latency;
- approximate cost per case.

## Baseline

**Status:** in progress

### Pilot / Evaluation Harness Check

The baseline agent reviewed `evals/cases/case_01` and correctly identified that committing the order before writing its audit record makes the operation non-atomic. It verified the failure by running the case tests: the transaction-consistency test failed because the order remained persisted after the simulated audit failure, while the happy-path test passed.

The finding used the category `data_consistency`; the hidden ground truth uses `transaction_consistency`. Because the current evaluator requires an exact category match, this substantively correct finding could be scored incorrectly due only to taxonomy wording. Before scored baseline runs, we froze a canonical defect taxonomy so agent output, ground truth, and evaluator expectations share the same category definitions. This harness pilot is diagnostic and does not count toward final baseline metrics.

### Pilot / Clean-Control Fixture Check

The first baseline run on `evals/cases/case_03` did not treat the intended clean control as ready. After the supplied tests passed, the agent ran additional probes and produced concrete evidence for four behaviors that the fixture did not cover: idempotency state was isolated per SQLite `:memory:` connection, simultaneous duplicate requests could surface a uniqueness error rather than replay the winning result, the payment function could interfere with a caller-owned transaction, and invalid payment values were accepted.

Because `case_03` is intended to be a true-negative control for false-positive measurement, these findings exposed a fixture-design problem rather than a baseline miss. The result is diagnostic and does not count toward final baseline metrics.

Decision: repair the clean control before scoring it. The revised fixture shared state across independent database connections, serialized competing writers before the idempotency check, attempted to preserve caller transaction ownership, validated basic payment inputs, and added regression tests for cross-connection replay, concurrent duplicates, nested transaction behavior, and invalid inputs.

### Pilot / Clean-Control Contract Check

A fresh baseline run against the repaired `case_03` still produced verified findings outside the original tests: module import and process exit deleted the shared database and therefore destroyed idempotency state across worker lifecycles; concurrent calls inside caller-owned deferred transactions could surface `database is locked`; and a positive float such as `1.5` could be persisted as `amount_cents` despite the integer-cents API contract.

This second diagnostic showed that making visible tests pass was not enough to define a clean benchmark case. The fixture lacked a bounded production contract, which allowed accidental behavior to remain in scope.

Decision: define the clean-control contract explicitly and repair the fixture to that contract before any scored run. `process_payment` now owns its transaction and rejects already-active caller transactions without mutating them; `request_id` must be a non-empty string; `amount_cents` must be a positive integer; database constraints also enforce integer positive cents; persistent state is no longer deleted on module import or process exit; and a process-boundary regression test verifies replay survives a separate Python process. The two earlier `case_03` outputs remain diagnostic and are excluded from baseline metrics.

### Three-Case Scored Harness Slice

After freezing the taxonomy and repairing the clean control, the baseline was rerun from fresh sessions on `case_01`, `case_02`, and `case_03`.

Observed aggregate metrics:

| Metric | Result |
|---|---:|
| Precision | 1.00 |
| Recall | 1.00 |
| F1 | 1.00 |
| Decision accuracy | 1.00 |
| Evidence-grounded finding rate | 1.00 |

The result validates the evaluator, schema, prompt isolation, and true-negative handling, but it does not provide headroom for measuring an improved agentic workflow.

Decision: do not optimize the advanced workflow against this three-case slice. Expand the benchmark first, while the baseline prompt remains frozen.

### Dataset Expansion Before Optimization

Cases `case_04` through `case_12` were added before any advanced reviewer architecture was implemented. The expanded suite introduces concurrency, authorization, retry-policy, error-handling, performance, state-transition, time-handling, a second clean control, and a composite multi-defect case.

The new cases are intentionally harder than the harness slice: their visible tests mainly cover normal behavior, while deterministic benchmark-construction probes live outside the reviewer-visible case directory. `case_11`, like `case_03`, has a bounded clean-control contract to prevent accidental requirements from corrupting false-positive measurement.

Decision: run the frozen baseline independently on all twelve cases before choosing any advanced orchestration, tools, or specialized verification strategy. Improvements must be driven by observed failures on this expanded baseline rather than by knowledge of the hidden ground truth.

### Pilot / Second Clean-Control Concurrency Check

The first baseline review of `case_11`, which was intended to be a clean control, produced a verified concurrency finding. The agent demonstrated that `WebhookStore.save()` used a non-atomic check-then-write sequence: two racing first deliveries for the same `event_id` could both succeed, return different results, and leave only one result stored. That behavior violated the case's own bounded contract, which requires racing duplicate deliveries to converge on the winner's stored result.

Because this was a real fixture defect rather than a reviewer false positive, the original `case_11` baseline output is diagnostic and excluded from final baseline metrics.

Decision: make the store's get/save operations concurrency-safe with a lock, add an explicit concurrent-delivery regression test, extend `verify_case_11()` to assert that both racing callers receive the same stored result, and rerun only `case_11` from a fresh baseline session before scoring the twelve-case benchmark.

### Approach

A general-purpose coding agent receives the evaluation repository/change and a direct instruction to review it for production readiness.

No custom orchestration or specialized verification workflow.

### Why

Establish the performance of a simple, reasonable agent workflow before introducing project-specific improvements.

### Evidence

The three-case harness slice scored perfectly. Expanded-suite metrics are pending completion of baseline runs for cases 04–12 and a clean rerun of the repaired `case_11` fixture.

### Decision / Learning

Keep the frozen baseline protocol and expand the evaluation dataset before introducing solution complexity.

---

## Iteration 1

**Status:** not started

### Observation / Hypothesis

TBD from expanded baseline failures.

### Change

TBD.

### Why

TBD.

### Evidence

| Metric | Before | After | Change |
|---|---:|---:|---:|
| F1 | TBD | TBD | TBD |
| Precision | TBD | TBD | TBD |
| Recall | TBD | TBD | TBD |
| False-positive rate | TBD | TBD | TBD |
| Evidence-grounded findings | TBD | TBD | TBD |
| Runtime/case | TBD | TBD | TBD |
| Cost/case | TBD | TBD | TBD |

### Decision / Learning

TBD: keep / revise / remove.

---

## Iteration Template

Copy this section for every meaningful experiment.

### Observation / Hypothesis

What failure, limitation, or opportunity did the previous evaluation expose?

### Change

What exactly changed?

### Why

Why should this change address the observed problem?

### Evidence

Report results using the same evaluation method whenever possible.

| Metric | Before | After | Change |
|---|---:|---:|---:|
| F1 |  |  |  |
| Precision |  |  |  |
| Recall |  |  |  |
| False-positive rate |  |  |  |
| Evidence-grounded findings |  |  |  |
| Runtime/case |  |  |  |
| Cost/case |  |  |  |

### Decision / Learning

Keep, revise, or remove the change. Explain why.

---

## Final

**Status:** not reached

### Included Changes

TBD.

### Removed Experiments

TBD.

### Final Comparison

| Metric | Baseline | Final | Change |
|---|---:|---:|---:|
| Production Defect Detection F1 | TBD | TBD | TBD |
| Precision | TBD | TBD | TBD |
| Recall | TBD | TBD | TBD |
| False-positive rate | TBD | TBD | TBD |
| Evidence-grounded findings | TBD | TBD | TBD |
| Runtime/case | TBD | TBD | TBD |
| Cost/case | TBD | TBD | TBD |

### Main Failure Mode

TBD.

### Hot Take

Working hypothesis, to be rewritten from actual evidence:

> The bottleneck in AI-assisted software engineering is shifting from code generation to evidence generation.

This should only remain the final hot take if the experiments actually support it.
