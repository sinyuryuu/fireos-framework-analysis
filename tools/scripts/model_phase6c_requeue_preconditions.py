#!/usr/bin/env python3
"""Host-only model of PS7331 requeue-PI preconditions.

The model extracts source landmarks and classifies two abstract states:
single-context/no-waiter versus paired-waiter/proxy-candidate.  It does not
construct syscall arguments, compile or execute code, contact a device, create
threads, schedule a race, access kernel memory, or emit an exploit payload.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def first_line(lines: list[str], pattern: str) -> int | None:
    regex = re.compile(pattern)
    for number, line in enumerate(lines, 1):
        if regex.search(line):
            return number
    return None


def first_line_after(lines: list[str], pattern: str, after: int | None) -> int | None:
    if after is None:
        return None
    regex = re.compile(pattern)
    for number in range(after + 1, len(lines) + 1):
        if regex.search(lines[number - 1]):
            return number
    return None


def build(root: Path) -> dict:
    futex = root / "kernel/futex.c"
    rtmutex = root / "kernel/locking/rtmutex.c"
    if not futex.is_file() or not rtmutex.is_file():
        raise SystemExit("missing PS7331 futex/rtmutex source")
    fu = futex.read_text(encoding="utf-8", errors="replace").splitlines()
    rt = rtmutex.read_text(encoding="utf-8", errors="replace").splitlines()
    proxy_start = first_line(rt, r"int rt_mutex_start_proxy_lock\(")
    landmarks = {
        "distinct_uaddr_check": first_line(fu, r"if \(uaddr1 == uaddr2\)"),
        "pi_state_refill": first_line(fu, r"refill_pi_state_cache\(\)"),
        "nr_wake_one_check": first_line(fu, r"if \(nr_wake != 1\)"),
        "top_waiter_lookup": first_line(fu, r"top_waiter = futex_top_waiter"),
        "no_waiter_return": first_line(fu, r"if \(!top_waiter\)"),
        "proxy_precondition": first_line(fu, r"requeue_pi && \(task_count - nr_wake < nr_requeue\)"),
        "paired_waiter_check": first_line(fu, r"requeue_pi && !this->rt_waiter"),
        "requeue_key_check": first_line(fu, r"requeue_pi && !match_futex\(this->requeue_pi_key"),
        "proxy_call": first_line(fu, r"rt_mutex_start_proxy_lock\(&pi_state->pi_mutex"),
        "stored_task_argument": first_line(fu, r"this->task\);"),
        "proxy_ret_cleanup": first_line(fu, r"\} else if \(ret\)"),
        "early_deadlock": first_line(rt, r"if \(owner == task\)"),
        "waiter_task_assignment": first_line(rt, r"waiter->task = task"),
        "task_pi_blocked_on": first_line(rt, r"task->pi_blocked_on = waiter"),
        "proxy_wrapper_start": proxy_start,
        "proxy_wrapper_cleanup": first_line_after(rt, r"if \(unlikely\(ret\)\)", proxy_start),
        "current_cleanup": first_line(rt, r"current->pi_blocked_on = NULL"),
    }
    states = [
        {
            "state": "single_context_no_waiter",
            "required_context": "one caller context; no pre-existing matching WAIT_REQUEUE_PI waiter",
            "no_waiter_branch": True,
            "proxy_call_reached": False,
            "identity_mismatch_observable": False,
            "stateful_side_effect_possible": True,
            "classification": "not_a_proxy_runtime_test",
        },
        {
            "state": "paired_waiter_proxy_candidate",
            "required_context": "pre-existing matching requeue waiter plus a requeue caller",
            "no_waiter_branch": False,
            "proxy_call_reached": True,
            "identity_mismatch_observable": True,
            "stateful_side_effect_possible": True,
            "classification": "stateful_and_risk_bounded_out",
        },
    ]
    return {
        "schema": "phase6c-requeue-preconditions-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "futex": {"path": str(futex), "sha256": sha256(futex)},
            "rtmutex": {"path": str(rtmutex), "sha256": sha256(rtmutex)},
        },
        "landmarks": landmarks,
        "abstract_states": states,
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "futex_triggered": False,
            "thread_created": False,
            "race_scheduled": False,
            "kernel_memory_accessed": False,
            "payload_or_address_generated": False,
        },
        "conclusion": (
            "A single-context no-waiter call can only classify the no-waiter branch; "
            "it cannot observe waiter->task versus current. The proxy identity "
            "question requires a pre-existing matching waiter and is therefore a "
            "stateful runtime experiment, not a harmless switch probe."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "device_contacted": False,
            "futex_triggered": False,
            "source_root": str(args.source_root),
            "output": str(args.output),
        }, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    result = build(args.source_root)
    args.output.mkdir(parents=True)
    summary = args.output / "preconditions.json"
    matrix = args.output / "precondition-matrix.csv"
    report = args.output / "result.md"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with matrix.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "state", "required_context", "no_waiter_branch", "proxy_call_reached",
            "identity_mismatch_observable", "stateful_side_effect_possible", "classification",
        ], lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["abstract_states"])
    report.write_text(
        "# Phase 6C requeue-PI precondition model\n\n"
        "Host-only source model; no device, syscall, thread, race, memory or payload.\n\n"
        "- Single-context/no-waiter: proxy call not reached; identity mismatch not observable.\n"
        "- Paired-waiter/proxy candidate: proxy call is structurally reachable; this is stateful and outside the stock-device safety boundary.\n\n"
        + result["conclusion"] + "\n",
        encoding="utf-8",
    )
    files = (summary, matrix, report)
    (args.output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
