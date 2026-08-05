#!/usr/bin/env python3
"""Extract and inspect the embedded mini-ELF debug data from an OTA updater.

The input is parsed as bytes only. The updater is never executed, loaded, or
sent to a device. This is a host-only provenance and symbol-recovery audit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import lzma
import re
import struct
from datetime import datetime, timezone
from pathlib import Path


ELF64_EHDR = struct.Struct("<16sHHIQQQIHHHHHH")
ELF64_SHDR = struct.Struct("<IIQQQQIIQQ")
ELF64_SYM = struct.Struct("<IBBHQQ")
MATCH = re.compile(
    r"(?i)(symlink|readlink|realpath|canonical|extract|verify|package|block|"
    r"write|rename|copy|delete|zip|sha|hash|install|path|mount|open|chmod|"
    r"chown|unlink|travers)"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def c_string(table: bytes, offset: int) -> str:
    if offset < 0 or offset >= len(table):
        return ""
    end = table.find(b"\0", offset)
    if end < 0:
        end = len(table)
    return table[offset:end].decode("utf-8", "replace")


def read_sections(elf: bytes) -> tuple[dict[str, object], list[dict[str, object]]]:
    if len(elf) < ELF64_EHDR.size or elf[:4] != b"\x7fELF":
        raise ValueError("not an ELF64 byte stream")
    header = ELF64_EHDR.unpack_from(elf, 0)
    if header[1] != 2 or header[2] != 183:
        raise ValueError("expected an AArch64 executable mini-ELF")
    shoff, shentsize, shnum, shstrndx = header[6], header[11], header[12], header[13]
    if shentsize != ELF64_SHDR.size or shoff + shnum * shentsize > len(elf):
        raise ValueError("invalid section table")
    raw = [ELF64_SHDR.unpack_from(elf, shoff + i * shentsize) for i in range(shnum)]
    shstr = raw[shstrndx]
    names = elf[shstr[4] : shstr[4] + shstr[5]]
    sections: list[dict[str, object]] = []
    for index, row in enumerate(raw):
        name = c_string(names, row[0])
        sections.append({
            "index": index,
            "name": name,
            "type": row[1],
            "flags": row[2],
            "address": row[3],
            "offset": row[4],
            "size": row[5],
            "link": row[6],
            "info": row[7],
            "align": row[8],
            "entsize": row[9],
        })
    meta = {
        "class": header[0][4],
        "type": header[1],
        "machine": header[2],
        "entry": header[4],
        "section_offset": shoff,
        "section_count": shnum,
    }
    return meta, sections


def section_bytes(elf: bytes, section: dict[str, object]) -> bytes:
    offset = int(section["offset"])
    size = int(section["size"])
    if offset + size > len(elf):
        raise ValueError(f"section outside ELF: {section['name']}")
    return elf[offset : offset + size]


def extract_debugdata(binary: bytes) -> bytes:
    _, sections = read_sections(binary)
    section = next((s for s in sections if s["name"] == ".gnu_debugdata"), None)
    if section is None:
        raise ValueError(".gnu_debugdata section not found")
    return lzma.decompress(section_bytes(binary, section))


def parse_symbols(mini: bytes, sections: list[dict[str, object]]) -> list[dict[str, object]]:
    sym = next((s for s in sections if s["name"] == ".symtab"), None)
    if sym is None:
        return []
    string_index = int(sym["link"])
    if string_index >= len(sections):
        return []
    strings = section_bytes(mini, sections[string_index])
    entry_size = int(sym["entsize"]) or ELF64_SYM.size
    if entry_size < ELF64_SYM.size:
        return []
    data = section_bytes(mini, sym)
    symbols: list[dict[str, object]] = []
    for offset in range(0, len(data) - ELF64_SYM.size + 1, entry_size):
        name_offset, info, other, shndx, value, size = ELF64_SYM.unpack_from(data, offset)
        name = c_string(strings, name_offset)
        if not name:
            continue
        symbols.append({
            "name": name,
            "value": f"0x{value:x}",
            "size": size,
            "binding": info >> 4,
            "type": info & 0x0F,
            "section": shndx,
        })
    return symbols


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "execute_input": False, "output": str(args.output)}, indent=2))
        return 0
    if not args.binary.is_file():
        raise SystemExit(f"missing input: {args.binary}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    original = args.binary.read_bytes()
    mini = extract_debugdata(original)
    meta, sections = read_sections(mini)
    symbols = parse_symbols(mini, sections)
    args.output.mkdir(parents=True)
    (args.output / "gnu_debugdata.elf").write_bytes(mini)
    with (args.output / "sections.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["index", "name", "type", "flags", "address", "offset", "size", "link", "info", "align", "entsize"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sections)
    with (args.output / "symbols.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["name", "value", "size", "binding", "type", "section"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(symbols)
    matched = [row for row in symbols if MATCH.search(str(row["name"]))]
    with (args.output / "matched-symbols.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["name", "value", "size", "binding", "type", "section"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(matched)
    summary = {
        "host_only": True,
        "input": str(args.binary),
        "input_sha256": sha256(args.binary),
        "input_executed": False,
        "mini_elf_sha256": sha256(args.output / "gnu_debugdata.elf"),
        "mini_elf_bytes": len(mini),
        "mini_elf": meta,
        "section_count": len(sections),
        "symbol_count": len(symbols),
        "matched_symbol_count": len(matched),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "limitations": [
            "The embedded mini-ELF contains symbol metadata but no executable section bytes in this extraction.",
            "Names and symbol addresses do not prove runtime reachability or a path-safety defect.",
            "No OTA package, updater, recovery binary, or malformed input was executed.",
        ],
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text("\n".join(f"{sha256(path)}  {path.relative_to(args.output)}" for path in files) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "symbols": len(symbols), "matched_symbols": len(matched), "mini_elf_bytes": len(mini)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
