#!/usr/bin/env python3
"""Normalize the Phase 20 host-only residual ledgers.

The script is deliberately device-free: it reads only the five worker CSVs and
emits a common caller -> gate -> identity/user scope -> sink ledger.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path


FIELDS = [
    "record_id",
    "record_type",
    "surface",
    "artifact_or_entry",
    "caller",
    "gate",
    "identity_or_user_scope",
    "sink",
    "runtime_or_result",
    "missing_edge",
    "classification",
    "confidence",
    "evidence",
    "next_safe_step",
]

SOURCES = {
    "ipc": "work/luna_worker_phase20_ipc_closure_20260810.csv",
    "ota": "work/luna_worker_phase20_ota_closure_20260810.csv",
    "driver": "work/luna_worker_phase20_driver_closure_20260810.csv",
    "reconciliation": "work/luna_worker_phase20_reconciliation_20260810.csv",
    "provenance": "work/luna_worker_phase20_provenance_20260810.csv",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        result = list(csv.DictReader(stream))
    if not result:
        raise ValueError(f"empty CSV: {path}")
    return result


def confidence(classification: str) -> str:
    value = classification.upper()
    if "BOUNDED_NEGATIVE" in value or "NEGATIVE_BOUNDARY" in value:
        return "Disproved"
    if "UNKNOWN" in value or "UNRESOLVED" in value:
        return "Hypothesis"
    if "CONFIRMED" in value or "EXACT_" in value or "CLOSED" in value:
        return "Confirmed"
    if "STATIC" in value or "CAPABILITY" in value or "PARTIAL" in value:
        return "Strong evidence"
    return "Probable"


def normalize(kind: str, row: dict[str, str]) -> dict[str, str]:
    if kind == "ipc":
        classification = row["classification"]
        return {
            "record_id": row["id"],
            "record_type": "ipc",
            "surface": row["service"],
            "artifact_or_entry": f"{row['class']} :: {row['entry']}",
            "caller": row["caller"],
            "gate": row["gate"],
            "identity_or_user_scope": f"{row['identity']} | {row['user_scope']}",
            "sink": row["sink"],
            "runtime_or_result": row["runtime"],
            "missing_edge": row["missing_edge"],
            "classification": classification,
            "confidence": confidence(classification),
            "evidence": row["evidence"],
            "next_safe_step": row["next_safe_step"],
        }
    if kind == "ota":
        classification = row["classification"]
        return {
            "record_id": row["id"],
            "record_type": "ota",
            "surface": row["surface"],
            "artifact_or_entry": row["artifact_or_path"],
            "caller": row["caller"],
            "gate": row["gate"],
            "identity_or_user_scope": "not closed in saved corpus",
            "sink": row["sink"],
            "runtime_or_result": "not replayed; host-only audit",
            "missing_edge": row["missing_edge"],
            "classification": classification,
            "confidence": confidence(classification),
            "evidence": row["evidence"],
            "next_safe_step": "Recover verifier/UID/SELinux provenance offline; do not execute OTA or recovery",
        }
    if kind == "driver":
        classification = row["closure_status"]
        return {
            "record_id": row["row_id"],
            "record_type": "driver",
            "surface": row["surface"],
            "artifact_or_entry": row["source_config_image"],
            "caller": f"{row['shipped_native_opener']} | {row['init_uid_domain']}",
            "gate": f"{row['node_owner_mode_context']} | {row['merged_te_genfs_policy']}",
            "identity_or_user_scope": row["init_uid_domain"],
            "sink": row["driver_sink"],
            "runtime_or_result": row["operation"],
            "missing_edge": row["remaining_gap"],
            "classification": classification,
            "confidence": confidence(classification),
            "evidence": row["evidence"],
            "next_safe_step": "Join selected object/DTB and policy offline; do not open or ioctl a device node",
        }
    if kind == "reconciliation":
        return {
            "record_id": row["reconciliation_id"],
            "record_type": "reconciliation",
            "surface": row["candidate"],
            "artifact_or_entry": row["prior_scope"],
            "caller": "historical tests only",
            "gate": row["existing_commands_or_inputs"],
            "identity_or_user_scope": row["prior_test_ids_or_evidence"],
            "sink": row["value"],
            "runtime_or_result": row["phase20_disposition"],
            "missing_edge": row["missing_evidence"],
            "classification": "RECONCILED_NO_REPEAT",
            "confidence": "Confirmed",
            "evidence": row["prior_test_ids_or_evidence"],
            "next_safe_step": row["explicitly_forbidden_action"],
        }
    if kind == "provenance":
        classification = row["alignment"]
        return {
            "record_id": row["id"],
            "record_type": "provenance",
            "surface": row["item"],
            "artifact_or_entry": row["path_or_provenance"],
            "caller": "host-side provenance",
            "gate": row["source_scope"],
            "identity_or_user_scope": row["version_or_runtime"],
            "sink": "artifact identity only",
            "runtime_or_result": row["result"],
            "missing_edge": "Version/path provenance is not runtime reachability",
            "classification": classification,
            "confidence": confidence(classification),
            "evidence": row["path_or_provenance"],
            "next_safe_step": "Keep PS7331 and saved PS7330 runtime provenance separate",
        }
    raise ValueError(f"unknown source kind: {kind}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/tables/phase20-caller-gate-sink.csv"),
    )
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()

    normalized: list[dict[str, str]] = []
    manifests: list[tuple[str, str, str]] = []
    for kind, relative in SOURCES.items():
        path = root / relative
        if not path.is_file():
            raise SystemExit(f"missing source: {path}")
        source_rows = rows(path)
        manifests.append((kind, relative, digest(path)))
        normalized.extend(normalize(kind, item) for item in source_rows)

    ids = [item["record_id"] for item in normalized]
    if len(ids) != len(set(ids)):
        duplicates = sorted({item for item in ids if ids.count(item) > 1})
        raise SystemExit(f"duplicate IDs: {duplicates}")
    if any(set(item) != set(FIELDS) for item in normalized):
        raise SystemExit("normalized schema mismatch")

    if args.verify_only:
        print(f"verified {len(normalized)} rows from {len(SOURCES)} ledgers")
        for kind, relative, sha in manifests:
            print(f"{kind}\t{sha}\t{relative}")
        return 0

    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=FIELDS, quoting=csv.QUOTE_ALL, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(normalized)
    print(f"wrote {len(normalized)} rows to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
