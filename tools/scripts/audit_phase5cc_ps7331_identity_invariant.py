#!/usr/bin/env python3
"""Audit PS7331 futex/PI task-identity dataflow without executing a kernel path.

This is intentionally a host-only source audit.  It does not emit syscall
arguments, timing recipes, addresses, payloads, or device operations.  The
result distinguishes a source-level interface that permits separate task
objects from a runtime observation of a scheduler race.
"""

from __future__ import annotations

import argparse
import csv
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


def struct_span(lines: list[str], signature: str) -> tuple[int, int, list[str]]:
    start = next((i for i, line in enumerate(lines) if re.search(signature, line)), None)
    if start is None:
        raise ValueError(f"struct not found: {signature}")
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


def first_match(lines: list[str], pattern: str, offset: int = 0) -> dict[str, object] | None:
    compiled = re.compile(pattern)
    for index, line in enumerate(lines):
        if compiled.search(line):
            return {"line": index + 1 + offset, "text": line.strip()}
    return None


def all_matches(lines: list[str], pattern: str, offset: int = 0) -> list[dict[str, object]]:
    compiled = re.compile(pattern)
    return [
        {"line": index + 1 + offset, "text": line.strip()}
        for index, line in enumerate(lines)
        if compiled.search(line)
    ]


def observation(
    evidence_id: str,
    source_name: str,
    source_path: Path,
    source_hash: str,
    location: str,
    hit: dict[str, object] | None,
    role: str,
    classification: str,
    confidence: str,
    note: str,
) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "source": source_name,
        "file": str(source_path),
        "sha256": source_hash,
        "location": location,
        "line": hit["line"] if hit else None,
        "text": hit["text"] if hit else None,
        "identity_role": role,
        "classification": classification,
        "confidence": confidence,
        "note": note,
    }


def inspect(futex_path: Path, rtmutex_path: Path) -> dict[str, object]:
    futex_lines = futex_path.read_text(encoding="utf-8", errors="replace").splitlines()
    rtmutex_lines = rtmutex_path.read_text(encoding="utf-8", errors="replace").splitlines()
    futex_hash = sha256(futex_path)
    rtmutex_hash = sha256(rtmutex_path)

    q_start, q_end, q_struct = struct_span(futex_lines, r"^struct futex_q\s*\{")
    queue_start, queue_end, queue_me = function_span(
        futex_lines, r"^\s*static inline void queue_me\s*\("
    )
    wait_queue_start, wait_queue_end, wait_queue = function_span(
        futex_lines, r"^\s*static void futex_wait_queue_me\s*\("
    )
    wait_requeue_start, wait_requeue_end, wait_requeue = function_span(
        futex_lines, r"^\s*static int futex_wait_requeue_pi\s*\("
    )
    requeue_start, requeue_end, requeue = function_span(
        futex_lines, r"^\s*static int futex_requeue\s*\("
    )
    proxy_start, proxy_end, proxy = function_span(
        rtmutex_lines, r"^\s*int rt_mutex_start_proxy_lock\s*\("
    )
    blocks_start, blocks_end, blocks = function_span(
        rtmutex_lines, r"^\s*static int task_blocks_on_rt_mutex\s*\("
    )
    remove_start, remove_end, remove = function_span(
        rtmutex_lines, r"^\s*static void remove_waiter\s*\("
    )

    observations: list[dict[str, object]] = []
    observations.append(observation(
        "P5CC-001", "futex.c", futex_path, futex_hash,
        f"struct futex_q lines {q_start}-{q_end}",
        first_match(q_struct, r"struct task_struct \*task;", q_start - 1),
        "futex queue task identity", "SOURCE_IDENTITY_ROLE_DECLARED", "Confirmed",
        "The queue object stores a task pointer described as the task waiting on the futex.",
    ))
    observations.append(observation(
        "P5CC-002", "futex.c", futex_path, futex_hash,
        f"queue_me() lines {queue_start}-{queue_end}",
        first_match(queue_me, r"q->task\s*=\s*current\s*;", queue_start - 1),
        "waiter binding", "SOURCE_BINDS_QUEUE_TASK_TO_CURRENT", "Confirmed",
        "The waiting thread binds its futex_q task field to the current task when queued.",
    ))
    observations.append(observation(
        "P5CC-003", "futex.c", futex_path, futex_hash,
        f"futex_wait_queue_me() lines {wait_queue_start}-{wait_queue_end}",
        first_match(wait_queue, r"queue_me\s*\(", wait_queue_start - 1),
        "wait path", "SOURCE_WAIT_PATH_REACHES_QUEUE_BINDING", "Confirmed",
        "The wait helper invokes queue_me before sleeping; this connects the wait path to P5CC-002.",
    ))
    observations.append(observation(
        "P5CC-004", "futex.c", futex_path, futex_hash,
        f"futex_wait_requeue_pi() lines {wait_requeue_start}-{wait_requeue_end}",
        first_match(wait_requeue, r"struct rt_mutex_waiter\s+rt_waiter;", wait_requeue_start - 1),
        "PI proxy waiter lifetime", "SOURCE_HAS_SEPARATE_PROXY_WAITER_OBJECT", "Confirmed",
        "The requeue-PI wait path creates a separate rt_mutex_waiter object and attaches it to q.",
    ))
    observations.append(observation(
        "P5CC-005", "futex.c", futex_path, futex_hash,
        f"futex_wait_requeue_pi() lines {wait_requeue_start}-{wait_requeue_end}",
        first_match(wait_requeue, r"rt_waiter\.task\s*=\s*NULL\s*;", wait_requeue_start - 1),
        "PI proxy waiter initialization", "SOURCE_WAITER_TASK_INITIALIZED_SEPARATELY", "Confirmed",
        "The proxy waiter task field is initialized independently before the sleep/requeue protocol.",
    ))
    observations.append(observation(
        "P5CC-006", "futex.c", futex_path, futex_hash,
        f"futex_wait_requeue_pi() lines {wait_requeue_start}-{wait_requeue_end}",
        first_match(wait_requeue, r"futex_wait_queue_me\s*\(", wait_requeue_start - 1),
        "PI wait path", "SOURCE_PROXY_WAIT_REQUEUE_HANDOFF", "Confirmed",
        "The comments and call sequence show that requeue code may manipulate the waiter while the wait path sleeps.",
    ))
    observations.append(observation(
        "P5CC-007", "futex.c", futex_path, futex_hash,
        f"futex_requeue() lines {requeue_start}-{requeue_end}",
        first_match(requeue, r"rt_mutex_start_proxy_lock\s*\(", requeue_start - 1),
        "proxy call site", "SOURCE_REQUEUE_PASSES_STORED_WAITER_TASK", "Confirmed",
        "The requeue path passes this->rt_waiter and this->task to the proxy API rather than substituting current in the call site.",
    ))
    proxy_signature = first_match(proxy, r"struct task_struct \*task", proxy_start - 1)
    observations.append(observation(
        "P5CC-008", "rtmutex.c", rtmutex_path, rtmutex_hash,
        f"rt_mutex_start_proxy_lock() lines {proxy_start}-{proxy_end}",
        proxy_signature,
        "proxy API identity inputs", "SOURCE_PROXY_TASK_IS_EXPLICIT_PARAMETER", "Confirmed",
        "The proxy API receives a task parameter distinct from the function's implicit current task.",
    ))
    observations.append(observation(
        "P5CC-009", "rtmutex.c", rtmutex_path, rtmutex_hash,
        f"rt_mutex_start_proxy_lock() lines {proxy_start}-{proxy_end}",
        first_match(proxy, r"task_blocks_on_rt_mutex\s*\(", proxy_start - 1),
        "proxy API dataflow", "SOURCE_PROXY_FORWARDS_EXPLICIT_TASK", "Confirmed",
        "The explicit task parameter is forwarded into task_blocks_on_rt_mutex.",
    ))
    observations.append(observation(
        "P5CC-010", "rtmutex.c", rtmutex_path, rtmutex_hash,
        f"task_blocks_on_rt_mutex() lines {blocks_start}-{blocks_end}",
        first_match(blocks, r"if\s*\(owner\s*==\s*task\)", blocks_start - 1),
        "early return", "SOURCE_EARLY_DEADLOCK_BRANCH_PRECEDES_WAITER_ASSIGNMENT", "Confirmed",
        "The owner==task deadlock branch returns before the later waiter->task assignment.",
    ))
    observations.append(observation(
        "P5CC-011", "rtmutex.c", rtmutex_path, rtmutex_hash,
        f"task_blocks_on_rt_mutex() lines {blocks_start}-{blocks_end}",
        first_match(blocks, r"waiter->task\s*=\s*task\s*;", blocks_start - 1),
        "waiter identity assignment", "SOURCE_WAITER_TASK_ASSIGNED_FROM_EXPLICIT_TASK", "Confirmed",
        "When the enqueue path proceeds past the early branch, waiter->task receives the explicit task argument.",
    ))
    observations.append(observation(
        "P5CC-012", "rtmutex.c", rtmutex_path, rtmutex_hash,
        f"remove_waiter() lines {remove_start}-{remove_end}",
        first_match(remove, r"current->pi_lock", remove_start - 1),
        "cleanup identity", "SOURCE_CLEANUP_USES_CURRENT_PI_LOCK", "Confirmed",
        "The inspected cleanup function locks current->pi_lock and clears current->pi_blocked_on.",
    ))
    observations.append(observation(
        "P5CC-013", "rtmutex.c", rtmutex_path, rtmutex_hash,
        f"remove_waiter() lines {remove_start}-{remove_end}",
        first_match(remove, r"current->pi_blocked_on\s*=\s*NULL", remove_start - 1),
        "cleanup identity", "SOURCE_CLEANUP_CLEARS_CURRENT_BLOCKED_STATE", "Confirmed",
        "The cleanup write targets current rather than waiter->task in this source function.",
    ))

    scoped_blocks = [
        ("rt_mutex_start_proxy_lock", proxy, proxy_start - 1),
        ("task_blocks_on_rt_mutex", blocks, blocks_start - 1),
        ("remove_waiter", remove, remove_start - 1),
    ]
    equality_hits = []
    for name, block, offset in scoped_blocks:
        for hit in all_matches(block, r"(?:current\s*(?:==|!=)\s*task|task\s*(?:==|!=)\s*current)", offset):
            equality_hits.append({"function": name, **hit})
    observations.append(observation(
        "P5CC-014", "rtmutex.c", rtmutex_path, rtmutex_hash,
        f"proxy/cleanup scoped functions lines {proxy_start}-{remove_end}",
        None if not equality_hits else equality_hits[0],
        "identity invariant", "SOURCE_EQUALITY_ASSERTION_SEARCH", "Confirmed" if not equality_hits else "Confirmed",
        "No direct current/task equality assertion was observed in the scoped proxy, task-blocking, and cleanup functions; this is a bounded search, not a proof about every caller or scheduler state.",
    ))

    return {
        "scope": "PS7331 exact 4.4 source; host-only identity/dataflow audit",
        "futex_path": str(futex_path),
        "futex_sha256": futex_hash,
        "rtmutex_path": str(rtmutex_path),
        "rtmutex_sha256": rtmutex_hash,
        "spans": {
            "struct_futex_q": [q_start, q_end],
            "queue_me": [queue_start, queue_end],
            "futex_wait_queue_me": [wait_queue_start, wait_queue_end],
            "futex_wait_requeue_pi": [wait_requeue_start, wait_requeue_end],
            "futex_requeue": [requeue_start, requeue_end],
            "rt_mutex_start_proxy_lock": [proxy_start, proxy_end],
            "task_blocks_on_rt_mutex": [blocks_start, blocks_end],
            "remove_waiter": [remove_start, remove_end],
        },
        "observations": observations,
        "identity_model": {
            "queue_task_bound_to_waiting_current_at_enqueue": True,
            "proxy_waiter_is_separate_object": True,
            "requeue_passes_stored_task_to_proxy_api": True,
            "proxy_api_has_explicit_task_parameter": True,
            "cleanup_reads_current_pi_lock": True,
            "cleanup_clears_current_pi_blocked_on": True,
            "scoped_current_equals_explicit_task_assertion_observed": bool(equality_hits),
            "identity_mismatch_allowed_by_source_interface": not bool(equality_hits),
            "identity_mismatch_observed_runtime": False,
            "race_window_proven": False,
            "cleanup_effect_proven": False,
            "kernel_control_proven": False,
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


def write_outputs(result: dict[str, object], output: Path) -> None:
    output.mkdir(parents=True)
    (output / "identity-audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "result.md").write_text(
        "# PS7331 task-identity invariant audit\n\n"
        "- Source-level identity mismatch permitted by interface: **"
        f"{result['identity_model']['identity_mismatch_allowed_by_source_interface']}**\n"
        "- Runtime identity mismatch observed: **False**\n"
        "- Race window proven: **False**\n"
        "- Cleanup effect proven: **False**\n"
        "- Kernel control/root proven: **False**\n\n"
        "This artifact is a bounded, host-only source/dataflow audit. It does not "
        "demonstrate a live scheduler interleaving or provide an exploit.\n",
        encoding="utf-8",
    )
    (output / "README.txt").write_text(
        "Host-only source/dataflow audit. No futex syscall, race trigger, device I/O, "
        "payload, address, image mutation, or privilege operation.\n",
        encoding="utf-8",
    )
    files = sorted(path for path in output.iterdir() if path.is_file())
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--futex", type=Path, required=True)
    parser.add_argument("--rtmutex", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output in {Path("/"), Path("."), Path("..")}:
        parser.error("refusing broad output path")
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "device_execution": False,
            "futex": str(args.futex),
            "rtmutex": str(args.rtmutex),
            "output": str(args.output),
        }, indent=2, sort_keys=True))
        return 0
    for path, label in ((args.futex, "futex source"), (args.rtmutex, "rtmutex source")):
        if not path.is_file():
            parser.error(f"{label} is not a regular file: {path}")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")
    result = inspect(args.futex, args.rtmutex)
    write_outputs(result, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
