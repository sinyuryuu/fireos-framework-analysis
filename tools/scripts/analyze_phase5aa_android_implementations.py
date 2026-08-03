#!/usr/bin/env python3
"""Derive a host-only Android implementation compatibility matrix.

This analyzer reads already preserved reports and public-source metadata.  It
does not fetch a repository, invoke adb, execute an APK/native object, invoke a
device node, build an exploit, or write an image.  The output directory must
not exist so that prior evidence cannot be overwritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path


ROUTES = [
    {
        "route": "KoCleo/mtk-easy-su",
        "android_layer": "Kotlin Android wrapper + precompiled MTK native payload",
        "implementation_boundary": "ExploitHandler extracts LFS assets and invokes a bundled shell/Magisk path; payload source is not in the Android tree",
        "public_target": "legacy MediaTek devices; README warns about post-2020 firmware",
        "exact_device": "same mtk-su64 payload hash was already tested on KFTRWI/trona/PS7330; no exact target profile",
        "status": "DISPROVED for this pinned payload/build",
        "confidence": "Confirmed",
        "evidence": "P5AA-MTK-001; P5E-CMDQ-007; P5-WEB-007",
        "safe_next_step": "No repeat execution; only obtain exact signed vendor artifact for offline comparison",
    },
    {
        "route": "x-spy/CVE-2026-43499-popsicle",
        "android_layer": "Android arm64 native preload + kernel futex/rtmutex",
        "implementation_boundary": "Boot/XBL-derived target generation and device-specific native build",
        "public_target": "Xiaomi 17 family; Snapdragon; Android 16; kernel 6.12.23",
        "exact_device": "SoC, Android release, kernel generation, boot artifact and target profile differ",
        "status": "NOT TRANSFERABLE",
        "confidence": "Confirmed",
        "evidence": "P5AA-ANDROID-005",
        "safe_next_step": "Methodology reference only; do not copy constants or run the payload",
    },
    {
        "route": "Linuxoid-cn/CVE-2026-43499-Poc-Analysis",
        "android_layer": "Android arm64 profile/target generator",
        "implementation_boundary": "Generic target/profile framework requiring exact boot and profile inputs",
        "public_target": "Xiaomi-oriented generic Android framework",
        "exact_device": "No trona/MT8183/PS7330 profile or validated output",
        "status": "PORTING FRAMEWORK ONLY",
        "confidence": "Confirmed",
        "evidence": "P5AA-ANDROID-006",
        "safe_next_step": "Static methodology review only",
    },
    {
        "route": "BuSung-dev/Root-My-Galaxy",
        "android_layer": "Kotlin selector separated from model/kernel-specific payload feed",
        "implementation_boundary": "Selects a payload by supported model and kernel combination",
        "public_target": "Supported Samsung model and kernel combinations",
        "exact_device": "No Amazon KFTRWI/trona payload or kernel match",
        "status": "NOT TRANSFERABLE",
        "confidence": "Confirmed",
        "evidence": "P5AA-ANDROID-001",
        "safe_next_step": "No payload retrieval or installation",
    },
    {
        "route": "soralis0912/CVE-2026-43499-aristotle",
        "android_layer": "Android arm64 native preload + kernel futex/rtmutex",
        "implementation_boundary": "MediaTek port re-derives target layout, kernel anchors and runtime offsets for one device",
        "public_target": "au/KDDI Xiaomi XIG04; MediaTek; Android 12; kernel 5.10.136",
        "exact_device": "MT8183/Android 9/4.4.146+/PS7330 differs; upstream README says the port was not hardware validated",
        "status": "NOT TRANSFERABLE",
        "confidence": "Confirmed",
        "evidence": "P5AA-ANDROID-002",
        "safe_next_step": "Use only as a target-specific analysis pattern; no porting or trigger",
    },
    {
        "route": "CakesTwix/Android-CVE-2026-43499",
        "android_layer": "Kotlin detector app + ABI-specific native test library",
        "implementation_boundary": "Detector infers vulnerability from native process termination behavior; it is not a root implementation",
        "public_target": "Android 7+ ARM; generic detector",
        "exact_device": "No PS7330 validation; README warns the native test may crash/reboot a vulnerable device",
        "status": "DETECTOR ONLY / DO NOT RUN",
        "confidence": "Confirmed",
        "evidence": "P5AA-ANDROID-003",
        "safe_next_step": "Static review only; no APK install",
    },
    {
        "route": "NebuSec/CyberMeowfia",
        "android_layer": "Linux/native exploit research tree; Android target varies by port",
        "implementation_boundary": "Public source family with per-target Android adaptations",
        "public_target": "Multiple Linux/Android research targets; no exact trona profile",
        "exact_device": "No exact KFTRWI/MT8183/PS7330 Android target",
        "status": "REFERENCE ONLY",
        "confidence": "Strong evidence",
        "evidence": "P5AA-ANDROID-007",
        "safe_next_step": "Source attribution only",
    },
    {
        "route": "polygraphene/DirtyPipe-Android",
        "android_layer": "Android native root PoC -> Linux pipe/page-cache path",
        "implementation_boundary": "Device-specific Android runner and payload; not an Android framework feature",
        "public_target": "Pixel 6 security patches 2022-02-05 through 2022-04-05",
        "exact_device": "KFTRWI reports Linux 4.4.146+ and a 2024-02 patch; target/kernel family mismatch",
        "status": "VERSION MISMATCH",
        "confidence": "Confirmed",
        "evidence": "P5AA-ANDROID-004; P5AA-BASE-001",
        "safe_next_step": "No install or trigger",
    },
    {
        "route": "tiann/DirtyPipeRoot",
        "android_layer": "Android temporary-root wrapper",
        "implementation_boundary": "Device support varies by port; wrapper does not create target compatibility",
        "public_target": "Historical Android temporary-root project",
        "exact_device": "No exact KFTRWI/MT8183/PS7330 support",
        "status": "WARNING-ONLY REFERENCE",
        "confidence": "Confirmed",
        "evidence": "P5AA-ANDROID-008",
        "safe_next_step": "No install or trigger",
    },
    {
        "route": "R0rt1z2/fenrir",
        "android_layer": "MediaTek preloader/secure-boot-chain PoC",
        "implementation_boundary": "Runs before Android userspace and depends on a device-specific boot-chain profile",
        "public_target": "Supported MediaTek devices listed by the project; no trona/KFTRWI profile",
        "exact_device": "No exact PS7330 preloader, DA/auth state or recovery set",
        "status": "LEVEL-3 / REJECTED",
        "confidence": "Strong evidence",
        "evidence": "P5AA-BOOT-001; P5-WEB-004",
        "safe_next_step": "No BROM/DA handshake, unlock, image write or preloader action",
    },
    {
        "route": "Shocked-Cat/oppo-mtk-fastboot-unlock",
        "android_layer": "OPlus factory-preloader modification",
        "implementation_boundary": "Boot-chain modification and preloader write; not Android userspace",
        "public_target": "Oppo/Realme/OnePlus MTK devices",
        "exact_device": "Amazon trona is a different OEM boot chain; no exact image or rollback-safe recovery",
        "status": "LEVEL-3 / REJECTED",
        "confidence": "Strong evidence",
        "evidence": "P5AA-BOOT-001; P5-WEB-004",
        "safe_next_step": "Host-side source review only",
    },
    {
        "route": "HackMD Qualcomm/ABL/IMQSNative/Magica candidates",
        "android_layer": "Qualcomm bootloader or Xiaomi vendor-service chains",
        "implementation_boundary": "Requires Qualcomm ABL/GPU or Xiaomi-specific service/SELinux conditions",
        "public_target": "Qualcomm/Xiaomi devices described by the index",
        "exact_device": "MT8183 Amazon tablet; no Qualcomm ABL, Xiaomi MQSAS service or matching target evidence",
        "status": "INAPPLICABLE",
        "confidence": "Confirmed, scope-scoped",
        "evidence": "P5AA-HACKMD-001; P5AA-BASE-001",
        "safe_next_step": "Do not adapt commands or services",
    },
    {
        "route": "CVE-2026-43503",
        "android_layer": "Linux networking skb/shared-fragment path",
        "implementation_boundary": "Kernel networking issue, not an Android APK or framework HOME/root implementation",
        "public_target": "Separate CVE from GhostLock",
        "exact_device": "No evidence connecting it to the observed Android 9 MT8183 path",
        "status": "UNRELATED TO GHOSTLOCK",
        "confidence": "Confirmed",
        "evidence": "P5AA-CVE-001",
        "safe_next_step": "Do not combine with the GhostLock route",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_file(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"missing input: {path}")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-report", type=Path, required=True)
    parser.add_argument("--existing-review", type=Path, required=True)
    parser.add_argument("--source-metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for path in (args.device_report, args.existing_review, args.source_metadata):
        require_file(path)
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    planned = [
        args.output / "commands.txt",
        args.output / "input-hashes.tsv",
        args.output / "metadata.tsv",
        args.output / "android-implementation-matrix.csv",
        args.output / "result.md",
        args.output / "sha256sums.txt",
    ]
    print("mode=" + ("dry-run" if args.dry_run else "write-derived-output"))
    print("device_mutation=none")
    print("network_fetch=none")
    for path in planned:
        print(f"planned={path}")
    if args.dry_run:
        return 0

    args.output.mkdir(parents=False, exist_ok=False)
    inputs = [args.device_report, args.existing_review, args.source_metadata]
    commands = (
        "# Host-only; no network/device/exploit operation\n"
        "python3 tools/scripts/analyze_phase5aa_android_implementations.py \\\n"
        f"  --device-report {args.device_report} \\\n"
        f"  --existing-review {args.existing_review} \\\n"
        f"  --source-metadata {args.source_metadata} \\\n"
        f"  --output {args.output}\n"
    )
    write_text(args.output / "commands.txt", commands)
    write_text(
        args.output / "input-hashes.tsv",
        "sha256\tpath\n"
        + "\n".join(f"{sha256(path)}\t{path}" for path in inputs)
        + "\n",
    )
    write_text(
        args.output / "metadata.tsv",
        "field\tvalue\n"
        "mode\thost-only\n"
        "device_mutation\tnone\n"
        "network_fetch\tnone\n"
        f"route_count\t{len(ROUTES)}\n",
    )
    with (args.output / "android-implementation-matrix.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=list(ROUTES[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(ROUTES)
    write_text(
        args.output / "result.md",
        "# Phase 5AA derived Android implementation matrix\n\n"
        "This output is host-only. It maps public Android/MTK implementation "
        "boundaries to the preserved KFTRWI/trona/MT8183/PS7330 evidence. No "
        "APK, native payload, exploit, device node, boot-chain interface or "
        "partition was accessed.\n",
    )
    manifest = []
    for path in sorted(args.output.iterdir()):
        if path.name != "sha256sums.txt":
            manifest.append(f"{sha256(path)}  {path.name}")
    write_text(args.output / "sha256sums.txt", "\n".join(manifest) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
