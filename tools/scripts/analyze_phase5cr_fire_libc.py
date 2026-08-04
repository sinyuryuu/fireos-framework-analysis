#!/usr/bin/env python3
"""Summarize Fire libc futex helper call edges without executing the ELF.

This is a host-only analyzer.  It invokes host `nm`, `objdump`, and `strings`
against a pulled file, records symbol/call-edge names, and deliberately omits
raw instructions, syscall arguments, addresses derived from the kernel, race
timing, or payload generation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


TARGETS = {
    "wait_helper": "_Z15__futex_wait_exPVvbibPK8timespec",
    "pi_helper": "_Z18__futex_pi_lock_exPVvbbPK8timespec",
    "syscall": "syscall",
}

RELEVANT_SYMBOLS = {
    "pthread_cond_wait",
    "pthread_cond_timedwait",
    "pthread_cond_timedwait_monotonic_np",
    "pthread_mutex_lock",
    "_ZL16PIMutexTimedLockR7PIMutexbPK8timespec",
    TARGETS["wait_helper"],
    TARGETS["pi_helper"],
    TARGETS["syscall"],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_host(*args: str) -> str:
    result = subprocess.run(
        list(args), check=False, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"host command failed ({result.returncode}): {' '.join(args)}")
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--libc", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY-RUN: no ELF is read and no files are written.")
        print(f"LIBC\t{args.libc}")
        print(f"OUTPUT\t{args.output}")
        return 0
    if not args.libc.is_file():
        print("ERROR: --libc must be a regular file", file=sys.stderr)
        return 2
    if args.output.exists():
        print(f"ERROR: refusing to overwrite output: {args.output}", file=sys.stderr)
        return 2

    try:
        nm_text = run_host("nm", "-a", str(args.libc))
        objdump_text = run_host("objdump", "-d", str(args.libc))
        strings_text = run_host("strings", str(args.libc))
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    symbols: dict[str, str] = {}
    for line in nm_text.splitlines():
        match = re.match(r"^([0-9a-fA-F]+)\s+\S\s+(\S+)", line)
        if match and match.group(2) in RELEVANT_SYMBOLS:
            symbols[match.group(2)] = match.group(1)

    callers: dict[str, list[str]] = {key: [] for key in TARGETS.values()}
    current_function = ""
    function_header = re.compile(r"^[0-9a-fA-F]+\s+<([^>]+)>:")
    call_target = re.compile(r"\bbl\s+[^<]*<([^>]+)>")
    for line in objdump_text.splitlines():
        header = function_header.match(line.strip())
        if header:
            current_function = header.group(1)
            continue
        call = call_target.search(line)
        if call and call.group(1) in callers and current_function:
            if current_function not in callers[call.group(1)]:
                callers[call.group(1)].append(current_function)

    requeue_literals = [
        line.strip() for line in strings_text.splitlines()
        if "requeue_pi" in line.lower() or "wait_requeue" in line.lower()
    ]
    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "libc": {"path": str(args.libc), "sha256": sha256(args.libc)},
        "relevant_symbols": symbols,
        "helper_callers": callers,
        "requeue_pi_strings_observed": requeue_literals,
        "classification": {
            "ordinary_condition_variable_edge": any(
                name in callers[TARGETS["wait_helper"]]
                for name in ("pthread_cond_wait", "pthread_cond_timedwait",
                             "pthread_cond_timedwait_monotonic_np")
            ),
            "pi_lock_helper_edge": any(
                "PIMutexTimedLock" in name
                for name in callers[TARGETS["pi_helper"]]
            ),
            "requeue_pi_caller_established": bool(requeue_literals),
            "runtime_identity_observed": False,
        },
        "safety": {
            "elf_executed": False,
            "device_contacted": False,
            "syscall_invoked": False,
            "race_triggered": False,
            "address_or_payload_generated": False,
        },
    }

    args.output.mkdir(parents=True)
    (args.output / "analysis.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.output / "commands.txt").write_text(
        "python3 tools/scripts/analyze_phase5cr_fire_libc.py \\\n  --libc " + str(args.libc) + " \\\n  --output " + str(args.output) + "\n",
        encoding="utf-8",
    )
    (args.output / "result.md").write_text(
        "# Phase 5CR Fire libc analysis\n\n"
        "Host-only symbol/call-edge analysis; the ELF was not executed and no\n"
        "device, syscall, race, address or payload operation was performed.\n\n"
        f"ordinary_condition_variable_edge={result['classification']['ordinary_condition_variable_edge']}\n"
        f"pi_lock_helper_edge={result['classification']['pi_lock_helper_edge']}\n"
        f"requeue_pi_caller_established={result['classification']['requeue_pi_caller_established']}\n",
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
