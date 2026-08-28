# Submission Checklist

Use this checklist before submitting the hackathon entry.

## Repository

- [x] Problem, intended user, and bottleneck are clearly stated.
- [x] Baseline is defined and preserved.
- [x] Iteration 1 architecture is documented.
- [x] Frozen 12-case benchmark is included.
- [x] Ground truth and deterministic evaluator are included.
- [x] Baseline outputs are preserved.
- [x] Iteration 1 candidate, admission, final, and scored artifacts are preserved.
- [x] All 24 Iteration 1 Stage A/Stage B logs are preserved.
- [x] Experiment changelog includes diagnostic failures and design changes.
- [x] Representative trajectories are documented.
- [x] Clean-checkout reproducibility was verified on Python 3.14.4.
- [x] Default project smoke tests are separated from intentionally failing benchmark defect tests.

## Measured Result

Frozen comparison:

| Metric | Baseline | Iteration 1 |
|---|---:|---:|
| True positives | 11 | 11 |
| False positives | 3 | 1 |
| False negatives | 0 | 0 |
| Precision | 0.786 | 0.917 |
| Recall | 1.000 | 1.000 |
| F1 | 0.880 | 0.957 |
| Decision accuracy | 1.000 | 1.000 |
| Evidence-grounded finding rate | 1.000 | 1.000 |

- [x] Improvement is measured on the same benchmark and evaluator.
- [x] Recall remains unchanged at 1.000.
- [x] False positives fall from 3 to 1.
- [x] Remaining false positive is disclosed rather than tuned away.
- [x] Runtime/cost are explicitly marked as not systematically captured rather than estimated.

## Reproducibility

From a clean checkout:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
python -m iteration_1.runner materialize-scored
python evals/evaluator.py evals/results/iteration_1_scored
```

Expected project smoke-test result: green.

Expected evaluator aggregate:

```text
TP = 11
FP = 1
FN = 0
precision = 0.9166666666666666
recall = 1.0
F1 = 0.9565217391304348
decision accuracy = 1.0
evidence-grounded finding rate = 1.0
```

Benchmark defect tests are separate and may intentionally fail:

```bash
python -m pytest evals/cases -q
```

## Judge Path

- [x] `README.md` provides a short judge path.
- [x] `docs/RESULTS.md` explains the quantitative result.
- [x] `docs/TRAJECTORIES.md` shows representative agent behavior.
- [x] `docs/DEMO.md` defines a ≤5-minute demonstration flow.
- [x] `experiments/CHANGELOG.md` preserves experiment history.

## Video / Submission

Complete immediately before submission:

- [ ] Record the final video in ≤5 minutes.
- [ ] Show the problem and intended user in the first ~30 seconds.
- [ ] Show the baseline result before explaining the advanced architecture.
- [ ] Show Case 06 as the main precision/admission trajectory.
- [ ] Briefly show a clean control (`case_11`) and composite defect case (`case_12`).
- [ ] Show the final measured table: precision 0.786 → 0.917, F1 0.880 → 0.957, recall 1.000 → 1.000.
- [ ] State that the remaining FP was intentionally not prompt-tuned away.
- [ ] State the hot take/insight in the closing section.
- [ ] Confirm repository URL is accessible to judges.
- [ ] Confirm video link permissions allow judge access.
- [ ] Confirm final submission text points directly to README, results, and video.

## Final Message

The submission should make one causal claim, not a broad claim about all code review:

> On this frozen 12-case production-readiness benchmark, separating broad candidate discovery from strict evidence/scope/materiality admission reduced false positives from 3 to 1 while preserving all 11 expected defect detections, improving precision from 78.6% to 91.7% and F1 from 0.880 to 0.957.
