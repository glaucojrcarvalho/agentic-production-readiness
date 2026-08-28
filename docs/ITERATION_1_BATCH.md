# Iteration 1 — Automated Codex Batch Run

The full twelve-case Iteration 1 experiment can be run non-interactively with the Codex CLI while preserving the experimental protocol: every Stage A and Stage B invocation is a separate `codex exec` process, so each stage receives a fresh model context.

## Command

Pull the latest repository changes, then run:

```bash
python -m iteration_1.batch --force
```

This runs `case_01` through `case_12`. For each case it:

1. launches a fresh Codex Stage A candidate-review process;
2. writes `candidates.json`;
3. validates it with `iteration_1.runner`;
4. launches a separate fresh Codex Stage B admission process;
5. writes `admission.json`;
6. validates the admission report and materializes `final.json` plus the flat scored file.

The batch script uses the configured Codex model by default. To pin a model explicitly:

```bash
python -m iteration_1.batch --force --model <MODEL>
```

Pinning the same model for all cases is preferred for a scored run.

## Existing Case 06 Diagnostic

`--force` deletes only Iteration 1 artifacts for the selected cases before rerunning them. If the existing `case_06` diagnostic artifacts should be preserved as experiment history, archive them before starting the scored batch:

```bash
mkdir -p evals/results/iteration_1_diagnostic
mv evals/results/iteration_1/case_06 \
  evals/results/iteration_1_diagnostic/case_06
rm -f evals/results/iteration_1_scored/case_06.json
```

Then run the full batch with `--force`. The diagnostic copy remains separate from scored artifacts.

## Resume After Interruption

If the batch stops because of a network failure, Codex error, terminal interruption, or another transient problem, rerun with:

```bash
python -m iteration_1.batch --resume
```

Existing candidate files are schema-validated before being reused. Existing admission files are validated through the normal finalize path.

Do not use `--force` when resuming because it intentionally removes the selected Iteration 1 artifacts.

## Run Selected Cases

For development or recovery:

```bash
python -m iteration_1.batch --cases case_04 case_05
```

The same `--resume`, `--force`, and `--model` options apply.

## Logs

Codex stdout/stderr for every stage is retained under:

```text
evals/results/iteration_1_logs/
  case_01_stage_a.log
  case_01_stage_b.log
  ...
```

These logs are useful for debugging and for preserving representative agent trajectories. Codex's own local session history may provide additional trajectory detail.

## Isolation Rules

Each generated prompt explicitly forbids access to:

- `evals/ground_truth.yaml`;
- `evals/verify_cases.py`;
- outputs from other evaluation cases;
- benchmark scores or known expected defect categories.

The script runs Codex with `workspace-write` sandboxing and approval policy `never` to make the batch non-interactive. It does **not** use the dangerous sandbox-bypass option.

## Score the Full Run

After all twelve cases complete:

```bash
python -m iteration_1.runner materialize-scored
python evals/evaluator.py evals/results/iteration_1_scored
```

Compare against the frozen baseline:

```text
precision = 0.786
recall = 1.000
F1 = 0.880
decision accuracy = 1.000
evidence-grounded finding rate = 1.000
```
