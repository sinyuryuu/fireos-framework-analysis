#!/usr/bin/env python3
"""Validate Phase 5AI artifact-search records without network or device access."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


MATRIX_COLUMNS = {
    "artifact_or_source",
    "exact_ps7330",
    "local_or_public_state",
    "version",
    "usable_for_live_low_level_test",
    "classification",
}
MANIFEST_COLUMNS = {
    "source_id",
    "source_type",
    "reference",
    "reviewed_or_revision",
    "downloaded",
    "sha256",
    "scope",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY_RUN: validate Phase 5AI artifact matrix and source manifest")
        return 0

    errors: list[str] = []
    fields, rows = read_csv(args.matrix)
    source_fields, sources = read_csv(args.source_manifest)
    errors.extend(f"matrix missing column: {x}" for x in sorted(MATRIX_COLUMNS - set(fields)))
    errors.extend(f"manifest missing column: {x}" for x in sorted(MANIFEST_COLUMNS - set(source_fields)))
    names = [row.get("artifact_or_source", "") for row in rows]
    if len(names) != len(set(names)):
        errors.append("matrix contains duplicate artifact_or_source values")
    source_ids = [row.get("source_id", "") for row in sources]
    if len(source_ids) != len(set(source_ids)):
        errors.append("source manifest contains duplicate source IDs")
    for source in sources:
        if source.get("downloaded") == "no" and source.get("sha256") == "":
            errors.append(f"source {source.get('source_id')} lacks explicit hash disposition")
    required = {"installed runtime capture", "full OTA", "PS7331 preloader.img"}
    errors.extend(f"matrix missing required row: {x}" for x in sorted(required - set(names)))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"validated artifacts: {len(rows)}")
    print(f"validated sources: {len(sources)}")
    print("network/device/write actions: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
