#!/usr/bin/env python3
"""Compare PS7331 build-input and runtime kernel config evidence.

This is a host-only provenance helper.  It reads already-preserved text
configuration files, never builds a kernel, downloads a source archive, or
contacts an Android device.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


FOCUS_KEYS = (
    "CONFIG_ARM64",
    "CONFIG_ARM64_4K_PAGES",
    "CONFIG_ARM64_VA_BITS",
    "CONFIG_ARM64_VA_BITS_39",
    "CONFIG_FUTEX",
    "CONFIG_RT_MUTEXES",
    "CONFIG_PREEMPT",
    "CONFIG_PREEMPT_COUNT",
    "CONFIG_RANDOMIZE_BASE",
    "CONFIG_THREAD_INFO_IN_TASK",
    "CONFIG_PANIC_ON_OOPS",
    "CONFIG_PANIC_ON_OOPS_VALUE",
    "CONFIG_SECURITY_SELINUX",
    "CONFIG_SECCOMP",
    "CONFIG_SECCOMP_FILTER",
    "CONFIG_ION",
    "CONFIG_MTK_ION",
    "CONFIG_MTK_CMDQ",
    "CONFIG_MTK_ENABLE_GENIEZONE",
    "CONFIG_DEBUG_RT_MUTEXES",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("# ") and line.endswith(" is not set"):
            key = line[2 : -len(" is not set")]
            values[key] = "n"
            continue
        if line.startswith("CONFIG_") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def record(label: str, path: Path) -> dict[str, object]:
    return {
        "label": label,
        "path": str(path),
        "available": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else 0,
        "sha256": sha256(path) if path.is_file() else "",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ps7330-runtime", type=Path, required=True)
    parser.add_argument("--ps7331-runtime", type=Path, required=True)
    parser.add_argument("--ps7331-defconfig", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    paths = {
        "ps7330_runtime": args.ps7330_runtime,
        "ps7331_runtime": args.ps7331_runtime,
        "ps7331_defconfig": args.ps7331_defconfig,
    }
    if args.output in {Path("/"), Path("."), Path("..")}:  # defensive scope check
        parser.error("refusing broad output path")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "inputs": {k: str(v) for k, v in paths.items()}}, indent=2))
        return 0
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        parser.error("missing input(s): " + ", ".join(missing))
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    configs = {key: parse_config(path) for key, path in paths.items()}
    rows: list[dict[str, str]] = []
    for key in FOCUS_KEYS:
        row = {"key": key}
        for label, values in configs.items():
            row[label] = values.get(key, "NOT_FOUND")
        row["runtime_equal"] = str(configs["ps7330_runtime"].get(key, "NOT_FOUND") == configs["ps7331_runtime"].get(key, "NOT_FOUND"))
        row["defconfig_matches_ps7331_runtime"] = str(configs["ps7331_defconfig"].get(key, "NOT_FOUND") == configs["ps7331_runtime"].get(key, "NOT_FOUND"))
        rows.append(row)

    args.output.mkdir(parents=True)
    with (args.output / "focus.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["key", "ps7330_runtime", "ps7331_runtime", "ps7331_defconfig", "runtime_equal", "defconfig_matches_ps7331_runtime"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "device_io": False,
        "source_execution": False,
        "records": [record(label, path) for label, path in paths.items()],
        "focus_keys": rows,
        "runtime_focus_equal": all(row["runtime_equal"] == "True" for row in rows),
        "defconfig_is_final_runtime_image": False,
        "interpretation": "A defconfig is build input, not proof of the final signed Image; runtime equality is reported separately.",
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in args.output.iterdir() if path.is_file())
    (args.output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files if path.name != "sha256sums.txt") + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
