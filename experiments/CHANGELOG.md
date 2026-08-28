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

**Status:** complete

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

### Twelve-Case Scored Baseline

After repairing and rerunning `case_11`, the frozen baseline was scored on all twelve cases.

Observed aggregate metrics:

| Metric | Result |
|---|---:|
| True positives | 11 |
| False positives | 3 |
| False negatives | 0 |
| Precision | 0.786 |
| Recall | 1.000 |
| F1 | 0.880 |
| Decision accuracy | 1.000 |
| Evidence-grounded finding rate | 1.000 |

The baseline detected every expected defect, correctly returned `ready` for both clean controls, and found both defects in the composite case. All three false positives came from `case_06`.

`case_06` exposed two precision failure modes. First, the reviewer split one retry-policy root cause into multiple findings, so an additional retry-policy symptom was scored separately. Second, it promoted plausible hardening concerns about idempotency and argument validation into material findings even though those concerns were broader than the case's supported contract and intended failure mode.

Decision: keep the current defect-discovery capability and target precision rather than recall in Iteration 1. Do not modify the benchmark, ground truth, taxonomy, or baseline outputs in response to these errors.

### Approach

A general-purpose coding agent receives the evaluation repository/change and a direct instruction to review it for production readiness.

No custom orchestration or specialized verification workflow.

### Why

Establish the performance of a simple, reasonable agent workflow before introducing project-specific improvements.

### Evidence

The final twelve-case baseline scored precision 0.786, recall 1.000, F1 0.880, decision accuracy 1.000, and evidence-grounded finding rate 1.000.

### Decision / Learning

The baseline is already strong at defect discovery. Its main measured weakness is over-reporting: candidate findings need stronger scope, materiality, and root-cause consolidation before they reach a human reviewer.

---

## Iteration 1 — Finding Admission and Consolidation

**Status:** complete

### Observation / Hypothesis

The expanded baseline produced no false negatives but three false positives, all concentrated in one retry-helper case. The reviewer is good at generating plausible and evidence-backed defect candidates, but it can over-promote secondary symptoms, generic hardening opportunities, or multiple manifestations of the same root cause.

Hypothesis: adding an explicit evidence/scope critic followed by root-cause consolidation will improve precision without reducing recall.

### Change

Iteration 1 uses two fresh model stages per case:

1. **Candidate reviewer** — broadly identifies concrete, material production-readiness concerns and gathers evidence.
2. **Admission critic + consolidator** — adjudicates every candidate against concrete failure, evidence, scope, materiality, and independence before producing the final review.

The second stage may admit, reject, or merge existing candidates, but it is not allowed to broadly search for unrelated new defects. Stage A and Stage B run in separate model contexts, and Stage B receives Stage A's JSON explicitly.

### Why

The baseline already achieved recall 1.000. Adding more defect-finding breadth was not justified by the evidence. The measured opportunity was to reduce reviewer noise while keeping every real defect.

### Success Criteria

Iteration 1 was considered an improvement only if:

- precision was greater than 0.786;
- recall remained 1.000;
- F1 was greater than 0.880;
- decision accuracy remained 1.000;
- evidence-grounded finding rate remained 1.000.

A perfect score was not assumed or required.

### Diagnostic / Case 06

Before the frozen twelve-case run, the two-stage workflow was tested diagnostically on `case_06`, the only baseline case with false positives. Stage A reproduced four candidate findings. Stage B rejected the idempotency concern as out of scope and the non-positive-attempts concern as not material, while preserving two independently defensible retry-policy findings.

This reduced the case from three false positives to one without suppressing the intended defect. The prompt was not further tuned against `case_06`; the workflow was then frozen and run across all twelve cases.

### Twelve-Case Scored Result

Observed aggregate metrics:

| Metric | Baseline | Iteration 1 | Change |
|---|---:|---:|---:|
| True positives | 11 | 11 | 0 |
| False positives | 3 | 1 | -2 |
| False negatives | 0 | 0 | 0 |
| Precision | 0.786 | 0.917 | +0.131 |
| Recall | 1.000 | 1.000 | 0.000 |
| F1 | 0.880 | 0.957 | +0.077 |
| Decision accuracy | 1.000 | 1.000 | 0.000 |
| Evidence-grounded finding rate | 1.000 | 1.000 | 0.000 |
| Runtime/case | not captured | not captured | — |
| Cost/case | not captured | not captured | — |

Iteration 1 met every frozen success criterion. False positives fell from three to one, while all eleven expected defects remained detected and both clean controls remained correctly classified as ready.

The remaining false positive is the second `retry_policy` finding in `case_06`: immediate retries with no delay, backoff, or jitter. The benchmark ground truth contains one retry-policy defect for the case, so the evaluator counts the second same-category finding as an extra finding. The reviewer preserved it because it was concrete, evidenced, in scope, and materially defensible. We did not suppress it merely to obtain a perfect benchmark score.

### Decision / Learning

**Keep the two-stage workflow.** The experiment supports the hypothesis that finding admission is a distinct engineering problem from finding generation.

The measured improvement did not come from discovering more defects. It came from deciding which evidence-backed candidates deserved human attention. Precision improved from 78.6% to 91.7% while recall remained 100%.

This also sharpens the project thesis: as coding agents become stronger at generating plausible findings, the next bottleneck is not simply evidence generation but **evidence admission and triage** — determining which supported findings are sufficiently scoped, material, and independent to interrupt a human reviewer.

All twelve Stage A and Stage B trajectories are preserved under `evals/results/iteration_1_logs/`, alongside the structured candidate, admission, final, and scored artifacts.

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

**Status:** current best solution is Iteration 1; final packaging not yet complete

### Included Changes

Current best measured system:

- frozen canonical defect taxonomy;
- bounded clean-control contracts;
- candidate-generation stage;
- independent admission critic and root-cause consolidator;
- deterministic schema and semantic validation;
- preserved agent trajectories and scored artifacts.

### Removed Experiments

No scored component has been removed. Diagnostic fixture failures remain documented because they exposed benchmark defects and changed the evaluation design.

### Final Comparison

| Metric | Baseline | Current Best | Change |
|---|---:|---:|---:|
| Production Defect Detection F1 | 0.880 | 0.957 | +0.077 |
| Precision | 0.786 | 0.917 | +0.131 |
| Recall | 1.000 | 1.000 | 0.000 |
| Evidence-grounded findings | 1.000 | 1.000 | 0.000 |
| Decision accuracy | 1.000 | 1.000 | 0.000 |
| Runtime/case | not captured | not captured | — |
| Cost/case | not captured | not captured | — |

### Main Failure Mode

The remaining measured failure is duplicate or overlapping reporting within the same defect category when multiple production-relevant symptoms are independently defensible. The current evaluator matches expected categories exactly and consumes an expected category once, so a second same-category finding is counted as a false positive even when it is technically valid.

### Hot Take

> The bottleneck in AI-assisted software engineering is shifting from code generation to evidence generation — and once agents generate enough plausible evidence, evidence admission becomes its own engineering problem.

The experiment supports a more concrete version:

> Strong review agents do not only need to find defects. They need a disciplined mechanism for deciding which findings are worth a human's attention.
