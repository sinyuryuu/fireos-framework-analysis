#!/usr/bin/env python3
"""Build a normalized, host-only Phase 19 privilege-surface ledger.

This script reads the five bounded worker ledgers and emits one CSV with a
common caller -> gate -> identity/user scope -> sink shape.  It never invokes
ADB, Binder, a driver, an updater, or any other device operation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path


OUTPUT_FIELDS = [
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
    "ipc": "work/luna_worker_phase19_ipc_audit_20260810.csv",
    "ota": "work/luna_worker_phase19_ota_audit_20260810.csv",
    "driver": "work/luna_worker_phase19_driver_audit_20260810.csv",
    "reconciliation": "work/luna_worker_phase19_reconciliation_20260810.csv",
    "provenance": "work/luna_worker_phase19_provenance_20260810.csv",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    return rows


def confidence(classification: str) -> str:
    value = classification.upper()
    if "CONFIRMED" in value or "EXACT_" in value:
        return "Confirmed"
    if "BOUNDED_NEGATIVE" in value:
        return "Disproved"
    if "UNKNOWN" in value or "UNRESOLVED" in value:
        return "Hypothesis"
    if "STATIC" in value or "CAPABILITY" in value or "STRONG" in value:
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
            "caller": row["shipped_native_opener"],
            "gate": f"{row['node_owner_mode_context']} | {row['merged_te_or_genfs']}",
            "identity_or_user_scope": row["caller_uid_domain"],
            "sink": row["sink"],
            "runtime_or_result": row["operation"],
            "missing_edge": row["missing_edge"],
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
            "artifact_or_entry": row["phase_scope"],
            "caller": "historical tests only",
            "gate": row["actual_commands_recorded"],
            "identity_or_user_scope": row["test_ids"],
            "sink": row["result"],
            "runtime_or_result": row["rollback_or_final_guard"],
            "missing_edge": row["missing_evidence"],
            "classification": "RECONCILED_NO_REPEAT",
            "confidence": "Confirmed",
            "evidence": row["primary_evidence"],
            "next_safe_step": "Host-only reparse only; do not replay the historical device mutation",
        }
    if kind == "provenance":
        classification = row["classification"]
        return {
            "record_id": f"P19E-{row['item']}",
            "record_type": "provenance",
            "surface": row["item"],
            "artifact_or_entry": row["path_or_evidence"],
            "caller": "host-side provenance",
            "gate": "version/product/hash alignment",
            "identity_or_user_scope": f"{row['device_product']} | {row['fingerprint']}",
            "sink": "artifact identity only",
            "runtime_or_result": f"version={row['version']}; security_patch={row['security_patch']}",
            "missing_edge": row["notes"],
            "classification": classification,
            "confidence": confidence(classification),
            "evidence": row["path_or_evidence"],
            "next_safe_step": "Keep exact-version boundaries; do not treat PS7331 artifacts as PS7330 runtime proof",
        }
    raise ValueError(f"unsupported source kind: {kind}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/tables/phase19-caller-gate-sink.csv"),
    )
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()

    normalized: list[dict[str, str]] = []
    input_manifest: list[tuple[str, str, str]] = []
    for kind, relative in SOURCES.items():
        path = root / relative
        if not path.is_file():
            raise SystemExit(f"missing Phase 19 source: {path}")
        rows = read_csv(path)
        input_manifest.append((kind, relative, sha256(path)))
        normalized.extend(normalize(kind, row) for row in rows)

    ids = [row["record_id"] for row in normalized]
    if len(ids) != len(set(ids)):
        duplicates = sorted({item for item in ids if ids.count(item) > 1})
        raise SystemExit(f"duplicate record IDs: {duplicates}")
    if any(set(row) != set(OUTPUT_FIELDS) for row in normalized):
        raise SystemExit("normalized row schema mismatch")

    if args.verify_only:
        print(f"verified {len(normalized)} rows from {len(SOURCES)} ledgers")
        for kind, relative, digest in input_manifest:
            print(f"{kind}\t{digest}\t{relative}")
        return 0

    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=OUTPUT_FIELDS,
            quoting=csv.QUOTE_ALL,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(normalized)
    print(f"wrote {len(normalized)} rows to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
