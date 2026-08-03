#!/usr/bin/env python3
"""Create a machine-readable inventory of project evidence files and hashes."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    config = parse_args()
    root = config.root.resolve()
    if not root.is_dir():
        print(f"root is not a directory: {root}", file=sys.stderr)
        return 2
    if config.output.exists():
        print(f"refusing to overwrite existing output: {config.output}", file=sys.stderr)
        return 2
    if config.dry_run:
        print("DRY-RUN: no evidence file will be hashed and no output will be written.")
        print(f"DRY-RUN: root={root} output={config.output}")
        return 0

    rows: list[tuple[str, int, str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.resolve() == config.output.resolve():
            continue
        relative = path.relative_to(root)
        kind = "raw"
        if path.name == "sha256sums.txt":
            kind = "hash-manifest"
        elif path.name.endswith("summary.md") or path.name in {"phase-1-report.md", "evidence-index.md"}:
            kind = "summary"
        elif path.suffix in {".java", ".smali", ".xml"}:
            kind = "analysis-source"
        rows.append((str(relative), path.stat().st_size, digest(path), kind))
    config.output.parent.mkdir(parents=True, exist_ok=True)
    with config.output.open("w", encoding="utf-8") as handle:
        handle.write("path\tsize\tsha256\tkind\n")
        for row in rows:
            handle.write("\t".join(str(item) for item in row) + "\n")
    print(f"generated {config.output} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
