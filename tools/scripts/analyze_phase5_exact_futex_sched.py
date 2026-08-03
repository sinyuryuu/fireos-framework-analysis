#!/usr/bin/env python3
"""Analyze exact Fire OS futex/scheduler source against a pinned 4.4.146 tree.

This is a host-only evidence utility.  It normalizes the line-numbered source
files emitted by the Phase 5 extraction script, computes hashes and diffs, and
records selected Kconfig/runtime-config observations.  It does not compile,
execute, contact a device, invoke an exploit, or overwrite an existing output
directory.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from pathlib import Path


NUMBERED = re.compile(r"^\s*([0-9]+)\t(.*)$")
CONFIG = re.compile(r"^(?:# )?(CONFIG_[A-Za-z0-9_]+)(?: is not set|=(.*))$")

INTERESTING_CONFIGS = (
    "CONFIG_ARM64",
    "CONFIG_ARM64_4K_PAGES",
    "CONFIG_ARM64_VA_BITS_39",
    "CONFIG_PREEMPT",
    "CONFIG_RANDOMIZE_BASE",
    "CONFIG_THREAD_INFO_IN_TASK",
    "CONFIG_SCHED_WALT",
    "CONFIG_FUTEX",
    "CONFIG_FUTEX_PI",
    "CONFIG_RT_MUTEXES",
    "CONFIG_DEBUG_RT_MUTEXES",
    "CONFIG_ION",
    "CONFIG_MTK_ION",
    "CONFIG_MTK_CMDQ",
    "CONFIG_MTK_ENABLE_GENIEZONE",
)


def read_source(path: Path) -> tuple[list[str], list[int]]:
    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    lines: list[str] = []
    numbers: list[int] = []
    for index, line in enumerate(raw, start=1):
        match = NUMBERED.match(line)
        if match:
            numbers.append(int(match.group(1)))
            lines.append(match.group(2))
        else:
            numbers.append(index)
            lines.append(line)
    return lines, numbers


def sha256_lines(lines: list[str]) -> str:
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


def compare_sources(exact: Path, reference: Path) -> tuple[dict, list[str], list[str], list[int]]:
    exact_lines, exact_numbers = read_source(exact)
    reference_lines, _ = read_source(reference)
    diff = list(
        difflib.unified_diff(
            reference_lines,
            exact_lines,
            fromfile=str(reference),
            tofile=str(exact),
            n=3,
        )
    )
    hunks = sum(1 for line in diff if line.startswith("@@"))
    result = {
        "exact_input": str(exact),
        "reference_input": str(reference),
        "exact_normalized_lines": len(exact_lines),
        "reference_normalized_lines": len(reference_lines),
        "exact_normalized_sha256": sha256_lines(exact_lines),
        "reference_normalized_sha256": sha256_lines(reference_lines),
        "unified_diff_lines": len(diff),
        "unified_diff_hunks": hunks,
        "identical": exact_lines == reference_lines,
        "scope": "source comparison only; no device or executable code",
    }
    return result, diff, exact_lines, exact_numbers


def marker_line(lines: list[str], numbers: list[int], pattern: str) -> int | None:
    for line, number in zip(lines, numbers):
        if pattern in line:
            return number
    return None


def task_struct_definition_line(lines: list[str], numbers: list[int]) -> int | None:
    for line, number in zip(lines, numbers):
        if re.search(r"\bstruct\s+task_struct\s*\{", line):
            return number
    return marker_line(lines, numbers, "struct task_struct")


def parse_config(path: Path) -> dict[str, tuple[str, int]]:
    values: dict[str, tuple[str, int]] = {}
    for number, raw_line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        source_number = number
        numbered = NUMBERED.match(raw_line)
        line = raw_line
        if numbered:
            source_number = int(numbered.group(1))
            line = numbered.group(2)
        match = CONFIG.match(line.strip())
        if not match:
            continue
        key = match.group(1)
        value = "n" if " is not set" in line else (match.group(2) or "")
        values[key] = (value, source_number)
    return values


def source_config_observations(path: Path) -> list[tuple[str, str, str, str]]:
    lines, numbers = read_source(path)
    observations: list[tuple[str, str, str, str]] = []
    for key in INTERESTING_CONFIGS:
        hits = [(str(number), line.strip()) for line, number in zip(lines, numbers) if key in line]
        if hits:
            observations.append((str(path), key, "; ".join(h[1] for h in hits[:4]), ",".join(h[0] for h in hits[:4])))
        else:
            observations.append((str(path), key, "NOT_FOUND", ""))
    return observations


def write_new(path: Path, content: str) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def escaped_diff(diff: list[str]) -> str:
    """Keep a reviewable unified diff without raw tabs/trailing spaces."""
    encoded: list[str] = []
    for line in diff:
        text = line.rstrip("\n")
        text = text.replace("\t", "\\t")
        trailing = len(text) - len(text.rstrip(" "))
        if trailing:
            text = text.rstrip(" ") + ("␠" * trailing)
        encoded.append(text + "\n")
    return "".join(encoded)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exact-futex", required=True, type=Path)
    parser.add_argument("--reference-futex", required=True, type=Path)
    parser.add_argument("--exact-sched", required=True, type=Path)
    parser.add_argument("--reference-sched", required=True, type=Path)
    parser.add_argument("--exact-kconfig", required=True, type=Path)
    parser.add_argument("--runtime-config", required=True, type=Path)
    parser.add_argument("--defconfig", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [
        args.exact_futex,
        args.reference_futex,
        args.exact_sched,
        args.reference_sched,
        args.exact_kconfig,
        args.runtime_config,
    ]
    if args.defconfig:
        inputs.append(args.defconfig)
    if any(not path.is_file() for path in inputs):
        parser.error("all source/config inputs must be readable regular files")
    if args.dry_run:
        print("DRY-RUN: no source is executed and no output is written.")
        print(f"DRY-RUN: compare futex {args.exact_futex} against {args.reference_futex}")
        print(f"DRY-RUN: compare sched.h {args.exact_sched} against {args.reference_sched}")
        print(f"DRY-RUN: inspect Kconfig/runtime config and write {args.output_dir}")
        return 0
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        parser.error(f"refusing to write into non-empty output directory: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    futex_result, futex_diff, _, _ = compare_sources(args.exact_futex, args.reference_futex)
    sched_result, sched_diff, sched_lines, sched_numbers = compare_sources(args.exact_sched, args.reference_sched)

    sched_summary = {
        **sched_result,
        "task_struct_source_line": task_struct_definition_line(sched_lines, sched_numbers),
        "pi_blocked_on_source_line": marker_line(sched_lines, sched_numbers, "pi_blocked_on"),
        "vendor_markers": {
            marker: marker_line(sched_lines, sched_numbers, marker)
            for marker in ("CONFIG_SCHED_WALT", "CONFIG_CPU_FREQ_TIMES", "CONFIG_SWAP", "CONFIG_THREAD_INFO_IN_TASK")
        },
    }

    exact_kconfig_lines, exact_kconfig_numbers = read_source(args.exact_kconfig)
    kconfig_text = "\n".join(exact_kconfig_lines)
    source_observations = source_config_observations(args.exact_kconfig)
    source_observations.extend(source_config_observations(args.exact_futex))
    runtime_values = parse_config(args.runtime_config)
    defconfig_values = parse_config(args.defconfig) if args.defconfig else {}

    config_rows = [("source", "key", "value_or_observation", "line")]
    for row in source_observations:
        config_rows.append(tuple(value or "-" for value in row))
    for label, values in (("runtime", runtime_values), ("defconfig", defconfig_values)):
        for key in INTERESTING_CONFIGS:
            if key in values:
                value, line = values[key]
                config_rows.append((label, key, value or "-", str(line)))
            else:
                config_rows.append((label, key, "NOT_FOUND", "-"))

    summary = {
        "scope": "host-only exact-source analysis; no device operation, compilation, exploit or payload",
        "futex": futex_result,
        "sched": sched_summary,
        "kconfig": {
            "exact_source_sha256": sha256_lines(exact_kconfig_lines),
            "contains_literal_CONFIG_FUTEX_PI": "CONFIG_FUTEX_PI" in kconfig_text,
        },
        "runtime_config": {
            key: runtime_values.get(key, ("NOT_FOUND", None))[0] for key in INTERESTING_CONFIGS
        },
    }

    write_new(args.output_dir / "futex-comparison.json", json.dumps(futex_result, indent=2) + "\n")
    write_new(args.output_dir / "futex-diff.txt", escaped_diff(futex_diff))
    write_new(args.output_dir / "sched-comparison.json", json.dumps(sched_summary, indent=2) + "\n")
    write_new(args.output_dir / "sched-diff.txt", escaped_diff(sched_diff))
    write_new(
        args.output_dir / "kconfig-observations.tsv",
        "\n".join("\t".join(row) for row in config_rows) + "\n",
    )
    write_new(args.output_dir / "summary.json", json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
