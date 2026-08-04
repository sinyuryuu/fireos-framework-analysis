#!/usr/bin/env python3
"""Verify the exact PS7331 target and preserved host-only GhostLock evidence.

This verifier checks already-produced metadata and sanitized markers. It does
not disassemble or execute an ELF, invoke ADB, calculate addresses, or emit a
payload.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


EXPECTED_SOURCE_SHA256 = (
    "6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde"
)
EXPECTED_BOOT_SHA256 = (
    "cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b"
)
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--match-metadata", type=Path, required=True)
    parser.add_argument("--source-result", type=Path, required=True)
    parser.add_argument("--boot-metadata", type=Path, required=True)
    parser.add_argument("--image-patterns", type=Path, required=True)
    parser.add_argument("--semantic-comparison", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inputs = [
        args.match_metadata,
        args.source_result,
        args.boot_metadata,
        args.image_patterns,
        args.semantic_comparison,
    ]
    if args.dry_run:
        print("DRY-RUN: read preserved metadata and sanitized markers only")
        print(f"output={args.output}")
        return 0
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise SystemExit("missing input: " + ", ".join(missing))
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite output: {args.output}")

    match = json.loads(args.match_metadata.read_text(encoding="utf-8"))
    source = json.loads(args.source_result.read_text(encoding="utf-8"))
    boot = json.loads(args.boot_metadata.read_text(encoding="utf-8"))
    comparison = json.loads(args.semantic_comparison.read_text(encoding="utf-8"))
    with args.image_patterns.open(newline="", encoding="utf-8") as stream:
        patterns = {(row["symbol"], row["pattern"]) for row in csv.DictReader(stream)}

    checks = {
        "exact_device_ota_match": match.get("exact_target_match") is True,
        "device_fingerprint_match": match.get("fingerprint_match") is True,
        "device_incremental_match": match.get("incremental_match") is True,
        "device_security_patch_match": match.get("security_patch_match") is True,
        "device_product_match": match.get("product_match") is True,
        "source_sha256_exact_mt8183": source.get("source_sha256") == EXPECTED_SOURCE_SHA256,
        "source_pre_fix_classification": source.get("classification")
        == "PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN",
        "source_proxy_cleanup_present": source.get("proxy_error_remove_waiter_call_present") is True,
        "boot_image_sha256_ps7331": boot.get("image_sha256") == EXPECTED_BOOT_SHA256,
        "boot_image_gzip_kernel": boot.get("kernel_compression_signature") == "gzip",
        "sanitized_image_markers_present": EXPECTED_PATTERNS.issubset(patterns),
        "preserved_comparison_pre_fix": comparison.get("verdict", {}).get(
            "ps7331_inspected_image_consistent_with_pre_fix_source"
        ) is True,
        "preserved_comparison_no_execution": comparison.get("analysis", {}).get(
            "binary_execution"
        ) is False,
    }
    verdict = all(checks.values())
    result = {
        "checks": checks,
        "verdict": {
            "exact_ps7331_target_chain_verified": verdict,
            "source_and_inspected_image_pre_fix_consistent": verdict,
            "runtime_identity_mismatch_observed": False,
            "runtime_exploitability_proven": False,
            "root_or_privilege_gain_proven": False,
        },
        "expected_hashes": {
            "source": EXPECTED_SOURCE_SHA256,
            "boot_image": EXPECTED_BOOT_SHA256,
        },
        "scope": "preserved host-only metadata and sanitized marker verification; no device I/O or code execution",
    }
    args.output.mkdir(parents=True)
    result_path = args.output / "verification.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output / "result.md").write_text(
        "# Phase 5DB exact PS7331 chain verification\n\n"
        f"- Exact device/OTA target chain: **{verdict}**\n"
        "- Source and inspected Image are pre-fix-consistent: **"
        f"{verdict}**\n"
        "- Runtime identity mismatch observed: **False**\n"
        "- Runtime exploitability/root proven: **False**\n\n"
        "This verifier only checks preserved metadata and sanitized markers; it "
        "does not execute code or contact the device.\n",
        encoding="utf-8",
    )
    (args.output / "sha256sums.txt").write_text(
        f"{sha256(result_path)}  verification.json\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
