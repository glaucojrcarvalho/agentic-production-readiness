# Representative Agent Trajectories

All 24 scored Iteration 1 Codex logs are preserved under `evals/results/iteration_1_logs/`. This index highlights three representative trajectories for judging and demo use.

## 1. Case 06 — Precision Stress Test

Why this trajectory matters: it demonstrates the exact measured failure mode that motivated Iteration 1.

Artifacts:

- Stage A log: `evals/results/iteration_1_logs/case_06_stage_a.log`
- Stage B log: `evals/results/iteration_1_logs/case_06_stage_b.log`
- Candidates: `evals/results/iteration_1/case_06/candidates.json`
- Admission report: `evals/results/iteration_1/case_06/admission.json`
- Final review: `evals/results/iteration_1/case_06/final.json`
- Baseline comparison: `evals/results/baseline/case_06.json`

What to look for:

Stage A behaves deliberately broadly. It probes the retry helper and retains concrete concerns rather than prematurely optimizing precision. Stage B then adjudicates those candidates using evidence, scope, and materiality instead of simply echoing Stage A.

The final result preserves the expected permanent-failure retry defect, rejects a lower-materiality validation concern, and still keeps a second technically defensible retry-policy finding. This is the best trajectory for explaining why the final score is 0.957 rather than an artificially tuned 1.000.

## 2. Case 11 — Clean Control

Why this trajectory matters: a production-readiness reviewer must know when not to report a defect.

Artifacts:

- Stage A log: `evals/results/iteration_1_logs/case_11_stage_a.log`
- Stage B log: `evals/results/iteration_1_logs/case_11_stage_b.log`
- Candidates: `evals/results/iteration_1/case_11/candidates.json`
- Admission report: `evals/results/iteration_1/case_11/admission.json`
- Final review: `evals/results/iteration_1/case_11/final.json`

What to look for:

Stage A returns `ready` with no findings. Stage B receives an empty candidate set and also returns `ready`. This shows the workflow is not structurally biased toward producing findings just because an agent stage exists.

This case is especially useful in the project story because an earlier diagnostic review found a real race in the original clean-control fixture. The fixture was repaired before scoring rather than counting the agent's correct finding as a false positive.

## 3. Case 12 — Composite Multi-Defect Case

Why this trajectory matters: the admission stage must reduce noise without collapsing independent defects.

Artifacts:

- Stage A log: `evals/results/iteration_1_logs/case_12_stage_a.log`
- Stage B log: `evals/results/iteration_1_logs/case_12_stage_b.log`
- Candidates: `evals/results/iteration_1/case_12/candidates.json`
- Admission report: `evals/results/iteration_1/case_12/admission.json`
- Final review: `evals/results/iteration_1/case_12/final.json`
- Baseline comparison: `evals/results/baseline/case_12.json`

What to look for:

Stage A verifies two distinct production failures: unauthorized cross-account credit issuance and duplicate credit creation under request replay. Stage B admits both because they have independent root causes and independent remediation paths.

The case scores two true positives with no false positives, showing that stricter admission did not trade away recall on a multi-defect change.

## Suggested Judge Reading Order

For the shortest path through the evidence:

1. `docs/RESULTS.md`
2. `evals/results/baseline/case_06.json`
3. `evals/results/iteration_1/case_06/candidates.json`
4. `evals/results/iteration_1/case_06/admission.json`
5. `evals/results/iteration_1/case_06/final.json`
6. `evals/results/iteration_1/case_11/final.json`
7. `evals/results/iteration_1/case_12/final.json`

The raw Stage A and Stage B logs are available when the full reasoning/tool trajectory is useful.