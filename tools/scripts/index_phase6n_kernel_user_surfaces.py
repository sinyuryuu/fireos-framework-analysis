#!/usr/bin/env python3
"""Build a host-only index of selected PS7331 kernel user-facing surfaces.

This tool reads source text only.  It does not invoke adb, compile a kernel,
open a device node, or send an ioctl.  A match is a source-review lead, not a
vulnerability or exploit finding.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


TEXT_SUFFIXES = {
    ".c",
    ".h",
    ".cc",
    ".cpp",
    ".dts",
    ".dtsi",
    ".S",
    ".s",
    ".te",
    ".cil",
    ".mk",
    ".bp",
}

INTERESTING_PATH = re.compile(
    r"(?:cmdq|ion|ged|m4u|amzn|amazon|idme|sign_of_life|logger|"
    r"wlan|bluetooth|btmtk|fmradio|fm_module|drivers/(?:misc|soc|input|power|usb|char|staging))",
    re.IGNORECASE,
)

PATTERNS = (
    ("ioctl_entry", re.compile(r"\.(?:unlocked_ioctl|compat_ioctl)\s*=|\b(?:unlocked_ioctl|compat_ioctl)\s*=", re.I)),
    ("procfs", re.compile(r"\bproc_create(?:_data)?\s*\(", re.I)),
    ("debugfs", re.compile(r"\bdebugfs_create_[A-Za-z0-9_]+\s*\(", re.I)),
    ("device_create", re.compile(r"\bdevice_create\s*\(", re.I)),
    ("misc_register", re.compile(r"\bmisc_register\s*\(", re.I)),
    ("usercopy", re.compile(r"\b(?:copy_(?:from|to)_user|get_user|put_user|copy_struct_from_user)\s*\(", re.I)),
    ("capability_check", re.compile(r"\b(?:capable|ns_capable|security_capable)\s*\(", re.I)),
    ("uid_check", re.compile(r"\b(?:current_(?:uid|euid|fsuid)|from_kuid|uid_eq|in_egroup_p)\b", re.I)),
    ("sysfs_or_store", re.compile(r"\b(?:DEVICE_ATTR(?:_RW|_RO|_WO)?|sysfs_create|kstrto(?:int|uint|long|ulong))\b", re.I)),
    ("module_param", re.compile(r"\bmodule_param(?:_named)?\s*\(", re.I)),
    ("write_handler", re.compile(r"\.(?:write|unlocked_ioctl|compat_ioctl)\s*=|\b(?:write|store)\s*\(", re.I)),
)

FUNCTION_RE = re.compile(
    r"^\s*(?:(?:static|inline|extern|__maybe_unused|__init|__exit|void|int|long|"
    r"ssize_t|size_t|struct\s+\w+\s*\*?|unsigned\s+\w+|bool|char\s*\*?)\s+)+"
    r"(?P<name>[A-Za-z_]\w*)\s*\([^;{}]*\)\s*(?:\{|$)"
)

SKIP_NAMES = {"if", "for", "while", "switch", "return", "sizeof"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        default="firmware/extracted/PS7331-SOURCE-20250617",
        help="extracted GPL source root",
    )
    parser.add_argument(
        "--output",
        default="output/tables/phase6n-kernel-user-surfaces.csv",
        help="CSV output path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="enumerate matching source files without writing output",
    )
    return parser.parse_args()


def scope_for(path: Path) -> str:
    path_text = path.as_posix()
    if "/platform/device/amazon/" in path_text:
        return "amazon-device"
    if "/platform/vendor/mediatek/" in path_text:
        return "mediatek-vendor"
    return "mt8183-kernel"


def function_guess(lines: list[str], index: int) -> str:
    # Keep this deliberately conservative.  A blank result is better than a
    # misleading decompiler-like method name.
    for previous in range(index, max(-1, index - 45), -1):
        candidate = lines[previous].strip()
        match = FUNCTION_RE.match(candidate)
        if match and match.group("name") not in SKIP_NAMES:
            return match.group("name")
    return ""


def file_flags(text: str) -> tuple[str, str, str]:
    has_usercopy = "yes" if re.search(r"\b(?:copy_(?:from|to)_user|get_user|put_user)\s*\(", text) else "no"
    has_caller_gate = "yes" if re.search(
        r"\b(?:capable|ns_capable|security_capable|current_(?:uid|euid|fsuid)|uid_eq|from_kuid)\b",
        text,
        re.I,
    ) else "no"
    has_write_path = "yes" if re.search(
        r"\.(?:write|unlocked_ioctl|compat_ioctl)\s*=|\b(?:write|store|ioctl)\s*\(",
        text,
        re.I,
    ) else "no"
    return has_usercopy, has_caller_gate, has_write_path


def collect(root: Path) -> list[dict[str, str]]:
    if not root.is_dir():
        raise FileNotFoundError(f"source root does not exist: {root}")

    records: list[dict[str, str]] = []
    # The archive contains generic, emulator, and multiple BSP copies.  The
    # build-selected MT8183 tree is the only kernel tree included here; this
    # avoids counting the same source from generic/4.4 and 4.4_emc copies.
    scan_roots = [
        root / "platform/kernel/mediatek/mt8183/4.4",
        root / "platform/vendor/mediatek",
        root / "platform/device/amazon",
    ]
    for scan_root in scan_roots:
        if not scan_root.is_dir():
            continue
        for path in sorted(scan_root.rglob("*")):
            if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
                continue
            relative = path.relative_to(root)
            if not INTERESTING_PATH.search(relative.as_posix()):
                continue
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if b"\x00" in data or len(data) > 4 * 1024 * 1024:
                continue
            text = data.decode("utf-8", errors="replace")
            lines = text.splitlines()
            has_usercopy, has_caller_gate, has_write_path = file_flags(text)
            for line_number, line in enumerate(lines, start=1):
                matches = [name for name, pattern in PATTERNS if pattern.search(line)]
                if not matches:
                    continue
                records.append(
                    {
                        "source_scope": scope_for(path),
                        "relative_path": relative.as_posix(),
                        "line": str(line_number),
                        "surface_markers": ";".join(matches),
                        "function_guess": function_guess(lines, line_number - 1),
                        "has_usercopy_in_file": has_usercopy,
                        "has_caller_gate_in_file": has_caller_gate,
                        "has_write_path_in_file": has_write_path,
                        "runtime_status": "SOURCE_ONLY",
                        "snippet": " ".join(line.strip().split())[:240],
                    }
                )
    return records


def main() -> int:
    args = parse_args()
    root = Path(args.source_root).resolve()
    records = collect(root)
    fieldnames = [
        "source_scope",
        "relative_path",
        "line",
        "surface_markers",
        "function_guess",
        "has_usercopy_in_file",
        "has_caller_gate_in_file",
        "has_write_path_in_file",
        "runtime_status",
        "snippet",
    ]
    if args.dry_run:
        print(f"source_root={root}")
        print(f"records={len(records)}")
        print("output=not_written")
        return 0

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    print(f"source_root={root}")
    print(f"records={len(records)}")
    print(f"output={output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
