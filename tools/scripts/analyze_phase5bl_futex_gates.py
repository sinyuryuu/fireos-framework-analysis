#!/usr/bin/env python3
"""Summarize a preserved, read-only Phase 5BL futex gate capture.

This tool is intentionally host-only. It never invokes adb, opens a device
node, triggers futex/PI operations, or interprets denied reads as enabled.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exit_code(capture: Path, stem: str) -> str:
    value = read(capture / f"{stem}.exit_code.txt").strip()
    return value or "MISSING"


def parse_identity(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("uid="):
            result["identity"] = line
        elif line == "Enforcing" or line == "Permissive" or line == "Disabled":
            result["selinux"] = line
        elif line.startswith("Linux "):
            result["uname"] = line
        elif line.startswith("Amazon/"):
            result["fingerprint"] = line
        elif re.fullmatch(r"\d+", line.strip()):
            result["incremental"] = line.strip()
    return result


def parse_sysctls(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in text.splitlines():
        if line.startswith("--- "):
            if current is not None:
                rows.append(current)
            current = {"key": line[4:].strip()}
        elif current is not None and "value" not in current:
            current["value"] = line.strip()
            current["status"] = "denied" if "Permission denied" in line else "read"
    if current is not None:
        rows.append(current)
    return rows


def summarize(capture: Path) -> dict[str, object]:
    identity = parse_identity(read(capture / "identity.stdout.txt"))
    sysctls = parse_sysctls(read(capture / "kernel_sysctls.stdout.txt"))
    visibility = read(capture / "proc_visibility.stdout.txt")
    symbols = read(capture / "futex_symbols.stdout.txt").strip()
    process = read(capture / "process_status.stdout.txt")
    observations = [
        {
            "id": "P5BL-RUNTIME-001",
            "surface": "identity",
            "observed": identity,
            "interpretation": "Exact runtime identity is preserved; caller remains ordinary shell under SELinux.",
            "confidence": "Confirmed, snapshot scope",
        },
        {
            "id": "P5BL-RUNTIME-002",
            "surface": "kernel_sysctls",
            "observed": sysctls,
            "interpretation": "Most hardening sysctls are not readable by shell; unreadable is not treated as enabled or disabled.",
            "confidence": "Confirmed, read-permission scope",
        },
        {
            "id": "P5BL-RUNTIME-003",
            "surface": "proc_kallsyms",
            "observed": "Permission denied" if "Permission denied" in visibility else "not observed",
            "interpretation": "No shell-readable kallsyms surface was observed; no address or offset is derived.",
            "confidence": "Confirmed, snapshot scope",
        },
        {
            "id": "P5BL-RUNTIME-004",
            "surface": "futex_symbols",
            "observed": symbols or "no output after denied kallsyms read",
            "interpretation": "The empty result cannot establish symbol absence because the source procfs read was denied.",
            "confidence": "Confirmed, negative observation only",
        },
        {
            "id": "P5BL-RUNTIME-005",
            "surface": "device_nodes",
            "observed": visibility,
            "interpretation": "ION and CMDQ node metadata was listed only; no node was opened and no ioctl was sent.",
            "confidence": "Confirmed, metadata scope",
        },
        {
            "id": "P5BL-SAFETY-001",
            "surface": "test_boundary",
            "observed": {
                "futex_trigger": False,
                "device_mutation": False,
                "adb_serial": read(capture / "metadata.tsv"),
            },
            "interpretation": "Capture remained read-only and did not test exploitability.",
            "confidence": "Confirmed",
        },
    ]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only_analyzer": True,
        "device_io": False,
        "capture_dir": str(capture),
        "capture_sha256": {
            path.name: sha256(path)
            for path in sorted(capture.iterdir())
            if path.is_file() and path.name != "sha256sums.txt"
        },
        "process_status_raw": process,
        "exit_codes": {
            stem: exit_code(capture, stem)
            for stem in ("identity", "kernel_sysctls", "proc_visibility", "futex_symbols", "process_status")
        },
        "observations": observations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print("DRY-RUN: no files will be read or written.")
        print(f"CAPTURE\t{args.capture_dir}")
        print(f"OUTPUT\t{args.output}")
        return 0
    if args.output.exists():
        print(f"ERROR: output already exists: {args.output}", file=sys.stderr)
        return 2
    if not args.capture_dir.is_dir():
        print("ERROR: capture directory missing", file=sys.stderr)
        return 2
    args.output.mkdir(parents=True)
    result = summarize(args.capture_dir)
    (args.output / "summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (args.output / "observations.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["evidence_id", "surface", "observed", "interpretation", "confidence"])
        for item in result["observations"]:
            writer.writerow([
                item["id"],
                item["surface"],
                json.dumps(item["observed"], ensure_ascii=False),
                item["interpretation"],
                item["confidence"],
            ])
    print(f"Wrote host-only futex gate summary to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
