#!/usr/bin/env python3
"""Audit GhostLock primary/follow-up fix control flow in preserved source.

Host-only source analysis.  It does not compile, execute, contact a device,
derive addresses, trigger futexes, or generate a payload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def block(lines: list[str], pattern: str) -> tuple[int, int, list[str]]:
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


def records(lines: list[str], needles: tuple[str, ...], offset: int) -> list[dict]:
    return [
        {"line": index + offset, "text": line.strip()}
        for index, line in enumerate(lines)
        if any(needle in line for needle in needles)
    ]


def inspect(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    rm_start, rm_end, rm = block(
        lines, r"^\s*(?:static\s+)?void\s+(?:__sched\s+)?remove_waiter\s*\("
    )
    task_start, task_end, task = block(
        lines, r"^\s*static\s+int\s+task_blocks_on_rt_mutex\s*\("
    )
    proxy_start, proxy_end, proxy = block(
        lines, r"^\s*int\s+rt_mutex_start_proxy_lock\s*\("
    )
    waiter_assignment = records(task, ("waiter->task = task",), task_start)
    early_deadlock = [
        {"line": index + task_start, "text": line.strip()}
        for index, line in enumerate(task)
        if re.match(r"^\s*return\s+-EDEAD(?:LK|LOCK)\s*;", line)
    ]
    conditional_remove = records(proxy, ("if (unlikely(ret))",), proxy_start)
    proxy_remove = records(proxy, ("remove_waiter(lock, waiter)",), proxy_start)
    current_cleanup = records(rm, ("current->pi_blocked_on",), rm_start)
    waiter_task = records(rm, ("waiter->task", "waiter_task"), rm_start)
    assignment_line = waiter_assignment[0]["line"] if waiter_assignment else None
    early_lines_before_assignment = [
        item for item in early_deadlock
        if assignment_line is None or item["line"] < assignment_line
    ]
    return {
        "path": str(path),
        "sha256": sha256(path),
        "remove_waiter": {
            "span": [rm_start, rm_end],
            "current_cleanup": current_cleanup,
            "waiter_task_references": waiter_task,
        },
        "task_blocks_on_rt_mutex": {
            "span": [task_start, task_end],
            "waiter_assignment": waiter_assignment,
            "early_deadlock_returns": early_deadlock,
            "early_deadlock_before_waiter_assignment": early_lines_before_assignment,
        },
        "rt_mutex_start_proxy_lock": {
            "span": [proxy_start, proxy_end],
            "conditional_remove": conditional_remove,
            "remove_waiter_calls": proxy_remove,
        },
        "primary_fix_shape": bool(current_cleanup) and not bool(waiter_task),
        "primary_fix_present": bool(waiter_task) and not bool(current_cleanup),
        "follow_up_guard_review_needed": bool(early_lines_before_assignment)
        and bool(proxy_remove),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.source.is_file():
        parser.error(f"source is not a file: {args.source}")
    if args.output.exists():
        parser.error(f"refusing to overwrite: {args.output}")

    result = inspect(args.source)
    result.update({
        "scope": "host-only source control-flow audit; no compilation, device I/O, futex trigger, address, offset, or payload",
        "classification": (
            "PRE_PRIMARY_FIX_WITH_EARLY_RETURN_GUARD_REVIEW"
            if result["primary_fix_shape"] and result["follow_up_guard_review_needed"]
            else "PRIMARY_FIX_PRESENT_FOLLOW_UP_REVIEW"
            if result["primary_fix_present"] and result["follow_up_guard_review_needed"]
            else "SOURCE_CONTROL_FLOW_REVIEW_REQUIRED"
        ),
        "runtime_exploitability_proven": False,
        "root_or_privilege_gain_proven": False,
    })
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "fix-chain.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "result.md").write_text(
        "# Phase 5BY fix-chain audit\n\n"
        f"- Classification: **{result['classification']}**\n"
        f"- Follow-up guard review needed: **{result['follow_up_guard_review_needed']}**\n"
        "- Runtime exploitability proven: **False**\n"
        "- Root/privilege gain proven: **False**\n\n"
        "This is a host-only control-flow observation; it does not execute a "
        "kernel, trigger futexes, calculate offsets, or generate a payload.\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
