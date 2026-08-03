#!/usr/bin/env python3
"""Build a host-only Android implementation and boot-chain applicability map.

The script reads preserved reports and a version-mismatched PS7331 image only
for printable-string inspection.  It never calls adb, opens a device node,
starts a vendor service, executes an input binary, or writes a device/image.
``--dry-run`` validates all inputs and reports the files that would be derived.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path


ANDROID_IMPLEMENTATIONS = [
    {
        "candidate": "CVE-2026-43499",
        "layer": "Linux kernel / Android native syscall boundary",
        "android_entry": "Bionic/native app -> futex PI syscall -> kernel futex/rtmutex",
        "public_reference": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/patch/?id=3bfdc63936dd4773109b7b8c280c0f3b5ae7d349",
        "exact_device_evidence": "Fire 4.4 source/config has futex and rtmutex family; signed binary/layout unknown",
        "status": "source overlap only; no live trigger",
        "confidence": "Strong evidence",
    },
    {
        "candidate": "CVE-2022-20053",
        "layer": "Android telephony IMS framework + MediaTek vendor IMS",
        "android_entry": "ImsResolver -> bound ImsService -> vendor IMS implementation",
        "public_reference": "https://android.googlesource.com/platform/frameworks/base/+/android-vts-9.0_r17/telephony/java/android/telephony/ims/ImsService.java",
        "exact_device_evidence": "No active ims/IMS package or service in preserved normal-runtime snapshot",
        "status": "not reachable through observed normal shell runtime",
        "confidence": "Confirmed, snapshot-scoped",
    },
    {
        "candidate": "CVE-2022-20054",
        "layer": "MediaTek vendor IMS/ATCI, reached from Android service boundary",
        "android_entry": "vendor IMS service -> ATCI HIDL/init service -> modem command path",
        "public_reference": "https://corp.mediatek.com/product-security-bulletin/March-2022",
        "exact_device_evidence": "atcid-daemon-u is disabled/oneshot; no active atcid service/process; vendor binary unreadable to shell",
        "status": "exact binary patch state unknown; no property/service/socket/AT test",
        "confidence": "Unknown, route rejected",
    },
    {
        "candidate": "CVE-2022-20055 / CVE-2022-20056",
        "layer": "MediaTek preloader USB, before Android userspace",
        "android_entry": "physical USB boot/download path -> preloader parser/authentication",
        "public_reference": "https://nvd.nist.gov/vuln/detail/CVE-2022-20056",
        "exact_device_evidence": "Only PS7331 adjacent preloader/LK images are locally available; current device is PS7330",
        "status": "Android 9 target mismatch in published MediaTek software scope; no preloader trigger",
        "confidence": "Version mismatch / risk-rejected",
    },
    {
        "candidate": "CVE-2020-0069",
        "layer": "Android CTS native test -> MediaTek CMDQ driver",
        "android_entry": "native test -> /dev/mtk_cmdq ioctl ABI",
        "public_reference": "https://android.googlesource.com/platform/cts/+/41603998db75f63a00581e359eca408ff30a3da1/",
        "exact_device_evidence": "Fire MT8183 source selects CMDQ v3; archived request #7 returned -ENOTTY",
        "status": "previous v2 route disproved; no additional ioctl",
        "confidence": "Disproved for tested route",
    },
    {
        "candidate": "CVE-2023-20616",
        "layer": "Android ION userspace ABI -> MediaTek ION driver",
        "android_entry": "ION_IOC_CUSTOM -> vendor ION command dispatch",
        "public_reference": "https://corp.mediatek.com/product-security-bulletin/February-2023",
        "exact_device_evidence": "MTK ION source/config and library ABI are preserved; exact Android 9 bulletin scope is not matched",
        "status": "host-only ABI review; no /dev/ion ioctl",
        "confidence": "Version mismatch / untested",
    },
]


STRING_PATTERNS = {
    "preloader": re.compile(
        r"(?i)(anti.?rollback|DA validation|DA authenticated|authentication|"
        r"MTK_BLOADER|preloader|USB|usbdl|MT8183|trona|secure|auth)"
    ),
    "lk": re.compile(
        r"(?i)(amzn_.*unlock|temp_unlock|authentication|production|"
        r"MT8183|fastboot|unlock status|secure|bootloader|device is)"
    ),
}


def sha256(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_file(file_path: Path) -> None:
    if not file_path.is_file():
        raise SystemExit(f"missing input file: {file_path}")


def printable_strings(file_path: Path, minimum: int = 6):
    data = file_path.read_bytes()
    pattern = re.compile(rb"[ -~]{%d,}" % minimum)
    for match in pattern.finditer(data):
        yield match.start(), match.group().decode("ascii", errors="replace")


def selected_strings(file_path: Path, kind: str):
    pattern = STRING_PATTERNS[kind]
    count = 0
    for offset, value in printable_strings(file_path):
        if pattern.search(value):
            # Preserve content while removing padding-only spaces that make a
            # text evidence file fail repository whitespace checks.
            yield offset, value.rstrip()
            count += 1
            if count >= 240:
                break


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-report", type=Path, required=True)
    parser.add_argument("--ims-report", type=Path, required=True)
    parser.add_argument("--preloader-report", type=Path, required=True)
    parser.add_argument("--preloader", type=Path, required=True)
    parser.add_argument("--lk", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for file_path in (
        args.device_report,
        args.ims_report,
        args.preloader_report,
        args.preloader,
        args.lk,
    ):
        require_file(file_path)

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    planned = [
        args.output / "commands.txt",
        args.output / "metadata.tsv",
        args.output / "source-hashes.tsv",
        args.output / "android-implementation-map.csv",
        args.output / "preloader-selected-strings.tsv",
        args.output / "lk-selected-strings.tsv",
        args.output / "result.md",
        args.output / "sha256sums.txt",
    ]
    print("mode=" + ("dry-run" if args.dry_run else "write-derived-output"))
    print("device_mutation=none")
    for path in planned:
        print(f"planned={path}")
    print(f"preloader_sha256={sha256(args.preloader)}")
    print(f"lk_sha256={sha256(args.lk)}")

    if args.dry_run:
        return 0

    args.output.mkdir(parents=False, exist_ok=False)
    inputs = [
        args.device_report,
        args.ims_report,
        args.preloader_report,
        args.preloader,
        args.lk,
    ]
    write_text(
        args.output / "commands.txt",
        "# Host-only reproduction command; no adb/device operation\n"
        "python3 tools/scripts/analyze_phase5w_android_implementations.py \\\n+  --device-report " + str(args.device_report) + " \\\n+  --ims-report " + str(args.ims_report) + " \\\n+  --preloader-report " + str(args.preloader_report) + " \\\n+  --preloader " + str(args.preloader) + " \\\n+  --lk " + str(args.lk) + " \\\n+  --output " + str(args.output) + "\n"
        "\nThis command reads preserved reports and local adjacent-version images only.\n",
    )
    write_text(
        args.output / "metadata.tsv",
        "field\tvalue\n"
        "mode\thost-only\n"
        "device_mutation\tnone\n"
        f"input_count\t{len(inputs)}\n"
        f"preloader_sha256\t{sha256(args.preloader)}\n"
        f"lk_sha256\t{sha256(args.lk)}\n",
    )
    write_text(
        args.output / "source-hashes.tsv",
        "sha256\tpath\n"
        + "\n".join(f"{sha256(path)}\t{path}" for path in inputs)
        + "\n",
    )

    with (args.output / "android-implementation-map.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(
            stream, fieldnames=list(ANDROID_IMPLEMENTATIONS[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(ANDROID_IMPLEMENTATIONS)

    for kind, input_path, output_name in (
        ("preloader", args.preloader, "preloader-selected-strings.tsv"),
        ("lk", args.lk, "lk-selected-strings.tsv"),
    ):
        lines = ["offset_hex\tstring\n"]
        lines.extend(
            f"0x{offset:x}\t{value}\n" for offset, value in selected_strings(input_path, kind)
        )
        write_text(args.output / output_name, "".join(lines))

    write_text(
        args.output / "result.md",
        "# Phase 5W derived Android implementation map\n\n"
        "This directory is derived host-side evidence. It maps public Android "
        "framework/CTS/kernel references to the exact-device reports and records "
        "selected printable strings from adjacent PS7331 images. The images are "
        "not the installed PS7330 boot chain.\n\n"
        "No adb command, device-node open, vendor service start, AT/HCI input, "
        "preloader handshake, exploit, reboot, or write operation is performed.\n",
    )
    manifest = []
    for path in sorted(args.output.iterdir()):
        if path.name == "sha256sums.txt":
            continue
        manifest.append(f"{sha256(path)}  {path.name}")
    write_text(args.output / "sha256sums.txt", "\n".join(manifest) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
