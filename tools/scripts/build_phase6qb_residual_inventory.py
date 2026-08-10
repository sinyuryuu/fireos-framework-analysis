#!/usr/bin/env python3
"""Normalize the Phase 6QB host-only residual inventories.

The script reads three worker CSVs and writes one immutable comparison matrix
plus a hash manifest.  It never contacts ADB, dispatches Binder, changes
settings/packages, executes OTA/recovery, or runs a root/exploit operation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


FIELDS = [
    "domain",
    "surface",
    "source_or_entry",
    "caller_or_scope",
    "authority_or_permission",
    "identity_or_user_scope",
    "sink_or_effect",
    "status",
    "next_safe_step",
    "source_csv",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def refuse(path: Path) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing output: {path}")


def normalize_amazonpm(path: Path) -> list[dict[str, str]]:
    rows = []
    for row in read_rows(path):
        rows.append({
            "domain": "amazon-package-manager-caller",
            "surface": row["tx"],
            "source_or_entry": row["source_path_line_or_disassembly_offset"],
            "caller_or_scope": row["caller"],
            "authority_or_permission": row["gate"],
            "identity_or_user_scope": row["identity"],
            "sink_or_effect": row["sink"],
            "status": row["status"],
            "next_safe_step": row["next_safe_step"],
            "source_csv": str(path),
        })
    return rows


def normalize_vending(path: Path) -> list[dict[str, str]]:
    rows = []
    for row in read_rows(path):
        rows.append({
            "domain": "vending-downstream",
            "surface": row["surface"],
            "source_or_entry": row["method/line/offset"],
            "caller_or_scope": row["caller"],
            "authority_or_permission": row["gate"],
            "identity_or_user_scope": row["identity"],
            "sink_or_effect": row["sink"],
            "status": row["status"],
            "next_safe_step": row["next_safe_step"],
            "source_csv": str(path),
        })
    return rows


def normalize_writer(path: Path) -> list[dict[str, str]]:
    rows = []
    for row in read_rows(path):
        rows.append({
            "domain": "ps7331-residual-writer",
            "surface": row["layer"] + ": " + row["id"],
            "source_or_entry": row["exact_path_method_offset"],
            "caller_or_scope": row["caller"],
            "authority_or_permission": row["permission_selinux"],
            "identity_or_user_scope": (
                f"identity={row['identity']}; user_scope={row['user_scope']}"
            ),
            "sink_or_effect": row["sink"],
            "status": row["status"],
            "next_safe_step": row["next_safe_step"],
            "source_csv": str(path),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--amazonpm", type=Path, required=True)
    parser.add_argument("--vending", type=Path, required=True)
    parser.add_argument("--writers", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.amazonpm, args.vending, args.writers]
    for path in inputs:
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")

    if args.dry_run:
        print(json.dumps({
            "device_contacted": False,
            "binder_or_settings_operation": False,
            "mutation": False,
            "ota_or_recovery_executed": False,
            "root_or_exploit": False,
            "inputs": [str(path) for path in inputs],
            "output": str(args.output),
            "manifest": str(args.manifest),
        }, indent=2))
        return 0

    refuse(args.output)
    refuse(args.manifest)

    rows = []
    rows.extend(normalize_amazonpm(args.amazonpm))
    rows.extend(normalize_vending(args.vending))
    rows.extend(normalize_writer(args.writers))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "schema": "phase6qb-residual-inventory-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "device_contacted_by_script": False,
        "binder_or_settings_operation_by_script": False,
        "mutation_by_script": False,
        "ota_or_recovery_executed_by_script": False,
        "root_or_exploit_by_script": False,
        "inputs": {str(path): sha256(path) for path in inputs},
        "input_row_counts": {str(path): len(read_rows(path)) for path in inputs},
        "row_count": len(rows),
        "output_sha256": sha256(args.output),
        "output": str(args.output),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
