#!/usr/bin/env python3
"""Map the public GhostLock follow-up fix shape onto PS7331 4.4 source.

Host-only source review.  This script does not compile, execute, trigger
futexes, derive addresses, produce a payload, or contact a device.
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


def function_block(lines: list[str], signature: str) -> tuple[int, int, list[str]]:
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


def occurrences(lines: list[str], needles: tuple[str, ...], offset: int) -> list[dict[str, object]]:
    return [
        {"line": i + offset, "text": line.strip()}
        for i, line in enumerate(lines)
        if any(needle in line for needle in needles)
    ]


def inspect(rtmutex_path: Path, futex_path: Path) -> dict:
    rt_lines = rtmutex_path.read_text(encoding="utf-8", errors="replace").splitlines()
    futex_lines = futex_path.read_text(encoding="utf-8", errors="replace").splitlines()
    rm_start, rm_end, rm = function_block(
        rt_lines, r"^\s*static\s+void\s+remove_waiter\s*\("
    )
    proxy_start, proxy_end, proxy = function_block(
        rt_lines, r"^\s*int\s+rt_mutex_start_proxy_lock\s*\("
    )
    task_start, task_end, task = function_block(
        rt_lines, r"^\s*static\s+int\s+task_blocks_on_rt_mutex\s*\("
    )

    assignment = occurrences(task, ("waiter->task = task",), task_start)
    early_return = [
        {"line": i + task_start, "text": line.strip()}
        for i, line in enumerate(task)
        if re.match(r"^\s*return\s+-EDEAD(?:LK|LOCK)\s*;", line)
    ]
    assignment_line = assignment[0]["line"] if assignment else None
    early_before_assignment = [
        item for item in early_return
        if assignment_line is None or item["line"] < assignment_line
    ]

    current_cleanup = occurrences(rm, ("current->pi_blocked_on",), rm_start)
    waiter_task_refs = occurrences(rm, ("waiter->task", "waiter_task"), rm_start)
    null_guard = occurrences(rm, ("if (!waiter_task)", "if (!waiter->task)"), rm_start)
    broad_wrapper_guard = occurrences(proxy, ("if (unlikely(ret))",), proxy_start)
    negative_wrapper_guard = occurrences(proxy, ("if (unlikely(ret < 0))",), proxy_start)
    proxy_calls = occurrences(proxy, ("remove_waiter(lock, waiter)",), proxy_start)
    futex_proxy_calls = occurrences(futex_lines, ("rt_mutex_start_proxy_lock(",), 1)
    futex_requeue_pi = occurrences(
        futex_lines,
        ("FUTEX_WAIT_REQUEUE_PI", "FUTEX_CMP_REQUEUE_PI"),
        1,
    )

    return {
        "scope": "PS7331 exact 4.4 source; host-only semantic mapping",
        "rtmutex_path": str(rtmutex_path),
        "rtmutex_sha256": sha256(rtmutex_path),
        "futex_path": str(futex_path),
        "futex_sha256": sha256(futex_path),
        "remove_waiter": {
            "span": [rm_start, rm_end],
            "current_cleanup": current_cleanup,
            "waiter_task_references": waiter_task_refs,
            "followup_null_guard": null_guard,
        },
        "task_blocks_on_rt_mutex": {
            "span": [task_start, task_end],
            "waiter_assignment": assignment,
            "early_deadlock_returns": early_return,
            "early_deadlock_before_assignment": early_before_assignment,
        },
        "rt_mutex_start_proxy_lock": {
            "span": [proxy_start, proxy_end],
            "broad_return_guard": broad_wrapper_guard,
            "negative_return_guard": negative_wrapper_guard,
            "remove_waiter_calls": proxy_calls,
        },
        "futex_requeue_path": {
            "proxy_calls": futex_proxy_calls,
            "pi_operations": futex_requeue_pi,
        },
        "upstream_followup_patch_shape": {
            "remove_waiter_null_waiter_task_guard": True,
            "wrapper_negative_return_check": True,
            "source": "https://patchew.org/linux/20260507112913.1019537-1-dave%40stgolabs.net/",
        },
        "primary_fix_present": bool(waiter_task_refs) and not bool(current_cleanup),
        "followup_guard_present": bool(null_guard) and bool(negative_wrapper_guard),
        "runtime_exploitability_proven": False,
        "root_or_privilege_gain_proven": False,
        "device_execution": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtmutex", type=Path, required=True)
    parser.add_argument("--futex", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output in {Path("/"), Path("."), Path("..")}:
        parser.error("refusing broad output path")
        parser.error("refusing broad output path")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "device_execution": False,
                          "rtmutex": str(args.rtmutex), "futex": str(args.futex),
                          "output": str(args.output)}, indent=2, sort_keys=True))
        return 0
    for path, label in ((args.rtmutex, "rtmutex source"), (args.futex, "futex source")):
        if not path.is_file():
            parser.error(f"{label} is not a regular file: {path}")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    result = inspect(args.rtmutex, args.futex)
    result["classification"] = (
        "PS7331_REQUIRES_PRIMARY_FIX_AND_FOLLOWUP_GUARD_REVIEW"
        if not result["primary_fix_present"] and not result["followup_guard_present"]
        else "SOURCE_REVIEW_REQUIRED"
    )
    args.output.mkdir(parents=True)
    (args.output / "followup-mapping.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "result.md").write_text(
        "# PS7331 follow-up patch mapping\n\n"
        f"- Classification: **{result['classification']}**\n"
        f"- Primary fix present in source: **{result['primary_fix_present']}**\n"
        f"- Follow-up guard shape present: **{result['followup_guard_present']}**\n"
        "- Runtime exploitability proven: **False**\n"
        "- Root/privilege gain proven: **False**\n\n"
        "The public follow-up patch shape is used only as a source-level mapping. "
        "No patch is applied to an image and no device code is executed.\n",
        encoding="utf-8",
    )
    (args.output / "README.txt").write_text(
        "Host-only Phase 5CA artifact. No compilation, device I/O, futex trigger, "
        "address extraction, payload generation, or image mutation.\n",
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
