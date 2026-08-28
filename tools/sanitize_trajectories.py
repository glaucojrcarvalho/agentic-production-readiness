from __future__ import annotations

import argparse
from pathlib import Path
import re


WORKDIR_RE = re.compile(r"^workdir:\s*(.+)$", re.MULTILINE)
SESSION_RE = re.compile(r"^session id:.*(?:\n|$)", re.MULTILINE)


def sanitize(text: str) -> str:
    match = WORKDIR_RE.search(text)
    if match:
        workdir = match.group(1).strip()
        if workdir:
            text = text.replace(workdir, "[REPO_ROOT]")

    text = SESSION_RE.sub("", text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove machine-specific metadata from preserved Codex trajectories."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="evals/results/iteration_1_logs",
        help="Directory containing .log trajectory files.",
    )
    args = parser.parse_args()

    directory = Path(args.directory)
    paths = sorted(directory.glob("*.log"))
    if not paths:
        raise SystemExit(f"no .log files found under {directory}")

    changed = 0
    for path in paths:
        original = path.read_text()
        cleaned = sanitize(original)
        if cleaned != original:
            path.write_text(cleaned)
            changed += 1

    print(f"sanitized {changed} of {len(paths)} trajectory logs")


if __name__ == "__main__":
    main()
