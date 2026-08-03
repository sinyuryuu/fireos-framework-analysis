#!/usr/bin/env python3
"""Validate the Phase 5V Bluetooth CVE evidence boundary.

This is a host-only evidence helper.  It never imports adb, opens a device
node, changes settings, enables Bluetooth, downloads code, or executes a
binary from the device.  ``--dry-run`` validates inputs and prints the planned
derived files without writing them.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


REQUIRED_REPORT_MARKERS = (
    "PS7330.4104N",
    "MT8183",
    "AmazonBtPolicyManagerAdapter",
    "FosGattService",
)


def sha256(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_file(file_path: Path) -> None:
    if not file_path.is_file():
        raise SystemExit(f"missing input file: {file_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-report", type=Path, required=True)
    parser.add_argument("--evidence-index", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    require_file(args.device_report)
    require_file(args.evidence_index)
    if not args.artifact_dir.is_dir():
        raise SystemExit(f"missing artifact directory: {args.artifact_dir}")

    report_text = args.device_report.read_text(encoding="utf-8", errors="replace")
    missing = [marker for marker in REQUIRED_REPORT_MARKERS if marker not in report_text]
    if missing:
        raise SystemExit("device report is missing markers: " + ", ".join(missing))

    artifact_files = sorted(
        path for path in args.artifact_dir.rglob("*") if path.is_file()
    )
    if not artifact_files:
        raise SystemExit(f"artifact directory is empty: {args.artifact_dir}")

    input_files = [args.device_report, args.evidence_index, *artifact_files]
    lines = [f"{sha256(path)}\t{path}" for path in input_files]
    planned = [
        args.output / "metadata.tsv",
        args.output / "input-hashes.tsv",
        args.output / "result.md",
        args.output / "sha256sums.txt",
    ]

    print("mode=" + ("dry-run" if args.dry_run else "write-derived-output"))
    print(f"validated_inputs={len(input_files)}")
    print(f"artifact_files={len(artifact_files)}")
    for path in planned:
        print(f"planned={path}")

    if args.dry_run:
        return 0

    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "input-hashes.tsv").write_text(
        "sha256\tpath\n" + "\n".join(lines) + "\n", encoding="utf-8"
    )
    (args.output / "metadata.tsv").write_text(
        "field\tvalue\n"
        "mode\thost-only\n"
        f"device-report\t{args.device_report}\n"
        f"evidence-index\t{args.evidence_index}\n"
        f"artifact-dir\t{args.artifact_dir}\n"
        f"input-count\t{len(input_files)}\n",
        encoding="utf-8",
    )
    (args.output / "result.md").write_text(
        "# Phase 5V derived validation\n\n"
        f"Validated {len(input_files)} preserved host-side inputs.\n\n"
        "No device connection, Bluetooth activation, input injection, Binder "
        "call, native execution, or exploit operation is performed by this script.\n",
        encoding="utf-8",
    )
    manifest_entries = []
    for file_path in sorted(args.output.iterdir()):
        if file_path.name == "sha256sums.txt":
            continue
        manifest_entries.append(f"{sha256(file_path)}  {file_path.name}")
    (args.output / "sha256sums.txt").write_text(
        "\n".join(manifest_entries) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
