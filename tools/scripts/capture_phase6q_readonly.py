#!/usr/bin/env python3
"""Capture a canonical, read-only Phase 6Q device evidence set.

The target serial is mandatory because more than one Android device may be
connected.  The command list contains only queries and dumps: it does not
start an activity, send a broadcast, obtain or transact on a Binder service,
change settings, mutate package state, clear logcat, reboot, or touch OTA
artifacts.  Existing output directories are never overwritten.
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


def run(argv: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(argv, check=False, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    adb = ["adb", "-s", args.serial]
    commands: list[tuple[str, list[str]]] = [
        ("adb_devices_l", ["adb", "devices", "-l"]),
        ("target_state", adb + ["get-state"]),
        ("target_id", adb + ["shell", "id"]),
        ("target_selinux", adb + ["shell", "getenforce"]),
        ("target_uname", adb + ["shell", "uname", "-a"]),
        ("build_properties", adb + ["shell", "getprop"]),
        ("firelauncher_path", adb + ["shell", "pm", "path", "com.amazon.firelauncher"]),
        ("firelauncher_package_dump", adb + ["shell", "dumpsys", "package", "com.amazon.firelauncher"]),
        ("ota_package_dump", adb + ["shell", "dumpsys", "package", "com.amazon.device.software.ota"]),
        ("oobe_package_dump", adb + ["shell", "dumpsys", "package", "com.amazon.kindle.otter.oobe"]),
        ("systemui_package_dump", adb + ["shell", "dumpsys", "package", "com.android.systemui"]),
        ("settings_package_dump", adb + ["shell", "dumpsys", "package", "com.android.settings"]),
        ("all_package_paths", adb + ["shell", "pm", "list", "packages", "-f"]),
        ("home_resolve", adb + [
            "shell", "cmd", "package", "resolve-activity", "--brief",
            "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME",
        ]),
        ("home_candidates_cmd", adb + [
            "shell", "cmd", "package", "query-activities",
            "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME",
        ]),
        ("home_candidates_pm", adb + [
            "shell", "pm", "query-activities",
            "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME",
        ]),
        ("preferred_activities", adb + ["shell", "dumpsys", "package", "preferred-activities"]),
        ("preferred_xml", adb + ["shell", "dumpsys", "package", "preferred-xml"]),
        ("package_dump_full", adb + ["shell", "dumpsys", "package"]),
        ("activity_activities", adb + ["shell", "dumpsys", "activity", "activities"]),
        ("activity_recents", adb + ["shell", "dumpsys", "activity", "recents"]),
        ("activity_top", adb + ["shell", "dumpsys", "activity", "top"]),
        ("window_windows", adb + ["shell", "dumpsys", "window", "windows"]),
        ("role_dump", adb + ["shell", "dumpsys", "role"]),
        ("device_policy_dump", adb + ["shell", "dumpsys", "device_policy"]),
        ("overlay_list", adb + ["shell", "cmd", "overlay", "list"]),
        ("appops_firelauncher", adb + ["shell", "appops", "get", "com.amazon.firelauncher"]),
        ("users_pm", adb + ["shell", "pm", "list", "users"]),
        ("users_cmd", adb + ["shell", "cmd", "user", "list"]),
        ("service_list", adb + ["shell", "service", "list"]),
        ("logcat_all_dump", adb + ["logcat", "-b", "all", "-d", "-v", "threadtime"]),
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

    # Fail closed if the explicitly requested serial is not in the normal
    # online state.  A second connected device is harmless because every
    # device query below is explicitly addressed with -s.
    devices = run(["adb", "devices"])
    device_lines = devices.stdout.decode("utf-8", errors="replace").splitlines()
    target_line = next((line for line in device_lines if line.startswith(args.serial + "\t")), None)
    if target_line is None or "\tdevice" not in target_line:
        raise SystemExit(f"refusing device access: requested serial is not online as 'device': {args.serial!r}")

    args.output.mkdir(parents=True)
    generated = datetime.now(timezone.utc).isoformat()
    manifest_rows: list[dict[str, object]] = []
    for name, argv in commands:
        stem = safe_name(name)
        result = run(argv)
        stdout_path = args.output / f"{stem}.stdout.txt"
        stderr_path = args.output / f"{stem}.stderr.txt"
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

    build_text = (args.output / "build_properties.stdout.txt").read_text(encoding="utf-8", errors="replace")
    fingerprint = next((line.split("]:", 1)[1].strip() for line in build_text.splitlines()
                        if line.startswith("[ro.build.fingerprint]:")), "NOT_OBSERVED")
    metadata = {
        "phase": "6Q",
        "purpose": "fresh canonical read-only baseline for Amazon Binder/OOBE/OTA static follow-up",
        "device_serial": args.serial,
        "build_fingerprint_observed": fingerprint,
        "generated_at_utc": generated,
        "host_script": str(Path(__file__).resolve()),
        "mutating_commands": False,
        "binder_transactions_invoked": False,
        "intents_or_broadcasts_sent": False,
        "settings_changed": False,
        "package_state_changed": False,
        "logcat_cleared": False,
        "reboot_requested": False,
        "partition_written": False,
        "commands": manifest_rows,
        "limitations": [
            "A failed or unsupported read-only command is retained with its exit code and stderr.",
            "A service listed by service list is not proof that shell may obtain or transact on it.",
            "No OOBE/OTA lifecycle broadcast was manually triggered.",
            "No unknown Binder transaction or private API was invoked.",
        ],
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(args.output),
        "serial": args.serial,
        "command_count": len(commands),
        "build_fingerprint": fingerprint,
        "mutating_commands": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
