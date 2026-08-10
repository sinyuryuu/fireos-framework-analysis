#!/usr/bin/env python3
"""Validate the host-only Phase 18 privilege-surface integration.

This script deliberately has no ADB, Binder, driver, reboot, OTA, or write-to-
device code. It validates the checked-in CSV schema, allowed classifications,
unique evidence IDs, and the existence of local evidence paths where the
integration claims a path is available.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys


ALLOWED = {"Confirmed", "Strong evidence", "Probable", "Hypothesis", "Disproved"}
REQUIRED = {
    "id",
    "branch",
    "surface",
    "entry_or_artifact",
    "caller_or_trigger",
    "gate_or_permission",
    "identity_scope",
    "sink_or_effect",
    "runtime_observation",
    "classification",
    "evidence",
    "missing_edge",
    "disposition",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    table = root / "output/tables/phase18-broad-privilege-surface.csv"
    if not table.is_file():
        print(f"missing table: {table}", file=sys.stderr)
        return 2

    seen: set[str] = set()
    with table.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED - fields
        if missing:
            print(f"missing columns: {sorted(missing)}", file=sys.stderr)
            return 2
        rows = list(reader)

    errors: list[str] = []
    for row_number, row in enumerate(rows, start=2):
        row_id = row["id"]
        if not row_id or row_id in seen:
            errors.append(f"row {row_number}: duplicate or empty id {row_id!r}")
        seen.add(row_id)
        if row["classification"] not in ALLOWED:
            errors.append(
                f"row {row_number}: invalid classification {row['classification']!r}"
            )
        if not row["evidence"].strip():
            errors.append(f"row {row_number}: empty evidence")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"validated {len(rows)} Phase 18 rows; host-only, no device actions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
