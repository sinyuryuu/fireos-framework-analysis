#!/usr/bin/env python3
"""Host-only audit of the PS7331 futex/policy source surface.

This script reads the preserved source/config and a previously generated native
scan summary.  It never contacts ADB, executes an ELF, compiles code, creates
futex arguments, enables tracing, accesses kernel memory, or emits a payload.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


OP_PATTERNS = {
    "FUTEX_WAIT_REQUEUE_PI": re.compile(r"\bFUTEX_WAIT_REQUEUE_PI\b"),
    "FUTEX_CMP_REQUEUE_PI": re.compile(r"\bFUTEX_CMP_REQUEUE_PI\b"),
    "FUTEX_LOCK_PI": re.compile(r"\bFUTEX_LOCK_PI(?:2)?(?:_PRIVATE)?\b"),
    "FUTEX_UNLOCK_PI": re.compile(r"\bFUTEX_UNLOCK_PI(?:_PRIVATE)?\b"),
    "FUTEX_WAIT": re.compile(r"\bFUTEX_WAIT(?:_PRIVATE)?\b"),
    "FUTEX_WAKE": re.compile(r"\bFUTEX_WAKE(?:_PRIVATE)?\b"),
    "seccomp": re.compile(r"\b(?:SECCOMP|seccomp)\b"),
}

TEXT_SUFFIXES = {
    ".c", ".h", ".cc", ".cpp", ".cxx", ".S", ".s", ".mk", ".bp",
    ".xml", ".te", ".cil", ".policy", ".txt", ".rc", ".json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_config(path: Path) -> dict[str, str | bool]:
    values: dict[str, str | bool] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("CONFIG_") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = True if value == "y" else False if value == "n" else value
        elif line.startswith("# CONFIG_") and line.endswith(" is not set"):
            values[line[2:-11]] = False
    return values


def is_kernel_path(path: Path) -> bool:
    return "kernel" in {part.lower() for part in path.parts}


def scan_userspace_tree(root: Path) -> tuple[dict[str, int], list[dict[str, object]], int]:
    counts = {key: 0 for key in OP_PATTERNS}
    hits: list[dict[str, object]] = []
    files_seen = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES or is_kernel_path(path):
            continue
        if path.stat().st_size > 8 * 1024 * 1024:
            continue
        files_seen += 1
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, 1):
            for label, pattern in OP_PATTERNS.items():
                if pattern.search(line):
                    counts[label] += 1
                    if len(hits) < 500:
                        hits.append({
                            "file": str(path),
                            "line": line_number,
                            "marker": label,
                            "excerpt": " ".join(line.strip().split())[:240],
                        })
    return counts, hits, files_seen


def policy_files(root: Path) -> list[str]:
    names = ("seccomp", "zygote", "syscall", "app_process")
    results = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or is_kernel_path(path):
            continue
        lowered = path.name.lower()
        if any(name in lowered for name in names):
            results.append(str(path))
    return results[:500]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--native-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "device_contacted": False,
            "elf_executed": False,
            "source_root": str(args.source_root),
            "config": str(args.config),
            "native_summary": str(args.native_summary),
            "output": str(args.output),
        }, indent=2))
        return 0

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    for path in (args.source_root, args.config, args.native_summary):
        if not path.exists():
            raise SystemExit(f"missing input: {path}")

    config = parse_config(args.config)
    counts, hits, files_seen = scan_userspace_tree(args.source_root)
    policy = policy_files(args.source_root)
    native = json.loads(args.native_summary.read_text(encoding="utf-8"))
    result = {
        "schema": "phase6c-futex-policy-surface-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "source_root": str(args.source_root),
            "source_root_exists": args.source_root.is_dir(),
            "config": str(args.config),
            "config_sha256": sha256(args.config),
            "native_summary": str(args.native_summary),
            "native_summary_sha256": sha256(args.native_summary),
        },
        "config": {key: config.get(key) for key in (
            "CONFIG_FUTEX", "CONFIG_RT_MUTEXES", "CONFIG_SECCOMP",
            "CONFIG_SECCOMP_FILTER", "CONFIG_USERFAULTFD",
        )},
        "userspace_source": {
            "text_files_scanned": files_seen,
            "marker_counts": counts,
            "policy_named_files_outside_kernel": policy,
            "hit_rows_capped_at": 500,
        },
        "native_summary": {
            "elf_files_scanned": native.get("elf_files_scanned"),
            "result_counts": native.get("result_counts"),
            "named_requeue_pi_files": native.get("named_requeue_pi_files"),
        },
        "safety": {
            "device_contacted": False,
            "elf_executed": False,
            "source_executed": False,
            "futex_triggered": False,
            "kernel_memory_accessed": False,
            "payload_or_address_generated": False,
        },
        "interpretation": [
            "Kernel configuration enables futex/rtmutex/seccomp only where the captured config says so.",
            "A userspace source hit is not proof of an installed or executed caller.",
            "No policy file outside kernel paths is not proof that device policy is absent.",
            "No named native marker is not proof against stripped, inline, numeric, indirect, or unpulled callers.",
        ],
    }

    args.output.mkdir(parents=True)
    summary_path = args.output / "policy-surface.json"
    hits_path = args.output / "userspace-source-hits.csv"
    matrix_path = args.output / "futex-policy-matrix.csv"
    result_path = args.output / "result.md"
    summary_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with hits_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["file", "line", "marker", "excerpt"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(hits)
    rows = [
        {"surface": "kernel config FUTEX", "value": config.get("CONFIG_FUTEX"), "evidence": "captured config", "classification": "Confirmed config scope"},
        {"surface": "kernel config RT_MUTEXES", "value": config.get("CONFIG_RT_MUTEXES"), "evidence": "captured config", "classification": "Confirmed config scope"},
        {"surface": "kernel config SECCOMP", "value": config.get("CONFIG_SECCOMP"), "evidence": "captured config", "classification": "Confirmed config scope"},
        {"surface": "kernel config SECCOMP_FILTER", "value": config.get("CONFIG_SECCOMP_FILTER"), "evidence": "captured config", "classification": "Confirmed config scope"},
        {"surface": "userspace named REQUEUE_PI source hits", "value": counts["FUTEX_WAIT_REQUEUE_PI"] + counts["FUTEX_CMP_REQUEUE_PI"], "evidence": "non-kernel source scan", "classification": "Bounded source observation"},
        {"surface": "policy-named files outside kernel", "value": len(policy), "evidence": "filename inventory", "classification": "Coverage limitation"},
        {"surface": "native named REQUEUE_PI files", "value": len(native.get("named_requeue_pi_files") or []), "evidence": "native artifact scan", "classification": "Bounded artifact observation"},
    ]
    with matrix_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["surface", "value", "evidence", "classification"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    result_path.write_text(
        "# Phase 6C futex/policy surface audit\n\n"
        "Host-only; no ADB, ELF execution, futex trigger, kernel memory access, or payload.\n\n"
        f"- Text files scanned outside kernel paths: {files_seen}\n"
        f"- Named non-kernel REQUEUE_PI source hits: {counts['FUTEX_WAIT_REQUEUE_PI'] + counts['FUTEX_CMP_REQUEUE_PI']}\n"
        f"- Policy-named files outside kernel paths: {len(policy)}\n"
        f"- Native named REQUEUE_PI files: {len(native.get('named_requeue_pi_files') or [])}\n\n"
        "No policy file or marker result is an absence proof; indirect/stripped/unpulled callers remain unverified.\n",
        encoding="utf-8",
    )
    output_files = (summary_path, hits_path, matrix_path, result_path)
    (args.output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in output_files) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
