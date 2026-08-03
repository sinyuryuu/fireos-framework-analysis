#!/usr/bin/env python3
"""Validate the host-only Phase 5AJ CVE/Android implementation review.

This validator never connects to a device, downloads code, compiles a payload,
or executes a binary. It checks that the derived matrix and source manifest are
complete and that the review records no live exploit activity.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


MATRIX_REQUIRED = {
    "cve",
    "layer",
    "android_entry_or_implementation",
    "public_scope",
    "exact_device_evidence",
    "exact_match_status",
    "privilege_or_precondition",
    "public_poc_status",
    "live_device_test",
    "classification",
    "evidence_ids",
}
SOURCE_REQUIRED = {
    "source_type",
    "identifier",
    "url_or_path",
    "claim_used",
    "review_date",
    "status",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate(matrix_path: Path, sources_path: Path) -> list[str]:
    errors: list[str] = []
    matrix = read_csv(matrix_path)
    sources = read_tsv(sources_path)

    if not matrix:
        errors.append("matrix has no data rows")
    if not sources:
        errors.append("source manifest has no data rows")

    matrix_fields = set(matrix[0]) if matrix else set()
    source_fields = set(sources[0]) if sources else set()
    errors.extend(f"matrix missing column: {name}" for name in sorted(MATRIX_REQUIRED - matrix_fields))
    errors.extend(f"sources missing column: {name}" for name in sorted(SOURCE_REQUIRED - source_fields))

    if len({row.get("cve", "") for row in matrix}) != len(matrix):
        errors.append("matrix contains duplicate CVE rows")

    for index, row in enumerate(matrix, start=2):
        for field in MATRIX_REQUIRED:
            if not row.get(field, "").strip():
                errors.append(f"matrix row {index} has empty {field}")
        if row.get("live_device_test", "").lower() not in {
            "not applicable",
            "not run",
            "rejected: kernel race/privilege-escalation trigger",
            "rejected: crafted network/kernel trigger",
            "rejected: activate bluetooth and crafted input would cross memory-corruption boundary",
            "rejected: bluetooth over-air/local trigger and memory corruption",
        }:
            errors.append(f"matrix row {index} has unexpected live_device_test value")

    for index, row in enumerate(sources, start=2):
        for field in SOURCE_REQUIRED:
            if not row.get(field, "").strip():
                errors.append(f"source row {index} has empty {field}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true", help="validate only; never write output")
    parser.add_argument("--output", type=Path, help="optional validation report path")
    args = parser.parse_args()

    errors = validate(args.matrix, args.sources)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    message = (
        "PASS: Phase 5AJ matrix and source manifest are structurally valid; "
        "no live exploit action is recorded."
    )
    print(message)
    if args.output and not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(message + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
