#!/usr/bin/env python3
"""Normalize Phase 6QD IPC, GPL-driver, and residual-sink inventories.

The generator is host-only.  It never contacts ADB, opens a device node,
dispatches Binder, sends a broadcast, changes settings/package state, executes
OTA/recovery, reboots, writes a partition, or runs a root/exploit operation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


FIELDS = [
    "domain", "row_id", "surface", "source", "caller_or_scope",
    "gate_or_permission", "identity_or_user_scope", "sink_or_effect",
    "low_privilege_status", "classification", "confidence_or_impact",
    "next_safe_step", "evidence", "source_sha256",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def refuse(path: Path) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing output: {path}")


def norm_ipc(path: Path) -> list[dict[str, str]]:
    result = []
    for row in read_csv(path):
        result.append({
            "domain": "amazon-ipc-unclosed",
            "row_id": row["id"],
            "surface": row["exact_file_class_method_offset"],
            "source": row["exact_file_class_method_offset"],
            "caller_or_scope": row["caller"],
            "gate_or_permission": row["permission_or_calling_uid"],
            "identity_or_user_scope": row["identity"],
            "sink_or_effect": row["sink"],
            "low_privilege_status": row["status"],
            "classification": row["status"],
            "confidence_or_impact": "bounded static; UNKNOWN preserved",
            "next_safe_step": row["next_safe_step"],
            "evidence": row["evidence_hash"],
            "source_sha256": sha256(path),
        })
    return result


def norm_driver(path: Path) -> list[dict[str, str]]:
    result = []
    for row in read_csv(path):
        result.append({
            "domain": "gpl-driver-surface",
            "row_id": row["row_id"],
            "surface": row["surface"],
            "source": row["source_exact_path_line"],
            "caller_or_scope": row["caller_evidence"],
            "gate_or_permission": row["permission_capability"],
            "identity_or_user_scope": row["low_priv_caller_status"],
            "sink_or_effect": row["sink_or_state_impact"],
            "low_privilege_status": row["low_priv_caller_status"],
            "classification": row["classification"],
            "confidence_or_impact": row["confidence"],
            "next_safe_step": row["next_safe_step"],
            "evidence": row["source_sha256"],
            "source_sha256": sha256(path),
        })
    return result


def norm_residual(path: Path) -> list[dict[str, str]]:
    result = []
    for row in read_csv(path):
        result.append({
            "domain": "residual-high-impact-gap",
            "row_id": row["row_id"],
            "surface": row["sink_class"],
            "source": row["source_file_line"],
            "caller_or_scope": row["caller"],
            "gate_or_permission": row["gate"],
            "identity_or_user_scope": row["identity"],
            "sink_or_effect": row["sink"],
            "low_privilege_status": row["status"],
            "classification": row["status"],
            "confidence_or_impact": row["impact_assessment"],
            "next_safe_step": row["minimum_safe_next_step"],
            "evidence": f"{row['evidence_id']}; {row['evidence_hash']}",
            "source_sha256": sha256(path),
        })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ipc", type=Path, required=True)
    parser.add_argument("--drivers", type=Path, required=True)
    parser.add_argument("--residual", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.ipc, args.drivers, args.residual]
    for path in inputs:
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")

    if args.dry_run:
        print(json.dumps({
            "device_contacted": False,
            "device_nodes_opened": False,
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
    rows = norm_ipc(args.ipc) + norm_driver(args.drivers) + norm_residual(args.residual)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "schema": "phase6qd-privilege-surface-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "device_contacted_by_script": False,
        "device_nodes_opened_by_script": False,
        "binder_or_settings_operation_by_script": False,
        "mutation_by_script": False,
        "ota_or_recovery_executed_by_script": False,
        "root_or_exploit_by_script": False,
        "inputs": {str(path): sha256(path) for path in inputs},
        "input_row_counts": {str(path): len(read_csv(path)) for path in inputs},
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
