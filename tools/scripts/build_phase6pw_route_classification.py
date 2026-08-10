#!/usr/bin/env python3
"""Normalize Phase 6PW worker audits and the live read-only capture.

This is deliberately host-only.  It reads CSV/text evidence, refuses to
overwrite outputs, and never invokes adb, Binder, package-manager commands,
or any device mutation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def ensure_distinct(path: Path) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing output: {path}")


def load_live(path: Path) -> dict[str, str]:
    metadata = (path / "metadata.txt").read_text(encoding="utf-8")
    required = {
        "mutation=false",
        "binder_transaction=false",
        "reboot=false",
    }
    if not required.issubset(set(metadata.splitlines())):
        raise SystemExit("live capture is not the expected read-only schema")
    resolve = (path / "home_resolve.stdout.txt").read_text(encoding="utf-8").strip()
    if "com.amazon.firelauncher/.Launcher" not in resolve:
        raise SystemExit("live capture does not identify the expected Fire HOME")
    return {
        "family": "live-readonly",
        "id_or_route": "PV-LIVE-RO-01",
        "status": "confirmed",
        "real_home_or_sink": "com.amazon.firelauncher/.Launcher; priority=50",
        "observed_result_or_effect": "User 0 resolver remains Fire; capture reports no mutation, Binder transaction, or reboot",
        "evidence": str(path),
        "evidence_type": "runtime-read-only",
        "next_safe_step": "Use as current comparator; do not repeat mutation without a changed hypothesis",
    }


def normalize_evidence(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "family": "existing-evidence-audit",
            "id_or_route": row["test/evidence"],
            "status": row["status (closed/unknown/rejected)"],
            "real_home_or_sink": row["security relevance"],
            "observed_result_or_effect": row["observed result"],
            "evidence": row["source file"],
            "evidence_type": "existing-evidence-audit",
            "next_safe_step": row["next safe step"],
        }
        for row in rows
    ]


def normalize_ipc(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "family": "ipc-boundary-audit",
            "id_or_route": row["id"],
            "status": row["status"].split(";", 1)[0],
            "real_home_or_sink": row["downstream_effect"],
            "observed_result_or_effect": (
                f"uid_scope={row['uid_scope']}; caller_gate={row['caller_gate']}"
            ),
            "evidence": row["evidence"],
            "evidence_type": "host-static-plus-existing-runtime",
            "next_safe_step": row["next_safe_verification"],
        }
        for row in rows
    ]


def normalize_workaround(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "family": "home-workaround-audit",
            "id_or_route": row["route"],
            "status": row["status"],
            "real_home_or_sink": (
                f"real_home={row['real HOME?']}; persistence={row['persistence']}"
            ),
            "observed_result_or_effect": row["risk"],
            "evidence": row["evidence"],
            "evidence_type": "existing-runtime-and-host-audit",
            "next_safe_step": row["next safe step"],
        }
        for row in rows
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--ipc", type=Path, required=True)
    parser.add_argument("--workaround", type=Path, required=True)
    parser.add_argument("--live-capture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.evidence, args.ipc, args.workaround]
    for path in inputs + [args.live_capture]:
        if not path.exists():
            raise SystemExit(f"missing input: {path}")
    ensure_distinct(args.output)
    ensure_distinct(args.manifest)

    if args.dry_run:
        print(json.dumps({
            "device_contacted": False,
            "mutation": False,
            "inputs": [str(path) for path in inputs],
            "live_capture": str(args.live_capture),
            "output": str(args.output),
            "manifest": str(args.manifest),
        }, indent=2))
        return 0

    rows = []
    rows.extend(normalize_evidence(read_csv(args.evidence)))
    rows.extend(normalize_ipc(read_csv(args.ipc)))
    rows.extend(normalize_workaround(read_csv(args.workaround)))
    rows.append(load_live(args.live_capture))
    fields = [
        "family",
        "id_or_route",
        "status",
        "real_home_or_sink",
        "observed_result_or_effect",
        "evidence",
        "evidence_type",
        "next_safe_step",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "schema": "phase6pw-route-classification-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "device_contacted_by_script": False,
        "mutation_by_script": False,
        "binder_transaction_by_script": False,
        "inputs": {str(path): digest(path) for path in inputs},
        "live_capture_sha256_manifest": digest(args.live_capture / "sha256sums.txt"),
        "row_count": len(rows),
        "output": str(args.output),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} normalized rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
