#!/usr/bin/env python3
"""Capture documented, read-like otadexopt status commands and HOME state.

This intentionally excludes prepare, step, next, and cleanup. It requires an
explicit serial, refuses overwrite, and keeps raw stdout/stderr plus hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--serial", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    if not args.serial.strip():
        print("--serial must not be empty", file=sys.stderr)
        return 2
    commands = [
        ("get_state", ["adb", "-s", args.serial, "get-state"]),
        ("otadexopt_done", ["adb", "-s", args.serial, "shell", "cmd", "otadexopt", "done"]),
        ("otadexopt_progress", ["adb", "-s", args.serial, "shell", "cmd", "otadexopt", "progress"]),
        (
            "home_resolve",
            [
                "adb", "-s", args.serial, "shell", "cmd", "package",
                "resolve-activity", "--brief", "-a", "android.intent.action.MAIN",
                "-c", "android.intent.category.HOME",
            ],
        ),
        (
            "activity_activities",
            ["adb", "-s", args.serial, "shell", "dumpsys", "activity", "activities"],
        ),
    ]
    plan = {
        "operation": "phase6ae_documented_otadexopt_status_capture",
        "serial": args.serial,
        "commands": [" ".join(cmd) for _, cmd in commands],
        "read_only": True,
        "allowed_otadexopt_commands": ["done", "progress"],
        "excluded_otadexopt_commands": ["prepare", "step", "next", "cleanup"],
        "package_or_settings_mutation": False,
        "reboot_requested": False,
        "unknown_binder_transaction": False,
        "output": str(args.output),
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return 0
    if args.output.exists():
        print(f"refusing to overwrite existing output: {args.output}", file=sys.stderr)
        return 2
    args.output.mkdir(parents=True)
    metadata = {**plan, "captured_at_utc": datetime.now(timezone.utc).isoformat(), "results": []}
    for name, cmd in commands:
        completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
        stdout = args.output / f"{name}.stdout.txt"
        stderr = args.output / f"{name}.stderr.txt"
        stdout.write_text(completed.stdout)
        stderr.write_text(completed.stderr)
        metadata["results"].append(
            {
                "name": name,
                "command": " ".join(cmd),
                "returncode": completed.returncode,
                "stdout": stdout.name,
                "stderr": stderr.name,
            }
        )
        if name == "get_state" and completed.returncode != 0:
            break
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
    )
    files = sorted(path for path in args.output.iterdir() if path.name != "sha256sums.txt")
    with (args.output / "sha256sums.txt").open("w") as handle:
        for path in files:
            handle.write(f"{sha256(path)}  {path.name}\n")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
