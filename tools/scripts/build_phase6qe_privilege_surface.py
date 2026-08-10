#!/usr/bin/env python3
"""Normalize Phase 6QE worker inventories without contacting a device."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path


COMMON = [
    "domain",
    "row_id",
    "subject",
    "method_or_test",
    "publication_or_source",
    "caller_or_image_node",
    "gate_or_policy",
    "identity_or_reachability",
    "user_scope_or_impact",
    "sink_or_result",
    "low_privilege_status",
    "classification",
    "evidence",
    "source_or_hash",
    "next_safe_step",
    "notes",
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def ipc_rows(path: Path) -> list[dict[str, str]]:
    rows = []
    for row in read_rows(path):
        rows.append({
            "domain": "amazon-ipc",
            "row_id": row["row_id"],
            "subject": row["service"],
            "method_or_test": row["method"],
            "publication_or_source": row["publication"],
            "caller_or_image_node": row["caller"],
            "gate_or_policy": row["gate"],
            "identity_or_reachability": row["identity"],
            "user_scope_or_impact": row["user_scope"],
            "sink_or_result": row["sink"],
            "low_privilege_status": row["low_priv_status"],
            "classification": row["classification"],
            "evidence": row["evidence"],
            "source_or_hash": "",
            "next_safe_step": row["next_safe_step"],
            "notes": "UNKNOWN is retained as an evidence gap, not a vulnerability",
        })
    return rows


def driver_rows(path: Path) -> list[dict[str, str]]:
    rows = []
    for row in read_rows(path):
        rows.append({
            "domain": "gpl-driver-policy",
            "row_id": row["surface"],
            "subject": row["source_capability"],
            "method_or_test": "",
            "publication_or_source": row["exact_image_node_or_path"],
            "caller_or_image_node": row["exact_image_node_or_path"],
            "gate_or_policy": row["exact_image_policy_evidence"],
            "identity_or_reachability": row["reachability_classification"],
            "user_scope_or_impact": row["impact_boundary"],
            "sink_or_result": row["source_capability"],
            "low_privilege_status": row["reachability_classification"],
            "classification": row["reachability_classification"],
            "evidence": row["notes"],
            "source_or_hash": ";".join(filter(None, [row.get("source_sha256", ""), row.get("policy_or_init_sha256", "")])),
            "next_safe_step": "Host-only source→init→SELinux→client mapping; do not open nodes or send ioctl",
            "notes": row["shipped_client_mapping"],
        })
    return rows


def test_rows(path: Path) -> list[dict[str, str]]:
    rows = []
    for row in read_rows(path):
        rows.append({
            "domain": "existing-tests",
            "row_id": row["id"],
            "subject": row["scope"],
            "method_or_test": row["test_or_surface"],
            "publication_or_source": row["raw_evidence"],
            "caller_or_image_node": "",
            "gate_or_policy": row["status"],
            "identity_or_reachability": row["status"],
            "user_scope_or_impact": "",
            "sink_or_result": row["observed_result"],
            "low_privilege_status": row["status"],
            "classification": row["status"],
            "evidence": row["hash_anchor"],
            "source_or_hash": "",
            "next_safe_step": row["minimal_non_state_changing_next_step"],
            "notes": "Existing evidence; excluded retests remain excluded",
        })
    return rows


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ipc", type=Path, required=True)
    p.add_argument("--drivers", type=Path, required=True)
    p.add_argument("--tests", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    inputs = [args.ipc, args.drivers, args.tests]
    rows = ipc_rows(args.ipc) + driver_rows(args.drivers) + test_rows(args.tests)
    for row in rows:
        missing = [key for key in COMMON if key not in row]
        if missing:
            raise SystemExit(f"missing normalized fields: {missing}")

    manifest = {
        "schema": "phase6qe-privilege-surface-v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "device_contacted_by_script": False,
        "device_nodes_opened_by_script": False,
        "binder_or_settings_operation_by_script": False,
        "mutation_by_script": False,
        "root_or_exploit_by_script": False,
        "inputs": {str(path): digest(path) for path in inputs},
        "input_row_counts": {str(path): len(read_rows(path)) for path in inputs},
        "row_count": len(rows),
        "output": str(args.output),
    }
    if args.dry_run:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COMMON, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    manifest["output_sha256"] = digest(args.output)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
