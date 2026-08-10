#!/usr/bin/env python3
"""Build a conservative Phase 6SB--6SE privilege-surface ledger.

This script only parses preserved CSV evidence.  It never imports ADB helpers,
opens device nodes, invokes Binder, executes APK/native artifacts, or mutates a
device.  The output deliberately keeps raw status and confidence separate so a
static sink cannot be promoted to a reachable privilege route by aggregation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


FIELDS = [
    "phase",
    "record_id",
    "surface",
    "source_path",
    "source_sha256",
    "entry_or_node",
    "caller_or_identity",
    "gate_or_policy",
    "sink_or_effect",
    "low_privilege_reachability",
    "classification",
    "confidence",
    "unknowns",
    "safety_disposition",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"missing CSV header: {path}")
        expected = len(reader.fieldnames)
        rows = []
        for row in reader:
            if None in row:
                raise ValueError(f"malformed CSV row at line {reader.line_num}: {path}")
            if len(row) != expected:
                raise ValueError(f"field count mismatch at line {reader.line_num}: {path}")
            rows.append({k: (v or "") for k, v in row.items()})
    return rows


def row(phase: str, record_id: str, **values: str) -> dict[str, str]:
    output = {field: "" for field in FIELDS}
    output.update(phase=phase, record_id=record_id)
    for key, value in values.items():
        if key not in output:
            raise KeyError(key)
        output[key] = value or ""
    return output


def from_base(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    result = []
    for item in rows:
        result.append(row(
            item.get("phase", "BASE"),
            item.get("row_id", ""),
            surface=item.get("surface_or_subject", ""),
            source_path=item.get("source_or_location", ""),
            source_sha256=item.get("source_sha256", ""),
            entry_or_node=item.get("user_entry_or_entry", ""),
            caller_or_identity=item.get("client_or_caller", ""),
            gate_or_policy=item.get("gate_or_access", ""),
            sink_or_effect=item.get("sink_or_impact", ""),
            low_privilege_reachability=item.get("status", ""),
            classification=item.get("status", ""),
            confidence="PRESERVED_BASE_LEDGER",
            unknowns=item.get("next_safe_host_only_step", ""),
            safety_disposition="host-only source ledger; no device mutation",
        ))
    return result


def from_sb(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row(
        "6SB", item.get("row_id", ""),
        surface=item.get("surface", ""),
        source_path=item.get("source_path", ""),
        source_sha256=item.get("source_sha256", ""),
        entry_or_node=item.get("exact_evidence", ""),
        caller_or_identity=item.get("bounded_result", ""),
        gate_or_policy=item.get("classification", ""),
        sink_or_effect=item.get("bounded_result", ""),
        low_privilege_reachability=item.get("classification", ""),
        classification=item.get("classification", ""),
        confidence=item.get("confidence", ""),
        unknowns=item.get("unknowns", ""),
        safety_disposition="no adb, Binder transaction, service call, or package mutation",
    ) for item in rows]


def from_sc(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row(
        "6SC", f"6SC-{item.get('row_id', '')}",
        surface=item.get("surface", ""),
        source_path=item.get("source_path_line", ""),
        source_sha256=item.get("source_sha256", ""),
        entry_or_node=item.get("node_or_entry", ""),
        caller_or_identity=item.get("userspace_caller", ""),
        gate_or_policy="; ".join(filter(None, [item.get("ueventd_evidence", ""), item.get("selinux_evidence", "")])),
        sink_or_effect=item.get("sensitive_effect", ""),
        low_privilege_reachability=item.get("status", ""),
        classification=item.get("status", ""),
        confidence=item.get("confidence", ""),
        unknowns=item.get("userspace_caller", ""),
        safety_disposition="source-only; no device node, ioctl, Binder, or diagnostic operation",
    ) for item in rows]


def from_sd(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row(
        "6SD", item.get("id", ""),
        surface=item.get("component_or_chain", ""),
        source_path=item.get("evidence", ""),
        entry_or_node=item.get("caller_or_sender", ""),
        caller_or_identity=item.get("permission_or_identity", ""),
        gate_or_policy="; ".join(filter(None, [item.get("input_validation", ""), item.get("path_symlink_metadata_gate", "")])),
        sink_or_effect=item.get("high_privilege_sink", ""),
        low_privilege_reachability=item.get("untrusted_app_or_shell_to_sink", ""),
        classification=item.get("status", ""),
        confidence="NOT_STATED_IN_SOURCE_ROW",
        unknowns="caller/provenance/canonicalization fields retained as stated in source row",
        safety_disposition="no OTA, recovery, updater, reboot, payload, or partition operation",
    ) for item in rows]


def from_se(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row(
        "6SE", item.get("id", ""),
        surface=item.get("surface_or_claim", ""),
        source_path=item.get("evidence_path", ""),
        source_sha256=item.get("evidence_sha256", ""),
        entry_or_node=item.get("issue_type", ""),
        caller_or_identity=item.get("existing_label_or_result", ""),
        gate_or_policy=item.get("reason_for_review", ""),
        sink_or_effect=item.get("review_action", ""),
        low_privilege_reachability=item.get("classification", ""),
        classification=item.get("classification", ""),
        confidence="REVIEW_CLASSIFICATION_NOT_CONFIDENCE",
        unknowns=item.get("reason_for_review", ""),
        safety_disposition="catalog-only; no device operation",
    ) for item in rows]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="output/tables/phase6ry-sa-control-surface.csv", type=Path)
    parser.add_argument("--sb", default="work/luna_worker_phase6sb_ipc_20260810.csv", type=Path)
    parser.add_argument("--sc", default="work/luna_worker_phase6sc_kernel_20260810.csv", type=Path)
    parser.add_argument("--sd", default="work/luna_worker_phase6sd_ota_20260810.csv", type=Path)
    parser.add_argument("--se", default="work/luna_worker_phase6se_catalog_20260810.csv", type=Path)
    parser.add_argument("--device-snapshot", type=Path, help="optional metadata-only snapshot directory")
    parser.add_argument("--output", default="output/tables/phase6sb-se-control-surface.csv", type=Path)
    parser.add_argument("--manifest", default="output/tables/phase6sb-se-control-surface.csv.manifest.json", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="validate and count only")
    args = parser.parse_args()

    inputs = {"base": args.base, "6SB": args.sb, "6SC": args.sc, "6SD": args.sd, "6SE": args.se}
    for name, path in inputs.items():
        if not path.is_file():
            raise SystemExit(f"missing input {name}: {path}")

    base = from_base(read_rows(args.base))
    sb = from_sb(read_rows(args.sb))
    sc = from_sc(read_rows(args.sc))
    sd = from_sd(read_rows(args.sd))
    se = from_se(read_rows(args.se))
    records = base + sb + sc + sd + se
    ids = [item["record_id"] for item in records]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate record_id in merged ledger")

    counts = Counter(item["phase"] for item in records)
    summary = {
        "schema": "phase6sb-se-control-surface-v1",
        "row_count": len(records),
        "row_counts": dict(sorted(counts.items())),
        "inputs": {name: {"path": str(path), "sha256": sha256(path), "rows": len(read_rows(path))} for name, path in inputs.items()},
        "output": str(args.output),
        "device_contacted_by_script": False,
        "binder_transaction_invoked_by_script": False,
        "settings_or_package_mutation_by_script": False,
        "driver_node_opened_by_script": False,
        "ota_recovery_or_updater_executed_by_script": False,
        "root_or_exploit_by_script": False,
    }

    if args.device_snapshot is not None:
        metadata_path = args.device_snapshot / "metadata.json"
        sums_path = args.device_snapshot / "sha256sums.txt"
        if not metadata_path.is_file() or not sums_path.is_file():
            raise SystemExit(f"invalid device snapshot: {args.device_snapshot}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        required_false = [
            "device_nodes_opened",
            "driver_data_read",
            "binder_transactions_invoked",
            "settings_or_package_mutation",
            "reboot",
            "ota_or_recovery",
            "root_or_exploit",
        ]
        if metadata.get("read_only") is not True or any(metadata.get(key) is not False for key in required_false):
            raise SystemExit("device snapshot safety metadata is not read-only")
        summary["device_snapshot"] = {
            "path": str(args.device_snapshot),
            "metadata_sha256": sha256(metadata_path),
            "sha256sums_sha256": sha256(sums_path),
            "serial": metadata.get("serial"),
            "captured_at_utc": metadata.get("captured_at_utc"),
        }

    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(records)
        summary["output_sha256"] = sha256(args.output)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
