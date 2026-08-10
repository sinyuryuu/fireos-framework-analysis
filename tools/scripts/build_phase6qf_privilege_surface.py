#!/usr/bin/env python3
"""Build the Phase 6QF host-only privilege-surface matrix.

This script reads only already-captured worker CSV files.  It never contacts a
device and never invokes adb, Binder, settings, package, driver, OTA, or root
operations.  The output schema deliberately retains UNKNOWN values instead of
turning incomplete provenance into a vulnerability claim.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


FIELDS = [
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def ipc_rows(path: Path) -> list[dict[str, str]]:
    result = []
    for row in read_csv(path):
        result.append({
            "domain": "amazon-ipc-provenance",
            "row_id": row["row_id"],
            "subject": row["scope"],
            "method_or_test": row["registration_and_contract"],
            "publication_or_source": row["registration_and_contract"],
            "caller_or_image_node": row["actual_caller_or_sender"],
            "gate_or_policy": row["gate_and_identity"],
            "identity_or_reachability": row["gate_and_identity"],
            "user_scope_or_impact": row["user_propagation"],
            "sink_or_result": row["first_consumer_or_sink"],
            "low_privilege_status": row["status"],
            "classification": row["status"],
            "evidence": row["static_evidence"],
            "source_or_hash": "",
            "next_safe_step": row["next_safe_step"],
            "notes": "UNKNOWN is an evidence gap, not a vulnerability claim",
        })
    return result


def policy_rows(path: Path) -> list[dict[str, str]]:
    result = []
    for row in read_csv(path):
        result.append({
            "domain": "exact-image-policy-client",
            "row_id": row["surface"],
            "subject": row["surface"],
            "method_or_test": row["source_ref"],
            "publication_or_source": row["init_ref"],
            "caller_or_image_node": "; ".join(
                value for value in (row["node"], row["mode_owner"]) if value
            ),
            "gate_or_policy": "; ".join(
                value for value in (row["label"], row["selinux_ref"]) if value
            ),
            "identity_or_reachability": row["reachability"],
            "user_scope_or_impact": row["mode_owner"],
            "sink_or_result": row["sink"],
            "low_privilege_status": row["reachability"],
            "classification": row["confidence"],
            "evidence": "; ".join(
                value for value in (row["source_ref"], row["selinux_ref"]) if value
            ),
            "source_or_hash": "",
            "next_safe_step": row["next_safe_step"],
            "notes": "Source capability is not promoted to shipped reachability",
        })
    return result


def runtime_rows(path: Path) -> list[dict[str, str]]:
    result = []
    for row in read_csv(path):
        result.append({
            "domain": "existing-runtime-evidence",
            "row_id": row["item_id"],
            "subject": row["scope"],
            "method_or_test": row["test_preconditions"],
            "publication_or_source": row["raw_evidence_and_sha256"],
            "caller_or_image_node": "UNKNOWN",
            "gate_or_policy": row["existing_runtime_evidence"],
            "identity_or_reachability": row["existing_runtime_evidence"],
            "user_scope_or_impact": row["test_preconditions"],
            "sink_or_result": row["existing_runtime_evidence"],
            "low_privilege_status": "EXISTING_EVIDENCE_ONLY",
            "classification": "BOUNDED_EXISTING_EVIDENCE",
            "evidence": row["raw_evidence_and_sha256"],
            "source_or_hash": "",
            "next_safe_step": row["minimal_no_mutation_repro"],
            "notes": row["remaining_runtime_evidence"] + "; stop: " + row["stop_condition"],
        })
    return result


def validate(rows: list[dict[str, str]]) -> None:
    for index, row in enumerate(rows, start=1):
        missing = [field for field in FIELDS if field not in row]
        if missing:
            raise SystemExit(f"row {index} missing fields: {missing}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ipc", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.ipc, args.policy, args.runtime]
    rows = ipc_rows(args.ipc) + policy_rows(args.policy) + runtime_rows(args.runtime)
    validate(rows)

    manifest = {
        "schema": "phase6qf-privilege-surface-v1",
        "device_contacted_by_script": False,
        "device_nodes_opened_by_script": False,
        "binder_or_settings_operation_by_script": False,
        "mutation_by_script": False,
        "root_or_exploit_by_script": False,
        "inputs": {str(path): sha256(path) for path in inputs},
        "input_row_counts": {str(path): len(read_csv(path)) for path in inputs},
        "row_count": len(rows),
        "output": str(args.output),
    }
    if args.dry_run:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    manifest["output_sha256"] = sha256(args.output)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
