#!/usr/bin/env python3
"""Validate Phase 5AH public-route evidence without network or device access."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROUTE_COLUMNS = {
    "route",
    "platform",
    "exact_target",
    "required_privilege_or_precondition",
    "observed_or_public_result",
    "status",
    "safe_next_action",
}
MANIFEST_COLUMNS = {
    "source_id",
    "source_type",
    "reference",
    "revision_or_query",
    "downloaded",
    "sha256",
    "scope",
}


def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
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
        print("DRY_RUN: validate Phase 5AH CSV structure and no-download markers")
        print(f"matrix={args.matrix}")
        print(f"source_manifest={args.source_manifest}")
        return 0

    errors: list[str] = []
    route_fields, routes = read(args.matrix)
    manifest_fields, sources = read(args.source_manifest)
    errors.extend(f"route matrix missing column: {x}" for x in sorted(ROUTE_COLUMNS - set(route_fields)))
    errors.extend(f"source manifest missing column: {x}" for x in sorted(MANIFEST_COLUMNS - set(manifest_fields)))

    route_names = [row.get("route", "") for row in routes]
    if len(route_names) != len(set(route_names)):
        errors.append("route matrix contains duplicate route names")
    source_ids = [row.get("source_id", "") for row in sources]
    if len(source_ids) != len(set(source_ids)):
        errors.append("source manifest contains duplicate source IDs")

    required = {"HackMD CVE-2025-21479", "mtk-easy-su pinned", "generic mtkclient BROM/DA"}
    errors.extend(f"route matrix missing required route: {x}" for x in sorted(required - set(route_names)))

    for source in sources:
        if source.get("downloaded") == "no" and source.get("sha256") != "NOT_DOWNLOADED":
            errors.append(f"source {source.get('source_id')} lacks NOT_DOWNLOADED marker")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"validated routes: {len(routes)}")
    print(f"validated sources: {len(sources)}")
    print("network/device/exploit actions: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
