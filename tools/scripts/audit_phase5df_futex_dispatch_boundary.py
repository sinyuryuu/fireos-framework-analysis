#!/usr/bin/env python3
"""Extract the PS7331 futex requeue-PI dispatch boundary.

This is a host-only, read-only source audit.  It reads the preserved kernel
source as text and records the dispatch, proxy-lock, and cleanup landmarks.
It does not compile or execute source, issue a futex syscall, contact a
device, generate kernel addresses, or generate an exploit payload.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


LANDMARKS = (
    ("syscall_entry", re.compile(r"SYSCALL_DEFINE6\(futex")),
    ("requeue_parameter", re.compile(r"cmd == FUTEX_CMP_REQUEUE_PI")),
    ("dispatch_wait_requeue_pi", re.compile(r"case FUTEX_WAIT_REQUEUE_PI")),
    ("dispatch_cmp_requeue_pi", re.compile(r"case FUTEX_CMP_REQUEUE_PI")),
    ("wait_requeue_pi_call", re.compile(r"return futex_wait_requeue_pi")),
    ("cmp_requeue_pi_call", re.compile(r"return futex_requeue\(.*1\)")),
    ("proxy_precondition", re.compile(r"requeue_pi && \(task_count - nr_wake < nr_requeue\)")),
    ("proxy_trylock", re.compile(r"futex_proxy_trylock_atomic")),
    ("proxy_start", re.compile(r"rt_mutex_start_proxy_lock")),
    ("proxy_waiter", re.compile(r"this->rt_waiter")),
    ("proxy_task", re.compile(r"this->task")),
    ("cleanup_ret_branch", re.compile(r"else if \(ret\)")),
    ("cleanup_remove_waiter", re.compile(r"remove_waiter\(lock, waiter\)")),
    ("early_self_deadlock", re.compile(r"if \(owner == task\)")),
    ("waiter_task_assignment", re.compile(r"waiter->task = task")),
    ("current_cleanup", re.compile(r"current->pi_blocked_on = NULL")),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def scan_file(path: Path, source_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    relative = path.relative_to(source_root).as_posix()
    for line_number, line in enumerate(read_lines(path), 1):
        compact = " ".join(line.strip().split())
        for label, pattern in LANDMARKS:
            if pattern.search(line):
                rows.append(
                    {
                        "file": relative,
                        "line": line_number,
                        "landmark": label,
                        "excerpt": compact,
                    }
                )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["file", "line", "landmark", "excerpt"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    futex = args.kernel_root / "kernel" / "futex.c"
    rtmutex = args.kernel_root / "kernel" / "locking" / "rtmutex.c"
    if args.dry_run:
        print(
            json.dumps(
                {
                    "kernel_root": str(args.kernel_root),
                    "inputs": [str(futex), str(rtmutex)],
                    "output": str(args.output),
                    "device_contacted": False,
                    "source_executed": False,
                    "futex_triggered": False,
                },
                indent=2,
            )
        )
        return 0

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    for path in (futex, rtmutex):
        if not path.is_file():
            raise FileNotFoundError(path)
    args.output.mkdir(parents=True)

    rows = scan_file(futex, args.kernel_root) + scan_file(rtmutex, args.kernel_root)
    rows.sort(key=lambda row: (str(row["file"]), int(row["line"]), str(row["landmark"])))
    csv_path = args.output / "futex-dispatch-landmarks.csv"
    write_csv(csv_path, rows)

    by_file: dict[str, list[int]] = {}
    for path in (futex, rtmutex):
        by_file[path.relative_to(args.kernel_root).as_posix()] = [
            int(path.stat().st_size),
        ]
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "kernel_root": str(args.kernel_root),
        "input_files": {
            str(path.relative_to(args.kernel_root)): {
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in (futex, rtmutex)
        },
        "landmark_rows": len(rows),
        "landmarks": sorted({str(row["landmark"]) for row in rows}),
        "device_contacted": False,
        "source_executed": False,
        "futex_triggered": False,
        "kernel_memory_accessed": False,
        "payload_or_address_generated": False,
        "interpretation": (
            "The preserved source exposes a futex syscall dispatch to the "
            "requeue-PI implementation and a proxy waiter/task dataflow. "
            "This is source reachability evidence only; it does not establish "
            "a shipped userspace caller, a runtime identity mismatch, cleanup "
            "residue, memory corruption, or privilege transition."
        ),
    }
    summary_path = args.output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    manifest = args.output / "sha256sums.txt"
    manifest.write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in (csv_path, summary_path))
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
