#!/usr/bin/env python3
"""Audit package-management permission holders from a saved dumpsys package.

This is an offline parser.  It does not contact a device and does not infer
that a granted permission bypasses PackageManager's protected-package checks.
The input is expected to be an immutable raw capture from
capture_phase6mc_permission_holders.py.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


TARGET_PERMISSIONS = (
    "android.permission.CHANGE_COMPONENT_ENABLED_STATE",
    "android.permission.MANAGE_USERS",
    "android.permission.WRITE_SECURE_SETTINGS",
    "android.permission.INSTALL_PACKAGES",
    "android.permission.DELETE_PACKAGES",
    "android.permission.FORCE_STOP_PACKAGES",
)

PACKAGE_START = re.compile(r"^  Package \[([^\]]+)\] \([^)]*\):$", re.MULTILINE)
PERMISSION_LINE = re.compile(r"^      ([^:]+): granted=true(?:,.*)?$", re.MULTILINE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_class(code_path: str) -> str:
    if code_path.startswith("/system/priv-app/"):
        return "system-priv-app"
    if code_path.startswith("/system/app/"):
        return "system-app"
    if code_path.startswith("/product/priv-app/"):
        return "product-priv-app"
    if code_path.startswith("/product/app/"):
        return "product-app"
    if code_path.startswith("/vendor/priv-app/"):
        return "vendor-priv-app"
    if code_path.startswith("/vendor/app/"):
        return "vendor-app"
    if code_path.startswith("/data/app/"):
        return "data-app"
    if code_path:
        return "other"
    return "unknown"


def parse_packages(text: str) -> list[dict[str, str]]:
    starts = list(PACKAGE_START.finditer(text))
    rows: list[dict[str, str]] = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        block = text[match.start():end]
        package = match.group(1)
        code_match = re.search(r"^    codePath=(.*)$", block, re.MULTILINE)
        flags_match = re.search(r"^    flags=\[(.*)\]$", block, re.MULTILINE)
        private_match = re.search(r"^    privateFlags=\[(.*)\]$", block, re.MULTILINE)
        uid_match = re.search(r"^    userId=(.*)$", block, re.MULTILINE)
        shared_match = re.search(r"^    sharedUser=(.*)$", block, re.MULTILINE)
        granted = sorted({
            permission_match.group(1)
            for permission_match in PERMISSION_LINE.finditer(block)
            if permission_match.group(1) in TARGET_PERMISSIONS
        })
        rows.append({
            "package": package,
            "code_path": code_match.group(1).strip() if code_match else "",
            "source_class": source_class(code_match.group(1).strip()) if code_match else "unknown",
            "flags": flags_match.group(1).strip() if flags_match else "",
            "private_flags": private_match.group(1).strip() if private_match else "",
            "user_id": uid_match.group(1).strip() if uid_match else "",
            "shared_user": shared_match.group(1).strip() if shared_match else "",
            "granted_permissions": ";".join(granted),
            "system_app": "true" if "SYSTEM" in (flags_match.group(1) if flags_match else "") else "false",
            "privileged": "true" if "PRIVILEGED" in (private_match.group(1) if private_match else "") else "false",
            "fire_literal_in_dump_block": "true" if "com.amazon.firelauncher" in block else "false",
            "home_literal_in_dump_block": "true" if "android.intent.category.HOME" in block else "false",
        })
    return [row for row in rows if row["granted_permissions"]]


def permission_protection(text: str) -> dict[str, str]:
    protections: dict[str, str] = {}
    for permission in TARGET_PERMISSIONS:
        match = re.search(rf"^  Permission \[{re.escape(permission)}\].*?(?=^  Permission \[|\Z)", text, re.MULTILINE | re.DOTALL)
        if not match:
            protections[permission] = "UNKNOWN"
            continue
        prot = re.search(r"\bprot=([^,\n]+)", match.group(0))
        protections[permission] = prot.group(1).strip() if prot else "UNKNOWN"
    return protections


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "package", "code_path", "source_class", "user_id", "shared_user",
        "system_app", "privileged", "flags", "private_flags", "granted_permissions",
        "fire_literal_in_dump_block", "home_literal_in_dump_block",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dump", type=Path, required=True)
    parser.add_argument("--permission-dump", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "package_dump": str(args.package_dump),
            "permission_dump": str(args.permission_dump) if args.permission_dump else None,
            "output": str(args.output),
        }, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    text = args.package_dump.read_text(encoding="utf-8", errors="replace")
    rows = parse_packages(text)
    protection_text = args.permission_dump.read_text(encoding="utf-8", errors="replace") if args.permission_dump else text
    protections = permission_protection(protection_text)
    args.output.mkdir(parents=True)
    table_path = args.output / "permission-holders.csv"
    write_csv(table_path, rows)
    counts = {
        permission: sum(permission in row["granted_permissions"].split(";") for row in rows)
        for permission in TARGET_PERMISSIONS
    }
    summary = {
        "analysis": "offline-only",
        "input": str(args.package_dump),
        "input_sha256": sha256(args.package_dump),
        "permission_input": str(args.permission_dump) if args.permission_dump else None,
        "permission_input_sha256": sha256(args.permission_dump) if args.permission_dump else None,
        "target_permissions": list(TARGET_PERMISSIONS),
        "permission_protection": protections,
        "holder_counts": counts,
        "holder_rows": len(rows),
        "fire_literal_rows": [row["package"] for row in rows if row["fire_literal_in_dump_block"] == "true"],
        "home_literal_rows": [row["package"] for row in rows if row["home_literal_in_dump_block"] == "true"],
        "limitations": [
            "A granted permission does not establish a protected-package bypass.",
            "dumpsys package output is not a complete proof of code reachability or signing provenance.",
            "Rows are package-state observations; writer behavior requires separate static evidence.",
        ],
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
