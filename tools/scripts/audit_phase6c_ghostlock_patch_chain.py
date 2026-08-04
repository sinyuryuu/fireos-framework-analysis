#!/usr/bin/env python3
"""Host-only audit of the PS7331 GhostLock-related patch-chain markers.

The audit compares the preserved 4.4 source against high-level signatures of
the upstream fixes.  It does not fetch or execute a PoC, compile a kernel,
construct futex arguments, create a waiter, schedule a race, contact ADB, or
generate a privilege-escalation payload.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


UPSTREAM_REFERENCES = [
    {
        "id": "3bfdc63936dd4773109b7b8c280c0f3b5ae7d349",
        "subject": "rtmutex: Use waiter::task instead of current in remove_waiter()",
        "scope": "primary cleanup-target fix",
        "url": "https://git.kernel.org/stable/c/3bfdc63936dd4773109b7b8c280c0f3b5ae7d349",
    },
    {
        "id": "1a1fb985f2e2b85ec0d3dc2e519ee48389ec2434",
        "subject": "futex: Handle early deadlock return correctly",
        "scope": "wrapper/early-return cleanup arrangement",
        "url": "https://git.kernel.org/stable/c/1a1fb985f2e2b85ec0d3dc2e519ee48389ec2434",
    },
    {
        "id": "post-3bfd-enqueued-guard",
        "subject": "locking/rtmutex: Skip remove_waiter() when waiter is not enqueued",
        "scope": "later waiter-task null/enqueued guard",
        "url": "https://lkml.iu.edu/2606.0/06468.html",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def first_line(lines: list[str], expression: str, start: int = 1) -> int | None:
    pattern = re.compile(expression)
    for number in range(max(1, start), len(lines) + 1):
        if pattern.search(lines[number - 1]):
            return number
    return None


def check(
    check_id: str,
    patch_id: str,
    file: Path,
    lines: list[str],
    expression: str,
    expected: str,
    start: int = 1,
) -> dict[str, object]:
    line = first_line(lines, expression, start)
    return {
        "check": check_id,
        "patch": patch_id,
        "file": str(file),
        "line": line if line is not None else "NOT_FOUND",
        "pattern": expression,
        "observation": "FOUND" if line is not None else "NOT_FOUND",
        "expected_for_fixed_tree": expected,
        "file_sha256": sha256(file),
    }


def build(source_root: Path) -> dict[str, object]:
    rtmutex = source_root / "kernel/locking/rtmutex.c"
    futex = source_root / "kernel/futex.c"
    common = source_root / "kernel/locking/rtmutex_common.h"
    for path in (rtmutex, futex, common):
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")
    rt = load_lines(rtmutex)
    fu = load_lines(futex)
    wrapper = first_line(rt, r"int rt_mutex_start_proxy_lock\(")
    remove_waiter = first_line(rt, r"static void remove_waiter\(")
    checks = [
        check(
            "primary_current_cleanup",
            "3bfdc63936dd4773109b7b8c280c0f3b5ae7d349",
            rtmutex,
            rt,
            r"current->pi_blocked_on = NULL;",
            "absent; fixed code uses waiter_task->pi_blocked_on",
            remove_waiter or 1,
        ),
        check(
            "primary_waiter_task_assignment",
            "3bfdc63936dd4773109b7b8c280c0f3b5ae7d349",
            rtmutex,
            rt,
            r"waiter->task = task;",
            "present as the task identity source",
            1,
        ),
        check(
            "primary_waiter_task_local",
            "3bfdc63936dd4773109b7b8c280c0f3b5ae7d349",
            rtmutex,
            rt,
            r"struct task_struct \*waiter_task\s*=\s*waiter->task;",
            "present before dequeue/cleanup",
            remove_waiter or 1,
        ),
        check(
            "wrapper_nonzero_cleanup",
            "1a1fb985f2e2b85ec0d3dc2e519ee48389ec2434",
            rtmutex,
            rt,
            r"if \(unlikely\(ret\)\)",
            "wrapper uses ret < 0 for remove_waiter",
            wrapper or 1,
        ),
        check(
            "wrapper_negative_cleanup",
            "1a1fb985f2e2b85ec0d3dc2e519ee48389ec2434",
            rtmutex,
            rt,
            r"if \(unlikely\(ret\s*<\s*0\)\)",
            "present in the fixed wrapper",
            wrapper or 1,
        ),
        check(
            "unenqueued_waiter_guard",
            "post-3bfd-enqueued-guard",
            rtmutex,
            rt,
            r"if \(!waiter_task\)",
            "present before remove_waiter body performs dereference/dequeue",
            remove_waiter or 1,
        ),
        check(
            "futex_proxy_call",
            "3bfdc63936dd4773109b7b8c280c0f3b5ae7d349",
            futex,
            fu,
            r"rt_mutex_start_proxy_lock\(",
            "call site is present for a runtime proxy path",
            1,
        ),
        check(
            "futex_proxy_nonzero_branch",
            "1a1fb985f2e2b85ec0d3dc2e519ee48389ec2434",
            futex,
            fu,
            r"else if \(ret\)",
            "caller branch is present; runtime entry remains unobserved",
            1,
        ),
    ]
    findings = {
        "primary_fix_pre_fix_shape": checks[0]["observation"] == "FOUND" and checks[2]["observation"] == "NOT_FOUND",
        "early_return_pre_fix_shape": checks[3]["observation"] == "FOUND" and checks[4]["observation"] == "NOT_FOUND",
        "unenqueued_guard_present": checks[5]["observation"] == "FOUND",
        "proxy_path_static_present": checks[6]["observation"] == "FOUND" and checks[7]["observation"] == "FOUND",
    }
    return {
        "schema": "phase6c-ghostlock-patch-chain-audit-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source_root),
        "inputs": {
            "futex": {"path": str(futex), "sha256": sha256(futex)},
            "rtmutex": {"path": str(rtmutex), "sha256": sha256(rtmutex)},
            "rtmutex_common": {"path": str(common), "sha256": sha256(common)},
        },
        "upstream_references": UPSTREAM_REFERENCES,
        "checks": checks,
        "findings": findings,
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "kernel_built": False,
            "futex_triggered": False,
            "threads_created": False,
            "race_scheduled": False,
            "kernel_memory_accessed": False,
            "payload_generated": False,
        },
    }


def write_output(result: dict[str, object], output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    summary = output / "patch-chain.json"
    matrix = output / "patch-chain.csv"
    report = output / "result.md"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["check", "patch", "file", "line", "observation", "expected_for_fixed_tree", "file_sha256"]
    with matrix.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in result["checks"])  # type: ignore[index]

    findings = result["findings"]
    report.write_text(
        "# PS7331 GhostLock upstream patch-chain audit\n\n"
        "Host-only source comparison. No POC, kernel build, futex call, waiter, race, device, memory operation, or root payload.\n\n"
        "## Result\n\n"
        f"- Primary `current` cleanup shape remains: **{findings['primary_fix_pre_fix_shape']}**\n"
        f"- Early-return wrapper pre-fix shape remains: **{findings['early_return_pre_fix_shape']}**\n"
        f"- Later unenqueued waiter guard present: **{findings['unenqueued_guard_present']}**\n"
        f"- Static proxy call/branch present: **{findings['proxy_path_static_present']}**\n\n"
        "## Classification\n\n"
        "**已證實（source scope）：** PS7331 retains the pre-fix signatures represented by the primary `current` cleanup and the wrapper's nonzero-return cleanup; the proxy call site and caller branch are present.\n\n"
        "**高可信推論：** the PS7331 source is semantically pre-fix relative to the cited upstream patch chain.\n\n"
        "**待驗證：** whether stock userspace can form the proxy state and whether any branch executes at runtime. Source-level pre-fix status is not a live exploit or root result.\n\n"
        "**因風險拒絕測試：** device-side trigger, paired waiter, race scheduling, panic, heap shaping, kernel memory access, and privilege escalation.\n\n"
        "The complete machine-readable check list and upstream commit URLs are in `patch-chain.json` and `patch-chain.csv`.\n",
        encoding="utf-8",
    )
    files = [summary, matrix, report]
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False,
                          "futex_triggered": False, "output": str(args.output)}, indent=2))
        return 0
    write_output(build(args.source_root), args.output)
    print(f"wrote host-only patch-chain audit: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
