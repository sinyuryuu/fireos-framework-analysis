#!/usr/bin/env python3
"""Compare preserved PS7331 source and inspected Image semantics.

This is a host-only evidence combiner.  It consumes a source-semantics JSON,
an address-sanitized instruction-pattern CSV, and a fixed-reference source.
It never executes a binary, talks to a device, calculates addresses, or emits
an exploit payload.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_output(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if resolved in {Path("/"), Path("/tmp"), Path("/var/tmp"), Path.cwd().resolve()}:
        raise ValueError(f"refusing broad or temporary output path: {resolved}")
    if resolved.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {resolved}")
    return resolved


def fixed_remove_waiter_pattern(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = None
    pattern = re.compile(r"(?:static\s+)?void\s+(?:__sched\s+)?remove_waiter\s*\(")
    for number, line in enumerate(lines, start=1):
        if pattern.search(line):
            start = number
            break
    if start is None:
        return {"found": False, "waiter_task_cleanup": False, "current_cleanup": False, "span": None}
    depth = 0
    opened = False
    end = len(lines)
    for number in range(start, len(lines) + 1):
        text = lines[number - 1]
        depth += text.count("{")
        opened = opened or "{" in text
        depth -= text.count("}")
        if opened and depth == 0:
            end = number
            break
    body = lines[start - 1 : end]
    return {
        "found": True,
        "waiter_task_cleanup": any("waiter->task" in line for line in body),
        "current_cleanup": any("current->pi_blocked_on" in line for line in body),
        "span": {"start_line": start, "end_line": end},
    }


def load_patterns(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-summary", required=True)
    parser.add_argument("--binary-patterns", required=True)
    parser.add_argument("--fixed-reference", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY-RUN: would combine preserved source semantics, sanitized Image patterns, and a fixed source reference")
        print("DRY-RUN: no ADB, execution, compilation, address, offset, payload, or flash operation")
        return 0

    try:
        output = safe_output(Path(args.output))
        source_summary = Path(args.source_summary).expanduser().resolve()
        binary_patterns = Path(args.binary_patterns).expanduser().resolve()
        fixed_reference = Path(args.fixed_reference).expanduser().resolve()
        inputs = (source_summary, binary_patterns, fixed_reference)
        for path in inputs:
            if not path.is_file():
                raise FileNotFoundError(path)

        source = json.loads(source_summary.read_text(encoding="utf-8"))
        patterns = load_patterns(binary_patterns)
        pattern_names = {(row.get("symbol", ""), row.get("pattern", "")) for row in patterns}
        fixed = fixed_remove_waiter_pattern(fixed_reference)

        source_old = source.get("classification") == "PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN"
        source_proxy = bool(source.get("proxy_error_remove_waiter_call_present"))
        binary_current = ("remove_waiter", "current_task_source") in pattern_names
        binary_clear = ("remove_waiter", "current_task_blocked_on_clear") in pattern_names
        binary_proxy = ("rt_mutex_start_proxy_lock", "proxy_error_calls_remove_waiter") in pattern_names
        consistent = source_old and source_proxy and binary_current and binary_clear and binary_proxy

        result = {
            "analysis": {
                "name": "Phase 5BG PS7331 source-to-inspected-Image semantic comparison",
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "device_io": False,
                "binary_execution": False,
                "address_or_offset_output": False,
                "payload_or_reproducer": False,
                "scope": "PS7331 preserved source and inspected Image pattern consistency only",
            },
            "inputs": [
                {"kind": "source_semantics", "path": str(source_summary), "sha256": sha256(source_summary)},
                {"kind": "sanitized_image_patterns", "path": str(binary_patterns), "sha256": sha256(binary_patterns)},
                {"kind": "fixed_reference_source", "path": str(fixed_reference), "sha256": sha256(fixed_reference)},
            ],
            "source": {
                "classification": source.get("classification"),
                "proxy_error_remove_waiter_call_present": source.get("proxy_error_remove_waiter_call_present"),
            },
            "inspected_image_patterns": {
                "remove_waiter_current_task_source": binary_current,
                "remove_waiter_current_task_blocked_on_clear": binary_clear,
                "proxy_error_calls_remove_waiter": binary_proxy,
            },
            "fixed_reference": fixed,
            "verdict": {
                "ps7331_inspected_image_consistent_with_pre_fix_source": consistent,
                "exact_ps7330_signed_binary_proven": False,
                "runtime_exploitability_proven": False,
                "root_or_privilege_gain_proven": False,
                "classification": "PS7331_INSPECTED_IMAGE_CONSISTENT_WITH_PRE_FIX_SOURCE" if consistent else "INCONSISTENT_OR_INCOMPLETE_EVIDENCE",
            },
            "safety": {
                "no_adb": True,
                "no_flash": True,
                "no_bootloader": True,
                "no_kernel_memory_access": True,
                "no_unknown_ioctl": True,
            },
        }

        output.mkdir(parents=True)
        json_path = output / "semantic-comparison.json"
        csv_path = output / "semantic-comparison.csv"
        result_path = output / "result.md"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(("layer", "observation", "value", "confidence"))
            writer.writerow(("source", "pre-fix current-task cleanup", source_old, "Confirmed, source scope"))
            writer.writerow(("source", "proxy error calls remove_waiter", source_proxy, "Confirmed, source scope"))
            writer.writerow(("inspected Image", "remove_waiter reads current-task source", binary_current, "Confirmed, inspected-function scope"))
            writer.writerow(("inspected Image", "remove_waiter clears current-task field", binary_clear, "Confirmed, inspected-function scope"))
            writer.writerow(("inspected Image", "proxy error calls remove_waiter", binary_proxy, "Confirmed, inspected-function scope"))
            writer.writerow(("fixed reference", "remove_waiter uses waiter task", fixed["waiter_task_cleanup"], "Confirmed, reference scope"))
            writer.writerow(("overall", "PS7331 inspected Image consistent with pre-fix source", consistent, "Strong evidence, version-scoped"))
            writer.writerow(("boundary", "exact PS7330 signed binary proven", False, "Unknown"))
        result_path.write_text(
            "# Phase 5BG PS7331 source-to-Image semantic comparison\n\n"
            f"- Classification: `{result['verdict']['classification']}`\n"
            "- This is version-scoped inspected-function evidence, not a runtime or root result.\n"
            "- No ADB, flash, bootloader, kernel memory, address, offset, payload or unknown ioctl operation was performed.\n",
            encoding="utf-8",
        )
        files = (json_path, csv_path, result_path)
        (output / "sha256sums.txt").write_text(
            "".join(f"{sha256(path)}  {path.name}\n" for path in files),
            encoding="utf-8",
        )
        print(output)
        return 0
    except (FileExistsError, FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
