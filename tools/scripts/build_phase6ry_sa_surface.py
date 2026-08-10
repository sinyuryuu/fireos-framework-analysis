#!/usr/bin/env python3
"""Normalize Phase 6RY/6RZ/6SA host-only ledgers.

The generator is offline and deterministic.  It never contacts a device or
invokes Binder, settings, package, OTA, driver, or exploit functionality.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


HEADER = [
    "phase",
    "row_id",
    "provenance_or_domain",
    "surface_or_subject",
    "source_or_location",
    "user_entry_or_entry",
    "gate_or_access",
    "client_or_caller",
    "sink_or_impact",
    "status",
    "next_safe_host_only_step",
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
        parsed = list(csv.DictReader(stream))
    if not parsed:
        raise ValueError(f"empty CSV: {path}")
    return parsed


def normalize(path: Path, phase: str) -> list[dict[str, str]]:
    source = rows(path)
    output: list[dict[str, str]] = []
    for row in source:
        if phase == "6RY":
            output.append(
                {
                    "phase": phase,
                    "row_id": row["row_id"],
                    "provenance_or_domain": "permission/IPC",
                    "surface_or_subject": row["permission_or_surface"],
                    "source_or_location": row["exact_evidence"],
                    "user_entry_or_entry": row["binder_entry"],
                    "gate_or_access": row["declaration"] + "; " + row["identity_user"],
                    "client_or_caller": row["production_caller"],
                    "sink_or_impact": row["sensitive_sink"],
                    "status": row["status"],
                    "next_safe_host_only_step": row["next_safe_host_only_step"],
                    "source_sha256": "",
                }
            )
        elif phase == "6RZ":
            output.append(
                {
                    "phase": phase,
                    "row_id": row["row_id"],
                    "provenance_or_domain": row["provenance_class"],
                    "surface_or_subject": row["surface"],
                    "source_or_location": row["source_exact_path_line"],
                    "user_entry_or_entry": row["user_entry"] + "; " + row["ioctl_read_write_open_path"],
                    "gate_or_access": row["permission_selinux"],
                    "client_or_caller": row["userspace_client_evidence"],
                    "sink_or_impact": row["state_or_privilege_impact"],
                    "status": row["status"],
                    "next_safe_host_only_step": "Complete exact shipped ueventd/file_contexts/TE/client mapping offline; do not open the node.",
                    "source_sha256": row["source_sha256"],
                }
            )
        elif phase == "6SA":
            output.append(
                {
                    "phase": phase,
                    "row_id": row["id"],
                    "provenance_or_domain": row["artifact_class"],
                    "surface_or_subject": row["artifact_or_scope"],
                    "source_or_location": row["source_or_location"],
                    "user_entry_or_entry": row["observed_boundary"],
                    "gate_or_access": row["privilege_or_gate"],
                    "client_or_caller": "No caller field in source ledger; preserve UNKNOWN",
                    "sink_or_impact": row["sensitivity_or_limit"],
                    "status": row["status"],
                    "next_safe_host_only_step": row["next_safe_step"],
                    "source_sha256": "",
                }
            )
        else:
            raise ValueError(phase)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ry", type=Path, required=True)
    parser.add_argument("--rz", type=Path, required=True)
    parser.add_argument("--sa", type=Path, required=True)
    parser.add_argument("--device-snapshot", type=Path, default=None)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [("6RY", args.ry), ("6RZ", args.rz), ("6SA", args.sa)]
    normalized: list[dict[str, str]] = []
    input_meta: dict[str, object] = {}
    for phase, path in inputs:
        parsed = rows(path)
        input_meta[str(path)] = {"sha256": sha256(path), "rows": len(parsed)}
        normalized.extend(normalize(path, phase))

    if args.device_snapshot is not None:
        snap = args.device_snapshot
        selected = {}
        for name in ("metadata.json", "home_resolve.stdout.txt", "sha256sums.txt"):
            candidate = snap / name
            if candidate.exists():
                selected[name] = sha256(candidate)
        input_meta[str(snap)] = {"selected_file_sha256": selected, "device_contact": False}

    manifest = {
        "schema": "phase6ry-sa-control-surface-v1",
        "device_contacted_by_script": False,
        "binder_or_settings_operation_by_script": False,
        "mutation_by_script": False,
        "root_or_exploit_by_script": False,
        "inputs": input_meta,
        "row_counts": {phase: sum(row["phase"] == phase for row in normalized) for phase, _ in inputs},
        "row_count": len(normalized),
        "output": str(args.output),
    }

    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=HEADER, lineterminator="\n")
            writer.writeheader()
            writer.writerows(normalized)
        manifest["output_sha256"] = sha256(args.output)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
