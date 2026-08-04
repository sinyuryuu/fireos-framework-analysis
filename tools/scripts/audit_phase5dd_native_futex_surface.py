#!/usr/bin/env python3
"""Inventory futex-related markers in preserved Fire ELF artifacts.

This is a host-only metadata/string/symbol scan.  It does not execute an ELF,
disassemble a trigger, infer kernel addresses, generate syscall arguments, or
contact a device.  A marker is evidence about an artifact surface only; it is
not proof of a particular syscall or runtime call edge.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


MARKER_PATTERNS = {
    "named_requeue_pi": re.compile(r"requeue[ _-]?pi", re.IGNORECASE),
    "futex": re.compile(r"futex", re.IGNORECASE),
    "rtmutex": re.compile(r"rtmutex|rt_mutex", re.IGNORECASE),
    "pthread_condition": re.compile(r"pthread_cond|conditionvariable", re.IGNORECASE),
    "pi_helper": re.compile(r"__futex_pi|futex_pi|PIMutex|PI mutex", re.IGNORECASE),
    "syscall_word": re.compile(r"\bsyscall\b", re.IGNORECASE),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def command_output(command: list[str]) -> str:
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return (result.stdout + result.stderr).strip()


def files_from_inputs(roots: list[Path], explicit: list[Path]) -> list[Path]:
    paths: set[Path] = set()
    for root in roots:
        if not root.exists():
            raise FileNotFoundError(f"input root does not exist: {root}")
        if root.is_file():
            paths.add(root)
        else:
            paths.update(
                path for path in root.rglob("*")
                if path.is_file() and not path.name.endswith((".txt", ".json", ".csv"))
            )
    for path in explicit:
        if not path.is_file():
            raise FileNotFoundError(f"input file does not exist: {path}")
        paths.add(path)
    return sorted(paths)


def scan_file(path: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    file_description = command_output(["file", "-b", str(path)])
    strings_text = command_output(["strings", "-a", "-n", "4", str(path)])
    symbols_text = command_output(["nm", "-D", "-C", str(path)])
    symbol_names = [
        "symbol:" + line.split()[-1]
        for line in symbols_text.splitlines()
        if line.split()
    ]
    combined = strings_text.splitlines() + symbol_names

    marker_counts: Counter[str] = Counter()
    marker_rows: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for line in combined:
        normalized = " ".join(line.strip().split())
        if not normalized:
            continue
        for marker, pattern in MARKER_PATTERNS.items():
            if pattern.search(normalized):
                marker_counts[marker] += 1
                key = (marker, normalized)
                if key not in seen and len([row for row in marker_rows if row["path"] == str(path)]) < 32:
                    marker_rows.append({"path": str(path), "marker": marker, "excerpt": normalized[:240]})
                    seen.add(key)

    symbols_have_syscall = any(
        re.search(r"^U\s+syscall(?:@.*)?$", line.strip())
        or re.search(r"^U\s+.*\bsyscall(?:@.*)?$", line.strip())
        for line in symbols_text.splitlines()
    )
    result = "no_named_requeue_pi_marker"
    if marker_counts["named_requeue_pi"]:
        result = "named_requeue_pi_marker"
    elif marker_counts["futex"] or marker_counts["pi_helper"]:
        result = "ordinary_or_pi_helper_marker_only"
    elif symbols_have_syscall:
        result = "generic_syscall_boundary_only"
    return (
        {
            "path": str(path),
            "sha256": sha256(path),
            "size": path.stat().st_size,
            "file_description": file_description,
            "result": result,
            "syscall_import_observed": symbols_have_syscall,
            **{f"{key}_count": marker_counts[key] for key in MARKER_PATTERNS},
        },
        marker_rows,
    )


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    return sha256(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", action="append", type=Path, default=[])
    parser.add_argument("--input-file", action="append", type=Path, default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.input_root and not args.input_file:
        parser.error("at least one --input-root or --input-file is required")
    if args.dry_run:
        print(json.dumps({
            "input_roots": [str(path) for path in args.input_root],
            "input_files": [str(path) for path in args.input_file],
            "output": str(args.output),
            "device_contacted": False,
            "elf_executed": False,
        }, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)
    inputs = files_from_inputs(args.input_root, args.input_file)
    rows: list[dict[str, object]] = []
    marker_rows: list[dict[str, object]] = []
    for path in inputs:
        description = command_output(["file", "-b", str(path)])
        if "ELF" not in description:
            continue
        row, markers = scan_file(path)
        rows.append(row)
        marker_rows.extend(markers)

    fields = [
        "path", "sha256", "size", "file_description", "result",
        "syscall_import_observed", "named_requeue_pi_count", "futex_count",
        "rtmutex_count", "pthread_condition_count", "pi_helper_count",
        "syscall_word_count",
    ]
    inventory = args.output / "native-futex-surface.csv"
    markers = args.output / "native-futex-markers.csv"
    summary_path = args.output / "summary.json"
    write_csv(inventory, fields, rows)
    write_csv(markers, ["path", "marker", "excerpt"], marker_rows)
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_roots": [str(path) for path in args.input_root],
        "input_files": [str(path) for path in args.input_file],
        "input_files_seen": len(inputs),
        "elf_files_scanned": len(rows),
        "result_counts": dict(Counter(str(row["result"]) for row in rows)),
        "named_requeue_pi_files": [row["path"] for row in rows if row["result"] == "named_requeue_pi_marker"],
        "generic_syscall_boundary_files": [row["path"] for row in rows if row["result"] == "generic_syscall_boundary_only"],
        "interpretation": (
            "String and symbol markers do not establish a syscall operation or runtime edge. "
            "A named requeue-PI marker would justify focused offline review; a generic syscall "
            "import remains non-specific."
        ),
        "safety": {
            "elf_executed": False,
            "device_contacted": False,
            "futex_triggered": False,
            "kernel_memory_accessed": False,
            "payload_or_address_generated": False,
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest = args.output / "sha256sums.txt"
    manifest.write_text(
        "\n".join(f"{sha256_file(path)}  {path.name}" for path in (inventory, markers, summary_path)) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
