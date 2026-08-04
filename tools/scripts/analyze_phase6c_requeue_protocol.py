#!/usr/bin/env python3
"""Host-only analysis of the PS7331 futex requeue-PI selftest protocol.

This script reads preserved C/header/source files and records the static
protocol roles used by the upstream-style selftest.  It does not compile or
execute the files, construct syscall arguments, create threads, schedule a
race, contact a device, access kernel memory, or generate a payload.
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


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def hits(lines: list[str], pattern: str) -> list[int]:
    regex = re.compile(pattern)
    return [number for number, line in enumerate(lines, 1) if regex.search(line)]


def first(lines: list[str], pattern: str) -> int | None:
    values = hits(lines, pattern)
    return values[0] if values else None


def source_record(path: Path, labels: dict[str, str]) -> dict[str, object]:
    lines = read_lines(path)
    landmarks = {
        name: hits(lines, pattern)
        for name, pattern in labels.items()
    }
    return {
        "path": str(path),
        "sha256": sha256(path),
        "line_count": len(lines),
        "landmarks": landmarks,
    }


def build(args: argparse.Namespace) -> dict[str, object]:
    header = args.selftest_root / "include/futextest.h"
    functional = args.selftest_root / "functional/futex_requeue_pi.c"
    mismatch = args.selftest_root / "functional/futex_requeue_pi_mismatched_ops.c"
    futex = args.kernel_root / "kernel/futex.c"
    for path in (header, functional, mismatch, futex):
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")

    header_record = source_record(header, {
        "wait_helper": r"futex_wait_requeue_pi\s*\(",
        "requeue_helper": r"futex_cmp_requeue_pi\s*\(",
        "wait_opcode": r"#define\s+FUTEX_WAIT_REQUEUE_PI\s+",
        "requeue_opcode": r"#define\s+FUTEX_CMP_REQUEUE_PI\s+",
        "pairing_note": r"always be\s*$|paired with futex_cmp_requeue_pi",
    })
    functional_record = source_record(functional, {
        "waiter_function": r"void\s*\*waiterfn\s*\(",
        "broadcast_waker_function": r"void\s*\*broadcast_wakerfn\s*\(",
        "signal_waker_function": r"void\s*\*signal_wakerfn\s*\(",
        "thread_creation": r"pthread_create\s*\(",
        "waiter_call": r"futex_wait_requeue_pi\s*\(",
        "waker_call": r"futex_cmp_requeue_pi\s*\(",
        "wait_for_waiters": r"waiters_blocked",
        "sleep_or_yield": r"\b(?:sleep|usleep)\s*\(",
        "join": r"pthread_join\s*\(",
        "pi_lock": r"futex_lock_pi\s*\(",
        "pi_unlock": r"futex_unlock_pi\s*\(",
    })
    mismatch_record = source_record(mismatch, {
        "thread_creation": r"pthread_create\s*\(",
        "ordinary_wait_call": r"futex_wait\s*\(",
        "requeue_call": r"futex_cmp_requeue_pi\s*\(",
        "delay_for_child": r"sleep\s*\(",
        "wake_after_check": r"futex_wake\s*\(",
        "join": r"pthread_join\s*\(",
    })
    futex_record = source_record(futex, {
        "requeue_dispatch": r"case\s+FUTEX_CMP_REQUEUE_PI\s*:",
        "wait_requeue_dispatch": r"case\s+FUTEX_WAIT_REQUEUE_PI\s*:",
        "no_waiter_return": r"if\s*\(!top_waiter\)",
        "proxy_call": r"rt_mutex_start_proxy_lock\s*\(",
        "stored_task_argument": r"this->task",
        "proxy_return_cleanup": r"else\s+if\s*\(ret\)",
    })

    protocol_rows = [
        {
            "role_or_condition": "waiter role",
            "source": str(functional),
            "line": ",".join(map(str, functional_record["landmarks"]["waiter_function"])),
            "static_fact": "A task calls FUTEX_WAIT_REQUEUE_PI and remains part of the requeue protocol.",
            "runtime_implication": "A single caller cannot create this pre-existing waiter state.",
            "classification": "stateful_precondition",
        },
        {
            "role_or_condition": "waker/requeue role",
            "source": str(functional),
            "line": ",".join(map(str, functional_record["landmarks"]["broadcast_waker_function"] + functional_record["landmarks"]["signal_waker_function"])),
            "static_fact": "A distinct control path calls FUTEX_CMP_REQUEUE_PI after waiters are observed.",
            "runtime_implication": "The proxy path requires at least two participating execution contexts.",
            "classification": "stateful_precondition",
        },
        {
            "role_or_condition": "waiter/waker ordering",
            "source": str(functional),
            "line": ",".join(map(str, functional_record["landmarks"]["wait_for_waiters"])),
            "static_fact": "The selftest waits for waiter progress before issuing the requeue operation.",
            "runtime_implication": "This is synchronization, not a harmless feature probe.",
            "classification": "ordering_requirement",
        },
        {
            "role_or_condition": "kernel no-waiter branch",
            "source": str(futex),
            "line": ",".join(map(str, futex_record["landmarks"]["no_waiter_return"])),
            "static_fact": "The kernel has a no-waiter return before the proxy call.",
            "runtime_implication": "A call without a matching waiter cannot observe waiter identity.",
            "classification": "bounded_no_waiter",
        },
        {
            "role_or_condition": "proxy branch",
            "source": str(futex),
            "line": ",".join(map(str, futex_record["landmarks"]["proxy_call"])),
            "static_fact": "The source contains a call to rt_mutex_start_proxy_lock().",
            "runtime_implication": "Static reachability is not runtime execution evidence.",
            "classification": "static_only",
        },
        {
            "role_or_condition": "mismatch selftest",
            "source": str(mismatch),
            "line": ",".join(map(str, mismatch_record["landmarks"]["ordinary_wait_call"] + mismatch_record["landmarks"]["requeue_call"])),
            "static_fact": "The negative selftest also creates a child waiter before testing the mismatch.",
            "runtime_implication": "Even the error-path test is not a single-call test.",
            "classification": "stateful_precondition",
        },
    ]
    return {
        "schema": "phase6c-requeue-protocol-analysis-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "selftest_header": header_record,
            "functional_selftest": functional_record,
            "mismatched_ops_selftest": mismatch_record,
            "kernel_futex": futex_record,
        },
        "protocol_rows": protocol_rows,
        "conclusion": (
            "The preserved PS7331 selftests define requeue-PI as a paired, stateful "
            "protocol. A single-thread/single-call probe can classify only the "
            "no-waiter or argument-validation boundary; it cannot validate the "
            "proxy identity condition or cleanup consequence."
        ),
        "safety": {
            "host_only": True,
            "source_compiled": False,
            "source_executed": False,
            "thread_created": False,
            "race_scheduled": False,
            "device_contacted": False,
            "futex_triggered": False,
            "kernel_memory_accessed": False,
            "payload_or_address_generated": False,
        },
    }


def write_outputs(output: Path, result: dict[str, object]) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    summary = output / "protocol-analysis.json"
    table = output / "protocol-matrix.csv"
    report = output / "result.md"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with table.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "role_or_condition", "source", "line", "static_fact",
            "runtime_implication", "classification",
        ], lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["protocol_rows"])
    report.write_text(
        "# Phase 6C requeue-PI protocol analysis\n\n"
        "Host-only source analysis. No compilation, execution, device contact, "
        "thread creation, race scheduling, kernel memory access or payload.\n\n"
        + result["conclusion"] + "\n\n"
        "The protocol matrix records why the proxy identity question is not "
        "covered by a single-call switch probe.\n",
        encoding="utf-8",
    )
    files = (summary, table, report)
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest-root", type=Path, required=True)
    parser.add_argument("--kernel-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "host_only": True,
            "source_compiled": False,
            "source_executed": False,
            "device_contacted": False,
            "output": str(args.output),
        }, indent=2))
        return 0
    result = build(args)
    write_outputs(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
