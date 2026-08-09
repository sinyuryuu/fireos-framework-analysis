#!/usr/bin/env python3
"""Close the PS7331 native updater dispatch/canonicalization gap offline.

This audit correlates the existing symbolized AArch64 disassembly, direct call
edge table, ELF data cells, and updater-script.  It recovers the names and
function-pointer cells passed to RegisterFunction, then records what is and is
not observable in the selected disassembly for path canonicalization.

The script is deliberately non-executing: it never runs update-binary, opens
an OTA, sends a recovery command, contacts a device, or writes a partition.
Outputs are versioned and an existing output directory is never overwritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
from datetime import datetime, timezone
from pathlib import Path


REGISTER_TARGET = 0x41D528
REGISTER_FUNCTIONS = "RegisterInstallFunctions"
DATA_POINTER_BASE = 0x5AF000
TEXT_BASE = 0x400000

CALLOUT_RE = re.compile(r"^\s*([0-9a-f]+):\s+bl\s+0x([0-9a-f]+)")
HEADER_RE = re.compile(r"^===== ([^ ]+) .+ \[0x([0-9a-f]+), 0x([0-9a-f]+)\) =====$")
ADR_PAGE_RE = re.compile(r"adrp\s+x(\d+),\s+0x([0-9a-f]+)")
ADD_PAGE_RE = re.compile(r"add\s+x(\d+),\s+x(\d+),\s+#0x([0-9a-f]+)")
LDR_CELL_RE = re.compile(r"ldr\s+x(\d+),\s+\[x(\d+),\s+#0x([0-9a-f]+)\]")
LDR_MEM_RE = re.compile(r"ldr\s+x(\d+),\s+\[x(\d+)\]")
LDUR_MEM_RE = re.compile(r"ldur\s+x(\d+),\s+\[x(\d+),\s+#0x([0-9a-f]+)\]")
LDR_Q_RE = re.compile(r"ldr\s+q(\d+),\s+\[x(\d+)\]")
MOV_RE = re.compile(r"mov\s+([wx])(\d+),\s+#0x([0-9a-f]+)")
MOV_DEC_RE = re.compile(r"mov\s+([wx])(\d+),\s+#([0-9]+)")
MOVK_RE = re.compile(r"movk\s+([wx])(\d+),\s+#0x([0-9a-f]+),\s+lsl\s+#([0-9]+)")
ORR_RE = re.compile(r"orr\s+w(\d+),\s+wzr,\s+#0x([0-9a-f]+)")
STRB_RE = re.compile(r"strb\s+w(\d+),\s+\[sp(?:,\s+#0x([0-9a-f]+))?\]")
STUR_RE = re.compile(r"stur\s+([wx])(\d+),\s+\[sp,\s+#0x([0-9a-f]+)\]")
STURH_RE = re.compile(r"sturh\s+w(\d+),\s+\[sp,\s+#0x([0-9a-f]+)\]")
STURQ_RE = re.compile(r"stur\s+q(\d+),\s+\[sp,\s+#0x([0-9a-f]+)\]")
STRING_RE = re.compile(r"^[0-9a-f]+\s+(.+)$")

CANONICAL_MARKERS = ("readlink", "realpath", "symlink_realpath", "canonical")
WRITE_MARKERS = ("ota_open", "open", "openat", "ota_write", "write", "rename", "chown")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_elf_load_segments(path: Path) -> list[tuple[int, int, int]]:
    with path.open("rb") as stream:
        header = stream.read(64)
        if header[:4] != b"\x7fELF" or header[4] != 2 or header[5] != 1:
            raise ValueError(f"expected little-endian ELF64: {path}")
        phoff = struct.unpack_from("<Q", header, 32)[0]
        phentsize = struct.unpack_from("<H", header, 54)[0]
        phnum = struct.unpack_from("<H", header, 56)[0]
        segments: list[tuple[int, int, int]] = []
        for index in range(phnum):
            stream.seek(phoff + index * phentsize)
            entry = stream.read(phentsize)
            p_type, _flags, p_offset, p_vaddr, _paddr, p_filesz, _memsz, _align = struct.unpack_from("<IIQQQQQQ", entry, 0)
            if p_type == 1 and p_filesz:
                segments.append((p_vaddr, p_offset, p_filesz))
        return segments


class ElfReader:
    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        self.segments = parse_elf_load_segments(path)

    def offset(self, virtual_address: int) -> int | None:
        for vaddr, file_offset, size in self.segments:
            if vaddr <= virtual_address < vaddr + size:
                return file_offset + virtual_address - vaddr
        return None

    def read(self, virtual_address: int, size: int) -> bytes | None:
        offset = self.offset(virtual_address)
        if offset is None or offset + size > len(self.data):
            return None
        return self.data[offset : offset + size]

    def read_u64(self, virtual_address: int) -> int | None:
        raw = self.read(virtual_address, 8)
        return struct.unpack("<Q", raw)[0] if raw is not None else None


def parse_symbols(path: Path) -> dict[int, str]:
    result: dict[int, str] = {}
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row.get("type") != "FUNC" or not row.get("name"):
                continue
            try:
                result[int(row["address"], 16)] = row["name"]
            except (KeyError, TypeError, ValueError):
                continue
    return result


def parse_edges(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def parse_disassembly(path: Path) -> dict[str, list[str]]:
    functions: dict[str, list[str]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        header = HEADER_RE.match(line)
        if header:
            current = header.group(1)
            functions[current] = [line]
        elif current is not None:
            functions[current].append(line)
    return functions


def parse_instruction_address(line: str) -> int | None:
    match = re.match(r"^\s*([0-9a-f]+):", line)
    return int(match.group(1), 16) if match else None


def register_calls(lines: list[str]) -> list[tuple[int, int, list[str]]]:
    calls: list[tuple[int, int, list[str]]] = []
    positions: list[tuple[int, int, list[str]]] = []
    for index, line in enumerate(lines):
        match = CALLOUT_RE.match(line)
        if match and int(match.group(2), 16) == REGISTER_TARGET:
            positions.append((index, int(match.group(1), 16), []))
    for number, (index, address, _unused) in enumerate(positions):
        start = positions[number - 1][0] + 1 if number else 0
        calls.append((address, index, lines[start:index + 1]))
    return calls


def set_reg(regs: dict[str, int], kind: str, number: int, value: int) -> None:
    width = 32 if kind == "w" else 64
    mask = (1 << width) - 1
    regs[f"x{number}"] = value & mask


def update_reg(regs: dict[str, int], kind: str, number: int, value: int, shift: int) -> None:
    key = f"x{number}"
    width = 32 if kind == "w" else 64
    mask = (1 << width) - 1
    current = regs.get(key, 0)
    if kind == "w":
        current = current & 0xFFFFFFFF
    current &= ~(0xFFFF << shift)
    regs[key] = (current | ((value & 0xFFFF) << shift)) & mask


def decode_stack_string(lines: list[str], elf: ElfReader) -> dict[str, object]:
    regs: dict[str, int] = {}
    addresses: dict[str, int] = {}
    vectors: dict[int, bytes] = {}
    stack = bytearray(96)
    source_addresses: list[int] = []

    def store(offset: int, raw: bytes) -> None:
        if 0 <= offset < len(stack):
            end = min(len(stack), offset + len(raw))
            stack[offset:end] = raw[: end - offset]

    for line in lines:
        match = ADR_PAGE_RE.search(line)
        if match:
            addresses[f"x{match.group(1)}"] = int(match.group(2), 16)
            continue
        match = ADD_PAGE_RE.search(line)
        if match and match.group(1) == match.group(2):
            key = f"x{match.group(1)}"
            if key in addresses:
                addresses[key] += int(match.group(3), 16)
            continue
        match = MOV_RE.search(line)
        if match:
            set_reg(regs, match.group(1), int(match.group(2)), int(match.group(3), 16))
            continue
        match = MOV_DEC_RE.search(line)
        if match:
            set_reg(regs, match.group(1), int(match.group(2)), int(match.group(3), 10))
            continue
        match = MOVK_RE.search(line)
        if match:
            update_reg(regs, match.group(1), int(match.group(2)), int(match.group(3), 16), int(match.group(4)))
            continue
        match = ORR_RE.search(line)
        if match:
            set_reg(regs, "w", int(match.group(1)), int(match.group(2), 16))
            continue
        match = LDR_MEM_RE.search(line)
        if match:
            dst, src = f"x{match.group(1)}", f"x{match.group(2)}"
            va = addresses.get(src)
            raw = elf.read(va, 8) if va is not None else None
            if va is not None:
                source_addresses.append(va)
            if raw is not None:
                regs[dst] = struct.unpack("<Q", raw)[0]
            continue
        match = LDUR_MEM_RE.search(line)
        if match:
            dst, src, addend = f"x{match.group(1)}", f"x{match.group(2)}", int(match.group(3), 16)
            va = addresses.get(src)
            raw = elf.read(va + addend, 8) if va is not None else None
            if va is not None:
                source_addresses.append(va + addend)
            if raw is not None:
                regs[dst] = struct.unpack("<Q", raw)[0]
            continue
        match = LDR_Q_RE.search(line)
        if match:
            vector_number, src = int(match.group(1)), f"x{match.group(2)}"
            va = addresses.get(src)
            raw = elf.read(va, 16) if va is not None else None
            if va is not None:
                source_addresses.append(va)
            if raw is not None:
                vectors[vector_number] = raw
            continue
        match = LDR_CELL_RE.search(line)
        if match:
            # This is generally the function-pointer load into x1; it is not
            # part of the string object and is handled by the caller.
            continue
        match = STRB_RE.search(line)
        if match:
            register, offset_text = int(match.group(1)), match.group(2)
            offset = int(offset_text, 16) if offset_text else 0
            store(offset, bytes([regs.get(f"x{register}", 0) & 0xFF]))
            continue
        match = STURH_RE.search(line)
        if match:
            register, offset = int(match.group(1)), int(match.group(2), 16)
            store(offset, struct.pack("<H", regs.get(f"x{register}", 0) & 0xFFFF))
            continue
        match = STUR_RE.search(line)
        if match:
            kind, register, offset = match.group(1), int(match.group(2)), int(match.group(3), 16)
            width = 4 if kind == "w" else 8
            store(offset, int(regs.get(f"x{register}", 0)).to_bytes(width, "little"))
            continue
        match = STURQ_RE.search(line)
        if match:
            vector_number, offset = int(match.group(1)), int(match.group(2), 16)
            if vector_number in vectors:
                store(offset, vectors[vector_number])

    encoded_length = stack[0]
    if encoded_length & 1:
        decoded_length: int | None = None
    else:
        decoded_length = encoded_length >> 1
    raw = bytes(stack[1 : 1 + decoded_length]) if decoded_length is not None else b""
    try:
        name = raw.split(b"\x00", 1)[0].decode("ascii") if raw else ""
    except UnicodeDecodeError:
        name = ""
    return {
        "name": name,
        "encoded_length": encoded_length,
        "decoded_length": decoded_length,
        "raw_hex": raw.hex(),
        "source_addresses": ",".join(hex(value) for value in sorted(set(source_addresses))),
        "stack_hex": bytes(stack[: 1 + (decoded_length or 0)]).hex(),
    }


def recover_registrations(function_lines: list[str], elf: ElfReader, symbols: dict[int, str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    calls = register_calls(function_lines)
    for index, (instruction_address, _line_index, block) in enumerate(calls, 1):
        pointer_cell: int | None = None
        for line in block:
            match = LDR_CELL_RE.search(line)
            if match and match.group(1) == "1" and match.group(2) == "1":
                pointer_cell = DATA_POINTER_BASE + int(match.group(3), 16)
        pointer_value = elf.read_u64(pointer_cell) if pointer_cell is not None else None
        # Some registration blocks deliberately reuse the SSO length register
        # established immediately before the previous RegisterFunction call.
        # Decode from the function start so register state is preserved while
        # the current call's stack writes provide the current name object.
        stack = decode_stack_string(function_lines[:_line_index + 1], elf)
        source_window = decode_stack_string(block, elf)
        stack["source_addresses"] = source_window["source_addresses"]
        resolved_symbol = symbols.get(pointer_value or 0, "")
        name = str(stack["name"])
        name_confidence = "strong" if name and stack["decoded_length"] == len(name) else "bounded"
        rows.append({
            "registration_index": index,
            "register_call_instruction": hex(instruction_address),
            "command_name": name,
            "command_name_confidence": name_confidence,
            "name_length_encoding": stack["encoded_length"],
            "name_raw_hex": stack["raw_hex"],
            "name_source_addresses": stack["source_addresses"],
            "function_pointer_cell": hex(pointer_cell) if pointer_cell is not None else "",
            "function_pointer_value": hex(pointer_value) if pointer_value is not None else "",
            "function_pointer_symbol": resolved_symbol,
            "function_pointer_resolution": "symbol" if resolved_symbol else ("data-cell" if pointer_value is not None else "unresolved"),
            "evidence_disassembly": f"RegisterInstallFunctions:{hex(instruction_address)}",
        })
    return rows


def selected_function_ranges(path: Path) -> dict[str, tuple[int, int]]:
    ranges: dict[str, tuple[int, int]] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = HEADER_RE.match(line)
        if match:
            ranges[match.group(1)] = (int(match.group(2), 16), int(match.group(3), 16))
    return ranges


def canonicalization_rows(edges: list[dict[str, str]], ranges: dict[str, tuple[int, int]], symbols: dict[int, str]) -> list[dict[str, object]]:
    targets = [
        ("readlink", 0x4CC3D8),
        ("__readlink_chk", 0x4CE4E8),
        ("readlinkat", 0x4D48A8),
        ("realpath", None),
        ("symlink_realpath", None),
    ]
    rows: list[dict[str, object]] = []
    for marker, address in targets:
        matching_edges = [row for row in edges if marker.lower() in (row.get("callee", "") + " " + row.get("callee_resolved", "")).lower()]
        selected_callers = sorted({row.get("caller_label", "") for row in matching_edges})
        rows.append({
            "marker": marker,
            "symbol_address": hex(address) if address is not None else "not symbolized in supplied table",
            "symbol_present": bool(address is not None and address in symbols) or marker in {"readlink", "readlinkat", "__readlink_chk"},
            "selected_disassembly_present": marker in ranges,
            "direct_edge_count": len(matching_edges),
            "direct_edge_callers": ";".join(selected_callers),
            "classification": (
                "direct-edge-observed" if matching_edges else
                "selected-function-without-caller-edge" if marker in ranges else
                "symbol-or-string-marker-not-in-selected-graph"
            ),
            "interpretation": "absence from the selected graph is bounded negative evidence, not proof of absence from the binary",
        })
    return rows


def parse_script(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if any(token in line for token in ("package_extract_file(", "block_image_update(", "run_program(")):
            rows.append({"line": line_number, "text": line.strip()})
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = sorted({key for row in rows for key in row}) if rows else ["empty"]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--symbols", type=Path, required=True)
    parser.add_argument("--edges", type=Path, required=True)
    parser.add_argument("--disassembly", type=Path, required=True)
    parser.add_argument("--strings", type=Path, required=True)
    parser.add_argument("--updater-script", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    inputs = [args.binary, args.symbols, args.edges, args.disassembly, args.strings, args.updater_script]
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "host_only": True,
            "device_contacted": False,
            "updater_executed": False,
            "partition_written": False,
            "output": str(args.output),
            "inputs": [str(path) for path in inputs],
        }, indent=2))
        return 0
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise SystemExit("missing input files:\n" + "\n".join(missing))
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    elf = ElfReader(args.binary)
    symbols = parse_symbols(args.symbols)
    edges = parse_edges(args.edges)
    disassembly = parse_disassembly(args.disassembly)
    ranges = selected_function_ranges(args.disassembly)
    register_rows = recover_registrations(disassembly.get(REGISTER_FUNCTIONS, []), elf, symbols)
    canonical_rows = canonicalization_rows(edges, ranges, symbols)
    script_rows = parse_script(args.updater_script)
    marker_lines = [
        {"line": index, "markers": ";".join(marker for marker in CANONICAL_MARKERS if marker in line.lower()), "text": line.strip()}
        for index, line in enumerate(args.strings.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
        if any(marker in line.lower() for marker in CANONICAL_MARKERS)
    ]

    args.output.mkdir(parents=True)
    write_csv(args.output / "registration-dispatch.csv", register_rows)
    write_csv(args.output / "canonicalization-context.csv", canonical_rows)
    write_csv(args.output / "canonicalization-marker-strings.csv", marker_lines)
    write_csv(args.output / "updater-script-entrypoints.csv", script_rows)

    function_pointer_resolved = sum(row["function_pointer_resolution"] == "symbol" for row in register_rows)
    command_names = [row["command_name"] for row in register_rows if row["command_name"]]
    direct_canonical_edges = sum(row["direct_edge_count"] for row in canonical_rows)
    edge_callee_text = lambda row: f"{row.get('callee', '')} {row.get('callee_resolved', '')}"
    summary = {
        "phase": "6MK",
        "analysis": "host-only native updater registration, indirect dispatch, and canonicalization closure",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "updater_executed": False,
        "recovery_executed": False,
        "partition_written": False,
        "inputs": {str(path): sha256(path) for path in inputs},
        "registration_call_count": len(register_rows),
        "function_pointer_symbol_resolution_count": function_pointer_resolved,
        "recovered_command_names": command_names,
        "canonicalization_direct_edge_count": direct_canonical_edges,
        "canonicalization_marker_string_count": len(marker_lines),
        "updater_script_entrypoint_count": len(script_rows),
        "selected_function_ranges": {name: [hex(start), hex(end)] for name, (start, end) in ranges.items()},
        "observations": {
            "register_install_functions_called_by_main": any(row.get("caller_label") == "main" and row.get("callee", "") == "_Z24RegisterInstallFunctionsv" for row in edges),
            "register_function_dispatch_is_indirect": bool(register_rows),
            "all_registration_function_pointers_resolved_to_symbols": function_pointer_resolved == len(register_rows) and bool(register_rows),
            "package_extract_file_has_ota_open_direct_edge": any(row.get("caller_label") == "PackageExtractFileFn" and "ota_open" in edge_callee_text(row) for row in edges),
            "canonicalization_direct_edge_in_selected_graph": bool(direct_canonical_edges),
            "canonicalization_markers_present": bool(marker_lines),
            "make_free_space_body_selected": "MakeFreeSpaceOnCache" in ranges,
        },
        "bounded_interpretation": [
            "RegisterInstallFunctions calls a common RegisterFunction routine with command-name objects and function-pointer cells; unresolved cells remain an indirect-dispatch boundary.",
            "The supplied selected disassembly directly connects extraction and write handlers to open/write/rename wrappers as recorded in the prior audit.",
            "readlink/realpath markers without a selected direct caller edge do not prove that canonicalization is absent from unselected functions or indirect dispatch.",
            "No runtime behavior, OTA verification, path traversal, symlink behavior, or partition mutation was tested.",
        ],
        "rejected_operations": [
            "Executing update-binary or recovery",
            "Sending, modifying, or crafting OTA packages",
            "Symlink/path-traversal/canonicalization runtime tests",
            "Fastboot, sideload, remount, partition write, or device mutation",
        ],
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    graph = [
        "flowchart LR",
        "    Main[\"main\"] --> Reg[\"RegisterInstallFunctions\"]",
        "    Main --> BlockReg[\"RegisterBlockImageFunction\"]",
        "    Reg --> RF[\"RegisterFunction(name, function pointer)\"]",
        "    RF -.\"indirect registry\".-> Handler[\"registered handler\"]",
        "    Handler --> Extract[\"PackageExtractFileFn\"]",
        "    Handler --> Block[\"PerformBlockImageUpdate / WriteToPartition\"]",
        "    Extract --> Open[\"ota_open / open\"]",
        "    Block --> Write[\"ota_write / write / rename\"]",
        "    Marker[\"readlink / realpath markers\"] -.\"no direct edge in selected graph\".-> Guard[\"canonicalization guard unresolved\"]",
    ]
    (args.output / "dispatch-canonicalization-flow.mmd").write_text("\n".join(graph) + "\n", encoding="utf-8")

    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps(summary["observations"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
