#!/usr/bin/env python3
"""Capture only standard, read-only dumps for shell-visible debug surfaces.

The commands use the public `dumpsys`/`service check` shell interfaces.  They
do not issue an arbitrary `service call`, start a component, change state, or
touch OTA/recovery paths.  A serial is mandatory because multiple devices may
be connected.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path


COMMANDS = [
    ("service_check_fosdebug", ("shell", "service", "check", "fosdebug")),
    ("service_check_amazonthermalservice", ("shell", "service", "check", "amazonthermalservice")),
    ("service_check_otadexopt", ("shell", "service", "check", "otadexopt")),
    ("dumpsys_fosdebug", ("shell", "dumpsys", "fosdebug")),
    ("dumpsys_amazonthermalservice", ("shell", "dumpsys", "amazonthermalservice")),
    ("dumpsys_otadexopt", ("shell", "dumpsys", "otadexopt")),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, text=True, capture_output=True, check=False, timeout=45)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    adb = ["adb", "-s", args.serial]
    commands = [(name, adb + list(parts)) for name, parts in COMMANDS]
    if args.dry_run:
        print(json.dumps({
            "host_only": False,
            "device_contacted": False,
            "mutating_commands": False,
            "commands": [shlex.join(command) for _, command in commands],
        }, indent=2))
        return 0
    devices = run(["adb", "devices"])
    if not any(line.startswith(args.serial + "\tdevice") for line in devices.stdout.splitlines()):
        raise SystemExit(f"target is not online as device: {args.serial}")
    args.output.mkdir(parents=True)
    records = []
    for name, command in commands:
        result = run(command)
        stdout = args.output / f"{name}.stdout.txt"
        stderr = args.output / f"{name}.stderr.txt"
        stdout.write_text(result.stdout, encoding="utf-8")
        stderr.write_text(result.stderr, encoding="utf-8")
        records.append({
            "name": name,
            "command": shlex.join(command),
            "returncode": result.returncode,
            "stdout": stdout.name,
            "stderr": stderr.name,
        })
    metadata = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "serial": args.serial,
        "read_only": True,
        "device_contacted": True,
        "standard_dumpsys_dump_transaction_used": True,
        "unknown_binder_transaction_sent": False,
        "arbitrary_service_call_sent": False,
        "activity_started": False,
        "settings_changed": False,
        "package_state_changed": False,
        "reboot_requested": False,
        "commands": records,
    }
    metadata_path = args.output / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    files = sorted(p for p in args.output.iterdir() if p.is_file())
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in files if path.name != "sha256sums.txt"),
        encoding="utf-8",
    )
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
