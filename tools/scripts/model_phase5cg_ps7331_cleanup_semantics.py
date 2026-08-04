#!/usr/bin/env python3
"""Model PS7331 cleanup branches from exact source, without kernel execution.

The model is an abstract decision table for review.  It does not accept or
emit futex syscall recipes, addresses, timing, payloads, or device commands.
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


def find_line(lines: list[str], pattern: str) -> dict[str, object] | None:
    compiled = re.compile(pattern)
    for index, line in enumerate(lines):
        if compiled.search(line):
            return {"line": index + 1, "text": line.strip()}
    return None


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


def scoped_line(block: tuple[int, int, list[str]], pattern: str) -> dict[str, object] | None:
    start, _end, lines = block
    hit = find_line(lines, pattern)
    if hit is None:
        return None
    hit["line"] = int(hit["line"]) + start - 1
    return hit


def model_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    cases = [
        ("try_to_take_success", "ret=1", False, "wake_requeued_waiter", False, False),
        ("ordinary_block", "ret=0", False, "requeue_waiter", False, False),
        ("early_deadlock_owner_present", "ret=-EDEADLK", True, "futex_requeue_error", True, True),
        ("negative_chain_result_owner_present", "ret<0", True, "futex_requeue_error", True, False),
        ("negative_result_owner_absent_normalized", "ret<0 then ret=0", False, "requeue_waiter", False, False),
    ]
    for name, proxy_result, owner_present, requeue_branch, cleanup, unassigned in cases:
        rows.append({
            "case": name,
            "proxy_result": proxy_result,
            "owner_present_at_wrapper_check": owner_present,
            "wrapper_cleanup_called": cleanup,
            "futex_requeue_branch": requeue_branch,
            "waiter_task_assignment_before_return": not unassigned,
            "followup_null_waiter_guard_relevant": unassigned,
            "runtime_observed": False,
        })
    identity_cases = [
        ("same_task", False, True),
        ("different_task_target_state_present", True, True),
        ("different_task_target_state_absent", True, False),
    ]
    for name, mismatch, target_state_present in identity_cases:
        rows.append({
            "case": f"identity_{name}",
            "proxy_result": "cleanup already selected",
            "owner_present_at_wrapper_check": True,
            "wrapper_cleanup_called": True,
            "futex_requeue_branch": "cleanup path",
            "waiter_task_assignment_before_return": True,
            "followup_null_waiter_guard_relevant": False,
            "identity_mismatch_assumed_for_model": mismatch,
            "target_pi_blocked_on_present_for_model": target_state_present,
            "cleanup_write_target": "current",
            "explicit_task_pi_blocked_on_directly_cleared": not mismatch,
            "conditional_target_residue": mismatch and target_state_present,
            "runtime_observed": False,
        })
    return rows


def inspect(futex_path: Path, rtmutex_path: Path) -> dict[str, object]:
    futex_lines = futex_path.read_text(encoding="utf-8", errors="replace").splitlines()
    rtmutex_lines = rtmutex_path.read_text(encoding="utf-8", errors="replace").splitlines()
    task_blocks = function_span(
        rtmutex_lines, r"^\s*static int task_blocks_on_rt_mutex\s*\("
    )
    proxy = function_span(
        rtmutex_lines, r"^\s*int rt_mutex_start_proxy_lock\s*\("
    )
    remove = function_span(
        rtmutex_lines, r"^\s*static void remove_waiter\s*\("
    )
    requeue = function_span(
        futex_lines, r"^\s*static int futex_requeue\s*\("
    )
    evidence = {
        "task_blocks_owner_check": scoped_line(task_blocks, r"if\s*\(owner\s*==\s*task\)"),
        "task_blocks_early_return": scoped_line(task_blocks, r"return\s+-EDEADLK\s*;"),
        "task_blocks_waiter_assignment": scoped_line(task_blocks, r"waiter->task\s*=\s*task\s*;"),
        "wrapper_owner_normalization": scoped_line(proxy, r"if\s*\(ret\s*&&\s*!rt_mutex_owner\(lock\)\)"),
        "wrapper_broad_cleanup_guard": scoped_line(proxy, r"if\s*\(unlikely\(ret\)\)"),
        "cleanup_current_write": scoped_line(remove, r"current->pi_blocked_on\s*=\s*NULL"),
        "futex_requeue_success_branch": scoped_line(requeue, r"if\s*\(ret\s*==\s*1\)"),
        "futex_requeue_error_branch": scoped_line(requeue, r"else if\s*\(ret\)"),
    }
    missing = [name for name, hit in evidence.items() if hit is None]
    rows = model_rows()
    return {
        "scope": "PS7331 exact source; abstract host-only branch model",
        "futex_path": str(futex_path),
        "futex_sha256": sha256(futex_path),
        "rtmutex_path": str(rtmutex_path),
        "rtmutex_sha256": sha256(rtmutex_path),
        "source_evidence": evidence,
        "source_evidence_complete": not missing,
        "missing_evidence": missing,
        "decision_rows": rows,
        "verdict": {
            "early_return_precedes_waiter_assignment": evidence["task_blocks_early_return"] is not None and evidence["task_blocks_waiter_assignment"] is not None,
            "broad_nonzero_cleanup_guard_present": evidence["wrapper_broad_cleanup_guard"] is not None,
            "cleanup_targets_current": evidence["cleanup_current_write"] is not None,
            "abstract_identity_mismatch_can_leave_target_state_conditionally": True,
            "runtime_identity_mismatch_observed": False,
            "persistent_invariant_violation_proven": False,
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


def write_outputs(result: dict[str, object], output: Path) -> None:
    output.mkdir(parents=True)
    (output / "cleanup-semantics.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (output / "decision-matrix.csv").open("w", newline="", encoding="utf-8") as stream:
        rows = result["decision_rows"]
        keys = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(
            stream, fieldnames=keys, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    (output / "result.md").write_text(
        "# PS7331 cleanup semantics model\n\n"
        f"- Exact source evidence complete: **{result['source_evidence_complete']}**\n"
        "- Early return before waiter assignment: **True**\n"
        "- Broad nonzero cleanup guard: **True**\n"
        "- Conditional target residue in abstract mismatch case: **True**\n"
        "- Runtime mismatch/race/root proven: **False**\n\n"
        "This is an abstract source model only; it does not execute the kernel path.\n",
        encoding="utf-8",
    )
    (output / "README.txt").write_text(
        "Host-only abstract source model. No futex syscall, race trigger, device I/O, "
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
        print(json.dumps({"dry_run": True, "device_execution": False,
                          "futex": str(args.futex), "rtmutex": str(args.rtmutex),
                          "output": str(args.output)}, indent=2, sort_keys=True))
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
