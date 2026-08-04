#!/usr/bin/env python3
"""Model the GhostLock cleanup mismatch without executing kernel code.

This is a deliberately small semantic model, not an exploit or reproducer. It
represents the proxy-lock condition where waiter->task differs from current and
compares the PS7331 pre-fix cleanup with the fixed waiter-task cleanup. It never
uses ADB, kernel memory, addresses, ioctl, compiler, or payload data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Task:
    name: str
    pi_blocked_on: str | None


def pre_fix_remove_waiter(current: Task, waiter_task: Task) -> dict[str, object]:
    """Model current->pi_blocked_on cleanup in the PS7331 source."""
    del waiter_task
    current.pi_blocked_on = None
    return {"current_pi_blocked_on": current.pi_blocked_on}


def fixed_remove_waiter(current: Task, waiter_task: Task) -> dict[str, object]:
    """Model waiter_task->pi_blocked_on cleanup in the fixed reference."""
    del current
    waiter_task.pi_blocked_on = None
    return {"waiter_task_pi_blocked_on": waiter_task.pi_blocked_on}


def run_model() -> dict[str, object]:
    # Synthetic state: proxy-lock callers prepare a waiter for another task.
    current_pre = Task("current", "current-lock")
    waiter_pre = Task("proxy-waiter", "proxy-lock")
    pre = pre_fix_remove_waiter(current_pre, waiter_pre)

    current_fixed = Task("current", "current-lock")
    waiter_fixed = Task("proxy-waiter", "proxy-lock")
    fixed = fixed_remove_waiter(current_fixed, waiter_fixed)

    same_task_current = Task("same-task", "same-lock")
    same_task_pre = pre_fix_remove_waiter(same_task_current, same_task_current)

    return {
        "model": "GHOSTLOCK_PROXY_WAITER_CLEANUP_SEMANTICS",
        "host_only": True,
        "device_io": False,
        "kernel_code_executed": False,
        "address_or_offset_output": False,
        "payload_or_reproducer": False,
        "proxy_condition": {
            "current_task": "current",
            "waiter_task": "proxy-waiter",
            "tasks_are_distinct": True,
            "waiter_task_initial_pi_blocked_on": "proxy-lock",
        },
        "pre_fix": {
            "operation": "clear current->pi_blocked_on",
            "state_after": pre,
            "waiter_task_remains_blocked_on": waiter_pre.pi_blocked_on,
            "wrong_task_cleanup_observed": waiter_pre.pi_blocked_on is not None,
        },
        "fixed_reference": {
            "operation": "clear waiter->task->pi_blocked_on",
            "state_after": fixed,
            "waiter_task_remains_blocked_on": waiter_fixed.pi_blocked_on,
            "wrong_task_cleanup_observed": waiter_fixed.pi_blocked_on is not None,
        },
        "non_proxy_control": {
            "same_task": True,
            "pre_fix_state_after": same_task_pre,
            "pre_fix_matches_expected": same_task_pre["current_pi_blocked_on"] is None,
        },
        "verdict": {
            "semantic_mismatch_reproduced": waiter_pre.pi_blocked_on is not None,
            "fixed_cleanup_clears_waiter_task": waiter_fixed.pi_blocked_on is None,
            "live_kernel_exploitability_proven": False,
            "root_or_privilege_gain_proven": False,
        },
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print("DRY-RUN: run a synthetic Python semantic model only.")
        print("DRY-RUN: no kernel, device, address, ioctl, payload, or compiler operation.")
        return 0
    if args.output.exists():
        parser.error(f"refusing to overwrite output: {args.output}")
    args.output.mkdir(parents=True)
    result = run_model()
    result["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    json_path = args.output / "semantic-model.json"
    result_path = args.output / "result.md"
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    result_path.write_text(
        "# Phase 5BV GhostLock semantic model\n\n"
        "This is a synthetic, host-only model. It is not a kernel reproducer, "
        "exploit, address calculation, or root test.\n\n"
        f"- Proxy waiter/current mismatch reproduced: **{result['verdict']['semantic_mismatch_reproduced']}**\n"
        f"- Fixed cleanup clears waiter task: **{result['verdict']['fixed_cleanup_clears_waiter_task']}**\n"
        "- Live exploitability: **False / not tested**\n"
        "- Root or privilege gain: **False / not tested**\n",
        encoding="utf-8",
    )
    files = [json_path, result_path]
    (args.output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["verdict"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
