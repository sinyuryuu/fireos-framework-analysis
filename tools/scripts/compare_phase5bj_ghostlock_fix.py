#!/usr/bin/env python3
"""Compare the GhostLock rtmutex cleanup marker in preserved source files.

This is a host-only semantic checker. It does not disassemble, execute, or
produce kernel addresses, offsets, payloads, or device commands.
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
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def function_body(text: str, name: str) -> tuple[str, int, int]:
    match = re.search(r"\b" + re.escape(name) + r"\s*\([^;]*\)\s*\{", text, re.S)
    if not match:
        raise ValueError(f"function not found: {name}")
    opening = text.find("{", match.start(), match.end())
    depth = 0
    closing = None
    for index in range(opening, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                closing = index + 1
                break
    if closing is None:
        raise ValueError(f"unterminated function: {name}")
    start_line = text.count("\n", 0, match.start()) + 1
    end_line = text.count("\n", 0, closing) + 1
    return text[match.start():closing], start_line, end_line


def inspect_source(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    body, start_line, end_line = function_body(text, "remove_waiter")
    markers = {
        "current_pi_blocked_on_cleanup": bool(
            re.search(r"\bcurrent\s*->\s*pi_blocked_on\s*=\s*NULL", body)
        ),
        "waiter_task_declaration": bool(
            re.search(
                r"struct\s+task_struct\s*\*\s*waiter_task\s*=\s*waiter\s*->\s*task",
                body,
            )
        ),
        "waiter_task_pi_blocked_on_cleanup": bool(
            re.search(r"\bwaiter_task\s*->\s*pi_blocked_on\s*=\s*NULL", body)
        ),
        "current_chain_walk_argument": bool(
            re.search(r"next_lock\s*,\s*NULL\s*,\s*current\b", body, re.S)
        ),
        "waiter_task_chain_walk_argument": bool(
            re.search(r"next_lock\s*,\s*NULL\s*,\s*waiter_task\b", body, re.S)
        ),
    }
    if markers["waiter_task_pi_blocked_on_cleanup"] and not markers[
        "current_pi_blocked_on_cleanup"
    ]:
        classification = "FIXED_WAITER_TASK_CLEANUP"
    elif markers["current_pi_blocked_on_cleanup"] and not markers[
        "waiter_task_pi_blocked_on_cleanup"
    ]:
        classification = "PRE_FIX_CURRENT_TASK_CLEANUP"
    else:
        classification = "MIXED_OR_UNKNOWN"
    return {
        "path": str(path),
        "sha256": sha256(path),
        "function": "remove_waiter",
        "function_start_line": start_line,
        "function_end_line": end_line,
        "markers": markers,
        "classification": classification,
        "proxy_caller_present_in_file": bool(
            re.search(r"rt_mutex_start_proxy_lock[\s\S]{0,12000}remove_waiter", text)
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ps7330", type=Path, required=True)
    parser.add_argument("--ps7331", type=Path, required=True)
    parser.add_argument("--fixed-reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inputs = {
        "PS7330_SOURCE_FAMILY": args.ps7330,
        "PS7331_BUILD_SELECTED_SOURCE": args.ps7331,
        "UPSTREAM_FIXED_REFERENCE": args.fixed_reference,
    }
    if args.dry_run:
        print("DRY-RUN: no files will be read or written.")
        print("Inputs:")
        for label, path in inputs.items():
            print(f"{label}\t{path}")
        print(f"Output\t{args.output}")
        return 0
    if args.output.exists():
        print(f"ERROR: output already exists: {args.output}", file=sys.stderr)
        return 2
    for label, path in inputs.items():
        if not path.is_file():
            print(f"ERROR: missing {label}: {path}", file=sys.stderr)
            return 2
    results = []
    for label, path in inputs.items():
        row = inspect_source(path)
        row["label"] = label
        results.append(row)
    args.output.mkdir(parents=True)
    generated = datetime.now(timezone.utc).isoformat()
    summary = {
        "generated_at_utc": generated,
        "host_only": True,
        "device_io": False,
        "address_or_offset_output": False,
        "payload_or_reproducer": False,
        "inputs": results,
        "comparison": {
            "ps7330_classification": results[0]["classification"],
            "ps7331_classification": results[1]["classification"],
            "fixed_reference_classification": results[2]["classification"],
            "ps7330_and_ps7331_same_classification": results[0]["classification"]
            == results[1]["classification"],
            "ps7331_is_fixed_marker": results[1]["classification"]
            == "FIXED_WAITER_TASK_CLEANUP",
        },
    }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (args.output / "comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "label",
                "classification",
                "function_start_line",
                "function_end_line",
                "current_cleanup",
                "waiter_task_cleanup",
                "current_chain_argument",
                "waiter_task_chain_argument",
                "proxy_caller_present",
                "sha256",
            ]
        )
        for row in results:
            markers = row["markers"]
            writer.writerow(
                [
                    row["label"],
                    row["classification"],
                    row["function_start_line"],
                    row["function_end_line"],
                    markers["current_pi_blocked_on_cleanup"],
                    markers["waiter_task_pi_blocked_on_cleanup"],
                    markers["current_chain_walk_argument"],
                    markers["waiter_task_chain_walk_argument"],
                    row["proxy_caller_present_in_file"],
                    row["sha256"],
                ]
            )
    (args.output / "result.md").write_text(
        "# Phase 5BJ semantic checker result\n\n"
        "This host-only checker compares the `remove_waiter()` cleanup markers "
        "in three preserved source inputs. It does not execute code, calculate "
        "addresses, produce offsets, or contact the device.\n\n"
        f"- PS7330 source family: **{results[0]['classification']}**\n"
        f"- PS7331 build-selected source: **{results[1]['classification']}**\n"
        f"- Fixed reference: **{results[2]['classification']}**\n"
        f"- PS7331 fixed marker present: **{summary['comparison']['ps7331_is_fixed_marker']}**\n",
        encoding="utf-8",
    )
    print(f"Wrote host-only comparison to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
