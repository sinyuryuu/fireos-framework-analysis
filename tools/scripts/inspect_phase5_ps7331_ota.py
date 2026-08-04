#!/usr/bin/env python3
"""Inspect a preserved Fire OS OTA without installing or extracting images.

The script reads ZIP metadata and selected text members only.  It never talks
to a device, executes an updater, writes a partition, or extracts boot/system
images.  The output directory must not already exist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


TEXT_MEMBERS = (
    "META-INF/com/android/metadata",
    "META-INF/com/android/otacert",
    "META-INF/com/google/android/updater-script",
    "META-INF/com/amazon/android/target.blocklist",
    "META-INF/com/amazon/android/target.system.devicepath",
    "ota.prop",
    "system/build.prop",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_or_empty(archive: zipfile.ZipFile, member: str) -> str:
    try:
        return archive.read(member).decode("utf-8", errors="replace")
    except KeyError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ota", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output in {Path("/"), Path("."), Path("..")}:  # defensive scope check
        parser.error("refusing broad output path")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "ota": str(args.ota), "output": str(args.output)}, indent=2))
        return 0
    if not args.ota.is_file():
        parser.error(f"OTA does not exist: {args.ota}")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.ota) as archive:
        infos = sorted(archive.infolist(), key=lambda info: info.filename)
        (args.output / "members.tsv").write_text(
            "member\tcompressed_size\tuncompressed_size\tcrc32\tcompression\n"
            + "\n".join(
                f"{info.filename}\t{info.compress_size}\t{info.file_size}\t{info.CRC:08x}\t{info.compress_type}"
                for info in infos
            )
            + "\n",
            encoding="utf-8",
        )
        for member in TEXT_MEMBERS:
            text = text_or_empty(archive, member)
            if member == "META-INF/com/android/otacert":
                output_name = "otacert.pem"
            elif member == "META-INF/com/google/android/updater-script":
                output_name = "updater-script.txt"
            elif member == "META-INF/com/amazon/android/target.blocklist":
                output_name = "target.blocklist.json"
            elif member == "META-INF/com/amazon/android/target.system.devicepath":
                output_name = "target.system.devicepath"
            elif member == "META-INF/com/android/metadata":
                output_name = "android-metadata.txt"
            elif member == "ota.prop":
                output_name = "ota.prop"
            else:
                output_name = "system-build.prop"
            (args.output / output_name).write_text(text, encoding="utf-8")

        compatibility = archive.read("compatibility.zip")
    (args.output / "compatibility.zip").write_bytes(compatibility)
    with zipfile.ZipFile(args.output / "compatibility.zip") as compatibility_zip:
        compatibility_dir = args.output / "compatibility"
        compatibility_dir.mkdir()
        for info in compatibility_zip.infolist():
            if info.is_dir():
                continue
            target = compatibility_dir / Path(info.filename).name
            target.write_bytes(compatibility_zip.read(info.filename))

    metadata = {
        "device_io": False,
        "image_extraction": False,
        "updater_execution": False,
        "ota_path": str(args.ota),
        "ota_bytes": args.ota.stat().st_size,
        "ota_sha256": sha256(args.ota),
        "zip_member_count": len(infos),
        "selected_text_members": list(TEXT_MEMBERS),
        "note": "Metadata-only inspection; no OTA member was installed or written to a device.",
    }
    (args.output / "summary.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.relative_to(args.output)}" for path in files) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote metadata-only OTA inspection to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
