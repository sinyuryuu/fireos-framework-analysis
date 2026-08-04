#!/usr/bin/env python3
"""Host-only inventory of PS7331 futex requeue-PI selftest roles.

The analyzer reads source and build files only.  It never compiles, runs, or
installs a selftest and never invokes ADB.  It reports the concurrency and API
roles present in the upstream-style functional tests so they are not confused
with a single-thread syscall switch probe.
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


def lines_with(text: str, pattern: str) -> list[int]:
    regex = re.compile(pattern)
    return [number for number, line in enumerate(text.splitlines(), 1) if regex.search(line)]


def facts(path: Path, label: str) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "label": label,
        "file": str(path),
        "sha256": sha256(path),
        "lines": len(text.splitlines()),
        "includes_pthread": bool(re.search(r"#include\s*<pthread\.h>", text)),
        "pthread_create_count": len(re.findall(r"\bpthread_create\s*\(", text)),
        "pthread_join_count": len(re.findall(r"\bpthread_join\s*\(", text)),
        "pthread_kill_count": len(re.findall(r"\bpthread_kill\s*\(", text)),
        "creates_rt_thread": bool(re.search(r"\bcreate_rt_thread\s*\(", text)),
        "futex_wait_requeue_pi_count": len(re.findall(r"\bfutex_wait_requeue_pi\s*\(", text)),
        "futex_cmp_requeue_pi_count": len(re.findall(r"\bfutex_cmp_requeue_pi\s*\(", text)),
        "futex_lock_pi_count": len(re.findall(r"\bfutex_lock_pi\s*\(", text)),
        "futex_unlock_pi_count": len(re.findall(r"\bfutex_unlock_pi\s*\(", text)),
        "futex_wake_count": len(re.findall(r"\bfutex_wake\s*\(", text)),
        "private_futex_flag": "FUTEX_PRIVATE_FLAG" in text,
        "role_function_lines": {
            name: lines_with(text, rf"\b(?:void\s*\*|int)\s*{name}\s*\(")
            for name in ("waiterfn", "broadcast_wakerfn", "signal_wakerfn", "third_party_blocker", "blocking_child")
        },
        "requeue_lines": lines_with(text, r"FUTEX_CMP_REQUEUE_PI|futex_cmp_requeue_pi"),
    }


def write_output(output: Path, inputs: list[dict], command: str) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    (output / "commands.txt").write_text(command + "\n", encoding="utf-8")
    result = {
        "schema": "phase6b-requeue-selftest-inventory-v1",
        "scope": {"host_only": True, "compiled": False, "executed": False,
                  "installed": False, "adb": False, "device_mutation": False},
        "inputs": inputs,
        "interpretation": {
            "single_thread_probe_equivalent": False,
            "reason": "All requeue-PI functional tests use waiter/waker roles, pthread, or signal coordination.",
        },
    }
    (output / "inventory.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = [
        "label", "file", "sha256", "lines", "includes_pthread", "pthread_create_count",
        "pthread_join_count", "pthread_kill_count", "creates_rt_thread",
        "futex_wait_requeue_pi_count", "futex_cmp_requeue_pi_count", "futex_lock_pi_count",
        "futex_unlock_pi_count", "futex_wake_count", "private_futex_flag", "requeue_lines",
    ]
    with (output / "inventory.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in inputs:
            flattened = dict(row)
            flattened["requeue_lines"] = ";".join(str(value) for value in row["requeue_lines"])
            flattened.pop("role_function_lines", None)
            writer.writerow(flattened)
    rows = [
        "# Phase 6B host-only requeue-PI selftest role analysis",
        "",
        "This artifact inventories source/build inputs only. No selftest was",
        "compiled, executed, installed, or sent to a device.",
        "",
        "## Findings",
        "",
        "- `futex_requeue_pi.c` contains waiter, broadcast-waker, signal-waker and",
        "  optional third-party blocker roles; it uses pthread creation/join and",
        "  both WAIT_REQUEUE_PI and CMP_REQUEUE_PI operations.",
        "- `futex_requeue_pi_mismatched_ops.c` creates a blocking child before the",
        "  CMP_REQUEUE_PI call, then joins and wakes it.",
        "- `futex_requeue_pi_signal_restart.c` creates a real-time waiter, uses",
        "  signals and joins it around the requeue operation.",
        "- The functional Makefile links with `-pthread`; the run script executes",
        "  multiple requeue-PI scenarios, not a single switch check.",
        "",
        "## Evidence labels",
        "",
        "- **已證實：** preserved PS7331 source contains the listed roles and API markers.",
        "- **高可信推論：** a single-thread, single-call harness cannot reproduce the",
        "  selftest's proxy-waiter setup or serve as equivalent GhostLock runtime evidence.",
        "- **待驗證：** whether any shipped Fire userspace component creates the same",
        "  role pairing at runtime.",
        "- **因風險拒絕測試：** building/running these tests on the stock tablet or",
        "  adapting them into a race/root trigger.",
        "",
        "## Input hashes",
        "",
    ]
    rows.extend(f"- `{row['label']}`: `{row['sha256']}`" for row in inputs)
    (output / "result.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
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
    base = args.source_root / "tools/testing/selftests/futex"
    paths = [
        (base / "functional/futex_requeue_pi.c", "futex_requeue_pi"),
        (base / "functional/futex_requeue_pi_mismatched_ops.c", "futex_requeue_pi_mismatched_ops"),
        (base / "functional/futex_requeue_pi_signal_restart.c", "futex_requeue_pi_signal_restart"),
        (base / "functional/Makefile", "functional_Makefile"),
        (base / "functional/run.sh", "functional_run_sh"),
        (base / "Makefile", "futex_Makefile"),
    ]
    if args.dry_run:
        print(json.dumps({"dry_run": True, "device_execution": False,
                          "inputs": [str(path) for path, _ in paths],
                          "output": str(args.output)}, indent=2))
        return 0
    missing = [str(path) for path, _ in paths if not path.is_file()]
    if missing:
        parser.error("missing input: " + ", ".join(missing))
    rows = [facts(path, label) for path, label in paths]
    write_output(args.output, rows, " ".join(__import__("sys").argv))
    print(f"wrote host-only selftest inventory: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
