from __future__ import annotations

import json
from pathlib import Path

import pytest

from iteration_1.runner import (
    ArtifactValidationError,
    finalize_case,
    validate_admission,
    validate_review,
)


def finding(category: str = "retry_policy") -> dict:
    return {
        "category": category,
        "severity": "high",
        "claim": "A material production failure occurs.",
        "evidence": ["runtime reproduction"],
        "verified": True,
        "confidence": 0.99,
    }


def review(case_id: str = "case_06", findings: list[dict] | None = None) -> dict:
    findings = [] if findings is None else findings
    return {
        "case_id": case_id,
        "decision": "not_ready" if findings else "ready",
        "findings": findings,
        "uncertainties": [],
    }


def admission(
    case_id: str,
    adjudications: list[dict],
    final_review: dict,
    merge_groups: list[dict] | None = None,
) -> dict:
    return {
        "case_id": case_id,
        "adjudications": adjudications,
        "merge_groups": merge_groups or [],
        "final_review": final_review,
    }


def adjudication(index: int, outcome: str = "admit", **extra: object) -> dict:
    item = {
        "candidate_index": index,
        "outcome": outcome,
        "reason": (
            "supported_material_finding"
            if outcome == "admit"
            else "hardening_only"
        ),
        "evidence_summary": "Evidence was checked.",
        "scope_assessment": "The behavior is within the component scope.",
        "materiality_assessment": "The impact is material.",
    }
    if outcome == "merge":
        item["reason"] = "duplicate_root_cause"
        item["merge_into"] = extra.pop("merge_into")
    else:
        item["merge_into"] = None
    item.update(extra)
    return item


def test_review_decision_must_match_findings() -> None:
    data = review(findings=[finding()])
    data["decision"] = "ready"

    with pytest.raises(ArtifactValidationError, match="decision must be 'not_ready'"):
        validate_review(data, "case_06")


def test_admission_requires_one_adjudication_per_candidate() -> None:
    candidates = review(findings=[finding(), finding("validation")])
    report = admission(
        "case_06",
        [adjudication(0)],
        review(findings=[finding()]),
    )

    with pytest.raises(ArtifactValidationError, match="cover every candidate index"):
        validate_admission(report, candidates, "case_06")


def test_merge_must_target_admitted_candidate() -> None:
    candidates = review(findings=[finding(), finding()])
    report = admission(
        "case_06",
        [
            adjudication(0, "reject"),
            adjudication(1, "merge", merge_into=0),
        ],
        review(),
        [
            {
                "target_candidate_index": 0,
                "merged_candidate_indices": [1],
                "root_cause": "same retry behavior",
            }
        ],
    )

    with pytest.raises(ArtifactValidationError, match="target is not admitted"):
        validate_admission(report, candidates, "case_06")


def test_valid_merge_and_finalize(tmp_path: Path) -> None:
    candidates = review(findings=[finding(), finding()])
    final = review(findings=[finding()])
    report = admission(
        "case_06",
        [
            adjudication(0, "admit"),
            adjudication(1, "merge", merge_into=0),
        ],
        final,
        [
            {
                "target_candidate_index": 0,
                "merged_candidate_indices": [1],
                "root_cause": "same retry root cause",
            }
        ],
    )

    candidate_path = tmp_path / "candidates.json"
    admission_path = tmp_path / "admission.json"
    final_path = tmp_path / "final.json"
    scored_path = tmp_path / "scored.json"
    candidate_path.write_text(json.dumps(candidates), encoding="utf-8")
    admission_path.write_text(json.dumps(report), encoding="utf-8")

    finalize_case(
        "case_06",
        candidate_path,
        admission_path,
        final_path,
        scored_path,
    )

    assert json.loads(final_path.read_text(encoding="utf-8")) == final
    assert json.loads(scored_path.read_text(encoding="utf-8")) == final
