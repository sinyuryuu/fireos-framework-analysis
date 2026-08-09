#!/usr/bin/env python3
"""Bounded, host-only closure audit for PS7331 custom kernel drivers.

This scanner reads source text only.  It does not invoke adb, execute an ELF,
open a device node, issue an ioctl, load a module, or write an output into the
source tree.  Its purpose is narrower than the Phase 6N surface index: it
normalizes registration -> fops/user-copy -> local-gate -> control-plane
markers and records whether an Android framework/HOME sink is directly visible
in the selected source files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


DEFAULT_MANIFEST = Path("kernel/source-manifest.json")
DEFAULT_OUTPUT = Path("artifacts/phase6me-driver-control-edges-20260810-01")

SOURCE_EXTENSIONS = {".c", ".h", ".cc", ".cpp", ".inc"}
SKIP_PARTS = {".git", "output", "venv", "prebuilt", "toolchain", "host"}

SCOPES = (
    "drivers/misc/mediatek",
    "drivers/staging/amazon",
    "drivers/staging/android/ion",
    "drivers/input",
    "drivers/power/mediatek",
    "drivers/usb",
    "drivers/char",
)

MARKERS: dict[str, re.Pattern[str]] = {
    "ioctl_entry": re.compile(r"\b(?:unlocked_ioctl|compat_ioctl|ioctl)\b|\.ioctl\s*=|_IO[RW]*\s*\("),
    "user_copy": re.compile(r"\b(?:copy_from_user|copy_to_user|__copy_from_user|access_ok)\s*\("),
    "proc_sysfs_debugfs_registration": re.compile(
        r"\b(?:proc_create|proc_mkdir|debugfs_create|device_create_file|device_create_with_groups|sysfs_create)\w*\s*\("
    ),
    "device_registration": re.compile(
        r"\b(?:misc_register|register_chrdev|alloc_chrdev_region|cdev_add|class_create|device_create|platform_driver_register|usb_register)\w*\s*\("
    ),
    "local_gate": re.compile(
        r"\b(?:capable|ns_capable|current_uid|current_euid|current_fsuid|uid_eq|gid_eq|in_egroup_p|file->f_cred|current->cred|security_\w+)\b"
    ),
    "uevent_or_netlink": re.compile(r"\b(?:kobject_uevent|netlink|uevent|NETLINK_)\w*\b"),
    "trusted_execution": re.compile(r"\b(?:call_usermodehelper|request_module|kernel_execve|do_execve)\s*\("),
    "secure_world": re.compile(r"\b(?:arm_smccc|smc_call|mt_secure_call|kree_|tz_|MTEE|geniezone|trustzone)\w*\b", re.I),
    "property_or_boot_state": re.compile(r"\b(?:androidboot\.|property_get|sysfs|procfs|boot_mode|factory_mode|eng(?:ineering)?_mode)\b", re.I),
    # Keep these deliberately narrow.  Common kernel identifiers such as
    # `system_server_pid` and comments mentioning a framework class are not a
    # framework data-flow edge.
    "framework_sink_literal": re.compile(
        r"(?:\b(?:setComponentEnabledSetting|setApplicationEnabledSetting|setHomeActivity)\s*\(|"
        r"\b(?:PackageManagerService|ActivityManagerService|ActivityTaskManagerService)\s*(?:->|::))",
        re.I,
    ),
    "launcher_sink_literal": re.compile(
        r"(?:[\"']com\.amazon\.firelauncher[\"']|[\"'](?:CATEGORY_HOME|ACTION_MAIN)[\"']|"
        r"\b(?:CATEGORY_HOME|ACTION_MAIN)\s*(?:,|\)|=))",
        re.I,
    ),
}

FUNCTION_RE = re.compile(
    r"^\s*(?:static\s+|inline\s+|__\w+\s+|const\s+|struct\s+\w+\s+)*"
    r"[A-Za-z_][\w\s\*]*?\s+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*(?:__\w+\s*)?\{"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_source_root(manifest_path: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return Path(data["source_root"])


def iter_sources(source_root: Path) -> Iterable[Path]:
    for scope in SCOPES:
        root = source_root / scope
        if not root.is_dir():
            continue
        for directory, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(
                name for name in dirnames if name not in SKIP_PARTS and not name.startswith(".")
            )
            for filename in sorted(filenames):
                path = Path(directory) / filename
                if path.suffix.lower() in SOURCE_EXTENSIONS and not path.is_symlink():
                    yield path


def nearest_kconfig(path: Path, source_root: Path) -> str:
    current = path.parent
    while current >= source_root:
        candidate = current / "Kconfig"
        if candidate.is_file():
            return candidate.relative_to(source_root).as_posix()
        if current == source_root:
            break
        current = current.parent
    return ""


def function_name(lines: list[str], index: int) -> str:
    for lookback in range(0, min(index + 1, 4)):
        candidate = lines[index - lookback].strip()
        match = FUNCTION_RE.match(candidate)
        if match:
            return match.group(1)
    return "<file-scope>"


def compact(text: str) -> str:
    return " ".join(text.strip().split())[:240]


def scan_file(path: Path, source_root: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"path": path, "error": str(exc), "markers": []}
    lines = text.splitlines()
    markers: list[dict] = []
    counts: Counter[str] = Counter()
    for number, line in enumerate(lines, start=1):
        for kind, pattern in MARKERS.items():
            if pattern.search(line):
                counts[kind] += 1
                markers.append(
                    {
                        "kind": kind,
                        "line": number,
                        "function": function_name(lines, number - 1),
                        "text": compact(line),
                    }
                )

    relative = path.relative_to(source_root).as_posix()
    direct_framework = bool(counts["framework_sink_literal"])
    direct_launcher = bool(counts["launcher_sink_literal"])
    registrations = counts["proc_sysfs_debugfs_registration"] + counts["device_registration"]
    user_copy = counts["user_copy"]
    ioctl = counts["ioctl_entry"]
    if direct_framework or direct_launcher:
        evidence_class = "direct-framework-or-launcher-literal"
        framework_sink = "direct-hit"
    elif ioctl or user_copy or registrations:
        evidence_class = "source-surface-only"
        framework_sink = "none-observed"
    else:
        evidence_class = "support-code-only"
        framework_sink = "none-observed"

    if counts["trusted_execution"]:
        channel = "trusted-execution-marker"
    elif counts["secure_world"]:
        channel = "secure-world-marker"
    elif counts["uevent_or_netlink"]:
        channel = "uevent-or-netlink-marker"
    elif ioctl or user_copy:
        channel = "ioctl-or-user-copy"
    elif registrations:
        channel = "proc-sysfs-device-registration"
    else:
        channel = "support-code"

    return {
        "path": path,
        "relative_path": relative,
        "sha256": sha256(path),
        "line_count": len(lines),
        "kconfig": nearest_kconfig(path, source_root),
        "framework_sink": framework_sink,
        "launcher_sink": "direct-hit" if direct_launcher else "none-observed",
        "channel": channel,
        "evidence_class": evidence_class,
        "runtime_reachability": "not-derived-from-source",
        "local_gate": "observed" if counts["local_gate"] else "not-observed",
        "marker_counts": dict(counts),
        "markers": markers,
    }


def write_outputs(records: list[dict], source_root: Path, manifest_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str | int]] = []
    marker_rows: list[dict[str, str | int]] = []
    total_markers: Counter[str] = Counter()
    for record in records:
        counts = record.get("marker_counts", {})
        total_markers.update(counts)
        scope_name = next(
            (scope for scope in SCOPES if record["relative_path"] == scope or record["relative_path"].startswith(scope + "/")),
            "unclassified",
        )
        rows.append(
            {
                "source_scope": scope_name,
                "source_path": record["relative_path"],
                "source_sha256": record["sha256"],
                "kconfig": record["kconfig"],
                "registration_or_fops": ",".join(
                    key for key in ("ioctl_entry", "proc_sysfs_debugfs_registration", "device_registration") if counts.get(key)
                ),
                "user_copy": counts.get("user_copy", 0),
                "local_gate": record["local_gate"],
                "control_channel": record["channel"],
                "secure_or_trusted_marker": "yes" if counts.get("secure_world", 0) or counts.get("trusted_execution", 0) else "no",
                "uevent_or_netlink_marker": "yes" if counts.get("uevent_or_netlink", 0) else "no",
                "framework_sink": record["framework_sink"],
                "launcher_sink": record["launcher_sink"],
                "runtime_reachability": record["runtime_reachability"],
                "evidence_class": record["evidence_class"],
                "representative_locations": "; ".join(
                    f"{item['kind']}:{item['line']}:{item['function']}" for item in record["markers"][:12]
                ),
            }
        )
        for item in record["markers"]:
            marker_rows.append(
                {
                    "source_path": record["relative_path"],
                    "source_sha256": record["sha256"],
                    "line": item["line"],
                    "function": item["function"],
                    "marker": item["kind"],
                    "text": item["text"],
                }
            )

    table_path = output_dir / "driver-control-closure.csv"
    with table_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()) if rows else ["source_path"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    marker_path = output_dir / "driver-control-markers.csv"
    with marker_path.open("w", encoding="utf-8", newline="") as handle:
        fields = ["source_path", "source_sha256", "line", "function", "marker", "text"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(marker_rows)

    manifest_copy = output_dir / "input-manifest.sha256"
    manifest_copy.write_text(f"{sha256(manifest_path)}  {manifest_path}\n", encoding="utf-8")
    with (output_dir / "source-hashes.tsv").open("w", encoding="utf-8") as handle:
        handle.write("source_path\tsha256\n")
        for record in records:
            handle.write(f"{record['relative_path']}\t{record['sha256']}\n")

    summary = {
        "schema": "phase6me-driver-control-closure-v1",
        "source_root": str(source_root),
        "manifest": str(manifest_path),
        "scope_roots": list(SCOPES),
        "file_count": len(records),
        "marker_count": sum(total_markers.values()),
        "marker_counts": dict(sorted(total_markers.items())),
        "direct_framework_or_launcher_files": sum(
            1 for record in records if record["framework_sink"] == "direct-hit" or record["launcher_sink"] == "direct-hit"
        ),
        "source_surface_files": sum(1 for record in records if record["evidence_class"] == "source-surface-only"),
        "runtime_reachability_policy": "not-derived-from-source; correlate only with separately hashed device evidence",
        "safety": {
            "adb": False,
            "device_node_open": False,
            "ioctl": False,
            "binary_execution": False,
            "mutation": False,
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    graph = [
        "flowchart LR",
        "  S[\"PS7331 selected source\"] --> R[\"driver registration / fops\"]",
        "  R --> U[\"user-copy / ioctl / proc / sysfs boundary\"]",
        "  U --> G[\"local gate markers\"]",
        "  U --> H[\"hardware / telemetry / DMA / secure-world candidates\"]",
        "  U -. no direct literal observed .-> F[\"AMS / ATMS / PMS / HOME\"]",
        "  F -.-> L[\"Fire Launcher\"]",
    ]
    (output_dir / "driver-control-closure.mmd").write_text("\n".join(graph) + "\n", encoding="utf-8")

    checks = []
    for path in sorted(output_dir.iterdir()):
        if path.name == "sha256sums.txt" or not path.is_file():
            continue
        checks.append(f"{sha256(path)}  {path.name}")
    (output_dir / "sha256sums.txt").write_text("\n".join(checks) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, help="canonical kernel source root")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true", help="print scope and counts without writing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = load_source_root(args.manifest, args.source_root)
    if not source_root.is_dir():
        raise SystemExit(f"source root does not exist: {source_root}")
    paths = list(iter_sources(source_root))
    if args.dry_run:
        print(f"source_root={source_root}")
        print(f"scope_count={len(SCOPES)}")
        print(f"source_file_count={len(paths)}")
        for scope in SCOPES:
            print(f"scope={scope} files={sum(1 for path in paths if str(path.relative_to(source_root)).startswith(scope + '/'))}")
        return 0
    records = [scan_file(path, source_root) for path in paths]
    write_outputs(records, source_root, args.manifest, args.output)
    print(json.dumps({"output": str(args.output), "file_count": len(records)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
