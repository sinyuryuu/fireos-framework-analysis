#!/usr/bin/env python3
"""Extract an allow-listed set of PS7331 source members from platform.tar.

This is a host-only provenance helper. It reads a local Amazon source archive,
streams the nested platform.tar member, extracts only named regular files, and
records hashes. It never invokes adb/fastboot and never executes extracted
content.
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


DEFAULT_MEMBERS = [
    "kernel/mediatek/4.4/kernel/locking/rtmutex.c",
    "kernel/mediatek/4.4/kernel/futex.c",
    "kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c",
    "kernel/mediatek/mt8183/4.4/kernel/futex.c",
    "kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig",
    "kernel/mediatek/mt8183/4.4/Makefile",
    "device/amazon/kernel/driver/Kconfig",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--outer-member", default="platform.tar")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.dry_run:
        print("DRY-RUN: no archive is read and no files are written.")
        print(f"ARCHIVE\t{args.archive}")
        print(f"OUTER_MEMBER\t{args.outer_member}")
        print(f"OUTPUT\t{args.output}")
        for member in DEFAULT_MEMBERS:
            print(f"MEMBER\t{member}")
        return 0
    if not args.archive.is_file():
        print(f"ERROR: archive missing: {args.archive}", file=sys.stderr)
        return 2
    if args.output.exists():
        print(f"ERROR: refusing to overwrite output: {args.output}", file=sys.stderr)
        return 2

    args.output.mkdir(parents=True)
    archive_hash = sha256(args.archive)
    requested = set(DEFAULT_MEMBERS)
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
                extracted.append(
                    {
                        "member": member.name,
                        "size": destination.stat().st_size,
                        "sha256": sha256(destination),
                        "path": str(destination),
                    }
                )
    finally:
        process.stdout.close()
        return_code = process.wait()
    if return_code != 0:
        print(f"ERROR: outer tar extraction failed: {return_code}", file=sys.stderr)
        return 3

    missing = sorted(requested - {str(row["member"]) for row in extracted})
    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_io": False,
        "archive": str(args.archive),
        "archive_sha256": archive_hash,
        "outer_member": args.outer_member,
        "requested_members": DEFAULT_MEMBERS,
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
        "# PS7331 nested source extraction\n\n"
        f"Archive SHA-256: `{archive_hash}`\n\n"
        f"Extracted members: **{len(extracted)}**\n\n"
        f"Missing requested members: **{len(missing)}**\n\n"
        "This output is host-only. No extracted content was executed and no "
        "device operation was performed.\n",
        encoding="utf-8",
    )
    (args.output / "sha256sums.txt").write_text(
        "\n".join(
            f"{sha256(path)}  {path.relative_to(args.output)}"
            for path in sorted(args.output.rglob("*"))
            if path.is_file() and path.name != "sha256sums.txt"
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(extracted)} selected members to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
