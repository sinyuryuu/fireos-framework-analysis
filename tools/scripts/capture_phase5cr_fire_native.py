#!/usr/bin/env python3
"""Capture selected Fire native runtime artifacts without changing the device.

The script requires an explicit ADB serial, refuses an existing output
directory, reads only fixed system paths, and records hashes.  It never runs a
binary on the device, opens a device node, invokes futex/ioctl, changes
settings/package state, or reboots.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REMOTE_FILES = {
    "libc": "/system/lib64/libc.so",
    "linker64": "/system/bin/linker64",
    "app_process64": "/system/bin/app_process64",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_adb(serial: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["adb", "-s", serial, *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.serial.strip():
        print("ERROR: --serial must be explicit", file=sys.stderr)
        return 2
    if args.dry_run:
        print("DRY-RUN: no ADB command is executed and no file is written.")
        print(f"SERIAL\t{args.serial}")
        print(f"OUTPUT\t{args.output}")
        for name, remote in REMOTE_FILES.items():
            print(f"PULL\t{name}\t{remote}")
        return 0
    if args.output.exists():
        print(f"ERROR: refusing to overwrite output: {args.output}", file=sys.stderr)
        return 2

    state = run_adb(args.serial, "get-state")
    if state.returncode != 0 or state.stdout.strip() != "device":
        print("ERROR: ADB state is not exactly 'device'", file=sys.stderr)
        print(state.stdout, file=sys.stderr, end="")
        return 2

    args.output.mkdir(parents=True)
    files_dir = args.output / "files"
    files_dir.mkdir()
    commands: list[str] = []
    observations: dict[str, object] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "serial": args.serial,
        "host_only_analysis_after_pull": True,
        "device_mutated": False,
        "device_node_opened": False,
        "futex_invoked": False,
        "ioctl_invoked": False,
        "rebooted": False,
        "remote_files": REMOTE_FILES,
    }

    commands.append(f"adb -s {args.serial} get-state")
    properties = run_adb(args.serial, "shell", "getprop")
    commands.append(f"adb -s {args.serial} shell getprop")
    if properties.returncode != 0:
        print("ERROR: getprop failed", file=sys.stderr)
        return 2
    (args.output / "getprop.txt").write_text(properties.stdout, encoding="utf-8")

    path_listing = run_adb(
        args.serial, "shell", "ls", "-l", *REMOTE_FILES.values()
    )
    commands.append(
        f"adb -s {args.serial} shell ls -l " + " ".join(REMOTE_FILES.values())
    )
    if path_listing.returncode != 0:
        print("ERROR: remote path listing failed", file=sys.stderr)
        print(path_listing.stdout, file=sys.stderr, end="")
        return 2
    (args.output / "remote-paths.txt").write_text(path_listing.stdout, encoding="utf-8")

    for name, remote in REMOTE_FILES.items():
        destination = files_dir / name
        result = subprocess.run(
            ["adb", "-s", args.serial, "pull", remote, str(destination)],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        commands.append(f"adb -s {args.serial} pull {remote} {destination}")
        (args.output / f"pull-{name}.txt").write_text(result.stdout, encoding="utf-8")
        if result.returncode != 0 or not destination.is_file():
            print(f"ERROR: pull failed for {remote}", file=sys.stderr)
            return 2

    observations["host_sha256"] = {
        name: sha256(files_dir / name) for name in REMOTE_FILES
    }
    observations["file_sizes"] = {
        name: (files_dir / name).stat().st_size for name in REMOTE_FILES
    }
    (args.output / "metadata.json").write_text(
        json.dumps(observations, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (args.output / "commands.txt").write_text(
        "\n".join(commands) + "\n", encoding="utf-8"
    )
    files = sorted(path for path in args.output.rglob("*") if path.is_file())
    with (args.output / "sha256sums.txt").open("w", encoding="utf-8") as stream:
        for path in files:
            if path.name == "sha256sums.txt":
                continue
            stream.write(f"{sha256(path)}  {path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
