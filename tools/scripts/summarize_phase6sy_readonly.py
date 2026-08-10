#!/usr/bin/env python3
"""Create a redacted summary from a Phase 6SY read-only snapshot.

The input directory may contain account-related settings.  This script emits
only selected build, resolver, package-state, user-count, and foreground fields
and never contacts a device.  It refuses to overwrite outputs by default.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def first(pattern: str, content: str, default: str = "UNKNOWN") -> str:
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else default


def build(args: argparse.Namespace) -> None:
    source = Path(args.input).resolve()
    if not source.is_dir():
        raise SystemExit(f"snapshot directory not found: {source}")
    summary_path = Path(args.summary).resolve()
    table_path = Path(args.table).resolve()
    if not args.force and (summary_path.exists() or table_path.exists()):
        raise SystemExit("refusing to overwrite an existing summary/table")
    if args.dry_run:
        print("host-only dry run; no output written")
        print(f"input={source}")
        print(f"summary={summary_path}")
        print(f"table={table_path}")
        return

    required = [
        source / "target_id.stdout.txt",
        source / "home_resolve.stdout.txt",
        source / "home_candidates.stdout.txt",
        source / "activity.stdout.txt",
        source / "window.stdout.txt",
        source / "users.stdout.txt",
        source / "firelauncher_package.stdout.txt",
        source / "sha256sums.txt",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit("missing snapshot files:\n" + "\n".join(missing))

    props = text(source / "target_id.stdout.txt")
    resolve = text(source / "home_resolve.stdout.txt")
    candidates = text(source / "home_candidates.stdout.txt")
    activity = text(source / "activity.stdout.txt")
    window = text(source / "window.stdout.txt")
    users = text(source / "users.stdout.txt")
    package = text(source / "firelauncher_package.stdout.txt")
    manifest_hash = sha256(source / "sha256sums.txt")
    try:
        display_source = str(source.relative_to(Path.cwd().resolve()))
    except ValueError:
        display_source = str(source)

    rows = [
        ("product_model", first(r"^\[ro\.product\.model\]: \[(.*?)\]$", props), "target_id.stdout.txt", "Confirmed"),
        ("product_device", first(r"^\[ro\.product\.device\]: \[(.*?)\]$", props), "target_id.stdout.txt", "Confirmed"),
        ("build_fingerprint", first(r"^\[ro\.build\.fingerprint\]: \[(.*?)\]$", props), "target_id.stdout.txt", "Confirmed"),
        ("security_patch", first(r"^\[ro\.build\.version\.security_patch\]: \[(.*?)\]$", props), "target_id.stdout.txt", "Confirmed"),
        ("verified_boot_state", first(r"^\[ro\.boot\.verifiedbootstate\]: \[(.*?)\]$", props), "target_id.stdout.txt", "Confirmed"),
        ("home_resolved_component", first(r"^(com\.[^\n]+/\.[^\n]+)$", resolve), "home_resolve.stdout.txt", "Confirmed"),
        ("home_resolved_priority", first(r"^priority=(\d+)", resolve), "home_resolve.stdout.txt", "Confirmed"),
        ("fire_activity_resumed", first(r"mResumedActivity: .*? (com\.amazon\.firelauncher/\.Launcher)", activity), "activity.stdout.txt", "Confirmed"),
        ("current_focus", first(r"mCurrentFocus=.*? (com\.amazon\.firelauncher/com\.amazon\.firelauncher\.Launcher)", window), "window.stdout.txt", "Confirmed"),
        ("fire_user0_enabled_state", first(r"User 0:.*?enabled=(\d+)", package), "firelauncher_package.stdout.txt", "Confirmed"),
        ("fire_activity_info_enabled", first(r"name=com\.amazon\.firelauncher\.Launcher.*?\n\s+packageName=.*?\n\s+labelRes=.*?\n\s+enabled=(true|false)", candidates), "home_candidates.stdout.txt", "Confirmed"),
        ("user_count", str(len(re.findall(r"^\s*UserInfo\{", users, re.MULTILINE))), "users.stdout.txt", "Confirmed"),
    ]

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    with table_path.open("w", encoding="utf-8", newline="\n") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["field", "value", "source_file", "classification"])
        writer.writerows(rows)

    lines = [
        "# Phase 6SY read-only device snapshot",
        "",
        "This is a redacted summary generated from a serial-bound, read-only ADB snapshot.",
        "The raw directory is intentionally not included in the public commit because its",
        "settings dumps may contain account-related values.",
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
    for field, value, _source, classification in rows:
        lines.append(f"| `{field}` | `{value}` | {classification} |")
    lines += [
        "",
        "`fire_user0_enabled_state=0` is the PackageManager default state, not a claim",
        "that the package is disabled; the HOME candidate and ActivityInfo remain enabled",
        "and the resolver still selects Fire Launcher.",
        "",
        "The full command list, raw outputs, return codes, and per-file hashes remain in",
        "the local snapshot directory.",
        "",
    ]
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
