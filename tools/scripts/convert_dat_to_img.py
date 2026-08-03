#!/usr/bin/env python3
"""Convert an Android BLOCK OTA .new.dat using its transfer list.

This deliberately supports the full-OTA operations used by the downloaded
Fire OS package (new/zero/erase).  It refuses incremental operations instead
of guessing their source blocks.  The output is always a new derived file and
is never allowed to overwrite an existing path.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


BLOCK_SIZE = 4096
RANGE_RE = re.compile(r"^([0-9]+)(?:,(.*))?$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transfer-list", required=True, type=Path)
    parser.add_argument("--new-dat", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def parse_ranges(raw: str) -> list[tuple[int, int]]:
    match = RANGE_RE.fullmatch(raw.strip())
    if not match:
        raise ValueError(f"invalid range expression: {raw!r}")
    count = int(match.group(1))
    values = [] if match.group(2) in (None, "") else [int(v) for v in match.group(2).split(",")]
    if count != len(values) or count % 2:
        raise ValueError(f"range count does not match endpoints: {raw!r}")
    ranges: list[tuple[int, int]] = []
    for start, end in zip(values[0::2], values[1::2]):
        if end < start:
            raise ValueError(f"descending range: {start},{end}")
        ranges.append((start, end))
    return ranges


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    config = parse_args()
    transfer_list = config.transfer_list.resolve()
    new_dat = config.new_dat.resolve()
    output = config.output.resolve()
    if not transfer_list.is_file() or not new_dat.is_file():
        print("transfer list and new.dat must be files", file=sys.stderr)
        return 2
    if output.exists():
        print(f"refusing to overwrite existing output: {output}", file=sys.stderr)
        return 2

    lines = [line.strip() for line in transfer_list.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) < 5:
        print("transfer list is missing the BLOCK OTA header", file=sys.stderr)
        return 2
    try:
        version = int(lines[0])
        total_blocks = int(lines[1])
    except ValueError as exc:
        print(f"invalid transfer-list header: {exc}", file=sys.stderr)
        return 2
    if version < 1:
        print(f"unsupported transfer-list version: {version}", file=sys.stderr)
        return 2

    operations = lines[4:]
    parsed: list[tuple[str, list[tuple[int, int]]]] = []
    unsupported: list[str] = []
    for line in operations:
        pieces = line.split(" ", 1)
        operation = pieces[0]
        if operation in {"new", "zero", "erase"}:
            if len(pieces) != 2:
                print(f"missing ranges for {operation}: {line}", file=sys.stderr)
                return 2
            try:
                ranges = parse_ranges(pieces[1])
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 2
            parsed.append((operation, ranges))
        else:
            unsupported.append(line)

    if unsupported:
        print("refusing unsupported/incremental operations:", file=sys.stderr)
        for line in unsupported[:20]:
            print(f"  {line}", file=sys.stderr)
        return 2

    new_blocks = sum(end - start for operation, ranges in parsed if operation == "new" for start, end in ranges)
    expected_bytes = new_blocks * BLOCK_SIZE
    source_size = new_dat.stat().st_size
    if config.dry_run:
        print("DRY-RUN: no output will be written.")
        print(f"DRY-RUN: version={version} total_blocks={total_blocks} operations={len(parsed)}")
        print(f"DRY-RUN: new_blocks={new_blocks} expected_new_dat_bytes={expected_bytes} source_bytes={source_size}")
        return 0
    if source_size < expected_bytes:
        print(f"new.dat is shorter than transfer list: {source_size} < {expected_bytes}", file=sys.stderr)
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    consumed = 0
    with new_dat.open("rb") as source, output.open("w+b") as destination:
        destination.truncate(total_blocks * BLOCK_SIZE)
        for operation, ranges in parsed:
            if operation != "new":
                continue
            for start, end in ranges:
                block_count = end - start
                byte_count = block_count * BLOCK_SIZE
                destination.seek(start * BLOCK_SIZE)
                remaining = byte_count
                while remaining:
                    chunk = source.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise RuntimeError("unexpected end of new.dat")
                    destination.write(chunk)
                    remaining -= len(chunk)
                consumed += byte_count

    digest = sha256_file(output)
    print(f"generated {output}")
    print(f"total_blocks={total_blocks} output_bytes={output.stat().st_size}")
    print(f"new_dat_consumed={consumed} new_dat_source={source_size} trailing_bytes={source_size - consumed}")
    print(f"sha256={digest}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
