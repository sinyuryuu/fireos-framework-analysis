#!/usr/bin/env python3
"""Capture the reversible lock-screen PIN pre-state before child setup."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
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
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite: {args.output}")

    commands = [
        ("secure_settings", ["shell", "settings", "list", "secure"]),
        ("password_type", ["shell", "settings", "get", "secure", "lockscreen.password_type"]),
        ("password_type_alternate", ["shell", "settings", "get", "secure", "lockscreen.password_type_alternate"]),
        ("lockscreen_disabled", ["shell", "settings", "get", "secure", "lockscreen.disabled"]),
        ("users", ["shell", "pm", "list", "users"]),
        ("lock_settings", ["shell", "dumpsys", "lock_settings"]),
        ("device_policy", ["shell", "dumpsys", "device_policy"]),
        ("activity", ["shell", "dumpsys", "activity", "activities"]),
        ("window", ["shell", "dumpsys", "window", "windows"]),
    ]
    metadata = {
        "test_id": args.output.name,
        "serial": args.serial,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "pin_value_captured": False,
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
        stdout_path = args.output / f"{name}.stdout.txt"
        stderr_path = args.output / f"{name}.stderr.txt"
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        metadata["commands"].append({
            "name": name,
            "argv": command,
            "returncode": completed.returncode,
            "stdout": stdout_path.name,
            "stderr": stderr_path.name,
        })
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
