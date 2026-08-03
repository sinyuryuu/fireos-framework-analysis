#!/usr/bin/env python3
"""Extract a small, traceable view from the exact Bluetooth VDEX disassembly.

This is a host-only analysis helper.  It never connects to a device and never
executes an APK, ODEX, VDEX, shared object, or kernel module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


CLASS_RE = re.compile(r"^  class #(\d+): (.+?) \('([^']+)'\)")
METHOD_RE = re.compile(r"^\s+(direct|virtual)_method #(\d+): (.+)$")
FOCUS_RE = re.compile(
    r"AmazonBtPolicyManagerAdapter|FosGattService|"
    r"AdapterService|GattService|IAmazonBluetooth|AmazonBluetoothGatt"
)
PERMISSION_RE = re.compile(
    r"enforce(?:CallingOrSelf)?Permission|check(?:Calling|CallingOrSelf)?Permission|"
    r"android\.permission\.[A-Z0-9_]+|Need BLUETOOTH permission"
)
AMAZON_API_RE = re.compile(
    r"Amazon|amazon/|amazon\.|FosGatt|BTPM|setAmazonBluetoothGattCallback|"
    r"btpm[A-Z]|IAmazonBluetooth"
)


def die(message: str) -> "NoReturn":
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(descriptor: str) -> str:
    name = descriptor.strip("L;").replace("/", "_").replace("$", "__")
    return re.sub(r"[^A-Za-z0-9_.-]", "_", name) + ".txt"


def class_sections(lines: list[str]) -> list[tuple[int, int, re.Match[str]]]:
    starts: list[tuple[int, re.Match[str]]] = []
    for number, line in enumerate(lines, 1):
        match = CLASS_RE.match(line)
        if match:
            starts.append((number, match))
    sections: list[tuple[int, int, re.Match[str]]] = []
    for index, (start, match) in enumerate(starts):
        end = starts[index + 1][0] - 1 if index + 1 < len(starts) else len(lines)
        sections.append((start, end, match))
    return sections


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.log.is_file():
        die(f"disassembly log not found: {args.log}")
    if args.output.exists():
        die(f"refusing to overwrite existing output: {args.output}")
    if args.output in {Path("/"), Path("."), Path(".."), Path("/tmp"), Path("/var/tmp")}:
        die(f"unsafe output directory: {args.output}")

    if args.dry_run:
        print(f"DRY-RUN: parse {args.log} and write focused class/method slices to {args.output}")
        print("DRY-RUN: host-only; no ADB, APK, ODEX, VDEX, ELF, or kernel-module execution")
        return 0

    lines = args.log.read_text(encoding="utf-8", errors="replace").splitlines()
    sections = class_sections(lines)
    args.output.mkdir(parents=True)

    class_rows: list[str] = ["class_number\tclass_name\tdescriptor\tstart_line\tend_line\tdirect_methods\tvirtual_methods"]
    focus_sections: list[tuple[int, int, re.Match[str]]] = []
    for start, end, match in sections:
        direct = 0
        virtual = 0
        for line in lines[start - 1 : end]:
            method = METHOD_RE.match(line)
            if method:
                if method.group(1) == "direct":
                    direct += 1
                else:
                    virtual += 1
        class_rows.append(
            "\t".join(
                [
                    match.group(1),
                    match.group(2),
                    match.group(3),
                    str(start),
                    str(end),
                    str(direct),
                    str(virtual),
                ]
            )
        )
        if FOCUS_RE.search(match.group(2)) or FOCUS_RE.search(match.group(3)):
            focus_sections.append((start, end, match))

    (args.output / "class-index.tsv").write_text("\n".join(class_rows) + "\n", encoding="utf-8")
    focus_dir = args.output / "focus-classes"
    focus_dir.mkdir()
    focus_rows = ["class_number\tclass_name\tdescriptor\tfile\tstart_line\tend_line"]
    for start, end, match in focus_sections:
        filename = safe_name(match.group(3))
        target = focus_dir / filename
        target.write_text(
            "".join(f"{number:>8}: {lines[number - 1]}\n" for number in range(start, end + 1)),
            encoding="utf-8",
        )
        focus_rows.append(
            "\t".join([match.group(1), match.group(2), match.group(3), str(Path("focus-classes") / filename), str(start), str(end)])
        )
    (args.output / "focus-class-index.tsv").write_text("\n".join(focus_rows) + "\n", encoding="utf-8")

    permission_lines: list[str] = []
    amazon_lines: list[str] = []
    for number, line in enumerate(lines, 1):
        if PERMISSION_RE.search(line):
            permission_lines.append(f"{number}: {line}")
        if AMAZON_API_RE.search(line):
            amazon_lines.append(f"{number}: {line}")
    (args.output / "permission-call-sites.txt").write_text("\n".join(permission_lines) + "\n", encoding="utf-8")
    (args.output / "amazon-api-call-sites.txt").write_text("\n".join(amazon_lines) + "\n", encoding="utf-8")

    metadata = {
        "source_log": str(args.log),
        "source_sha256": sha256(args.log),
        "source_line_count": len(lines),
        "class_count": len(sections),
        "focus_class_count": len(focus_sections),
        "permission_line_count": len(permission_lines),
        "amazon_api_line_count": len(amazon_lines),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "execution": "host-only text parsing; no device or binary execution",
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    output_files = sorted(path for path in args.output.rglob("*") if path.is_file())
    manifest_lines = []
    for path in output_files:
        manifest_lines.append(f"{sha256(path)}  {path.relative_to(args.output)}")
    (args.output / "sha256sums.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(f"classes={len(sections)} focus_classes={len(focus_sections)}")
    print(f"permission_lines={len(permission_lines)} amazon_api_lines={len(amazon_lines)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
