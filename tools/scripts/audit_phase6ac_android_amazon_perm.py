#!/usr/bin/env python3
"""Audit the android.amazon.perm APK protected-broadcast declarations offline.

This tool is intentionally host-only.  It reads one preserved APK and invokes
the local Android Asset Packaging Tool to decode its binary manifest.  It never
contacts ADB, sends a broadcast, calls Binder, starts an Android component, or
modifies a device.
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


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_APK = ROOT / "artifacts/phase6ac/android-amazon-perm-device-20260805-01/android.amazon.perm.apk"
DEFAULT_AAPT = Path("/opt/homebrew/share/android-commandlinetools/build-tools/35.0.0/aapt")
TARGET_ACTION = "amazon.intent.action.BOOT_AFTER_SYSTEM_OTA"
TARGET_PERMISSION = "com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_manifest(text: str) -> tuple[str, str, list[str]]:
    package = "UNKNOWN"
    shared_uid = "NOT_OBSERVED"
    package_match = re.search(r'package="([^"]+)"', text)
    uid_match = re.search(r'android:sharedUserId\([^)]*\)="([^"]+)"', text)
    if package_match:
        package = package_match.group(1)
    if uid_match:
        shared_uid = uid_match.group(1)

    protected: list[str] = []
    in_protected = False
    for line in text.splitlines():
        if re.search(r"\bE:\s+protected-broadcast\b", line):
            in_protected = True
            continue
        if in_protected:
            name_match = re.search(r'android:name\([^)]*\)="([^"]+)"', line)
            if name_match:
                protected.append(name_match.group(1))
                in_protected = False
            elif re.match(r"\s*E:\s+", line):
                in_protected = False
    return package, shared_uid, protected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, default=DEFAULT_APK)
    parser.add_argument("--aapt", type=Path, default=DEFAULT_AAPT)
    parser.add_argument("--target-action", default=TARGET_ACTION)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "host_only": True,
            "device_contacted": False,
            "broadcast_sent": False,
            "binder_transaction_sent": False,
            "apk": str(args.apk),
            "aapt": str(args.aapt),
            "target_action": args.target_action,
            "output": str(args.output),
        }, indent=2, sort_keys=True))
        return 0

    if not args.apk.is_file():
        raise SystemExit(f"missing APK: {args.apk}")
    if not args.aapt.is_file():
        raise SystemExit(f"missing aapt: {args.aapt}")

    args.output.mkdir(parents=True)
    command = [str(args.aapt), "dump", "xmltree", str(args.apk), "AndroidManifest.xml"]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise SystemExit(
            f"aapt failed with exit {completed.returncode}: {completed.stderr.strip()}"
        )

    manifest_text = completed.stdout
    package, shared_uid, protected = parse_manifest(manifest_text)
    target_present = args.target_action in protected
    permission_present = args.target_action in manifest_text or TARGET_PERMISSION in manifest_text

    manifest_path = args.output / "manifest-aapt.xmltree.txt"
    manifest_path.write_text(manifest_text, encoding="utf-8")
    rows = [
        {
            "source_package": package,
            "shared_user_id": shared_uid,
            "protected_broadcast": action,
            "is_target_action": str(action == args.target_action).lower(),
            "target_permission_string_observed": str(TARGET_PERMISSION in manifest_text).lower(),
        }
        for action in protected
    ]
    write_csv(
        args.output / "protected-broadcasts.csv",
        ["source_package", "shared_user_id", "protected_broadcast", "is_target_action", "target_permission_string_observed"],
        rows,
    )

    input_sha = {
        "apk": str(args.apk),
        "apk_sha256": sha256(args.apk),
        "aapt": str(args.aapt),
        "target_action": args.target_action,
        "target_permission": TARGET_PERMISSION,
    }
    (args.output / "input.json").write_text(json.dumps(input_sha, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    classification = (
        "CONFIRMED_PROTECTED_BROADCAST_IN_SOURCE_PACKAGE"
        if target_present
        else "BOUNDED_NEGATIVE_FOR_SOURCE_PACKAGE"
    )
    summary = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "broadcast_sent": False,
        "binder_transaction_sent": False,
        "ota_executed": False,
        "partition_written": False,
        "source_package": package,
        "shared_user_id": shared_uid,
        "protected_broadcast_count": len(protected),
        "protected_broadcasts": protected,
        "target_action": args.target_action,
        "target_action_present_in_this_manifest": target_present,
        "target_permission_string_present_in_this_manifest": permission_present,
        "classification": classification,
        "limitation": "Other system packages or runtime inputs could still contribute to mProtectedBroadcasts; this APK manifest alone is not a global runtime proof.",
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = f"""# Phase 6AC：android.amazon.perm protected-broadcast audit

## Result

- Source package: `{package}`
- Shared user ID: `{shared_uid}`
- Protected-broadcast declarations in this manifest: **{len(protected)}**
- Target action: `{args.target_action}`
- Target action in this manifest: **{target_present}**
- Classification: **{classification}**

The package manifest contains the protected broadcasts listed in
`protected-broadcasts.csv`; the target `BOOT_AFTER_SYSTEM_OTA` action is present
in this manifest when `target_action_present_in_this_manifest` is true. This is
stronger than a string search over an unrelated framework manifest because
`android.amazon.perm` is the saved source package for the
`RECEIVE_BOOT_AFTER_SYSTEM_OTA` permission. It still does not prove that no
other system package or runtime source can add or remove the action from
`PackageManagerService.mProtectedBroadcasts`.

## Safety

This run was host-only.  No ADB, broadcast, Binder transaction, OTA/recovery,
package/settings mutation, reboot, or partition operation was performed.
"""
    (args.output / "result.md").write_text(result, encoding="utf-8")

    manifest_lines = []
    for path in sorted(args.output.iterdir()):
        if path.name == "sha256sums.txt" or not path.is_file():
            continue
        manifest_lines.append(f"{sha256(path)}  {path.name}")
    (args.output / "sha256sums.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
