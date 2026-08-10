#!/usr/bin/env python3
"""Normalize the Phase 6QC host-only privilege-surface audits.

This script reads the three bounded worker CSVs and writes a single comparison
matrix plus a hash manifest.  It never contacts ADB, obtains or transacts on a
Binder service, sends an intent/broadcast, changes settings or package state,
executes OTA/recovery, or runs a root/exploit operation.
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
    "location",
    "caller_or_scope",
    "gate_or_permission",
    "identity_and_user_scope",
    "sink_or_effect",
    "runtime_evidence",
    "status",
    "next_safe_step",
    "evidence_hash",
    "source_csv",
    "source_sha256",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def refuse(path: Path) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing output: {path}")


def common(source: Path, domain: str, row: dict[str, str], *, surface: str,
           location: str, caller: str, gate: str, identity: str, sink: str,
           runtime: str, status: str, next_step: str) -> dict[str, str]:
    return {
        "domain": domain,
        "surface": surface,
        "location": location,
        "caller_or_scope": caller,
        "gate_or_permission": gate,
        "identity_and_user_scope": identity,
        "sink_or_effect": sink,
        "runtime_evidence": runtime,
        "status": status,
        "next_safe_step": next_step,
        "evidence_hash": row.get("hash", ""),
        "source_csv": str(source),
        "source_sha256": sha256(source),
    }


def normalize_prewarm(path: Path) -> list[dict[str, str]]:
    result = []
    for row in rows(path):
        result.append(common(
            path,
            "prewarm-identity",
            row,
            surface=row["method/offset"].split(";", 1)[0],
            location=row["method/offset"],
            caller=row["caller"],
            gate=row["gate"],
            identity=row["identity"],
            sink=row["sink"],
            runtime="NOT_NEW_THIS_PHASE",
            status=row["status"],
            next_step=row["next_safe_step"],
        ))
    return result


def normalize_asp(path: Path) -> list[dict[str, str]]:
    result = []
    for row in rows(path):
        result.append(common(
            path,
            "asp-audio",
            row,
            surface=f"{row['service']}::{row['method']}",
            location=f"{row['exact_path']}:{row['offset']}",
            caller=row["caller"],
            gate=row["permission"],
            identity=row["identity"],
            sink=row["sink"],
            runtime=row["runtime_evidence"],
            status=row["status"],
            next_step=row["next_safe_step"],
        ))
    return result


def normalize_ota(path: Path) -> list[dict[str, str]]:
    result = []
    for row in rows(path):
        result.append(common(
            path,
            "ota-canonicalization",
            row,
            surface=row["id"],
            location=row["exact_va_or_source_path"],
            caller=row["caller"],
            gate=row["gate"],
            identity=row["identity"],
            sink=row["sink"],
            runtime="NOT_EXECUTED; host-only artifact closure",
            status=row["status"],
            next_step=row["next_safe_step"],
        ))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prewarm", type=Path, required=True)
    parser.add_argument("--asp", type=Path, required=True)
    parser.add_argument("--ota", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.prewarm, args.asp, args.ota]
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
    normalized = normalize_prewarm(args.prewarm) + normalize_asp(args.asp) + normalize_ota(args.ota)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(normalized)

    manifest = {
        "schema": "phase6qc-privilege-closure-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "device_contacted_by_script": False,
        "binder_or_settings_operation_by_script": False,
        "mutation_by_script": False,
        "ota_or_recovery_executed_by_script": False,
        "root_or_exploit_by_script": False,
        "inputs": {str(path): sha256(path) for path in inputs},
        "input_row_counts": {str(path): len(rows(path)) for path in inputs},
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
