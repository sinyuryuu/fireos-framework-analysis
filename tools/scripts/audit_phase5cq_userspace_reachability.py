#!/usr/bin/env python3
"""Create a bounded, host-only Phase 5CQ userspace reachability audit.

This script reads an existing Phase 5CP JSON artifact and emits a small
evidence bundle.  It never contacts a device, compiles or executes kernel
source, invokes a syscall, creates a race, derives addresses, or emits a
trigger/payload recipe.  The AOSP observations are reference annotations, not
claims about the installed Fire libc.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase5cp-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY-RUN: no source is read and no files are written.")
        print(f"PHASE5CP_JSON\t{args.phase5cp_json}")
        print(f"OUTPUT\t{args.output}")
        return 0

    if not args.phase5cp_json.is_file():
        print("ERROR: --phase5cp-json must be a regular file", file=sys.stderr)
        return 2
    if args.output.exists():
        print(f"ERROR: refusing to overwrite output: {args.output}", file=sys.stderr)
        return 2

    phase5cp = json.loads(args.phase5cp_json.read_text(encoding="utf-8"))
    runtime = phase5cp.get("runtime_result", {})
    safety = phase5cp.get("safety", {})
    observations = [
        {
            "evidence_id": "P5CQ-006",
            "layer": "Fire PS7331 kernel source/config",
            "subject": "proxy dataflow",
            "observation": "Phase 5CO/5CP source evidence is present; userspace caller is not established here",
            "confidence": "Confirmed source/config scope",
        },
        {
            "evidence_id": "P5CQ-008",
            "layer": "Fire PS7331 runtime",
            "subject": "identity mismatch and cleanup",
            "observation": "existing Phase 5CP capture does not observe runtime mismatch or cleanup",
            "confidence": "Unknown / runtime unobserved",
        },
        {
            "evidence_id": "P5CQ-SAFETY-001",
            "layer": "audit process",
            "subject": "execution boundary",
            "observation": "host-only; no device, syscall, race, address or payload operation",
            "confidence": "Confirmed safety scope",
        },
    ]
    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "phase5cp_json": {
            "path": str(args.phase5cp_json),
            "sha256": sha256(args.phase5cp_json),
        },
        "aosp_reference_observations": {
            "pthread_cond_uses_requeue_pi": "not established by Android 9 r61 reference",
            "uapi_exposes_pi_names": True,
            "dedicated_bionic_futex_stub_observed": False,
            "fire_policy_inferred_from_aosp": False,
        },
        "existing_runtime_result": runtime,
        "safety": {
            "source_executed": False,
            "kernel_built": False,
            "syscall_invoked": False,
            "race_triggered": False,
            "device_contacted": False,
            "address_or_payload_generated": False,
            **safety,
        },
        "observations": observations,
        "classification": "AOSP_COMMON_PTHREAD_PATH_NOT_ESTABLISHED_AS_REQUEUE_PI; FIRE_CALLER_AND_RUNTIME_UNOBSERVED",
        "references": [
            "https://android.googlesource.com/platform/bionic/+/refs/tags/android-9.0.0_r61/libc/bionic/pthread_cond.cpp",
            "https://android.googlesource.com/platform/bionic/+/3a6c6b3/libc/kernel/uapi/linux/futex.h",
            "https://android.googlesource.com/platform/bionic/+/refs/tags/android-9.0.0_r61/libc/SYSCALLS.TXT",
            "https://android.googlesource.com/platform/bionic/+/refs/tags/android-9.0.0_r61/libc/SECCOMP_WHITELIST_APP.TXT",
            "https://android.googlesource.com/platform/bionic/+/refs/tags/android-9.0.0_r61/libc/SECCOMP_BLACKLIST_APP.TXT",
        ],
    }

    args.output.mkdir(parents=True)
    (args.output / "userspace-reachability.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (args.output / "observations.csv").open("w", encoding="utf-8") as stream:
        stream.write("evidence_id,layer,subject,observation,confidence\n")
        for item in observations:
            values = [str(item[key]).replace('"', '""') for key in
                      ("evidence_id", "layer", "subject", "observation", "confidence")]
            stream.write('"' + '","'.join(values) + '"\n')
    (args.output / "result.md").write_text(
        "# Phase 5CQ userspace reachability audit\n\n"
        "Host-only audit. No device, syscall, race, kernel build, address or payload.\n\n"
        "AOSP Android 9 reference pthread condition variables do not establish a\n"
        "requeue-PI caller. Fire-specific caller, policy and runtime cleanup remain\n"
        "unobserved.\n",
        encoding="utf-8",
    )
    (args.output / "commands.txt").write_text(
        "python3 tools/scripts/audit_phase5cq_userspace_reachability.py \\\n  --phase5cp-json " + str(args.phase5cp_json) + " \\\n  --output " + str(args.output) + "\n",
        encoding="utf-8",
    )
    files = sorted(args.output.iterdir())
    with (args.output / "sha256sums.txt").open("w", encoding="utf-8") as stream:
        for path in files:
            if path.name == "sha256sums.txt":
                continue
            stream.write(f"{sha256(path)}  {path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
