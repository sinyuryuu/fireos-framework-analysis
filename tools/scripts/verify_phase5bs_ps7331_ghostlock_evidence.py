#!/usr/bin/env python3
"""Verify preserved PS7331 GhostLock evidence without executing code.

This verifier checks hashes and semantic markers already produced by separate
host-only analyses. It never disassembles a fresh image, runs an ELF, contacts
ADB, computes runtime addresses, or creates an exploit payload.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


EXPECTED_BOOT_SHA256 = "cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b"
EXPECTED_PATTERNS = {
    ("remove_waiter", "current_task_source"),
    ("remove_waiter", "current_task_blocked_on_clear"),
    ("rt_mutex_start_proxy_lock", "proxy_error_calls_remove_waiter"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--boot-image", type=Path, required=True)
    parser.add_argument("--source-result", type=Path, required=True)
    parser.add_argument("--image-patterns", type=Path, required=True)
    parser.add_argument("--semantic-comparison", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(json.dumps({"dry_run": True, "output": str(args.output)}, indent=2))
        return 0

    inputs = (args.boot_image, args.source_result, args.image_patterns, args.semantic_comparison)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        parser.error("missing input: " + ", ".join(missing))
    if args.output.exists():
        parser.error(f"refusing to overwrite output: {args.output}")

    source = json.loads(args.source_result.read_text(encoding="utf-8"))
    comparison = json.loads(args.semantic_comparison.read_text(encoding="utf-8"))
    with args.image_patterns.open(newline="", encoding="utf-8") as stream:
        patterns = {(row["symbol"], row["pattern"]) for row in csv.DictReader(stream)}

    checks = {
        "boot_hash_matches_ps7331": sha256(args.boot_image) == EXPECTED_BOOT_SHA256,
        "source_is_pre_fix": source.get("classification") == "PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN",
        "source_has_proxy_remove_waiter": source.get("proxy_error_remove_waiter_call_present") is True,
        "image_has_current_task_source": ("remove_waiter", "current_task_source") in patterns,
        "image_has_current_task_cleanup": ("remove_waiter", "current_task_blocked_on_clear") in patterns,
        "image_proxy_calls_remove_waiter": ("rt_mutex_start_proxy_lock", "proxy_error_calls_remove_waiter") in patterns,
        "comparison_verdict_pre_fix": comparison.get("verdict", {}).get(
            "classification"
        ) == "PS7331_INSPECTED_IMAGE_CONSISTENT_WITH_PRE_FIX_SOURCE",
        "comparison_safety_no_execution": comparison.get("analysis", {}).get("binary_execution") is False,
    }
    verdict = all(checks.values())
    result = {
        "inputs": {
            "boot_image_sha256": sha256(args.boot_image),
            "source_result_sha256": sha256(args.source_result),
            "image_patterns_sha256": sha256(args.image_patterns),
            "semantic_comparison_sha256": sha256(args.semantic_comparison),
        },
        "checks": checks,
        "verdict": {
            "ps7331_source_and_inspected_image_are_pre_fix_consistent": verdict,
            "runtime_exploitability_proven": False,
            "root_or_privilege_gain_proven": False,
            "address_or_offset_output": False,
            "payload_or_reproducer": False,
        },
        "scope": "verification of preserved host-only evidence; no code execution or device I/O",
    }
    args.output.mkdir(parents=True)
    result_path = args.output / "verification.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output / "sha256sums.txt").write_text(
        f"{sha256(result_path)}  verification.json\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
