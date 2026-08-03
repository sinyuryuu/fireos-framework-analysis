#!/usr/bin/env python3
"""Compare an extracted Amazon rtmutex member with a pinned source snapshot.

Host-only evidence utility.  It accepts either plain source or the numbered
text emitted by extract_phase5_exact_kernel_members.py.  It never compiles,
executes, contacts a device, or overwrites an output file.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from pathlib import Path


NUMBERED = re.compile(r"^\s*([0-9]+)\t(.*)$")


def normalized_lines(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    result: list[str] = []
    for line in lines:
        match = NUMBERED.match(line)
        result.append(match.group(2) if match else line)
    return result


def digest(lines: list[str]) -> str:
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--amazon", required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.amazon.is_file() or not args.reference.is_file():
        parser.error("both inputs must be readable regular files")
    if args.dry_run:
        print("DRY-RUN: no source is executed and no output is written.")
        print(f"DRY-RUN: compare {args.amazon} with {args.reference}")
        print(f"DRY-RUN: write JSON result to {args.output}")
        return 0
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    amazon = normalized_lines(args.amazon)
    reference = normalized_lines(args.reference)
    diff = list(difflib.unified_diff(reference, amazon, fromfile=str(args.reference), tofile=str(args.amazon), n=3))
    result = {
        "amazon_input": str(args.amazon),
        "reference_input": str(args.reference),
        "amazon_normalized_lines": len(amazon),
        "reference_normalized_lines": len(reference),
        "amazon_normalized_sha256": digest(amazon),
        "reference_normalized_sha256": digest(reference),
        "unified_diff_lines": len(diff),
        "identical": amazon == reference,
        "scope": "source comparison only; no device or executable code",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["identical"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
