#!/usr/bin/env python3
"""Extract HOME resolver candidates from saved command output.

This is a parser only. It does not choose a launcher or infer Amazon logic.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PRIORITY_RE = re.compile(r"^\s*priority=(-?\d+)")
NAME_RE = re.compile(r"^\s*name=([A-Za-z0-9_.$]+)")
PACKAGE_RE = re.compile(r"^\s*packageName=([A-Za-z0-9_.$]+)")
COMPONENT_RE = re.compile(r"^([A-Za-z0-9_.$]+)/([A-Za-z0-9_.$]+)$")


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path.resolve())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def parse_file(path: Path) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    source = display_path(path)
    pending_priority: str | None = None
    pending_name: str | None = None
    pending_package: str | None = None

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.rstrip()
        priority = PRIORITY_RE.search(line)
        if priority:
            pending_priority = priority.group(1)
            pending_name = None
            pending_package = None
            component = line.split()[0] if line.split() else ""
            match = COMPONENT_RE.match(component)
            if match:
                rows.append((source, match.group(0), pending_priority, "resolver"))
                pending_priority = None
        name = NAME_RE.search(line)
        if name:
            pending_name = name.group(1)
        package = PACKAGE_RE.search(line)
        if package:
            pending_package = package.group(1)
        if pending_priority and pending_name and pending_package:
            activity = pending_name
            if activity.startswith(pending_package + "."):
                activity = activity[len(pending_package) + 1 :]
            rows.append((source, f"{pending_package}/{activity}", pending_priority, "query"))
            pending_priority = None
            pending_name = None
            pending_package = None

        match = COMPONENT_RE.match(line.strip())
        if match and "priority=" not in line:
            if pending_priority is not None:
                rows.append((source, match.group(0), pending_priority, "resolver"))
                pending_priority = None
            else:
                rows.append((source, match.group(0), "", "component"))

    return rows


def main() -> int:
    args = parse_args()
    inputs = [path.resolve() for path in args.input]
    missing = [path for path in inputs if not path.is_file()]
    if missing:
        for path in missing:
            print(f"input is not a file: {path}", file=sys.stderr)
        return 2
    if args.output.exists():
        print(f"refusing to overwrite existing output: {args.output}", file=sys.stderr)
        return 2
    if args.dry_run:
        print("DRY-RUN: no input will be parsed and no output will be written.")
        print(f"DRY-RUN: inputs={len(inputs)} output={args.output}")
        return 0

    rows: list[tuple[str, str, str, str]] = []
    for path in inputs:
        rows.extend(parse_file(path))
    rows.sort(key=lambda row: row)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        handle.write("source\tcomponent\tpriority\tparser\n")
        seen: set[tuple[str, str, str, str]] = set()
        for row in rows:
            if row in seen:
                continue
            seen.add(row)
            handle.write("\t".join(row) + "\n")
    print(f"generated {args.output} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
