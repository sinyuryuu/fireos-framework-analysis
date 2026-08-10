#!/usr/bin/env python3
"""Normalize the host-only Phase 6RV/6RW/6RX ledgers.

This script is deliberately offline.  It reads the three worker CSV ledgers,
records their SHA-256 values, and emits one stable cross-surface table plus a
JSON manifest.  It never contacts a device, Binder service, settings provider,
package manager, or network.
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
    "domain",
    "control_flow",
    "caller_gate_identity_user",
    "sink_or_effect",
    "evidence",
    "evidence_sha256",
    "status_or_classification",
    "disposition",
    "next_safe_host_only_step",
    "risk_rejected_path",
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


def malformed_row_numbers(path: Path) -> list[int]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.reader(stream))
    if not rows:
        return []
    width = len(rows[0])
    return [number for number, row in enumerate(rows[1:], 1) if len(row) != width]


def normalize(path: Path, phase: str) -> list[dict[str, str]]:
    rows = read_rows(path)
    result: list[dict[str, str]] = []
    for row in rows:
        if phase == "6RV":
            result.append(
                {
                    "phase": phase,
                    "row_id": row["row_id"],
                    "domain": row["permission"],
                    "control_flow": row["caller"],
                    "caller_gate_identity_user": row["identity"] + "; " + row["user_scope"],
                    "sink_or_effect": row["sink"],
                    "evidence": row["evidence"],
                    "evidence_sha256": "",
                    "status_or_classification": row["evidence_class"],
                    "disposition": row["reachability"],
                    "next_safe_host_only_step": "Exact holder/caller or consumer provenance; preserve UNKNOWN.",
                    "risk_rejected_path": "No private Binder, mutation, device-node, OTA, Root, or reboot.",
                }
            )
        elif phase == "6RW":
            result.append(
                {
                    "phase": phase,
                    "row_id": row["id"],
                    "domain": row["layer"],
                    "control_flow": row["control_flow"],
                    "caller_gate_identity_user": row["caller_gate_identity_user"],
                    "sink_or_effect": row["sink_or_effect"],
                    "evidence": row["evidence_path_method_offset"],
                    "evidence_sha256": row["evidence_sha256"],
                    "status_or_classification": row["classification"],
                    "disposition": row["disposition"],
                    "next_safe_host_only_step": "Recover missing exact-build/native caller scope only.",
                    "risk_rejected_path": "No Binder, broadcast, settings/package/overlay mutation, OTA, Root, or reboot.",
                }
            )
        elif phase == "6RX":
            # The worker's RX CSV contains unquoted commas in several cells.
            # Keep that raw ledger byte-for-byte and mark shifted fields as
            # UNKNOWN instead of silently assigning them to the wrong column.
            if None in row or any(value is None for value in row.values()):
                result.append(
                    {
                        "phase": phase,
                        "row_id": row["id"],
                        "domain": row["area"],
                        "control_flow": row["writer_or_boundary"],
                        "caller_gate_identity_user": row["low_priv_caller"],
                        "sink_or_effect": row["sensitive_sink"],
                        "evidence": "RAW_CSV_FORMAT_WARNING: unquoted comma; consult the preserved Markdown ledger",
                        "evidence_sha256": "",
                        "status_or_classification": "UNKNOWN_DUE_TO_UNQUOTED_RAW_CSV",
                        "disposition": "UNKNOWN_DUE_TO_UNQUOTED_RAW_CSV",
                        "next_safe_host_only_step": "Use the preserved Markdown ledger; do not infer shifted CSV fields.",
                        "risk_rejected_path": "Preserved raw ledger; no device operation was performed.",
                    }
                )
                continue
            result.append(
                {
                    "phase": phase,
                    "row_id": row["id"],
                    "domain": row["area"],
                    "control_flow": row["writer_or_boundary"],
                    "caller_gate_identity_user": row["low_priv_caller"],
                    "sink_or_effect": row["sensitive_sink"],
                    "evidence": "phase6rx ledger; " + row["writer_or_boundary"],
                    "evidence_sha256": "",
                    "status_or_classification": row["status"],
                    "disposition": row["status"],
                    "next_safe_host_only_step": row["next_safe_host_only_step"],
                    "risk_rejected_path": row["risk_rejected_path"],
                }
            )
        else:
            raise ValueError(f"unknown phase: {phase}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rv", type=Path, required=True)
    parser.add_argument("--rw", type=Path, required=True)
    parser.add_argument("--rx", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [("6RV", args.rv), ("6RW", args.rw), ("6RX", args.rx)]
    rows: list[dict[str, str]] = []
    input_meta = {}
    for phase, path in inputs:
        malformed = malformed_row_numbers(path)
        input_meta[str(path)] = {
            "sha256": sha256(path),
            "rows": len(read_rows(path)),
            "malformed_row_numbers": malformed,
        }
        rows.extend(normalize(path, phase))

    manifest = {
        "schema": "phase6rv-rx-privilege-surface-v1",
        "device_contacted_by_script": False,
        "binder_or_settings_operation_by_script": False,
        "mutation_by_script": False,
        "root_or_exploit_by_script": False,
        "inputs": input_meta,
        "row_counts": {phase: sum(1 for row in rows if row["phase"] == phase) for phase, _ in inputs},
        "row_count": len(rows),
        "output": str(args.output),
    }

    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=HEADER, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        manifest["output_sha256"] = sha256(args.output)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
