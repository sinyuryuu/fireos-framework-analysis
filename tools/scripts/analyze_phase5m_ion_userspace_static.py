#!/usr/bin/env python3
"""Host-only static inventory of MTK ION userspace wrappers.

This script invokes host inspection tools (file, nm, objdump, strings) on
already-pulled ELF files. It never loads or executes an ELF, opens an Android
device node, sends an ioctl, pushes a file, or contacts a device.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def die(message: str) -> "NoReturn":
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_capture(command: list[str], output: Path) -> int:
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, check=False)
    output.write_text(completed.stdout, encoding="utf-8")
    return completed.returncode


def parse_ioctl_calls(disassembly: str) -> list[tuple[str, str, str, str]]:
    current = "<unknown>"
    prior: list[str] = []
    rows: list[tuple[str, str, str, str]] = []
    function_re = re.compile(r"^0*[0-9a-f]+ <([^>]+)>:")
    call_re = re.compile(r"^\s*([0-9a-f]+):.*<ioctl@plt>")
    direct_constant_re = re.compile(r"mov\s+w1, #0x([0-9a-f]+)")
    copy_re = re.compile(r"mov\s+w1, w(\d+)")
    low_re = re.compile(r"mov\s+w(\d+), #0x([0-9a-f]+)")
    movk_re = re.compile(r"movk\s+w(\d+), #0x([0-9a-f]+), lsl #16")

    def decode_request(request: int) -> str:
        ioc_type = (request >> 8) & 0xff
        number = request & 0xff
        size = (request >> 16) & 0x3fff
        if ioc_type != 0x49:
            return "unknown ioctl type"
        names = {
            0: "ION_IOC_ALLOC",
            1: "ION_IOC_FREE",
            2: "ION_IOC_MAP",
            4: "ION_IOC_SHARE",
            5: "ION_IOC_IMPORT",
            6: "ION_IOC_CUSTOM",
            7: "ION_IOC_SYNC",
        }
        return f"{names.get(number, 'ION_IOC_UNKNOWN')} (type 'I', nr {number}, size 0x{size:x})"

    for line in disassembly.splitlines():
        match = function_re.search(line)
        if match:
            current = match.group(1)
            prior = []
        call = call_re.search(line)
        if call:
            low = None
            high = None
            register = None
            recent = prior[-32:]
            selected_index = None
            for index in range(len(recent) - 1, -1, -1):
                direct_match = direct_constant_re.search(recent[index])
                if direct_match:
                    register = "1"
                    low = int(direct_match.group(1), 16)
                    selected_index = index
                    break
                copy_match = copy_re.search(recent[index])
                if copy_match:
                    register = copy_match.group(1)
                    selected_index = index
                    break
            if selected_index is not None and register != "1":
                source_lines = recent[:selected_index]
            else:
                source_lines = recent
            for previous in source_lines:
                low_match = low_re.search(previous)
                if low_match and low_match.group(1) == register:
                    low = int(low_match.group(2), 16)
                movk_match = movk_re.search(previous)
                if movk_match and movk_match.group(1) == register:
                    high = int(movk_match.group(2), 16)
            if register == "1" and selected_index is not None:
                for previous in recent[selected_index + 1:]:
                    movk_match = movk_re.search(previous)
                    if movk_match and movk_match.group(1) == "1":
                        high = int(movk_match.group(2), 16)
            if low is not None and high is not None:
                request = f"0x{((high << 16) | low):08x}"
                interpretation = decode_request(int(request, 16))
            elif low is not None and high is None:
                request = f"low-only-0x{low:04x}"
                interpretation = "request high half not recovered from nearby instructions"
            else:
                request = "NOT_RECOVERED"
                interpretation = "request value not recovered from nearby instructions"
            rows.append((current, call.group(1), request, interpretation))
        prior.append(line)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True,
                        help="directory containing already-pulled ELF files")
    parser.add_argument("--output", required=True,
                        help="new output directory; must not already exist")
    parser.add_argument("--dry-run", action="store_true",
                        help="validate paths and print the host-only plan")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output = Path(args.output)
    if not input_dir.is_dir():
        die(f"input directory does not exist: {input_dir}")
    if output.exists():
        die(f"output already exists: {output}")

    tools = ["file", "nm", "objdump", "strings", "shasum"]
    missing = [tool for tool in tools if shutil.which(tool) is None]
    if missing:
        die("missing host tools: " + ", ".join(missing))

    inputs = sorted(input_dir.glob("libion*.so"))
    if not inputs:
        die(f"no libion*.so files in {input_dir}")

    if args.dry_run:
        print("DRY-RUN: no ELF is executed; no device node or ioctl is touched.")
        print(f"input={input_dir}")
        print(f"output={output}")
        print("files:")
        for path in inputs:
            print(path)
        return 0

    output.mkdir(parents=True)
    metadata = output / "metadata.txt"
    metadata.write_text(
        "test_id=" + output.name + "\n"
        + "mode=host-only-static-inspection\n"
        + "start_utc=" + datetime.now(timezone.utc).isoformat() + "\n"
        + f"input_dir={input_dir}\n"
        + "safety=ELFs are inspected but never loaded or executed; no device access\n",
        encoding="utf-8",
    )
    (output / "commands.txt").write_text(
        "host tools only; generated command records are not device commands\n",
        encoding="utf-8",
    )

    all_rows: list[tuple[str, str, str, str, str]] = []
    for source in inputs:
        name = source.name
        source_hash = sha256(source)
        run_capture(["file", str(source)], output / f"{name}.file.txt")
        run_capture(["nm", "-D", str(source)], output / f"{name}.nm-D.txt")
        disassembly_path = output / f"{name}.objdump-d.txt"
        run_capture(["objdump", "-d", str(source)], disassembly_path)
        run_capture(["strings", "-a", str(source)], output / f"{name}.strings.txt")
        disassembly = disassembly_path.read_text(encoding="utf-8", errors="replace")
        for function, callsite, request, interpretation in parse_ioctl_calls(disassembly):
            all_rows.append((name, source_hash, function, "0x" + callsite,
                             request + " | " + interpretation))

    tsv = output / "ioctl-call-sites.tsv"
    with tsv.open("w", encoding="utf-8") as stream:
        stream.write("file\tsha256\tfunction\tcallsite\tstatic_interpretation\n")
        for row in all_rows:
            stream.write("\t".join(row) + "\n")

    summary = output / "summary.md"
    summary.write_text(
        "# Phase 5M ION userspace static inventory\n\n"
        "This is host-only disassembly of already-pulled AArch64 shared objects. "
        "No file was loaded as code, and no Android device node or ioctl was touched.\n\n"
        "The nearby-instruction parser identifies request constants only when the "
        "AArch64 `mov`/`movk` pattern is visible. It is a static candidate, not a "
        "runtime observation. See `ioctl-call-sites.tsv` and raw `objdump-d` files.\n",
        encoding="utf-8",
    )
    with metadata.open("a", encoding="utf-8") as stream:
        stream.write("end_utc=" + datetime.now(timezone.utc).isoformat() + "\n")
    manifest = output / "sha256sums.txt"
    files = sorted(path for path in output.rglob("*")
                   if path.is_file() and path != manifest)
    with manifest.open("w", encoding="utf-8") as stream:
        for path in files:
            stream.write(f"{sha256(path)}  {path.relative_to(output)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
