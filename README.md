# Agentic Production Readiness

An evidence-driven agentic workflow for reviewing AI-generated backend changes before they reach production.

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

An agentic workflow that gathers repository context, executes available verification tools, checks suspected defects, and reports uncertainty explicitly will detect production-readiness defects more reliably than a simple general-purpose review agent.

## Baseline

The baseline is intentionally simple:

> A general-purpose coding agent receives the repository/change and a direct instruction to review it for production readiness.

The baseline and advanced workflow will receive the same evaluation cases and will be scored with the same rubric.

## Advanced Direction

The advanced workflow will evolve experimentally rather than being fixed upfront. Candidate capabilities include:

1. context discovery;
2. targeted test execution;
3. static and runtime evidence gathering;
4. defect hypothesis generation;
5. explicit verification of suspected findings;
6. evidence-backed final assessment;
7. uncertainty and confidence reporting.

Every additional component must justify its existence through measured improvement.

## Primary Metric

**Production Defect Detection F1 score**

This balances two things that matter to a real reviewer:

- recall: finding real production defects;
- precision: avoiding invented or irrelevant problems.

## Secondary Metrics

- precision;
- recall;
- false-positive rate;
- evidence-grounded finding rate;
- human review time;
- latency;
- approximate cost per case.

## Evaluation Principle

The baseline and advanced solution will be evaluated on the same fixed set of backend engineering cases with known ground truth.

The evaluation set should include both defective and valid changes. At least one difficult case should expose a failure mode that meaningfully changes the design.

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
agent improvement
      ↓
re-evaluate
      ↓
keep / revise / remove
      ↓
final system
```

The goal is not to build the most complex agent system. The goal is to build the smallest system whose design choices are supported by evidence.

## Repository Structure

```text
.
├── README.md
├── docs/
│   ├── PROBLEM.md
│   ├── EVALUATION.md
│   └── ARCHITECTURE.md
├── experiments/
│   └── CHANGELOG.md
├── src/
│   ├── baseline/
│   ├── agent/
│   └── shared/
├── evals/
│   ├── cases/
│   ├── ground_truth/
│   └── results/
├── tests/
└── trajectories/
    ├── baseline/
    └── advanced/
```

Implementation directories will be added only when needed.

## Status

Planning and evaluation design.

No advanced agent architecture is considered final until it demonstrates measurable improvement over the baseline.
