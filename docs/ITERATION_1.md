# Iteration 1 — Finding Admission and Consolidation

## Goal

Improve review precision without sacrificing the baseline's perfect recall.

The twelve-case baseline scored:

- precision: 0.786;
- recall: 1.000;
- F1: 0.880;
- decision accuracy: 1.000;
- evidence-grounded finding rate: 1.000.

The measured weakness is over-reporting, not missed defects.

## Design Principle

Do not ask another agent to find more bugs unless evaluation shows a recall problem.

Iteration 1 keeps broad candidate generation, then introduces a stricter admission boundary before findings are shown to a human reviewer.

## Provisional Workflow

```text
case
  |
  v
candidate reviewer
  |
  v
evidence/scope critic
  |
  v
root-cause consolidator
  |
  v
final review
```

The stages may later be implemented as separate agents, separate model calls, or deterministic code plus model calls. The architecture is provisional until measured.

## Candidate Reviewer

Purpose: maximize useful defect discovery while remaining grounded in the case.

Responsibilities:

- inspect source, tests, and explicit case contract when present;
- run safe local verification probes when useful;
- produce concrete candidate findings using the canonical taxonomy;
- attach code or runtime evidence;
- distinguish verified behavior from uncertainty.

This stage should not be optimized for final precision. Its output is candidate material for the admission stage.

## Evidence / Scope Critic

Purpose: decide whether each candidate finding deserves admission to the final human-facing review.

For every candidate, answer these questions:

1. **Concrete failure** — Is there a specific failure mode rather than a generic best-practice concern?
2. **Evidence** — Is the claim supported by code, runtime behavior, an explicit contract, or a strongly implied invariant?
3. **Scope** — Does the finding apply to the supplied implementation and supported usage, rather than hypothetical callers or infrastructure?
4. **Materiality** — Could this plausibly affect production correctness, security, reliability, data integrity, or operational performance?
5. **Independence** — Is this a distinct root cause, or merely another symptom/consequence of an already admitted finding?

### Admission Rule

A candidate is admitted only when all of the following are true:

- it describes a concrete production-impacting failure;
- it has directly inspectable or reproducible evidence;
- it is within the explicit or strongly implied contract of the reviewed component;
- it is material enough to justify human attention;
- it is not redundant with a stronger finding that captures the same root cause.

### Reject as Non-Finding

Reject or demote candidates that are only:

- generic hardening advice;
- hypothetical misuse by unknown callers;
- infrastructure assumptions not represented in the case;
- style or API preference without material consequence;
- duplicate symptoms of the same root cause;
- unsupported speculation.

Rejected candidates may be retained internally for trajectory/debugging, but must not appear in the final `findings` array.

## Root-Cause Consolidator

Purpose: reduce duplicate findings without collapsing genuinely independent defects.

Two candidates should normally be merged when:

- they have the same category;
- they arise from the same implementation decision or missing control;
- fixing the root cause would resolve both reported symptoms;
- reporting them separately would not change the remediation decision.

Do **not** merge findings merely because they share a file, function, severity, or category. Composite cases can contain multiple independent defects.

The consolidated finding should preserve the strongest evidence from the merged candidates and describe the common production consequence.

## Decision Rule

After admission and consolidation:

- `not_ready` when at least one admitted material finding remains;
- `ready` when no admitted material findings remain.

Uncertainties must not independently force `not_ready`.

## Output Contract

The final output must continue to match `schemas/review.schema.json` exactly.

The canonical taxonomy remains frozen. Iteration 1 does not modify ground truth or scoring rules.

## Experimental Controls

For a fair comparison with baseline:

- use the same twelve evaluation cases;
- do not expose `evals/ground_truth.yaml` or `evals/verify_cases.py` to the reviewer workflow;
- do not change case fixtures after the Iteration 1 run begins unless a genuine benchmark defect is discovered and documented;
- keep the canonical taxonomy and final review schema unchanged;
- record prompts/instructions and representative trajectories for every agent or stage used;
- evaluate with the same evaluator.

## Success Criteria

Iteration 1 succeeds only if:

- precision > 0.786;
- recall = 1.000;
- F1 > 0.880;
- decision accuracy = 1.000;
- evidence-grounded finding rate = 1.000.

Improving precision by suppressing true defects is a failed experiment.

## Primary Risk

An aggressive critic may improve precision by filtering legitimate but less obvious defects, causing recall to fall. The critic therefore needs to challenge candidate findings without defaulting to rejection.

## What We Are Testing

This iteration tests a specific hypothesis:

> A production-readiness reviewer benefits from separating defect discovery from finding admission.

If the results do not improve, the critic/consolidator architecture should be revised or removed rather than retained for complexity's sake.
