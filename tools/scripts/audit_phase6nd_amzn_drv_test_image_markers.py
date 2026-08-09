#!/usr/bin/env python3
"""Compare source-specific amzn_drv_test strings with the official kernel Image.

Host-only provenance check.  It reads one member from the GPL tar stream and
one already extracted official boot Image, never executes either input, and
does not contact an Android device.  A missing string is bounded negative
evidence only; it is not a complete proof about generated configuration,
modules, SELinux, or runtime behavior.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import tarfile
from pathlib import Path


DRIVER_MEMBER = "device/amazon/kernel/driver/amzn_drv_test.c"
DEFAULT_MARKERS = (
    "amzn_drvs",
    "sign_of_life",
    "idme",
    "logger",
    "logger_loop",
    "no this test item",
    "sign_of_life_test",
    "idme_test",
    "logger_test",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_from_tar(archive: Path) -> bytes:
    with tarfile.open(archive, "r:") as tar:
        member = tar.getmember(DRIVER_MEMBER)
        stream = tar.extractfile(member)
        if stream is None:
            raise RuntimeError(f"unreadable source member: {DRIVER_MEMBER}")
        return stream.read()


def count_ascii(image: bytes, marker: str) -> int:
    return len(list(re.finditer(re.escape(marker.encode("ascii")), image)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.archive.is_file() or not args.image.is_file():
        parser.error("archive and image must be regular files")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error(f"refusing to overwrite non-empty output: {args.output}")
    args.output.mkdir(parents=True, exist_ok=True)

    source_bytes = source_from_tar(args.archive)
    source = source_bytes.decode("utf-8", errors="replace")
    image = args.image.read_bytes()
    source_markers = [marker for marker in DEFAULT_MARKERS if marker in source]
    rows: list[dict[str, object]] = []
    for marker in source_markers:
        rows.append({
            "marker": marker,
            "source_member": DRIVER_MEMBER,
            "source_present": True,
            "official_image_occurrences": count_ascii(image, marker),
            "classification": "image-marker-present" if count_ascii(image, marker) else "image-marker-not-observed",
        })

    table = args.output / "phase6nd-image-marker-audit.csv"
    with table.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    report = args.output / "phase6nd-image-marker-audit.md"
    absent = [row["marker"] for row in rows if row["official_image_occurrences"] == 0]
    present = [row for row in rows if row["official_image_occurrences"]]
    report.write_text(
        "# Phase 6ND — `amzn_drv_test` official Image marker audit\n\n"
        f"Archive: `{args.archive}`\n\n"
        f"Archive SHA-256: `{sha256(args.archive)}`\n\n"
        f"Official boot Image: `{args.image}`\n\n"
        f"Official boot Image SHA-256: `{sha256(args.image)}`\n\n"
        "## Scope\n\n"
        "The source member was read from the tar stream and the already extracted "
        "official kernel Image was searched as raw bytes. Nothing was executed; "
        "no device or kernel interface was contacted.\n\n"
        "## Result\n\n"
        f"Source-defined markers: `{len(rows)}`.\n\n"
        f"Markers observed in official Image: `{len(present)}`.\n\n"
        f"Source markers not observed in official Image: `{len(absent)}` "
        f"({', '.join(map(str, absent)) if absent else 'none'}).\n\n"
        "**Interpretation:** absence of the unique `amzn_drv_test` proc/test "
        "strings is bounded negative evidence against this driver being built "
        "into this Image in an unoptimized, literal-preserving form. It does not "
        "close loadable modules, generated `.config`, compiler elimination, "
        "SELinux, or runtime procfs existence. The common `idme` marker is not "
        "specific to the test driver and is not used as positive proof.\n\n"
        "See the CSV for exact counts and the input hash manifest for provenance.\n",
        encoding="utf-8",
    )

    manifest = args.output / "sha256sums.txt"
    outputs = [report, table]
    manifest.write_text("".join(f"{sha256(path)}  {path.name}\n" for path in outputs), encoding="utf-8")
    input_manifest = args.output / "input-evidence-sha256sums.txt"
    input_manifest.write_text(
        f"archive_sha256 {sha256(args.archive)}  {args.archive.resolve()}\n"
        f"driver_member_sha256 {hashlib.sha256(source_bytes).hexdigest()}  {DRIVER_MEMBER}\n"
        f"image_sha256 {sha256(args.image)}  {args.image.resolve()}\n",
        encoding="utf-8",
    )
    print(f"markers={len(rows)} present={len(present)} absent={len(absent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
