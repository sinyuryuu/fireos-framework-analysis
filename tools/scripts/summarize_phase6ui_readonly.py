#!/usr/bin/env python3
"""Create a redacted summary from the Phase 6UI read-only snapshot."""

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


def prop(text: str, key: str) -> str:
    match = re.search(rf"^\[{re.escape(key)}\]: \[(.*?)\]$", text, re.MULTILINE)
    return match.group(1) if match else "UNKNOWN"


def first_line(path: Path) -> str:
    for line in read(path).splitlines():
        if line.strip():
            return line.strip()
    return "UNKNOWN"


def find(pattern: str, text: str, default: str = "UNKNOWN") -> str:
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1).strip() if match else default


def build(args: argparse.Namespace) -> None:
    source = Path(args.input).resolve()
    summary = Path(args.summary).resolve()
    table = Path(args.table).resolve()
    if args.dry_run:
        print("host-only dry run; no files written")
        print(f"input={source}")
        print(f"summary={summary}")
        print(f"table={table}")
        return
    if not source.is_dir():
        raise SystemExit(f"missing snapshot: {source}")
    if summary.exists() or table.exists():
        raise SystemExit("refusing to overwrite summary output")
    required = [
        source / "target_id.stdout.txt",
        source / "security_state.stdout.txt",
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

    props = read(source / "target_id.stdout.txt")
    security = read(source / "security_state.stdout.txt")
    resolve = read(source / "home_resolve.stdout.txt")
    candidates = read(source / "home_candidates.stdout.txt")
    activity = read(source / "activity.stdout.txt")
    window = read(source / "window.stdout.txt")
    users = read(source / "users.stdout.txt")
    package = read(source / "firelauncher_package.stdout.txt")
    manifest_hash = sha256(source / "sha256sums.txt")

    rows = [
        ("model", prop(props, "ro.product.model"), "target_id.stdout.txt", "Confirmed"),
        ("device", prop(props, "ro.product.device"), "target_id.stdout.txt", "Confirmed"),
        ("build_fingerprint", prop(props, "ro.build.fingerprint"), "target_id.stdout.txt", "Confirmed"),
        ("build_incremental", prop(props, "ro.build.version.incremental"), "target_id.stdout.txt", "Confirmed"),
        ("android_release", prop(props, "ro.build.version.release"), "target_id.stdout.txt", "Confirmed"),
        ("android_sdk", prop(props, "ro.build.version.sdk"), "target_id.stdout.txt", "Confirmed"),
        ("security_patch", prop(props, "ro.build.version.security_patch"), "target_id.stdout.txt", "Confirmed"),
        ("verified_boot_state", prop(props, "ro.boot.verifiedbootstate"), "target_id.stdout.txt", "Confirmed"),
        ("selinux", security.splitlines()[0].strip() if security else "UNKNOWN", "security_state.stdout.txt", "Confirmed"),
        ("home_resolve", first_line(source / "home_resolve.stdout.txt"), "home_resolve.stdout.txt", "Confirmed"),
        ("home_priority", find(r"^priority=(-?\d+)", resolve), "home_resolve.stdout.txt", "Confirmed"),
        ("home_candidate_count", str(len(re.findall(r"^  Activity #\d+:", candidates, re.MULTILINE))), "home_candidates.stdout.txt", "Confirmed"),
        ("fire_home_candidate", "yes" if "com.amazon.firelauncher" in candidates else "no", "home_candidates.stdout.txt", "Confirmed"),
        ("resumed_activity", find(r"mResumedActivity:.*?(com\.amazon\.firelauncher/\.Launcher)", activity), "activity.stdout.txt", "Observed"),
        ("current_focus", find(r"mCurrentFocus=.*?(com\.amazon\.firelauncher/com\.amazon\.firelauncher\.Launcher)", window), "window.stdout.txt", "Observed"),
        ("fire_user0_state_line", find(r"(?m)^(\s*User 0:.*)$", package), "firelauncher_package.stdout.txt", "Observed"),
        ("user_count", str(len(re.findall(r"^\s*UserInfo\{", users, re.MULTILINE))), "users.stdout.txt", "Confirmed"),
    ]

    table.parent.mkdir(parents=True, exist_ok=True)
    with table.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["field", "value", "source_file", "source_sha256", "classification"])
        for field, value, source_name, classification in rows:
            writer.writerow([field, value, source_name, sha256(source / source_name), classification])

    summary.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 6UI read-only device snapshot",
        "",
        "This redacted summary was generated from a serial-bound read-only ADB capture.",
        "The raw snapshot remains local because settings, service and package dumps may contain",
        "device-specific or account-related values.",
        "",
        f"Snapshot manifest SHA-256: `{manifest_hash}`",
        f"Raw snapshot (local): `{source}`",
        "",
        "## Safety",
        "",
        "Only getprop, read-only dumpsys, resolver queries, package/user/service/overlay lists,",
        "and settings list commands were used. No package, component, preferred activity, setting,",
        "user, Binder, driver, OTA, reboot, or partition state was changed.",
        "",
        "## Selected results",
        "",
        "| Field | Value | Classification |",
        "|---|---|---|",
    ]
    lines.extend(f"| `{field}` | `{value}` | {classification} |" for field, value, _source, classification in rows)
    lines.extend([
        "",
        "The complete command list, raw outputs, return codes and per-file hashes remain in the",
        "local snapshot directory. This summary does not claim that a visible service or static",
        "sink is reachable by shell or an ordinary application.",
        "",
    ])
    summary.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(summary)
    print(table)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--table", required=True)
    parser.add_argument("--dry-run", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
