#!/usr/bin/env python3
"""Extract allow-listed top-level members from the local PS7331 archive.

Host-only provenance helper. It uses the local archive as read-only input and
extracts only named regular files. It never executes scripts and never touches
an Android device.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_MEMBERS = ["build_kernel.sh", "build_kernel_config.sh"]


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
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.dry_run:
        print("DRY-RUN: no archive is read and no files are written.")
        print(f"ARCHIVE\t{args.archive}")
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

    for member_name in DEFAULT_MEMBERS:
        member_command = ["tar", "-xOjf", str(args.archive), member_name]
        member_process = subprocess.run(
            member_command, check=False, capture_output=True
        )
        if member_process.returncode != 0:
            continue
        destination = args.output / "extracted" / member_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(member_process.stdout)
        extracted.append(
            {
                "member": member_name,
                "size": destination.stat().st_size,
                "sha256": sha256(destination),
                "path": str(destination),
            }
        )

    missing = sorted(requested - {str(row["member"]) for row in extracted})
    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_io": False,
        "archive": str(args.archive),
        "archive_sha256": archive_hash,
        "container": "outer_archive",
        "requested_members": DEFAULT_MEMBERS,
        "extracted_members": extracted,
        "missing_members": missing,
        "executed_content": False,
    }
    (args.output / "metadata.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.output / "commands.txt").write_text(
        "per-member: " + " ; ".join(" ".join(
            ["tar", "-xOjf", str(args.archive), member]
        ) for member in DEFAULT_MEMBERS) + "\n",
        encoding="utf-8",
    )
    (args.output / "result.md").write_text(
        "# PS7331 top-level build-script extraction\n\n"
        f"Archive SHA-256: {archive_hash}\n\n"
        f"Extracted members: {len(extracted)}\n\n"
        f"Missing requested members: {len(missing)}\n\n"
        "This output is host-only. The extracted shell scripts were not "
        "executed and no device operation was performed.\n",
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
