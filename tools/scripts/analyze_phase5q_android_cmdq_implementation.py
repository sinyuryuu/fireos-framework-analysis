#!/usr/bin/env python3
"""Compare the public Android CMDQ implementation with saved Fire evidence.

This is a host-only analyzer.  It reads recovered source excerpts and the
already archived bounded runtime result; it never talks to ADB, opens a device
node, emits an ioctl, builds native code, or executes a PoC.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def has(text: str, needle: str) -> bool:
    return needle in text


def runtime_value(path: Path, key: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(key)}=(.*)$", re.MULTILINE)
    match = pattern.search(read(path))
    return match.group(1).strip() if match else None


def build_result(args: argparse.Namespace) -> dict[str, object]:
    v2 = read(args.v2_excerpt)
    v3 = read(args.v3_excerpt)
    runtime = read(args.runtime_result)

    rows = [
        {
            "factor": "AOSP CTS implementation form",
            "public_observation": "native CTS cc_test / poc.c; device-node and ioctl path",
            "fire_observation": "no APK or live PoC used in this review",
            "classification": "Confirmed",
        },
        {
            "factor": "CMDQ write-address ioctl #7",
            "public_observation": "CMDQ_IOCTL_ALLOC_WRITE_ADDRESS 0x40087807",
            "fire_observation": (
                "present in recovered v2 excerpt; absent from v3 dispatcher excerpt; "
                "saved runtime result is -25 (-ENOTTY)"
            ),
            "classification": "Confirmed, source/runtime scoped",
        },
        {
            "factor": "v2 allocation implementation",
            "public_observation": "copy_from_user -> cmdqCoreAllocWriteAddress -> copy_to_user",
            "fire_observation": "recovered v2 source only; not evidence that installed v3 exposes it",
            "classification": "Confirmed, source scoped",
        },
        {
            "factor": "v3 unknown-request behavior",
            "public_observation": "not applicable to the old AOSP PoC contract",
            "fire_observation": "default branch returns -ENOIOCTLCMD",
            "classification": "Confirmed, source scoped",
        },
        {
            "factor": "CVE status of signed PS7330 kernel",
            "public_observation": "public PoC targets a historical CMDQ contract",
            "fire_observation": "exact signed driver binary/backport status is not proven by source excerpts",
            "classification": "Unknown",
        },
    ]

    return {
        "analyzer": "analyze_phase5q_android_cmdq_implementation.py",
        "scope": "host-only; no ADB, ioctl, exploit build, or device mutation",
        "inputs": {
            "v2_excerpt": {"path": str(args.v2_excerpt), "sha256": sha256(args.v2_excerpt)},
            "v3_excerpt": {"path": str(args.v3_excerpt), "sha256": sha256(args.v3_excerpt)},
            "runtime_result": {"path": str(args.runtime_result), "sha256": sha256(args.runtime_result)},
        },
        "checks": {
            "v2_has_alloc_write_case": has(v2, "case CMDQ_IOCTL_ALLOC_WRITE_ADDRESS"),
            "v2_has_copy_from_user": has(v2, "copy_from_user(&addrReq"),
            "v2_has_alloc_helper": has(v2, "cmdqCoreAllocWriteAddress"),
            "v3_has_alloc_write_case": has(v3, "case CMDQ_IOCTL_ALLOC_WRITE_ADDRESS"),
            "v3_has_unknown_ioctl_return": has(v3, "return -ENOIOCTLCMD"),
            "runtime_open_ret": runtime_value(args.runtime_result, "open_ret"),
            "runtime_ioctl_ret": runtime_value(args.runtime_result, "ioctl_ret"),
        },
        "rows": rows,
        "decision": (
            "The saved evidence supports a v2-PoC versus v3-driver ABI mismatch "
            "for the tested request. It does not prove that all v3 interfaces are "
            "safe or that CVE-2020-0069 is absent from the signed kernel."
        ),
    }


def write_outputs(result: dict[str, object], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "comparison.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = ["factor\tpublic_observation\tfire_observation\tclassification"]
    for row in result["rows"]:  # type: ignore[index]
        lines.append("\t".join(str(row[field]) for field in (
            "factor", "public_observation", "fire_observation", "classification"
        )))
    (output_dir / "comparison.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2-excerpt", type=Path, required=True)
    parser.add_argument("--v3-excerpt", type=Path, required=True)
    parser.add_argument("--runtime-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for path in (args.v2_excerpt, args.v3_excerpt, args.runtime_result):
        if not path.is_file():
            parser.error(f"input is not a file: {path}")
    if args.output.exists():
        if not args.output.is_dir():
            parser.error(f"refusing to overwrite existing non-directory: {args.output}")
        protected = (args.output / "comparison.json", args.output / "comparison.tsv")
        if any(path.exists() for path in protected):
            parser.error(f"refusing to overwrite existing derived output: {args.output}")
    if args.dry_run:
        print(f"would read 3 host files and write {args.output}/comparison.json + comparison.tsv")
        return 0
    write_outputs(build_result(args), args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
