#!/usr/bin/env python3
"""Use the visible Amazon Settings screen to authenticate and disable the test PIN.

This script is intentionally limited to the supported LockScreenActivity UI. It
does not call locksettings, settings put/delete, a Binder transaction, or a
private API. The PIN is never written to metadata or output files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    parser.add_argument("--pin", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite: {args.output}")
    if not args.pin.isdigit() or len(args.pin) < 4:
        raise SystemExit("PIN must be at least four decimal digits")

    commands = [
        ("focus_current_pin", ["shell", "input", "tap", "600", "275"]),
        ("enter_current_pin", ["shell", "input", "text", args.pin]),
        ("dismiss_keyboard", ["shell", "input", "keyevent", "KEYCODE_BACK"]),
        ("submit_disable", ["shell", "input", "tap", "282", "372"]),
        ("activity_after_submit", ["shell", "dumpsys", "activity", "activities"]),
        ("window_after_submit", ["shell", "dumpsys", "window", "windows"]),
        ("users_after_submit", ["shell", "pm", "list", "users"]),
        ("password_type_after_submit", ["shell", "settings", "get", "secure", "lockscreen.password_type"]),
        ("lockscreen_disabled_after_submit", ["shell", "settings", "get", "secure", "lockscreen.disabled"]),
        ("lock_settings_after_submit", ["shell", "dumpsys", "lock_settings"]),
    ]
    metadata = {
        "test_id": args.output.name,
        "serial": args.serial,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "supported_settings_ui_only": True,
        "pin_value_captured": False,
        "pin_value_stored": False,
        "private_binder_transaction": False,
        "service_call_used": False,
        "firelauncher_mutation_attempted": False,
        "child_profile_submitted": False,
        "commands": [],
    }
    if args.dry_run:
        metadata["dry_run"] = True
        print(json.dumps(metadata, indent=2))
        return 0

    args.output.mkdir(parents=True)
    for name, tail in commands:
        command = ["adb", "-s", args.serial, *tail]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        (args.output / f"{name}.stdout.txt").write_text(completed.stdout, encoding="utf-8")
        (args.output / f"{name}.stderr.txt").write_text(completed.stderr, encoding="utf-8")
        recorded = command[:]
        if name == "enter_current_pin":
            recorded[-1] = "<REDACTED_PIN>"
        metadata["commands"].append({
            "name": name,
            "argv": recorded,
            "returncode": completed.returncode,
            "stdout": f"{name}.stdout.txt",
            "stderr": f"{name}.stderr.txt",
        })
        if name in {"focus_current_pin", "enter_current_pin", "dismiss_keyboard"}:
            time.sleep(0.5)
    metadata["finished_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    hashes = []
    for path in sorted(args.output.iterdir()):
        if path.is_file() and path.name != "sha256sums.txt":
            hashes.append(f"{sha256(path)}  {path.name}")
    (args.output / "sha256sums.txt").write_text("\n".join(hashes) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
