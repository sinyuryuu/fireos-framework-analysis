#!/usr/bin/env python3
"""Capture a narrow PS7331 PackageManager/OOBE read-only boundary.

The script requires an explicit serial and only runs getprop, cmd package,
dumpsys, service list, settings get, and ls metadata queries.  It never writes
device state, sends an intent, calls Binder transactions directly, or reads
protected files through an elevated path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


COMMANDS = {
    "adb_state": ["get-state"],
    "fingerprint": ["shell", "getprop", "ro.build.fingerprint"],
    "build_version": ["shell", "getprop", "ro.build.version.incremental"],
    "home_resolve": ["shell", "cmd", "package", "resolve-activity", "--brief", "--user", "0", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"],
    "home_candidates": ["shell", "cmd", "package", "query-activities", "--brief", "--user", "0", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"],
    "firelauncher_package": ["shell", "dumpsys", "package", "com.amazon.firelauncher"],
    "activity_state": ["shell", "dumpsys", "activity", "activities"],
    "window_state": ["shell", "dumpsys", "window", "windows"],
    "service_list": ["shell", "service", "list"],
    "denylist_metadata": ["shell", "ls", "-ld", "/data/system/PackageManagerDenyList"],
    "denylist_children_metadata": ["shell", "ls", "-l", "/data/system/PackageManagerDenyList"],
    "oobe_setup_complete": ["shell", "settings", "get", "secure", "user_setup_complete"],
    "oobe_active": ["shell", "settings", "get", "secure", "isOOBEActive"],
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()

    if output.exists() and any(output.iterdir()):
        print(f"refusing to overwrite non-empty output: {output}", file=sys.stderr)
        return 2

    rendered = {name: ["adb", "-s", args.serial, *argv] for name, argv in COMMANDS.items()}
    if args.dry_run:
        print(json.dumps({"serial": args.serial, "device_contacted": False, "commands": rendered}, indent=2))
        return 0

    output.mkdir(parents=True, exist_ok=True)
    metadata = {
        "test_id": output.name,
        "serial": args.serial,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "device_mutation": False,
        "unknown_binder_transaction": False,
        "commands": rendered,
        "results": {},
    }

    for name, argv in rendered.items():
        proc = subprocess.run(argv, capture_output=True, text=True, check=False)
        (output / f"{name}.stdout.txt").write_text(proc.stdout, encoding="utf-8")
        (output / f"{name}.stderr.txt").write_text(proc.stderr, encoding="utf-8")
        metadata["results"][name] = {"returncode": proc.returncode, "stdout_bytes": len(proc.stdout.encode()), "stderr_bytes": len(proc.stderr.encode())}

    metadata["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(p for p in output.iterdir() if p.name != "sha256sums.txt")
    (output / "sha256sums.txt").write_text("\n".join(f"{digest(p)}  {p.name}" for p in files) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "serial": args.serial, "device_mutation": False, "command_count": len(rendered)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
