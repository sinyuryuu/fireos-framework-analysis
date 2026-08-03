#!/usr/bin/env python3
"""Index launcher-package references with nearby source context.

The output is intentionally a context index, not a claim that every match is
a launch.  Reviewers can distinguish a package literal, an observation of the
current activity, and a call that appears near an activity-start API.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


TEXT_SUFFIXES = {".java", ".kt", ".smali", ".xml", ".txt", ".json", ".properties", ".md", ".log"}
LAUNCH_RE = re.compile(r"(?:startActivity|startActivityAsUser|startActivityForResult|startService|startServiceAsUser|setClass|setComponent|ComponentName)", re.I)
OBSERVATION_RE = re.compile(r"(?:getRunningTasks|currentRunningActivityName|topActivity|topRunning|isHomeTask|mResumedActivity)", re.I)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", required=True, type=Path, help="text tree to scan; repeatable")
    parser.add_argument("--package", default="com.amazon.firelauncher")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--context", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def classify(line: str, context: str) -> str:
    combined = f"{line}\n{context}"
    if LAUNCH_RE.search(combined) and re.search(r"firelauncher|Launcher", combined, re.I):
        return "launch-api-context"
    if OBSERVATION_RE.search(combined):
        return "conditional-observation"
    if "firelauncher" in combined.lower():
        return "package-literal"
    return "other"


def candidate_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def main() -> int:
    config = parse_args()
    roots = [root.resolve() for root in config.root]
    missing = [str(root) for root in roots if not root.is_dir()]
    if missing:
        print("missing scan roots: " + ", ".join(missing), file=sys.stderr)
        return 2
    output = config.output.resolve()
    if output.exists():
        print(f"refusing to overwrite existing output: {output}", file=sys.stderr)
        return 2
    if config.context < 0:
        print("--context must be non-negative", file=sys.stderr)
        return 2
    if config.dry_run:
        print("DRY-RUN: no source tree will be scanned and no output will be written.")
        print(f"DRY-RUN: package={config.package} context={config.context} output={output}")
        for root in roots:
            print(f"DRY-RUN: scan {root}")
        return 0

    needle = config.package.lower()
    output.parent.mkdir(parents=True, exist_ok=True)
    records: list[tuple[str, int, str, str]] = []
    scanned = 0
    for root in roots:
        for path in candidate_files(root):
            scanned += 1
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError as exc:
                print(f"warning: cannot read {path}: {exc}", file=sys.stderr)
                continue
            for index, line in enumerate(lines):
                if needle not in line.lower():
                    continue
                low = max(0, index - config.context)
                high = min(len(lines), index + config.context + 1)
                context = "\n".join(lines[low:high])
                classification = classify(line, context)
                text = line.strip().replace("\t", " ")
                records.append((classification, str(path), index + 1, text))

    with output.open("w", encoding="utf-8") as handle:
        handle.write("classification\tfile\tline\ttext\n")
        for classification, path, line_number, text in sorted(records):
            handle.write(f"{classification}\t{path}\t{line_number}\t{text}\n")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"scanned_files={scanned} matches={len(records)}")
    print(f"generated {output}")
    print(f"sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
