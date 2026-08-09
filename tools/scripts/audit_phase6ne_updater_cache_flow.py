#!/usr/bin/env python3
"""Host-only closure for the PS7331 updater cache-size decision flow.

The audit disassembles the already preserved official update-binary and uses
its GNU debugdata symbol table only for function boundaries and names.  It
records the CacheSizeCheck -> MakeFreeSpaceOnCache relation, the two callers'
return-value branches, and direct calls in the selected functions.

This script never executes update-binary, opens an OTA, contacts a device, or
writes a partition.  Existing output directories are never overwritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


FOCUS = ("CacheSizeCheck", "MakeFreeSpaceOnCache", "PerformBlockImageUpdate")
BL_RE = re.compile(r"^\s*([0-9a-f]+):\s+bl\s+0x([0-9a-f]+)")
CBZ_RE = re.compile(r"^\s*([0-9a-f]+):\s+cbz\s+w0,\s+0x([0-9a-f]+)")
TBNZ_SIGN_RE = re.compile(r"^\s*([0-9a-f]+):\s+tbnz\s+w0,\s+#0x1f,\s+0x([0-9a-f]+)")
HEADER_RE = re.compile(r"^===== ([^ ]+) .+ \[0x([0-9a-f]+), 0x([0-9a-f]+)\) =====$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_objdump(explicit: str | None) -> str:
    candidates = [explicit] if explicit else []
    candidates.extend((shutil.which("llvm-objdump"), "/opt/homebrew/opt/llvm/bin/llvm-objdump", "/usr/local/opt/llvm/bin/llvm-objdump"))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise SystemExit("llvm-objdump not found; pass --objdump")


def load_symbols(path: Path) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row.get("type") != "FUNC" or not row.get("name"):
                continue
            try:
                int(row["address"], 16)
                int(row["size"])
            except (KeyError, TypeError, ValueError):
                continue
            result[row["name"]] = row
    return result


def choose_symbols(symbols: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for label in FOCUS:
        candidates = [row for name, row in symbols.items() if name == label or label in name]
        candidates.sort(key=lambda row: (0 if row["name"] == label else 1, -int(row["size"]), row["name"]))
        if candidates:
            row = dict(candidates[0])
            row["focus_label"] = label
            selected.append(row)
    return selected


def disassemble(objdump: str, binary: Path, selected: list[dict[str, str]]) -> str:
    blocks: list[str] = []
    for row in selected:
        start = int(row["address"], 16)
        stop = start + int(row["size"])
        command = [objdump, "-d", "--no-show-raw-insn", f"--start-address=0x{start:x}", f"--stop-address=0x{stop:x}", str(binary)]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        blocks.append(f"===== {row['focus_label']} {row['name']} [0x{start:x}, 0x{stop:x}) =====\n{result.stdout}")
    return "\n".join(blocks) + "\n"


def parse_blocks(text: str) -> dict[str, list[str]]:
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        match = HEADER_RE.match(line)
        if match:
            current = match.group(1)
            blocks[current] = [line]
        elif current is not None:
            blocks[current].append(line)
    return blocks


def direct_edges(blocks: dict[str, list[str]], symbols_by_address: dict[int, dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for caller, lines in blocks.items():
        for line in lines:
            match = BL_RE.match(line)
            if not match:
                continue
            instruction = int(match.group(1), 16)
            target = int(match.group(2), 16)
            callee = symbols_by_address.get(target, {})
            rows.append({
                "caller": caller,
                "instruction": hex(instruction),
                "target": hex(target),
                "callee": callee.get("name", ""),
                "resolution": "symbol" if callee else "address-only",
            })
    return rows


def branch_rows(blocks: dict[str, list[str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for caller, lines in blocks.items():
        for line in lines:
            match = CBZ_RE.match(line)
            if match:
                meaning = "zero result takes the success/continuation branch at this call site"
                if caller == "PerformBlockImageUpdate" and int(match.group(1), 16) in {0x409CB8, 0x409CE0}:
                    meaning = "zero CacheSizeCheck result takes the continuation branch"
                rows.append({"function": caller, "instruction": hex(int(match.group(1), 16)), "branch": "cbz w0", "target": hex(int(match.group(2), 16)), "meaning": meaning})
                continue
            match = TBNZ_SIGN_RE.match(line)
            if match:
                meaning = "negative/sign-bit result takes the error branch"
                if caller == "CacheSizeCheck":
                    meaning += " in CacheSizeCheck"
                elif caller == "MakeFreeSpaceOnCache":
                    meaning += " in MakeFreeSpaceOnCache"
                rows.append({"function": caller, "instruction": hex(int(match.group(1), 16)), "branch": "tbnz w0,#0x1f", "target": hex(int(match.group(2), 16)), "meaning": meaning})
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--symbols", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--objdump")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"host_only": True, "device_contacted": False, "updater_executed": False, "partition_written": False, "focus": list(FOCUS), "output": str(args.output)}, indent=2))
        return 0
    if not args.binary.is_file() or not args.symbols.is_file():
        raise SystemExit("missing --binary or --symbols input")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    objdump = find_objdump(args.objdump)
    symbols = load_symbols(args.symbols)
    selected = choose_symbols(symbols)
    if set(row["focus_label"] for row in selected) != set(FOCUS):
        raise SystemExit("required symbols not found: " + ", ".join(FOCUS))
    by_address = {int(row["address"], 16): row for row in symbols.values()}
    disassembly = disassemble(objdump, args.binary, selected)
    blocks = parse_blocks(disassembly)
    edges = direct_edges(blocks, by_address)
    branches = branch_rows(blocks)
    args.output.mkdir(parents=True)
    (args.output / "focus-disassembly.txt").write_text(disassembly, encoding="utf-8")
    write_csv(args.output / "selected-functions.csv", selected, ["focus_label", "name", "address", "size", "binding", "section_index"])
    write_csv(args.output / "direct-call-edges.csv", edges, ["caller", "instruction", "target", "callee", "resolution"])
    write_csv(args.output / "return-branches.csv", branches, ["function", "instruction", "branch", "target", "meaning"])
    cache_to_make = [row for row in edges if row["caller"] == "CacheSizeCheck" and row["callee"] == "_Z20MakeFreeSpaceOnCachem"]
    perf_to_cache = [row for row in edges if row["caller"] == "PerformBlockImageUpdate" and row["callee"] == "_Z14CacheSizeCheckm"]
    cache_result_branch_instructions = {row["instruction"] for row in branches if row["function"] == "PerformBlockImageUpdate" and row["branch"] == "cbz w0"}
    summary = {
        "phase": "6NE",
        "analysis": "host-only updater CacheSizeCheck and MakeFreeSpaceOnCache flow closure",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "updater_executed": False,
        "recovery_executed": False,
        "partition_written": False,
        "inputs": {str(path): sha256(path) for path in (args.binary, args.symbols)},
        "objdump": objdump,
        "selected_functions": [row["focus_label"] for row in selected],
        "observations": {
            "perform_block_image_update_calls_cache_size_check": len(perf_to_cache) == 2,
            "cache_size_check_calls_make_free_space_on_cache": len(cache_to_make) == 1,
            "cache_size_check_tests_sign_bit": any(row["function"] == "CacheSizeCheck" and row["branch"] == "tbnz w0,#0x1f" for row in branches),
            "perform_block_image_update_branches_on_cache_result": {"0x409cb8", "0x409ce0"}.issubset(cache_result_branch_instructions),
        },
        "interpretation": [
            "The two direct calls and return branches establish a static decision-flow relation only.",
            "A zero CacheSizeCheck result takes the continuation path at both observed call sites; non-zero takes an error or fallback path selected by surrounding control flow.",
            "No runtime updater, OTA, malformed path, symlink, recovery, device, or partition operation was executed.",
        ],
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    graph = [
        "flowchart LR",
        "    Update[\"PerformBlockImageUpdate\"] -->|0x409cb4| Cache[\"CacheSizeCheck\"]",
        "    Update -->|0x409cdc| Cache",
        "    Cache -->|x0=size| Free[\"MakeFreeSpaceOnCache\"]",
        "    Cache -->|sign bit set| Error[\"error result\"]",
        "    Cache -->|w0=0| Continue[\"continuation path\"]",
        "    Free -.\"static helper only\".-> FS[\"cache/filesystem operations\"]",
    ]
    (args.output / "cache-decision-flow.mmd").write_text("\n".join(graph) + "\n", encoding="utf-8")
    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text("".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in files), encoding="utf-8")
    print(json.dumps(summary["observations"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
