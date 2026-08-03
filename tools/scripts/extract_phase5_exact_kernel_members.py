#!/usr/bin/env python3
"""Extract selected members from a recovered, possibly unaligned ustar slice.

This is a host-only evidence tool.  It never executes extracted content and
refuses to overwrite an existing output directory.  The input is expected to
be a recovered decompressed tar slice such as the bounded HTTP-range artifact
used by the Phase 5 source review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ZERO = bytes([0])


def parse_octal(value: bytes) -> int | None:
    value = value.split(ZERO, 1)[0].strip()
    try:
        return int(value or b"0", 8)
    except ValueError:
        return None


def parse_members(raw: bytes):
    """Yield (name, header_offset, size, typeflag, payload) for valid headers.

    Recovered bzip2 blocks can lose tar block alignment.  Searching for the
    ustar magic and validating the tar checksum is intentional and recorded
    in the output metadata; it is not a substitute for a complete archive.
    """
    pos = 0
    while True:
        magic_pos = raw.find(b"ustar", pos)
        if magic_pos < 0:
            return
        pos = magic_pos + 1
        header_offset = magic_pos - 257
        if header_offset < 0 or header_offset + 512 > len(raw):
            continue
        header = raw[header_offset : header_offset + 512]
        if header[257:263] not in (b"ustar\x00", b"ustar "):
            continue
        stored = parse_octal(header[148:156])
        if stored is None:
            continue
        calculated = sum(header[:148]) + sum(b" " * 8) + sum(header[156:])
        if calculated != stored:
            continue
        name = header[:100].split(ZERO, 1)[0].decode("utf-8", "replace")
        prefix = header[345:500].split(ZERO, 1)[0].decode("utf-8", "replace")
        full_name = f"{prefix}/{name}" if prefix else name
        size = parse_octal(header[124:136])
        if size is None or size < 0:
            continue
        payload_start = header_offset + 512
        payload_end = payload_start + size
        if payload_end > len(raw):
            continue
        typeflag = header[156:157].decode("ascii", "replace")
        yield full_name, header_offset, size, typeflag, raw[payload_start:payload_end]


def safe_filename(name: str) -> str:
    base = name.rsplit("/", 1)[-1] or "member"
    digest = hashlib.sha256(name.encode()).hexdigest()[:12]
    return f"{base}.{digest}.txt"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--member", action="append", default=[], help="Exact member name; repeatable")
    parser.add_argument("--pattern", action="append", default=[], help="Regular expression on member name; repeatable")
    parser.add_argument("--dry-run", action="store_true", help="Print the planned host-only extraction and write nothing")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input is not a regular file: {args.input}")
    if args.dry_run:
        selectors = list(args.member) + list(args.pattern)
        if not selectors:
            parser.error("provide --member and/or --pattern")
        print("DRY-RUN: no output written; no source is executed or built.")
        print(f"DRY-RUN: read {args.input} and write selected members under {args.output}")
        print("DRY-RUN: selectors=" + ", ".join(selectors))
        return 0
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")
    if not args.member and not args.pattern:
        parser.error("provide --member and/or --pattern")

    patterns = [re.compile(value, re.IGNORECASE) for value in args.pattern]
    wanted = set(args.member)
    raw = args.input.read_bytes()
    matches = []
    seen = set()
    for name, offset, size, typeflag, payload in parse_members(raw):
        if name in seen:
            continue
        seen.add(name)
        if name not in wanted and not any(pattern.search(name) for pattern in patterns):
            continue
        matches.append((name, offset, size, typeflag, payload))

    args.output.mkdir(parents=True)
    members_dir = args.output / "members"
    members_dir.mkdir()
    records = []
    for name, offset, size, typeflag, payload in sorted(matches):
        destination = members_dir / safe_filename(name)
        text = payload.decode("utf-8", "replace")
        numbered = "".join(f"{line_no:6d}\t{line}\n" for line_no, line in enumerate(text.splitlines(), 1))
        destination.write_text(numbered, encoding="utf-8")
        records.append(
            {
                "member": name,
                "header_offset": offset,
                "size": size,
                "typeflag": typeflag,
                "evidence_file": str(destination.relative_to(args.output)),
                "payload_sha256": hashlib.sha256(payload).hexdigest(),
            }
        )

    metadata = {
        "input": str(args.input),
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "input_bytes": len(raw),
        "valid_member_matches": len(records),
        "note": "Recovered decompressed tar slice; not a complete source archive.",
        "members": records,
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (args.output / "README.txt").write_text(
        "Host-only extraction from a bounded recovered source slice.\n"
        "Extracted text is evidence only; no extracted source was executed or built.\n",
        encoding="utf-8",
    )
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
