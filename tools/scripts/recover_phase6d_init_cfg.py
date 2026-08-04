#!/usr/bin/env python3
"""Recover a conservative AArch64 CFG around the PS7331 `/init` loader.

This parser consumes host-side objdump text and emits basic-block/branch/call
edges. It is intentionally conservative: indirect branches, stripped symbol
names, and high-level policy semantics remain unresolved. The ELF is never
executed and the script never contacts a device.
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


LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(.+?)\s*$", re.IGNORECASE)
HEX_RE = re.compile(r"0x([0-9a-f]+)", re.IGNORECASE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_objdump(binary: Path, start: str, stop: str) -> str:
    return subprocess.run(
        ["objdump", "-d", f"--start-address={start}", f"--stop-address={stop}", str(binary)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def parse_instructions(text: str) -> list[dict[str, object]]:
    instructions = []
    for line in text.splitlines():
        match = LINE_RE.match(line)
        if match:
            instructions.append({"address": int(match.group(1), 16), "text": match.group(2), "raw": line})
    return instructions


def branch_target(text: str) -> int | None:
    if not re.match(r"^(?:b(?:\.[a-z]+)?|cbz|cbnz|tbz|tbnz)\b", text):
        return None
    # Bit-test branches contain an immediate such as `#0x0` before the target;
    # objdump then appends a `<.text+...>` annotation. The final hex literal
    # before that annotation is the actual branch target.
    prefix = text.split("<", 1)[0]
    matches = list(HEX_RE.finditer(prefix))
    return int(matches[-1].group(1), 16) if matches else None


def is_conditional_branch(text: str) -> bool:
    return bool(re.match(r"^(?:b\.[a-z]+|cbz|cbnz|tbz|tbnz)\b", text))


def is_unconditional_branch(text: str) -> bool:
    return bool(re.match(r"^b\s", text))


def block_model(instructions: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if not instructions:
        return [], []
    address_set = {int(item["address"]) for item in instructions}
    starts = {int(instructions[0]["address"])}
    for index, item in enumerate(instructions):
        text = str(item["text"])
        target = branch_target(text)
        if target in address_set:
            starts.add(target)
        if (is_conditional_branch(text) or is_unconditional_branch(text)) and index + 1 < len(instructions):
            starts.add(int(instructions[index + 1]["address"]))
    ordered = sorted(starts)
    blocks = []
    edges = []
    by_start = {start: index for index, start in enumerate(ordered)}
    for index, start in enumerate(ordered):
        end_limit = ordered[index + 1] if index + 1 < len(ordered) else None
        members = [item for item in instructions if int(item["address"]) >= start and (end_limit is None or int(item["address"]) < end_limit)]
        if not members:
            continue
        terminator = str(members[-1]["text"])
        block = {
            "id": f"B{start:x}",
            "start": f"0x{start:x}",
            "end": f"0x{int(members[-1]['address']):x}",
            "instruction_count": len(members),
            "terminator": terminator,
            "calls": [
                f"0x{int(match.group(1), 16):x}"
                for item in members
                for match in re.finditer(r"\bbl\s+0x([0-9a-f]+)", str(item["text"]), re.IGNORECASE)
            ],
        }
        blocks.append(block)
        last_index = instructions.index(members[-1])
        target = branch_target(terminator)
        if target in by_start:
            edges.append({"from": block["id"], "to": f"B{target:x}", "kind": "branch"})
        if (is_conditional_branch(terminator) or not target and not is_unconditional_branch(terminator)) and last_index + 1 < len(instructions):
            next_start = int(instructions[last_index + 1]["address"])
            if next_start in by_start:
                edges.append({"from": block["id"], "to": f"B{next_start:x}", "kind": "fallthrough"})
    return blocks, edges


def callsite_markers(instructions: list[dict[str, object]]) -> list[dict[str, object]]:
    markers = []
    for item in instructions:
        address = int(item["address"])
        text = str(item["text"])
        if address in (0x41ae44, 0x41af78, 0x41be48, 0x41ae5C, 0x41af80, 0x41c30c):
            markers.append({"address": f"0x{address:x}", "instruction": text, "role": "known_loader_landmark"})
        if re.search(r"\bbl\s+0x41be00\b", text):
            markers.append({"address": f"0x{address:x}", "instruction": text, "role": "call_common_helper_candidate"})
    return markers


def build(binary: Path, start: str, stop: str) -> tuple[dict[str, object], str]:
    disassembly = run_objdump(binary, start, stop)
    instructions = parse_instructions(disassembly)
    blocks, edges = block_model(instructions)
    result = {
        "schema": "phase6d-init-cfg-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {"binary": str(binary), "sha256": sha256(binary)},
        "range": {"start": start, "stop": stop},
        "instruction_count": len(instructions),
        "blocks": blocks,
        "edges": edges,
        "callsite_markers": callsite_markers(instructions),
        "limits": [
            "Indirect branches and stripped target semantics remain unresolved.",
            "A CFG edge does not prove the stock boot reaches that edge.",
            "Address labels are binary offsets, not original function names.",
        ],
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "elf_executed": False,
            "boot_property_changed": False,
            "policy_loaded": False,
            "kernel_memory_accessed": False,
            "root_payload": False,
        },
    }
    return result, disassembly


def write(result: dict[str, object], disassembly: str, output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    files = {
        "cfg": output / "cfg.json",
        "raw": output / "disassembly.txt",
        "blocks": output / "cfg-blocks.csv",
        "edges": output / "cfg-edges.csv",
        "markers": output / "callsite-markers.csv",
        "report": output / "result.md",
    }
    files["cfg"].write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files["raw"].write_text(disassembly, encoding="utf-8")
    with files["blocks"].open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["id", "start", "end", "instruction_count", "terminator", "calls"], lineterminator="\n")
        writer.writeheader()
        for block in result["blocks"]:
            row = dict(block)
            row["calls"] = ";".join(row["calls"])
            writer.writerow(row)
    with files["edges"].open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["from", "to", "kind"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["edges"])
    with files["markers"].open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["address", "instruction", "role"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["callsite_markers"])
    files["report"].write_text(
        "# PS7331 `/init` conservative CFG recovery\n\n"
        "This artifact is generated from host `objdump` output. The ELF was not\n"
        "executed and no device or boot state was touched.\n\n"
        f"The selected range contains **{result['instruction_count']}** parsed instructions,\n"
        f"**{len(result['blocks'])}** conservative blocks and **{len(result['edges'])}** explicit\n"
        "branch/fall-through edges.\n\n"
        "**已證實：** the parser recovers the known rootable/standard call sites and\n"
        "the `w5` branch target as instruction-level landmarks.\n\n"
        "**待驗證：** indirect calls, original symbols, active boot path, and the\n"
        "high-level meaning of the alternate branch.\n\n"
        "**因風險拒絕測試：** executing `/init`, changing boot properties, selecting\n"
        "policy variants, verification bypass, kernel-memory operations or root payloads.\n",
        encoding="utf-8",
    )
    manifest = output / "sha256sums.txt"
    manifest.write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files.values()) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--init-binary", type=Path, required=True)
    parser.add_argument("--start", default="0x41ad00")
    parser.add_argument("--stop", default="0x41d900")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False}, indent=2))
        return 0
    if not args.init_binary.is_file():
        raise SystemExit(f"missing /init binary: {args.init_binary}")
    result, disassembly = build(args.init_binary, args.start, args.stop)
    write(result, disassembly, args.output)
    print(f"wrote conservative /init CFG: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
