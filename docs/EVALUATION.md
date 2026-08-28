# Evaluation Contract

This document defines how the project will measure whether the agentic workflow actually improves production-readiness review.

The evaluation should be established before the advanced solution is optimized against it.

## Primary Question

> On the same backend engineering cases, does the advanced workflow identify real production defects more accurately than a simple general-purpose review agent?

## Primary Metric

### Production Defect Detection F1

Each case has known ground-truth defects. The system produces a structured set of findings. Findings are matched against the ground truth using a documented matching rule.

We compute:

- **Precision** = true positive findings / all reported findings
- **Recall** = true positive findings / all ground-truth defects
- **F1** = harmonic mean of precision and recall

F1 is the primary metric because a useful reviewer must both detect real issues and avoid overwhelming the human with speculative findings.

## Secondary Metrics

### False-positive rate

How often the system reports defects that are not present.

### Evidence-grounded finding rate

Percentage of reported findings that include enough concrete evidence for a reviewer to verify the claim.

Evidence may include:

- file and line references;
- test failures;
- runtime output;
- reproducible commands;
- configuration or dependency evidence;
- a minimal execution trace.

### Human review time

Approximate time required for a human to interpret the final result and decide what to investigate next.

### Latency

Wall-clock time per evaluation case.

### Cost per case

Approximate model/API cost per case when applicable.

## Evaluation Dataset

Target: **12–15 fixed cases** if implementation time allows, with at least 10 completed cases.

The cases should be small enough to reproduce quickly but realistic enough to require engineering judgment.

Candidate categories:

| Case | Candidate defect | Expected evidence |
|---|---|---|
| 01 | missing transaction rollback | failing state-consistency test or code-path evidence |
| 02 | race condition | concurrent execution test |
| 03 | non-idempotent write endpoint | duplicate-request test |
| 04 | N+1 query | query count or code-path evidence |
| 05 | authorization boundary failure | access-control test |
| 06 | unsafe retry policy | reproducible duplicate side effect |
| 07 | swallowed exception | incorrect response/logging behavior |
| 08 | pagination boundary error | deterministic boundary test |
| 09 | timezone bug | fixed timestamp case |
| 10 | state-transition inconsistency | invalid transition test |
| 11 | valid implementation | no material defect expected |
| 12 | multiple interacting defects | more difficult composite case |

This table is a planning target, not final ground truth. Every case must have an unambiguous expected result before it enters the scored evaluation set.

## Ground-Truth Schema

Each case should include machine-readable metadata similar to:

```yaml
case_id: case_03
title: duplicate payment request
expected_status: defective
defects:
  - id: D1
    category: idempotency
    severity: high
    location: src/payments/service.py
    description: repeated request can create a duplicate charge
    verification:
      command: pytest tests/test_idempotency.py -q
      expected: test fails before fix
```

Ground truth must not be exposed to the agent during evaluation.

## Finding Schema

Both baseline and advanced solution should emit the same normalized shape where possible:

```json
{
  "case_id": "case_03",
  "decision": "not_ready",
  "findings": [
    {
      "category": "idempotency",
      "severity": "high",
      "claim": "Repeated requests can trigger the side effect twice.",
      "evidence": ["..."],
      "verified": true,
      "confidence": 0.95
    }
  ],
  "uncertainties": []
}
```

A shared output schema makes scoring and comparison easier and reduces evaluator bias.

## Baseline Protocol

The baseline receives:

- the exact same case repository/change as the advanced solution;
- the same user goal: review production readiness;
- standard repository access defined for the experiment.

The baseline uses a single direct review instruction and no custom orchestration or specialized verification workflow.

The exact prompt, model, tools, versions, temperature/settings where relevant, runtime, and cost must be recorded.

## Advanced Protocol

The advanced system receives the same case and task.

Any additional resources or capabilities must be documented explicitly. If it has different tools, context, or execution privileges, that difference must be part of the experiment report rather than hidden.

## Fair-Comparison Rules

1. Baseline and advanced solution use the same scored cases.
2. Ground truth is hidden from both systems.
3. Evaluation code is fixed before the final comparison.
4. Any case changes after observing results must be documented.
5. Failed runs are retained rather than silently discarded.
6. Repeated trials, if used, follow the same policy for both systems.
7. Resource differences are reported.
8. The final report includes all scored cases, not only successful examples.

## Finding Matching

A reported finding counts as a true positive only when it matches a ground-truth defect in substance, not merely by sharing a broad category.

Example:

- Ground truth: duplicate charge caused by missing idempotency protection.
- Valid match: "Retrying POST /payments can create a second charge because no idempotency key is persisted."
- Invalid match: "The endpoint may have concurrency problems."

The final evaluator should use deterministic matching where possible. If human matching is required, the rubric must be written before scoring and applied consistently.

## Challenging Case

At least one case should be deliberately difficult and should teach us something about the system design.

A good candidate is a change that appears suspicious statically but is actually safe because of a constraint elsewhere in the repository. This tests whether the agent gathers enough context before raising a finding and exposes false-positive behavior.

## Experiment Decision Rule

For every meaningful architectural change:

1. state the observed failure or hypothesis;
2. implement one targeted intervention;
3. run the same evaluation;
4. record primary and secondary metrics;
5. decide to keep, revise, or remove the change.

No component earns a place in the final architecture solely because it sounds agentic.

## Final Comparison

The final report should include at minimum:

| Metric | Baseline | Final | Change |
|---|---:|---:|---:|
| Defect Detection F1 | TBD | TBD | TBD |
| Precision | TBD | TBD | TBD |
| Recall | TBD | TBD | TBD |
| False-positive rate | TBD | TBD | TBD |
| Evidence-grounded findings | TBD | TBD | TBD |
| Median runtime/case | TBD | TBD | TBD |
| Approx. cost/case | TBD | TBD | TBD |

All final claims must be traceable to saved evaluation artifacts.
