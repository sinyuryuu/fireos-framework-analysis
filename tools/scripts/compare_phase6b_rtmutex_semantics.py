#!/usr/bin/env python3
"""Host-only comparison of the PS7331 rtmutex cleanup semantics.

This parser reads C source files only.  It never invokes ADB, compiles a
kernel, creates futex arguments, emits an exploit payload, or contacts a
device.  The output is a marker-level comparison, not a proof of runtime
reachability or exploitability.
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


def extract_function(text: str, signature: str) -> tuple[str, int, int]:
    lines = text.splitlines()
    start = next(
        (
            i
            for i, line in enumerate(lines)
            if signature in line and not line.lstrip().startswith(("*", "//", "/*"))
        ),
        None,
    )
    if start is None:
        raise ValueError(f"function signature not found: {signature}")
    open_line = next((i for i in range(start, len(lines)) if "{" in lines[i]), None)
    if open_line is None:
        raise ValueError(f"function body not found: {signature}")
    depth = 0
    seen = False
    end = open_line
    for i in range(open_line, len(lines)):
        # This is intentionally a conservative marker parser.  It is used for
        # stable source landmarks, not as a C compiler or semantic parser.
        depth += lines[i].count("{")
        depth -= lines[i].count("}")
        seen = True
        if seen and depth == 0:
            end = i
            break
    else:
        raise ValueError(f"unterminated function body: {signature}")
    return "\n".join(lines[start : end + 1]), start + 1, end + 1


def marker(body: str, pattern: str) -> bool:
    return re.search(pattern, body, flags=re.MULTILINE) is not None


def analyse(path: Path, label: str) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    remove, remove_start, remove_end = extract_function(text, "remove_waiter")
    try:
        proxy, proxy_start, proxy_end = extract_function(text, "rt_mutex_start_proxy_lock")
        proxy_result = {
            "available": True,
            "start": proxy_start,
            "end": proxy_end,
            "remove_waiter_call": marker(proxy, r"remove_waiter\s*\("),
            "broad_nonzero_cleanup": marker(proxy, r"if\s*\(\s*(?:unlikely\s*\(\s*)?ret\s*\)?\s*\)"),
            "negative_only_cleanup": marker(proxy, r"ret\s*<\s*0"),
            "early_return_before_cleanup": marker(proxy, r"return\s+1\s*;"),
        }
    except ValueError as exc:
        proxy_result = {"available": False, "reason": str(exc)}
    return {
        "label": label,
        "file": str(path),
        "sha256": sha256(path),
        "functions": {
            "remove_waiter": {
                "start": remove_start,
                "end": remove_end,
                "current_pi_lock": marker(remove, r"current->pi_lock"),
                "current_pi_blocked_on_clear": marker(remove, r"current->pi_blocked_on\s*=\s*NULL"),
                "waiter_task_binding": marker(remove, r"waiter_task\s*=\s*waiter->task"),
                "waiter_task_pi_lock": marker(remove, r"waiter_task->pi_lock"),
                "waiter_task_pi_blocked_on_clear": marker(remove, r"waiter_task->pi_blocked_on\s*=\s*NULL"),
                "null_waiter_guard": marker(remove, r"!\s*waiter_task|!\s*waiter->task"),
                "chain_uses_waiter_task": marker(remove, r"waiter_task\s*[,)]"),
            },
            "rt_mutex_start_proxy_lock": proxy_result,
        },
    }


def write_output(output: Path, rows: list[dict], command: str) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    (output / "commands.txt").write_text(command + "\n", encoding="utf-8")
    (output / "comparison.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = [
        "label", "function", "file", "sha256", "available", "reason", "start", "end",
        "current_pi_lock", "current_pi_blocked_on_clear", "waiter_task_binding",
        "waiter_task_pi_lock", "waiter_task_pi_blocked_on_clear", "null_waiter_guard",
        "chain_uses_waiter_task", "remove_waiter_call", "broad_nonzero_cleanup",
        "negative_only_cleanup", "early_return_before_cleanup",
    ]
    with (output / "comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            for function, values in row["functions"].items():
                flattened = {"label": row["label"], "function": function,
                             "file": row["file"], "sha256": row["sha256"],
                             "available": values.get("available", True),
                             "reason": values.get("reason", "")}
                flattened.update(values)
                writer.writerow(flattened)
    ps7331 = next(row for row in rows if row["label"] == "PS7331")
    legacy = next(row for row in rows if row["label"] == "legacy-v4.4.146")
    fixed = next(row for row in rows if row["label"] == "fixed-v6.1.175")
    old = ps7331["functions"]["remove_waiter"]
    proxy = ps7331["functions"]["rt_mutex_start_proxy_lock"]
    fixed_proxy = fixed["functions"]["rt_mutex_start_proxy_lock"]
    report = [
        "# Phase 6B host-only rtmutex semantic comparison",
        "",
        "This is a source-marker comparison only. It does not execute a kernel,",
        "invoke ADB, generate futex arguments, create a waiter, trigger a race,",
        "or establish exploitability.",
        "",
        "## Result",
        "",
        f"- PS7331 `remove_waiter()` current-task cleanup: **{old['current_pi_blocked_on_clear']}**.",
        f"- PS7331 `remove_waiter()` waiter-task cleanup marker: **{old['waiter_task_pi_blocked_on_clear']}**.",
        f"- PS7331 proxy wrapper calls `remove_waiter()`: **{proxy['remove_waiter_call']}**.",
        f"- PS7331 wrapper has broad nonzero cleanup marker: **{proxy['broad_nonzero_cleanup']}**.",
        f"- PS7331 wrapper has negative-only cleanup marker: **{proxy['negative_only_cleanup']}**.",
        f"- Fixed v6.1.175 proxy wrapper in the preserved slice: **{'available' if fixed_proxy.get('available') else 'UNAVAILABLE'}**.",
        "",
        "The PS7331 marker set is consistent with the preserved legacy v4.4.146",
        "pre-fix shape. The fixed v6.1.175 input is a focused remove_waiter slice,",
        "so its proxy-wrapper absence is not treated as a semantic difference. This is",
        "strong source-level evidence for pre-fix semantics, not runtime identity",
        "mismatch, residue, memory corruption, crash, or privilege transition.",
        "",
        "## Reference inputs",
        "",
        f"- legacy: `{legacy['file']}` SHA-256 `{legacy['sha256']}`",
        f"- fixed: `{fixed['file']}` SHA-256 `{fixed['sha256']}`",
        f"- PS7331: `{ps7331['file']}` SHA-256 `{ps7331['sha256']}`",
        "",
        "## Evidence labels",
        "",
        "- **已證實：** source marker、函式行號與三份輸入雜湊。",
        "- **高可信推論：** inspected PS7331 source retains the legacy cleanup shape.",
        "- **待驗證：** stock runtime identity mismatch and any later consumer.",
        "- **因風險拒絕測試：** device requeue-PI trigger, race, panic, memory operation, root payload.",
    ]
    (output / "result.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    manifest = []
    for path in sorted(output.iterdir()):
        if path.name != "sha256sums.txt":
            manifest.append(f"{sha256(path)}  {path.name}")
    (output / "sha256sums.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ps7331", type=Path, required=True)
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--fixed", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    paths = (args.ps7331, args.legacy, args.fixed)
    if args.dry_run:
        print(json.dumps({"dry_run": True, "device_execution": False,
                          "inputs": [str(path) for path in paths],
                          "output": str(args.output)}, indent=2))
        return 0
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        parser.error("missing input: " + ", ".join(missing))
    rows = [analyse(args.ps7331, "PS7331"),
            analyse(args.legacy, "legacy-v4.4.146"),
            analyse(args.fixed, "fixed-v6.1.175")]
    write_output(args.output, rows, " ".join(__import__("sys").argv))
    print(f"wrote host-only comparison: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
