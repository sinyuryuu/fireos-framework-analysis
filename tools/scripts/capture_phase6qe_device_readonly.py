#!/usr/bin/env python3
"""Capture a serial-bound, metadata-only Phase 6QE device snapshot.

This script intentionally does not open driver nodes, read proc driver files,
send Binder transactions, mutate package/settings state, reboot, or execute an
OTA/recovery/root operation.  The node checks use ls/stat metadata only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


SERIAL = "G001LT0511550CFT"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run_adb(serial: str, shell_args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["adb", "-s", serial, "shell", *shell_args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_adb_host(serial: str, args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["adb", "-s", serial, *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.serial != SERIAL:
        raise SystemExit(f"refusing unexpected serial: {args.serial!r}")

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    commands = [
        ("adb_state", ["get-state"]),
        ("target_id", ["id"]),
        ("build_properties", ["getprop"]),
        ("selinux", ["getenforce"]),
        ("home_resolve", ["cmd", "package", "resolve-activity", "--brief", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"]),
        ("home_candidates", ["cmd", "package", "query-activities", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"]),
        ("package_state", ["dumpsys", "package", "com.amazon.firelauncher"]),
        ("preferred", ["dumpsys", "package", "preferred-activities"]),
        ("activity_top", ["dumpsys", "activity", "top"]),
        ("service_list", ["service", "list"]),
        ("node_metadata", ["ls", "-lZ", "/dev/mtk_cmdq", "/dev/m4u", "/dev/M4U_device", "/dev/gsensor", "/proc/m4u", "/proc/perfmgr/perf_ioctl", "/proc/amzn_drvs", "/proc/life_cycle_reason"]),
        ("mounts", ["cat", "/proc/mounts"]),
    ]

    metadata = {
        "schema": "phase6qe-device-readonly-v1",
        "serial": args.serial,
        "captured_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "commands": len(commands),
        "read_only": True,
        "device_nodes_opened": False,
        "driver_data_read": False,
        "binder_transactions_invoked": False,
        "settings_or_package_mutation": False,
        "reboot": False,
        "ota_or_recovery": False,
        "root_or_exploit": False,
    }
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    for name, shell_args in commands:
        if name == "adb_state":
            rc, stdout, stderr = run_adb_host(args.serial, shell_args)
        else:
            rc, stdout, stderr = run_adb(args.serial, shell_args)
        (out / f"{name}.stdout.txt").write_text(stdout)
        (out / f"{name}.stderr.txt").write_text(stderr)
        (out / f"{name}.rc.txt").write_text(f"{rc}\n")

    files = sorted(p for p in out.iterdir() if p.is_file() and p.name != "sha256sums.txt")
    lines = [f"{sha256(p)}  {p.name}" for p in files]
    (out / "sha256sums.txt").write_text("\n".join(lines) + "\n")
    print(json.dumps(metadata, indent=2))
    print(f"output={out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
