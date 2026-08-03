#!/usr/bin/env python3
"""Extract selected source members from an arbitrary recovered tar slice.

The input is a host-side reconstructed slice of the official Fire OS source
archive.  It may begin in the middle of the tar stream, so the extractor
locates and validates ustar headers instead of invoking tar.  It writes only
small, line-numbered excerpts and metadata; it never touches a device or
executes source content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


TARGETS: dict[str, str] = {
    "cmdq_make": "kernel/mediatek/4.4/drivers/misc/mediatek/cmdq/Makefile",
    "mt8183_defconfig": "kernel/mediatek/4.4/arch/arm/configs/mt8183_defconfig",
    "v2_core": "kernel/mediatek/4.4/drivers/misc/mediatek/cmdq/v2/cmdq_core.c",
    "v2_core_header": "kernel/mediatek/4.4/drivers/misc/mediatek/cmdq/v2/cmdq_core.h",
    "v2_driver": "kernel/mediatek/4.4/drivers/misc/mediatek/cmdq/v2/cmdq_driver.c",
    "v2_header": "kernel/mediatek/4.4/drivers/misc/mediatek/cmdq/v2/cmdq_driver.h",
    "v3_device": "kernel/mediatek/4.4/drivers/misc/mediatek/cmdq/v3/cmdq_device.c",
    "v3_driver": "kernel/mediatek/4.4/drivers/misc/mediatek/cmdq/v3/cmdq_driver.c",
    "v3_header": "kernel/mediatek/4.4/drivers/misc/mediatek/cmdq/v3/cmdq_driver.h",
    "v3_make": "kernel/mediatek/4.4/drivers/misc/mediatek/cmdq/v3/Makefile",
}

EXCERPTS: dict[str, tuple[tuple[int, int], ...]] = {
    "cmdq_make": ((14, 21),),
    "mt8183_defconfig": ((1260, 1260), (1354, 1355)),
    "v2_core": ((8360, 8454), (8456, 8487), (8489, 8573)),
    "v2_core_header": ((112, 120),),
    "v2_driver": ((709, 752), (973, 982)),
    "v2_header": ((46, 74),),
    "v3_device": ((473, 522),),
    "v3_driver": ((52, 55), (120, 178), (663, 706), (708, 746), (817, 909), (947, 1045)),
    "v3_header": ((47, 85),),
    "v3_make": ((14, 29), (80, 95)),
}


def die(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def octal_field(field: bytes) -> int:
    value = field.split(b"\0", 1)[0].strip() or b"0"
    return int(value, 8)


def valid_header(header: bytes) -> bool:
    if len(header) != 512:
        return False
    magic = header[257:263]
    if magic not in (b"ustar\0", b"ustar "):
        return False
    try:
        stored = octal_field(header[148:156])
    except ValueError:
        return False
    calculated = sum(header[:148] + b"        " + header[156:])
    return stored == calculated


def iter_members(data: bytes) -> Iterable[tuple[str, int, bytes]]:
    seen_offsets: set[int] = set()
    for magic in (b"ustar\0", b"ustar "):
        start = 0
        while True:
            marker = data.find(magic, start)
            if marker < 0:
                break
            header_offset = marker - 257
            start = marker + 1
            if header_offset in seen_offsets:
                continue
            seen_offsets.add(header_offset)
            header_end = header_offset + 512
            if header_offset < 0 or header_end > len(data):
                continue
            header = data[header_offset:header_end]
            if not valid_header(header):
                continue
            name = header[0:100].split(b"\0", 1)[0].decode("utf-8", "replace")
            prefix = header[345:500].split(b"\0", 1)[0].decode("utf-8", "replace")
            member = f"{prefix}/{name}" if prefix else name
            try:
                size = octal_field(header[124:136])
            except ValueError:
                continue
            content_start = header_end
            content_end = content_start + size
            if content_end <= len(data):
                yield member, header_offset, data[content_start:content_end]


def excerpt_text(member: str, content: bytes, ranges: tuple[tuple[int, int], ...]) -> str:
    text = content.decode("utf-8", "replace").splitlines()
    output = [f"/* source member: {member} */", "/* line numbers are from the recovered source member */", ""]
    for start, end in ranges:
        output.append(f"/* BEGIN source lines {start}-{end} */")
        for line_number in range(start, min(end, len(text)) + 1):
            output.append(f"{line_number:5d}\t{text[line_number - 1]}")
        output.append(f"/* END source lines {start}-{end} */")
        output.append("")
    return "\n".join(output).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path, help="reconstructed tar slice")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(f"DRY-RUN: read {args.input}")
        print(f"DRY-RUN: locate and validate ustar members: {', '.join(TARGETS.values())}")
        print(f"DRY-RUN: write excerpts and metadata under {args.output}")
        return 0

    if not args.input.is_file():
        die(f"input is not a regular file: {args.input}")
    if args.output.exists():
        die(f"output already exists: {args.output}")

    data = args.input.read_bytes()
    input_sha256 = hashlib.sha256(data).hexdigest()
    found: dict[str, tuple[int, bytes]] = {}
    for member, header_offset, content in iter_members(data):
        for key, target in TARGETS.items():
            if member == target and key not in found:
                found[key] = (header_offset, content)

    missing = sorted(set(TARGETS) - set(found))
    if missing:
        die("target members not found in the supplied slice: " + ", ".join(missing))

    args.output.mkdir(parents=True)
    records = []
    for key, target in TARGETS.items():
        header_offset, content = found[key]
        output_file = args.output / f"{key}-excerpt.txt"
        output_file.write_text(excerpt_text(target, content, EXCERPTS[key]), encoding="utf-8")
        records.append(
            {
                "key": key,
                "member": target,
                "header_offset_in_reconstructed_slice": header_offset,
                "member_bytes": len(content),
                "member_sha256": hashlib.sha256(content).hexdigest(),
                "excerpt_file": output_file.name,
                "excerpt_ranges": EXCERPTS[key],
            }
        )

    (args.output / "metadata.json").write_text(
        json.dumps(
            {
                "input": str(args.input),
                "input_bytes": len(data),
                "input_sha256": input_sha256,
                "targets": records,
                "host_only": True,
                "device_operations": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Extracted {len(records)} source members to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
