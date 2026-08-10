#!/usr/bin/env python3
"""Build a normalized, host-only Phase 6SF–SI control-surface ledger.

The worker CSVs are preserved verbatim.  This script only parses them, maps
their different schemas into the existing 14-column ledger shape, and emits
hash metadata.  It never talks to ADB and never mutates device state.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


LEDGER_FIELDS = [
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
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"{path}: no data rows")
    return [{str(k): (v or "") for k, v in row.items()} for row in rows]


def row(**values: str) -> dict[str, str]:
    return {field: values.get(field, "") for field in LEDGER_FIELDS}


def map_sf(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    mapped = []
    for item in rows:
        mapped.append(row(
            phase="6SF",
            record_id=item["id"],
            surface=item["subject"],
            source_path=item["source"],
            source_sha256=item["source_sha256"],
            entry_or_node=item["relation"],
            caller_or_identity="holder_or_grant=" + item["holder_or_grant"] + "; caller=" + item["caller"],
            gate_or_policy="service_permission=" + item["service_permission"] + "; observed=" + item["observed"],
            sink_or_effect=item["sink"],
            low_privilege_reachability="requested=" + item["requested"] + "; granted=" + item["granted"],
            classification=item["status"],
            confidence=item["confidence"],
            unknowns=item["notes"],
            safety_disposition="HOST_ONLY; no ADB, Binder, package-state, driver, OTA or recovery mutation",
        ))
    return mapped


def map_sg(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    mapped = []
    for number, item in enumerate(rows, 1):
        mapped.append(row(
            phase="6SG",
            record_id=f"6SG-{number:03d}",
            surface=item["target"],
            source_path=item["evidence"],
            source_sha256="NOT_RECORDED_IN_WORKER_ROW",
            entry_or_node=item["target"],
            caller_or_identity=item["exact_native_open_ioctl_caller"],
            gate_or_policy=item["file_context_selinux"],
            sink_or_effect=item["effect"],
            low_privilege_reachability="exact source→config→policy→native-client join not closed",
            classification=item["status"],
            confidence=item["confidence"],
            unknowns=item["source_config"] + "; shipped_owner_mode=" + item["shipped_owner_mode"],
            safety_disposition="HOST_ONLY; no node open, ioctl, proc write, Binder or diagnostic operation",
        ))
    return mapped


def map_sh(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    mapped = []
    for item in rows:
        mapped.append(row(
            phase="6SH",
            record_id=item["evidence_id"],
            surface=item["question"],
            source_path=item["source"],
            source_sha256=item["sha256_or_note"] if len(item["sha256_or_note"]) == 64 else "NOT_RECORDED_IN_WORKER_ROW",
            entry_or_node=item["result"],
            caller_or_identity=item["result"],
            gate_or_policy=item["status"],
            sink_or_effect=item["result"],
            low_privilege_reachability="not established" if item["status"] != "CONFIRMED" else "see source boundary",
            classification=item["status"],
            confidence=item["confidence"],
            unknowns=item["sha256_or_note"],
            safety_disposition="HOST_ONLY; no OTA, recovery, updater, reboot or partition write",
        ))
    return mapped


def map_si(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    mapped = []
    for item in rows:
        mapped.append(row(
            phase="6SI",
            record_id=item["test id"],
            surface=item["scope"],
            source_path=item["evidence path/hash"],
            source_sha256="SEE_EVIDENCE_PATH_HASH_COLUMN",
            entry_or_node=item["command class"],
            caller_or_identity="catalog classification=" + item["classification"],
            gate_or_policy="device mutation=" + item["device mutation"],
            sink_or_effect=item["result"],
            low_privilege_reachability="not a new reachability assertion",
            classification=item["classification"],
            confidence="CATALOG_ONLY",
            unknowns=item["next safe action"],
            safety_disposition="HOST_ONLY catalog; no new device action",
        ))
    return mapped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true", help="validate inputs and print the plan without writing output")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "output/tables/phase6sf-si-control-surface.csv"

    inputs = {
        "6SF": root / "work/luna_worker_phase6sf_permission_20260810.csv",
        "6SG": root / "work/luna_worker_phase6sg_driver_join_20260810.csv",
        "6SH": root / "work/luna_worker_phase6sh_recovery_20260810.csv",
        "6SI": root / "work/luna_worker_phase6si_test_catalog_20260810.csv",
    }
    mapped = []
    for phase, path in inputs.items():
        if not path.is_file():
            raise FileNotFoundError(path)
    if args.dry_run:
        print("dry-run: no files will be written")
        for phase, path in inputs.items():
            print(f"{phase}: {path}")
        print(f"output: {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)

    for phase, path in inputs.items():
        rows = read_rows(path)
        if phase == "6SF":
            mapped.extend(map_sf(rows))
        elif phase == "6SG":
            mapped.extend(map_sg(rows))
        elif phase == "6SH":
            mapped.extend(map_sh(rows))
        else:
            mapped.extend(map_si(rows))

    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=LEDGER_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(mapped)

    manifest = output.with_name("phase6sf-si-input-manifest.sha256")
    with manifest.open("w", encoding="utf-8") as stream:
        stream.write("schema=phase6sf-si-input-manifest-v1\n")
        stream.write(f"output={output.relative_to(root)}\n")
        stream.write(f"output_sha256={sha256(output)}\n")
        for phase, path in inputs.items():
            stream.write(f"{phase}\t{path.relative_to(root)}\t{sha256(path)}\n")
        stream.write(f"row_count={len(mapped)}\n")
    print(f"wrote {output} rows={len(mapped)} sha256={sha256(output)}")
    print(f"wrote {manifest} sha256={sha256(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
