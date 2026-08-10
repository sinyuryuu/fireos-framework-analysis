#!/usr/bin/env python3
"""Normalize Phase 6RS/6RT/6RU host-only ledgers offline."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


FIELDS = [
    "domain", "row_id", "subject", "method_or_route", "registration_or_api",
    "caller_or_permission", "gate_or_policy", "identity_or_formal_home",
    "user_scope_or_persistence", "sink_or_result", "reachability_or_mutation",
    "classification", "evidence", "source_or_hash", "next_safe_step", "notes",
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def settings_rows(path: Path) -> list[dict[str, str]]:
    out = []
    for row in rows(path):
        out.append({
            "domain": "settings-pm-writer",
            "row_id": row["row_id"],
            "subject": row["scope"],
            "method_or_route": row["writer"],
            "registration_or_api": row["writer"],
            "caller_or_permission": row["caller"],
            "gate_or_policy": row["permission_or_gate"],
            "identity_or_formal_home": row["identity"],
            "user_scope_or_persistence": row["user_scope"],
            "sink_or_result": row["sink"],
            "reachability_or_mutation": row["reachability"],
            "classification": row["confidence"],
            "evidence": row["evidence"],
            "source_or_hash": "",
            "next_safe_step": row["next_safe_step"],
            "notes": "UNKNOWN/NOT_FOUND retained as evidence gaps",
        })
    return out


def systemui_rows(path: Path) -> list[dict[str, str]]:
    out = []
    for row in rows(path):
        out.append({
            "domain": "systemui-callback",
            "row_id": row["row_id"],
            "subject": row["scope"],
            "method_or_route": row["registration"],
            "registration_or_api": row["registration"],
            "caller_or_permission": row["caller"],
            "gate_or_policy": row["gate"],
            "identity_or_formal_home": row["identity"],
            "user_scope_or_persistence": row["input"],
            "sink_or_result": row["sink"],
            "reachability_or_mutation": row["reachability"],
            "classification": row["classification"],
            "evidence": row["evidence"],
            "source_or_hash": "",
            "next_safe_step": row["next_safe_step"],
            "notes": "No explicit Fire selector is inferred from registration alone",
        })
    return out


def fallback_rows(path: Path) -> list[dict[str, str]]:
    out = []
    for row in rows(path):
        out.append({
            "domain": "rootless-fallback",
            "row_id": row["row_id"],
            "subject": row["route"],
            "method_or_route": row["api_or_tool"],
            "registration_or_api": row["api_or_tool"],
            "caller_or_permission": row["required_permission"],
            "gate_or_policy": row["required_permission"],
            "identity_or_formal_home": row["formal_home"],
            "user_scope_or_persistence": row["persistence"],
            "sink_or_result": row["latency_or_flicker"],
            "reachability_or_mutation": row["device_state_mutation"],
            "classification": row["classification"],
            "evidence": row["evidence"],
            "source_or_hash": "",
            "next_safe_step": row["next_safe_step"],
            "notes": "rollback=" + row["rollback"],
        })
    return out


def validate(data: list[dict[str, str]]) -> None:
    for number, row in enumerate(data, 1):
        missing = [field for field in FIELDS if field not in row]
        if missing:
            raise SystemExit(f"row {number} missing {missing}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--systemui", type=Path, required=True)
    parser.add_argument("--fallback", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.settings, args.systemui, args.fallback]
    data = settings_rows(args.settings) + systemui_rows(args.systemui) + fallback_rows(args.fallback)
    validate(data)
    manifest = {
        "schema": "phase6rs-ru-surface-v1",
        "device_contacted_by_script": False,
        "binder_or_settings_operation_by_script": False,
        "mutation_by_script": False,
        "root_or_exploit_by_script": False,
        "inputs": {str(path): digest(path) for path in inputs},
        "input_row_counts": {str(path): len(rows(path)) for path in inputs},
        "row_count": len(data),
        "output": str(args.output),
    }
    if args.dry_run:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)
    manifest["output_sha256"] = digest(args.output)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(data)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
