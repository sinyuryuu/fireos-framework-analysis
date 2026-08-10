#!/usr/bin/env python3
"""Normalize Phase 6RG host ledgers and saved read-only device evidence.

The script is intentionally offline.  It reads CSV/markdown files and an
already-captured snapshot directory; it never invokes adb or any device,
Binder, settings, package, driver, OTA, recovery, or root operation.
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


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def normalize_ipc(path: Path) -> list[dict[str, str]]:
    rows = []
    for row in read_csv(path):
        rows.append({
            "domain": "amazon-ipc-residual",
            "row_id": row["row_id"],
            "subject": row["scope"],
            "method_or_test": row["registration"],
            "publication_or_source": row["registration"],
            "caller_or_image_node": "; ".join(
                value for value in (row["caller"], row["sender_or_input"]) if value
            ),
            "gate_or_policy": row["gate"],
            "identity_or_reachability": "; ".join(
                value for value in (row["identity"], row["reachability"]) if value
            ),
            "user_scope_or_impact": row["user_scope"],
            "sink_or_result": row["sink"],
            "low_privilege_status": row["reachability"],
            "classification": row["confidence"],
            "evidence": row["evidence"],
            "source_or_hash": "",
            "next_safe_step": row["next_safe_step"],
            "notes": "UNKNOWN remains an evidence gap, not a vulnerability claim",
        })
    return rows


def normalize_source(path: Path) -> list[dict[str, str]]:
    rows = []
    for row in read_csv(path):
        rows.append({
            "domain": "source-package-policy",
            "row_id": row["row_id"],
            "subject": row["surface"],
            "method_or_test": row["source_ref"],
            "publication_or_source": row["image_ref"],
            "caller_or_image_node": "; ".join(
                value for value in (row["init_or_config"], row["client_or_caller"]) if value
            ),
            "gate_or_policy": row["selinux_or_permission"],
            "identity_or_reachability": row["risk_status"],
            "user_scope_or_impact": row["remainder"],
            "sink_or_result": row["sink"],
            "low_privilege_status": row["risk_status"],
            "classification": row["confidence"],
            "evidence": row["evidence"],
            "source_or_hash": "",
            "next_safe_step": row["next_safe_step"],
            "notes": row["remainder"],
        })
    return rows


def normalize_existing(path: Path) -> list[dict[str, str]]:
    rows = []
    for row in read_csv(path):
        rows.append({
            "domain": "existing-runtime-evidence",
            "row_id": row["row_id"],
            "subject": row["scope"],
            "method_or_test": "; ".join(
                value for value in (row["test_id"], row["command_or_path"]) if value
            ),
            "publication_or_source": row["command_or_path"],
            "caller_or_image_node": "UNKNOWN",
            "gate_or_policy": row["precondition"],
            "identity_or_reachability": row["classification"],
            "user_scope_or_impact": row["precondition"],
            "sink_or_result": row["observed_result"],
            "low_privilege_status": row["classification"],
            "classification": row["classification"],
            "evidence": row["evidence_hash"],
            "source_or_hash": "",
            "next_safe_step": row["next_safe_step"],
            "notes": row["repeat_status"],
        })
    return rows


def snapshot_row(path: Path) -> dict[str, str]:
    files = sorted(p for p in path.rglob("*") if p.is_file())
    hashes = "; ".join(f"{p.name}={digest(p)}" for p in files)
    metadata = path / "metadata.json"
    return {
        "domain": "exact-device-readonly",
        "row_id": "6RG-DEVICE-01",
        "subject": "PS7331 exact-device metadata snapshot",
        "method_or_test": "capture_phase6qe_device_readonly.py",
        "publication_or_source": str(path),
        "caller_or_image_node": "ADB shell metadata commands only",
        "gate_or_policy": "SELinux enforcing and node metadata only",
        "identity_or_reachability": "read-only observation; no privilege transition",
        "user_scope_or_impact": "User 0 / exact serial",
        "sink_or_result": "HOME Fire priority 50; node ownership/mode/label metadata",
        "low_privilege_status": "NO_PRIVILEGE_TRANSITION_OBSERVED",
        "classification": "CONFIRMED_READONLY",
        "evidence": str(metadata),
        "source_or_hash": hashes,
        "next_safe_step": "Host-only correlation; do not open nodes or call private services",
        "notes": "Snapshot metadata explicitly records no Binder, mutation, reboot, OTA, root, or exploit",
    }


def asset_row(path: Path) -> dict[str, str]:
    return {
        "domain": "asset-provenance",
        "row_id": "6RG-ASSET-01",
        "subject": "PS7331 source and installation package scope",
        "method_or_test": "host-only asset-scope review",
        "publication_or_source": str(path),
        "caller_or_image_node": "official extracted image/source vs local research files",
        "gate_or_policy": "provenance classification",
        "identity_or_reachability": "not a runtime reachability claim",
        "user_scope_or_impact": "host-only",
        "sink_or_result": "source/package evidence boundaries",
        "low_privilege_status": "NOT_APPLICABLE",
        "classification": "CONFIRMED_PROVENANCE_BOUNDARY",
        "evidence": str(path),
        "source_or_hash": digest(path),
        "next_safe_step": "Use official image/source only for exact-build claims; keep local exploit files excluded",
        "notes": "Local boot_unpacked exploit/root files are not official OTA/GPL provenance",
    }


def validate(rows: list[dict[str, str]]) -> None:
    for number, row in enumerate(rows, start=1):
        missing = [field for field in FIELDS if field not in row]
        if missing:
            raise SystemExit(f"row {number} missing fields: {missing}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ipc", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--existing", type=Path, required=True)
    parser.add_argument("--device-snapshot", type=Path, required=True)
    parser.add_argument("--asset-scope", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.ipc, args.source, args.existing, args.asset_scope]
    rows = (
        normalize_ipc(args.ipc)
        + normalize_source(args.source)
        + normalize_existing(args.existing)
        + [snapshot_row(args.device_snapshot), asset_row(args.asset_scope)]
    )
    validate(rows)
    manifest = {
        "schema": "phase6rg-privilege-surface-v1",
        "device_contacted_by_script": False,
        "device_nodes_opened_by_script": False,
        "binder_or_settings_operation_by_script": False,
        "mutation_by_script": False,
        "root_or_exploit_by_script": False,
        "inputs": {str(path): digest(path) for path in inputs},
        "device_snapshot": str(args.device_snapshot),
        "device_snapshot_file_count": len(
            [p for p in args.device_snapshot.rglob("*") if p.is_file()]
        ),
        "input_row_counts": {
            str(args.ipc): len(read_csv(args.ipc)),
            str(args.source): len(read_csv(args.source)),
            str(args.existing): len(read_csv(args.existing)),
        },
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
    manifest["output_sha256"] = digest(args.output)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
