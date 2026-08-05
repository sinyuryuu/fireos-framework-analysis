#!/usr/bin/env python3
"""Capture the known non-mutating `cmd otadexopt help` surface.

The script requires an explicit serial, refuses to overwrite an output
directory, records stdout/stderr/exit status, and hashes every artifact. It
does not call prepare, done, progress, step, cleanup, or any Binder transaction
other than the documented shell-command help path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
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
        ["adb", "-s", args.serial, "get-state"],
        ["adb", "-s", args.serial, "shell", "cmd", "otadexopt", "help"],
    ]
    plan = {
        "operation": "phase6ae_known_otadexopt_help_capture",
        "serial": args.serial,
        "commands": [" ".join(cmd) for cmd in commands],
        "read_only": True,
        "help_only": True,
        "mutating_otadexopt_commands": [],
        "reboot_requested": False,
        "package_or_settings_mutation": False,
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
    metadata = {
        **plan,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "results": [],
    }
    for index, cmd in enumerate(commands, start=1):
        name = "get_state" if index == 1 else "cmd_otadexopt_help"
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
        if index == 1 and completed.returncode != 0:
            (args.output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
            )
            print("ADB state check failed; stopped before help command", file=sys.stderr)
            return 1

    (args.output / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
    )
    files = sorted(path for path in args.output.iterdir() if path.name != "sha256sums.txt")
    with (args.output / "sha256sums.txt").open("w") as handle:
        for path in files:
            handle.write(f"{digest(path)}  {path.name}\n")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
