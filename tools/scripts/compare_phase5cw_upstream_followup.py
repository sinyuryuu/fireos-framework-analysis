#!/usr/bin/env python3
"""Compare PS7331 rtmutex cleanup markers with upstream fix shapes.

This is a host-only source-marker audit.  It never connects to a device,
compiles or executes code, invokes futexes, derives addresses/offsets, or
generates an exploit payload.
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


UPSTREAM_PRIMARY_URL = "https://github.com/torvalds/linux/commit/3bfdc63936dd"
UPSTREAM_FOLLOWUP_URL = (
    "https://patchew.org/linux/20260507112913.1019537-1-dave%40stgolabs.net/"
)
UPSTREAM_FOLLOWUP_COMMIT = "40a25d59e85b3c8709ac2424d44f65610467871e"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def function_block(lines: list[str], pattern: str) -> tuple[int, int, list[str]]:
    start = next(
        (index for index, line in enumerate(lines) if re.search(pattern, line)), None
    )
    if start is None:
        raise ValueError(f"function not found: {pattern}")
    depth = 0
    opened = False
    end = start
    for index in range(start, len(lines)):
        depth += lines[index].count("{") - lines[index].count("}")
        opened |= "{" in lines[index]
        if opened and depth == 0:
            end = index
            break
    return start + 1, end + 1, lines[start : end + 1]


def matches(lines: list[str], needles: tuple[str, ...], line_base: int) -> list[dict[str, object]]:
    return [
        {"line": index + line_base, "text": line.strip()}
        for index, line in enumerate(lines)
        if any(needle in line for needle in needles)
    ]


def inspect_source(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    remove_start, remove_end, remove = function_block(
        lines, r"^\s*(?:static\s+)?void\s+(?:__sched\s+)?remove_waiter\s*\("
    )
    task_start, task_end, task = function_block(
        lines, r"^\s*static\s+int\s+(?:__sched\s+)?task_blocks_on_rt_mutex\s*\("
    )
    proxy_pattern = (
        r"^\s*(?:static\s+)?(?:__sched\s+)?int\s+"
        r"(?:__)?rt_mutex_start_proxy_lock\s*\("
    )
    proxy_start, proxy_end, proxy = function_block(lines, proxy_pattern) if any(
        re.search(proxy_pattern, line) for line in lines
    ) else (None, None, [])

    waiter_assignment = matches(task, ("waiter->task = task",), task_start)
    early_deadlock = [
        {"line": index + task_start, "text": line.strip()}
        for index, line in enumerate(task)
        if re.search(r"return\s+-EDEAD(?:LK|LOCK)\s*;", line)
    ]
    assignment_line = waiter_assignment[0]["line"] if waiter_assignment else None
    early_before_assignment = [
        item for item in early_deadlock
        if assignment_line is None or item["line"] < assignment_line
    ]

    remove_markers = {
        "current_pi_blocked_on_cleanup": bool(
            matches(remove, ("current->pi_blocked_on",), remove_start)
        ),
        "waiter_task_declaration": bool(
            re.search(r"struct\s+task_struct\s+\*\s*waiter_task\s*=\s*waiter->task", "\n".join(remove))
        ),
        "waiter_task_pi_blocked_on_cleanup": bool(
            re.search(r"waiter_task\s*->\s*pi_blocked_on\s*=\s*NULL", "\n".join(remove))
        ),
        "waiter_task_pi_lock": bool(
            re.search(r"waiter_task\s*->\s*pi_lock", "\n".join(remove))
        ),
        "waiter_null_guard": bool(
            re.search(r"if\s*\(\s*!\s*waiter_task\s*\)", "\n".join(remove))
        ),
        "current_chain_walk_argument": bool(
            re.search(r"next_lock\s*,\s*NULL\s*,\s*current\b", "\n".join(remove), re.S)
        ),
        "waiter_task_chain_walk_argument": bool(
            re.search(r"next_lock\s*,\s*NULL\s*,\s*waiter_task\b", "\n".join(remove), re.S)
        ),
    }

    proxy_markers = {
        "broad_ret_cleanup_guard": bool(
            re.search(r"if\s*\(\s*unlikely\s*\(\s*ret\s*\)\s*\)", "\n".join(proxy))
        ),
        "negative_only_cleanup_guard": bool(
            re.search(r"if\s*\(\s*unlikely\s*\(\s*ret\s*<\s*0\s*\)\s*\)", "\n".join(proxy))
        ),
        "proxy_remove_waiter_call": bool(
            "remove_waiter(lock, waiter)" in "\n".join(proxy)
        ),
    }

    if remove_markers["waiter_task_pi_blocked_on_cleanup"] and not remove_markers[
        "current_pi_blocked_on_cleanup"
    ]:
        primary_classification = "PRIMARY_FIX_SHAPE"
    elif remove_markers["current_pi_blocked_on_cleanup"] and not remove_markers[
        "waiter_task_pi_blocked_on_cleanup"
    ]:
        primary_classification = "PRE_PRIMARY_FIX_SHAPE"
    else:
        primary_classification = "MIXED_OR_UNKNOWN"

    if proxy_markers["negative_only_cleanup_guard"] and remove_markers["waiter_null_guard"]:
        followup_classification = "FOLLOW_UP_GUARD_SHAPE"
    elif proxy_markers["broad_ret_cleanup_guard"] and proxy_markers["proxy_remove_waiter_call"]:
        followup_classification = "BROAD_RET_CLEANUP_SHAPE"
    else:
        followup_classification = "NOT_PRESENT_OR_NOT_THIS_API_SHAPE"

    return {
        "path": str(path),
        "sha256": sha256(path),
        "remove_waiter": {
            "span": [remove_start, remove_end],
            "markers": remove_markers,
        },
        "task_blocks_on_rt_mutex": {
            "span": [task_start, task_end],
            "waiter_assignment": waiter_assignment,
            "early_deadlock_returns": early_deadlock,
            "early_deadlock_before_waiter_assignment": early_before_assignment,
        },
        "rt_mutex_start_proxy_lock": {
            "span": [proxy_start, proxy_end] if proxy_start is not None else None,
            "markers": proxy_markers,
        },
        "primary_classification": primary_classification,
        "followup_classification": followup_classification,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ps7331", type=Path, required=True)
    parser.add_argument("--fixed-reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inputs = {
        "PS7331_EXACT_SOURCE": args.ps7331,
        "LOCAL_UPSTREAM_PRIMARY_FIX_REFERENCE": args.fixed_reference,
    }
    if args.dry_run:
        print("DRY-RUN: no files will be read or written.")
        for label, path in inputs.items():
            print(f"{label}\t{path}")
        print(f"OUTPUT\t{args.output}")
        return 0
    if args.output.exists():
        print(f"ERROR: refusing to overwrite {args.output}", file=sys.stderr)
        return 2
    for label, path in inputs.items():
        if not path.is_file():
            print(f"ERROR: missing {label}: {path}", file=sys.stderr)
            return 2

    inspected = []
    for label, path in inputs.items():
        row = inspect_source(path)
        row["label"] = label
        inspected.append(row)

    ps7331 = inspected[0]
    fixed = inspected[1]
    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "host_only": True,
            "device_io": False,
            "compilation": False,
            "futex_trigger": False,
            "kernel_memory_access": False,
            "address_or_offset_output": False,
            "payload_or_reproducer": False,
        },
        "inputs": inspected,
        "upstream_references": {
            "primary_fix": {
                "url": UPSTREAM_PRIMARY_URL,
                "commit": "3bfdc63936dd",
                "semantic_change": "remove_waiter() uses waiter->task for PI cleanup and chain adjustment",
            },
            "followup_fix": {
                "url": UPSTREAM_FOLLOWUP_URL,
                "commit": UPSTREAM_FOLLOWUP_COMMIT,
                "semantic_change": "guard an un-enqueued waiter and restrict wrapper cleanup to ret < 0",
            },
        },
        "verdict": {
            "ps7331_primary_fix_present": ps7331["primary_classification"] == "PRIMARY_FIX_SHAPE",
            "ps7331_matches_pre_primary_shape": ps7331["primary_classification"] == "PRE_PRIMARY_FIX_SHAPE",
            "ps7331_has_followup_guard_shape": ps7331["followup_classification"] == "FOLLOW_UP_GUARD_SHAPE",
            "runtime_identity_mismatch_observed": False,
            "cleanup_residue_observed": False,
            "memory_effect_observed": False,
            "root_or_privilege_gain_proven": False,
        },
    }
    args.output.mkdir(parents=True)
    (args.output / "summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (args.output / "markers.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "label", "primary_classification", "followup_classification",
            "current_cleanup", "waiter_task_cleanup", "waiter_null_guard",
            "broad_ret_guard", "negative_only_guard", "proxy_remove_waiter",
            "early_deadlock_before_assignment", "sha256",
        ])
        for row in inspected:
            rm = row["remove_waiter"]["markers"]
            proxy = row["rt_mutex_start_proxy_lock"]["markers"]
            writer.writerow([
                row["label"], row["primary_classification"], row["followup_classification"],
                rm["current_pi_blocked_on_cleanup"],
                rm["waiter_task_pi_blocked_on_cleanup"],
                rm["waiter_null_guard"],
                proxy["broad_ret_cleanup_guard"],
                proxy["negative_only_cleanup_guard"],
                proxy["proxy_remove_waiter_call"],
                len(row["task_blocks_on_rt_mutex"]["early_deadlock_before_waiter_assignment"]),
                row["sha256"],
            ])
    (args.output / "result.md").write_text(
        "# Phase 5CW upstream follow-up marker audit\n\n"
        "This is a host-only source comparison. It does not compile or execute "
        "code, contact a device, trigger futexes, inspect kernel memory, derive "
        "addresses/offsets, or generate a payload.\n\n"
        f"- PS7331 primary classification: **{ps7331['primary_classification']}**\n"
        f"- PS7331 follow-up classification: **{ps7331['followup_classification']}**\n"
        f"- Local upstream reference primary classification: **{fixed['primary_classification']}**\n"
        "- Runtime identity mismatch observed: **False**\n"
        "- Cleanup residue or memory effect observed: **False**\n\n"
        f"Primary reference: {UPSTREAM_PRIMARY_URL}\n\n"
        f"Follow-up reference: {UPSTREAM_FOLLOWUP_URL}\n",
        encoding="utf-8",
    )
    print(f"Wrote host-only marker audit to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
