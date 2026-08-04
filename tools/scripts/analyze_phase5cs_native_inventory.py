#!/usr/bin/env python3
"""Audit selected Fire/Amazon native artifacts without executing them.

This is deliberately a host-only analyzer.  It reads an existing read-only
capture, invokes host ``file``, ``strings``, ``nm`` and ``objdump -t`` on the
pulled ELF files, and emits a bounded inventory.  It never contacts ADB,
loads an ELF, invokes a syscall, opens a device node, or generates a kernel
address/payload.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SELECTED = [
    "libAmazon_tat_jni.so",
    "libamazon_remotes.so",
    "libamazonaspservice.so",
    "libamazonmediaanalytica.so",
    "libamazonwifiservice.so",
    "libandroid_runtime.so",
    "libart.so",
    "libbinder.so",
    "libcutils.so",
    "libutils.so",
]

TOKENS = (
    "futex",
    "pthread_cond",
    "pthread_mutex",
    "requeue",
    "rtmutex",
    "seccomp",
    "syscall",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def host_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"required host tool not found: {name}")
    return path


def run_host(*args: str) -> str:
    result = subprocess.run(
        list(args), check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"host command failed ({result.returncode}): {' '.join(args)}")
    return result.stdout


def relevant_lines(text: str) -> list[str]:
    return sorted({
        line.strip() for line in text.splitlines()
        if any(token in line.lower() for token in TOKENS)
    })


def symbol_names(nm_text: str) -> list[str]:
    names: list[str] = []
    for line in nm_text.splitlines():
        match = re.match(r"^\s*(?:[0-9a-fA-F]+|U)\s+\S\s+(.+)$", line)
        if match:
            name = match.group(1).strip()
            if any(token in name.lower() for token in TOKENS):
                names.append(name)
    return sorted(set(names))


def classify(name: str, strings: list[str], symbols: list[str]) -> tuple[str, str]:
    all_text = "\n".join(strings + symbols).lower()
    if name == "libart.so" and "futex cmp requeue failed for" in all_text:
        return (
            "ordinary compare-requeue marker in ART; syscall boundary present",
            "Confirmed, binary scope",
        )
    if name == "libandroid_runtime.so" and "seccomp" in all_text:
        return (
            "ART/runtime seccomp setup references and pthread condition symbols",
            "Confirmed, binary scope",
        )
    if name in {"libbinder.so", "libutils.so"} and "pthread_cond" in all_text:
        return ("ordinary pthread condition synchronization references", "Confirmed, bounded scope")
    if name == "libcutils.so" and "syscall" in all_text:
        return ("syscall reference; futex operation not identified", "Confirmed, bounded scope")
    if not strings and not symbols:
        return ("no relevant named token in bounded scan", "Negative observation only")
    if not any(token in all_text for token in ("futex", "requeue", "rtmutex")):
        return ("no futex/requeue/rtmutex token in bounded scan", "Negative observation only")
    return ("relevant synchronization token; call semantics not established", "Needs manual review")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY-RUN: no ELF is read and no files are written.")
        print(f"CAPTURE_DIR\t{args.capture_dir}")
        print(f"OUTPUT\t{args.output}")
        return 0
    if not args.capture_dir.is_dir():
        print("ERROR: --capture-dir must be a directory", file=sys.stderr)
        return 2
    if args.output.exists():
        print(f"ERROR: refusing to overwrite output: {args.output}", file=sys.stderr)
        return 2

    try:
        for tool in ("file", "strings", "nm", "objdump"):
            host_tool(tool)
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    files_dir = args.capture_dir / "files"
    rows: list[dict[str, object]] = []
    command_log: list[str] = []
    libart_disassembly = ""
    for name in SELECTED:
        path = files_dir / name
        if not path.is_file():
            rows.append({
                "artifact": name,
                "path": str(path),
                "sha256": "MISSING",
                "file_description": "MISSING",
                "strings": [],
                "symbols": [],
                "classification": "not captured",
                "confidence": "Unknown",
            })
            continue
        file_text = run_host("file", str(path))
        strings_text = run_host("strings", str(path))
        nm_text = run_host("nm", "-a", str(path))
        objdump_text = run_host("objdump", "-t", str(path))
        command_log.extend([
            f"file {path}",
            f"strings {path}",
            f"nm -a {path}",
            f"objdump -t {path}",
        ])
        if name == "libart.so":
            symbol = "_ZN3art10ThreadList18SuspendAllInternalEPNS_6ThreadES2_S2_NS_13SuspendReasonE"
            libart_disassembly = run_host(
                "objdump", "-d", "--start-address=0x4acf88",
                "--stop-address=0x4ad4e8", str(path)
            )
            command_log.append(
                f"objdump -d --start-address=0x4acf88 --stop-address=0x4ad4e8 {path}"
            )
        string_hits = relevant_lines(strings_text)
        symbols = symbol_names(nm_text + "\n" + objdump_text)
        classification, confidence = classify(name, string_hits, symbols)
        rows.append({
            "artifact": name,
            "path": str(path),
            "sha256": sha256(path),
            "file_description": file_text.strip(),
            "strings": string_hits,
            "symbols": symbols,
            "classification": classification,
            "confidence": confidence,
        })

    args.output.mkdir(parents=True)
    (args.output / "analysis.json").write_text(
        json.dumps({
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "host_only": True,
            "device_contacted": False,
            "capture_dir": str(args.capture_dir),
            "rows": rows,
            "safety": {
                "elf_executed": False,
                "syscall_invoked": False,
                "device_node_opened": False,
                "kernel_memory_access": False,
                "race_triggered": False,
                "address_or_payload_generated": False,
            },
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    with (args.output / "native-inventory.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=(
            "artifact", "path", "sha256", "file_description",
            "classification", "confidence", "string_hit_count", "symbol_hit_count",
        ))
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "artifact": row["artifact"],
                "path": row["path"],
                "sha256": row["sha256"],
                "file_description": row["file_description"],
                "classification": row["classification"],
                "confidence": row["confidence"],
                "string_hit_count": len(row["strings"]),
                "symbol_hit_count": len(row["symbols"]),
            })

    (args.output / "commands.txt").write_text(
        "# Host-only commands; no ADB and no ELF execution\n" +
        "\n".join(command_log) + "\n", encoding="utf-8"
    )
    if libart_disassembly:
        (args.output / "libart-suspendall-disassembly.txt").write_text(
            libart_disassembly, encoding="utf-8"
        )
    (args.output / "result.md").write_text(
        "# Phase 5CS native inventory\n\n"
        "This result is a bounded host-side scan of already pulled ELF files. "
        "No file was executed and no device was contacted.\n\n"
        + "\n".join(
            f"- `{row['artifact']}`: {row['classification']} ({row['confidence']})"
            for row in rows
        ) + "\n",
        encoding="utf-8",
    )
    files = sorted(args.output.iterdir())
    with (args.output / "sha256sums.txt").open("w", encoding="utf-8") as stream:
        for path in files:
            if path.name != "sha256sums.txt":
                stream.write(f"{sha256(path)}  {path.name}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
