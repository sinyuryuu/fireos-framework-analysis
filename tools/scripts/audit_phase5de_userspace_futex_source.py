#!/usr/bin/env python3
"""Audit non-kernel PS7331 source for direct futex userspace call shapes.

The audit is text-only and host-only.  It excludes kernel trees and archives,
records source excerpts, and separates ordinary WAIT/WAKE calls from PI or
requeue-PI tokens.  It never compiles or executes the source and never contacts
a device.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PATTERNS = (
    "__NR_futex",
    "SYS_futex",
    "FUTEX_WAIT",
    "FUTEX_WAKE",
    "FUTEX_LOCK_PI",
    "FUTEX_UNLOCK_PI",
    "FUTEX_WAIT_REQUEUE_PI",
    "FUTEX_CMP_REQUEUE_PI",
    "FUTEX_REQUEUE_PI"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify(path: str) -> str:
    normalized = path.replace("\\", "/")
    if "/tests/" in normalized or normalized.endswith("/tests"):
        return "userspace_test"
    if "/external/" in normalized:
        return "external_userspace_source"
    if "/tools/" in normalized:
        return "userspace_tool"
    return "userspace_source"


def scan_root(root: Path) -> list[dict[str, object]]:
    if not root.is_dir():
        raise FileNotFoundError(f"source root does not exist: {root}")
    command = [
        "rg", "--no-messages", "--no-heading", "-H", "--line-number",
        "--ignore-case", "--glob", "!kernel/**", "--glob", "!**/kernel/**",
        "--glob", "!*.tar", "--glob", "!*.tar.*", "--glob", "!*.gz",
        "--glob", "!*.bz2", "--glob", "!*.xz", "--glob", "!*.o",
        "--glob", "!*.a", "--glob", "!*.so",
    ]
    for pattern in PATTERNS:
        command.extend(["-e", pattern])
    command.append(str(root))
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode not in (0, 1):
        raise RuntimeError(f"rg failed for {root}: {result.stderr}")
    rows: list[dict[str, object]] = []
    for raw in result.stdout.splitlines():
        match = re.match(r"^(.*?):(\d+):(.*)$", raw)
        if not match:
            continue
        filename, number, excerpt = match.groups()
        matched = next(
            (pattern for pattern in PATTERNS if pattern.lower() in excerpt.lower()),
            "UNKNOWN",
        )
        rows.append({
            "root": str(root),
            "path": str(Path(filename).relative_to(root)),
            "line": int(number),
            "pattern": matched,
            "class": classify(str(Path(filename).relative_to(root))),
            "excerpt": " ".join(excerpt.strip().split()),
        })
    return rows


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({
            "source_roots": [str(root) for root in args.source_root],
            "output": str(args.output),
            "kernel_excluded": True,
            "source_executed": False,
            "device_contacted": False,
        }, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)
    rows: list[dict[str, object]] = []
    for root in args.source_root:
        rows.extend(scan_root(root))
    rows.sort(key=lambda row: (str(row["root"]), str(row["path"]), int(row["line"])))
    hits_path = args.output / "userspace-futex-source-hits.csv"
    summary_path = args.output / "summary.json"
    write_csv(hits_path, ["root", "path", "line", "pattern", "class", "excerpt"], rows)
    requeue_rows = [
        row for row in rows
        if "REQUEUE_PI" in str(row["pattern"]).upper()
        or "REQUEUE_PI" in str(row["excerpt"]).upper()
    ]
    pi_rows = [
        row for row in rows
        if "LOCK_PI" in str(row["excerpt"]).upper()
        or "UNLOCK_PI" in str(row["excerpt"]).upper()
    ]
    direct_syscall_rows = [
        row for row in rows
        if "__NR_FUTEX" in str(row["excerpt"]).upper()
        and "SYSCALL" in str(row["excerpt"]).upper()
    ]
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_roots": [str(root) for root in args.source_root],
        "kernel_trees_excluded": True,
        "hit_rows": len(rows),
        "hit_files": len({(row["root"], row["path"]) for row in rows}),
        "class_counts": dict(Counter(str(row["class"]) for row in rows)),
        "pattern_counts": dict(Counter(str(row["pattern"]) for row in rows)),
        "ordinary_direct_syscall_rows": len(direct_syscall_rows),
        "pi_rows": len(pi_rows),
        "requeue_pi_rows": len(requeue_rows),
        "requeue_pi_files": sorted({f"{row['root']}/{row['path']}" for row in requeue_rows}),
        "interpretation": (
            "Non-kernel source is evidence about build inputs, not proof that the "
            "same code shipped or ran on the tablet. Ordinary FUTEX_WAIT/WAKE "
            "does not enter the requeue-PI proxy path."
        ),
        "safety": {
            "source_executed": False,
            "kernel_built": False,
            "device_contacted": False,
            "futex_triggered": False,
            "kernel_memory_accessed": False,
            "payload_or_address_generated": False,
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest = args.output / "sha256sums.txt"
    manifest.write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in (hits_path, summary_path)) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
