#!/usr/bin/env python3
"""Audit PS7331 proxy-task versus caller context from preserved source.

This is a host-only source/dataflow audit.  It does not compile or execute the
kernel, invoke a futex syscall, generate syscall arguments, derive addresses,
construct a race schedule, or contact a device.  It records only bounded source
locations that establish the roles of the waiting task, the requeue caller and
the proxy error cleanup path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def line_no(lines: list[str], needle: str, start: int = 0, end: int | None = None) -> int:
    stop = len(lines) if end is None else min(end, len(lines))
    for index in range(max(start, 0), stop):
        if needle in lines[index]:
            return index + 1
    raise ValueError(f"source line not found: {needle}")


def span(lines: list[str], needle: str, end_needle: str) -> tuple[int, int]:
    start = line_no(lines, needle)
    end = line_no(lines, end_needle, start - 1)
    return start, end


def function_span(lines: list[str], needle: str) -> tuple[int, int]:
    start = line_no(lines, needle)
    depth = 0
    opened = False
    for index in range(start - 1, len(lines)):
        depth += lines[index].count("{") - lines[index].count("}")
        opened = opened or "{" in lines[index]
        if opened and depth == 0:
            return start, index + 1
    raise ValueError(f"function end not found: {needle}")


def struct_span(lines: list[str], needle: str) -> tuple[int, int]:
    return function_span(lines, needle)


def evidence(evidence_id: str, file_name: str, lines: list[str], number: int,
             role: str, text: str, classification: str) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "file": file_name,
        "line": number,
        "role": role,
        "text": text,
        "classification": classification,
        "confidence": "Confirmed, source scope",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--futex", type=Path, required=True)
    parser.add_argument("--rtmutex", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY-RUN: no source is read and no files are written.")
        print(f"FUTEX\t{args.futex}")
        print(f"RTMUTEX\t{args.rtmutex}")
        print(f"OUTPUT\t{args.output}")
        return 0

    if not args.futex.is_file() or not args.rtmutex.is_file():
        print("ERROR: source inputs must be regular files", file=sys.stderr)
        return 2
    if args.output.exists():
        print(f"ERROR: refusing to overwrite output: {args.output}", file=sys.stderr)
        return 2

    futex_lines = args.futex.read_text(encoding="utf-8", errors="replace").splitlines()
    rtmutex_lines = args.rtmutex.read_text(encoding="utf-8", errors="replace").splitlines()
    observations: list[dict[str, object]] = []

    q_start, q_end = struct_span(futex_lines, "struct futex_q {")
    queue_me_start, queue_me_end = function_span(futex_lines, "static inline void queue_me")
    wait_start, wait_end = function_span(futex_lines, "static int futex_wait_requeue_pi")
    requeue_start, requeue_end = function_span(futex_lines, "static int futex_requeue")
    proxy_start, proxy_end = function_span(rtmutex_lines, "int rt_mutex_start_proxy_lock")
    blocks_start, blocks_end = function_span(rtmutex_lines, "static int task_blocks_on_rt_mutex")
    cleanup_start, cleanup_end = function_span(rtmutex_lines, "static void remove_waiter")

    observations.extend([
        evidence("P5CP-001", str(args.futex), futex_lines,
                 line_no(futex_lines, "struct task_struct *task;", q_start - 1, q_end),
                 "futex_q waiting-task field", "struct task_struct *task;",
                 "SOURCE_ROLE_DECLARATION"),
        evidence("P5CP-002", str(args.futex), futex_lines,
                 line_no(futex_lines, "q->task = current;", queue_me_start - 1, queue_me_end),
                 "waiter enqueue context", "q->task = current;",
                 "SOURCE_WAITING_TASK_BINDING"),
        evidence("P5CP-003", str(args.futex), futex_lines,
                 line_no(futex_lines, "struct rt_mutex_waiter rt_waiter;", wait_start - 1, wait_end),
                 "proxy waiter object", "struct rt_mutex_waiter rt_waiter;",
                 "SOURCE_SEPARATE_PROXY_OBJECT"),
        evidence("P5CP-004", str(args.futex), futex_lines,
                 line_no(futex_lines, "futex_wait_queue_me(hb, &q, to);", wait_start - 1, wait_end),
                 "wait/requeue handoff", "futex_wait_queue_me(hb, &q, to);",
                 "SOURCE_WAIT_PATH_HANDOFF"),
        evidence("P5CP-005", str(args.futex), futex_lines,
                 line_no(futex_lines, "ret = rt_mutex_start_proxy_lock(&pi_state->pi_mutex,",
                         requeue_start - 1, requeue_end),
                 "requeue proxy call", "ret = rt_mutex_start_proxy_lock(&pi_state->pi_mutex,",
                 "SOURCE_PROXY_CALLSITE"),
        evidence("P5CP-006", str(args.futex), futex_lines,
                 line_no(futex_lines, "this->rt_waiter,", requeue_start - 1, requeue_end),
                 "proxy waiter argument", "this->rt_waiter,",
                 "SOURCE_PROXY_WAITER_ARGUMENT"),
        evidence("P5CP-007", str(args.futex), futex_lines,
                 line_no(futex_lines, "this->task);", requeue_start - 1, requeue_end),
                 "proxy task argument", "this->task);",
                 "SOURCE_STORED_TASK_ARGUMENT"),
        evidence("P5CP-008", str(args.rtmutex), rtmutex_lines,
                 line_no(rtmutex_lines, "struct task_struct *task)", proxy_start - 1, proxy_end),
                 "proxy API task parameter", "struct task_struct *task)",
                 "SOURCE_EXPLICIT_TASK_PARAMETER"),
        evidence("P5CP-009", str(args.rtmutex), rtmutex_lines,
                 line_no(rtmutex_lines, "ret = task_blocks_on_rt_mutex(lock, waiter, task,",
                         proxy_start - 1, proxy_end),
                 "proxy forwards task", "ret = task_blocks_on_rt_mutex(lock, waiter, task,",
                 "SOURCE_EXPLICIT_TASK_FORWARD"),
        evidence("P5CP-010", str(args.rtmutex), rtmutex_lines,
                 line_no(rtmutex_lines, "if (owner == task)", blocks_start - 1, blocks_end),
                 "early return condition", "if (owner == task)",
                 "SOURCE_EARLY_RETURN_BEFORE_ASSIGNMENT"),
        evidence("P5CP-011", str(args.rtmutex), rtmutex_lines,
                 line_no(rtmutex_lines, "waiter->task = task;", blocks_start - 1, blocks_end),
                 "waiter identity assignment", "waiter->task = task;",
                 "SOURCE_WAITER_TASK_ASSIGNMENT"),
        evidence("P5CP-012", str(args.rtmutex), rtmutex_lines,
                 line_no(rtmutex_lines, "if (unlikely(ret))", proxy_start - 1, proxy_end),
                 "proxy error branch", "if (unlikely(ret))",
                 "SOURCE_ERROR_CLEANUP_BRANCH"),
        evidence("P5CP-013", str(args.rtmutex), rtmutex_lines,
                 line_no(rtmutex_lines, "remove_waiter(lock, waiter);", proxy_start - 1, proxy_end),
                 "proxy error cleanup call", "remove_waiter(lock, waiter);",
                 "SOURCE_ERROR_CLEANUP_CALL"),
        evidence("P5CP-014", str(args.rtmutex), rtmutex_lines,
                 line_no(rtmutex_lines, "current->pi_blocked_on = NULL;", cleanup_start - 1, cleanup_end),
                 "cleanup executor identity", "current->pi_blocked_on = NULL;",
                 "SOURCE_CURRENT_CLEANUP"),
    ])

    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_io": False,
        "futex": {"path": str(args.futex), "sha256": sha256(args.futex)},
        "rtmutex": {"path": str(args.rtmutex), "sha256": sha256(args.rtmutex)},
        "spans": {
            "struct_futex_q": [q_start, q_end],
            "queue_me": [queue_me_start, queue_me_end],
            "futex_wait_requeue_pi": [wait_start, wait_end],
            "futex_requeue": [requeue_start, requeue_end],
            "rt_mutex_start_proxy_lock": [proxy_start, proxy_end],
            "task_blocks_on_rt_mutex": [blocks_start, blocks_end],
            "remove_waiter": [cleanup_start, cleanup_end],
        },
        "observations": observations,
        "classification": "SOURCE_CROSS_CONTEXT_PROXY_PATH_CONFIRMED_RUNTIME_UNOBSERVED",
        "source_context_result": {
            "waiting_task_binds_q_task_to_current": True,
            "requeue_passes_stored_task": True,
            "proxy_api_has_explicit_task": True,
            "cleanup_uses_implicit_current": True,
            "cross_context_identity_is_permitted_by_source": True,
            "error_branch_reaches_cleanup": True,
        },
        "runtime_result": {
            "identity_mismatch_observed": False,
            "remove_waiter_observed": False,
            "post_cleanup_state_observed": False,
        },
        "safety": {
            "source_executed": False,
            "kernel_built": False,
            "syscall_invoked": False,
            "race_triggered": False,
            "device_contacted": False,
            "payload_or_address_generated": False,
        },
    }

    args.output.mkdir(parents=True)
    (args.output / "proxy-context.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (args.output / "observations.csv").open("w", encoding="utf-8", newline="") as stream:
        stream.write("evidence_id,file,line,role,text,classification,confidence\n")
        for item in observations:
            values = [str(item[key]).replace('"', '""') for key in
                      ("evidence_id", "file", "line", "role", "text", "classification", "confidence")]
            stream.write('"' + '","'.join(values) + '"\n')
    (args.output / "result.md").write_text(
        "# Phase 5CP proxy context audit\n\n"
        "Host-only source/dataflow audit. No kernel was built or executed; no device, "
        "syscall, race trigger, address, payload or privilege operation was used.\n\n"
        "Classification: `SOURCE_CROSS_CONTEXT_PROXY_PATH_CONFIRMED_RUNTIME_UNOBSERVED`.\n"
        "The source permits a stored waiting task to be passed through the proxy API "
        "while cleanup uses the caller's implicit `current`; runtime execution and "
        "post-cleanup effects remain unobserved.\n",
        encoding="utf-8",
    )
    (args.output / "commands.txt").write_text(
        "python3 tools/scripts/audit_phase5cp_proxy_context.py \\\n+  --futex " + str(args.futex) + " \\\n+  --rtmutex " + str(args.rtmutex) + " \\\n+  --output " + str(args.output) + "\n",
        encoding="utf-8",
    )
    files = sorted(args.output.iterdir())
    with (args.output / "sha256sums.txt").open("w", encoding="utf-8") as stream:
        for path in files:
            if path.name == "sha256sums.txt":
                continue
            stream.write(f"{sha256(path)}  {path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
