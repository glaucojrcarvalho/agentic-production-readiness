# Agentic Production Readiness

An evidence-driven agentic workflow for reviewing AI-generated backend changes before they reach production.

## Judge Quick Path

If you have only a few minutes, read these in order:

1. [`docs/RESULTS.md`](docs/RESULTS.md) — measured baseline vs Iteration 1 comparison.
2. [`docs/TRAJECTORIES.md`](docs/TRAJECTORIES.md) — representative agent behavior, including the precision stress test.
3. [`docs/DEMO.md`](docs/DEMO.md) — the ≤5-minute demonstration flow.
4. [`experiments/CHANGELOG.md`](experiments/CHANGELOG.md) — full experiment history, including failed benchmark assumptions and design changes.

Current best result: **F1 0.957, precision 0.917, recall 1.000** on the frozen 12-case benchmark.

## Problem

AI-generated backend code can look convincing, compile successfully, and pass happy-path tests while still containing production risks such as race conditions, missing idempotency, unsafe retries, broken transaction boundaries, authorization mistakes, N+1 queries, weak error handling, and missing observability.

The problem is not generating more code. The problem is deciding whether a change should be trusted.

## Intended User

Senior backend engineers and technical leads reviewing AI-generated pull requests or code changes before deployment.

## Bottleneck

A reviewer must usually combine several signals manually:

- the code diff;
- surrounding repository context;
- test results;
- runtime behavior;
- dependencies and configuration;
- architecture constraints;
- known production failure modes.

General-purpose code-review agents can produce plausible findings, but plausibility is not enough. A useful review must distinguish real defects from false positives and connect conclusions to evidence a human can verify.

## Hypothesis

An agentic workflow that separates broad defect discovery from strict evidence/scope/materiality admission can improve review precision without sacrificing recall.

## Baseline

The baseline is intentionally simple:

> A general-purpose coding agent receives one evaluation case and a direct instruction to review it for production readiness.

On the frozen twelve-case benchmark, the baseline achieved:

| Metric | Baseline |
|---|---:|
| Precision | 0.786 |
| Recall | 1.000 |
| F1 | 0.880 |
| Decision accuracy | 1.000 |
| Evidence-grounded finding rate | 1.000 |

The baseline found every expected defect, but produced three false positives, all in the retry-policy case.

## Iteration 1 — Finding Admission and Consolidation

The measured failure mode was over-reporting, not missed defects. Iteration 1 therefore adds one purposeful second agent stage instead of expanding discovery breadth.

```text
case
  ↓
Stage A — candidate reviewer
  ↓
candidates.json
  ↓
Stage B — admission critic + root-cause consolidator
  ↓
final review
  ↓
deterministic validation + scoring
```

Stage A is intentionally broad. Stage B evaluates every candidate against five criteria:

1. concrete failure mode;
2. direct evidence;
3. supported scope;
4. material production impact;
5. independence from stronger or duplicate findings.

Stage B can admit, reject, or merge candidates. It cannot broadly introduce unrelated new findings.

### Measured Result

The same frozen twelve cases were rerun with two fresh model contexts per case.

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

The second stage reduced false positives by two-thirds while preserving all expected defects.

The remaining false positive is a second technically defensible `retry_policy` finding in `case_06` about immediate retries without backoff or jitter. It was not suppressed merely to optimize benchmark score.

## What Changed Our Design

Two benchmark-development failures materially changed the project.

First, agents found real defects in intended clean controls even when visible tests passed. That forced the benchmark to define bounded contracts and strengthen fixture construction rather than treating agent disagreement as noise.

Second, the twelve-case baseline achieved perfect recall but imperfect precision. That shifted the advanced architecture away from "find more" toward "admit better."

The resulting design principle is:

> Do not add agent complexity without a measured failure mode that justifies it.

## Primary Metric

**Production Defect Detection F1 score**

This balances two things that matter to a real reviewer:

- recall: finding real production defects;
- precision: avoiding invented, duplicate, or irrelevant problems.

## Secondary Metrics

- precision;
- recall;
- false-positive rate;
- evidence-grounded finding rate;
- human review time;
- latency;
- approximate cost per case.

Runtime and cost were not yet captured systematically in the current scored run and are reported as such rather than estimated.

## Evaluation Principle

Baseline and advanced workflows use the same fixed twelve backend cases, the same canonical defect taxonomy, the same final review schema, and the same deterministic evaluator.

Ground truth and hidden benchmark-construction probes are not exposed to the reviewing agents. Agent trajectories are preserved for reproducibility.

## Project Method

This repository follows an evaluation-first workflow:

```text
problem definition
      ↓
evaluation contract
      ↓
baseline
      ↓
measure failures
      ↓
smallest justified agent change
      ↓
re-evaluate
      ↓
keep / revise / remove
```

The goal is not to build the most complex agent system. The goal is to build the smallest system whose design choices are supported by evidence.

## Repository Structure

```text
.
├── README.md
├── docs/
│   ├── PROBLEM.md
│   ├── EVALUATION.md
│   ├── ARCHITECTURE.md
│   ├── TAXONOMY.md
│   ├── BASELINE.md
│   ├── ITERATION_1.md
│   ├── ITERATION_1_IMPLEMENTATION.md
│   ├── ITERATION_1_RUNBOOK.md
│   ├── RESULTS.md
│   ├── TRAJECTORIES.md
│   └── DEMO.md
├── experiments/
│   └── CHANGELOG.md
├── prompts/
│   ├── baseline_review.md
│   ├── candidate_review.md
│   └── finding_admission.md
├── schemas/
│   ├── review.schema.json
│   └── admission.schema.json
├── iteration_1/
│   ├── runner.py
│   └── batch.py
├── evals/
│   ├── cases/
│   ├── ground_truth.yaml
│   ├── evaluator.py
│   └── results/
└── tests/
```

## Reproducibility

The repository preserves:

- frozen prompts and schemas;
- deterministic evaluator and runner;
- twelve benchmark cases;
- baseline outputs;
- Iteration 1 candidate, admission, final, and scored outputs;
- all 24 Iteration 1 Codex Stage A/Stage B logs under `evals/results/iteration_1_logs/`;
- diagnostic outputs that exposed benchmark fixture defects.

### Clean-checkout verification

On Ubuntu/Debian, create the virtual environment with `python3` because a global `python` command is not guaranteed:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

# Project/orchestration smoke tests — expected green.
python -m pytest -q

# Re-materialize and reproduce the frozen score.
python -m iteration_1.runner materialize-scored
python evals/evaluator.py evals/results/iteration_1_scored
```

Expected deterministic score:

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

### Benchmark defect tests

The benchmark cases are **not** the project's default pytest target because some cases deliberately encode production defects. To inspect the benchmark tests directly, run:

```bash
python -m pytest evals/cases -q
```

That command is expected to include intentional failures for planted defects such as the transaction-consistency failure in `case_01` and idempotency failure in `case_02`. Those failures are benchmark evidence, not orchestration regressions.

See `docs/ITERATION_1_RUNBOOK.md` for the execution protocol, `docs/RESULTS.md` for the measured comparison, `docs/TRAJECTORIES.md` for representative agent behavior, `docs/DEMO.md` for the demo flow, and `experiments/CHANGELOG.md` for the full experiment history.

## Current Result

**Iteration 1 is the current best measured system.**

It improves Production Defect Detection F1 from **0.880 to 0.957** and precision from **78.6% to 91.7%**, while keeping recall at **100%**.

## Hot Take

> The bottleneck in AI-assisted software engineering is shifting from code generation to evidence generation — and once agents generate enough plausible evidence, evidence admission becomes its own engineering problem.

Strong review agents do not only need to find defects. They need a disciplined mechanism for deciding which findings are worth a human's attention.

## Status

Core experiment and clean-checkout reproducibility verification complete. Current work is final judge-facing packaging and video presentation.