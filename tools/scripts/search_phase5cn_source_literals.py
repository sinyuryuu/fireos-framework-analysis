#!/usr/bin/env python3
"""Search selected PS7331 source members without extracting the source tree.

The script streams the nested ``platform.tar`` member of the official source
archive and records only matching member names, hashes, line numbers and
short source lines. It never executes or builds source and never performs
device I/O.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_LITERALS = ("HAVE_FUTEX_CMPXCHG", "CONFIG_HAVE_FUTEX_CMPXCHG")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--literal", action="append", default=[])
    parser.add_argument("--outer-member", default="platform.tar")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    literals = tuple(args.literal or DEFAULT_LITERALS)

    if args.dry_run:
        print("DRY-RUN: no archive is read and no files are written.")
        print(f"ARCHIVE\t{args.archive}")
        print(f"OUTER_MEMBER\t{args.outer_member}")
        print(f"OUTPUT\t{args.output}")
        for literal in literals:
            print(f"LITERAL\t{literal}")
        return 0

    if not args.archive.is_file():
        print(f"ERROR: archive is not a regular file: {args.archive}", file=sys.stderr)
        return 2
    if args.output.exists():
        print(f"ERROR: refusing to overwrite output: {args.output}", file=sys.stderr)
        return 2

    args.output.mkdir(parents=True)
    archive_hash = sha256_file(args.archive)
    patterns = tuple(re.compile(re.escape(literal)) for literal in literals)
    results: list[dict[str, object]] = []
    inspected = 0
    command = ["tar", "-xOjf", str(args.archive), args.outer_member]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    assert process.stdout is not None
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as nested:
            for member in nested:
                if not member.isfile():
                    continue
                name = member.name
                basename = name.rsplit("/", 1)[-1]
                is_kconfig = basename == "Kconfig" or basename.startswith("Kconfig.")
                is_futex_header = basename in {"futex.h", "futex-irq.h"}
                if not (is_kconfig or is_futex_header):
                    continue
                source = nested.extractfile(member)
                if source is None:
                    continue
                inspected += 1
                digest = hashlib.sha256()
                hits: list[dict[str, object]] = []
                for line_no, raw_line in enumerate(source, 1):
                    digest.update(raw_line)
                    line = raw_line.decode("utf-8", "replace").rstrip("\n")
                    if any(pattern.search(line) for pattern in patterns):
                        hits.append({"line": line_no, "text": line[:400]})
                if hits:
                    results.append({
                        "member": name,
                        "size": member.size,
                        "sha256": digest.hexdigest(),
                        "hits": hits,
                    })
    finally:
        process.stdout.close()
        return_code = process.wait()

    if return_code != 0:
        print(f"ERROR: nested archive stream failed: {return_code}", file=sys.stderr)
        return 3

    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_io": False,
        "archive": str(args.archive),
        "archive_sha256": archive_hash,
        "outer_member": args.outer_member,
        "literals": list(literals),
        "inspected_kconfig_or_futex_header_members": inspected,
        "matches": results,
        "executed_content": False,
    }
    (args.output / "metadata.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.output / "commands.txt").write_text(
        " ".join(command) + " | stream-search-selected-members\n", encoding="utf-8"
    )
    (args.output / "result.md").write_text(
        "# Phase 5CN source literal search\n\n"
        f"- Archive SHA-256: `{archive_hash}`\n"
        f"- Inspected selected members: **{inspected}**\n"
        f"- Matching members: **{len(results)}**\n"
        "- Host-only; no source was executed or built and no device operation ran.\n",
        encoding="utf-8",
    )
    files = sorted(path for path in args.output.rglob("*") if path.is_file())
    (args.output / "sha256sums.txt").write_text(
        "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(args.output)}\n"
            for path in files if path.name != "sha256sums.txt"
        ),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
