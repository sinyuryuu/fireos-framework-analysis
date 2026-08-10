#!/usr/bin/env python3
"""Normalize Phase 6QA residual IPC/Vending/Settings evidence.

Host-only and write-once: this script reads three worker CSVs and writes a new
combined matrix plus a hash manifest.  It never contacts a device, dispatches
Binder, modifies settings, or executes an OTA/recovery operation.
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
    "authority_or_permission",
    "caller_or_scope",
    "identity_or_runtime",
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


def refuse_overwrite(path: Path) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing output: {path}")


def normalize_vending(path: Path) -> list[dict[str, str]]:
    return [
        {
            "domain": "vending-residual",
            "surface": row["component"],
            "source_or_entry": row["artifact/method"],
            "authority_or_permission": row["exported_or_permission"],
            "caller_or_scope": row["caller_or_trigger"],
            "identity_or_runtime": (
                f"identity={row['identity_boundary']}; "
                f"runtime={row['runtime_evidence']}"
            ),
            "sink_or_effect": row["first_sink"],
            "status": row["status"],
            "next_safe_step": row["next_safe_step"],
            "source_csv": str(path),
        }
        for row in read_rows(path)
    ]


def normalize_amazonpm(path: Path) -> list[dict[str, str]]:
    return [
        {
            "domain": "amazon-package-manager-proxy",
            "surface": row["entry"],
            "source_or_entry": row["interface_and_code"],
            "authority_or_permission": row["permission_or_gate"],
            "caller_or_scope": row["static_caller"],
            "identity_or_runtime": (
                f"identity={row['identity_handling']}; "
                f"runtime={row['runtime_boundary']}"
            ),
            "sink_or_effect": row["receiver_or_sink"],
            "status": row["status"],
            "next_safe_step": row["next_safe_step"],
            "source_csv": str(path),
        }
        for row in read_rows(path)
    ]


def normalize_settings(path: Path) -> list[dict[str, str]]:
    return [
        {
            "domain": "settings-home-resource",
            "surface": row["resource_or_class"],
            "source_or_entry": row["artifact"],
            "authority_or_permission": row["caller_authority"],
            "caller_or_scope": row["reader_or_writer"],
            "identity_or_runtime": row["existing_runtime"],
            "sink_or_effect": (
                f"key={row['namespace_or_key']}; effect={row['home_effect']}"
            ),
            "status": row["status"],
            "next_safe_step": row["next_safe_step"],
            "source_csv": str(path),
        }
        for row in read_rows(path)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vending", type=Path, required=True)
    parser.add_argument("--amazonpm", type=Path, required=True)
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.vending, args.amazonpm, args.settings]
    for path in inputs:
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")

    if args.dry_run:
        print(
            json.dumps(
                {
                    "device_contacted": False,
                    "binder_or_settings_operation": False,
                    "mutation": False,
                    "ota_or_recovery_executed": False,
                    "root_or_exploit": False,
                    "inputs": [str(path) for path in inputs],
                    "output": str(args.output),
                    "manifest": str(args.manifest),
                },
                indent=2,
            )
        )
        return 0

    refuse_overwrite(args.output)
    refuse_overwrite(args.manifest)

    normalized = []
    normalized.extend(normalize_vending(args.vending))
    normalized.extend(normalize_amazonpm(args.amazonpm))
    normalized.extend(normalize_settings(args.settings))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(normalized)

    manifest = {
        "schema": "phase6qa-residual-control-closure-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "device_contacted_by_script": False,
        "binder_or_settings_operation_by_script": False,
        "mutation_by_script": False,
        "ota_or_recovery_executed_by_script": False,
        "root_or_exploit_by_script": False,
        "inputs": {str(path): sha256(path) for path in inputs},
        "input_row_counts": {
            str(args.vending): len(read_rows(args.vending)),
            str(args.amazonpm): len(read_rows(args.amazonpm)),
            str(args.settings): len(read_rows(args.settings)),
        },
        "row_count": len(normalized),
        "output_sha256": sha256(args.output),
        "output": str(args.output),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(normalized)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
