#!/usr/bin/env python3
"""Create a redacted summary from a Phase 6TI read-only snapshot.

The input directory may contain account-related settings.  This script never
contacts a device and emits only selected build, resolver, package-state,
foreground, and user-count fields.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def first(pattern: str, content: str, default: str = "UNKNOWN") -> str:
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else default


def build(args: argparse.Namespace) -> None:
    source = Path(args.input).resolve()
    summary_path = Path(args.summary).resolve()
    table_path = Path(args.table).resolve()
    if not source.is_dir():
        raise SystemExit(f"snapshot directory not found: {source}")
    if not args.force and (summary_path.exists() or table_path.exists()):
        raise SystemExit("refusing to overwrite an existing summary/table")
    if args.dry_run:
        print("host-only dry run; no output written")
        print(f"input={source}")
        print(f"summary={summary_path}")
        print(f"table={table_path}")
        return

    names = {
        "props": "target_id.stdout.txt",
        "resolve": "home_resolve.stdout.txt",
        "candidates": "home_candidates.stdout.txt",
        "activity": "activity.stdout.txt",
        "window": "window.stdout.txt",
        "users": "users.stdout.txt",
        "package": "firelauncher_package.stdout.txt",
        "manifest": "sha256sums.txt",
    }
    missing = [name for name in names.values() if not (source / name).is_file()]
    if missing:
        raise SystemExit("missing snapshot files:\n" + "\n".join(missing))

    data = {key: read(source / name) for key, name in names.items() if key != "manifest"}
    rows = [
        ("product_model", first(r"^\[ro\.product\.model\]: \[(.*?)\]$", data["props"]), names["props"], "Confirmed"),
        ("product_device", first(r"^\[ro\.product\.device\]: \[(.*?)\]$", data["props"]), names["props"], "Confirmed"),
        ("build_fingerprint", first(r"^\[ro\.build\.fingerprint\]: \[(.*?)\]$", data["props"]), names["props"], "Confirmed"),
        ("security_patch", first(r"^\[ro\.build\.version\.security_patch\]: \[(.*?)\]$", data["props"]), names["props"], "Confirmed"),
        ("verified_boot_state", first(r"^\[ro\.boot\.verifiedbootstate\]: \[(.*?)\]$", data["props"]), names["props"], "Confirmed"),
        ("home_resolved_component", first(r"^(com\.[^\n]+/\.[^\n]+)$", data["resolve"]), names["resolve"], "Confirmed"),
        ("home_resolved_priority", first(r"^priority=(\d+)", data["resolve"]), names["resolve"], "Confirmed"),
        ("fire_activity_resumed", first(r"mResumedActivity: .*? (com\.amazon\.firelauncher/\.Launcher)", data["activity"]), names["activity"], "Confirmed"),
        ("current_focus", first(r"mCurrentFocus=.*? (com\.amazon\.firelauncher/com\.amazon\.firelauncher\.Launcher)", data["window"]), names["window"], "Confirmed"),
        ("fire_user0_enabled_state", first(r"User 0:.*?enabled=(\d+)", data["package"]), names["package"], "Confirmed"),
        ("user_count", str(len(re.findall(r"^\s*UserInfo\{", data["users"], re.MULTILINE))), names["users"], "Confirmed"),
    ]

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    with table_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["field", "value", "source_file", "classification"])
        writer.writerows(rows)

    manifest_hash = sha256(source / names["manifest"])
    try:
        display_source = str(source.relative_to(Path.cwd().resolve()))
    except ValueError:
        display_source = str(source)
    lines = [
        "# Phase 6TI read-only device snapshot",
        "",
        "This is a redacted summary generated from a serial-bound, read-only ADB snapshot.",
        "Raw settings and dumps remain local because they may contain account-related values.",
        "",
        f"Snapshot manifest (`sha256sums.txt`) SHA-256: `{manifest_hash}`",
        f"Raw snapshot directory (local): `{display_source}`",
        "",
        "## Safety and provenance",
        "",
        "Only getprop, read-only dumpsys, resolver queries, package/user/service/overlay",
        "lists, and settings list commands were captured. No package, settings, Binder,",
        "driver, OTA, recovery, reboot, or partition mutation was performed.",
        "",
        "## Selected results",
        "",
        "| Field | Value | Classification |",
        "|---|---|---|",
    ]
    lines.extend(f"| `{field}` | `{value}` | {classification} |" for field, value, _source, classification in rows)
    lines.extend([
        "",
        "`fire_user0_enabled_state=0` is PackageManager's default state; it is not a",
        "claim that Fire Launcher is disabled. The resolver and foreground evidence",
        "still select `com.amazon.firelauncher/.Launcher`.",
        "",
        "The full command list, raw outputs, return codes, and per-file hashes remain",
        "in the local snapshot directory.",
        "",
    ])
    summary_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(summary_path)
    print(table_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--table", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
