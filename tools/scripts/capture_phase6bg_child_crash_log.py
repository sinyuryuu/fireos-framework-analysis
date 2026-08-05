#!/usr/bin/env python3
"""Capture the existing read-only logcat evidence for the stock child UI crash."""

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
    command = ["adb", "-s", args.serial, "shell", "logcat", "-d", "-v", "threadtime", "-b", "all"]
    metadata = {
        "test_id": args.output.name,
        "serial": args.serial,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "private_binder_transaction": False,
        "service_call_used": False,
        "commands": [{"name": "logcat_all", "argv": command, "stdout": "logcat_all.stdout.txt", "stderr": "logcat_all.stderr.txt"}],
    }
    if args.dry_run:
        metadata["dry_run"] = True
        print(json.dumps(metadata, indent=2))
        return 0
    args.output.mkdir(parents=True)
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    (args.output / "logcat_all.stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (args.output / "logcat_all.stderr.txt").write_text(completed.stderr, encoding="utf-8")
    metadata["commands"][0]["returncode"] = completed.returncode
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
