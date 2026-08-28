# Problem Definition

## Working Title

**Agentic Production Readiness Reviewer**

## Intended User

The primary user is a senior backend engineer or technical lead responsible for reviewing AI-generated code changes before they are merged or deployed.

## User Job to Be Done

> Given an unfamiliar or AI-generated backend change, determine whether it is production-ready, identify material risks, and provide evidence that supports the decision without wasting reviewer time on speculative findings.

## Current Bottleneck

Modern coding agents can generate substantial backend changes quickly. Review capacity does not scale at the same rate.

The reviewer must determine whether a change is merely convincing or actually safe under realistic production conditions. That requires more than reading the diff. Important evidence may be distributed across tests, neighboring code, persistence behavior, configuration, concurrency assumptions, dependency usage, and runtime output.

A shallow review can miss defects. An overly suspicious review can generate many false positives and increase human workload.

## Failure Classes We Care About

The initial evaluation taxonomy may include:

- transaction and rollback errors;
- non-idempotent operations;
- race conditions and concurrent-update bugs;
- authentication and authorization boundary mistakes;
- unsafe retry behavior;
- swallowed or incorrectly mapped exceptions;
- N+1 query or obvious data-access inefficiency;
- pagination or boundary-condition errors;
- time and timezone bugs;
- missing validation;
- inconsistent state transitions;
- inadequate tests for consequential behavior;
- false positives on valid implementations.

This taxonomy is provisional. Cases should be included only when we can define clear ground truth and reproducible evidence.

## Why This Is Worth Solving

The value is not simply faster code review. The intended benefit is better allocation of scarce senior-engineering attention.

A useful system should help a reviewer answer:

1. What could fail in production?
2. What evidence supports that concern?
3. Has the concern been verified where possible?
4. How severe is it?
5. What remains uncertain?
6. Is the change ready for human approval?

## Product Boundary

This project is a decision-support system, not an autonomous deployment gate.

It may recommend that a change is ready, risky, or requires further investigation, but consequential actions remain under human control.

## Core Hypothesis

A review workflow that actively gathers and verifies evidence will outperform a direct general-purpose agent review on a fixed set of backend production-readiness cases.

## What Would Falsify the Hypothesis?

The hypothesis should be considered unsupported if the advanced workflow:

- fails to improve F1 over the baseline;
- improves recall only by producing an unacceptable number of false positives;
- relies on substantially different information than the baseline without documenting the comparison;
- cannot reproduce its results consistently;
- adds orchestration or agent complexity without measurable benefit.

## Non-Goals

For the hackathon scope, this is not intended to become:

- a general code-quality scoring platform;
- a full static-analysis replacement;
- an autonomous merge or deployment system;
- a generic RAG assistant;
- a complete security scanner;
- an architecture-review platform for arbitrary large repositories.

## Desired Final Experience

A user provides an evaluation repository or code change. The system investigates it, runs allowed verification steps, and returns a concise review containing:

- decision/status;
- verified findings;
- severity;
- exact evidence;
- relevant test or tool output;
- unresolved uncertainty;
- recommended next human action.

The output should be useful enough that a senior engineer could reasonably use it as part of a real review rather than treating it as an AI-generated draft that must be redone from scratch.
