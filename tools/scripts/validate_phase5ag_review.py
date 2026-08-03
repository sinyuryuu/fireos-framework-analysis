#!/usr/bin/env python3
"""Validate the host-only Phase 5AG source-review matrix.

This script never connects to ADB, fetches URLs, executes APK/native code, or
changes device state. It checks that the committed review matrix remains
internally consistent and that every source has an explicit non-download
hash marker when no local copy exists.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


MATRIX_COLUMNS = {
    "cve",
    "layer",
    "mt8183_listed",
    "android_or_software_scope",
    "entry_requirement",
    "impact",
    "exact_ps7330_fit",
    "source",
    "action",
    "status",
}
MANIFEST_COLUMNS = {
    "source_id",
    "source_type",
    "reference",
    "fixed_revision_or_date",
    "downloaded",
    "sha256",
    "review_scope",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        return fields, list(reader)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY_RUN: would validate CSV structure and exact-target dispositions")
        print(f"matrix={args.matrix}")
        print(f"source_manifest={args.source_manifest}")
        return 0

    errors: list[str] = []
    matrix_fields, matrix_rows = read_csv(args.matrix)
    manifest_fields, manifest_rows = read_csv(args.source_manifest)
    errors.extend(f"matrix missing column: {name}" for name in sorted(MATRIX_COLUMNS - set(matrix_fields)))
    errors.extend(f"manifest missing column: {name}" for name in sorted(MANIFEST_COLUMNS - set(manifest_fields)))

    ids = [row.get("cve", "") for row in matrix_rows]
    if len(ids) != len(set(ids)):
        errors.append("matrix contains duplicate cve identifiers")
    source_ids = [row.get("source_id", "") for row in manifest_rows]
    if len(source_ids) != len(set(source_ids)):
        errors.append("source manifest contains duplicate source_id values")

    required_rows = {"CVE-2026-3499", "CVE-2026-43499", "CVE-2026-43503", "CVE-2025-20694"}
    missing = required_rows - set(ids)
    errors.extend(f"matrix missing required row: {name}" for name in sorted(missing))

    for row in manifest_rows:
        if row.get("downloaded") == "no" and row.get("sha256") != "NOT_DOWNLOADED":
            errors.append(f"source {row.get('source_id')} lacks NOT_DOWNLOADED hash marker")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"validated matrix rows: {len(matrix_rows)}")
    print(f"validated source rows: {len(manifest_rows)}")
    print("network/device/exploit actions: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
