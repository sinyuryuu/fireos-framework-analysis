#!/usr/bin/env python3
"""Host-only fallback-mode JADX extraction for the Play Store launcher receiver.

The script reads a preserved APK and writes an isolated decompilation artifact.
It never contacts a device, installs or starts an APK, sends Binder traffic, or
changes any project source/evidence input. Existing output directories are not
overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


CLASS_NAME = "com.google.android.finsky.setup.LauncherConfigurationReceiver"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jadx", default="jadx")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    apk = args.apk.resolve()
    output = args.output.resolve()
    class_file = output / "LauncherConfigurationReceiver.java"
    command = [
        args.jadx,
        "--log-level", "INFO",
        "--show-bad-code",
        "--decompilation-mode", "fallback",
        "--comments-level", "debug",
        "--single-class", CLASS_NAME,
        "--single-class-output", str(class_file),
        str(apk),
    ]

    if not apk.is_file():
        raise SystemExit(f"APK not found: {apk}")
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "apk": str(apk),
            "apk_sha256": sha256(apk),
            "class": CLASS_NAME,
            "output": str(output),
            "command": command,
            "device_access": False,
            "mutating_operations": False,
        }, indent=2))
        return 0

    output.mkdir(parents=True)
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    (output / "jadx.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (output / "jadx.stderr.txt").write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise SystemExit(f"jadx failed with exit code {result.returncode}; evidence kept at {output}")
    if not class_file.is_file():
        raise SystemExit(f"expected class output missing: {class_file}")

    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_apk": str(apk),
        "input_apk_sha256": sha256(apk),
        "class": CLASS_NAME,
        "jadx_path": shutil.which(args.jadx),
        "command": command,
        "jadx_returncode": result.returncode,
        "device_access": False,
        "binder_transactions": False,
        "mutating_operations": False,
        "class_output": class_file.name,
        "class_output_sha256": sha256(class_file),
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in output.iterdir() if path.is_file() and path.name != "sha256sums.txt")
    (output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(output),
        "class_output": str(class_file),
        "class_output_sha256": sha256(class_file),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
