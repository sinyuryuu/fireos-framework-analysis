#!/usr/bin/env python3
"""Host-only applicability review for selected Linux/Android CVE surfaces.

This script reads an already captured vendor defconfig and an already captured
source-comparison JSON file.  It never invokes adb, opens a device node, builds
or runs exploit code, or changes device state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


RELEVANT = [
    "CONFIG_FUTEX",
    "CONFIG_RT_MUTEXES",
    "CONFIG_PREEMPT",
    "CONFIG_PANIC_ON_OOPS",
    "CONFIG_RANDOMIZE_BASE",
    "CONFIG_NF_DUP_IPV4",
    "CONFIG_NF_DUP_IPV6",
    "CONFIG_NETFILTER_XT_TARGET_TEE",
    "CONFIG_NF_TABLES",
    "CONFIG_INET_ESP",
    "CONFIG_INET6_ESP",
    "CONFIG_XFRM",
    "CONFIG_IPV6",
]


def parse_defconfig(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        # Some saved vendor excerpts include a source line number before the
        # original defconfig text, e.g. "  169 CONFIG_FUTEX=y".
        match = re.match(r"^\s*(?:\d+\s+)?(CONFIG_[A-Za-z0-9_]+)=(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2)
            continue
        match = re.match(
            r"^\s*(?:\d+\s+)?# (CONFIG_[A-Za-z0-9_]+) is not set$", line
        )
        if match:
            values[match.group(1)] = "n"
    return values


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--defconfig", required=True)
    parser.add_argument("--rtmutex-comparison", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--test-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    defconfig = Path(args.defconfig)
    comparison = Path(args.rtmutex_comparison)
    output = Path(args.output)

    if args.dry_run:
        print(f"DRY-RUN: read {defconfig}")
        print(f"DRY-RUN: read {comparison}")
        print(f"DRY-RUN: write host-only CVE surface review under {output}")
        return 0

    if not defconfig.is_file():
        parser.error(f"defconfig does not exist: {defconfig}")
    if not comparison.is_file():
        parser.error(f"comparison JSON does not exist: {comparison}")
    if output.exists():
        parser.error(f"output already exists: {output}")

    output.mkdir(parents=True)
    values = parse_defconfig(defconfig.read_text(encoding="utf-8", errors="replace"))
    comparison_data = json.loads(comparison.read_text(encoding="utf-8"))

    rows: list[str] = [
        "candidate\tsurface\tvalue\tinterpretation\tconfidence"
    ]
    ghostlock_ok = (
        values.get("CONFIG_FUTEX") == "y"
        and values.get("CONFIG_RT_MUTEXES") == "y"
    )
    rows.append(
        "CVE-2026-43499\tfutex/rtmutex\t"
        f"FUTEX={values.get('CONFIG_FUTEX', 'UNKNOWN')};"
        f"RT_MUTEXES={values.get('CONFIG_RT_MUTEXES', 'UNKNOWN')}\t"
        "source/config family is present; this is not runtime exploitability\t"
        + ("已證實（source/config scope）" if ghostlock_ok else "待驗證")
    )

    absent_dup = all(
        values.get(symbol) == "n"
        for symbol in (
            "CONFIG_NF_DUP_IPV4",
            "CONFIG_NF_DUP_IPV6",
            "CONFIG_NETFILTER_XT_TARGET_TEE",
        )
    )
    no_nft = values.get("CONFIG_NF_TABLES") == "n"
    rows.append(
        "CVE-2026-43503\tXFRM/ESP + packet duplication\t"
        f"NF_DUP={values.get('CONFIG_NF_DUP_IPV4', 'UNKNOWN')}/"
        f"{values.get('CONFIG_NF_DUP_IPV6', 'UNKNOWN')};"
        f"TEE={values.get('CONFIG_NETFILTER_XT_TARGET_TEE', 'UNKNOWN')};"
        f"NF_TABLES={values.get('CONFIG_NF_TABLES', 'UNKNOWN')}\t"
        "captured defconfig lacks the documented dup/TEE/nft entry path\t"
        + ("已排除（defconfig scope）" if absent_dup and no_nft else "待驗證")
    )

    write_text(output / "cve-surface-matrix.tsv", "\n".join(rows) + "\n")
    write_text(
        output / "input-hashes.tsv",
        "file\tsha256\n"
        f"{defconfig}\t{sha256_file(defconfig)}\n"
        f"{comparison}\t{sha256_file(comparison)}\n",
    )
    write_text(
        output / "metadata.tsv",
        f"test_id\t{args.test_id}\n"
        "scope\thost-only static analysis\n"
        "device_mutation\tno\n"
        "exploit_execution\tno\n",
    )
    write_text(
        output / "result.md",
        "# Phase 5U host-only CVE surface analysis\n\n"
        f"- Test ID: `{args.test_id}`\n"
        "- Device operation: none\n"
        "- Exploit compilation/execution: none\n"
        f"- GhostLock source/config family present: `{ghostlock_ok}`\n"
        f"- CVE-2026-43503 documented dup/TEE/nft path absent in captured defconfig: `{absent_dup and no_nft}`\n"
        f"- rtmutex comparison identical to v4.4.146 reference: `{comparison_data.get('identical')}`\n",
    )

    files = sorted(path for path in output.rglob("*") if path.is_file())
    manifest_lines = []
    for path in files:
        manifest_lines.append(f"{sha256_file(path)}  {path.relative_to(output)}")
    write_text(output / "sha256sums.txt", "\n".join(manifest_lines) + "\n")
    print(f"Wrote host-only CVE surface analysis to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
