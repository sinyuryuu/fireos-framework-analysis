#!/usr/bin/env python3
"""Compare preserved PS7330 properties with PS7331 OTA build properties."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


KEYS = (
    "ro.build.id",
    "ro.build.fingerprint",
    "ro.build.version.security_patch",
    "ro.build.version.incremental",
    "ro.build.version.name",
    "ro.product.device",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def parse_props(path: Path, android_prop_format: bool) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if android_prop_format:
            match = re.match(r"\[([^]]+)\]: \[([^]]*)\]$", line)
        else:
            match = re.match(r"([^=]+)=(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2)
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ps7330-props", type=Path, required=True)
    parser.add_argument("--ps7331-build-prop", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print("DRY-RUN: no files will be read or written.")
        print(f"PS7330\t{args.ps7330_props}")
        print(f"PS7331\t{args.ps7331_build_prop}")
        print(f"OUTPUT\t{args.output}")
        return 0
    if args.output.exists():
        print(f"ERROR: output already exists: {args.output}", file=sys.stderr)
        return 2
    if not args.ps7330_props.is_file() or not args.ps7331_build_prop.is_file():
        print("ERROR: input file missing", file=sys.stderr)
        return 2
    old = parse_props(args.ps7330_props, True)
    new = parse_props(args.ps7331_build_prop, False)
    rows = []
    for key in KEYS:
        old_value = old.get(key, "NOT_PRESENT")
        new_value = new.get(key, "NOT_PRESENT")
        rows.append(
            {
                "key": key,
                "ps7330": old_value,
                "ps7331": new_value,
                "changed": old_value != new_value,
            }
        )
    args.output.mkdir(parents=True)
    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_io": False,
        "inputs": {
            "ps7330": {"path": str(args.ps7330_props), "sha256": sha256(args.ps7330_props)},
            "ps7331": {"path": str(args.ps7331_build_prop), "sha256": sha256(args.ps7331_build_prop)},
        },
        "rows": rows,
        "decision": {
            "security_patch_delta": (
                old.get("ro.build.version.security_patch", "NOT_PRESENT"),
                new.get("ro.build.version.security_patch", "NOT_PRESENT"),
            ),
            "same_product": old.get("ro.product.device") == new.get("ro.product.device"),
        },
    }
    (args.output / "comparison.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (args.output / "comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["key", "ps7330", "ps7331", "changed"])
        for row in rows:
            writer.writerow([row["key"], row["ps7330"], row["ps7331"], row["changed"]])
    print(f"Wrote host-only security delta to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
