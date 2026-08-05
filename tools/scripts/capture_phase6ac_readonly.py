#!/usr/bin/env python3
"""Capture the android.amazon.perm provenance surface with read-only ADB.

The serial and output directory are mandatory.  The script refuses to reuse an
existing output directory, records stdout/stderr/exit status for every command,
and only pulls the APK returned by ``pm path``.  It never sends a broadcast,
invokes Binder, changes package/settings state, reboots, or writes a device
partition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


PACKAGE = "android.amazon.perm"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True)


def write_result(output: Path, name: str, command: list[str], result: subprocess.CompletedProcess[str]) -> None:
    (output / f"{name}.command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")
    (output / f"{name}.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (output / f"{name}.stderr.txt").write_text(result.stderr, encoding="utf-8")
    (output / f"{name}.exit_code.txt").write_text(f"{result.returncode}\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--adb", default="adb")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.serial or args.serial in {"all", "*"}:
        raise SystemExit("a single explicit device serial is required")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    commands = {
        "get_state": [args.adb, "-s", args.serial, "get-state"],
        "fingerprint": [args.adb, "-s", args.serial, "shell", "getprop", "ro.build.fingerprint"],
        "incremental": [args.adb, "-s", args.serial, "shell", "getprop", "ro.build.version.incremental"],
        "shell_id": [args.adb, "-s", args.serial, "shell", "id"],
        "pm_path": [args.adb, "-s", args.serial, "shell", "pm", "path", PACKAGE],
        "pm_dump": [args.adb, "-s", args.serial, "shell", "pm", "dump", PACKAGE],
    }

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "device_contacted": False,
            "package": PACKAGE,
            "serial": args.serial,
            "commands": commands,
            "output": str(args.output),
        }, indent=2, sort_keys=True))
        return 0

    args.output.mkdir(parents=True)
    started = datetime.now(timezone.utc).isoformat()
    results: dict[str, subprocess.CompletedProcess[str]] = {}
    for name, command in commands.items():
        result = run_command(command)
        results[name] = result
        write_result(args.output, name, command, result)

    path_lines = [line.strip() for line in results["pm_path"].stdout.splitlines() if line.strip().startswith("package:")]
    if results["get_state"].returncode != 0 or results["get_state"].stdout.strip() != "device":
        raise SystemExit("device did not report state=device; capture retained without APK pull")
    if not path_lines:
        raise SystemExit("pm path returned no package path; capture retained without APK pull")

    remote_path = path_lines[0].split("=", 1)[0].removeprefix("package:")
    local_apk = args.output / Path(remote_path).name
    pull_command = [args.adb, "-s", args.serial, "pull", remote_path, str(local_apk)]
    pull_result = run_command(pull_command)
    results["pull_apk"] = pull_result
    write_result(args.output, "pull_apk", pull_command, pull_result)
    if pull_result.returncode != 0 or not local_apk.is_file():
        raise SystemExit("APK pull failed; capture retained")

    metadata = {
        "schema": 1,
        "captured_at_utc": started,
        "serial": args.serial,
        "package": PACKAGE,
        "device_state": results["get_state"].stdout.strip(),
        "build_fingerprint": results["fingerprint"].stdout.strip(),
        "build_incremental": results["incremental"].stdout.strip(),
        "remote_path": remote_path,
        "local_apk": local_apk.name,
        "apk_sha256": sha256(local_apk),
        "read_only": True,
        "broadcast_sent": False,
        "binder_transaction_sent": False,
        "package_state_mutated": False,
        "settings_mutated": False,
        "reboot_performed": False,
        "partition_written": False,
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output / "README.md").write_text(
        "# Phase 6AC read-only device capture\n\n"
        "This directory contains raw stdout/stderr/exit-code records for the\n"
        "explicit-serial read-only commands and the APK returned by `pm path`.\n"
        "No broadcast, Binder transaction, package/settings mutation, reboot,\n"
        "OTA/recovery action, or partition write was performed.\n",
        encoding="utf-8",
    )

    manifest_lines = []
    for path in sorted(args.output.iterdir()):
        if path.name == "sha256sums.txt" or not path.is_file():
            continue
        manifest_lines.append(f"{sha256(path)}  {path.name}")
    (args.output / "sha256sums.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
