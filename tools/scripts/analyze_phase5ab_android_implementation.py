#!/usr/bin/env python3
"""Analyze the safe Android redirect implementation boundary offline.

This script never invokes ADB, downloads code, installs an APK, or changes a
device. It reads the local source and emits a deterministic route matrix. The
matrix intentionally separates a real HOME resolver change from an
Accessibility foreground redirect.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import pathlib
import sys


FIELDS = [
    "route",
    "source_or_evidence",
    "trigger",
    "launch_api",
    "explicit_component",
    "background_start_boundary",
    "requires_user_consent",
    "requires_overlay",
    "requires_network",
    "changes_home_resolver",
    "device_state_mutation",
    "observed_result",
    "confidence",
]


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_rows(source: pathlib.Path) -> list[dict[str, str]]:
    text = source.read_text(encoding="utf-8")
    required = [
        "PendingIntent.getActivity",
        "pendingIntent.send",
        "Intent.ACTION_MAIN",
        "Intent.CATEGORY_LAUNCHER",
        "com.amazon.firelauncher",
        "REDIRECT_REQUEST_CODE",
    ]
    missing = [token for token in required if token not in text]
    if missing:
        raise SystemExit("source is not the expected PendingIntent variant; missing: "
                         + ", ".join(missing))

    source_id = f"local:{source} sha256={sha256(source)}"
    return [
        {
            "route": "historical-direct-start",
            "source_or_evidence": "adb/phase4/PHASE4-ACCESSIBILITY-T03; prior source",
            "trigger": "Fire package TYPE_WINDOW_STATE_CHANGED",
            "launch_api": "Context.startActivity",
            "explicit_component": "yes",
            "background_start_boundary": "direct service start",
            "requires_user_consent": "yes, Accessibility",
            "requires_overlay": "no",
            "requires_network": "no",
            "changes_home_resolver": "no",
            "device_state_mutation": "install/service preference only",
            "observed_result": "0/30 foreground handoffs",
            "confidence": "Confirmed",
        },
        {
            "route": "pending-intent-source-variant",
            "source_or_evidence": source_id,
            "trigger": "Fire package TYPE_WINDOW_STATE_CHANGED",
            "launch_api": "PendingIntent.getActivity().send",
            "explicit_component": "yes",
            "background_start_boundary": "public PendingIntent dispatch",
            "requires_user_consent": "yes, Accessibility",
            "requires_overlay": "no",
            "requires_network": "no",
            "changes_home_resolver": "no",
            "device_state_mutation": "not run; source/build only",
            "observed_result": "not measured",
            "confidence": "待驗證",
        },
        {
            "route": "launcherhijack-public-reference",
            "source_or_evidence": "LauncherHijack f79aee3; HomePress.java",
            "trigger": "Accessibility event or homekey observer",
            "launch_api": "PendingIntent.getActivity().send",
            "explicit_component": "yes",
            "background_start_boundary": "public PendingIntent dispatch",
            "requires_user_consent": "yes, Accessibility",
            "requires_overlay": "optional legacy service",
            "requires_network": "no",
            "changes_home_resolver": "no",
            "device_state_mutation": "app/service preference only",
            "observed_result": "public implementation reference; not this device run",
            "confidence": "Strong evidence",
        },
        {
            "route": "android-standard-home",
            "source_or_evidence": "Fire OS/AOSP evidence index",
            "trigger": "Home key / ACTION_MAIN+CATEGORY_HOME",
            "launch_api": "ActivityTaskManager HOME resolution",
            "explicit_component": "no, resolver selected",
            "background_start_boundary": "system_server",
            "requires_user_consent": "no",
            "requires_overlay": "no",
            "requires_network": "no",
            "changes_home_resolver": "only through legitimate package state/default APIs",
            "device_state_mutation": "none in this script",
            "observed_result": "Fire Launcher remains selected",
            "confidence": "Confirmed",
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.source.is_file():
        parser.error(f"source not found: {args.source}")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")
    rows = build_rows(args.source)
    if args.dry_run:
        print(f"DRY-RUN: read {args.source}; would write {args.output}")
        print(f"DRY-RUN: rows={len(rows)}; no ADB, network, APK, or device mutation")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {args.output} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
