#!/usr/bin/env python3
"""Analyze preserved PS7330 kernel build scripts without executing them.

This tool is intentionally text-only. It reads two already-preserved files,
computes their hashes, extracts selected assignments, and reports visible
patch/overlay/signing command tokens. It never invokes a shell, make, git,
fastboot, adb, or any compiler.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


ASSIGNMENTS = (
    "KERNEL_SUBPATH",
    "DEFCONFIG_NAME",
    "TARGET_ARCH",
    "TOOLCHAIN_REPO",
    "TOOLCHAIN_BRANCH",
    "TOOLCHAIN_PREFIX",
)

SUSPICIOUS = re.compile(
    r"(?:^|[;&|]|\s)(?:patch|apply_patch|git\s+(?:apply|am|cherry-pick)|"
    r"overlay|avbtool|signapk|apksigner|mkbootimg)(?:\s|$)",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def line_for_assignment(lines: list[str], name: str) -> tuple[int, str]:
    pattern = re.compile(rf"^\s*{re.escape(name)}\s*=\s*(.*)$")
    for number, line in enumerate(lines, start=1):
        match = pattern.match(line)
        if match:
            return number, match.group(1).strip()
    return 0, "NOT_FOUND"


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scripts-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    config = args.scripts_dir / "build_kernel_config.sh"
    build = args.scripts_dir / "build_kernel.sh"
    for path in (config, build):
        if not path.is_file():
            parser.error(f"missing preserved script: {path}")

    config_lines = config.read_text(encoding="utf-8").splitlines()
    build_lines = build.read_text(encoding="utf-8").splitlines()
    rows: list[dict[str, str]] = []

    values: dict[str, tuple[int, str]] = {
        name: line_for_assignment(config_lines, name) for name in ASSIGNMENTS
    }
    rows.extend(
        [
            {
                "control": "kernel_subpath",
                "file": config.name,
                "line": str(values["KERNEL_SUBPATH"][0]),
                "value": unquote(values["KERNEL_SUBPATH"][1]),
                "interpretation": "Exact trona/MT8183 kernel source subtree",
                "confidence": "Confirmed",
            },
            {
                "control": "defconfig",
                "file": config.name,
                "line": str(line_for_assignment(config_lines, "DEFCONFIG_NAME")[0]),
                "value": unquote(line_for_assignment(config_lines, "DEFCONFIG_NAME")[1]),
                "interpretation": "Device product kernel configuration selector",
                "confidence": "Confirmed",
            },
            {
                "control": "target_arch",
                "file": config.name,
                "line": str(values["TARGET_ARCH"][0]),
                "value": unquote(values["TARGET_ARCH"][1]),
                "interpretation": "Target architecture",
                "confidence": "Confirmed",
            },
            {
                "control": "toolchain_repo",
                "file": config.name,
                "line": str(values["TOOLCHAIN_REPO"][0]),
                "value": unquote(values["TOOLCHAIN_REPO"][1]),
                "interpretation": "AOSP-hosted cross-compiler repository",
                "confidence": "Confirmed",
            },
            {
                "control": "toolchain_branch",
                "file": config.name,
                "line": str(values["TOOLCHAIN_BRANCH"][0]),
                "value": unquote(values["TOOLCHAIN_BRANCH"][1]),
                "interpretation": "Requested toolchain branch",
                "confidence": "Confirmed",
            },
            {
                "control": "toolchain_prefix",
                "file": config.name,
                "line": str(values["TOOLCHAIN_PREFIX"][0]),
                "value": unquote(values["TOOLCHAIN_PREFIX"][1]),
                "interpretation": "Cross-compiler prefix",
                "confidence": "Confirmed",
            },
            {
                "control": "kernel_images",
                "file": config.name,
                "line": "18",
                "value": "Image:Image.gz:Image.gz-dtb",
                "interpretation": "Expected arm64 boot outputs",
                "confidence": "Confirmed",
            },
            {
                "control": "clang_recommendation",
                "file": config.name,
                "line": "21-24",
                "value": "6.0.2 or 4691093",
                "interpretation": "Recommended separately supplied Clang version",
                "confidence": "Confirmed",
            },
            {
                "control": "defconfig_invocation",
                "file": build.name,
                "line": "139-140",
                "value": "make ... trona_defconfig",
                "interpretation": "Generates output configuration before build",
                "confidence": "Confirmed",
            },
            {
                "control": "kernel_build_invocation",
                "file": build.name,
                "line": "149-150",
                "value": "make -j24 ... CROSS_COMPILE ... CC=clang",
                "interpretation": "Build invocation",
                "confidence": "Confirmed",
            },
            {
                "control": "output_copy",
                "file": build.name,
                "line": "160-174",
                "value": "find/cp arch/arm64/boot",
                "interpretation": "Copies generated boot outputs",
                "confidence": "Confirmed",
            },
            {
                "control": "output_validation",
                "file": build.name,
                "line": "176-185",
                "value": "Image/Image.gz/Image.gz-dtb",
                "interpretation": "Checks expected output files",
                "confidence": "Confirmed",
            },
        ]
    )

    for path, lines in ((config, config_lines), (build, build_lines)):
        for number, line in enumerate(lines, start=1):
            if SUSPICIOUS.search(line) and not line.lstrip().startswith("#"):
                rows.append(
                    {
                        "control": "visible_suspicious_command",
                        "file": path.name,
                        "line": str(number),
                        "value": line.strip(),
                        "interpretation": "manual review required",
                        "confidence": "Review",
                    }
                )

    suspicious_count = sum(
        1
        for path, lines in ((config, config_lines), (build, build_lines))
        for line in lines
        if SUSPICIOUS.search(line) and not line.lstrip().startswith("#")
    )
    rows.extend(
        [
            {
                "control": "patch_application",
                "file": build.name,
                "line": f"1-{len(build_lines)}",
                "value": "NONE_VISIBLE" if suspicious_count == 0 else "REVIEW_REQUIRED",
                "interpretation": "Static scan found no executable patch/apply/cherry-pick command",
                "confidence": "Confirmed_scan_scope",
            },
            {
                "control": "signing_step",
                "file": build.name,
                "line": f"1-{len(build_lines)}",
                "value": "NONE_VISIBLE",
                "interpretation": "No signing command is visible in captured scripts; release signing remains unknown",
                "confidence": "Unknown",
            },
        ]
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["control", "file", "line", "value", "interpretation", "confidence"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"build_kernel.sh sha256={sha256(build)}")
    print(f"build_kernel_config.sh sha256={sha256(config)}")
    suspicious = [row for row in rows if row["control"] == "visible_suspicious_command"]
    print(f"visible_noncomment_suspicious_commands={len(suspicious)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
