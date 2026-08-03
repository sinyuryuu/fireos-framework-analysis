#!/usr/bin/env python3
"""Build a host-only MTKClient compatibility matrix.

The analyzer reads a fixed source excerpt and existing local evidence. It does
not import, invoke, or communicate with mtkclient and never calls ADB.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import pathlib
import sys


FIELDS = [
    "route",
    "public_revision",
    "exact_device_requirement",
    "observed_source_fact",
    "operation_class",
    "device_state_changed",
    "live_test_status",
    "confidence",
]


def digest(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--config-excerpt", type=pathlib.Path, required=True)
    p.add_argument("--device-report", type=pathlib.Path, required=True)
    p.add_argument("--test-metadata", type=pathlib.Path, required=True)
    p.add_argument("--output", type=pathlib.Path, required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    for path in (args.config_excerpt, args.device_report, args.test_metadata):
        if not path.is_file():
            p.error(f"missing input: {path}")
    if args.output.exists():
        p.error(f"refusing to overwrite existing output: {args.output}")

    config = args.config_excerpt.read_text(encoding="utf-8")
    device = args.device_report.read_text(encoding="utf-8")
    metadata = args.test_metadata.read_text(encoding="utf-8")
    required = ["MT6771/MT8385/MT8183/MT8666", "dacode=0x6771"]
    missing = [token for token in required if token not in config]
    if missing:
        p.error("unexpected config excerpt; missing " + ", ".join(missing))
    if "0x8183:" in config:
        p.error("excerpt unexpectedly contains an independent 0x8183 key")
    if "PS7330" not in device or "locked" not in device.lower():
        p.error("device report is not the expected locked PS7330 evidence")
    if "PENDINGINTENT-T01" not in metadata:
        p.error("test metadata is not the expected preparation run")

    config_id = f"{args.config_excerpt} sha256={digest(args.config_excerpt)}"
    rows = [
        {
            "route": "mtkclient-shared-mt6771-profile",
            "public_revision": "0542a8729993000661e2325e838217ee754d1632",
            "exact_device_requirement": "exact BROM/preloader/DA/auth profile",
            "observed_source_fact": "MT8183 listed in shared profile; dacode 0x6771; no 0x8183 key",
            "operation_class": "BROM/preloader/DA",
            "device_state_changed": "not run",
            "live_test_status": "rejected: no exact Amazon loader/auth chain",
            "confidence": "Strong evidence",
        },
        {
            "route": "mtk-easy-su-pinned-payload",
            "public_revision": "8c6871ac7c15b8e98a47e25c35ab93b87e260475",
            "exact_device_requirement": "matching kernel/driver ABI",
            "observed_source_fact": "same mtk-su64 payload as prior exact PS7330 run; step-3 failure",
            "operation_class": "Android userspace/kernel exploit",
            "device_state_changed": "rollback verified",
            "live_test_status": "not rerun",
            "confidence": "Confirmed",
        },
        {
            "route": "pendingintent-android-variant",
            "public_revision": "local current source",
            "exact_device_requirement": "manual Accessibility consent only",
            "observed_source_fact": "self-built v3-signed APK; T01 installed; service still disabled",
            "operation_class": "reversible foreground redirect",
            "device_state_changed": "research APKs installed; Fire untouched",
            "live_test_status": "waiting for manual consent",
            "confidence": "待驗證",
        },
        {
            "route": "official-home-resolver",
            "public_revision": "Fire OS/AOSP evidence",
            "exact_device_requirement": "PackageManager resolver state",
            "observed_source_fact": "Fire Launcher priority 50 remains resolver result",
            "operation_class": "formal HOME selection",
            "device_state_changed": "no mutation in analyzer",
            "live_test_status": "confirmed Fire Launcher",
            "confidence": "Confirmed",
        },
    ]
    if args.dry_run:
        print(f"DRY-RUN: read {config_id}, {args.device_report}, {args.test_metadata}")
        print(f"DRY-RUN: would write {args.output}; rows={len(rows)}; no ADB/network/MTKClient")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {args.output} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
