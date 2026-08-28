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

**Status:** planned

### Approach

A general-purpose coding agent receives the evaluation repository/change and a direct instruction to review it for production readiness.

No custom orchestration or specialized verification workflow.

### Why

Establish the performance of a simple, reasonable agent workflow before introducing project-specific improvements.

### Evidence

TBD after the evaluation dataset and baseline runner are implemented.

### Decision / Learning

TBD.

---

## Iteration 1

**Status:** not started

### Observation / Hypothesis

TBD from baseline failures.

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
