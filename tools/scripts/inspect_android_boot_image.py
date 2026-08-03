#!/usr/bin/env python3
"""Inspect an Android boot image without executing or modifying it.

This parser is intentionally limited to provenance metadata and optional
host-side extraction of the kernel payload.  It does not parse or write any
Android partition and it does not infer a device exploit profile.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import struct
import sys


PAGE_ALIGN = lambda value, page: ((value + page - 1) // page) * page


def compression_name(data: bytes) -> str:
    signatures = {
        b"\x1f\x8b": "gzip",
        b"\x02\x21\x4c\x18": "lz4",
        b"\x28\xb5\x2f\xfd": "zstd",
        b"\xfd7zXZ\x00": "xz",
        b"\x5d\x00\x00": "lzma-or-legacy-lzma",
    }
    for signature, name in signatures.items():
        if data.startswith(signature):
            return name
    return "unknown"


def parse_header(blob: bytes) -> dict:
    if len(blob) < 2048 or blob[:8] != b"ANDROID!":
        raise ValueError("not an Android boot image v0/v1 header")

    # Android boot_img_hdr up to the 16-byte name field.  This is the v0/v1
    # layout used by the PS7331 image currently in the workspace.
    fields = struct.unpack_from("<8s10I16s512s32s", blob, 0)
    (
        magic,
        kernel_size,
        kernel_addr,
        ramdisk_size,
        ramdisk_addr,
        second_size,
        second_addr,
        tags_addr,
        page_size,
        dt_size,
        unused,
        name,
        cmdline,
        image_id,
    ) = fields
    if page_size == 0 or page_size & (page_size - 1):
        raise ValueError(f"invalid page size: {page_size}")

    kernel_offset = page_size
    ramdisk_offset = kernel_offset + PAGE_ALIGN(kernel_size, page_size)
    second_offset = ramdisk_offset + PAGE_ALIGN(ramdisk_size, page_size)
    dt_offset = second_offset + PAGE_ALIGN(second_size, page_size)
    image_size = len(blob)

    return {
        "magic": magic.decode("ascii", "replace"),
        "kernel_size": kernel_size,
        "kernel_addr": f"0x{kernel_addr:08x}",
        "ramdisk_size": ramdisk_size,
        "ramdisk_addr": f"0x{ramdisk_addr:08x}",
        "second_size": second_size,
        "second_addr": f"0x{second_addr:08x}",
        "tags_addr": f"0x{tags_addr:08x}",
        "page_size": page_size,
        "dt_size": dt_size,
        "name": name.split(b"\0", 1)[0].decode("ascii", "replace"),
        "cmdline": cmdline.split(b"\0", 1)[0].decode("ascii", "replace"),
        "image_id_sha1_prefix": image_id.hex(),
        "kernel_offset": kernel_offset,
        "ramdisk_offset": ramdisk_offset,
        "second_offset": second_offset,
        "dt_offset": dt_offset,
        "image_size": image_size,
        "layout_end": dt_offset + dt_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--extract-kernel", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.output in {pathlib.Path("/"), pathlib.Path("."), pathlib.Path("..")}:  # noqa: PLR2004
        parser.error("refusing broad output path")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "image": str(args.image), "output": str(args.output)}, indent=2))
        return 0
    if not args.image.is_file():
        parser.error(f"image is not a regular file: {args.image}")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    blob = args.image.read_bytes()
    metadata = parse_header(blob)
    kernel_start = metadata["kernel_offset"]
    kernel_end = kernel_start + metadata["kernel_size"]
    if metadata["layout_end"] > len(blob) or kernel_end > len(blob):
        raise ValueError("boot image is truncated according to its header")
    kernel = blob[kernel_start:kernel_end]
    metadata.update(
        {
            "image_sha256": hashlib.sha256(blob).hexdigest(),
            "kernel_sha256": hashlib.sha256(kernel).hexdigest(),
            "kernel_compression_signature": compression_name(kernel),
        }
    )

    args.output.mkdir(parents=True)
    (args.output / "boot-image-metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "input.sha256").write_text(
        f"{metadata['image_sha256']}  {args.image}\n", encoding="utf-8"
    )
    if args.extract_kernel:
        (args.output / "kernel.payload").write_bytes(kernel)
        (args.output / "kernel.payload.sha256").write_text(
            f"{metadata['kernel_sha256']}  kernel.payload\n", encoding="utf-8"
        )
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
