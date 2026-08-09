#!/usr/bin/env python3
"""Host-only closure for the PS7331 native updater block-image path.

This audit expands the previously selected updater disassembly to include the
block-image registration routine and the cache-space helper.  It correlates
symbol-guided AArch64 direct calls with ELF data cells and literal strings.
The updater is never executed, an OTA is never opened, and no device or
partition is contacted.  Existing output directories are never overwritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REGISTER_TARGET = 0x41D528
DATA_BASE = 0x5AF000

FOCUS = (
    "RegisterBlockImageFunction",
    "MakeFreeSpaceOnCache",
    "BlockImageVerifyFn",
    "BlockImageUpdateFn",
    "BlockImageRecoverFn",
    "PerformBlockImageUpdate",
    "LoadSrcTgtVersion3",
    "VerifyBlocks",
    "WriteToPartition",
    "WipeBlockDeviceFn",
    "readlink",
    "__readlink_chk",
    "readlinkat",
)

HEADER_RE = re.compile(r"^===== ([^ ]+) .+ \[0x([0-9a-f]+), 0x([0-9a-f]+)\) =====$")
BL_RE = re.compile(r"^\s*([0-9a-f]+):\s+bl\s+0x([0-9a-f]+)")
ADRP_RE = re.compile(r"adrp\s+x(\d+),\s+0x([0-9a-f]+)")
ADD_RE = re.compile(r"add\s+x(\d+),\s+x(\d+),\s+#0x([0-9a-f]+)")
LDR_CELL_RE = re.compile(r"ldr\s+x1,\s+\[x1,\s+#0x([0-9a-f]+)\]")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ElfReader:
    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        self.segments = self._load_segments()

    def _load_segments(self) -> list[tuple[int, int, int]]:
        header = self.data[:64]
        if header[:4] != b"\x7fELF" or header[4] != 2 or header[5] != 1:
            raise ValueError(f"expected little-endian ELF64: {self.path}")
        phoff = struct.unpack_from("<Q", header, 32)[0]
        phentsize = struct.unpack_from("<H", header, 54)[0]
        phnum = struct.unpack_from("<H", header, 56)[0]
        segments: list[tuple[int, int, int]] = []
        for index in range(phnum):
            entry = self.data[phoff + index * phentsize : phoff + (index + 1) * phentsize]
            p_type, _flags, offset, vaddr, _paddr, filesz, _memsz, _align = struct.unpack_from(
                "<IIQQQQQQ", entry, 0
            )
            if p_type == 1 and filesz:
                segments.append((vaddr, offset, filesz))
        return segments

    def read(self, address: int, size: int) -> bytes | None:
        for vaddr, offset, filesz in self.segments:
            if vaddr <= address < vaddr + filesz:
                file_offset = offset + address - vaddr
                if file_offset + size <= len(self.data):
                    return self.data[file_offset : file_offset + size]
        return None

    def read_u64(self, address: int) -> int | None:
        raw = self.read(address, 8)
        return struct.unpack("<Q", raw)[0] if raw is not None else None

    def read_ascii(self, address: int) -> str | None:
        raw = self.read(address, 128)
        if raw is None:
            return None
        value = raw.split(b"\x00", 1)[0]
        if not value or any(byte < 0x20 or byte > 0x7e for byte in value):
            return None
        return value.decode("ascii")


def parse_symbols(path: Path) -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row.get("type") != "FUNC" or not row.get("name"):
                continue
            try:
                result[int(row["address"], 16)] = row
            except (KeyError, TypeError, ValueError):
                continue
    return result


def choose_functions(symbols: dict[int, dict[str, str]]) -> list[dict[str, str]]:
    chosen: list[dict[str, str]] = []
    for label in FOCUS:
        candidates = [
            row for row in symbols.values()
            if label == row.get("name") or label in row.get("name", "")
        ]
        candidates.sort(key=lambda row: (
            0 if row.get("name") == label else 1,
            0 if row.get("name", "").startswith("_Z") else 1,
            -int(row.get("size", "0")),
            row.get("name", ""),
        ))
        if candidates:
            row = dict(candidates[0])
            row["focus_label"] = label
            chosen.append(row)
    return chosen


def find_objdump(explicit: str | None) -> str:
    candidates = [explicit] if explicit else []
    candidates.extend([
        shutil.which("llvm-objdump"),
        "/opt/homebrew/opt/llvm/bin/llvm-objdump",
        "/usr/local/opt/llvm/bin/llvm-objdump",
    ])
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise SystemExit("llvm-objdump not found; pass --objdump")


def disassemble(objdump: str, binary: Path, selected: list[dict[str, str]]) -> tuple[str, list[list[str]]]:
    blocks: list[str] = []
    commands: list[list[str]] = []
    for row in selected:
        start = int(row["address"], 16)
        stop = start + int(row["size"])
        command = [
            objdump,
            "-d",
            "--no-show-raw-insn",
            f"--start-address=0x{start:x}",
            f"--stop-address=0x{stop:x}",
            str(binary),
        ]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        blocks.append(
            f"===== {row['focus_label']} {row['name']} "
            f"[0x{start:x}, 0x{stop:x}) =====\n{result.stdout}"
        )
        commands.append(command)
    return "\n".join(blocks) + "\n", commands


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


def direct_edges(blocks: dict[str, list[str]], symbols: dict[int, dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for label, lines in blocks.items():
        for line in lines:
            match = BL_RE.match(line)
            if not match:
                continue
            address = int(match.group(1), 16)
            target = int(match.group(2), 16)
            target_row = symbols.get(target)
            rows.append({
                "caller_label": label,
                "instruction": hex(address),
                "target_address": hex(target),
                "callee_symbol": target_row.get("name", "") if target_row else "",
                "callee_resolution": "symbol" if target_row else "address-only",
            })
    return rows


def registration_rows(lines: list[str], elf: ElfReader, symbols: dict[int, dict[str, str]]) -> list[dict[str, str]]:
    calls = [
        (index, int(match.group(1), 16))
        for index, line in enumerate(lines)
        if (match := BL_RE.match(line)) and int(match.group(2), 16) == REGISTER_TARGET
    ]
    rows: list[dict[str, str]] = []
    for number, (index, instruction) in enumerate(calls, 1):
        start = calls[number - 2][0] + 1 if number > 1 else 0
        block = lines[start : index + 1]
        addresses: dict[str, int] = {}
        for line in block:
            if match := ADRP_RE.search(line):
                addresses[f"x{match.group(1)}"] = int(match.group(2), 16)
            elif match := ADD_RE.search(line):
                dst, src, addend = f"x{match.group(1)}", f"x{match.group(2)}", int(match.group(3), 16)
                if dst == src and src in addresses:
                    addresses[dst] += addend
        string_candidates = []
        for address in addresses.values():
            value = elf.read_ascii(address)
            if value and (value.startswith("block_image") or value.startswith("check_") or value.startswith("range_") or value.startswith("missing")):
                string_candidates.append((address, value))
        pointer_cell = None
        for line in block:
            if match := LDR_CELL_RE.search(line):
                pointer_cell = DATA_BASE + int(match.group(1), 16)
        pointer_value = elf.read_u64(pointer_cell) if pointer_cell is not None else None
        symbol = symbols.get(pointer_value or 0, {})
        rows.append({
            "registration_index": str(number),
            "register_call_instruction": hex(instruction),
            "command_name": string_candidates[0][1] if string_candidates else "",
            "command_string_address": hex(string_candidates[0][0]) if string_candidates else "",
            "function_pointer_cell": hex(pointer_cell) if pointer_cell is not None else "",
            "function_pointer_value": hex(pointer_value) if pointer_value is not None else "",
            "function_pointer_symbol": symbol.get("name", ""),
            "function_pointer_resolution": "symbol" if symbol else ("data-cell" if pointer_value is not None else "unresolved"),
            "evidence": f"RegisterBlockImageFunction:{hex(instruction)}",
        })
    return rows


def canonicalization_rows(edges: list[dict[str, str]]) -> list[dict[str, str]]:
    marker_rows = []
    for row in edges:
        callee = f"{row.get('callee_symbol', '')} {row.get('target_address', '')}".lower()
        if any(marker in callee for marker in ("readlink", "realpath", "canonical")):
            marker_rows.append({
                "marker": "readlink/canonicalization",
                "caller_label": row["caller_label"],
                "instruction": row["instruction"],
                "target_address": row["target_address"],
                "callee_symbol": row["callee_symbol"],
                "classification": "direct-edge-observed",
                "interpretation": "direct host-side call edge; no runtime behavior inferred",
            })
    return marker_rows


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = sorted({key for row in rows for key in row}) if rows else ["empty"]
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
        print(json.dumps({
            "dry_run": True,
            "host_only": True,
            "device_contacted": False,
            "updater_executed": False,
            "partition_written": False,
            "focus": list(FOCUS),
            "output": str(args.output),
        }, indent=2))
        return 0
    for path in (args.binary, args.symbols):
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    objdump = find_objdump(args.objdump)
    elf = ElfReader(args.binary)
    symbols = parse_symbols(args.symbols)
    selected = choose_functions(symbols)
    if not selected:
        raise SystemExit("no focus symbols selected")
    disassembly, commands = disassemble(objdump, args.binary, selected)
    blocks = parse_blocks(disassembly)
    edges = direct_edges(blocks, symbols)
    registrations = registration_rows(blocks.get("RegisterBlockImageFunction", []), elf, symbols)
    canonical = canonicalization_rows(edges)

    args.output.mkdir(parents=True)
    (args.output / "focus-disassembly.txt").write_text(disassembly, encoding="utf-8")
    write_csv(args.output / "selected-functions.csv", selected, ["focus_label", "name", "address", "size", "binding", "section_index"])
    write_csv(args.output / "selected-call-edges.csv", edges)
    write_csv(args.output / "block-image-registration.csv", registrations)
    write_csv(args.output / "canonicalization-call-sites.csv", canonical)
    summary = {
        "phase": "6MM",
        "analysis": "host-only updater block-image registration and cache canonicalization closure",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "updater_executed": False,
        "recovery_executed": False,
        "partition_written": False,
        "inputs": {str(path): sha256(path) for path in (args.binary, args.symbols)},
        "objdump": objdump,
        "selected_function_count": len(selected),
        "selected_functions": [row["focus_label"] for row in selected],
        "direct_edge_count": len(edges),
        "block_image_registration_count": len(registrations),
        "block_image_registration_names": [row["command_name"] for row in registrations],
        "block_image_pointer_symbol_resolution_count": sum(row["function_pointer_resolution"] == "symbol" for row in registrations),
        "canonicalization_call_site_count": len(canonical),
        "observations": {
            "register_block_image_calls_common_register_function": any(row["target_address"] == hex(REGISTER_TARGET) for row in edges if row["caller_label"] == "RegisterBlockImageFunction"),
            "block_image_names_recovered": bool(registrations) and all(row["command_name"] for row in registrations),
            "block_image_pointers_resolved_to_symbols": bool(registrations) and all(row["function_pointer_resolution"] == "symbol" for row in registrations),
            "make_free_space_directly_calls_readlink_family": any(row["caller_label"] == "MakeFreeSpaceOnCache" and "readlink" in row["callee_symbol"].lower() for row in edges),
            "canonicalization_direct_edge_to_extraction_or_partition_write": any(
                "readlink" in row["callee_symbol"].lower() and row["caller_label"] in {"PackageExtractFileFn", "PerformBlockImageUpdate", "BlockImageUpdateFn", "WriteToPartition"}
                for row in edges
            ),
        },
        "bounded_interpretation": [
            "Block-image registry mapping is an indirect command-to-handler boundary; it is not a runtime invocation.",
            "A readlink-family edge in MakeFreeSpaceOnCache establishes a static canonicalization-related call site only.",
            "Absence of a direct edge from the selected canonicalization helper to a write sink is bounded to the selected symbol set and direct BL edges.",
            "No updater, recovery, OTA, crafted path, symlink, device, or partition operation was executed.",
        ],
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    graph = [
        "flowchart LR",
        "    Main[\"main\"] --> BlockReg[\"RegisterBlockImageFunction\"]",
        "    BlockReg --> RF[\"RegisterFunction(name, function pointer)\"]",
        "    RF -.\"indirect registry\".-> BlockHandlers[\"block_image_* handlers\"]",
        "    BlockHandlers --> Verify[\"BlockImageVerifyFn\"]",
        "    BlockHandlers --> Update[\"BlockImageUpdateFn\"]",
        "    BlockHandlers --> Recover[\"BlockImageRecoverFn\"]",
        "    Update --> Perform[\"PerformBlockImageUpdate\"]",
        "    Perform --> Write[\"WriteToPartition\"]",
        "    Cache[\"MakeFreeSpaceOnCache\"] --> Readlink[\"__readlink_chk\"]",
        "    Readlink -.\"no direct selected edge to write sink\".-> Write",
    ]
    (args.output / "blockimage-canonicalization-flow.mmd").write_text("\n".join(graph) + "\n", encoding="utf-8")
    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps(summary["observations"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
