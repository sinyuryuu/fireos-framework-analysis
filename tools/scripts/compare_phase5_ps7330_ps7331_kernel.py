#!/usr/bin/env python3
"""Compare preserved PS7330 evidence with an adjacent PS7331 reference.

Host-only and evidence-oriented.  Missing files are reported as UNKNOWN; the
script never downloads, executes, flashes, or talks to an Android device.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize(path: Path) -> str:
    return "\n".join(line.rstrip() for line in path.read_text(errors="replace").splitlines()) + "\n"


def file_record(label: str, path: Path | None) -> dict[str, object]:
    if path is None:
        return {"label": label, "path": "", "available": False, "sha256": "", "bytes": 0}
    if not path.is_file():
        return {"label": label, "path": str(path), "available": False, "sha256": "", "bytes": 0}
    return {"label": label, "path": str(path), "available": True, "sha256": sha256(path), "bytes": path.stat().st_size}


def compare_text(label: str, left: Path | None, right: Path | None) -> dict[str, object]:
    row = file_record(label + ":ps7330", left)
    row.update({"right_path": str(right) if right else "", "right_available": bool(right and right.is_file())})
    if left is None or right is None or not left.is_file() or not right.is_file():
        row.update({"comparison": "UNKNOWN_MISSING_INPUT", "left_sha256": row.get("sha256", ""), "right_sha256": ""})
        if right and right.is_file():
            row["right_sha256"] = sha256(right)
        return row
    left_text = normalize(left)
    right_text = normalize(right)
    row.update(
        {
            "left_sha256": hashlib.sha256(left_text.encode()).hexdigest(),
            "right_sha256": hashlib.sha256(right_text.encode()).hexdigest(),
            "comparison": "IDENTICAL_NORMALIZED" if left_text == right_text else "DIFFERENT_NORMALIZED",
        }
    )
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ps7330-config", type=Path, required=True)
    parser.add_argument("--ps7331-config", type=Path, required=True)
    parser.add_argument("--ps7330-source", type=Path)
    parser.add_argument("--ps7331-source", type=Path)
    parser.add_argument("--ps7331-boot", type=Path, required=True)
    parser.add_argument("--ps7331-image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output in {Path("/"), Path("."), Path("..")}:  # defensive scope check
        parser.error("refusing broad output path")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "output": str(args.output)}, indent=2))
        return 0
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    args.output.mkdir(parents=True)
    records = [
        file_record("PS7331 boot.img", args.ps7331_boot),
        file_record("PS7331 decompressed Image", args.ps7331_image),
    ]
    comparisons = [
        compare_text("kernel config", args.ps7330_config, args.ps7331_config),
        compare_text("rtmutex source", args.ps7330_source, args.ps7331_source),
    ]
    (args.output / "summary.json").write_text(
        json.dumps({"device_io": False, "source_execution": False, "records": records, "comparisons": comparisons}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with (args.output / "comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["label", "comparison", "path", "right_path", "available", "right_available", "sha256", "left_sha256", "right_sha256", "bytes"]
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in comparisons:
            writer.writerow(row)
        for row in records:
            writer.writerow({"label": row["label"], "comparison": "REFERENCE_ONLY", "path": row["path"], "available": row["available"], "sha256": row["sha256"], "bytes": row["bytes"]})
    (args.output / "README.txt").write_text(
        "Host-only comparison. Missing PS7331 source members remain UNKNOWN; no device, bootloader, partition, or executable source operation was used.\n",
        encoding="utf-8",
    )
    files = sorted(p for p in args.output.iterdir() if p.is_file() and p.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
