#!/usr/bin/env python3
"""Build the Phase 6PY service/state/exported-sink closure matrix.

This is a host-only normalizer.  It reads three worker CSVs and writes a new
normalized CSV plus a hash manifest.  It never contacts a device, invokes a
Binder transaction, executes an updater, or mutates package/settings state.
Existing output files are never overwritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


FIELDS = [
    "domain",
    "subject",
    "source_or_entry",
    "target_or_scope",
    "caller_gate",
    "identity_or_permission",
    "sink_or_effect",
    "runtime_evidence",
    "status",
    "next_safe_step",
    "source_csv",
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


def refuse_overwrite(path: Path) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing output: {path}")


def normalize_service(path: Path) -> list[dict[str, str]]:
    result = []
    for row in read_rows(path):
        result.append(
            {
                "domain": "amazon-service-permission",
                "subject": row["service"],
                "source_or_entry": row["entry"],
                "target_or_scope": row["permission"],
                "caller_gate": row["caller gate"],
                "identity_or_permission": row["identity handling"],
                "sink_or_effect": row["sink"],
                "runtime_evidence": row["runtime evidence"],
                "status": row["status"],
                "next_safe_step": row["next safe step"],
                "source_csv": str(path),
            }
        )
    return result


def normalize_state(path: Path) -> list[dict[str, str]]:
    result = []
    for row in read_rows(path):
        result.append(
            {
                "domain": "fire-package-state-writer",
                "subject": row["writer"],
                "source_or_entry": row["source/method"],
                "target_or_scope": (
                    f"target={row['target package/component']}; "
                    f"user_scope={row['user scope']}"
                ),
                "caller_gate": row["caller gate"],
                "identity_or_permission": row["identity handling"],
                "sink_or_effect": row["sink"],
                "runtime_evidence": row["existing runtime result"],
                "status": row["status"],
                "next_safe_step": row["next safe step"],
                "source_csv": str(path),
            }
        )
    return result


def normalize_fosinit(path: Path) -> list[dict[str, str]]:
    result = []
    for row in read_rows(path):
        result.append(
            {
                "domain": "fosinit-exported-sink",
                "subject": row["component"],
                "source_or_entry": row["registration/source"],
                "target_or_scope": (
                    f"exported={row['exported']}; permission={row['permission']}"
                ),
                "caller_gate": row["caller gate"],
                "identity_or_permission": row["permission"],
                "sink_or_effect": row["downstream sink"],
                "runtime_evidence": row["evidence"],
                "status": row["status"],
                "next_safe_step": row["next safe step"],
                "source_csv": str(path),
            }
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service", type=Path, required=True)
    parser.add_argument("--state-writers", type=Path, required=True)
    parser.add_argument("--fosinit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.service, args.state_writers, args.fosinit]
    for path in inputs:
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")

    if args.dry_run:
        print(
            json.dumps(
                {
                    "device_contacted": False,
                    "mutation": False,
                    "binder_transaction": False,
                    "root_or_exploit": False,
                    "inputs": [str(path) for path in inputs],
                    "output": str(args.output),
                    "manifest": str(args.manifest),
                },
                indent=2,
            )
        )
        return 0

    refuse_overwrite(args.output)
    refuse_overwrite(args.manifest)

    normalized = []
    normalized.extend(normalize_service(args.service))
    normalized.extend(normalize_state(args.state_writers))
    normalized.extend(normalize_fosinit(args.fosinit))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(normalized)

    manifest = {
        "schema": "phase6py-service-state-exported-closure-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "device_contacted_by_script": False,
        "mutation_by_script": False,
        "binder_transaction_by_script": False,
        "root_or_exploit_by_script": False,
        "inputs": {str(path): sha256(path) for path in inputs},
        "input_row_counts": {
            str(args.service): len(read_rows(args.service)),
            str(args.state_writers): len(read_rows(args.state_writers)),
            str(args.fosinit): len(read_rows(args.fosinit)),
        },
        "row_count": len(normalized),
        "output_sha256": sha256(args.output),
        "output": str(args.output),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(normalized)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
