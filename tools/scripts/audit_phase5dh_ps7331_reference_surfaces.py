#!/usr/bin/env python3
"""Compare bounded GhostLock reference surfaces with PS7331 evidence.

This host-only audit records configuration symbols and source presence only.
It does not extract offsets, compile code, invoke syscalls, contact a device,
or construct a kernel-memory primitive.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


SYMBOLS = (
    "CONFIG_FUTEX",
    "CONFIG_RT_MUTEXES",
    "CONFIG_CONFIGFS_FS",
    "CONFIG_USERFAULTFD",
    "CONFIG_SLUB",
    "CONFIG_SLUB_DEBUG",
    "CONFIG_SLUB_STATS",
    "CONFIG_SECCOMP",
    "CONFIG_SECCOMP_FILTER",
    "CONFIG_RANDOMIZE_BASE",
)

SOURCE_MARKERS = (
    ("configfs_source", re.compile(r"configfs", re.IGNORECASE)),
    ("pipe_buffer_source", re.compile(r"struct pipe_buffer|pipe_buf_operations")),
    ("anon_pipe_ops_source", re.compile(r"anon_pipe_buf_ops")),
    ("userfaultfd_source", re.compile(r"userfaultfd", re.IGNORECASE)),
    ("requeue_pi_source", re.compile(r"FUTEX_CMP_REQUEUE_PI")),
    ("proxy_lock_source", re.compile(r"rt_mutex_start_proxy_lock")),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"^(CONFIG_[A-Z0-9_]+)=(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2)
            continue
        match = re.match(r"^# (CONFIG_[A-Z0-9_]+) is not set$", line)
        if match:
            values[match.group(1)] = "not set"
    return values


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(
            json.dumps(
                {
                    "kernel_root": str(args.kernel_root),
                    "config": str(args.config),
                    "output": str(args.output),
                    "device_contacted": False,
                    "source_executed": False,
                    "offsets_extracted": False,
                },
                indent=2,
            )
        )
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    if not args.kernel_root.is_dir() or not args.config.is_file():
        raise FileNotFoundError("kernel root or config is missing")
    args.output.mkdir(parents=True)

    config_values = parse_config(args.config)
    rows: list[dict[str, object]] = []
    for symbol in SYMBOLS:
        value = config_values.get(symbol, "not observed")
        rows.append(
            {
                "surface": "config",
                "name": symbol,
                "value": value,
                "evidence": str(args.config),
                "interpretation": (
                    "explicit extracted IKCONFIG value"
                    if value != "not observed"
                    else "not observed; not treated as disabled"
                ),
            }
        )

    source_files = [
        path
        for path in args.kernel_root.rglob("*")
        if path.is_file() and path.suffix in {".c", ".h", ".S"}
    ]
    source_counts: dict[str, int] = {name: 0 for name, _ in SOURCE_MARKERS}
    source_examples: dict[str, list[str]] = {name: [] for name, _ in SOURCE_MARKERS}
    for path in source_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = path.relative_to(args.kernel_root).as_posix()
        for name, pattern in SOURCE_MARKERS:
            if pattern.search(text):
                source_counts[name] += 1
                if len(source_examples[name]) < 8:
                    source_examples[name].append(relative)
    for name, _ in SOURCE_MARKERS:
        rows.append(
            {
                "surface": "source",
                "name": name,
                "value": source_counts[name],
                "evidence": ";".join(source_examples[name]),
                "interpretation": "source-file presence count only",
            }
        )

    matrix_path = args.output / "surface-matrix.csv"
    write_csv(
        matrix_path,
        ["surface", "name", "value", "evidence", "interpretation"],
        rows,
    )
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "kernel_root": str(args.kernel_root),
        "config": str(args.config),
        "config_sha256": sha256(args.config),
        "source_file_count": len(source_files),
        "config_values": {symbol: config_values.get(symbol, "not observed") for symbol in SYMBOLS},
        "source_counts": source_counts,
        "device_contacted": False,
        "source_executed": False,
        "offsets_extracted": False,
        "kernel_memory_accessed": False,
        "root_or_privilege_gain_proven": False,
        "interpretation": (
            "Generic source/config surface presence does not establish that a "
            "reference post-trigger primitive exists, is reachable, or is safe "
            "to test on PS7331."
        ),
    }
    summary_path = args.output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest = args.output / "sha256sums.txt"
    manifest.write_text(
        "\n".join(
            f"{sha256(path)}  {path.name}" for path in (matrix_path, summary_path)
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
