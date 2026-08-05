#!/usr/bin/env python3
"""Build a host-only function/call-site view of the PS7331 OTA updater.

The input is a preserved AArch64 disassembly plus the symbol table recovered
from the updater's embedded .gnu_debugdata.  This script parses text and
metadata only.  It never loads or executes update-binary, opens an OTA, calls
ADB, enters recovery, or writes a device path.

The report deliberately treats a direct call edge as a reachability hint, not
as proof that an attacker can supply the corresponding input or reach the
recovery process.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


FOCUS_TERMS = (
    "main",
    "RegisterInstallFunctions",
    "PackageExtractFileFn",
    "ExtractEntryToFile",
    "WriteToPartition",
    "PerformBlockImageUpdate",
    "BlockImageUpdateFn",
    "WipeBlockDeviceFn",
    "MakeFreeSpaceOnCache",
    "ota_open",
    "ota_read",
    "ota_write",
    "ota_close",
    "ota_fsync",
    "readlink",
    "readlinkat",
    "__readlink_chk",
    "open",
    "write",
    "pwrite",
    "realpath",
)

HEADING = re.compile(
    r"^===== (?P<label>\S+) (?P<name>.+) \[(?P<start>0x[0-9a-f]+),"
)
INSTRUCTION = re.compile(r"^\s*(?P<address>[0-9a-f]+):.*?\bbl\s+(?:#?0x)?(?P<target>[0-9a-f]+)", re.I)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_symbols(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            value = row.get("value") or row.get("address")
            if not value:
                continue
            try:
                start = int(value, 16)
                size = int(row.get("size", "0"))
            except ValueError:
                continue
            if size <= 0:
                continue
            # The newer extractor stores numeric ELF types; the older focus
            # extractor stores the literal FUNC label.  Both are acceptable.
            kind = row.get("type", "")
            if kind not in ("", "FUNC", "2"):
                continue
            name = row.get("name", "")
            if not name:
                continue
            rows.append({"name": name, "start": start, "stop": start + size, "size": size})
    return rows


def label_for(target: int, symbols: list[dict[str, object]]) -> str:
    candidates = [row for row in symbols if int(row["start"]) <= target < int(row["stop"])]
    if not candidates:
        return f"UNKNOWN_0x{target:x}"
    candidates.sort(key=lambda row: (int(row["stop"]) - int(row["start"]), str(row["name"])))
    return str(candidates[0]["name"])


def choose_focus(symbols: list[dict[str, object]]) -> list[dict[str, object]]:
    chosen: list[dict[str, object]] = []
    for term in FOCUS_TERMS:
        matches = [row for row in symbols if term.lower() in str(row["name"]).lower()]
        if not matches:
            continue
        matches.sort(key=lambda row: (
            0 if str(row["name"]) == term else
            1 if str(row["name"]).endswith(term) else 2,
            int(row["start"]),
        ))
        row = dict(matches[0])
        row["focus_term"] = term
        if not any(int(existing["start"]) == int(row["start"]) for existing in chosen):
            chosen.append(row)
    chosen.sort(key=lambda row: int(row["start"]))
    return chosen


def parse_direct_calls(disassembly: Path, focus: list[dict[str, object]], symbols: list[dict[str, object]]) -> list[dict[str, object]]:
    calls: list[dict[str, object]] = []
    text = disassembly.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        match = INSTRUCTION.match(line)
        if not match:
            continue
        address = int(match.group("address"), 16)
        target = int(match.group("target"), 16)
        callers = [row for row in focus if int(row["start"]) <= address < int(row["stop"])]
        if not callers:
            continue
        caller = callers[0]
        calls.append({
            "caller_term": str(caller["focus_term"]),
            "caller": str(caller["name"]),
            "callsite": f"0x{address:x}",
            "target": f"0x{target:x}",
            "callee": label_for(target, symbols),
        })
    return calls


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def mangle_node(value: str) -> str:
    return "N" + hashlib.sha1(value.encode()).hexdigest()[:10]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--disassembly", type=Path, required=True)
    parser.add_argument("--symbols", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for path in (args.disassembly, args.symbols):
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")
    if args.dry_run:
        print(json.dumps({
            "host_only": True,
            "device_contacted": False,
            "updater_executed": False,
            "operation": "parse symbol-guided direct AArch64 BL edges",
            "focus_terms": list(FOCUS_TERMS),
        }, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    symbols = load_symbols(args.symbols)
    focus = choose_focus(symbols)
    calls = parse_direct_calls(args.disassembly, focus, symbols)
    args.output.mkdir(parents=True)

    focus_rows = []
    for row in focus:
        focus_rows.append({
            "focus_term": row["focus_term"],
            "symbol": row["name"],
            "start": f"0x{int(row['start']):x}",
            "stop": f"0x{int(row['stop']):x}",
            "size": row["size"],
            "direct_call_count": sum(call["caller_term"] == row["focus_term"] for call in calls),
            "source": str(args.symbols),
        })
    write_csv(args.output / "focus-functions.csv", [
        "focus_term", "symbol", "start", "stop", "size", "direct_call_count", "source"
    ], focus_rows)
    write_csv(args.output / "direct-call-edges.csv", [
        "caller_term", "caller", "callsite", "target", "callee"
    ], calls)

    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for call in calls:
        grouped.setdefault((str(call["caller_term"]), str(call["callee"])), []).append(call)
    surface_names = {
        "open", "ota_open", "ota_write", "write", "pwrite", "ota_fsync", "ota_close",
        "readlink", "readlinkat", "__readlink_chk", "realpath", "ExtractEntryToFile",
    }
    surface_rows = []
    for (caller, callee), entries in sorted(grouped.items()):
        if caller not in FOCUS_TERMS and not any(name.lower() in callee.lower() for name in surface_names):
            continue
        surface_rows.append({
            "caller": caller,
            "callee": callee,
            "callsites": ",".join(str(entry["callsite"]) for entry in entries),
            "call_count": len(entries),
            "classification": (
                "path-open" if callee == "open" or callee.endswith("ota_openPKcij") else
                "file-write" if callee == "write" or "ota_write" in callee else
                "partition-sync" if "ota_fsync" in callee else
                "path-readlink" if "readlink" in callee else
                "archive-extract" if "ExtractEntryToFile" in callee else
                "other"
            ),
        })
    write_csv(args.output / "write-surface.csv", [
        "caller", "callee", "callsites", "call_count", "classification"
    ], surface_rows)

    nodes = sorted({str(row["caller_term"]) for row in calls} | {str(row["callee"]) for row in calls})
    graph = ["flowchart LR"]
    for node in nodes:
        graph.append(f'    {mangle_node(node)}["{node.replace(chr(34), chr(39))[:120]}"]')
    for caller, callee in sorted(grouped):
        graph.append(f"    {mangle_node(caller)} --> {mangle_node(callee)}")
    (args.output / "control-flow.mmd").write_text("\n".join(graph) + "\n", encoding="utf-8")

    summary = {
        "host_only": True,
        "device_contacted": False,
        "updater_executed": False,
        "recovery_executed": False,
        "partition_written": False,
        "disassembly": str(args.disassembly),
        "disassembly_sha256": sha256(args.disassembly),
        "symbols": str(args.symbols),
        "symbols_sha256": sha256(args.symbols),
        "focus_function_count": len(focus),
        "direct_call_count": len(calls),
        "unique_direct_edge_count": len(grouped),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "limitations": [
            "Only direct BL edges in the supplied text disassembly are mapped.",
            "Indirect calls, function-pointer dispatch and script data flow remain unresolved.",
            "A path-open edge is not proof of attacker-controlled input or recovery reachability.",
            "No updater, OTA, recovery, Binder transaction or device command was executed.",
        ],
    }
    summary_path = args.output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs = sorted(path for path in args.output.iterdir() if path.is_file())
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in outputs if path.name != "sha256sums.txt"),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
