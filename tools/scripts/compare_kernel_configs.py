#!/usr/bin/env python3
"""Compare two Linux .config files and report selected kernel gates."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib


FOCUS = (
    "FUTEX",
    "RT_MUTEXES",
    "PREEMPT",
    "KALLSYMS",
    "KALLSYMS_ALL",
    "RANDOMIZE_BASE",
    "ARM64",
    "ARM64_4K_PAGES",
    "ARM64_VA_BITS",
    "THREAD_INFO_IN_TASK",
    "DEBUG_INFO",
    "IKCONFIG",
    "SECURITY_SELINUX",
    "SECCOMP",
)


def parse_config(path: pathlib.Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("# CONFIG_") and line.endswith(" is not set"):
            values[line[2:-11]] = "not set"
        elif line.startswith("CONFIG_") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ps7330", required=True, type=pathlib.Path)
    parser.add_argument("--ps7331", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output in {pathlib.Path("/"), pathlib.Path("."), pathlib.Path("..")}:  # noqa: PLR2004
        parser.error("refusing broad output path")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "output": str(args.output)}, indent=2))
        return 0
    for path in (args.ps7330, args.ps7331):
        if not path.is_file():
            parser.error(f"config is not a regular file: {path}")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    old = parse_config(args.ps7330)
    new = parse_config(args.ps7331)
    keys = sorted(set(old) | set(new))
    rows = []
    for key in keys:
        rows.append(
            {
                "key": key,
                "ps7330": old.get(key, "ABSENT"),
                "ps7331": new.get(key, "ABSENT"),
                "changed": str(old.get(key, "ABSENT") != new.get(key, "ABSENT")).lower(),
                "focus": str(key.removeprefix("CONFIG_") in FOCUS).lower(),
            }
        )
    changed = [row for row in rows if row["changed"] == "true"]
    args.output.mkdir(parents=True)
    with (args.output / "config-diff.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "ps7330": str(args.ps7330),
        "ps7331": str(args.ps7331),
        "ps7330_sha256": hashlib.sha256(args.ps7330.read_bytes()).hexdigest(),
        "ps7331_sha256": hashlib.sha256(args.ps7331.read_bytes()).hexdigest(),
        "total_keys": len(keys),
        "changed_keys": len(changed),
        "changed_key_names": [row["key"] for row in changed],
        "focus_changes": [row for row in changed if row["focus"] == "true"],
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output / "sha256sums.txt").write_text(
        "\n".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}"
            for path in (args.output / "config-diff.csv", args.output / "summary.json")
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
