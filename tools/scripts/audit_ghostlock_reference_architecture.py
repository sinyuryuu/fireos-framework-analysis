#!/usr/bin/env python3
"""Audit a GhostLock reference repository without executing its payload.

The audit records high-level architecture markers and selected source hashes.
It deliberately does not compile, run, emulate, extract offsets for reuse,
generate a trigger, contact Android, or reproduce a kernel read/write chain.
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


SELECTED_FILES = (
    "README.md",
    "Makefile",
    "src/core/slide.c",
    "src/core/kernelsnitch/kernelsnitch.h",
    "src/core/fops.c",
    "src/core/pipe_physrw.c",
    "src/core/umh_root.c",
    "src/core/root.c",
    "src/core/target.h",
    "src/devices/offsets.h",
    "src/devices/emerald/offsets.h",
)

MARKERS = (
    (
        "pi_futex_sequence",
        re.compile(
            r"FUTEX_(?:WAIT_REQUEUE_PI|CMP_REQUEUE_PI|LOCK_PI|UNLOCK_PI)"
        ),
    ),
    (
        "kernel_memory_primitive",
        re.compile(
            r"kernel_(?:read|write)|physrw|pipe_phys|configfs|"
            r"kernel_read64|kernel_write_data"
        ),
    ),
    (
        "credential_or_execution_transition",
        re.compile(
            r"setuid|commit_creds|prepare_kernel_cred|usermodehelper|"
            r"umh_|root_uid"
        ),
    ),
    (
        "target_specific_layout",
        re.compile(
            r"offset|KASLR|SLIDE_|boot_id|kernel_phys|phys_offset|"
            r"STRUCT_.*_OFF"
        ),
    ),
    (
        "orchestration",
        re.compile(
            r"pthread_create|pselect|timerfd|mmap|mprotect|pipe\( |"
            r"FUTEX_WAIT_PRIVATE|FUTEX_WAKE_PRIVATE"
        ),
    ),
    (
        "build_target",
        re.compile(r"aarch64-linux-android|NDK|API\s*\?|pthread"),
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repo_commit(reference_dir: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(reference_dir), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "UNAVAILABLE"
    return result.stdout.strip()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(
            json.dumps(
                {
                    "reference_dir": str(args.reference_dir),
                    "selected_files": list(SELECTED_FILES),
                    "output": str(args.output),
                    "source_executed": False,
                    "payload_executed": False,
                    "device_contacted": False,
                },
                indent=2,
            )
        )
        return 0

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    if not args.reference_dir.is_dir():
        raise FileNotFoundError(args.reference_dir)
    args.output.mkdir(parents=True)

    marker_rows: list[dict[str, object]] = []
    hash_rows: list[dict[str, object]] = []
    missing: list[str] = []
    for relative in SELECTED_FILES:
        path = args.reference_dir / relative
        if not path.is_file():
            missing.append(relative)
            continue
        hash_rows.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            excerpt = " ".join(line.strip().split())
            for category, pattern in MARKERS:
                if pattern.search(line):
                    marker_rows.append(
                        {
                            "path": relative,
                            "line": line_number,
                            "category": category,
                            "excerpt": excerpt,
                        }
                    )

    marker_rows.sort(
        key=lambda row: (str(row["path"]), int(row["line"]), str(row["category"]))
    )
    hash_rows.sort(key=lambda row: str(row["path"]))
    marker_path = args.output / "architecture-markers.csv"
    hash_path = args.output / "selected-source-hashes.csv"
    write_csv(marker_path, ["path", "line", "category", "excerpt"], marker_rows)
    write_csv(hash_path, ["path", "bytes", "sha256"], hash_rows)

    category_counts: dict[str, int] = {}
    for row in marker_rows:
        category = str(row["category"])
        category_counts[category] = category_counts.get(category, 0) + 1
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "reference_commit": repo_commit(args.reference_dir),
        "reference_dir": str(args.reference_dir),
        "selected_files": len(hash_rows),
        "missing_selected_files": missing,
        "marker_rows": len(marker_rows),
        "category_counts": dict(sorted(category_counts.items())),
        "source_executed": False,
        "payload_compiled": False,
        "payload_executed": False,
        "device_contacted": False,
        "kernel_memory_accessed": False,
        "offsets_reused": False,
        "root_or_privilege_gain_proven": False,
        "interpretation": (
            "The reference source contains an explicit PI/requeue orchestration "
            "and later kernel-memory/credential-transition stages. This proves "
            "the reference architecture only; it does not establish compatibility "
            "with PS7331 or authorize compilation/execution."
        ),
    }
    summary_path = args.output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest = args.output / "sha256sums.txt"
    manifest.write_text(
        "\n".join(
            f"{sha256(path)}  {path.name}"
            for path in (marker_path, hash_path, summary_path)
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
