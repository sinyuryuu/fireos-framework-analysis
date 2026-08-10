#!/usr/bin/env python3
"""Normalize the Phase 6PZ broad kernel/IPC/workaround evidence.

Host-only.  The script reads three worker CSVs and writes a new combined
matrix and a hash manifest.  It never contacts a device, executes a Binder or
driver operation, runs an OTA/recovery helper, or mutates repository inputs.
Existing output files are never overwritten.
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
    "surface_or_route",
    "source_or_entry",
    "authority_or_permission",
    "caller_or_scope",
    "sink_or_effect",
    "persistence_or_runtime",
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


def normalize_kernel(path: Path) -> list[dict[str, str]]:
    return [
        {
            "domain": "kernel-driver-surface",
            "surface_or_route": row["surface"],
            "source_or_entry": row["source/artifact"],
            "authority_or_permission": row["permission_or_selinux"],
            "caller_or_scope": row["caller_reachability"],
            "sink_or_effect": row["sink"],
            "persistence_or_runtime": row["existing_evidence"],
            "status": row["status"],
            "next_safe_step": row["next_safe_step"],
            "source_csv": str(path),
        }
        for row in read_rows(path)
    ]


def normalize_ipc(path: Path) -> list[dict[str, str]]:
    return [
        {
            "domain": "ipc-ota-oobe-surface",
            "surface_or_route": row["surface"],
            "source_or_entry": row["interface_or_entry"],
            "authority_or_permission": row["permission_or_gate"],
            "caller_or_scope": row["caller"],
            "sink_or_effect": row["sink"],
            "persistence_or_runtime": row["existing_runtime"],
            "status": row["evidence_status"],
            "next_safe_step": row["next_safe_step"],
            "source_csv": str(path),
        }
        for row in read_rows(path)
    ]


def normalize_workaround(path: Path) -> list[dict[str, str]]:
    return [
        {
            "domain": "launcher-workaround",
            "surface_or_route": row["route"],
            "source_or_entry": row["runtime_evidence"],
            "authority_or_permission": row["required_authority"],
            "caller_or_scope": row["changes_user0_home"],
            "sink_or_effect": row["fire_state_effect"],
            "persistence_or_runtime": (
                f"persistence={row['persistence']}; rollback={row['rollback']}"
            ),
            "status": row["status"],
            "next_safe_step": row["next_safe_step"],
            "source_csv": str(path),
        }
        for row in read_rows(path)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", type=Path, required=True)
    parser.add_argument("--ipc-ota", type=Path, required=True)
    parser.add_argument("--workarounds", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.kernel, args.ipc_ota, args.workarounds]
    for path in inputs:
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")

    if args.dry_run:
        print(
            json.dumps(
                {
                    "device_contacted": False,
                    "mutation": False,
                    "binder_or_driver_operation": False,
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
    normalized.extend(normalize_kernel(args.kernel))
    normalized.extend(normalize_ipc(args.ipc_ota))
    normalized.extend(normalize_workaround(args.workarounds))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(normalized)

    manifest = {
        "schema": "phase6pz-broad-surface-closure-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "device_contacted_by_script": False,
        "mutation_by_script": False,
        "binder_or_driver_operation_by_script": False,
        "ota_or_recovery_executed_by_script": False,
        "root_or_exploit_by_script": False,
        "inputs": {str(path): sha256(path) for path in inputs},
        "input_row_counts": {
            str(args.kernel): len(read_rows(args.kernel)),
            str(args.ipc_ota): len(read_rows(args.ipc_ota)),
            str(args.workarounds): len(read_rows(args.workarounds)),
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
