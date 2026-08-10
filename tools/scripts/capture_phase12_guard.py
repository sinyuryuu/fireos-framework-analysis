#!/usr/bin/env python3
"""Capture a minimal read-only post-analysis device guard."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite: {args.output}")
    args.output.mkdir(parents=True)

    commands = {
        "adb_state": ["get-state"],
        "fingerprint": ["shell", "getprop", "ro.build.fingerprint"],
        "current_user": ["shell", "am", "get-current-user"],
        "home_user0": [
            "shell", "cmd", "package", "resolve-activity", "--brief",
            "--user", "0", "-a", "android.intent.action.MAIN", "-c",
            "android.intent.category.HOME",
        ],
        "fire_package": ["shell", "dumpsys", "package", "com.amazon.firelauncher"],
    }
    metadata = {
        "serial": args.serial,
        "started_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "mutation": False,
        "binder_transaction": False,
        "reboot": False,
        "commands": [],
    }
    for name, tail in commands.items():
        argv = ["adb", "-s", args.serial, *tail]
        result = subprocess.run(argv, text=True, capture_output=True, check=False)
        stdout = args.output / f"{name}.stdout.txt"
        stderr = args.output / f"{name}.stderr.txt"
        stdout.write_text(result.stdout, encoding="utf-8")
        stderr.write_text(result.stderr, encoding="utf-8")
        metadata["commands"].append({
            "name": name,
            "argv": argv,
            "returncode": result.returncode,
            "stdout": stdout.name,
            "stderr": stderr.name,
        })
    metadata["finished_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    entries = []
    for path in sorted(args.output.iterdir()):
        if path.is_file() and path.name != "sha256sums.txt":
            entries.append(f"{sha256(path)}  {path.name}")
    (args.output / "sha256sums.txt").write_text(
        "\n".join(entries) + "\n", encoding="utf-8"
    )
    print(json.dumps({"output": str(args.output), "read_only": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
