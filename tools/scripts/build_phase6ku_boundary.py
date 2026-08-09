#!/usr/bin/env python3
"""Build a host-only Phase 6KU IPC/updater dispatch boundary bundle.

The script reads preserved reports, CSVs, disassembly text, the PS7331
updater ELF, and the original updater script.  It never invokes ADB, Binder,
the updater, recovery, an APK, or a native executable.  The generated bundle
records the exact native callbacks registered by RegisterInstallFunctions and
the fixed commands present in updater-script, then hashes all inputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


REGISTERED_NAMES = [
    "mount",
    "is_mounted",
    "unmount",
    "format",
    "show_progress",
    "set_progress",
    "package_extract_file",
    "getprop",
    "file_getprop",
    "apply_patch",
    "apply_patch_check",
    "apply_patch_space",
    "wipe_block_device",
    "read_file",
    "sha1_check",
    "write_value",
    "wipe_cache",
    "ui_print",
    "run_program",
    "reboot_now",
    "get_stage",
    "set_stage",
    "enable_reboot",
    "tune2fs",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(root: Path, relative: str) -> Path:
    path = root / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def elf_sections(path: Path) -> Dict[str, Dict[str, int]]:
    data = path.read_bytes()
    if data[:4] != b"\x7fELF" or data[4] != 2 or data[5] != 1:
        raise ValueError(f"expected ELF64 little-endian input: {path}")
    header = struct.unpack_from("<16sHHIQQQIHHHHHH", data, 0)
    section_offset = header[6]
    section_entry_size = header[11]
    section_count = header[12]
    string_index = header[13]
    raw_sections = []
    for index in range(section_count):
        values = struct.unpack_from(
            "<IIQQQQIIQQ",
            data,
            section_offset + index * section_entry_size,
        )
        raw_sections.append(values)
    string_section = raw_sections[string_index]
    string_data = data[string_section[4] : string_section[4] + string_section[5]]
    result: Dict[str, Dict[str, int]] = {}
    for values in raw_sections:
        name_offset, _, _, address, offset, size, _, _, _, _ = values
        end = string_data.find(b"\0", name_offset)
        name = string_data[name_offset:end].decode("utf-8", "replace")
        result[name] = {"address": address, "offset": offset, "size": size}
    return result


def vaddr_to_offset(section: Dict[str, int], address: int) -> int:
    relative = address - section["address"]
    if relative < 0 or relative + 8 > section["size"]:
        raise ValueError(f"address 0x{address:x} outside section")
    return section["offset"] + relative


def resolve_register_entries(
    root: Path,
    binary: Path,
    call_edges: Path,
    symbols: Path,
    disassembly: Path,
) -> Tuple[List[Dict[str, object]], Tuple[int, int]]:
    edges = [
        row
        for row in read_csv(call_edges)
        if row.get("caller_label") == "RegisterInstallFunctions"
        and "RegisterFunction" in row.get("callee", "")
    ]
    symbol_rows = read_csv(symbols)
    by_address = {
        int(row["address"], 16): row["name"]
        for row in symbol_rows
        if row.get("type") == "FUNC" and row.get("address")
    }
    sections = elf_sections(binary)
    got = sections[".got"]
    rodata = sections[".rodata"]
    binary_data = binary.read_bytes()
    rodata_data = binary_data[rodata["offset"] : rodata["offset"] + rodata["size"]]
    # The compiler keeps the first 17 names and the final six names in the
    # adjacent rodata pool.  `ui_print` is built from AArch64 immediates in
    # the middle of the function, so it is intentionally not treated as a
    # rodata literal.
    prefix = b"\0".join(name.encode() for name in REGISTERED_NAMES[:17]) + b"\0"
    suffix = b"\0".join(name.encode() for name in REGISTERED_NAMES[18:]) + b"\0"
    prefix_offset = rodata_data.find(prefix)
    suffix_offset = rodata_data.find(suffix)
    if prefix_offset < 0 or suffix_offset < 0:
        raise ValueError("RegisterInstallFunctions rodata name sequences not found")

    lines = disassembly.read_text(errors="replace").splitlines()
    instruction_indices: Dict[int, int] = {}
    for index, line in enumerate(lines):
        match = re.match(r"\s*([0-9a-f]+):", line)
        if match:
            instruction_indices[int(match.group(1), 16)] = index

    if len(edges) != len(REGISTERED_NAMES):
        raise ValueError(
            f"expected {len(REGISTERED_NAMES)} registration calls, found {len(edges)}"
        )

    entries: List[Dict[str, object]] = []
    for ordinal, edge in enumerate(edges, 1):
        instruction = int(edge["instruction"], 16)
        line_index = instruction_indices.get(instruction)
        if line_index is None:
            raise ValueError(f"missing disassembly instruction 0x{instruction:x}")
        got_offset = None
        for previous in reversed(lines[max(0, line_index - 12) : line_index]):
            match = re.search(r"ldr\s+x1,\s+\[x1,\s+#0x([0-9a-f]+)\]", previous)
            if match:
                got_offset = int(match.group(1), 16)
                break
        if got_offset is None:
            raise ValueError(f"missing GOT load before 0x{instruction:x}")
        got_address = 0x5AF000 + got_offset
        pointer = struct.unpack_from("<Q", binary_data, vaddr_to_offset(got, got_address))[0]
        entries.append(
            {
                "ordinal": ordinal,
                "edify_name": REGISTERED_NAMES[ordinal - 1],
                "registration_instruction": f"0x{instruction:x}",
                "got_address": f"0x{got_address:x}",
                "handler_address": f"0x{pointer:x}",
                "handler_symbol": by_address.get(pointer, f"UNKNOWN_0x{pointer:x}"),
                "string_source": (
                    "inline AArch64 immediate at 0x406e68-0x406e94"
                    if REGISTERED_NAMES[ordinal - 1] == "ui_print"
                    else f".rodata:0x{rodata['address'] + (prefix_offset if ordinal <= 17 else suffix_offset):x}"
                ),
            }
        )
    return entries, (rodata["address"] + prefix_offset, rodata["address"] + suffix_offset)


def script_commands(path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    pattern = re.compile(r"^\s*([a-zA-Z0-9_]+)\((.*)$")
    for line_number, raw in enumerate(path.read_text(errors="replace").splitlines(), 1):
        match = pattern.match(raw)
        if not match:
            continue
        command = match.group(1)
        if command not in {"block_image_update", "package_extract_file", "getprop", "ui_print"}:
            continue
        quoted = re.findall(r'"([^"]*)"', raw)
        target = ""
        source = ""
        classification = "parser_or_compatibility_gate"
        if command == "block_image_update" and quoted:
            target = quoted[0]
            classification = "block_image_update_partition_path"
        elif command == "package_extract_file":
            source = quoted[0] if quoted else ""
            target = quoted[1] if len(quoted) > 1 else ""
            classification = (
                "partition_write"
                if target.startswith("/dev/block/")
                else "recovery_metadata_write"
                if target.startswith("/cache/")
                else "package_extraction"
            )
        elif command == "getprop":
            classification = "compatibility_gate_or_property_read"
        rows.append(
            {
                "line": line_number,
                "command": command,
                "target": target,
                "source": source,
                "classification": classification,
                "execution_status": "NOT_EXECUTED",
                "text": raw.strip(),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="output directory (default: artifacts/phase6ku/boundary-20260810-01)",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output or root / "artifacts/phase6ku/boundary-20260810-01").resolve()
    output.mkdir(parents=True, exist_ok=True)

    input_paths = {
        "update_binary": "firmware/extracted/PS7331/META-INF/com/google/android/update-binary",
        "updater_script": "firmware/extracted/PS7331/META-INF/com/google/android/updater-script",
        "call_edges": "artifacts/phase6s/ota-call-edges-20260805-01/call-edges.csv",
        "function_symbols": "artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv",
        "focus_disassembly": "artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt",
        "phase6er_report": "findings/phase-6er-amazon-prewarm-confused-deputy.md",
        "phase6fi_fk_report": "findings/phase-6fi-fk-amazon-user-manager-tx-boundary.md",
        "phase6ia_report": "findings/phase-6ia-amazon-package-manager-closure.md",
        "phase6p_report": "findings/phase-6p-native-updater-closure.md",
        "phase6kt_report": "findings/phase-6kt-recovery-verifier-provenance.md",
    }
    paths = {name: require(root, relative) for name, relative in input_paths.items()}
    input_hashes = {
        name: {"path": str(path.relative_to(root)), "sha256": sha256(path), "size": path.stat().st_size}
        for name, path in paths.items()
    }

    registrations, string_addresses = resolve_register_entries(
        root,
        paths["update_binary"],
        paths["call_edges"],
        paths["function_symbols"],
        paths["focus_disassembly"],
    )
    commands = script_commands(paths["updater_script"])

    with (output / "updater-dispatch.csv").open("w", newline="") as handle:
        fields = list(registrations[0].keys())
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(registrations)
    public_table = root / "output/tables/phase6ku-updater-function-map.csv"
    public_table.parent.mkdir(parents=True, exist_ok=True)
    with public_table.open("w", newline="") as handle:
        fields = list(registrations[0].keys())
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(registrations)
    with (output / "updater-script-commands.csv").open("w", newline="") as handle:
        fields = list(commands[0].keys())
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(commands)

    relevant_edges = read_csv(paths["call_edges"])
    selected_callees = {
        "RegisterInstallFunctions",
        "RegisterBlockImageFunctions",
        "Evaluate",
        "VerifyBlocks",
        "WriteToPartition",
        "ota_open",
        "ota_write",
        "SHA1",
        "memcmp",
        "open",
        "write",
    }
    selected_edges = [
        row
        for row in relevant_edges
        if row.get("caller_label") in selected_callees or row.get("callee") in selected_callees
    ]
    with (output / "relevant-call-edges.csv").open("w", newline="") as handle:
        fields = list(selected_edges[0].keys()) if selected_edges else ["caller_label", "instruction", "target_address", "callee"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(selected_edges)

    record = {
        "phase": "6KU",
        "classification": "host-only IPC and native updater boundary",
        "execution_policy": {
            "adb": False,
            "binder": False,
            "apk_execution": False,
            "native_execution": False,
            "ota_or_recovery": False,
            "partition_write": False,
        },
        "inputs": input_hashes,
        "register_install_functions": {
            "address": "0x406978",
            "end": "0x407078",
            "registration_count": len(registrations),
            "string_prefix_address": f"0x{string_addresses[0]:x}",
            "string_suffix_address": f"0x{string_addresses[1]:x}",
            "dispatch_table": registrations,
        },
        "updater_script_command_count": len(commands),
        "findings": [
            "Ordinary-app prewarm is a confirmed process/resource confused deputy, but its sink is startProcessLocked rather than HOME/package state.",
            "The KFT tx3 path reaches standard PMS setters and is blocked by cross-user or component-state gates in the preserved runtime evidence.",
            "The private Amazon PackageManager interface does not expose a HOME or package-state setter.",
            "The native updater registers data-driven handlers and contains partition I/O, but recovery caller provenance and verification remain outside this bounded audit.",
        ],
        "unresolved": [
            "recovery verifier to update-binary end-to-end caller provenance",
            "indirect function-pointer dispatch outside the recovered direct call edges",
            "complete platform/native staging canonicalization",
            "a low-privilege User-0 HOME/package-state writer",
        ],
        "confidence": "Strong evidence",
    }
    audit_path = output / "result.json"
    audit_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    manifest = []
    for path in sorted(output.iterdir()):
        if path.name == "sha256sums.txt" or not path.is_file():
            continue
        manifest.append(f"{sha256(path)}  {path.name}")
    (output / "sha256sums.txt").write_text("\n".join(manifest) + "\n")
    print(json.dumps({"output": str(audit_path), "sha256": sha256(audit_path), "registration_count": len(registrations), "script_command_count": len(commands)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
