#!/usr/bin/env python3
"""Copy a reviewed Markdown report to a new reproducible output artifact.

The renderer deliberately does not invent findings. It only validates the
source and writes a new copy with an evidence manifest reference.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--evidence-index", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    config = parse_args()
    if not config.input.is_file():
        print(f"input report is not a file: {config.input}", file=sys.stderr)
        return 2
    if config.evidence_index and not config.evidence_index.is_file():
        print(f"evidence index is not a file: {config.evidence_index}", file=sys.stderr)
        return 2
    if config.output.exists():
        print(f"refusing to overwrite existing output: {config.output}", file=sys.stderr)
        return 2
    if config.dry_run:
        print("DRY-RUN: report will not be read or written.")
        print(f"DRY-RUN: input={config.input} output={config.output}")
        return 0

    report = config.input.read_text(encoding="utf-8")
    if "Status:" not in report:
        print("input report must contain a Status line", file=sys.stderr)
        return 2
    evidence_digest = "not-supplied"
    if config.evidence_index:
        evidence_digest = hashlib.sha256(config.evidence_index.read_bytes()).hexdigest()
    rendered = report.rstrip() + "\n\n---\n\nGenerated evidence-index SHA-256: [" + evidence_digest + "]\n"
    config.output.parent.mkdir(parents=True, exist_ok=True)
    config.output.write_text(rendered, encoding="utf-8")
    print(f"generated {config.output}")
    print(f"sha256={hashlib.sha256(config.output.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
