from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
GROUND_TRUTH_PATH = ROOT / "evals" / "ground_truth.yaml"
SCHEMA_PATH = ROOT / "schemas" / "review.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_ground_truth() -> dict[str, dict[str, Any]]:
    with GROUND_TRUTH_PATH.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return {case["case_id"]: case for case in data["cases"]}


def load_schema() -> dict[str, Any]:
    return load_json(SCHEMA_PATH)


def load_reviews(results_dir: Path) -> dict[str, dict[str, Any]]:
    schema = load_schema()
    reviews: dict[str, dict[str, Any]] = {}

    for path in sorted(results_dir.glob("*.json")):
        review = load_json(path)
        validate(instance=review, schema=schema)
        case_id = review["case_id"]
        if case_id in reviews:
            raise ValueError(f"duplicate review for {case_id}")
        reviews[case_id] = review

    return reviews


def score_case(
    ground_truth: dict[str, Any], review: dict[str, Any]
) -> dict[str, Any]:
    """Score one case using the locked initial-slice matching rule.

    For the first three cases, each defective case contains exactly one material
    defect and each defect has a distinct category. A finding is a true positive
    only when its category exactly matches an unmatched ground-truth category.

    Wrong or additional categories are false positives. Unmatched ground-truth
    defects are false negatives. This rule is intentionally simple and must be
    revised before introducing cases with multiple defects in the same category.
    """

    expected_categories = [defect["category"] for defect in ground_truth["defects"]]
    unmatched = list(expected_categories)

    true_positives = 0
    false_positives = 0

    for finding in review["findings"]:
        category = finding["category"]
        if category in unmatched:
            true_positives += 1
            unmatched.remove(category)
        else:
            false_positives += 1

    false_negatives = len(unmatched)
    expected_decision = (
        "ready" if ground_truth["expected_status"] == "ready" else "not_ready"
    )

    evidence_grounded = sum(
        1 for finding in review["findings"] if len(finding.get("evidence", [])) > 0
    )

    return {
        "case_id": ground_truth["case_id"],
        "tp": true_positives,
        "fp": false_positives,
        "fn": false_negatives,
        "decision_correct": review["decision"] == expected_decision,
        "finding_count": len(review["findings"]),
        "evidence_grounded_findings": evidence_grounded,
    }


def safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def aggregate(case_scores: list[dict[str, Any]]) -> dict[str, Any]:
    tp = sum(case["tp"] for case in case_scores)
    fp = sum(case["fp"] for case in case_scores)
    fn = sum(case["fn"] for case in case_scores)
    findings = sum(case["finding_count"] for case in case_scores)
    evidence_grounded = sum(
        case["evidence_grounded_findings"] for case in case_scores
    )

    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "decision_accuracy": safe_divide(
            sum(case["decision_correct"] for case in case_scores), len(case_scores)
        ),
        "evidence_grounded_finding_rate": safe_divide(evidence_grounded, findings),
    }


def evaluate(results_dir: Path) -> dict[str, Any]:
    ground_truth = load_ground_truth()
    reviews = load_reviews(results_dir)

    missing = sorted(set(ground_truth) - set(reviews))
    unexpected = sorted(set(reviews) - set(ground_truth))
    if missing:
        raise ValueError(f"missing review files for: {', '.join(missing)}")
    if unexpected:
        raise ValueError(f"unexpected review files for: {', '.join(unexpected)}")

    case_scores = [
        score_case(ground_truth[case_id], reviews[case_id])
        for case_id in sorted(ground_truth)
    ]

    return {
        "cases": case_scores,
        "aggregate": aggregate(case_scores),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score production-readiness review outputs against hidden ground truth."
    )
    parser.add_argument(
        "results_dir",
        type=Path,
        help="Directory containing one JSON review per evaluation case.",
    )
    args = parser.parse_args()

    report = evaluate(args.results_dir)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
