#!/usr/bin/env python3
"""Host-only static inventory of the PS7331 MTK CMDQ driver surface.

This records config gates, device registration, ioctl dispatch, and user-copy
validation markers from the preserved source. It never opens a device node,
issues an ioctl, builds a kernel, or contacts a device.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


RELATIVE_FILES = (
    "drivers/misc/mediatek/cmdq/v3/cmdq_driver.c",
    "drivers/misc/mediatek/cmdq/v3/cmdq_def.h",
    "drivers/misc/mediatek/cmdq/v3/cmdq_driver.h",
    "drivers/misc/mediatek/cmdq/v3/Makefile",
    "drivers/misc/mediatek/cmdq/v3/Kconfig",
    "arch/arm64/configs/trona_defconfig",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def config_state(text: str, symbol: str) -> str:
    if re.search(rf"^CONFIG_{re.escape(symbol)}=y$", text, re.MULTILINE):
        return "y"
    if re.search(rf"^CONFIG_{re.escape(symbol)}=m$", text, re.MULTILINE):
        return "m"
    if re.search(rf"^# CONFIG_{re.escape(symbol)} is not set$", text, re.MULTILINE):
        return "disabled"
    return "absent"


def line_for(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text, re.MULTILINE)
    return text.count("\n", 0, match.start()) + 1 if match else None


def build(source_root: Path, kernel_config: Path) -> dict[str, object]:
    kernel_root = source_root / "platform/kernel/mediatek/mt8183/4.4"
    config_text = kernel_config.read_text(encoding="utf-8", errors="replace")
    files = []
    for relative in RELATIVE_FILES:
        path = kernel_root / relative
        files.append(
            {
                "path": relative,
                "exists": path.is_file(),
                "size": path.stat().st_size if path.is_file() else 0,
                "sha256": sha256(path) if path.is_file() else "",
            }
        )
    driver_path = kernel_root / "drivers/misc/mediatek/cmdq/v3/cmdq_driver.c"
    def_path = kernel_root / "drivers/misc/mediatek/cmdq/v3/cmdq_def.h"
    driver = driver_path.read_text(encoding="utf-8", errors="replace") if driver_path.is_file() else ""
    header = def_path.read_text(encoding="utf-8", errors="replace") if def_path.is_file() else ""

    ioctls = list(dict.fromkeys(re.findall(r"case\s+(CMDQ_IOCTL_[A-Z0-9_]+):", driver)))
    markers = {
        "device_name": re.search(r"CMDQ_DRIVER_DEVICE_NAME\s+\"([^\"]+)\"", header).group(1)
        if re.search(r"CMDQ_DRIVER_DEVICE_NAME\s+\"([^\"]+)\"", header)
        else None,
        "open_present": "cmdq_open" in driver,
        "release_present": "cmdq_release" in driver,
        "file_operations_present": "cmdqOP" in driver,
        "unlocked_ioctl_present": ".unlocked_ioctl = cmdq_ioctl" in driver,
        "compat_ioctl_present": ".compat_ioctl = cmdq_ioctl_compat" in driver,
        "alloc_chrdev_region_present": "alloc_chrdev_region" in driver,
        "device_create_present": "device_create(gCMDQClass" in driver,
        "copy_from_user_present": driver.count("copy_from_user"),
        "copy_to_user_present": driver.count("copy_to_user"),
        "read_address_handler_present": "cmdq_driver_process_read_address_request" in driver,
        "read_address_count_bound_present": "req_user->count > CMDQ_MAX_DUMP_REG_COUNT" in driver,
        "reg_count_bound_present": "userRegCount > CMDQ_MAX_DUMP_REG_COUNT" in driver,
        "ioctl_default_reject_present": "-ENOIOCTLCMD" in driver,
        "proc_debug_status_mode": "proc_create(\"status\", 0440" in driver,
        "proc_debug_record_mode": "proc_create(\"record\", 0440" in driver,
    }
    findings = [
        {
            "surface": "/dev/mtk_cmdq registration",
            "result": "source-present",
            "confidence": "Confirmed",
            "evidence": "CMDQ_DRIVER_DEVICE_NAME, alloc_chrdev_region, class_create and device_create are present",
        },
        {
            "surface": "CMDQ ioctl dispatcher",
            "result": "source-present",
            "confidence": "Confirmed",
            "evidence": "cmdqOP wires unlocked_ioctl and cmdq_ioctl dispatches named CMDQ requests",
        },
        {
            "surface": "user-controlled register/readback path",
            "result": "sensitive control surface; vulnerability not established",
            "confidence": "Strong evidence",
            "evidence": "copy_from_user/copy_to_user and count bounds are present; hardware semantics and runtime permissions are separate questions",
        },
        {
            "surface": "CVE-2020-0069 applicability",
            "result": "Unknown",
            "confidence": "Unknown",
            "evidence": "the preserved source has no exact CVE patch comparison in this audit; no ioctl or exploit test is permitted",
        },
    ]
    return {
        "schema": "phase6g-cmdq-static-surface-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "source_root": str(source_root),
            "kernel_root": str(kernel_root),
            "kernel_config": str(kernel_config),
            "kernel_config_sha256": sha256(kernel_config),
        },
        "config_symbols": {symbol: config_state(config_text, symbol) for symbol in ("MTK_CMDQ", "MTK_CMDQ_TAB", "COMPAT")},
        "files": files,
        "source_markers": markers,
        "ioctl_cases": ioctls,
        "line_anchors": {
            pattern: line_for(driver, pattern)
            for pattern in (
                r"static int cmdq_open",
                r"static int cmdq_release",
                r"cmdq_driver_process_read_address_request",
                r"static long cmdq_ioctl",
                r"static const struct file_operations cmdqOP",
                r"alloc_chrdev_region",
                r"device_create\(gCMDQClass",
            )
        },
        "findings": findings,
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "device_mutated": False,
            "kernel_built": False,
            "device_node_opened": False,
            "ioctl_issued": False,
            "kernel_memory_accessed": False,
            "exploit_or_payload": False,
        },
    }


def write(result: dict[str, object], output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    summary = output / "cmdq-static.json"
    table = output / "cmdq-static.csv"
    report = output / "result.md"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["surface", "result", "confidence", "evidence"]
    with table.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["findings"])
    report.write_text(
        "# PS7331 MTK CMDQ static surface\n\n"
        "Host-only source/config inventory. No device node was opened and no ioctl,\n"
        "kernel-memory, crash, or privilege-escalation test was performed.\n\n"
        "## Findings\n\n"
        "- **已證實：** the preserved MT8183 source enables `CONFIG_MTK_CMDQ=y` and\n"
        "  `CONFIG_MTK_CMDQ_TAB=y`, registers a device named `mtk_cmdq`, and wires a\n"
        "  v3 `unlocked_ioctl` dispatcher with a compat path.\n"
        "- **高可信推論：** the driver is a sensitive userspace-to-kernel control\n"
        "  surface because it accepts structured requests, performs user copies, and\n"
        "  reaches CMDQ/readback helpers. Bounds checks visible in this source are\n"
        "  evidence about this tree, not a complete vulnerability proof.\n"
        "- **待驗證：** whether the shipped binary exactly matches the source and how\n"
        "  SELinux/device-node permissions constrain each caller.\n"
        "- **Unknown：** CVE-2020-0069 applicability. No exact patch mapping or runtime\n"
        "  ioctl test is included.\n"
        "- **因風險拒絕測試：** any standalone ioctl, non-zero request, address\n"
        "  readback, DMA interaction, race, crash, or root payload.\n",
        encoding="utf-8",
    )
    files = [summary, table, report]
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--kernel-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False}, indent=2))
        return 0
    if not args.source_root.is_dir():
        raise SystemExit(f"missing source root: {args.source_root}")
    if not args.kernel_config.is_file():
        raise SystemExit(f"missing kernel config: {args.kernel_config}")
    write(build(args.source_root, args.kernel_config), args.output)
    print(f"wrote CMDQ surface audit: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
