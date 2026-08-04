#!/usr/bin/env python3
"""Audit PS7331 rtmutex cleanup and later state consumers, source-only.

The checker maps fields touched by remove_waiter() and identifies functions
that later read or clear the relevant state.  It does not execute a futex,
construct a race, or produce an exploit procedure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def function_span(lines: list[str], signature: str) -> tuple[int, int, list[str]]:
    start = next((i for i, line in enumerate(lines) if re.search(signature, line)), None)
    if start is None:
        raise ValueError(f"function not found: {signature}")
    depth = 0
    opened = False
    end = start
    for i in range(start, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        opened |= "{" in lines[i]
        if opened and depth == 0:
            end = i
            break
    return start + 1, end + 1, lines[start : end + 1]


def matches(lines: list[str], pattern: str, offset: int = 0) -> list[dict[str, object]]:
    compiled = re.compile(pattern)
    return [
        {"line": i + 1 + offset, "text": line.strip()}
        for i, line in enumerate(lines)
        if compiled.search(line)
    ]


def first(lines: list[str], pattern: str, offset: int = 0) -> dict[str, object] | None:
    found = matches(lines, pattern, offset)
    return found[0] if found else None


def inspect(rtmutex_path: Path) -> dict[str, object]:
    lines = rtmutex_path.read_text(encoding="utf-8", errors="replace").splitlines()
    source_hash = sha256(rtmutex_path)
    spans: dict[str, tuple[int, int, list[str]]] = {}
    signatures = {
        "rt_mutex_dequeue": r"^\s*rt_mutex_dequeue\s*\(",
        "rt_mutex_dequeue_pi": r"^\s*rt_mutex_dequeue_pi\s*\(",
        "task_blocked_on_lock": r"^\s*static inline struct rt_mutex \*task_blocked_on_lock\s*\(",
        "rt_mutex_adjust_prio_chain": r"^\s*static int rt_mutex_adjust_prio_chain\s*\(",
        "try_to_take_rt_mutex": r"^\s*static int try_to_take_rt_mutex\s*\(",
        "task_blocks_on_rt_mutex": r"^\s*static int task_blocks_on_rt_mutex\s*\(",
        "mark_wakeup_next_waiter": r"^\s*static void mark_wakeup_next_waiter\s*\(",
        "remove_waiter": r"^\s*static void remove_waiter\s*\(",
        "rt_mutex_adjust_pi": r"^\s*void rt_mutex_adjust_pi\s*\(",
    }
    for name, signature in signatures.items():
        spans[name] = function_span(lines, signature)

    def scoped(name: str, pattern: str) -> list[dict[str, object]]:
        start, _end, block = spans[name]
        return matches(block, pattern, start - 1)

    cleanup = {
        "current_pi_blocked_on_write": scoped("remove_waiter", r"current->pi_blocked_on\s*=\s*NULL"),
        "waiter_task_write": scoped("remove_waiter", r"waiter->task\s*="),
        "waiter_lock_write": scoped("remove_waiter", r"waiter->lock\s*="),
        "waiter_tree_dequeue_call": scoped("remove_waiter", r"rt_mutex_dequeue\s*\("),
        "waiter_pi_tree_dequeue_call": scoped("remove_waiter", r"rt_mutex_dequeue_pi\s*\("),
        "current_pi_lock": scoped("remove_waiter", r"current->pi_lock"),
    }

    consumers = [
        {
            "function": "task_blocked_on_lock",
            "kind": "read_dereference",
            "matches": scoped("task_blocked_on_lock", r"p->pi_blocked_on(?:\s*\?|->)"),
            "meaning": "reads a task's pi_blocked_on and, when present, obtains waiter->lock",
            "classification": "POTENTIAL_SECOND_CONSUMER",
        },
        {
            "function": "rt_mutex_adjust_prio_chain",
            "kind": "read_dereference",
            "matches": scoped("rt_mutex_adjust_prio_chain", r"task->pi_blocked_on|waiter->lock"),
            "meaning": "walks the PI chain through task->pi_blocked_on and the waiter's lock",
            "classification": "POTENTIAL_SECOND_CONSUMER",
        },
        {
            "function": "rt_mutex_adjust_pi",
            "kind": "read_dereference",
            "matches": scoped("rt_mutex_adjust_pi", r"task->pi_blocked_on"),
            "meaning": "rechecks a task's blocked waiter during PI adjustment",
            "classification": "POTENTIAL_SECOND_CONSUMER",
        },
        {
            "function": "try_to_take_rt_mutex",
            "kind": "state_clear",
            "matches": scoped("try_to_take_rt_mutex", r"task->pi_blocked_on\s*=\s*NULL"),
            "meaning": "can clear the explicit task's blocked state on successful lock acquisition",
            "classification": "POTENTIAL_REPAIR_OR_STATE_TRANSITION",
        },
        {
            "function": "mark_wakeup_next_waiter",
            "kind": "waiter_task_use",
            "matches": scoped("mark_wakeup_next_waiter", r"wake_q_add\s*\(.*waiter->task"),
            "meaning": "uses waiter->task as the wake target after selecting a top waiter",
            "classification": "POTENTIAL_SECOND_CONSUMER",
        },
    ]

    ret_path = {
        "early_deadlock_return": scoped("task_blocks_on_rt_mutex", r"owner\s*==\s*task|return\s+-EDEADLK"),
        "waiter_task_assignment": scoped("task_blocks_on_rt_mutex", r"waiter->task\s*=\s*task"),
        "proxy_cleanup_condition": scoped("remove_waiter", r"current->pi_blocked_on\s*=\s*NULL"),
        "proxy_wrapper_source": first(lines, r"if\s*\(unlikely\(ret\)\)"),
    }

    evidence = []
    evidence.append({
        "id": "P5CD-001",
        "function": "remove_waiter",
        "observation": "cleanup writes current->pi_blocked_on and does not write waiter->task or waiter->lock",
        "matches": cleanup,
        "confidence": "Confirmed, exact source",
    })
    evidence.append({
        "id": "P5CD-002",
        "function": "rt_mutex_dequeue / rt_mutex_dequeue_pi",
        "observation": "cleanup may clear waiter tree_entry and pi_tree_entry through helper calls, conditionally",
        "matches": {
            "rt_mutex_dequeue_tree_clear": scoped("rt_mutex_dequeue", r"RB_CLEAR_NODE\s*\(.*tree_entry"),
            "rt_mutex_dequeue_pi_tree_clear": scoped("rt_mutex_dequeue_pi", r"RB_CLEAR_NODE\s*\(.*pi_tree_entry"),
        },
        "confidence": "Confirmed, exact source",
    })
    evidence.append({
        "id": "P5CD-003",
        "function": "PI state consumers",
        "observation": "normal rtmutex paths later read task->pi_blocked_on or waiter->task",
        "matches": consumers,
        "confidence": "Confirmed as source references; runtime reachability unproven",
    })
    evidence.append({
        "id": "P5CD-004",
        "function": "task_blocks_on_rt_mutex / rt_mutex_start_proxy_lock",
        "observation": "early return precedes waiter task assignment and PS7331 wrapper uses nonzero cleanup condition",
        "matches": ret_path,
        "confidence": "Confirmed, exact source",
    })

    return {
        "scope": "PS7331 exact rtmutex.c; host-only cleanup/consumer audit",
        "source": str(rtmutex_path),
        "source_sha256": source_hash,
        "spans": {name: [span[0], span[1]] for name, span in spans.items()},
        "cleanup_effect_model": {
            "writes_current_pi_blocked_on": bool(cleanup["current_pi_blocked_on_write"]),
            "writes_waiter_task": bool(cleanup["waiter_task_write"]),
            "writes_waiter_lock": bool(cleanup["waiter_lock_write"]),
            "dequeues_lock_tree_via_helper": bool(cleanup["waiter_tree_dequeue_call"]),
            "dequeues_owner_pi_tree_via_helper": bool(cleanup["waiter_pi_tree_dequeue_call"]),
            "target_task_pi_blocked_on_cleared_by_remove_waiter": False,
            "persistent_target_state_violation_proven": False,
        },
        "consumer_model": {
            "potential_second_consumers": [item["function"] for item in consumers if item["classification"] == "POTENTIAL_SECOND_CONSUMER"],
            "potential_repair_or_state_transitions": [item["function"] for item in consumers if item["classification"] == "POTENTIAL_REPAIR_OR_STATE_TRANSITION"],
            "runtime_second_consumer_observed": False,
            "runtime_repair_observed": False,
        },
        "ret_and_early_return": ret_path,
        "evidence": evidence,
        "verdict": {
            "source_post_cleanup_effects_mapped": True,
            "runtime_mismatch_observed": False,
            "persistent_invariant_violation_proven": False,
            "stable_crash_proven": False,
            "controlled_memory_effect_proven": False,
            "root_or_privilege_gain_proven": False,
            "device_execution": False,
        },
        "safety": {
            "syscall_invoked": False,
            "race_triggered": False,
            "unknown_ioctl_used": False,
            "device_modified": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtmutex", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output in {Path("/"), Path("."), Path("..")}:
        parser.error("refusing broad output path")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "device_execution": False,
                          "rtmutex": str(args.rtmutex), "output": str(args.output)},
                         indent=2, sort_keys=True))
        return 0
    if not args.rtmutex.is_file():
        parser.error(f"rtmutex source is not a regular file: {args.rtmutex}")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")
    result = inspect(args.rtmutex)
    args.output.mkdir(parents=True)
    (args.output / "cleanup-consumer-audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "result.md").write_text(
        "# PS7331 cleanup/consumer audit\n\n"
        "- Source post-cleanup effects mapped: **True**\n"
        "- Runtime persistent invariant violation proven: **False**\n"
        "- Runtime second consumer observed: **False**\n"
        "- Controlled memory effect/root proven: **False**\n\n"
        "This is source-only mapping; potential consumers are not runtime evidence.\n",
        encoding="utf-8",
    )
    (args.output / "README.txt").write_text(
        "Host-only source audit. No futex syscall, race trigger, device I/O, payload, "
        "address, image mutation, or privilege operation.\n",
        encoding="utf-8",
    )
    files = sorted(path for path in args.output.iterdir() if path.is_file())
    (args.output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
