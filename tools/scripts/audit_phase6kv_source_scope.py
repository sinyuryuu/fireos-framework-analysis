#!/usr/bin/env python3
"""Build a host-only PS7331 GPL source-scope and provenance manifest.

The script hashes preserved archives/files and checks a small, explicit set of
paths.  It does not unpack archives, invoke a build, execute source code, or
touch a device.  Absence is reported only for the exact searched paths/patterns.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_record(root: Path, relative: str) -> Dict[str, object]:
    path = root / relative
    record: Dict[str, object] = {"path": relative, "exists": path.is_file()}
    if path.is_file():
        record.update({"size": path.stat().st_size, "sha256": sha256(path)})
    return record


def count_files(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file()) if path.is_dir() else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    source = root / "firmware/extracted/PS7331-SOURCE-20250617"
    output = (args.output_dir or root / "artifacts/phase6kv/source-scope-20260810-01").resolve()
    output.mkdir(parents=True, exist_ok=True)

    archive_paths = [
        "firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2",
        "firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2",
        "firmware/extracted/PS7331-SOURCE-20250617/platform.tar",
        "firmware/extracted/PS7331-SOURCE-20250617/fireos.tar",
    ]
    source_paths = [
        "platform/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig",
        "platform/kernel/mediatek/mt8183/4.4/arch/arm64/boot/dts/mediatek/trona_evt.dts",
        "platform/system/core/init/selinux.cpp",
    ]
    driver_paths = [
        "platform/device/amazon/kernel/driver/amzn_idme.c",
        "platform/device/amazon/kernel/driver/amzn_logger.c",
        "platform/device/amazon/kernel/driver/amzn_keycombo.c",
    ]
    records = {
        "archives": [file_record(root, item) for item in archive_paths],
        "source_paths": [file_record(source, item) for item in source_paths],
        "amazon_driver_paths": [file_record(source, item) for item in driver_paths],
        "directory_counts": {
            "platform_kernel_mt8183_4_4_files": count_files(source / "platform/kernel/mediatek/mt8183/4.4"),
            "platform_vendor_mediatek_files": count_files(source / "platform/vendor/mediatek"),
            "amazon_driver_files": count_files(source / "platform/device/amazon/kernel/driver"),
        },
        "rootable_policy_matches": sorted(
            str(item.relative_to(source))
            for item in source.rglob("*")
            if item.is_file() and "rootable_" in item.name and item.name.endswith("_sepolicy.cil")
        ),
    }
    records["scope_limit"] = (
        "The manifest checks exact paths and an exact filename pattern. It does not prove that an absent path is dead code, "
        "that an artifact is loaded, or that any policy/driver is exploitable."
    )
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(records, indent=2) + "\n")

    rows: List[Dict[str, str]] = []
    for group in ("archives", "source_paths", "amazon_driver_paths"):
        for record in records[group]:
            rows.append(
                {
                    "group": group,
                    "path": str(record["path"]),
                    "exists": str(record["exists"]),
                    "size": str(record.get("size", "")),
                    "sha256": str(record.get("sha256", "")),
                }
            )
    table_path = root / "output/tables/phase6kv-source-scope.csv"
    table_path.parent.mkdir(parents=True, exist_ok=True)
    with table_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["group", "path", "exists", "size", "sha256"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"manifest": str(manifest_path), "table": str(table_path), "records": records}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
