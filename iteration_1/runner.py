from __future__ import annotations

import argparse
import copy
import json
import shutil
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REVIEW_SCHEMA_PATH = ROOT / "schemas" / "review.schema.json"
ADMISSION_SCHEMA_PATH = ROOT / "schemas" / "admission.schema.json"
DEFAULT_RESULTS_ROOT = ROOT / "evals" / "results" / "iteration_1"
DEFAULT_SCORED_ROOT = ROOT / "evals" / "results" / "iteration_1_scored"


class ArtifactValidationError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ArtifactValidationError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def review_schema() -> dict[str, Any]:
    return load_json(REVIEW_SCHEMA_PATH)


def admission_schema() -> dict[str, Any]:
    schema = copy.deepcopy(load_json(ADMISSION_SCHEMA_PATH))
    schema["properties"]["final_review"] = review_schema()
    return schema


def _validate_schema(instance: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    errors = sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )
    if not errors:
        return

    details = []
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path) or "<root>"
        details.append(f"{path}: {error.message}")
    raise ArtifactValidationError(f"invalid {label}: " + "; ".join(details))


def validate_review(review: dict[str, Any], case_id: str, label: str = "review") -> None:
    _validate_schema(review, review_schema(), label)
    if review["case_id"] != case_id:
        raise ArtifactValidationError(
            f"{label} case_id {review['case_id']!r} does not match {case_id!r}"
        )

    expected_decision = "not_ready" if review["findings"] else "ready"
    if review["decision"] != expected_decision:
        raise ArtifactValidationError(
            f"{label} decision must be {expected_decision!r} for its findings array"
        )


def validate_admission(
    admission: dict[str, Any],
    candidates: dict[str, Any],
    case_id: str,
) -> None:
    _validate_schema(admission, admission_schema(), "admission report")

    if admission["case_id"] != case_id:
        raise ArtifactValidationError(
            f"admission case_id {admission['case_id']!r} does not match {case_id!r}"
        )

    validate_review(candidates, case_id, "candidate review")
    validate_review(admission["final_review"], case_id, "final review")

    count = len(candidates["findings"])
    adjudications = admission["adjudications"]
    indices = [item["candidate_index"] for item in adjudications]

    if sorted(indices) != list(range(count)):
        raise ArtifactValidationError(
            "adjudications must cover every candidate index exactly once "
            f"(expected 0..{count - 1}, got {sorted(indices)})"
        )

    by_index = {item["candidate_index"]: item for item in adjudications}
    admitted = {
        index
        for index, item in by_index.items()
        if item["outcome"] == "admit"
    }
    merged = {
        index: item["merge_into"]
        for index, item in by_index.items()
        if item["outcome"] == "merge"
    }

    for source, target in merged.items():
        if target == source:
            raise ArtifactValidationError(f"candidate {source} cannot merge into itself")
        if target not in admitted:
            raise ArtifactValidationError(
                f"candidate {source} merges into {target}, but target is not admitted"
            )

    group_targets: set[int] = set()
    grouped_sources: set[int] = set()
    for group in admission["merge_groups"]:
        target = group["target_candidate_index"]
        sources = group["merged_candidate_indices"]
        if target not in admitted:
            raise ArtifactValidationError(
                f"merge group target {target} must be an admitted candidate"
            )
        if target in sources:
            raise ArtifactValidationError(
                f"merge group target {target} cannot also be a merged source"
            )
        group_targets.add(target)
        grouped_sources.update(sources)
        for source in sources:
            if merged.get(source) != target:
                raise ArtifactValidationError(
                    f"merge group says candidate {source} merges into {target}, "
                    "but adjudication does not"
                )

    if grouped_sources != set(merged):
        missing = sorted(set(merged) - grouped_sources)
        extra = sorted(grouped_sources - set(merged))
        raise ArtifactValidationError(
            f"merge_groups do not match merge adjudications; missing={missing}, extra={extra}"
        )

    if len(admission["final_review"]["findings"]) > len(admitted):
        raise ArtifactValidationError(
            "final review contains more findings than admitted root candidates"
        )


def case_paths(case_id: str, results_root: Path) -> dict[str, Path]:
    case_dir = results_root / case_id
    return {
        "case_dir": case_dir,
        "candidates": case_dir / "candidates.json",
        "admission": case_dir / "admission.json",
        "final": case_dir / "final.json",
    }


def validate_candidates(case_id: str, candidate_path: Path) -> None:
    candidates = load_json(candidate_path)
    validate_review(candidates, case_id, "candidate review")


def finalize_case(
    case_id: str,
    candidate_path: Path,
    admission_path: Path,
    final_path: Path,
    scored_path: Path,
) -> None:
    candidates = load_json(candidate_path)
    admission = load_json(admission_path)
    validate_admission(admission, candidates, case_id)
    final_review = admission["final_review"]
    write_json(final_path, final_review)
    write_json(scored_path, final_review)


def materialize_scored(results_root: Path, scored_root: Path) -> None:
    scored_root.mkdir(parents=True, exist_ok=True)
    for case_dir in sorted(path for path in results_root.glob("case_[0-9][0-9]") if path.is_dir()):
        final_path = case_dir / "final.json"
        if not final_path.exists():
            raise ArtifactValidationError(f"missing final artifact: {final_path}")
        review = load_json(final_path)
        validate_review(review, case_dir.name, "final review")
        write_json(scored_root / f"{case_dir.name}.json", review)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and materialize Iteration 1 review artifacts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_candidate_parser = subparsers.add_parser("validate-candidates")
    validate_candidate_parser.add_argument("case_id")
    validate_candidate_parser.add_argument("candidate_path", type=Path)

    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("case_id")
    finalize_parser.add_argument("candidate_path", type=Path)
    finalize_parser.add_argument("admission_path", type=Path)
    finalize_parser.add_argument(
        "--results-root", type=Path, default=DEFAULT_RESULTS_ROOT
    )
    finalize_parser.add_argument(
        "--scored-root", type=Path, default=DEFAULT_SCORED_ROOT
    )

    materialize_parser = subparsers.add_parser("materialize-scored")
    materialize_parser.add_argument(
        "--results-root", type=Path, default=DEFAULT_RESULTS_ROOT
    )
    materialize_parser.add_argument(
        "--scored-root", type=Path, default=DEFAULT_SCORED_ROOT
    )

    args = parser.parse_args()

    try:
        if args.command == "validate-candidates":
            validate_candidates(args.case_id, args.candidate_path)
            print(f"{args.case_id} candidate review valid")
            return

        if args.command == "finalize":
            paths = case_paths(args.case_id, args.results_root)
            scored_path = args.scored_root / f"{args.case_id}.json"
            finalize_case(
                args.case_id,
                args.candidate_path,
                args.admission_path,
                paths["final"],
                scored_path,
            )
            print(f"{args.case_id} admission valid; final artifacts written")
            return

        materialize_scored(args.results_root, args.scored_root)
        print(f"scored reviews materialized in {args.scored_root}")
    except (ArtifactValidationError, json.JSONDecodeError, OSError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
