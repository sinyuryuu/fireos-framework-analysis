#!/usr/bin/env python3
"""Capture KFT preconditions without invoking the KFT path.

This is deliberately read-only.  It records user/profile state, service
visibility, launcher state, HOME resolution, and policy state.  It never sends
a Binder transaction, creates/removes a user, starts an activity, changes a
package/setting, sends an OTA/OOBE event, or reboots the device.
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

    adb = ["adb", "-s", args.serial]
    commands = [
        ("adb_devices_l", ["adb", "devices", "-l"]),
        ("target_state", adb + ["get-state"]),
        ("build_fingerprint", adb + ["shell", "getprop", "ro.build.fingerprint"]),
        ("build_incremental", adb + ["shell", "getprop", "ro.build.version.incremental"]),
        ("security_patch", adb + ["shell", "getprop", "ro.build.version.security_patch"]),
        ("target_id", adb + ["shell", "id"]),
        ("selinux", adb + ["shell", "getenforce"]),
        ("users_list", adb + ["shell", "cmd", "user", "list"]),
        ("users_dump", adb + ["shell", "dumpsys", "user"]),
        ("device_policy", adb + ["shell", "dumpsys", "device_policy"]),
        ("amazon_user_manager_check", adb + ["shell", "service", "check", "amazonusermanagerservice"]),
        ("service_list", adb + ["shell", "service", "list"]),
        ("home_resolve", adb + ["shell", "cmd", "package", "resolve-activity", "--brief", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"]),
        ("home_candidates", adb + ["shell", "cmd", "package", "query-activities", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"]),
        ("preferred_activities", adb + ["shell", "dumpsys", "package", "preferred-activities"]),
        ("firelauncher_package", adb + ["shell", "dumpsys", "package", "com.amazon.firelauncher"]),
        ("tahoe_package", adb + ["shell", "dumpsys", "package", "com.amazon.tahoe"]),
        ("activity_state", adb + ["shell", "dumpsys", "activity", "activities"]),
        ("window_state", adb + ["shell", "dumpsys", "window", "windows"]),
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
    rows = []
    for name, argv in commands:
        result = subprocess.run(argv, check=False, capture_output=True)
        stdout = args.output / f"{safe_name(name)}.stdout.txt"
        stderr = args.output / f"{safe_name(name)}.stderr.txt"
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        rows.append({
            "id": name,
            "argv": argv,
            "command": shlex.join(argv),
            "returncode": result.returncode,
            "stdout": stdout.name,
            "stderr": stderr.name,
            "stdout_sha256": sha256(stdout),
            "stderr_sha256": sha256(stderr),
        })

    metadata = {
        "schema": 1,
        "phase": "KFT-PREFLIGHT",
        "device_serial": args.serial,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mutating_commands": False,
        "binder_transactions_invoked": False,
        "users_created_or_removed": False,
        "package_state_changed": False,
        "settings_changed": False,
        "activities_started": False,
        "ota_or_oobe_triggered": False,
        "reboot_requested": False,
        "commands": rows,
        "purpose": "Determine whether a safe, isolated KFT test user and service route exist before any state-changing experiment.",
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
