#!/usr/bin/env python3
"""Inventory holders of CHANGE_COMPONENT_ENABLED_STATE from a saved dump.

Host-only parser for an already-collected ``dumpsys package`` output.  It
does not contact a device, grant permissions, call PackageManager, execute an
APK, or mutate package state.  A granted permission is reported as a holder
fact only; this script does not infer that the holder can disable a protected
package.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "artifacts/phase6j/phase6j-ota-controller-holders-20260805-01/dumpsys_package_all.stdout.txt"
PERMISSION = "android.permission.CHANGE_COMPONENT_ENABLED_STATE"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def blocks(text: str) -> list[tuple[str, list[str], int]]:
    lines = text.splitlines()
    starts = [(i, line) for i, line in enumerate(lines) if line.startswith("  Package [")]
    shared_users = next((i for i, line in enumerate(lines) if line == "Shared users:"), len(lines))
    output: list[tuple[str, list[str], int]] = []
    for index, (start, header) in enumerate(starts):
        next_package = starts[index + 1][0] if index + 1 < len(starts) else len(lines)
        end = min(next_package, shared_users)
        match = re.search(r"Package \[([^\]]+)\]", header)
        if match:
            output.append((match.group(1), lines[start:end], start + 1))
    return output


def value(lines: list[str], prefix: str) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix):].strip()
    return ""


def user_states(lines: list[str]) -> str:
    # Only package-state headings are four-space-indented in this dump.  Do
    # not collect nested fields such as ``User 0: ceDataInode=...``.
    return " | ".join(line.strip() for line in lines if line.startswith("    User "))


def classify(package: str, code_path: str, private_flags: str) -> str:
    if "PRIVILEGED" in private_flags or "/system/" in code_path:
        return "system_or_privileged_holder"
    if package == "com.android.vending" and code_path.startswith("/data/"):
        return "data_app_grant_needs_provenance_review"
    return "non_privileged_snapshot_holder_needs_review"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output/tables/phase6lz-component-state-permissions")
    args = parser.parse_args()
    if not args.input.exists():
        raise SystemExit(f"missing input: {args.input}")

    text = args.input.read_text(encoding="utf-8", errors="replace")
    rows: list[dict[str, str]] = []
    for package, body, header_line in blocks(text):
        if not any(f"{PERMISSION}: granted=true" in line for line in body):
            continue
        code_path = value(body, "codePath=")
        private_flags = value(body, "privateFlags=")
        rows.append({
            "package": package,
            "header_line": str(header_line),
            "user_id": value(body, "userId="),
            "code_path": code_path,
            "pkg_flags": value(body, "pkgFlags="),
            "private_flags": private_flags,
            "signatures": value(body, "signatures="),
            "user_states": user_states(body),
            "permission": PERMISSION,
            "classification": classify(package, code_path, private_flags),
            "interpretation": "holder fact only; protected-package gate and caller contract remain separate",
        })

    args.output_dir.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else [
        "package", "header_line", "user_id", "code_path", "pkg_flags", "private_flags",
        "signatures", "user_states", "permission", "classification", "interpretation",
    ]
    with (args.output_dir / "component-state-permission-holders.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "input": str(args.input.relative_to(ROOT)),
        "input_sha256": sha256(args.input),
        "permission": PERMISSION,
        "holder_count": len(rows),
        "device_actions": "none",
        "warning": "A holder does not prove access to a protected package or a HOME writer.",
    }
    (args.output_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
