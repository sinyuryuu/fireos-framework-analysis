#!/usr/bin/env python3
"""Create a compact public subset of a Phase 6AO read-only capture.

The complete local capture remains untouched. This exporter omits the full
logcat, full package dump, activity/window dumps, and raw getprop output, which
can contain unrelated user/device state. It performs no ADB operation and
never overwrites an existing output directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "adb/phase6ao/PHASE6AO-RO-20260805-01"
DEFAULT_OUTPUT = ROOT / "artifacts/phase6ao/public-summary-20260805-01"

COPY_FILES = (
    "target_state.stdout.txt",
    "target_id.stdout.txt",
    "target_selinux.stdout.txt",
    "target_uname.stdout.txt",
    "home_resolve.stdout.txt",
    "home_candidates_cmd.stdout.txt",
    "firelauncher_path.stdout.txt",
    "firelauncher_package_dump.stdout.txt",
    "preferred_xml.stdout.txt",
    "role_dump.stderr.txt",
    "service_list.stdout.txt",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prop(text: str, key: str) -> str:
    match = re.search(rf"^\[{re.escape(key)}\]: \[(.*?)\]$", text, re.MULTILINE)
    return match.group(1) if match else "NOT_OBSERVED"


def package_summary(source: Path, package: str, keep_home_filter: bool = False) -> str:
    lines = (source / f"{package}_package_dump.stdout.txt").read_text(
        encoding="utf-8", errors="replace"
    ).splitlines()
    wanted: list[str] = []
    metadata_prefixes = (
        "  Package [",
        "    userId=",
        "    codePath=",
        "    resourcePath=",
        "    versionCode=",
        "    versionName=",
        "    flags=",
        "    privateFlags=",
        "    pkgFlags=",
    )
    for line in lines:
        if line.startswith(metadata_prefixes):
            wanted.append(line)
        if keep_home_filter and (
            'Action: "android.intent.action.MAIN"' in line
            or 'Category: "android.intent.category.HOME"' in line
            or 'Category: "android.intent.category.SETUP_WIZARD"' in line
            or "mPriority=100" in line
        ):
            wanted.append(line)
    return "\n".join(wanted) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(json.dumps({
            "host_only": True,
            "device_contacted": False,
            "source": str(args.source),
            "output": str(args.output),
            "omitted": ["logcat_all_dump", "package_dump_full", "activity/window dumps", "raw getprop"],
        }, indent=2))
        return 0

    if not args.source.is_dir():
        raise SystemExit(f"missing source capture: {args.source}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    metadata_path = args.source / "metadata.json"
    build_path = args.source / "build_properties.stdout.txt"
    if not metadata_path.is_file() or not build_path.is_file():
        raise SystemExit("source capture lacks metadata.json or build_properties.stdout.txt")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True)
    for name in COPY_FILES:
        source = args.source / name
        if not source.is_file():
            raise SystemExit(f"missing source evidence: {source}")
        shutil.copyfile(source, args.output / name)

    (args.output / "ota_package_summary.txt").write_text(
        package_summary(args.source, "ota"), encoding="utf-8"
    )
    (args.output / "oobe_package_summary.txt").write_text(
        package_summary(args.source, "oobe", keep_home_filter=True), encoding="utf-8"
    )

    source_manifest = {}
    source_hash_file = args.source / "sha256sums.txt"
    for line in source_hash_file.read_text(encoding="utf-8").splitlines():
        if "  " not in line:
            continue
        digest, name = line.split("  ", 1)
        if name in COPY_FILES or name in {
            "metadata.json", "build_properties.stdout.txt",
            "ota_package_dump.stdout.txt", "oobe_package_dump.stdout.txt",
        }:
            source_manifest[name] = digest

    build_text = build_path.read_text(encoding="utf-8", errors="replace")
    summary = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "source_capture": str(args.source),
        "source_metadata_sha256": sha256(metadata_path),
        "source_build_fingerprint": prop(build_text, "ro.build.fingerprint"),
        "source_device_serial": "REDACTED_IN_PUBLIC_SUMMARY",
        "source_command_count": len(metadata.get("commands", [])),
        "source_flags": {
            "mutating_commands": metadata.get("mutating_commands"),
            "binder_transactions_invoked": metadata.get("binder_transactions_invoked"),
            "intents_or_broadcasts_sent": metadata.get("intents_or_broadcasts_sent"),
            "settings_changed": metadata.get("settings_changed"),
            "package_state_changed": metadata.get("package_state_changed"),
            "reboot_requested": metadata.get("reboot_requested"),
            "partition_written": metadata.get("partition_written"),
        },
        "omitted_from_public_subset": [
            "logcat_all_dump.stdout.txt",
            "package_dump_full.stdout.txt",
            "activity_activities.stdout.txt",
            "activity_recents.stdout.txt",
            "activity_top.stdout.txt",
            "window_windows.stdout.txt",
            "build_properties.stdout.txt",
        ],
        "source_sha256": source_manifest,
    }
    (args.output / "runtime-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    files = sorted(path for path in args.output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(args.output),
        "host_only": True,
        "device_contacted": False,
        "copied_files": len(COPY_FILES),
        "omitted_sensitive_or_unrelated_dumps": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
