#!/usr/bin/env python3
"""Inventory protected-broadcast declarations in preserved APK manifests.

This is a host-only provenance audit.  It never contacts ADB, starts an
Android component, sends a broadcast, calls Binder, mutates a package/settings
state, or changes an input APK.  The scan is intentionally scoped by explicit
APK files/directories so test and third-party APKs are not silently treated as
system provenance.
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
DEFAULT_AAPT = Path("/opt/homebrew/share/android-commandlinetools/build-tools/35.0.0/aapt")
TARGET_ACTION = "amazon.intent.action.BOOT_AFTER_SYSTEM_OTA"
TARGET_PERMISSION = "com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    waiting_for_name = False
    for line in text.splitlines():
        if re.search(r"\bE:\s+protected-broadcast\b", line):
            waiting_for_name = True
            continue
        if waiting_for_name:
            name_match = re.search(r'android:name\([^)]*\)="([^"]+)"', line)
            if name_match:
                protected.append(name_match.group(1))
                waiting_for_name = False
            elif re.match(r"\s*E:\s+", line):
                waiting_for_name = False
    return package, shared_uid, protected


def collect_apks(files: list[Path], roots: list[Path]) -> list[Path]:
    paths = set(path.resolve() for path in files)
    for root in roots:
        root = root.resolve()
        if root.is_file() and root.suffix.lower() == ".apk":
            paths.add(root)
        elif root.is_dir():
            paths.update(path.resolve() for path in root.rglob("*.apk"))
    return sorted(path for path in paths if path.is_file())


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", action="append", type=Path, default=[])
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--aapt", type=Path, default=DEFAULT_AAPT)
    parser.add_argument("--target-action", default=TARGET_ACTION)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    apks = collect_apks(args.apk, args.root)
    if not apks:
        raise SystemExit("no APK inputs were found")

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "host_only": True,
            "device_contacted": False,
            "broadcast_sent": False,
            "binder_transaction_sent": False,
            "apk_count": len(apks),
            "apks": [str(path) for path in apks],
            "aapt": str(args.aapt),
            "target_action": args.target_action,
            "output": str(args.output),
        }, indent=2, sort_keys=True))
        return 0

    if not args.aapt.is_file():
        raise SystemExit(f"missing aapt: {args.aapt}")

    args.output.mkdir(parents=True)
    manifest_dir = args.output / "manifests"
    manifest_dir.mkdir()
    rows: list[dict[str, object]] = []
    input_rows: list[dict[str, object]] = []

    for index, apk in enumerate(apks, start=1):
        digest = sha256(apk)
        input_rows.append({"apk": str(apk), "sha256": digest})
        command = [str(args.aapt), "dump", "xmltree", str(apk), "AndroidManifest.xml"]
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        raw_path = manifest_dir / f"{index:03d}_{apk.stem}.xmltree.txt"
        raw_path.write_text(result.stdout, encoding="utf-8")
        (manifest_dir / f"{index:03d}_{apk.stem}.stderr.txt").write_text(result.stderr, encoding="utf-8")
        if result.returncode == 0:
            package, shared_uid, protected = parse_manifest(result.stdout)
            status = "OK"
        else:
            package, shared_uid, protected = "UNKNOWN", "UNKNOWN", []
            status = f"AAPT_EXIT_{result.returncode}"
        rows.append({
            "apk": str(apk),
            "apk_sha256": digest,
            "package": package,
            "shared_user_id": shared_uid,
            "protected_broadcast_count": len(protected),
            "target_action_present": str(args.target_action in protected).lower(),
            "target_permission_string_present": str(TARGET_PERMISSION in result.stdout).lower(),
            "aapt_status": status,
        })
        for action_index, action in enumerate(protected, start=1):
            rows.append({
                "apk": str(apk),
                "apk_sha256": digest,
                "package": package,
                "shared_user_id": shared_uid,
                "protected_broadcast_count": len(protected),
                "target_action_present": str(action == args.target_action).lower(),
                "target_permission_string_present": str(TARGET_PERMISSION in result.stdout).lower(),
                "aapt_status": f"PROTECTED_BROADCAST:{action}",
            })

    write_csv(
        args.output / "protected-broadcast-inventory.csv",
        ["apk", "apk_sha256", "package", "shared_user_id", "protected_broadcast_count", "target_action_present", "target_permission_string_present", "aapt_status"],
        rows,
    )
    write_csv(args.output / "input-sha256.csv", ["apk", "sha256"], input_rows)

    target_rows = [row for row in rows if row["aapt_status"] == "PROTECTED_BROADCAST:" + args.target_action]
    aapt_failures = [row for row in rows if str(row["aapt_status"]).startswith("AAPT_EXIT_")]
    summary = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "broadcast_sent": False,
        "binder_transaction_sent": False,
        "ota_executed": False,
        "partition_written": False,
        "input_apk_count": len(apks),
        "target_action": args.target_action,
        "target_permission": TARGET_PERMISSION,
        "target_source_rows": target_rows,
        "aapt_failure_count": len(aapt_failures),
        "scope_limitation": "Only explicitly supplied preserved APKs were scanned; this is not a global runtime PackageManager inventory.",
        "classification": "CONFIRMED_IN_SCANNED_SOURCES" if target_rows else "NOT_FOUND_IN_SCANNED_SOURCES",
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    graph_lines = [
        "flowchart TD",
        "    A[Explicit preserved PS7331 APK scope] --> B[aapt manifest parser]",
        "    B --> C{BOOT_AFTER_SYSTEM_OTA protected-broadcast?}",
        "    C -->|yes| D[Source-package membership confirmed]",
        "    C -->|no| E[No declaration in this APK scope]",
        "    D -. not a global runtime inventory .-> F[Other packages/runtime inputs remain out of scope]",
    ]
    (args.output / "protected-broadcast-inventory.mmd").write_text("\n".join(graph_lines) + "\n", encoding="utf-8")

    result_text = f"""# Phase 6AD：saved APK protected-broadcast inventory

- Explicit APK inputs: **{len(apks)}**
- Target action: `{args.target_action}`
- Target declarations in scanned scope: **{len(target_rows)}**
- AAPT failures: **{len(aapt_failures)}**
- Classification: **{summary['classification']}**

This is host-only provenance analysis over the explicitly supplied preserved APKs.
It does not prove the complete runtime `PackageManagerService.mProtectedBroadcasts`
set and does not make manual broadcast delivery safe.

No ADB, broadcast, Binder transaction, OTA/recovery operation, package/settings
mutation, reboot, or partition write was performed.
"""
    (args.output / "result.md").write_text(result_text, encoding="utf-8")

    manifest_lines = []
    for path in sorted(args.output.rglob("*")):
        if not path.is_file() or path.name == "sha256sums.txt":
            continue
        manifest_lines.append(f"{sha256(path)}  {path.relative_to(args.output)}")
    (args.output / "sha256sums.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
