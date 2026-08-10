#!/usr/bin/env python3
"""Normalize the Phase 6SJ–SM worker ledgers without contacting a device."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


FIELDS = [
    "phase", "record_id", "surface", "source_path", "source_sha256",
    "entry_or_node", "caller_or_identity", "gate_or_policy", "sink_or_effect",
    "low_privilege_reachability", "classification", "confidence", "unknowns",
    "safety_disposition",
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    return [{k: v or "" for k, v in row.items()} for row in rows]


def make(phase: str, record_id: str, **values: str) -> dict[str, str]:
    item = {field: "" for field in FIELDS}
    item.update(phase=phase, record_id=record_id, **values)
    return item


def map_sj(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [make(
        "6SJ", r["row_id"],
        surface=f"{r['area']}:{r['subject']}",
        source_path=r["source_path"], source_sha256=r["source_sha256"],
        entry_or_node=r["subject"], caller_or_identity=r["caller_or_holder"],
        gate_or_policy=r["edge_or_finding"], sink_or_effect=r["edge_or_finding"],
        low_privilege_reachability=r["caller_or_holder"], classification=r["status"],
        confidence=r["confidence"],
        unknowns=(
            "worker_locator=" + r["line_range"] + "; verified_locator=1822-1824"
            if r["row_id"] == "SJ-01" else r["line_range"]
        ),
        safety_disposition="HOST_ONLY; no adb/Binder/device mutation",
    ) for r in rows]


def map_sk(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [make(
        "6SK", r["evidence_id"], surface=r["scope"],
        source_path=r["source_path"], source_sha256="NOT_RECORDED_IN_CSV",
        entry_or_node=r["edge_or_control"], caller_or_identity=r["observation"],
        gate_or_policy=r["classification"], sink_or_effect=r["observation"],
        low_privilege_reachability="not established in bounded corpus",
        classification=r["classification"], confidence=r["confidence"],
        unknowns=r["source_locator"] + "; version=" + r["version_boundary"],
        safety_disposition="HOST_ONLY; no OTA/recovery/reboot/partition write",
    ) for r in rows]


def map_sl(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    result = []
    for index, r in enumerate(rows, 1):
        result.append(make(
            "6SL", f"6SL-{index:03d}", surface=r["surface"],
            source_path=r["source_config"], source_sha256="NOT_RECORDED_IN_CSV",
            entry_or_node=r["surface"], caller_or_identity=r["exact_caller"],
            gate_or_policy=r["policy_init"], sink_or_effect=r["result"],
            low_privilege_reachability="exact native caller not closed",
            classification=r["result"], confidence="UNKNOWN",
            unknowns=r["evidence_gap"] + "; shipped_node=" + r["shipped_node"],
            safety_disposition="HOST_ONLY; no node open/ioctl/proc write/adb",
        ))
    return result


def map_sm(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    result = []
    for r in rows:
        result.append(make(
            "6SM", r["test_id"], surface=r["phase_scope"],
            source_path=r["primary_evidence_path"], source_sha256=r["primary_sha256"],
            entry_or_node=r["evidence_kind"], caller_or_identity=r["classification"],
            gate_or_policy=r["mutation_or_boundary"], sink_or_effect=r["current_result"],
            low_privilege_reachability="catalog boundary; no new reachability claim",
            classification=r["classification"], confidence="CATALOG_ONLY",
            unknowns=r["missing_evidence"],
            safety_disposition="HOST_ONLY catalog; no new device action",
        ))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true", help="validate inputs without writing output")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "output/tables/phase6sj-sm-control-surface.csv"
    inputs = {
        "6SJ": root / "work/luna_worker_phase6sj_ipc_permission_20260810.csv",
        "6SK": root / "work/luna_worker_phase6sk_ota_recovery_20260810.csv",
        "6SL": root / "work/luna_worker_phase6sl_driver_callers_20260810.csv",
        "6SM": root / "work/luna_worker_phase6sm_test_catalog_20260810.csv",
    }
    for path in inputs.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    if args.dry_run:
        print("dry-run: no files will be written")
        for phase, path in inputs.items():
            print(f"{phase}: {path}")
        print(f"output: {output}")
        return 0

    rows = []
    rows.extend(map_sj(read_csv(inputs["6SJ"])))
    rows.extend(map_sk(read_csv(inputs["6SK"])))
    rows.extend(map_sl(read_csv(inputs["6SL"])))
    rows.extend(map_sm(read_csv(inputs["6SM"])))
    ids = [r["record_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate normalized record ID")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    manifest = output.with_name("phase6sj-sm-input-manifest.sha256")
    with manifest.open("w", encoding="utf-8") as stream:
        stream.write("schema=phase6sj-sm-input-manifest-v1\n")
        stream.write(f"output={output.relative_to(root)}\n")
        stream.write(f"output_sha256={digest(output)}\n")
        for phase, path in inputs.items():
            stream.write(f"{phase}\t{path.relative_to(root)}\t{digest(path)}\n")
        stream.write(f"row_count={len(rows)}\n")
    print(f"wrote {output} rows={len(rows)} sha256={digest(output)}")
    print(f"wrote {manifest} sha256={digest(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
