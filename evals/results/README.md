# Evaluation Results

Store scored reviewer outputs here. Keep raw trajectories separately under `trajectories/`.

Initial layout:

```text
evals/results/
├── baseline/
│   ├── case_01.json
│   ├── case_02.json
│   └── case_03.json
└── README.md
```

Each JSON file must validate against `schemas/review.schema.json`.

To score a complete baseline slice:

```bash
python evals/evaluator.py evals/results/baseline
```

The evaluator requires exactly one result for every case currently present in `evals/ground_truth.yaml`. Missing or unexpected cases fail the run rather than being silently ignored.

For the initial three-case slice, finding matching is deterministic by exact defect category. This is sufficient because each defective case contains one distinct material defect. Before adding cases with multiple defects in the same category, the matching rubric must be expanded and documented before those cases are scored.
