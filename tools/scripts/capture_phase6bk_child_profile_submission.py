#!/usr/bin/env python3
"""Capture the post-submission state of the supported child-profile UI.

This script is read-only.  It does not create, switch, stop, remove, or
provision a user; it does not change package/settings state; and it does not
send a Binder transaction or broadcast.  It is intended to preserve the
device-side evidence after a manual Settings UI attempt.
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
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--lines", type=int, default=800)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    adb = ["adb", "-s", args.serial]
    commands = [
        ("get_state", ["get-state"]),
        ("fingerprint", ["shell", "getprop", "ro.build.fingerprint"]),
        ("current_user", ["shell", "am", "get-current-user"]),
        ("users", ["shell", "pm", "list", "users"]),
        ("user_state", ["shell", "dumpsys", "user"]),
        ("home_user0", [
            "shell", "cmd", "package", "resolve-activity", "--brief",
            "--user", "0", "-a", "android.intent.action.MAIN",
            "-c", "android.intent.category.HOME",
        ]),
        ("firelauncher_package", ["shell", "dumpsys", "package", "com.amazon.firelauncher"]),
        ("tahoe_package", ["shell", "dumpsys", "package", "com.amazon.tahoe"]),
        ("activity_state", ["shell", "dumpsys", "activity", "activities"]),
        ("window_state", ["shell", "dumpsys", "window", "windows"]),
        ("logcat_all", ["logcat", "-d", "-b", "all", "-v", "threadtime", "-t", str(args.lines)]),
    ]

    metadata = {
        "schema": 1,
        "test_id": args.output.name,
        "serial": args.serial,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "manual_gui_submission_already_completed": True,
        "user_created_by_script": False,
        "user_switched_by_script": False,
        "package_state_changed": False,
        "settings_changed": False,
        "private_binder_transaction": False,
        "broadcast_sent": False,
        "reboot_requested": False,
        "partition_written": False,
        "commands": [],
    }

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "serial": args.serial,
            "commands": [shlex.join(adb + tail) for _, tail in commands],
            "mutations": False,
        }, indent=2))
        return 0

    args.output.mkdir(parents=True)
    for label, tail in commands:
        argv = adb + tail
        completed = subprocess.run(argv, capture_output=True, check=False)
        stdout = args.output / f"{label}.stdout.txt"
        stderr = args.output / f"{label}.stderr.txt"
        stdout.write_bytes(completed.stdout)
        stderr.write_bytes(completed.stderr)
        metadata["commands"].append({
            "label": label,
            "argv": argv,
            "command": shlex.join(argv),
            "returncode": completed.returncode,
            "stdout": stdout.name,
            "stderr": stderr.name,
        })

    metadata["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "result.md").write_text(
        "# Phase 6BK child-profile post-submission read-only capture\n\n"
        f"- Serial: `{args.serial}`\n"
        "- No user/package/settings mutation was performed by this capture.\n"
        "- The manual UI submission occurred before this capture.\n",
        encoding="utf-8",
    )
    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in files),
        encoding="utf-8",
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
