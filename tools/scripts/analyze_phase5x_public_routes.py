#!/usr/bin/env python3
"""Build a conservative public-route compatibility matrix from a read-only capture.

This is a host-only report generator. It never connects to ADB, executes a
device binary, opens a device node, or changes device state.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


def die(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    required = [
        "home.stdout.txt",
        "processes.stdout.txt",
        "packages.stdout.txt",
        "services.stdout.txt",
        "init_paths.stdout.txt",
        "node_metadata.stdout.txt",
        "aee_nodes.stdout.txt",
        "aee_access.stdout.txt",
        "apex_property.stdout.txt",
        "apex_paths.stdout.txt",
        "apex_help.stderr.txt",
    ]
    if args.dry_run:
        print("DRY-RUN: host-only analysis; no device command and no output write.")
        print(f"runtime_dir={args.runtime_dir}")
        print(f"output={args.output}")
        print("required_inputs=" + ",".join(required))
        return 0

    if not args.runtime_dir.is_dir():
        die(f"runtime directory does not exist: {args.runtime_dir}")
    if args.output.exists():
        die(f"output already exists: {args.output}")
    missing = [name for name in required if not (args.runtime_dir / name).is_file()]
    if missing:
        die("missing runtime inputs: " + ", ".join(missing))

    args.output.mkdir(parents=True)
    processes = read_text(args.runtime_dir / "processes.stdout.txt")
    packages = read_text(args.runtime_dir / "packages.stdout.txt")
    services = read_text(args.runtime_dir / "services.stdout.txt")
    init_paths = read_text(args.runtime_dir / "init_paths.stdout.txt")
    node_metadata = read_text(args.runtime_dir / "node_metadata.stdout.txt")
    aee_nodes = read_text(args.runtime_dir / "aee_nodes.stdout.txt")
    aee_access = read_text(args.runtime_dir / "aee_access.stdout.txt")
    apex_property = read_text(args.runtime_dir / "apex_property.stdout.txt").strip()
    apex_paths = read_text(args.runtime_dir / "apex_paths.stdout.txt")
    apex_help = read_text(args.runtime_dir / "apex_help.stderr.txt")
    home = read_text(args.runtime_dir / "home.stdout.txt").strip()

    kernel_aee_threads = sorted(
        line.strip()
        for line in processes.splitlines()
        if re.search(r"\[(?:gpu_aee_wq|mali_aeewp)\]", line, re.I)
    )
    userspace_aee = sorted(
        line.strip()
        for line in processes.splitlines()
        if re.search(r"\baee(?:[_-]|\s|$)", line, re.I)
        and "[gpu_aee_wq]" not in line
        and "[mali_aeewp]" not in line
    )
    apex_package_lines = sorted(
        line.strip() for line in packages.splitlines() if re.search(r"apex|vndk", line, re.I)
    )
    route_runtime = (
        f"HOME={home}; kernel_aee_threads={len(kernel_aee_threads)}; "
        f"userspace_aee_lines={len(userspace_aee)}; aee_node_lines={len(aee_nodes.splitlines())}; "
        f"aee_access={aee_access.strip() or 'EMPTY'}; apex_packages={len(apex_package_lines)}; "
        f"apex_property={apex_property or 'EMPTY'}"
    )

    rows = [
        [
            "CVE-2025-20765",
            "MediaTek AEE daemon double-free/race; Android/vendor crash-reporting layer",
            "Official MTK bulletin: MT8183; Android software version not listed",
            "SoC matches; exact Android/PS7330 daemon version unknown",
            "Unknown; daemon/service path, not shell UID",
            "Kernel AEE worker threads and root-only /dev/aed0,/dev/aed1 metadata observed; shell access check is read=0/write=0; no userspace AEE process, package, service, or init path observed",
            "Read-only process/package/service/init capture",
            "No shell-reachable AEE daemon observed; no trigger attempted",
            "Strong evidence, scope/runtime only",
            "P5X-WEB-001; P5X-DEVICE-002",
        ],
        [
            "CVE-2024-20021",
            "ATF SPM physical-memory remap boundary; secure/firmware interface",
            "Official MTK bulletin: MT8183; Android 12/13/14; requires System privilege",
            "Android 9/API 28 and shell UID 2000 do not match",
            "System privilege required; /dev/sspm is root:system and SELinux-labeled",
            "Only node metadata visible; node was not opened or read",
            "Read-only node metadata capture",
            "Version/privilege mismatch; no live access test",
            "Confirmed, applicability boundary",
            "P5X-WEB-002; P5X-DEVICE-004",
        ],
        [
            "CVE-2023-45779",
            "Android APEX package-manager/update path using test-signed APEX",
            "Public advisory demonstrates Android 13 Lenovo Tab M10 Plus path",
            "Android 9 device has no observed APEX runtime surface",
            "Would require APEX installation/update authority; not a normal shell route here",
            "ro.apex.updatable empty; APEX directories/packages absent; apexservice unavailable",
            "Read-only APEX property/path/service checks",
            "Feature/version mismatch; no APEX install or update attempted",
            "Confirmed, runtime-surface scope",
            "P5X-WEB-003; P5X-DEVICE-003",
        ],
        [
            "CVE-2026-43499 (GhostLock)",
            "Linux futex PI -> rtmutex kernel path reached by native syscall",
            "Public implementations are target-specific; Fire source/config overlap only",
            "Kernel family overlap; signed PS7330 backport/layout/reachability unknown",
            "No safe shell privilege or root primitive established",
            "Existing Phase 5U/5W source and runtime boundary; no new trigger",
            "Host/source review only",
            "No exact-device payload; live futex race rejected",
            "High-confidence source applicability; not exploitability",
            "P5X-WEB-004; P5X-HOST-001; P5U-GHOST-003",
        ],
        [
            "CVE-2026-43503",
            "Linux networking skb/shared-frag path; unrelated to GhostLock",
            "Existing Phase 5U review and exact defconfig gate",
            "No matching enabled path in captured MT8183 config",
            "Would require kernel trigger; not an Android app route",
            "Existing config review; no packet trigger",
            "Host/source review only",
            "Not a GhostLock route; no live trigger",
            "Confirmed, identity/config boundary",
            "P5X-HOST-002; P5U-MATRIX-001; P5U-FRAG-001",
        ],
        [
            "CVE-2026-3499",
            "Identifier supplied as a possible GhostLock label",
            "No verified GhostLock record in the recorded public-source review",
            "Cannot establish CVE-to-implementation mapping",
            "Unknown",
            "No device action justified by an unresolved identifier",
            "Host-only identifier review",
            "Rejected as an unverified alias; do not treat as GhostLock",
            "Hypothesis / unresolved identifier",
            "P5X-WEB-005; P5X-PUBLIC-004",
        ],
        [
            "KoCleo/mtk-easy-su",
            "Magisk/mtk-su bootless-root wrapper; legacy MTK userspace route",
            "Current public README warns post-March 2020 firmware may block it; no exact target entry",
            "No KFTRWI/trona/MT8183 tested profile; previous exact-device test failed",
            "Requires a kernel/firmware vulnerability and native payload behavior",
            "No new runtime route; previous failure already archived",
            "Public-source recheck only",
            "Do not repeat the same payload; no new evidence",
            "Confirmed, route already disproved on this build",
            "P5X-PUBLIC-001; P5R-MTKSU-001",
        ],
        [
            "LauncherHijack",
            "Accessibility foreground redirect; not PackageManager HOME replacement",
            "Current repository is deprecated and documents Amazon blocked-package behavior",
            "Historical helper; prior exact controlled run was 0/30 handoffs",
            "Requires explicit user Accessibility consent; no root",
            "Current capture shows no redirect Accessibility service enabled",
            "Read-only service-state observation",
            "Historical approximation only; no new test",
            "Confirmed, not a formal HOME replacement",
            "P5X-PUBLIC-002; prior Phase 4 evidence",
        ],
        [
            "Generic MTK BROM/DA/preloader tools",
            "Pre-Android boot-chain protocol, not Android userspace implementation",
            "Public tools are generic and include read/write or unlock capabilities",
            "Exact PS7330 loader/DA/auth/rollback set unavailable",
            "BROM/DA/boot-chain authority; destructive risk",
            "No bootloader path touched in this capture",
            "Host-only compatibility review",
            "Level 3 / risk-rejected; no handshake or write",
            "Confirmed, safety boundary",
            "P5X-PUBLIC-003; P5W-PL-001; P5R-LK-001; P5R-LK-002",
        ],
    ]

    fieldnames = [
        "candidate",
        "android_implementation",
        "public_scope",
        "exact_device_match",
        "required_privilege",
        "device_runtime_surface",
        "action",
        "result",
        "confidence",
        "evidence",
    ]
    matrix_path = args.output / "candidate-matrix.csv"
    with matrix_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(fieldnames)
        writer.writerows(rows)

    summary = args.output / "route-surface-summary.md"
    summary.write_text(
        "# Phase 5X route-surface summary\n\n"
        f"- HOME resolver raw result: `{home}`\n"
        f"- Runtime summary: `{route_runtime}`\n"
        f"- AEE kernel-thread observations: {len(kernel_aee_threads)}\n"
        f"- AEE userspace candidate lines: {len(userspace_aee)}\n"
        f"- AEE node metadata lines: {len(aee_nodes.splitlines())}\n"
        f"- APEX package lines: {len(apex_package_lines)}\n"
        f"- APEX property: `{apex_property or 'EMPTY'}`\n"
        f"- APEX path output: `{apex_paths.strip() or 'EMPTY'}`\n"
        f"- APEX service stderr: `{apex_help.strip() or 'EMPTY'}`\n\n"
        "This is a host-only, read-only derivation. It does not prove exploitability "
        "or patch status and does not open a device node or run a payload.\n",
        encoding="utf-8",
    )

    input_hashes = args.output / "input-sha256.tsv"
    with input_hashes.open("w", encoding="utf-8") as handle:
        for name in required:
            handle.write(f"{name}\t{sha256(args.runtime_dir / name)}\n")

    manifest = args.output / "sha256sums.txt"
    with manifest.open("w", encoding="utf-8") as handle:
        for path in sorted(args.output.iterdir()):
            if path.name == "sha256sums.txt" or not path.is_file():
                continue
            handle.write(f"{sha256(path)}  {path}\n")
    print(f"Wrote {matrix_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
