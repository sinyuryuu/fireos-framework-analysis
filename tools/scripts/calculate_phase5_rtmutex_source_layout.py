#!/usr/bin/env python3
"""Calculate a bounded Linux 4.4 rt_mutex_waiter source layout.

This is a host-only source/ABI check. It deliberately does not parse a boot
image, recover symbols, calculate KASLR, generate exploit headers, communicate
with a device, or execute kernel code. The schema is a version-pinned summary
of the public Linux v4.4.146 declaration and the input config must be supplied
by the caller.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, NoReturn


def die(message: str) -> NoReturn:
    raise SystemExit(f"ERROR: {message}")


def parse_config(path: Path) -> dict[str, bool | None]:
    values: dict[str, bool | None] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or (line.startswith("#") and " is not set" not in line):
            continue
        match = re.fullmatch(r"CONFIG_([A-Za-z0-9_]+)=(.*)", line)
        if match:
            values[f"CONFIG_{match.group(1)}"] = match.group(2) == "y"
            continue
        match = re.fullmatch(r"# (CONFIG_[A-Za-z0-9_]+) is not set", line)
        if match:
            values[match.group(1)] = False
    return values


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def kind_size(kind: str, pointer_size: int) -> tuple[int, int]:
    if kind == "rb_node":
        # Linux 4.4 rb_node: parent/color plus right and left pointers.
        return 3 * pointer_size, pointer_size
    if kind == "pointer":
        return pointer_size, pointer_size
    if kind == "int":
        return 4, 4
    die(f"unsupported schema field kind: {kind}")


def calculate(schema: dict[str, Any], config: dict[str, bool | None],
              config_path: Path, pointer_size: int) -> dict[str, Any]:
    required = ["CONFIG_ARM64", "CONFIG_RT_MUTEXES", "CONFIG_FUTEX"]
    config_observations = {
        key: config.get(key) for key in required + [
            "CONFIG_DEBUG_RT_MUTEXES",
            "CONFIG_RANDOMIZE_BASE",
            "CONFIG_KALLSYMS",
            "CONFIG_KALLSYMS_ALL",
            "CONFIG_ARM64_4K_PAGES",
            "CONFIG_ARM64_VA_BITS_39",
        ]
    }
    missing = [key for key in required if config.get(key) is None]
    if missing:
        die("required config keys are absent: " + ", ".join(missing))
    if not all(config[key] for key in required):
        die("config does not enable ARM64 + RT_MUTEXES + FUTEX")

    offset = 0
    max_alignment = 1
    fields: list[dict[str, Any]] = []
    for field in schema["layout"]["fields"]:
        guard = field.get("guard")
        if guard and config.get(guard) is not True:
            fields.append({
                "name": field["name"],
                "guard": guard,
                "included": False,
                "reason": "guard is not enabled in supplied config",
            })
            continue
        size, alignment = kind_size(field["kind"], pointer_size)
        offset = align_up(offset, alignment)
        fields.append({
            "name": field["name"],
            "kind": field["kind"],
            "guard": guard,
            "included": True,
            "offset": offset,
            "offset_hex": hex(offset),
            "size": size,
            "size_hex": hex(size),
            "alignment": alignment,
        })
        offset += size
        max_alignment = max(max_alignment, alignment)

    size = align_up(offset, max_alignment)
    return {
        "schema_id": schema["schema_id"],
        "source": schema["source"],
        "input": {
            "config_observations": config_observations,
            "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
            "pointer_size": pointer_size,
            "abi": "AArch64 LP64" if pointer_size == 8 else "generic pointer ABI",
        },
        "calculation": {
            "object": "struct rt_mutex_waiter",
            "source_level_only": True,
            "fields": fields,
            "sizeof": size,
            "sizeof_hex": hex(size),
            "max_alignment": max_alignment,
        },
        "not_calculated": schema["scope"]["does_not_calculate"],
        "interpretation": (
            "These are source/ABI layout facts for the pinned v4.4 declaration. "
            "They are not runtime kernel addresses and are not sufficient to "
            "construct or execute an exploit."
        ),
    }


def write_outputs(output: Path, result: dict[str, Any], command: str) -> None:
    if output.exists():
        die(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    (output / "commands.txt").write_text(command + "\n", encoding="utf-8")
    (output / "layout.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    rows = [
        "# Source-derived rt_mutex_waiter layout",
        "",
        f"- Object: `{result['calculation']['object']}`",
        f"- `sizeof`: `{result['calculation']['sizeof_hex']}`",
        f"- Pointer size: `{result['input']['pointer_size']}`",
        "- Scope: source/ABI layout only; no runtime addresses or exploit header",
        "",
        "| Field | Included | Offset | Size |",
        "|---|---:|---:|---:|",
    ]
    for field in result["calculation"]["fields"]:
        rows.append(
            f"| `{field['name']}` | {field['included']} | "
            f"{field.get('offset_hex', 'N/A')} | {field.get('size_hex', 'N/A')} |"
        )
    (output / "result.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    manifest_lines = []
    for path in sorted(output.iterdir()):
        if path.name == "sha256sums.txt":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_lines.append(f"{digest}  {path.name}")
    (output / "sha256sums.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="captured kernel .config text")
    parser.add_argument("--schema", required=True, help="version-pinned layout schema JSON")
    parser.add_argument("--pointer-size", required=True, type=int, choices=(4, 8))
    parser.add_argument("--output", required=True, help="new output directory")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config)
    schema_path = Path(args.schema)
    if not config_path.is_file() or not schema_path.is_file():
        die("config and schema must be readable regular files")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    config = parse_config(config_path)
    if args.dry_run:
        print("DRY-RUN: no output written; no device or executable code involved.")
        print(f"Would read config={config_path} schema={schema_path} pointer_size={args.pointer_size}")
        return 0
    result = calculate(schema, config, config_path, args.pointer_size)
    command = " ".join(sys.argv)
    write_outputs(Path(args.output), result, command)
    print(json.dumps(result["calculation"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
