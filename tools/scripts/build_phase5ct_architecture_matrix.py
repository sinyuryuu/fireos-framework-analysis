#!/usr/bin/env python3
"""Build a sanitized GhostLock architecture comparison matrix.

This script is intentionally non-executable with respect to the exploit.  It
only records source-level stage boundaries and evidence labels.  It does not
download, compile, execute, adapt, or emit exploit code, offsets, syscall
recipes, kernel addresses, memory-write targets, or root commands.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROWS = [
    {
        "evidence_id": "P5CT-001",
        "stage": "target selection",
        "emerald": "Build-specific kernel/profile selector in main.c and target metadata",
        "fire_ps7331": "Exact build is PS7331.4463N, MT8183, Android 9, 4.4 family",
        "result": "profile mismatch; no direct binary compatibility",
        "classification": "Confirmed, artifact/source scope",
        "safety": "profile-only; no offsets copied",
    },
    {
        "evidence_id": "P5CT-002",
        "stage": "userspace trigger",
        "emerald": "Source describes coordinated waiter/owner/consumer roles and PI requeue operations",
        "fire_ps7331": "Fire libc confirms generic wait and PI-lock helpers; requeue-PI caller not established",
        "result": "Emerald trigger architecture is not demonstrated on Fire",
        "classification": "Strong evidence, bounded scope",
        "safety": "no futex trigger executed",
    },
    {
        "evidence_id": "P5CT-003",
        "stage": "kernel defect path",
        "emerald": "Project relies on the GhostLock futex/rtmutex proxy-cleanup defect",
        "fire_ps7331": "PS7331 source contains futex requeue → proxy-lock → current-based cleanup pattern",
        "result": "source-level defect family matches",
        "classification": "Confirmed, source scope",
        "safety": "no runtime execution claim",
    },
    {
        "evidence_id": "P5CT-004",
        "stage": "runtime identity",
        "emerald": "Public project reports a working target profile, but source review is not a Fire runtime trace",
        "fire_ps7331": "waiter->task != current has not been observed on stock runtime",
        "result": "dynamic validation gate remains open",
        "classification": "Unobserved",
        "safety": "no race/instrumentation performed",
    },
    {
        "evidence_id": "P5CT-005",
        "stage": "memory effect",
        "emerald": "Project includes a target-specific post-trigger memory/root stage",
        "fire_ps7331": "No Fire-compatible memory primitive or target profile is established",
        "result": "controlled memory effect is unproven",
        "classification": "Unknown / not established",
        "safety": "no kernel memory access or payload generation",
    },
    {
        "evidence_id": "P5CT-006",
        "stage": "privilege transition",
        "emerald": "Project contains a target-specific root delivery stage",
        "fire_ps7331": "No legitimate Fire privilege transition has been demonstrated",
        "result": "temporary root is unproven",
        "classification": "Unproven",
        "safety": "no root payload executed",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY-RUN: no files are written; no exploit source is read or executed.")
        print(f"OUTPUT\t{args.output}")
        return 0
    if args.output.exists():
        print(f"ERROR: refusing to overwrite output: {args.output}", file=sys.stderr)
        return 2

    args.output.mkdir(parents=True)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "exploit_source_read": False,
        "exploit_compiled": False,
        "exploit_executed": False,
        "rows": ROWS,
    }
    (args.output / "architecture.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (args.output / "architecture.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(ROWS[0]))
        writer.writeheader()
        writer.writerows(ROWS)
    (args.output / "commands.txt").write_text(
        "# Host-only evidence matrix generation\n"
        "python3 tools/scripts/build_phase5ct_architecture_matrix.py \\\n+  --output " + str(args.output) + "\n", encoding="utf-8"
    )
    (args.output / "result.md").write_text(
        "# Phase 5CT architecture matrix\n\n"
        "Sanitized source/evidence comparison only. No exploit source was read, "
        "compiled or executed, and no device was contacted.\n",
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
