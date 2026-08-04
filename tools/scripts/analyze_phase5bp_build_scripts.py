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
    "TOOLCHAIN_NAME",
    "TOOLCHAIN_PREFIX",
    "KERNEL_IMAGES",
    "CLANG_COMPILER_PATH",
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

    for name in ASSIGNMENTS:
        line, value = line_for_assignment(config_lines, name)
        rows.append(
            {
                "control": name.lower(),
                "file": config.name,
                "line": str(line),
                "value": value,
                "interpretation": "captured assignment",
                "confidence": "Confirmed",
            }
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

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["control", "file", "line", "value", "interpretation", "confidence"],
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
