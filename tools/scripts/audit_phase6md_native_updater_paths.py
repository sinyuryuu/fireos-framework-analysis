#!/usr/bin/env python3
"""Audit the PS7331 native OTA updater's path/write call edges offline.

This tool correlates an immutable updater binary hash, its embedded-debugdata
symbol index, a previously generated direct-BL edge table, strings, and the
official updater-script.  It never executes the updater, opens an OTA package,
contacts a device, sends a recovery command, or writes a partition.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_CALLS = ("block_image_update", "package_extract_file", "run_program")
PARTITION_RE = re.compile(r"/dev/block/[^\"')\s]+")
QUOTED_RE = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')

CALLEE_CLASSES = {
    "ota_open": "open-wrapper",
    "open": "open-sink",
    "open64": "open-sink",
    "__open_2": "open-sink",
    "__openat_2": "openat-sink",
    "openat": "openat-sink",
    "ota_write": "write-wrapper",
    "write": "write-sink",
    "rename": "rename-sink",
    "renameat": "rename-sink",
    "chown": "metadata-mutation",
    "fchown": "metadata-mutation",
    "fchownat": "metadata-mutation",
    "chmod": "metadata-mutation",
    "fchmod": "metadata-mutation",
    "fchmodat": "metadata-mutation",
    "readlink": "path-canonicalization-candidate",
    "readlinkat": "path-canonicalization-candidate",
    "__readlink_chk": "path-canonicalization-candidate",
    "realpath": "path-canonicalization-candidate",
    "symlink_realpath": "path-canonicalization-candidate",
    "ExtractEntryToFile": "zip-extraction",
    "ExtractToMemory": "zip-extraction",
    "PackageExtractFileFn": "install-handler",
    "PerformBlockImageUpdate": "block-image-handler",
    "WriteToPartition": "partition-write-handler",
    "RegisterInstallFunctions": "handler-registration",
    "RegisterBlockImageFunction": "handler-registration",
}

STRING_MARKERS = (
    "symlink_realpath",
    "readlinkat",
    "readlink",
    "realpath",
    "run_program",
    "package_extract_file",
    "block_image_update",
    "verify",
    "sha256",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_edges(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def parse_symbols(path: Path) -> dict[int, str]:
    names: dict[int, str] = {}
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row.get("type") != "FUNC" or not row.get("name") or not row.get("address"):
                continue
            try:
                names[int(row["address"], 16)] = row["name"]
            except ValueError:
                continue
    return names


def classify_callee(callee: str) -> str | None:
    if callee in CALLEE_CLASSES:
        return CALLEE_CLASSES[callee]
    # Only use long, distinctive tokens for mangled C++ names.  A suffix
    # match for the short token "open" would misclassify fdopen/fopen.
    mangled_tokens = {
        name for name in CALLEE_CLASSES
        if len(name) >= 8 or name in {"ota_open", "ota_write"}
    }
    for name in mangled_tokens:
        category = CALLEE_CLASSES[name]
        if name in callee:
            return category
    return None


def parse_script(path: Path) -> tuple[list[dict[str, object]], list[str]]:
    rows: list[dict[str, object]] = []
    targets: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        matched = [call for call in SCRIPT_CALLS if f"{call}(" in line]
        if not matched:
            continue
        call = matched[0]
        quoted = [value.replace('\\"', '"') for value in QUOTED_RE.findall(line)]
        line_targets = PARTITION_RE.findall(line)
        targets.extend(line_targets)
        rows.append({
            "line": line_number,
            "operation": call,
            "quoted_arguments": " | ".join(quoted),
            "partition_targets": " | ".join(line_targets),
            "text": line.strip(),
        })
    return rows, sorted(set(targets))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--symbols", type=Path, required=True)
    parser.add_argument("--edges", type=Path, required=True)
    parser.add_argument("--strings", type=Path, required=True)
    parser.add_argument("--disassembly", type=Path, required=True)
    parser.add_argument("--updater-script", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.binary, args.symbols, args.edges, args.strings, args.disassembly, args.updater_script]
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "host_only": True,
            "device_contacted": False,
            "updater_executed": False,
            "partition_written": False,
            "inputs": [str(path) for path in inputs],
            "output": str(args.output),
        }, indent=2))
        return 0
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise SystemExit("missing input files:\n" + "\n".join(missing))
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    edges = parse_edges(args.edges)
    symbols_by_address = parse_symbols(args.symbols)
    selected: list[dict[str, str]] = []
    for edge in edges:
        category = classify_callee(edge.get("callee", ""))
        try:
            resolved_callee = symbols_by_address.get(int(edge.get("target_address", "0"), 16), "")
        except ValueError:
            resolved_callee = ""
        if category is None:
            category = classify_callee(resolved_callee)
        if category is None:
            continue
        selected.append({
            "caller_label": edge.get("caller_label", ""),
            "caller": edge.get("caller", ""),
            "instruction": edge.get("instruction", ""),
            "target_address": edge.get("target_address", ""),
            "callee": edge.get("callee", ""),
            "callee_resolved": resolved_callee,
            "classification": category,
            "callee_is_symbolized": str(bool(resolved_callee)).lower(),
        })

    string_rows: list[dict[str, object]] = []
    for line_number, line in enumerate(args.strings.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        lower = line.lower()
        matches = [marker for marker in STRING_MARKERS if marker.lower() in lower]
        if matches:
            string_rows.append({"line": line_number, "markers": ";".join(matches), "text": line.strip()})

    script_rows, partition_targets = parse_script(args.updater_script)
    args.output.mkdir(parents=True)
    edge_path = args.output / "path-write-call-edges.csv"
    edge_fields = ["caller_label", "caller", "instruction", "target_address", "callee", "callee_resolved", "classification", "callee_is_symbolized"]
    with edge_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=edge_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(selected)

    string_path = args.output / "path-marker-strings.csv"
    with string_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["line", "markers", "text"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(string_rows)

    script_path = args.output / "updater-script-operations.csv"
    with script_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["line", "operation", "quoted_arguments", "partition_targets", "text"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(script_rows)

    direct_path_guard_edges = [row for row in selected if row["classification"] == "path-canonicalization-candidate"]
    direct_write_edges = [row for row in selected if row["classification"] in {"open-wrapper", "open-sink", "openat-sink", "write-wrapper", "write-sink", "rename-sink", "partition-write-handler"}]
    summary = {
        "phase": "6MD",
        "analysis": "host-only native OTA updater path/write correlation",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "updater_executed": False,
        "recovery_executed": False,
        "partition_written": False,
        "inputs": {str(path): sha256(path) for path in inputs},
        "selected_edge_count": len(selected),
        "direct_path_guard_edge_count": len(direct_path_guard_edges),
        "direct_write_edge_count": len(direct_write_edges),
        "path_marker_string_count": len(string_rows),
        "updater_script_operation_count": len(script_rows),
        "updater_script_partition_targets": partition_targets,
        "observations": {
            "partition_write_handler_present": any(row["caller_label"] == "WriteToPartition" for row in selected),
            "extract_path_reaches_ota_open": any(row["caller_label"] == "PackageExtractFileFn" and "ota_open" in row["callee_resolved"] for row in selected),
            "extract_path_reaches_file_extraction": any(row["caller_label"] == "PackageExtractFileFn" and row["classification"] == "zip-extraction" for row in selected),
            "block_update_has_open_rename_or_chown": any(row["caller_label"] == "PerformBlockImageUpdate" and row["classification"] in {"open-sink", "open-wrapper", "rename-sink", "metadata-mutation"} for row in selected),
            "direct_canonicalization_edge_in_selected_graph": bool(direct_path_guard_edges),
            "canonicalization_strings_present": any("symlink_realpath" in row["markers"] or "readlink" in row["markers"] for row in string_rows),
            "low_privilege_entry_proven": False,
        },
        "interpretation": [
            "The updater has symbolized privileged extraction and partition-write sinks.",
            "Path canonicalization names are present in the binary strings, but no direct path-canonicalization edge was found in the selected direct-BL graph.",
            "This is not proof that no indirect call or unselected function performs canonicalization; complete CFG/dataflow remains unresolved.",
            "The updater-script explicitly targets protected block-device paths; it is not an ADB-level launcher selector.",
        ],
        "rejected_operations": [
            "Executing update-binary or recovery",
            "Sending or modifying OTA packages",
            "Symlink/path-traversal or malformed-input testing",
            "Fastboot, sideload, partition write, or device mutation",
        ],
    }
    summary_path = args.output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    graph = ["flowchart LR", "    Script[\"updater-script\"] --> Extract[\"package_extract_file\"]", "    Script --> Block[\"block_image_update\"]", "    Extract --> ExtractFn[\"PackageExtractFileFn\"]", "    Block --> BlockFn[\"PerformBlockImageUpdate\"]", "    ExtractFn --> Open[\"ota_open / open\"]", "    ExtractFn --> Zip[\"ExtractEntryToFile\"]", "    BlockFn --> Open", "    BlockFn --> Rename[\"rename\"]", "    BlockFn --> Chown[\"chown\"]", "    Write[\"WriteToPartition\"] --> Open", "    Write --> WriteSink[\"ota_write / write\"]", "    Guard[\"readlink/readlinkat/realpath markers\"] -.\"no direct edge in selected graph\".-> Open"]
    (args.output / "path-write-flow.mmd").write_text("\n".join(graph) + "\n", encoding="utf-8")

    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps(summary["observations"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
