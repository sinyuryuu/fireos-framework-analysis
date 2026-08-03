#!/usr/bin/env python3
"""Extract embedded dex/cdex blobs from Android VDEX files.

This performs container extraction only. It does not decompact compact-dex,
deodex an ELF oat file, or claim that extracted bytecode is executable by a
host tool. Those transformations require a separately versioned toolchain.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from pathlib import Path


MAGICS = (b"cdex001\x00", b"dex\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    if not args.input.is_file():
        print(f"input is not a file: {args.input}", file=sys.stderr)
        return 2
    data = args.input.read_bytes()
    if not data.startswith(b"vdex"):
        print(f"input does not start with VDEX magic: {args.input}", file=sys.stderr)
        return 2
    if len(data) < 16:
        print("VDEX header is truncated", file=sys.stderr)
        return 2

    dex_count = struct.unpack_from("<I", data, 12)[0]
    candidates: list[tuple[int, int, bytes]] = []
    cursor = 0
    while cursor < len(data):
        offsets = [data.find(magic, cursor) for magic in MAGICS]
        offsets = [offset for offset in offsets if offset >= 0]
        if not offsets:
            break
        offset = min(offsets)
        if offset + 0x24 > len(data):
            break
        file_size = struct.unpack_from("<I", data, offset + 0x20)[0]
        if file_size == 0 or file_size > len(data) - offset:
            cursor = offset + 1
            continue
        magic = next(magic for magic in MAGICS if data.startswith(magic, offset))
        candidates.append((offset, file_size, magic))
        cursor = offset + file_size

    # The verifier-deps area can contain dex-like strings. Keep only a
    # non-overlapping set and respect the VDEX header's dex count when present.
    selected: list[tuple[int, int, bytes]] = []
    for candidate in candidates:
        if selected and candidate[0] < selected[-1][0] + selected[-1][1]:
            continue
        selected.append(candidate)
        if dex_count and len(selected) == dex_count:
            break
    if not selected:
        print(f"no embedded dex/cdex blobs found in {args.input}", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.input.name.rsplit(".", 1)[0]
    outputs: list[Path] = []
    for index, (offset, file_size, magic) in enumerate(selected):
        suffix = "cdex" if magic.startswith(b"cdex") else "dex"
        output = args.output_dir / f"{stem}_{index}.{suffix}"
        if output.exists():
            print(f"refusing to overwrite existing output: {output}", file=sys.stderr)
            return 2
        output.write_bytes(data[offset : offset + file_size])
        outputs.append(output)

    manifest = args.output_dir / f"{stem}_manifest.tsv"
    if manifest.exists():
        print(f"refusing to overwrite existing output: {manifest}", file=sys.stderr)
        return 2
    with manifest.open("w", encoding="utf-8") as handle:
        handle.write("index\toffset\tfile_size\tformat\tsha256\tpath\n")
        for index, ((offset, file_size, magic), output) in enumerate(zip(selected, outputs)):
            fmt = "cdex" if magic.startswith(b"cdex") else "dex"
            handle.write(f"{index}\t0x{offset:x}\t{file_size}\t{fmt}\t{sha256(output)}\t{output}\n")

    print(f"input={args.input}")
    print(f"declared_dex_count={dex_count}")
    print(f"extracted={len(outputs)}")
    print(f"manifest={manifest}")
    for output in outputs:
        print(f"output={output} sha256={sha256(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
