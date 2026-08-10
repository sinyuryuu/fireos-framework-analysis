#!/usr/bin/env python3
"""Normalize Phase 6PX provenance worker matrices.

Host-only: reads worker CSV files and writes a new normalized table.  It never
contacts a device, invokes Binder, parses an OTA for execution, or mutates any
state.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def output_exists(path: Path) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing output: {path}")


def normalize_denylist(items: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "family": "deny-list-provenance",
            "route": item["key/resource"],
            "status": item["status"],
            "direct_evidence": item["package membership evidence"],
            "caller_or_gate": item["reader/writer"],
            "sink_or_effect": item["source"],
            "evidence": item["hash"],
            "next_safe_step": item["next safe step"],
        }
        for item in items
    ]


def normalize_boot(items: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "family": "boot-after-system-ota",
            "route": item["edge"],
            "status": item["status"].split(";", 1)[0],
            "direct_evidence": item["caller context"],
            "caller_or_gate": item["permission/gate"],
            "sink_or_effect": item["sink"],
            "evidence": item["evidence hash"],
            "next_safe_step": item["next safe step"],
        }
        for item in items
    ]


def normalize_ota(items: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "family": "ota-recovery-handoff",
            "route": item["route"],
            "status": item["status (closed/unknown/rejected)"],
            "direct_evidence": f"low_privilege_reachable={item['low_privilege_reachable']}; path={item['path handling']}",
            "caller_or_gate": f"caller={item['caller']}; gate={item['gate']}",
            "sink_or_effect": item["first sink"],
            "evidence": item["source artifact/hash"],
            "next_safe_step": item["next safe step"],
        }
        for item in items
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--denylist", type=Path, required=True)
    parser.add_argument("--bootafter-ota", type=Path, required=True)
    parser.add_argument("--ota-recovery", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.denylist, args.bootafter_ota, args.ota_recovery]
    for path in inputs:
        if not path.exists():
            raise SystemExit(f"missing input: {path}")
    if args.dry_run:
        print(json.dumps({
            "device_contacted": False,
            "mutation": False,
            "binder_transaction": False,
            "inputs": [str(path) for path in inputs],
            "output": str(args.output),
            "manifest": str(args.manifest),
        }, indent=2))
        return 0

    output_exists(args.output)
    output_exists(args.manifest)

    normalized = []
    normalized.extend(normalize_denylist(rows(args.denylist)))
    normalized.extend(normalize_boot(rows(args.bootafter_ota)))
    normalized.extend(normalize_ota(rows(args.ota_recovery)))
    fields = [
        "family",
        "route",
        "status",
        "direct_evidence",
        "caller_or_gate",
        "sink_or_effect",
        "evidence",
        "next_safe_step",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(normalized)

    manifest = {
        "schema": "phase6px-provenance-closure-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "device_contacted_by_script": False,
        "mutation_by_script": False,
        "binder_transaction_by_script": False,
        "ota_executed_by_script": False,
        "inputs": {str(path): sha256(path) for path in inputs},
        "row_count": len(normalized),
        "output": str(args.output),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(normalized)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
