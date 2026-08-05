#!/usr/bin/env python3
"""Capture read-only service visibility evidence for PS7331.

Only service-manager lookups, standard dumps and package/build queries are
used.  This script never sends a Binder transaction to a private service,
never invokes ``service call``, and never changes device state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(argv: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(argv, capture_output=True, check=False)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--serial", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    adb = ["adb", "-s", args.serial]
    private = [
        "amazonpackagemanager", "amazonactivitymanager", "amazonwindowmanager",
        "amazondevicepolicymanager", "amazonprofileservice", "amazonusermanagerservice",
        "amazon_input", "amazon_keyevent", "fosdebug", "otadexopt",
    ]
    commands: list[tuple[str, list[str]]] = [
        ("devices", ["adb", "devices", "-l"]),
        ("state", adb + ["get-state"]),
        ("id", adb + ["shell", "id"]),
        ("getenforce", adb + ["shell", "getenforce"]),
        ("fingerprint", adb + ["shell", "getprop", "ro.build.fingerprint"]),
        ("service_list", adb + ["shell", "service", "list"]),
    ]
    commands.extend((f"service_check_{name}", adb + ["shell", "service", "check", name]) for name in private)
    commands.extend([
        ("dumpsys_fosdebug", adb + ["shell", "dumpsys", "fosdebug"]),
        ("dumpsys_otadexopt", adb + ["shell", "dumpsys", "otadexopt"]),
        ("logcat_targeted", adb + ["logcat", "-b", "all", "-d", "-v", "threadtime"]),
    ])
    if args.dry_run:
        print(json.dumps({
            "serial": args.serial,
            "output": str(args.output),
            "mutating_commands": False,
            "binder_transactions": False,
            "commands": [shlex.join(c) for _, c in commands],
        }, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    devices = run(["adb", "devices"]).stdout.decode(errors="replace")
    if not any(line.startswith(args.serial + "\tdevice") for line in devices.splitlines()):
        raise SystemExit(f"refusing device access: {args.serial!r} is not online as device")
    args.output.mkdir(parents=True)
    rows = []
    for name, argv in commands:
        result = run(argv)
        out = args.output / f"{name}.stdout.txt"
        err = args.output / f"{name}.stderr.txt"
        out.write_bytes(result.stdout)
        err.write_bytes(result.stderr)
        rows.append({
            "id": name,
            "command": shlex.join(argv),
            "returncode": result.returncode,
            "stdout": out.name,
            "stderr": err.name,
            "stdout_sha256": digest(out),
            "stderr_sha256": digest(err),
        })
    metadata = {
        "phase": "6AQ",
        "serial": args.serial,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mutating_commands": False,
        "binder_transactions": False,
        "settings_changed": False,
        "package_state_changed": False,
        "reboot_requested": False,
        "private_service_methods_invoked": False,
        "commands": rows,
        "limitations": [
            "service check is only a service-manager lookup; a successful lookup is not authorization proof",
            "dumpsys is a standard diagnostic transaction; no private method transaction was sent",
            "logcat is read with -d and is not cleared",
        ],
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    files = sorted(p for p in args.output.iterdir() if p.is_file() and p.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text("".join(f"{digest(p)}  {p.name}\n" for p in files))
    print(json.dumps({"output": str(args.output), "command_count": len(commands), "mutating_commands": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
