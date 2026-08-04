#!/usr/bin/env python3
"""Host-only PS7331 proxy-waiter identity state model.

The model extracts source landmarks and records their ordering.  It does not
compile or execute the kernel, create futex arguments, schedule threads, or
emit a race/root payload.
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


def first_line(lines: list[str], pattern: str) -> int | None:
    regex = re.compile(pattern)
    for number, line in enumerate(lines, 1):
        if regex.search(line):
            return number
    return None


def first_line_after(lines: list[str], pattern: str, start: int) -> int | None:
    regex = re.compile(pattern)
    for number in range(start, len(lines)):
        if regex.search(lines[number]):
            return number + 1
    return None


def build(root: Path) -> dict:
    rtmutex = root / "kernel/locking/rtmutex.c"
    futex = root / "kernel/futex.c"
    common = root / "kernel/locking/rtmutex_common.h"
    paths = (rtmutex, futex, common)
    if any(not path.is_file() for path in paths):
        raise SystemExit("missing exact source input")
    rt_lines = rtmutex.read_text(encoding="utf-8", errors="replace").splitlines()
    fu_lines = futex.read_text(encoding="utf-8", errors="replace").splitlines()
    co_lines = common.read_text(encoding="utf-8", errors="replace").splitlines()
    early = first_line(rt_lines, r"if\s*\(owner\s*==\s*task\)")
    assignment = first_line(rt_lines, r"waiter->task\s*=\s*task")
    lock_assignment = first_line(rt_lines, r"waiter->lock\s*=\s*lock")
    task_blocked = first_line(rt_lines, r"task->pi_blocked_on\s*=\s*waiter")
    proxy_task = first_line(fu_lines, r"this->task\);")
    proxy_call = first_line(fu_lines, r"rt_mutex_start_proxy_lock\(")
    cleanup = first_line(rt_lines, r"current->pi_blocked_on\s*=\s*NULL")
    proxy_start = first_line(rt_lines, r"int rt_mutex_start_proxy_lock\(")
    wrapper = first_line_after(rt_lines, r"if\s*\(unlikely\(ret\)\)", (proxy_start or 1) - 1)
    waiter_local = first_line(fu_lines, r"struct rt_mutex_waiter\s+rt_waiter;")
    waiter_stack_doc = first_line(fu_lines, r"waiter is allocated on our stack")
    q_waiter = first_line(fu_lines, r"q\.rt_waiter\s*=\s*&rt_waiter")
    return {
        "schema": "phase6c-identity-state-model-v1",
        "scope": {"host_only": True, "device_execution": False,
                   "thread_creation": False, "race_trigger": False,
                   "memory_operation": False, "root_operation": False},
        "inputs": {str(path.relative_to(root)): sha256(path) for path in paths},
        "landmarks": {
            "early_deadlock_return": {"file": str(rtmutex), "line": early},
            "waiter_task_assignment": {"file": str(rtmutex), "line": assignment},
            "waiter_lock_assignment": {"file": str(rtmutex), "line": lock_assignment},
            "task_pi_blocked_on_assignment": {"file": str(rtmutex), "line": task_blocked},
            "proxy_call": {"file": str(futex), "line": proxy_call},
            "proxy_stored_task_argument": {"file": str(futex), "line": proxy_task},
            "current_cleanup": {"file": str(rtmutex), "line": cleanup},
            "broad_cleanup_gate": {"file": str(rtmutex), "line": wrapper},
            "local_waiter": {"file": str(futex), "line": waiter_local},
            "stack_waiter_documentation": {"file": str(futex), "line": waiter_stack_doc},
            "futex_queue_waiter": {"file": str(futex), "line": q_waiter},
        },
        "ordering": {
            "early_return_precedes_waiter_assignment": early is not None and assignment is not None and early < assignment,
            "waiter_identity_set_before_task_blocked_on": assignment is not None and task_blocked is not None and assignment < task_blocked,
            "proxy_passes_stored_task": proxy_call is not None and proxy_task is not None,
            "cleanup_uses_current": cleanup is not None,
            "proxy_cleanup_gate_is_broad_nonzero": wrapper is not None,
        },
        "interpretation": [
            "Source establishes a stored waiter/task dataflow and a separate current-task cleanup target.",
            "The model does not assert that the two identities differ at runtime.",
            "The model does not assert cleanup residue, memory corruption, crash, or privilege transition.",
        ],
    }


def write_output(output: Path, result: dict, command: str) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    (output / "commands.txt").write_text(command + "\n", encoding="utf-8")
    (output / "identity-model.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Phase 6C host-only identity state model", "",
        "No kernel/device execution, thread scheduling, race, memory operation, or root payload was used.", "",
        "## Source-order result", "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in result["ordering"].items())
    lines.extend([
        "", "## Evidence labels", "",
        "- **已證實：** source landmarks and ordering in the preserved PS7331 tree.",
        "- **高可信推論：** the inspected path preserves separate stored-task and current-task concepts.",
        "- **待驗證：** runtime identity mismatch and any persistent consequence.",
        "- **因風險拒絕測試：** stock-device requeue-PI, race, panic, memory operation, or root chain.",
    ])
    (output / "result.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = []
    for path in sorted(output.iterdir()):
        if path.name != "sha256sums.txt":
            manifest.append(f"{sha256(path)}  {path.name}")
    (output / "sha256sums.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "device_execution": False,
                          "source_root": str(args.source_root), "output": str(args.output)}, indent=2))
        return 0
    if not args.source_root.is_dir():
        parser.error("source root is missing")
    write_output(args.output, build(args.source_root), " ".join(__import__("sys").argv))
    print(f"wrote host-only identity model: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
