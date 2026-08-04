#!/usr/bin/env python3
"""Extract the PS7331 ARM64 futex/config members for host-only review.

This script reads the local official source archive, streams its nested
``platform.tar`` member, and extracts only the fixed allow-list below. It
never invokes adb/fastboot, executes source, builds a kernel, or writes to a
device. Existing output directories are never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path


MEMBERS = (
    "kernel/mediatek/4.4/arch/arm64/include/asm/futex.h",
    "kernel/mediatek/4.4/arch/Kconfig",
    "kernel/mediatek/4.4/arch/arm/Kconfig",
    "kernel/mediatek/4.4/init/Kconfig",
    "kernel/mediatek/4.4/arch/arm/mach-mediatek/Kconfig",
    "kernel/mediatek/4.4/include/asm-generic/futex.h",
    "kernel/mediatek/4.4/include/linux/futex.h",
    "kernel/mediatek/4.4/include/linux/rtmutex.h",
    "kernel/mediatek/4.4/arch/arm64/Kconfig",
    "kernel/mediatek/4.4/arch/arm64/Kconfig.debug",
    "kernel/mediatek/4.4/arch/arm64/Kconfig.platforms",
    "kernel/mediatek/4.4/Kconfig",
    "kernel/mediatek/4.4/kernel/Kconfig.locks",
    "kernel/mediatek/4.4/kernel/Kconfig.preempt",
    "kernel/mediatek/mt8183/4.4/arch/arm64/include/asm/futex.h",
    "kernel/mediatek/mt8183/4.4/arch/Kconfig",
    "kernel/mediatek/mt8183/4.4/arch/arm/Kconfig",
    "kernel/mediatek/mt8183/4.4/init/Kconfig",
    "kernel/mediatek/mt8183/4.4/arch/arm/mach-mediatek/Kconfig",
    "kernel/mediatek/mt8183/4.4/include/asm-generic/futex.h",
    "kernel/mediatek/mt8183/4.4/include/linux/futex.h",
    "kernel/mediatek/mt8183/4.4/include/linux/rtmutex.h",
    "kernel/mediatek/mt8183/4.4/arch/arm64/Kconfig",
    "kernel/mediatek/mt8183/4.4/arch/arm64/Kconfig.debug",
    "kernel/mediatek/mt8183/4.4/arch/arm64/Kconfig.platforms",
    "kernel/mediatek/mt8183/4.4/Kconfig",
    "kernel/mediatek/mt8183/4.4/kernel/Kconfig.locks",
    "kernel/mediatek/mt8183/4.4/kernel/Kconfig.preempt",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--outer-member", default="platform.tar")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY-RUN: no archive is read and no files are written.")
        print(f"ARCHIVE\t{args.archive}")
        print(f"OUTER_MEMBER\t{args.outer_member}")
        print(f"OUTPUT\t{args.output}")
        for member in MEMBERS:
            print(f"MEMBER\t{member}")
        return 0

    if not args.archive.is_file():
        print(f"ERROR: archive is not a regular file: {args.archive}", file=sys.stderr)
        return 2
    if args.output.exists():
        print(f"ERROR: refusing to overwrite output: {args.output}", file=sys.stderr)
        return 2

    args.output.mkdir(parents=True)
    archive_hash = sha256(args.archive)
    requested = set(MEMBERS)
    extracted: list[dict[str, object]] = []
    command = ["tar", "-xOjf", str(args.archive), args.outer_member]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    assert process.stdout is not None
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as nested:
            for member in nested:
                if member.name not in requested or not member.isfile():
                    continue
                destination = args.output / "extracted" / member.name
                destination.parent.mkdir(parents=True, exist_ok=True)
                source = nested.extractfile(member)
                if source is None:
                    continue
                with destination.open("wb") as target:
                    while True:
                        block = source.read(1024 * 1024)
                        if not block:
                            break
                        target.write(block)
                extracted.append({
                    "member": member.name,
                    "size": destination.stat().st_size,
                    "sha256": sha256(destination),
                    "path": str(destination),
                })
    finally:
        process.stdout.close()
        return_code = process.wait()

    if return_code != 0:
        print(f"ERROR: nested archive stream failed: {return_code}", file=sys.stderr)
        return 3

    missing = sorted(requested - {str(row["member"]) for row in extracted})
    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_io": False,
        "archive": str(args.archive),
        "archive_sha256": archive_hash,
        "outer_member": args.outer_member,
        "requested_members": list(MEMBERS),
        "extracted_members": extracted,
        "missing_members": missing,
        "executed_content": False,
    }
    (args.output / "metadata.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.output / "commands.txt").write_text(
        " ".join(command) + "\n", encoding="utf-8"
    )
    (args.output / "result.md").write_text(
        "# Phase 5CN ARM64 futex/config source extraction\n\n"
        f"- Archive SHA-256: `{archive_hash}`\n"
        f"- Extracted members: **{len(extracted)}**\n"
        f"- Missing members: **{len(missing)}**\n"
        "- Host-only; no source was executed or built and no device operation ran.\n",
        encoding="utf-8",
    )
    files = sorted(
        path for path in args.output.rglob("*")
        if path.is_file() and path.name != "sha256sums.txt"
    )
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
