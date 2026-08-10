#!/usr/bin/env python3
"""Capture current, read-only provenance for the Play Store permission holder.

This script deliberately performs no package install/start/stop, Binder
transaction, permission grant/revoke, package-state mutation, settings write,
reboot, OTA, or partition operation. It refuses to overwrite an evidence
directory and requires an explicit device serial.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    commands = [
        ("adb_devices_l", ["adb", "devices", "-l"]),
        ("target_state", ["adb", "-s", args.serial, "get-state"]),
        ("target_id", ["adb", "-s", args.serial, "shell", "id"]),
        ("getenforce", ["adb", "-s", args.serial, "shell", "getenforce"]),
        ("fingerprint", ["adb", "-s", args.serial, "shell", "getprop", "ro.build.fingerprint"]),
        ("vending_path", ["adb", "-s", args.serial, "shell", "pm", "path", "com.android.vending"]),
        ("vending_package", ["adb", "-s", args.serial, "shell", "dumpsys", "package", "com.android.vending"]),
        ("permission_definition", ["adb", "-s", args.serial, "shell", "dumpsys", "package", "permissions"]),
        ("home_resolve", ["adb", "-s", args.serial, "shell", "cmd", "package", "resolve-activity", "--brief", "--user", "0", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"]),
        ("home_candidates", ["adb", "-s", args.serial, "shell", "cmd", "package", "query-activities", "--brief", "--user", "0", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"]),
        ("preferred_activities", ["adb", "-s", args.serial, "shell", "dumpsys", "package", "preferred-activities"]),
        ("device_policy", ["adb", "-s", args.serial, "shell", "dumpsys", "device_policy"]),
        ("vending_appops", ["adb", "-s", args.serial, "shell", "appops", "get", "com.android.vending"]),
        ("activity_top", ["adb", "-s", args.serial, "shell", "dumpsys", "activity", "top"]),
    ]

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "serial": args.serial,
            "output": str(args.output),
            "mutating_commands": False,
            "commands": [{"id": name, "argv": argv, "command": shlex.join(argv)} for name, argv in commands],
        }, indent=2))
        return 0

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)
    generated = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, object]] = []
    for name, argv in commands:
        result = subprocess.run(argv, check=False, capture_output=True)
        stdout_path = args.output / f"{safe_name(name)}.stdout.txt"
        stderr_path = args.output / f"{safe_name(name)}.stderr.txt"
        stdout_path.write_bytes(result.stdout)
        stderr_path.write_bytes(result.stderr)
        rows.append({
            "id": name,
            "argv": argv,
            "command": shlex.join(argv),
            "returncode": result.returncode,
            "stdout": stdout_path.name,
            "stderr": stderr_path.name,
            "stdout_sha256": sha256(stdout_path),
            "stderr_sha256": sha256(stderr_path),
        })

    metadata = {
        "phase": "6PR-VENDING",
        "purpose": "current read-only permission-holder provenance capture",
        "device_serial": args.serial,
        "generated_at_utc": generated,
        "mutating_commands": False,
        "binder_transactions_invoked": False,
        "package_state_changed": False,
        "settings_changed": False,
        "rebooted": False,
        "ota_or_partition_operation": False,
        "commands": rows,
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps({"evidence": str(args.output), "command_count": len(commands)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
