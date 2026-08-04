#!/usr/bin/env python3
"""Build a host-only provenance ledger for PS7330/PS7331 low-level artifacts.

The ledger records availability and version scope. It never invokes adb,
fastboot, a bootloader, an OTA updater, or any device-node operation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def entries(repo: Path) -> list[dict[str, object]]:
    records = [
        {
            "id": "P5BM-PS7330-RUNTIME",
            "version": "PS7330.4104N",
            "artifact": "device runtime properties",
            "path": "device/baseline/BASELINE-20260803-05/device_properties.txt",
            "relation": "EXACT_DEVICE_RUNTIME",
            "status": "AVAILABLE",
            "exact_signed_binary": False,
            "usable_for_offset_proof": False,
            "evidence": "runtime identity only",
        },
        {
            "id": "P5BM-PS7330-SOURCE",
            "version": "PS7330.4104N",
            "artifact": "Amazon source member metadata / rtmutex.c hash",
            "path": "artifacts/phase5/exact-kernel-source-review-20260804-02/metadata.tsv",
            "relation": "EXACT_SOURCE_FAMILY",
            "status": "AVAILABLE",
            "exact_signed_binary": False,
            "usable_for_offset_proof": False,
            "evidence": "source-level only; rtmutex member hash recorded",
        },
        {
            "id": "P5BM-PS7330-BOOT-PROBE",
            "version": "PS7330.4104N",
            "artifact": "installed boot partition read probe",
            "path": "adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/boot_pull.stderr.txt",
            "relation": "EXACT_DEVICE_READ_PROBE",
            "status": "ACCESS_DENIED",
            "exact_signed_binary": False,
            "usable_for_offset_proof": False,
            "evidence": "shell pull returned Permission denied",
        },
        {
            "id": "P5BM-PS7330-VMLINUX",
            "version": "PS7330.4104N",
            "artifact": "signed vmlinux / boot Image",
            "path": None,
            "relation": "EXACT_SIGNED_BINARY",
            "status": "NOT_PRESENT_IN_WORKSPACE",
            "exact_signed_binary": False,
            "usable_for_offset_proof": False,
            "evidence": "no verified exact file located",
        },
        {
            "id": "P5BM-PS7330-BOOTCHAIN",
            "version": "PS7330.4104N",
            "artifact": "preloader / LK / recovery set",
            "path": None,
            "relation": "EXACT_BOOTCHAIN_SET",
            "status": "NOT_PRESENT_IN_WORKSPACE",
            "exact_signed_binary": False,
            "usable_for_offset_proof": False,
            "evidence": "no verified exact set located",
        },
        {
            "id": "P5BM-PS7331-OTA",
            "version": "PS7331.4463N",
            "artifact": "official full OTA",
            "path": "firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin",
            "relation": "ADJACENT_VERSION",
            "status": "AVAILABLE_VERSION_MISMATCH",
            "known_sha256": "9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5",
            "exact_signed_binary": False,
            "usable_for_offset_proof": False,
            "evidence": "full-block OTA; not installed PS7330",
        },
        {
            "id": "P5BM-PS7331-BOOT",
            "version": "PS7331.4463N",
            "artifact": "boot.img from official OTA",
            "path": "firmware/extracted/PS7331/boot.img",
            "relation": "ADJACENT_VERSION",
            "status": "AVAILABLE_VERSION_MISMATCH",
            "known_sha256": "cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b",
            "exact_signed_binary": False,
            "usable_for_offset_proof": False,
            "evidence": "host-only adjacent Image reference",
        },
        {
            "id": "P5BM-PS7331-RTMUTEX-SOURCE",
            "version": "PS7331.4463N",
            "artifact": "build-selected rtmutex.c",
            "path": "artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c",
            "relation": "ADJACENT_VERSION_SOURCE",
            "status": "AVAILABLE_VERSION_MISMATCH",
            "known_sha256": "6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde",
            "exact_signed_binary": False,
            "usable_for_offset_proof": False,
            "evidence": "source/Image semantic comparison only",
        },
    ]
    for record in records:
        path_text = record.get("path")
        if path_text:
            path = repo / str(path_text)
            record["path_exists"] = path.is_file()
            if path.is_file() and path.stat().st_size <= 128 * 1024 * 1024:
                record["observed_sha256"] = sha256(path)
        else:
            record["path_exists"] = False
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print("DRY-RUN: no files will be read or written.")
        print(f"REPO\t{args.repo}")
        print(f"OUTPUT\t{args.output}")
        return 0
    if args.output.exists():
        print(f"ERROR: output already exists: {args.output}", file=sys.stderr)
        return 2
    if not args.repo.is_dir():
        print("ERROR: repository directory missing", file=sys.stderr)
        return 2
    args.output.mkdir(parents=True)
    rows = entries(args.repo)
    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_io": False,
        "purpose": "PS7330/PS7331 low-level artifact provenance",
        "records": rows,
    }
    (args.output / "ledger.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    fields = [
        "id", "version", "artifact", "path", "relation", "status", "path_exists",
        "known_sha256", "observed_sha256", "exact_signed_binary",
        "usable_for_offset_proof", "evidence",
    ]
    with (args.output / "ledger.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote host-only artifact ledger to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
