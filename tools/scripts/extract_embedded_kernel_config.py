#!/usr/bin/env python3
"""Extract Linux IKCONFIG from an uncompressed kernel Image, host-only."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import pathlib


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
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

    image = args.image.read_bytes()
    start_marker = b"IKCFG_ST"
    end_marker = b"IKCFG_ED"
    start = image.find(start_marker)
    if start < 0:
        raise SystemExit("IKCFG_ST not found")
    start += len(start_marker)
    end = image.find(end_marker, start)
    if end < 0:
        raise SystemExit("IKCFG_ED not found")
    compressed = image[start:end]
    config = gzip.decompress(compressed)
    args.output.mkdir(parents=True)
    (args.output / "kernel.config").write_bytes(config)
    metadata = {
        "image": str(args.image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "marker_start": start - len(start_marker),
        "marker_end": end,
        "compressed_size": len(compressed),
        "config_size": len(config),
        "config_sha256": hashlib.sha256(config).hexdigest(),
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    (args.output / "sha256sums.txt").write_text(
        f"{metadata['config_sha256']}  kernel.config\n"
        f"{metadata['image_sha256']}  {args.image}\n"
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
