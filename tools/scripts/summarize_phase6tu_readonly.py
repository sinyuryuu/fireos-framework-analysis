#!/usr/bin/env python3
"""Create a redacted summary of the Phase 6TU read-only device snapshot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def prop(text: str, key: str) -> str:
    match = re.search(rf"^\[{re.escape(key)}\]: \[(.*?)\]$", text, re.MULTILINE)
    return match.group(1) if match else "UNKNOWN"


def first(path: Path) -> str:
    lines = [line.strip() for line in read(path).splitlines() if line.strip()]
    return lines[0] if lines else "UNKNOWN"


def build(args: argparse.Namespace) -> None:
    root = Path(args.input).resolve()
    report_path = Path(args.report).resolve()
    table_path = Path(args.table).resolve()
    if args.dry_run:
        print(f"input={root}")
        print(f"report={report_path}")
        print(f"table={table_path}")
        print("dry-run: no files written")
        return
    if not root.is_dir():
        raise SystemExit(f"missing snapshot: {root}")
    if report_path.exists() or table_path.exists():
        raise SystemExit("refusing to overwrite summary output")

    target = root / "target_id.stdout.txt"
    security = root / "security_state.stdout.txt"
    resolve = root / "home_resolve.stdout.txt"
    candidates = root / "home_candidates.stdout.txt"
    users = root / "users.stdout.txt"
    required = [target, security, resolve, candidates, users]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit("missing selected evidence:\n" + "\n".join(missing))

    target_text = read(target)
    security_text = read(security)
    user_lines = [line.strip() for line in read(users).splitlines() if "UserInfo{" in line]
    user_summary = "; ".join(
        re.sub(r"UserInfo\{[^}]+", "UserInfo{REDACTED", line) for line in user_lines
    ) or "UNKNOWN"
    values = [
        ("model", prop(target_text, "ro.product.model"), target),
        ("device", prop(target_text, "ro.product.device"), target),
        ("build_fingerprint", prop(target_text, "ro.build.fingerprint"), target),
        ("build_incremental", prop(target_text, "ro.build.version.incremental"), target),
        ("android_release", prop(target_text, "ro.build.version.release"), target),
        ("android_sdk", prop(target_text, "ro.build.version.sdk"), target),
        ("security_patch", prop(target_text, "ro.build.version.security_patch"), target),
        ("verified_boot_state", prop(target_text, "ro.boot.verifiedbootstate"), target),
        ("selinux", security_text.splitlines()[0].strip() if security_text else "UNKNOWN", security),
        ("home_resolve", first(resolve), resolve),
        ("home_candidates_fire", "yes" if "com.amazon.firelauncher" in read(candidates) else "no", candidates),
        ("user_list", user_summary, users),
    ]

    table_path.parent.mkdir(parents=True, exist_ok=True)
    with table_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["field", "value", "evidence_file", "evidence_sha256", "classification"])
        for field, value, evidence in values:
            writer.writerow([
                field,
                value,
                str(evidence.relative_to(Path.cwd())) if evidence.is_relative_to(Path.cwd()) else evidence.name,
                digest(evidence),
                "READONLY_OBSERVED",
            ])

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "# Phase 6TU read-only device snapshot\n\n"
        "This is a redacted summary. The raw snapshot remains local because settings and "
        "service output may contain account- or device-specific data.\n\n"
        "## Safety\n\n"
        "The capture used only `getprop`, `dumpsys`, `cmd package` query/resolve, `pm list "
        "users`, `service list`, `cmd overlay list`, and settings list commands. No package, "
        "component, preferred activity, setting, user, Binder, driver, OTA, reboot, or partition "
        "state was changed.\n\n"
        "## Observed state\n\n"
        + "\n".join(f"- **{field}:** `{value}`" for field, value, _ in values)
        + "\n\n"
        "`home_resolve` is the complete first line of the resolver output; the raw candidate and "
        "preferred dumps remain in the local snapshot. The table records SHA-256 for each selected "
        "raw evidence file.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {report_path} and {table_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--table", required=True)
    parser.add_argument("--dry-run", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
