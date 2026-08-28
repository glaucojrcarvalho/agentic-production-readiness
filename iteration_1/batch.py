from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = [f"case_{index:02d}" for index in range(1, 13)]
RESULTS_ROOT = ROOT / "evals" / "results" / "iteration_1"
SCORED_ROOT = ROOT / "evals" / "results" / "iteration_1_scored"
LOG_ROOT = ROOT / "evals" / "results" / "iteration_1_logs"


def run_streaming(command: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"$ {' '.join(command)}")

    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            log.write(line)

        return_code = process.wait()

    if return_code != 0:
        raise SystemExit(
            f"command failed with exit code {return_code}; see {log_path.relative_to(ROOT)}"
        )


def codex_command(prompt: str, model: str | None) -> list[str]:
    command = [
        "codex",
        "--sandbox",
        "workspace-write",
        "--ask-for-approval",
        "never",
        "--cd",
        str(ROOT),
    ]
    if model:
        command.extend(["--model", model])
    command.extend(["exec", prompt])
    return command


def stage_a_prompt(case_id: str) -> str:
    return f"""Review evals/cases/{case_id} for production readiness.

Use:
- prompts/candidate_review.md
- schemas/review.schema.json

Do not inspect or use:
- evals/ground_truth.yaml
- evals/verify_cases.py
- outputs from other evaluation cases
- benchmark scores or known expected defects

Write only the schema-valid candidate review JSON to:

evals/results/iteration_1/{case_id}/candidates.json

Do not modify the case files. Follow prompts/candidate_review.md exactly.
"""


def stage_b_prompt(case_id: str) -> str:
    return f"""Review the candidate findings for evals/cases/{case_id}.

Use:
- evals/results/iteration_1/{case_id}/candidates.json
- prompts/finding_admission.md
- schemas/review.schema.json
- schemas/admission.schema.json

Do not inspect or use:
- evals/ground_truth.yaml
- evals/verify_cases.py
- outputs from other evaluation cases
- benchmark scores or known expected defects

Write only the schema-valid admission report JSON to:

evals/results/iteration_1/{case_id}/admission.json

Do not modify the case files. Follow prompts/finding_admission.md exactly.
"""


def validate_candidates(case_id: str, candidates: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "iteration_1.runner",
            "validate-candidates",
            case_id,
            str(candidates.relative_to(ROOT)),
        ],
        cwd=ROOT,
        check=True,
    )


def finalize(case_id: str, candidates: Path, admission: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "iteration_1.runner",
            "finalize",
            case_id,
            str(candidates.relative_to(ROOT)),
            str(admission.relative_to(ROOT)),
        ],
        cwd=ROOT,
        check=True,
    )


def clear_case(case_id: str) -> None:
    case_dir = RESULTS_ROOT / case_id
    scored_file = SCORED_ROOT / f"{case_id}.json"
    logs = [
        LOG_ROOT / f"{case_id}_stage_a.log",
        LOG_ROOT / f"{case_id}_stage_b.log",
    ]

    if case_dir.exists():
        shutil.rmtree(case_dir)
    if scored_file.exists():
        scored_file.unlink()
    for log in logs:
        if log.exists():
            log.unlink()


def run_case(case_id: str, model: str | None, resume: bool) -> None:
    case_dir = RESULTS_ROOT / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    candidates = case_dir / "candidates.json"
    admission = case_dir / "admission.json"

    print(f"\n=== {case_id}: Stage A / candidate reviewer ===")
    if resume and candidates.exists():
        validate_candidates(case_id, candidates)
        print("existing candidate artifact is valid; skipping Stage A")
    else:
        if candidates.exists():
            raise SystemExit(
                f"{candidates.relative_to(ROOT)} already exists; use --resume or --force"
            )
        run_streaming(
            codex_command(stage_a_prompt(case_id), model),
            LOG_ROOT / f"{case_id}_stage_a.log",
        )
        if not candidates.exists():
            raise SystemExit(f"Stage A did not create {candidates.relative_to(ROOT)}")
        validate_candidates(case_id, candidates)

    print(f"\n=== {case_id}: Stage B / admission critic ===")
    if resume and admission.exists():
        print("existing admission artifact found; validating through finalize")
    else:
        if admission.exists():
            raise SystemExit(
                f"{admission.relative_to(ROOT)} already exists; use --resume or --force"
            )
        run_streaming(
            codex_command(stage_b_prompt(case_id), model),
            LOG_ROOT / f"{case_id}_stage_b.log",
        )
        if not admission.exists():
            raise SystemExit(f"Stage B did not create {admission.relative_to(ROOT)}")

    finalize(case_id, candidates, admission)
    print(f"=== {case_id}: complete ===")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the frozen two-stage Iteration 1 protocol through Codex CLI."
    )
    parser.add_argument(
        "--cases",
        nargs="+",
        choices=CASES,
        default=CASES,
        help="Cases to run. Defaults to case_01 through case_12.",
    )
    parser.add_argument(
        "--model",
        help="Optional Codex model override. Omit to use the configured default.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse already-valid stage artifacts and continue incomplete cases.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete Iteration 1 artifacts for selected cases before running them again.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.resume and args.force:
        raise SystemExit("--resume and --force are mutually exclusive")

    if args.force:
        for case_id in args.cases:
            clear_case(case_id)

    for case_id in args.cases:
        run_case(case_id, args.model, args.resume)

    print("\nAll selected cases completed.")
    print("When all 12 cases are present, run:")
    print("  python -m iteration_1.runner materialize-scored")
    print("  python evals/evaluator.py evals/results/iteration_1_scored")


if __name__ == "__main__":
    main()
