#!/usr/bin/env python3
"""Host-only inventory of PS7331 /init boot-property and cmdline surfaces.

The input is a preserved AArch64 ELF.  This tool maps literal markers to ELF
file offsets/VMAs and, where possible, to nearby ADRP/ADD references.  It does
not execute /init, read a device, change a boot property, select a policy,
invoke fastboot, or produce bootloader/property-mutation instructions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


MARKERS = (
    "/proc/cmdline",
    "proc/%d/cmdline",
    "androidboot.",
    "androidboot.selinux",
    "androidboot.seccomp",
    "androidboot.verifiedbootstate",
    "androidboot.flash.locked",
    "androidboot.unlocked_kernel",
    "androidboot.prod",
    "ro.boot.",
    "ro.boot.verifiedbootstate",
    "ro.boot.flash.locked",
    "ro.bootloader",
    "ro.bootmode",
    "ro.boot.mode",
    "ro.debuggable",
    "ro.secure",
    "permissive",
    "selinux",
    "rootable_",
    "rootable_fireos_sepolicy.cil",
    "/proc/idme/",
    "/sbin/recovery",
    "boot-recovery",
    "reboot,recovery",
    "/recovery",
    "/dev/sepolicy",
    "/vendor/etc/selinux/",
    "/system/etc/selinux/",
    "/odm/etc/selinux/",
    "verifiedbootstate",
    "flash.locked",
    "unlocked_kernel",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_tool(binary: str, args: list[str]) -> str:
    completed = subprocess.run(
        [binary, *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout


def parse_loads(program_headers: str) -> list[dict[str, int | str]]:
    loads: list[dict[str, int | str]] = []
    header = re.compile(
        r"^\s*LOAD\s+off\s+0x([0-9a-f]+)\s+"
        r"vaddr\s+0x([0-9a-f]+)\s+paddr\s+0x([0-9a-f]+)\s+"
        r"align\s+2\*\*(\d+)\s*$",
        re.IGNORECASE,
    )
    for line in program_headers.splitlines():
        match = header.match(line)
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
            sizes = re.search(
                r"filesz\s+0x([0-9a-f]+)\s+memsz\s+0x([0-9a-f]+)\s+"
                r"flags\s+([rwx-]+)",
                line,
                re.IGNORECASE,
            )
            if sizes and "filesz" not in loads[-1]:
                loads[-1].update(
                    {
                        "filesz": int(sizes.group(1), 16),
                        "memsz": int(sizes.group(2), 16),
                        "flags": sizes.group(3),
                    }
                )
    return loads


def vma_for_offset(loads: list[dict[str, int | str]], offset: int) -> tuple[int, int] | None:
    for index, load in enumerate(loads):
        file_offset = int(load["offset"])
        file_size = int(load.get("filesz", 0))
        if file_offset <= offset < file_offset + file_size:
            return index, int(load["vaddr"]) + offset - file_offset
    return None


def marker_class(marker: str) -> str:
    if "cmdline" in marker:
        return "cmdline_source"
    if marker.startswith("androidboot.") or marker.startswith("ro.boot"):
        return "boot_property"
    if marker in {"ro.debuggable", "ro.secure"}:
        return "security_property"
    if marker == "permissive" or marker == "selinux":
        return "selinux_policy_or_mode"
    if "rootable" in marker or "sepolicy" in marker or "selinux/" in marker:
        return "policy_path_or_variant"
    if marker in {"verifiedbootstate", "flash.locked", "unlocked_kernel"}:
        return "boot_integrity_or_lock_state"
    if marker in {"/proc/idme/", "/sbin/recovery", "boot-recovery", "reboot,recovery", "/recovery"}:
        return "boot_or_recovery_control"
    if marker == "/dev/sepolicy":
        return "policy_io"
    return "boot_related_literal"


def occurrences(data: bytes, marker: str) -> list[int]:
    needle = marker.encode("utf-8")
    found: list[int] = []
    cursor = 0
    while True:
        position = data.find(needle, cursor)
        if position < 0:
            return found
        found.append(position)
        cursor = position + 1


def parse_instructions(disassembly: str) -> list[dict[str, object]]:
    pattern = re.compile(r"^\s*([0-9a-f]+):\s+([0-9a-f ]+)\s+(.+?)\s*$", re.IGNORECASE)
    result: list[dict[str, object]] = []
    for line in disassembly.splitlines():
        match = pattern.match(line)
        if match:
            result.append(
                {
                    "address": int(match.group(1), 16),
                    "bytes": match.group(2).strip(),
                    "text": match.group(3),
                }
            )
    return result


def map_adrp_add_references(
    instructions: list[dict[str, object]], targets: dict[int, str]
) -> list[dict[str, object]]:
    adrp = re.compile(r"\badrp\s+x(\d+),\s*0x([0-9a-f]+)", re.IGNORECASE)
    add = re.compile(r"\badd\s+x(\d+),\s*x(\d+),\s*#0x([0-9a-f]+)", re.IGNORECASE)
    refs: list[dict[str, object]] = []
    for index, instruction in enumerate(instructions):
        match = adrp.search(str(instruction["text"]))
        if not match:
            continue
        register = int(match.group(1))
        page = int(match.group(2), 16)
        for candidate in instructions[index + 1 : index + 6]:
            add_match = add.search(str(candidate["text"]))
            if not add_match:
                continue
            if int(add_match.group(1)) != register or int(add_match.group(2)) != register:
                continue
            target = page + int(add_match.group(3), 16)
            if target in targets:
                refs.append(
                    {
                        "marker": targets[target],
                        "target_vma": f"0x{target:x}",
                        "adrp_address": f"0x{int(instruction['address']):x}",
                        "add_address": f"0x{int(candidate['address']):x}",
                        "register": f"x{register}",
                    }
                )
            break
    return refs


def nearby_call_targets(instructions: list[dict[str, object]], address: int) -> list[str]:
    calls: list[str] = []
    for instruction in instructions:
        distance = abs(int(instruction["address"]) - address)
        if distance > 0x60:
            continue
        text = str(instruction["text"])
        match = re.search(r"\bbl\s+0x([0-9a-f]+)", text, re.IGNORECASE)
        if match:
            calls.append(f"0x{int(match.group(1), 16):x}")
    return sorted(set(calls))


def build(binary: Path, objdump: str) -> dict[str, object]:
    data = binary.read_bytes()
    headers = run_tool(objdump, ["-p", str(binary)])
    loads = parse_loads(headers)
    if not loads or "filesz" not in loads[0]:
        raise SystemExit("could not parse ELF LOAD headers")

    marker_rows: list[dict[str, object]] = []
    target_vmas: dict[int, str] = {}
    for marker in MARKERS:
        for index, offset in enumerate(occurrences(data, marker)):
            mapped = vma_for_offset(loads, offset)
            row: dict[str, object] = {
                "marker": marker,
                "class": marker_class(marker),
                "occurrence": index,
                "file_offset": f"0x{offset:x}",
                "vma": "UNMAPPED",
                "load_segment": "UNMAPPED",
            }
            if mapped is not None:
                segment, vma = mapped
                row["vma"] = f"0x{vma:x}"
                row["load_segment"] = segment
                target_vmas[vma] = marker
            marker_rows.append(row)

    disassembly = run_tool(objdump, ["-d", str(binary)])
    instructions = parse_instructions(disassembly)
    references = map_adrp_add_references(instructions, target_vmas)
    for reference in references:
        reference["class"] = marker_class(str(reference["marker"]))
        reference["nearby_bl_targets"] = nearby_call_targets(
            instructions, int(str(reference["adrp_address"]), 16)
        )

    counts = Counter(str(row["class"]) for row in marker_rows)
    reference_counts = Counter(str(row["class"]) for row in references)
    return {
        "schema": "phase6d-init-property-cmdline-inventory-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {
            "path": str(binary),
            "sha256": sha256(binary),
            "objdump": shutil.which(objdump) or objdump,
            "elf_executed": False,
        },
        "program_headers": loads,
        "marker_count_by_class": dict(sorted(counts.items())),
        "reference_count_by_class": dict(sorted(reference_counts.items())),
        "markers": marker_rows,
        "adrp_add_references": references,
        "static_known_context": [
            {
                "address": "0x41bd60",
                "observation": "length/value comparisons around androidboot.selinux and permissive; existing disassembly window is retained as context",
                "status": "static_candidate_only",
            },
            {
                "address": "0x41ad00/0x41af80",
                "observation": "rootable and standard policy path-builder regions call a common helper with different w5 values",
                "status": "static_call-site_only",
            },
        ],
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "elf_executed": False,
            "boot_property_changed": False,
            "policy_selected": False,
            "fastboot_invoked": False,
            "bootloader_mutated": False,
            "kernel_memory_accessed": False,
            "exploit_or_root_payload": False,
        },
        "limits": [
            "A literal or ADRP/ADD reference does not prove that a property is read on the current boot.",
            "A stripped ELF does not expose source-level names, complete data-flow semantics, or the active policy variant.",
            "No property value, cmdline argument, bootloader mode, policy path, or SELinux transition was changed.",
        ],
    }


def write_outputs(result: dict[str, object], output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    summary = output / "property-cmdline-inventory.json"
    markers = output / "property-cmdline-markers.csv"
    references = output / "property-cmdline-adrp-add-references.csv"
    report = output / "result.md"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with markers.open("w", encoding="utf-8", newline="") as stream:
        fields = ["marker", "class", "occurrence", "file_offset", "vma", "load_segment"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in result["markers"])  # type: ignore[index]

    with references.open("w", encoding="utf-8", newline="") as stream:
        fields = ["marker", "class", "target_vma", "adrp_address", "add_address", "register", "nearby_bl_targets"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in result["adrp_add_references"]:  # type: ignore[index]
            record = dict(row)
            record["nearby_bl_targets"] = ",".join(record.get("nearby_bl_targets", []))
            writer.writerow({field: record.get(field, "") for field in fields})

    counts = result["marker_count_by_class"]
    ref_counts = result["reference_count_by_class"]
    report.write_text(
        "# PS7331 `/init` property/cmdline static inventory\n\n"
        "Host-only inventory of a preserved stripped AArch64 ELF. `/init` was not executed; no device, boot property, policy selection, fastboot, bootloader, kernel memory, or root payload was touched.\n\n"
        "## Input\n\n"
        f"- Input: `{result['input']['path']}`\n"
        f"- SHA-256: `{result['input']['sha256']}`\n"
        f"- Literal marker count: `{len(result['markers'])}`\n"
        f"- ADRP/ADD references mapped to markers: `{len(result['adrp_add_references'])}`\n\n"
        "## Marker classes\n\n"
        "| Class | Literal markers | Mapped ADRP/ADD references |\n|---|---:|---:|\n"
        + "".join(
            f"| `{category}` | {counts.get(category, 0)} | {ref_counts.get(category, 0)} |\n"
            for category in sorted(set(counts) | set(ref_counts))
        )
        + "\n## Interpretation\n\n"
        "**已證實：** the preserved `/init` contains literal surfaces for `/proc/cmdline`, `androidboot.*`/`ro.boot.*`, SELinux mode/policy names, recovery markers, boot-integrity markers, and rootable/standard policy paths. Some literals are reached by statically mapped AArch64 ADRP/ADD pairs.\n\n"
        "**高可信推論：** these strings are consistent with a boot-time property and policy-loader decision surface. The existing `0x41bd60` window contains the `androidboot.selinux`/`permissive` comparison candidate, while the `0x41ad00`/`0x41af80` windows contain rootable/standard path-builder call sites.\n\n"
        "**待驗證：** which callers execute on the stock boot, the exact property source/data-flow, the meaning of the stripped helper flag, and the active SELinux policy variant. Literal presence is not proof that a shell-writable property can select an alternate policy.\n\n"
        "**已排除：** this inventory does not support the claim that the device is rootable, that `androidboot.selinux=permissive` can be set from Android userspace, or that a rootable policy is active.\n\n"
        "**因風險拒絕測試：** boot-property mutation, cmdline injection, bootloader/fastboot selection, policy replacement, remount, image write, and any GhostLock trigger/race/panic/memory/root operation.\n\n"
        "## Reproduction\n\n"
        "```sh\n"
        f"python3 tools/scripts/inventory_phase6d_init_properties.py --dry-run --init {result['input']['path']} --output artifacts/phase6d/phase6d-init-property-inventory-YYYYMMDD-NN\n"
        f"python3 tools/scripts/inventory_phase6d_init_properties.py --init {result['input']['path']} --output artifacts/phase6d/phase6d-init-property-inventory-YYYYMMDD-NN\n"
        "```\n\n"
        "Machine-readable marker and reference tables are kept beside this report.\n",
        encoding="utf-8",
    )

    files = [summary, markers, references, report]
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
            "boot_property_changed": False,
            "fastboot_invoked": False,
            "output": str(args.output),
        }, indent=2))
        return 0
    if not args.init.is_file():
        raise SystemExit(f"missing input: {args.init}")
    result = build(args.init, args.objdump)
    write_outputs(result, args.output)
    print(json.dumps({
        "output": str(args.output),
        "marker_count": len(result["markers"]),
        "reference_count": len(result["adrp_add_references"]),
        "host_only": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
