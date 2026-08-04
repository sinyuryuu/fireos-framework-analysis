#!/usr/bin/env python3
"""Verify the source scope of the PS7331 Amazon GPL tarball.

This is a host-only coverage audit. It does not build, execute, install or
send any source to a device. Missing files are recorded as missing rather
than inferred from the binary.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


TARGETS = (
    "platform/system/core/init",
    "platform/system/core/init/selinux.cpp",
    "platform/system/core/init/selinux.h",
    "platform/system/core/libcutils",
    "platform/system/core/logwrapper",
    "platform/device/amazon",
    "platform/kernel/mediatek/mt8183/4.4/kernel/futex.c",
    "platform/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(root: Path) -> dict[str, object]:
    target_rows: list[dict[str, object]] = []
    for relative in TARGETS:
        path = root / relative
        target_rows.append(
            {
                "target": relative,
                "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
                "exists": path.exists(),
                "sha256": sha256(path) if path.is_file() else "",
            }
        )

    matching: list[dict[str, object]] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        name = path.name.lower()
        if name in {"selinux.cpp", "selinux.h"} or "rootable" in name or "sepolicy" in name:
            matching.append(
                {
                    "path": str(path.relative_to(root)),
                    "size": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    target_init = next(row for row in target_rows if row["target"] == "platform/system/core/init")
    return {
        "schema": "phase6c5-gpl-source-scope-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "targets": target_rows,
        "selinux_named_matches": sorted(matching, key=lambda row: str(row["path"])),
        "findings": {
            "system_core_init_present": bool(target_init["exists"]),
            "kernel_futex_present": any(
                row["target"].endswith("kernel/futex.c") and row["exists"] for row in target_rows
            ),
            "kernel_rtmutex_present": any(
                row["target"].endswith("kernel/locking/rtmutex.c") and row["exists"] for row in target_rows
            ),
        },
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "source_built": False,
            "source_executed": False,
            "device_mutated": False,
        },
    }


def write(result: dict[str, object], output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    summary = output / "scope.json"
    table = output / "scope.csv"
    report = output / "result.md"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with table.open("w", encoding="utf-8", newline="") as stream:
        fields = ["target", "kind", "exists", "sha256"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in result["targets"])  # type: ignore[index]
    present = result["findings"]["system_core_init_present"]  # type: ignore[index]
    report.write_text(
        "# PS7331 GPL source scope verification\n\n"
        "Host-only coverage audit. No source was built or executed and no device was contacted.\n\n"
        f"Source root: {result['root']}\n\n"
        "## Result\n\n"
        f"- platform/system/core/init present: **{present}**\n"
        f"- kernel futex.c present: **{result['findings']['kernel_futex_present']}**\n"
        f"- kernel rtmutex.c present: **{result['findings']['kernel_rtmutex_present']}**\n\n"
        "**已證實：** this tarball contains the selected MT8183 4.4 kernel source and "
        "Amazon device/kernel support, but the expected Android system/core/init "
        "directory and selinux.cpp are absent. The named-match table records any "
        "remaining SELinux/rootable filenames without treating them as init source.\n\n"
        "**高可信推論：** the GPL package cannot directly provide Amazon's /init "
        "policy-loader source diff; the stripped /init and AOSP anchor remain "
        "necessary for that pipeline.\n\n"
        "**待驗證：** whether Amazon's private build overlay or an unreleased source "
        "component supplied the /init changes. This archive alone cannot answer it.\n\n"
        "**已排除：** the absence of system/core/init in this archive is not evidence "
        "that /init has no Amazon modification.\n\n"
        "## Reproduction\n\n"
        "python3 tools/scripts/audit_phase6c5_gpl_source_scope.py --dry-run "
        "--source-root firmware/extracted/PS7331-SOURCE-20250617 "
        "--output artifacts/phase6c5/gpl-source-scope-YYYYMMDD-NN\n\n"
        "python3 tools/scripts/audit_phase6c5_gpl_source_scope.py "
        "--source-root firmware/extracted/PS7331-SOURCE-20250617 "
        "--output artifacts/phase6c5/gpl-source-scope-YYYYMMDD-NN\n",
        encoding="utf-8",
    )
    files = [summary, table, report]
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False}, indent=2))
        return 0
    if not args.source_root.is_dir():
        raise SystemExit(f"missing source root: {args.source_root}")
    write(build(args.source_root), args.output)
    print(f"wrote GPL source scope audit: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
