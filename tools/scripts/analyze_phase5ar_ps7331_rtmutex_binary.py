#!/usr/bin/env python3
"""Host-only, address-sanitized PS7331 rtmutex pattern review.

The input is an ELF reconstructed from a kernel Image by a separately
reviewed kallsyms extractor.  This script only invokes nm/objdump to inspect
the file; it never contacts a device and never executes the ELF.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import re
import subprocess
from typing import Iterable


SYMBOLS = (
    "remove_waiter",
    "rt_mutex_start_proxy_lock",
    "rt_mutex_finish_proxy_lock",
    "futex_requeue",
)

NM_RE = re.compile(r"^\s*([0-9a-fA-F]+)\s+\S\s+(\S+)\s*$")
INSN_RE = re.compile(r"^\s*([0-9a-fA-F]+):\s+[0-9a-fA-F]+\s+(.+?)\s*$")
MRS_RE = re.compile(r"^mrs\s+(x\d+),\s*SP_EL0$")
STR_ZERO_RE = re.compile(r"^str\s+xzr,\s*\[(x\d+),\s*#0x[0-9a-fA-F]+\]$")


def run_capture(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return completed.stdout


def parse_symbols(nm_text: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for line in nm_text.splitlines():
        match = NM_RE.match(line)
        if match:
            result.setdefault(match.group(2), int(match.group(1), 16))
    return result


def parse_instructions(text: str) -> list[tuple[int, str]]:
    result = []
    for line in text.splitlines():
        match = INSN_RE.match(line)
        if match:
            result.append((int(match.group(1), 16), match.group(2).strip()))
    return result


def next_symbol_address(all_addresses: Iterable[int], start: int) -> int:
    later = [address for address in all_addresses if address > start]
    return min(later) if later else start + 0x1000


def disassemble(elf: pathlib.Path, start: int, stop: int) -> list[tuple[int, str]]:
    output = run_capture(
        [
            "/usr/bin/objdump",
            "-d",
            f"--start-address=0x{start:x}",
            f"--stop-address=0x{stop:x}",
            str(elf),
        ]
    )
    return parse_instructions(output)


def collect_patterns(symbol: str, instructions: list[tuple[int, str]]) -> list[dict[str, str]]:
    patterns: list[dict[str, str]] = []
    current_register: str | None = None
    for _, text in instructions:
        mrs = MRS_RE.match(text)
        if mrs:
            current_register = mrs.group(1)
            patterns.append(
                {
                    "symbol": symbol,
                    "pattern": "current_task_source",
                    "instruction": "mrs <reg>, SP_EL0",
                    "interpretation": "reads the architecture current-task source",
                }
            )
            continue
        store = STR_ZERO_RE.match(text)
        if store and current_register == store.group(1):
            patterns.append(
                {
                    "symbol": symbol,
                    "pattern": "current_task_blocked_on_clear",
                    "instruction": "str xzr, [current_task_reg, <field-immediate>]",
                    "interpretation": "clears a field through the task loaded from SP_EL0",
                }
            )
    if symbol == "rt_mutex_start_proxy_lock":
        if any("<remove_waiter>" in text for _, text in instructions):
            patterns.append(
                {
                    "symbol": symbol,
                    "pattern": "proxy_error_calls_remove_waiter",
                    "instruction": "bl remove_waiter",
                    "interpretation": "proxy-lock path contains a remove_waiter call",
                }
            )
    return patterns


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--source-old-sha256", default="")
    parser.add_argument("--source-fixed-sha256", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output in {pathlib.Path("/"), pathlib.Path("."), pathlib.Path("..")}:
        parser.error("refusing broad output path")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "elf": str(args.elf), "output": str(args.output)}, indent=2))
        return 0
    if not args.elf.is_file():
        parser.error(f"ELF is not a regular file: {args.elf}")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    nm_text = run_capture(["/usr/bin/nm", "-n", str(args.elf)])
    symbols = parse_symbols(nm_text)
    addresses = list(symbols.values())
    rows: list[dict[str, object]] = []
    patterns: list[dict[str, str]] = []
    for name in SYMBOLS:
        if name not in symbols:
            rows.append({"symbol": name, "present": False, "pattern_count": 0})
            continue
        instructions = disassemble(args.elf, symbols[name], next_symbol_address(addresses, symbols[name]))
        found = collect_patterns(name, instructions)
        patterns.extend(found)
        rows.append({"symbol": name, "present": True, "pattern_count": len(found)})

    args.output.mkdir(parents=True)
    with (args.output / "symbol-presence.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["symbol", "present", "pattern_count"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with (args.output / "instruction-patterns.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["symbol", "pattern", "instruction", "interpretation"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(patterns)
    summary = {
        "input_elf_sha256": hashlib.sha256(args.elf.read_bytes()).hexdigest(),
        "source_old_sha256": args.source_old_sha256,
        "source_fixed_sha256": args.source_fixed_sha256,
        "symbols_requested": list(SYMBOLS),
        "symbols_present": [row["symbol"] for row in rows if row["present"]],
        "patterns": patterns,
        "address_output": "intentionally omitted",
        "device_execution": False,
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = [args.output / "instruction-patterns.csv", args.output / "summary.json", args.output / "symbol-presence.csv"]
    (args.output / "sha256sums.txt").write_text(
        "\n".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
