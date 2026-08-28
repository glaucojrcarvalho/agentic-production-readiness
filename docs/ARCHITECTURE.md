# Architecture Notes

This document records the current architectural direction. It is intentionally provisional.

The final architecture must emerge from evaluation results rather than from a desire to maximize the number of agents or components.

## Design Principle

> Add a capability only when it addresses an observed failure mode or produces measurable improvement.

## Baseline Architecture

The baseline should remain deliberately simple:

```text
repository / code change
        ↓
general-purpose coding agent
        ↓
production-readiness review
```

The baseline establishes what a competent direct agent can already do without custom orchestration.

## Candidate Advanced Workflow

```text
                 repository / code change
                          │
                          ▼
                  Context Discovery
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
    Relevant code      Tests/tools      Config/deps
          │               │                │
          └───────────────┼────────────────┘
                          ▼
                  Risk Hypotheses
                          │
                          ▼
                 Targeted Verification
                          │
                 ┌────────┴────────┐
                 │                 │
          insufficient evidence   verified/refuted
                 │                 │
                 └──── gather ─────┘
                          │
                          ▼
                Evidence-backed Review
```

This is a working hypothesis, not a commitment.

## Candidate Capabilities

### 1. Context discovery

Identify only the repository context necessary to understand the changed behavior.

Potential value:

- reduces incorrect assumptions;
- exposes architectural constraints hidden outside the diff;
- may reduce false positives.

Risk:

- excessive context increases cost and distracts the model.

### 2. Tool-assisted evidence gathering

Potential tools may include:

- test runner;
- targeted scripts;
- static analysis;
- repository search;
- dependency/configuration inspection;
- controlled runtime execution.

Potential value:

- converts plausible claims into observable evidence.

Risk:

- tool output can be noisy or misinterpreted.

### 3. Risk hypothesis generation

The agent proposes a small set of concrete production-risk hypotheses rather than immediately writing a final review.

Potential value:

- separates suspicion from conclusion;
- makes verification targeted.

Risk:

- may add latency without improving accuracy.

### 4. Verification

Each material finding should be verified when practical.

Verification can:

- confirm a suspected defect;
- refute a false positive;
- downgrade confidence when evidence is incomplete.

This is currently the most important candidate improvement over the baseline.

### 5. Structured final assessment

The final output should distinguish:

- verified findings;
- unverified concerns;
- severity;
- evidence;
- uncertainty;
- recommended human action.

## One Agent or Multiple Agents?

Undecided.

A multi-agent design is not assumed to be better. Initial experiments should prefer the simplest implementation capable of testing the hypothesis.

Possible progression:

```text
single baseline agent
        ↓
single agent + tools
        ↓
single agent + explicit verification loop
        ↓
only then test specialized/multi-agent orchestration
```

A specialized critic or verifier should be kept only if it improves evaluation results enough to justify extra complexity, latency, and cost.

## Human Control

The system is advisory.

It must not autonomously merge, deploy, modify production systems, or perform consequential actions. The final decision remains with the human reviewer.

## Reproducibility Requirements

The final implementation should make the following explicit:

- Python/runtime version;
- dependency versions;
- model/provider configuration;
- required environment variables;
- exact baseline command;
- exact advanced-workflow command;
- exact evaluation command;
- expected output locations;
- approximate runtime;
- approximate cost.

Where practical, evaluation cases should avoid external dependencies that make results difficult to reproduce.

## Observability

Each run should produce enough structured trace data to reconstruct:

1. initial instructions;
2. context requested;
3. tools called;
4. tool results;
5. hypotheses formed;
6. verification attempts;
7. retries;
8. human checkpoints, if any;
9. final output;
10. timing and cost metadata where available.

These traces serve both debugging and hackathon trajectory requirements.

## Open Architectural Questions

These should be answered through experiments:

1. Does explicit context discovery improve precision?
2. Does tool execution improve recall, precision, or both?
3. Does a dedicated verification phase reduce false positives?
4. Is a second agent better than a verification loop in one agent?
5. How much repository context is enough?
6. Does structured uncertainty improve usefulness without harming detection metrics?
7. Which verification techniques produce the best improvement per unit of cost/latency?

## Current Architecture Status

**Not frozen.**

The only committed design decisions are:

- evaluation comes first;
- baseline remains simple;
- baseline and advanced solution use the same scored cases;
- findings should be evidence-backed;
- consequential decisions remain human-controlled;
- architectural complexity must be justified by measured improvement.
