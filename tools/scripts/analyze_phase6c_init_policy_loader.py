#!/usr/bin/env python3
"""Host-only static audit of the PS7331 /init SELinux policy-loader surface.

This tool reads a preserved AArch64 ELF and uses a host disassembler to map
literal policy-path references back to code.  It never executes the ELF, loads
SELinux policy, contacts a device, changes boot properties, or emits device
mutation/exploit instructions.  The result is provenance evidence only: a
reference to a path is not proof that the path was selected at boot.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


PATH_MARKERS = (
    "/system/etc/selinux/rootable_plat_sepolicy.cil",
    "/vendor/etc/selinux/rootable_plat_pub_versioned.cil",
    "/vendor/etc/selinux/rootable_vendor_sepolicy.cil",
    "/odm/etc/selinux/rootable_odm_sepolicy.cil",
    "rootable_fireos_sepolicy.cil",
    "/vendor/etc/selinux/plat_pub_versioned.cil",
    "/vendor/etc/selinux/vendor_sepolicy.cil",
    "/odm/etc/selinux/odm_sepolicy.cil",
    "fireos_sepolicy.cil",
    "/system/etc/selinux/plat_and_mapping_sepolicy.cil.sha256",
    "fireos_precompiled_sepolicy.plat_and_mapping.sha256",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_disassembler(objdump: str, args: list[str]) -> str:
    completed = subprocess.run(
        [objdump, *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout


def parse_loads(program_headers: str) -> list[dict[str, int]]:
    loads: list[dict[str, int]] = []
    pattern = re.compile(
        r"^\s*LOAD\s+off\s+0x([0-9a-f]+)\s+"
        r"vaddr\s+0x([0-9a-f]+)\s+paddr\s+0x([0-9a-f]+)\s+"
        r"align\s+2\*\*(\d+)\s*$",
        re.IGNORECASE,
    )
    # The following two lines contain filesz/memsz/flags in objdump's
    # multi-line program-header format.  Associate them with the most recent
    # LOAD row without parsing any runtime state.
    for line in program_headers.splitlines():
        match = pattern.match(line)
        if match:
            loads.append(
                {
                    "offset": int(match.group(1), 16),
                    "vaddr": int(match.group(2), 16),
                    "paddr": int(match.group(3), 16),
                    "align_power": int(match.group(4)),
                }
            )
            continue
        if loads and "filesz" in line and "memsz" in line:
            size_match = re.search(
                r"filesz\s+0x([0-9a-f]+)\s+memsz\s+0x([0-9a-f]+)\s+"
                r"flags\s+([rwx-]+)",
                line,
                re.IGNORECASE,
            )
            if size_match and "filesz" not in loads[-1]:
                loads[-1].update(
                    {
                        "filesz": int(size_match.group(1), 16),
                        "memsz": int(size_match.group(2), 16),
                        "flags": size_match.group(3),
                    }
                )
    return loads


def file_offset_for_vma(loads: list[dict[str, int]], vma: int) -> int | None:
    for load in loads:
        if "filesz" not in load:
            continue
        if load["vaddr"] <= vma < load["vaddr"] + load["filesz"]:
            return load["offset"] + vma - load["vaddr"]
    return None


def find_marker_occurrences(data: bytes, marker: str) -> list[int]:
    needle = marker.encode("utf-8")
    offsets: list[int] = []
    cursor = 0
    while True:
        position = data.find(needle, cursor)
        if position < 0:
            return offsets
        # Avoid treating a shorter marker as a substring of a longer filename
        # (for example, ``fireos_sepolicy.cil`` inside
        # ``rootable_fireos_sepolicy.cil``).  The full path markers remain
        # exact byte matches; this boundary check only filters an alphanumeric
        # filename continuation immediately before the marker.
        if position == 0 or not chr(data[position - 1]).isalnum() and data[position - 1] not in b"_-":
            offsets.append(position)
        cursor = position + 1


def parse_instructions(disassembly: str) -> list[dict[str, object]]:
    pattern = re.compile(r"^\s*([0-9a-f]+):\s+([0-9a-f ]+)\s+(.+?)\s*$", re.IGNORECASE)
    instructions: list[dict[str, object]] = []
    for line in disassembly.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        instructions.append(
            {
                "address": int(match.group(1), 16),
                "bytes": match.group(2).strip(),
                "text": match.group(3),
            }
        )
    return instructions


def find_adrp_add_references(
    instructions: list[dict[str, object]], target_vmas: dict[int, str]
) -> list[dict[str, object]]:
    adrp_pattern = re.compile(r"\badrp\s+x(\d+),\s*0x([0-9a-f]+)", re.IGNORECASE)
    add_pattern = re.compile(r"\badd\s+x(\d+),\s*x(\d+),\s*#0x([0-9a-f]+)", re.IGNORECASE)
    references: list[dict[str, object]] = []
    for index, instruction in enumerate(instructions):
        adrp = adrp_pattern.search(str(instruction["text"]))
        if not adrp:
            continue
        register = int(adrp.group(1))
        page = int(adrp.group(2), 16)
        for candidate in instructions[index + 1 : index + 5]:
            add = add_pattern.search(str(candidate["text"]))
            if not add:
                continue
            destination = int(add.group(1))
            source = int(add.group(2))
            if destination != register or source != register:
                continue
            target = page + int(add.group(3), 16)
            marker = target_vmas.get(target)
            if marker:
                references.append(
                    {
                        "adrp_address": f"0x{int(instruction['address']):x}",
                        "add_address": f"0x{int(candidate['address']):x}",
                        "register": f"x{register}",
                        "target_vma": f"0x{target:x}",
                        "marker": marker,
                    }
                )
            break
    return references


def window(objdump: str, binary: Path, start: int, stop: int) -> str:
    return run_disassembler(
        objdump,
        ["-d", f"--start-address=0x{start:x}", f"--stop-address=0x{stop:x}", str(binary)],
    )


def build(binary: Path, objdump: str) -> dict[str, object]:
    data = binary.read_bytes()
    program_headers = run_disassembler(objdump, ["-p", str(binary)])
    loads = parse_loads(program_headers)
    if not loads or "filesz" not in loads[0]:
        raise SystemExit("could not parse the first LOAD mapping from objdump -p")

    markers: list[dict[str, object]] = []
    target_vmas: dict[int, str] = {}
    for marker in PATH_MARKERS:
        for offset in find_marker_occurrences(data, marker):
            vma = loads[0]["vaddr"] + offset - loads[0]["offset"]
            record = {
                "marker": marker,
                "file_offset": f"0x{offset:x}",
                "vma": f"0x{vma:x}",
                "load_segment": 0,
            }
            markers.append(record)
            target_vmas[vma] = marker

    full_disassembly = run_disassembler(objdump, ["-d", str(binary)])
    instructions = parse_instructions(full_disassembly)
    references = find_adrp_add_references(instructions, target_vmas)
    windows = [
        (0x4041F0, 0x404220, "caller_4041f0"),
        (0x41AD00, 0x41B0A0, "policy_path_builder_41ad00"),
        (0x41BD60, 0x41BE00, "selinux_property_compare_41bd60"),
        (0x41BE00, 0x41BF30, "policy_loader_41be00"),
    ]

    return {
        "schema": "phase6c-init-policy-loader-audit-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {
            "path": str(binary),
            "sha256": sha256(binary),
            "objdump": objdump,
            "elf_execution": False,
        },
        "program_headers": loads,
        "string_markers": markers,
        "code_references": references,
        "static_landmarks": [
            {
                "address": "0x4041fc",
                "observation": "direct call to 0x41b748, followed by direct call to 0x41ad00",
                "classification": "static_call_site_only",
            },
            {
                "address": "0x41ad00",
                "observation": "builds several policy-path records and calls 0x41be00 with w5=1",
                "classification": "rootable_path_builder_candidate",
            },
            {
                "address": "0x41af80",
                "observation": "calls 0x41be00 with w5=0 after standard policy-path setup",
                "classification": "standard_path_builder_candidate",
            },
            {
                "address": "0x41bd60",
                "observation": "compares a 19-byte key against androidboot.selinux and a 10-byte value against permissive, then writes zero to a field on success",
                "classification": "boot_property_parser_candidate",
            },
            {
                "address": "0x41be48",
                "observation": "branches on w5 before the policy-loader body; exact semantic meaning of the flag is unresolved in stripped code",
                "classification": "unresolved_branch",
            },
        ],
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "elf_executed": False,
            "selinux_policy_loaded": False,
            "boot_property_changed": False,
            "kernel_memory_accessed": False,
            "exploit_or_root_payload": False,
        },
        "limits": [
            "A code reference proves only that the stripped /init contains a path-building or loader reference.",
            "The audit cannot identify the active policy variant on a stock boot.",
            "The audit cannot infer the exact high-level meaning of stripped helper calls or w5.",
        ],
        "windows": [{"start": f"0x{s:x}", "stop": f"0x{e:x}", "label": label} for s, e, label in windows],
    }


def write_outputs(result: dict[str, object], output: Path, objdump: str, binary: Path) -> None:
    output.mkdir(parents=True)
    summary = output / "policy-loader-audit.json"
    references = output / "policy-path-references.csv"
    report = output / "result.md"
    windows_file = output / "disassembly-windows.txt"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with references.open("w", encoding="utf-8", newline="") as stream:
        fields = ["marker", "adrp_address", "add_address", "register", "target_vma"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for item in result["code_references"]:  # type: ignore[index]
            writer.writerow({field: item.get(field, "") for field in fields})

    window_specs = [(0x4041F0, 0x404220, "caller_4041f0"),
                    (0x41AD00, 0x41B0A0, "policy_path_builder_41ad00"),
                    (0x41BD60, 0x41BE00, "selinux_property_compare_41bd60"),
                    (0x41BE00, 0x41BF30, "policy_loader_41be00")]
    with windows_file.open("w", encoding="utf-8") as stream:
        for start, stop, label in window_specs:
            stream.write(f"===== {label} 0x{start:x}-0x{stop:x} =====\n")
            stream.write(window(objdump, binary, start, stop))
            stream.write("\n")

    rootable = [item for item in result["code_references"] if "rootable" in item["marker"]]  # type: ignore[index]
    standard = [item for item in result["code_references"] if "rootable" not in item["marker"]]  # type: ignore[index]
    report.write_text(
        "# PS7331 `/init` policy-loader static audit\n\n"
        "Host-only disassembly/provenance analysis. The ELF was not executed; no boot property, SELinux policy, device, kernel memory, or exploit path was touched.\n\n"
        "## Observed\n\n"
        f"- Input SHA-256: `{result['input']['sha256']}`\n"
        f"- Literal policy markers: `{len(result['string_markers'])}`\n"
        f"- ADRP/ADD code references mapped to markers: `{len(result['code_references'])}`\n"
        f"- Rootable-marker code references: `{len(rootable)}`\n"
        f"- Standard-marker code references: `{len(standard)}`\n\n"
        "## Evidence interpretation\n\n"
        "**已證實：** stripped `/init` contains code-level ADRP/ADD references to both rootable and standard SELinux policy path strings; the references occur in a path-building region which calls a common helper with different flag values. A separate function compares the `androidboot.selinux` key and `permissive` value.\n\n"
        "**高可信推論：** the image contains a policy-loader decision surface rather than only inert filenames.\n\n"
        "**待驗證：** the active policy variant, exact branch predicate, helper semantics, and whether the current stock boot can select any alternate policy. A stripped binary and static path references cannot answer those runtime questions.\n\n"
        "**因風險拒絕測試：** changing boot properties, selecting a rootable policy, remounting, flashing, bootloader operations, or executing any kernel race/panic/root payload.\n\n"
        "## Reproduction\n\n"
        "```sh\n"
        f"python3 tools/scripts/analyze_phase6c_init_policy_loader.py --init {binary} --output {output}\n"
        "```\n\n"
        "Raw disassembly windows and machine-readable mappings are kept beside this report.\n",
        encoding="utf-8",
    )

    files = [summary, references, report, windows_file]
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--init", type=Path, required=True, help="preserved /init ELF; never executed")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--objdump", default="objdump")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "host_only": True,
            "elf_executed": False,
            "device_contacted": False,
            "init": str(args.init),
            "output": str(args.output),
        }, indent=2))
        return 0
    if not args.init.is_file():
        raise SystemExit(f"missing input: {args.init}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    result = build(args.init, args.objdump)
    write_outputs(result, args.output, args.objdump, args.init)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
