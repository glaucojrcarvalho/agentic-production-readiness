# Five-Minute Demo Plan

Goal: explain the problem, show the measured failure, show the smallest justified agentic change, and finish with reproducible evidence. Do not spend the video walking through every file.

## 0:00–0:35 — Problem and Thesis

Open `README.md`.

Say:

> AI can generate backend code that looks correct and passes happy-path tests while still failing under production conditions. My project asks a narrower question: can an agent reviewer distinguish defects that deserve human attention from plausible but noisy findings?

Show the intended user: senior backend engineers and technical leads reviewing AI-generated changes.

State the hot take:

> As code generation improves, the bottleneck shifts toward evidence generation — and then toward evidence admission.

## 0:35–1:10 — Evaluation-First Setup

Show the twelve-case benchmark and `docs/EVALUATION.md` briefly.

Explain that both systems use:

- the same cases;
- the same defect taxonomy;
- the same final JSON schema;
- the same deterministic evaluator;
- hidden ground truth and hidden benchmark-construction probes.

Mention the two clean controls and the composite two-defect case.

The important message is that the architecture was chosen after measuring the baseline, not before.

## 1:10–1:50 — Baseline Failure

Open `evals/results/baseline/case_06.json`.

Show the four findings in the retry helper.

Explain:

> The baseline found every expected defect across the full benchmark. Recall was already 100%. But in this case it promoted several plausible concerns into final findings, producing three false positives.

Show the baseline aggregate:

```text
Precision  0.786
Recall     1.000
F1         0.880
FP         3
```

Transition:

> So adding more defect-discovery agents would not address the measured problem. The measured problem was admission quality.

## 1:50–2:40 — Iteration 1 Architecture

Show the architecture from `README.md` or `docs/ITERATION_1_IMPLEMENTATION.md`:

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
```

Explain Stage A is intentionally broad. Stage B evaluates every candidate for:

- concrete failure;
- evidence;
- scope;
- materiality;
- independence.

Emphasize that Stage B cannot broadly invent unrelated findings.

## 2:40–3:35 — One Real Trajectory

Use `case_06`.

First open:

`evals/results/iteration_1/case_06/candidates.json`

Show that Stage A still generates multiple concerns.

Then open:

`evals/results/iteration_1/case_06/admission.json`

Show the adjudications. Point out that the validation concern is rejected because it is concrete but not shown to be materially production-impacting under the supplied contract/evidence.

Then open:

`evals/results/iteration_1/case_06/final.json`

Explain that two retry-policy findings remain. One is the expected defect; the second is technically defensible but not represented separately in hidden ground truth.

Say:

> I deliberately did not tune that finding away after seeing the score. The goal is a credible reviewer, not a benchmark-perfect reviewer.

## 3:35–4:15 — Measured Improvement

Open `docs/RESULTS.md`.

Show:

```text
                  Baseline   Iteration 1
Precision           0.786        0.917
Recall              1.000        1.000
F1                  0.880        0.957
False positives         3            1
```

State:

> The second stage cut false positives by two-thirds and preserved every true positive. F1 improved from 0.880 to 0.957.

Briefly mention `case_12`: both independent defects survived admission. Mention `case_11`: clean control remained ready with zero findings.

## 4:15–4:45 — Reproducibility

Show the repository artifacts:

- frozen prompts;
- schemas;
- deterministic runner/evaluator;
- baseline outputs;
- candidate/admission/final outputs;
- 24 raw Stage A/Stage B Codex logs;
- experiment changelog.

Show the reproduction command:

```bash
python -m iteration_1.runner materialize-scored
python evals/evaluator.py evals/results/iteration_1_scored
```

If time permits, run the evaluator and show the aggregate JSON.

## 4:45–5:00 — Close

End with:

> My main result is not that two agents are better than one. It is that agent architecture should follow measured failure modes. Here, discovery was already strong. The useful second agent was the one deciding which evidence deserved a human's attention.

## Screen Preparation

Before recording, have these files already open in tabs:

1. `README.md`
2. `evals/results/baseline/case_06.json`
3. `evals/results/iteration_1/case_06/candidates.json`
4. `evals/results/iteration_1/case_06/admission.json`
5. `evals/results/iteration_1/case_06/final.json`
6. `docs/RESULTS.md`
7. `docs/TRAJECTORIES.md`

Keep terminal ready with the evaluator command. Avoid live-running Codex during the video; the stored trajectories are more reproducible and avoid wasting the five-minute limit.