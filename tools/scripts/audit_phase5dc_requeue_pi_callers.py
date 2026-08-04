#!/usr/bin/env python3
"""Audit PS7331 source and preserved native scans for requeue-PI callers.

This is a host-only, read-only audit.  It deliberately does not compile or
execute any source, native object, futex operation, ioctl, or device command.
The output is a bounded caller inventory: kernel implementation and test
helpers are kept separate from possible shipped userspace callers.
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
    "FUTEX_CMP_REQUEUE_PI",
    "FUTEX_WAIT_REQUEUE_PI",
    "FUTEX_REQUEUE_PI",
    "futex_cmp_requeue_pi",
    "futex_wait_requeue_pi",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify(path: str) -> str:
    normalized = path.replace("\\", "/")
    if "/tools/testing/selftests/futex/" in normalized:
        return "selftest"
    if "/tools/perf/" in normalized:
        return "perf_or_benchmark"
    if "/Documentation/" in normalized or "/include/" in normalized:
        return "uapi_or_documentation"
    if "/kernel/" in normalized:
        return "kernel_implementation"
    if normalized.startswith("fireos/") or "/fireos/" in normalized:
        return "fireos_non_kernel_candidate"
    if any(token in normalized for token in ("/framework/", "/packages/", "/apps/")):
        return "framework_or_app_candidate"
    return "unknown"


def run_source_scan(source_roots: list[Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for root in source_roots:
        if not root.is_dir():
            raise FileNotFoundError(f"source root does not exist: {root}")
        command = [
            "rg",
            "--no-messages",
            "--no-heading",
            "--line-number",
            "-H",
            "--ignore-case",
            "--glob",
            "!*.tar",
            "--glob",
            "!*.tar.*",
            "--glob",
            "!*.gz",
            "--glob",
            "!*.bz2",
            "--glob",
            "!*.xz",
            "--glob",
            "!*.zip",
        ]
        for pattern in PATTERNS:
            command.extend(["-e", pattern])
        command.append(str(root))
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        if result.returncode not in (0, 1):
            raise RuntimeError(f"rg failed for {root}: exit {result.returncode}: {result.stderr}")
        for raw in result.stdout.splitlines():
            match = re.match(r"^(.*?):(\d+):(.*)$", raw)
            if not match:
                continue
            file_name, line_number, excerpt = match.groups()
            matched = next(
                (pattern for pattern in PATTERNS if pattern.lower() in excerpt.lower()),
                "UNKNOWN_PATTERN",
            )
            relative = str(Path(file_name).relative_to(root))
            rows.append(
                {
                    "root": str(root),
                    "path": relative,
                    "line": int(line_number),
                    "pattern": matched,
                    "class": classify(relative),
                    "excerpt": " ".join(excerpt.strip().split()),
                }
            )
    rows.sort(key=lambda row: (str(row["root"]), str(row["path"]), int(row["line"])))
    return rows


def run_native_scan(native_scan_dirs: list[Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for native_scan_dir in native_scan_dirs:
        if not native_scan_dir.exists():
            raise FileNotFoundError(f"native scan directory does not exist: {native_scan_dir}")
        for path in sorted(native_scan_dir.rglob("*")):
            if not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for number, line in enumerate(text.splitlines(), 1):
                lowered = line.lower()
                if any(pattern.lower() in lowered for pattern in PATTERNS):
                    rows.append(
                        {
                            "path": str(path),
                            "line": number,
                            "excerpt": " ".join(line.strip().split()),
                        }
                    )
    return rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", action="append", type=Path, required=True)
    parser.add_argument("--native-scan-dir", action="append", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(json.dumps({
            "source_roots": [str(path) for path in args.source_root],
            "native_scan_dirs": [str(path) for path in (args.native_scan_dir or [])],
            "output": str(args.output),
            "device_contacted": False,
            "source_executed": False,
        }, indent=2))
        return 0

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)
    source_rows = run_source_scan(args.source_root)
    native_rows = run_native_scan(args.native_scan_dir or [])

    source_csv = args.output / "source-hits.csv"
    native_csv = args.output / "native-scan-hits.csv"
    summary_path = args.output / "summary.json"
    write_csv(
        source_csv,
        ["root", "path", "line", "pattern", "class", "excerpt"],
        source_rows,
    )
    write_csv(native_csv, ["path", "line", "excerpt"], native_rows)

    class_counts = Counter(str(row["class"]) for row in source_rows)
    pattern_counts = Counter(str(row["pattern"]) for row in source_rows)
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_roots": [str(path) for path in args.source_root],
        "native_scan_dirs": [str(path) for path in (args.native_scan_dir or [])],
        "source_hit_rows": len(source_rows),
        "source_hit_files": len({(row["root"], row["path"]) for row in source_rows}),
        "source_classes": dict(sorted(class_counts.items())),
        "source_patterns": dict(sorted(pattern_counts.items())),
        "native_hit_rows": len(native_rows),
        "userspace_candidate_rows": sum(
            1 for row in source_rows
            if row["class"] in {"fireos_non_kernel_candidate", "framework_or_app_candidate"}
        ),
        "source_executed": False,
        "native_objects_executed": False,
        "device_contacted": False,
        "futex_triggered": False,
        "kernel_memory_accessed": False,
        "payload_or_address_generated": False,
        "interpretation": (
            "Requeue-PI references are classified by source role. A kernel or selftest "
            "hit is not a shipped userspace caller; zero userspace-candidate hits is "
            "a bounded negative observation, not proof of impossibility."
        ),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    manifest = args.output / "sha256sums.txt"
    manifest.write_text(
        "\n".join(
            f"{sha256(path)}  {path.name}" for path in (source_csv, native_csv, summary_path)
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
