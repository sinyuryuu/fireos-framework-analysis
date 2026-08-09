#!/usr/bin/env python3
"""Host-only scan for Play Store package/component state writer call sites.

This script never connects to a device and never invokes an APK.  It scans a
JADX source tree and, optionally, the pulled base APK as opaque bytes.  The
output is a candidate index, not a proof that a call site is reachable from an
exported component.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


SETTER_RE = re.compile(
    r"\b(setApplicationEnabledSetting|setComponentEnabledSetting)\s*\("
)
HOME_RE = re.compile(
    r"(?:CATEGORY_HOME|ACTION_MAIN|startHomeActivity|startHomeOnAllDisplays|"
    r"setPreferredActivity|addPreferredActivity|replacePreferredActivity)",
    re.IGNORECASE,
)
CLASS_RE = re.compile(r"\b(?:class|interface|enum)\s+([A-Za-z0-9_$]+)")
METHOD_RE = re.compile(
    r"\b(?:public|private|protected|static|final|synchronized|native|abstract|\s)+"
    r"(?:[A-Za-z0-9_$<>\[\].?, ]+)\s+([A-Za-z0-9_$]+)\s*\([^;{}]*\)\s*(?:\{|throws)"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def nearest_name(lines: list[str], index: int) -> tuple[str, str]:
    class_name = ""
    method_name = ""
    for prior in range(index, max(-1, index - 120), -1):
        if not class_name:
            match = CLASS_RE.search(lines[prior])
            if match:
                class_name = match.group(1)
        if not method_name:
            match = METHOD_RE.search(lines[prior])
            if match:
                method_name = match.group(1)
        if class_name and method_name:
            break
    return class_name, method_name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--apk", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_dir = args.source_dir.resolve()
    rows: list[dict[str, str]] = []
    source_files = sorted(source_dir.rglob("*.java"))
    for source in source_files:
        try:
            text = source.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        file_has_fire = "com.amazon.firelauncher" in text
        file_has_home = bool(HOME_RE.search(text))
        file_hash = sha256(source)
        for index, line in enumerate(lines):
            match = SETTER_RE.search(line)
            if not match:
                continue
            class_name, method_name = nearest_name(lines, index)
            rows.append(
                {
                    "file": str(source.relative_to(source_dir)),
                    "line": str(index + 1),
                    "api": match.group(1),
                    "class_guess": class_name,
                    "method_guess": method_name,
                    "fire_literal_in_file": str(file_has_fire).lower(),
                    "home_token_in_file": str(file_has_home).lower(),
                    "source_sha256": file_hash,
                    "source_line": line.strip(),
                }
            )

    apk_fire_count = "UNKNOWN"
    apk_sha = ""
    if args.apk:
        apk_sha = sha256(args.apk)
        apk_fire_count = "0"
        with args.apk.open("rb") as handle:
            data = handle.read()
        apk_fire_count = str(data.count(b"com.amazon.firelauncher"))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "file",
                "line",
                "api",
                "class_guess",
                "method_guess",
                "fire_literal_in_file",
                "home_token_in_file",
                "source_sha256",
                "source_line",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"source_files={len(source_files)}")
    print(f"writer_sites={len(rows)}")
    print(f"apk_sha256={apk_sha}")
    print(f"apk_fire_literal_byte_count={apk_fire_count}")
    print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
