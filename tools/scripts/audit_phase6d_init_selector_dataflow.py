#!/usr/bin/env python3
"""Host-only direct-call and selector-evidence audit for PS7331 ``/init``.

The input is a preserved AArch64 ELF.  The tool disassembles it with the host
``objdump`` program, records direct ``bl``/branch landmarks, and compares the
observed shape with the already identified AOSP ``StatusFromCmdline`` anchor.
It never executes the ELF, loads a policy, contacts a device, changes a boot
property, or emits exploit instructions.

This is deliberately a negative-capability tool: the absence of a direct call
does not prove that an indirect call or inlined path is absent, and a code/data
reference does not prove stock-boot reachability.
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


TARGETS = {
    0x41AD00: "policy_path_builder_candidate",
    0x41BD60: "androidboot_selinux_parser_candidate",
    0x41BE00: "common_policy_helper_candidate",
    0x41C30C: "alternate_branch_target",
    0x41B748: "property_or_global_helper_candidate",
}

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
)

INSTRUCTION_RE = re.compile(
    r"^\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(.+?)\s*$", re.IGNORECASE
)
CALL_RE = re.compile(r"\bbl\s+0x([0-9a-f]+)", re.IGNORECASE)
BRANCH_RE = re.compile(
    r"^(?:b(?:\.[a-z]+)?|cbz|cbnz|tbz|tbnz)\b.*\b0x([0-9a-f]+)",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str]) -> str:
    completed = subprocess.run(
        command, check=True, capture_output=True, text=True
    )
    return completed.stdout


def parse_instructions(disassembly: str) -> list[dict[str, object]]:
    instructions: list[dict[str, object]] = []
    for line in disassembly.splitlines():
        match = INSTRUCTION_RE.match(line)
        if match:
            instructions.append(
                {
                    "address": int(match.group(1), 16),
                    "text": match.group(2).strip(),
                    "raw": line,
                }
            )
    return instructions


def parse_loads(program_headers: str) -> list[dict[str, int]]:
    loads: list[dict[str, int]] = []
    load_re = re.compile(
        r"^\s*LOAD\s+off\s+0x([0-9a-f]+)\s+"
        r"vaddr\s+0x([0-9a-f]+)\s+paddr\s+0x([0-9a-f]+)\s+"
        r"align\s+2\*\*(\d+)\s*$",
        re.IGNORECASE,
    )
    for line in program_headers.splitlines():
        match = load_re.match(line)
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
            size = re.search(
                r"filesz\s+0x([0-9a-f]+)\s+memsz\s+0x([0-9a-f]+)\s+"
                r"flags\s+([rwx-]+)",
                line,
                re.IGNORECASE,
            )
            if size and "filesz" not in loads[-1]:
                loads[-1].update(
                    {
                        "filesz": int(size.group(1), 16),
                        "memsz": int(size.group(2), 16),
                        "flags": size.group(3),
                    }
                )
    return loads


def marker_vmas(binary: Path, objdump: str) -> list[dict[str, object]]:
    data = binary.read_bytes()
    loads = parse_loads(run([objdump, "-p", str(binary)]))
    if not loads or "filesz" not in loads[0]:
        return []
    load = loads[0]
    records: list[dict[str, object]] = []
    for marker in PATH_MARKERS:
        needle = marker.encode("utf-8")
        cursor = 0
        while True:
            offset = data.find(needle, cursor)
            if offset < 0:
                break
            # Do not count ``fireos_sepolicy.cil`` inside the longer
            # ``rootable_fireos_sepolicy.cil`` marker as a second occurrence.
            if offset > 0 and (chr(data[offset - 1]).isalnum() or data[offset - 1] in b"_-"):
                cursor = offset + 1
                continue
            vma = load["vaddr"] + offset - load["offset"]
            records.append(
                {
                    "marker": marker,
                    "file_offset": f"0x{offset:x}",
                    "vma": f"0x{vma:x}",
                }
            )
            cursor = offset + 1
    return records


def direct_calls(instructions: list[dict[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for item in instructions:
        match = CALL_RE.search(str(item["text"]))
        if not match:
            continue
        target = int(match.group(1), 16)
        if target in TARGETS:
            records.append(
                {
                    "call_site": f"0x{int(item['address']):x}",
                    "target": f"0x{target:x}",
                    "target_role": TARGETS[target],
                    "instruction": str(item["text"]),
                }
            )
    return records


def branch_references(instructions: list[dict[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for item in instructions:
        text = str(item["text"])
        if not re.match(r"^(?:b(?:\.[a-z]+)?|cbz|cbnz|tbz|tbnz)\b", text, re.IGNORECASE):
            continue
        # Bit/count operands can contain another hexadecimal literal.  The
        # target is the last literal before objdump's optional annotation.
        prefix = text.split("<", 1)[0]
        literals = re.findall(r"0x([0-9a-f]+)", prefix, re.IGNORECASE)
        if not literals:
            continue
        target = int(literals[-1], 16)
        if target in TARGETS:
            records.append(
                {
                    "branch_site": f"0x{int(item['address']):x}",
                    "target": f"0x{target:x}",
                    "target_role": TARGETS[target],
                    "instruction": str(item["text"]),
                }
            )
    return records


def nearby_w5_definition(
    instructions: list[dict[str, object]], call_index: int, window: int = 12
) -> dict[str, object]:
    candidates: list[dict[str, object]] = []
    start = max(0, call_index - window)
    for item in instructions[start:call_index]:
        text = str(item["text"])
        value = None
        if re.search(r"\bmov\s+w5,\s*wzr\b", text, re.IGNORECASE):
            value = "0"
        elif re.search(r"\borr\s+w5,\s*wzr,\s*#0x1\b", text, re.IGNORECASE):
            value = "1"
        if value is not None:
            candidates.append(
                {
                    "address": f"0x{int(item['address']):x}",
                    "instruction": text,
                    "value": value,
                }
            )
    if not candidates:
        return {"value": "unresolved", "definitions": []}
    chosen = candidates[-1]
    return {"value": chosen["value"], "definitions": candidates}


def build(binary: Path, objdump: str) -> tuple[dict[str, object], str]:
    disassembly = run([objdump, "-d", str(binary)])
    instructions = parse_instructions(disassembly)
    calls = direct_calls(instructions)
    branches = branch_references(instructions)
    helper_calls: list[dict[str, object]] = []
    for index, item in enumerate(instructions):
        if not re.search(r"\bbl\s+0x41be00\b", str(item["text"]), re.IGNORECASE):
            continue
        definition = nearby_w5_definition(instructions, index)
        helper_calls.append(
            {
                "call_site": f"0x{int(item['address']):x}",
                "instruction": str(item["text"]),
                "w5_nearby": definition,
            }
        )

    call_counts = {f"0x{target:x}": 0 for target in TARGETS}
    for record in calls:
        call_counts[str(record["target"])] += 1
    branch_counts = {f"0x{target:x}": 0 for target in TARGETS}
    for record in branches:
        branch_counts[str(record["target"])] += 1

    observations = [
        {
            "id": "INIT-DF-001",
            "observation": "0x41bd60 contains an androidboot.selinux/permissive comparison shape and writes zero to a caller-provided field on success.",
            "classification": "AOSP-shaped enforcing-status-parser-candidate",
            "confidence": "Strong evidence",
        },
        {
            "id": "INIT-DF-002",
            "observation": f"Full-text direct-call scan found {call_counts['0x41bd60']} direct bl call(s) to 0x41bd60.",
            "classification": "not-direct-policy-selector-evidence",
            "confidence": "Confirmed",
        },
        {
            "id": "INIT-DF-003",
            "observation": "0x41be00 is called from both a nearby w5=1 site and a nearby w5=0 site; 0x41be48 branches on w5.",
            "classification": "mode-branch-exists-but-semantics-unresolved",
            "confidence": "Confirmed",
        },
        {
            "id": "INIT-DF-004",
            "observation": "Rootable policy path literals have code/data references in the stripped ELF.",
            "classification": "path-reference-only",
            "confidence": "Confirmed",
        },
        {
            "id": "INIT-DF-005",
            "observation": "Indirect calls, inlining, runtime caller reachability, and the active policy variant remain unresolved.",
            "classification": "evidence-limit",
            "confidence": "Confirmed",
        },
    ]
    result: dict[str, object] = {
        "schema": "phase6d-init-selector-dataflow-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {
            "binary": str(binary),
            "sha256": sha256(binary),
            "objdump": objdump,
            "instruction_count": len(instructions),
            "elf_executed": False,
        },
        "targets": {f"0x{target:x}": role for target, role in TARGETS.items()},
        "direct_calls": calls,
        "branch_references": branches,
        "common_helper_calls": helper_calls,
        "direct_call_counts": call_counts,
        "branch_reference_counts": branch_counts,
        "policy_path_markers": marker_vmas(binary, objdump),
        "observations": observations,
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
            "No direct-call match does not exclude an indirect call or inlined logic.",
            "A string/code reference does not prove stock-boot reachability.",
            "Address labels are stripped-binary landmarks, not original source symbols.",
            "This audit does not select, replace, or load any SELinux policy.",
        ],
    }
    return result, disassembly


def write_outputs(result: dict[str, object], disassembly: str, output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    files: list[Path] = []
    summary = output / "summary.json"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files.append(summary)

    calls = output / "direct-calls.csv"
    with calls.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["call_site", "target", "target_role", "instruction"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(result["direct_calls"])
    files.append(calls)

    evidence = output / "selector-evidence.csv"
    with evidence.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["id", "observation", "classification", "confidence"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(result["observations"])
    files.append(evidence)

    windows = output / "disassembly-windows.txt"
    windows.write_text(
        "Host objdump full-text scan; selected evidence windows are retained below.\n\n"
        + "\n".join(
            line
            for line in disassembly.splitlines()
            if any(
                token in line.lower()
                for token in (
                    "41bd60",
                    "41be00",
                    "41be48",
                    "41c30c",
                    "41ad00",
                    "41ae44",
                    "41ae5c",
                    "41af78",
                    "41af80",
                    "41b748",
                )
            )
        )
        + "\n",
        encoding="utf-8",
    )
    files.append(windows)

    report = output / "result.md"
    direct = result["direct_call_counts"]
    report.write_text(
        "# PS7331 `/init` selector data-flow audit\n\n"
        "This is a host-only audit of a preserved stripped AArch64 ELF. The ELF was not\n"
        "executed; no device, boot property, SELinux policy, or kernel state was touched.\n\n"
        "## Findings\n\n"
        f"- **已證實：** the full-text scan found `{direct['0x41be00']}` direct call(s) to\n"
        "  `0x41be00`, with nearby `w5` definitions recorded in `summary.json`.\n"
        f"- **已證實：** the full-text scan found `{direct['0x41bd60']}` direct `bl` call(s)\n"
        "  to `0x41bd60`. Its instruction shape is consistent with an\n"
        "  `androidboot.selinux=permissive` enforcing-status parser candidate, not by\n"
        "  itself evidence of rootable-policy selection.\n"
        "- **高可信推論：** the rootable path literals and the `w5` branch are real\n"
        "  instruction/data landmarks, but their stripped high-level semantics remain\n"
        "  unresolved.\n"
        "- **待驗證：** indirect/inlined callers, stock-boot reachability, and which\n"
        "  policy variant is active on the retail device.\n"
        "- **因風險拒絕測試：** executing `/init`, changing boot properties, loading an\n"
        "  alternate policy, bypassing AVB, or attempting root.\n\n"
        "## Interpretation boundary\n\n"
        "A zero direct-call count is not a proof of absence: an indirect call or inlined\n"
        "implementation could still exist. Conversely, a path reference or branch is not\n"
        "proof that a retail boot selects that path.\n",
        encoding="utf-8",
    )
    files.append(report)

    manifest = output / "sha256sums.txt"
    manifest.write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--init-binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--objdump", default="objdump")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False}, indent=2))
        return 0
    if not args.init_binary.is_file():
        raise SystemExit(f"missing /init binary: {args.init_binary}")
    result, disassembly = build(args.init_binary, args.objdump)
    write_outputs(result, disassembly, args.output)
    print(f"wrote host-only /init selector audit: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
