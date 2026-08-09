#!/usr/bin/env python3
"""Capture a read-only inventory for package-management permission holders.

The script deliberately performs only ADB queries.  It never starts an
activity, sends a broadcast, invokes a Binder transaction, changes package
state, changes settings, reboots, or touches an OTA/partition.  Existing
output directories are never overwritten.
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
        ("build_properties", ["adb", "-s", args.serial, "shell", "getprop"]),
        ("package_list_f", ["adb", "-s", args.serial, "shell", "pm", "list", "packages", "-f"]),
        ("package_dump", ["adb", "-s", args.serial, "shell", "dumpsys", "package"]),
        ("permission_definitions", ["adb", "-s", args.serial, "shell", "dumpsys", "package", "permissions"]),
        ("home_resolve", ["adb", "-s", args.serial, "shell", "cmd", "package", "resolve-activity", "--brief", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"]),
        ("home_candidates", ["adb", "-s", args.serial, "shell", "cmd", "package", "query-activities", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"]),
        ("preferred_activities", ["adb", "-s", args.serial, "shell", "dumpsys", "package", "preferred-activities"]),
        ("activity_state", ["adb", "-s", args.serial, "shell", "dumpsys", "activity", "activities"]),
        ("users", ["adb", "-s", args.serial, "shell", "pm", "list", "users"]),
    ]

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "serial": args.serial,
            "output": str(args.output),
            "commands": [{"id": name, "argv": argv, "command": shlex.join(argv)} for name, argv in commands],
        }, indent=2))
        return 0

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)
    generated = datetime.now(timezone.utc).isoformat()
    manifest_rows: list[dict[str, object]] = []
    for name, argv in commands:
        result = subprocess.run(argv, check=False, capture_output=True)
        stdout_path = args.output / f"{safe_name(name)}.stdout.txt"
        stderr_path = args.output / f"{safe_name(name)}.stderr.txt"
        stdout_path.write_bytes(result.stdout)
        stderr_path.write_bytes(result.stderr)
        manifest_rows.append({
            "id": name,
            "argv": argv,
            "command": shlex.join(argv),
            "returncode": result.returncode,
            "stdout": str(stdout_path.relative_to(args.output)),
            "stderr": str(stderr_path.relative_to(args.output)),
            "stdout_sha256": sha256(stdout_path),
            "stderr_sha256": sha256(stderr_path),
        })

    metadata = {
        "phase": "6MC",
        "purpose": "read-only package-management permission-holder inventory",
        "device_serial": args.serial,
        "generated_at_utc": generated,
        "mutating_commands": False,
        "activities_started": False,
        "broadcasts_sent": False,
        "binder_transactions_invoked": False,
        "settings_changed": False,
        "package_state_changed": False,
        "rebooted": False,
        "commands": manifest_rows,
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in files),
        encoding="utf-8",
    )
    print(f"captured {len(commands)} read-only commands in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
