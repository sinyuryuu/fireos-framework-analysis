#!/usr/bin/env python3
"""Compare GhostLock cleanup semantics in preserved kernel source files.

This is a host-only source checker.  It does not compile, execute, contact a
device, inspect kernel memory, calculate addresses, or generate an exploit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def function_block(text: str, needle: str) -> tuple[int, int, str]:
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if needle in line), None)
    if start is None:
        raise ValueError(f"function marker not found: {needle}")

    # The preserved sources use a compact, non-nested function style.  Count
    # braces so the checker remains independent of line numbers.
    brace_depth = 0
    seen_open = False
    end = start
    for i in range(start, len(lines)):
        line = re.sub(r"//.*$", "", lines[i])
        brace_depth += line.count("{") - line.count("}")
        seen_open |= "{" in line
        if seen_open and brace_depth == 0:
            end = i
            break
    return start + 1, end + 1, "\n".join(lines[start : end + 1])


def inspect(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    start, end, block = function_block(text, "remove_waiter")
    proxy_start, proxy_end, proxy_block = function_block(
        text, "rt_mutex_start_proxy_lock"
    )
    return {
        "path": str(path),
        "sha256": sha256(path),
        "remove_waiter_lines": [start, end],
        "current_pi_blocked_on_cleanup": "current->pi_blocked_on = NULL" in block,
        "waiter_task_binding": bool(re.search(r"waiter_task\s*=\s*waiter->task", block)),
        "waiter_task_pi_blocked_on_cleanup": bool(
            re.search(r"waiter_task->pi_blocked_on\s*=\s*NULL", block)
        ),
        "waiter_task_direct_cleanup": bool(
            re.search(r"waiter->task->pi_blocked_on\s*=\s*NULL", block)
        ),
        "current_chain_argument": bool(
            re.search(r"rt_mutex_adjust_prio_chain\([^;]*,\s*current\s*\)", block, re.S)
        ),
        "waiter_task_chain_argument": bool(
            re.search(r"rt_mutex_adjust_prio_chain\([^;]*,\s*waiter_task\s*\)", block, re.S)
        ),
        "proxy_function_lines": [proxy_start, proxy_end],
        "proxy_error_calls_remove_waiter": bool(
            re.search(r"if\s*\s*\(\s*unlikely\s*\(\s*ret\s*\)\s*\)[\s\S]*?remove_waiter\s*\(", proxy_block)
        ),
    }


def classification(item: dict) -> str:
    if item["current_pi_blocked_on_cleanup"] and item["current_chain_argument"]:
        return "PRE_FIX_CURRENT_TASK_CLEANUP"
    if (
        item["waiter_task_binding"]
        and item["waiter_task_pi_blocked_on_cleanup"]
        and item["waiter_task_chain_argument"]
    ):
        return "FIXED_WAITER_TASK_CLEANUP"
    return "UNRESOLVED_CLEANUP_SEMANTICS"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=Path, required=True)
    ap.add_argument("--fixed-reference", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    target = inspect(args.target)
    fixed = inspect(args.fixed_reference)
    target["classification"] = classification(target)
    fixed["classification"] = classification(fixed)
    result = {
        "tool": "compare_phase5bw_ghostlock_fix.py",
        "scope": "host-only source semantics; no compilation, device I/O, address, offset, payload, or exploit generation",
        "target": target,
        "fixed_reference": fixed,
        "upstream_fix_semantics": {
            "use_waiter_task_for_pi_lock_and_cleanup": fixed["waiter_task_pi_blocked_on_cleanup"],
            "use_waiter_task_for_priority_chain": fixed["waiter_task_chain_argument"],
            "target_matches_pre_fix_shape": target["classification"] == "PRE_FIX_CURRENT_TASK_CLEANUP",
            "target_matches_fixed_shape": target["classification"] == "FIXED_WAITER_TASK_CLEANUP",
        },
        "verdict": (
            "PS7331_SOURCE_MATCHES_PRE_FIX_SEMANTICS"
            if target["classification"] == "PRE_FIX_CURRENT_TASK_CLEANUP"
            and fixed["classification"] == "FIXED_WAITER_TASK_CLEANUP"
            else "SOURCE_SEMANTICS_REQUIRE_REVIEW"
        ),
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "comparison.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "result.md").write_text(
        "# Phase 5BW source comparison\n\n"
        f"- Target classification: **{target['classification']}**\n"
        f"- Fixed reference classification: **{fixed['classification']}**\n"
        f"- Verdict: **{result['verdict']}**\n\n"
        "This result is source-level evidence only. It does not demonstrate a "
        "race, memory corruption, code execution, root, or a privilege transition.\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
