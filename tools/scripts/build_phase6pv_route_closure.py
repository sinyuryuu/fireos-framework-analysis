#!/usr/bin/env python3
"""Build a normalized host-only closure table from Phase 6PV worker CSVs.

This script reads worker-produced CSV evidence only. It never contacts a device,
invokes a Binder/service, writes package/settings state, or executes an OTA.
The output path must be new so that raw evidence is not overwritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


FIELDS = [
    "family",
    "source_id",
    "surface",
    "caller_reachability",
    "gate_or_boundary",
    "sink_or_capability",
    "runtime_result",
    "disposition",
    "confidence",
    "evidence",
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


def normalize_kernel(row: dict[str, str]) -> dict[str, str]:
    disposition = row["disposition"]
    confidence = {
        "closed": "Strong evidence",
        "risk-rejected": "Strong evidence",
        "static-only": "Strong evidence",
        "unknown": "Unknown",
    }.get(disposition, "Unknown")
    return {
        "family": "kernel/GPL",
        "source_id": row["surface"],
        "surface": row["source_path"],
        "caller_reachability": row["caller_permission_boundary"],
        "gate_or_boundary": row["config_or_artifact"],
        "sink_or_capability": row["framework_sink"],
        "runtime_result": row["runtime_evidence"],
        "disposition": disposition,
        "confidence": confidence,
        "evidence": row["source_path"] + "; source_sha256=" + row["source_sha256"],
    }


def normalize_ipc(row: dict[str, str]) -> dict[str, str]:
    return {
        "family": "Binder/IPC",
        "source_id": row["id"],
        "surface": row["caller_entry"],
        "caller_reachability": row["caller_reachability"],
        "gate_or_boundary": row["manifest_service_gate"],
        "sink_or_capability": row["sink"],
        "runtime_result": row["saved_runtime_result"],
        "disposition": row["classification"],
        "confidence": row["confidence"],
        "evidence": row["evidence_paths"],
    }


def normalize_ota(row: dict[str, str]) -> dict[str, str]:
    if row["id"] == "ARCH-01":
        # The worker report preserves the earlier Phase 6FE bounded result.
        # Phase 6MI later completed the same source-tar stream to EOF; keep the
        # worker input immutable and apply the authoritative correction here.
        return {
            "family": "OTA/post-install",
            "source_id": row["id"],
            "surface": row["surface"],
            "caller_reachability": "No unlisted outer-tail member remains after the EOF-complete audit",
            "gate_or_boundary": "artifacts/phase6mi-source-tar-eof-20260810-03/summary.json",
            "sink_or_capability": "No OTA/post-install/recovery/HOME helper in the 35-member source archive",
            "runtime_result": "Phase 6MI reached_eof=true; extracted=false; executed=false; device_mutation=false",
            "disposition": "negative at EOF-complete source-archive member-name scope",
            "confidence": "Strong evidence",
            "evidence": "summary_sha256=409ed81ede46db87a0ef8a05cc33b99df2b66e068d1edc1ac481a42e0606169b",
        }
    status = row["status"]
    confidence = "Unknown" if "incomplete" in status or "open" in status else "Strong evidence"
    return {
        "family": "OTA/post-install",
        "source_id": row["id"],
        "surface": row["surface"],
        "caller_reachability": row["untrusted caller route"],
        "gate_or_boundary": row["exact path or offset"],
        "sink_or_capability": row["privileged capability or sink"],
        "runtime_result": row["existing test or limit"],
        "disposition": status,
        "confidence": confidence,
        "evidence": row["evidence SHA-256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", type=Path, required=True)
    parser.add_argument("--ipc", type=Path, required=True)
    parser.add_argument("--ota", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.kernel, args.ipc, args.ota]
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise SystemExit("missing input: " + ", ".join(missing))
    if args.dry_run:
        print(json.dumps({
            "output": str(args.output),
            "inputs": [str(path) for path in inputs],
            "device_contacted": False,
            "binder_invoked": False,
            "ota_executed": False,
        }, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    rows.extend(normalize_kernel(row) for row in read_rows(args.kernel))
    rows.extend(normalize_ipc(row) for row in read_rows(args.ipc))
    rows.extend(normalize_ota(row) for row in read_rows(args.ota))

    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "schema": "phase6pv-broad-route-closure-v1",
        "inputs": {str(path): sha256(path) for path in inputs},
        "output": str(args.output),
        "row_count": len(rows),
        "device_contacted": False,
        "binder_invoked": False,
        "ota_executed": False,
    }
    manifest_path = args.output.with_suffix(args.output.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"row_count": len(rows), "output": str(args.output), "manifest": str(manifest_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
