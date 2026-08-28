# Results

This document summarizes the frozen twelve-case comparison between the baseline reviewer and Iteration 1.

## Aggregate Comparison

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

Iteration 1 reduced false positives by two-thirds while preserving every expected defect and every case-level readiness decision.

## What Actually Improved

The baseline already achieved perfect recall. Its measured weakness was not defect discovery but finding admission: it could elevate plausible but weakly scoped or low-materiality concerns into final review findings.

Iteration 1 therefore made one targeted architectural change:

```text
Stage A: broad candidate review
        ↓
Stage B: evidence + scope + materiality admission
        ↓
final review
```

The second stage evaluates each candidate for concrete failure, direct evidence, supported scope, material production impact, and independence from duplicate or stronger findings.

## Case 06 — The Precision Stress Case

`case_06` is the clearest before/after example.

The baseline returned four findings:

- one expected `retry_policy` finding about indiscriminate retries;
- a second `retry_policy` finding about zero-delay retry loops;
- an `idempotency` concern that depended on how an arbitrary caller used the helper;
- a `validation` concern about non-positive attempt counts.

The evaluator scored one true positive and three false positives.

In Iteration 1, Stage A still generated a broad candidate set. Stage B rejected the non-positive-attempt validation concern as not materially production-impacting under the supplied evidence. It retained both retry-policy concerns because each was directly evidenced and materially defensible.

Final scored result for `case_06`:

```text
TP = 1
FP = 1
FN = 0
```

This is intentionally not tuned to a perfect score. The remaining false positive is a technically defensible finding about immediate retries with no pacing. Suppressing it only to match hidden ground truth would make the benchmark result less credible.

## Clean Controls

`case_03` and `case_11` are true-negative controls. Iteration 1 returned `ready` with no findings for both.

The clean controls matter because earlier diagnostic runs exposed real fixture defects even though visible tests passed. Those failures forced the benchmark to define bounded contracts and strengthen the fixtures before scored evaluation.

## Composite Case

`case_12` contains two independent defects:

- `authorization`: actor identity is ignored during credit issuance;
- `idempotency`: repeated use of the same request ID creates duplicate credits.

Iteration 1 preserved both findings as independent material defects and scored two true positives with no false positives.

## Interpretation

The experiment supports three conclusions.

1. Strong agent reviewers can already have high recall on small backend defect suites.
2. As discovery improves, reviewer quality becomes constrained by evidence admission and scope control.
3. The useful architectural move was not adding more agents or more search breadth; it was adding one narrowly defined adjudication stage tied to an observed precision failure.

## Reproduce

Run the frozen Iteration 1 artifacts through the deterministic evaluator:

```bash
python -m iteration_1.runner materialize-scored
python evals/evaluator.py evals/results/iteration_1_scored
```

See `experiments/CHANGELOG.md` for the full experiment history and `docs/TRAJECTORIES.md` for representative agent traces.