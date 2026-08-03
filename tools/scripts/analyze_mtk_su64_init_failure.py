#!/usr/bin/env python3
"""Analyze the archived mtk-su64 failure path without executing the payload.

This tool is intentionally host-only.  It invokes file/strings/llvm-objdump on
the supplied ELF and never runs the ELF, sends it to a device, or invokes ADB.
The output directory must not already exist so that derived evidence cannot be
silently overwritten.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


DEFAULT_LLVM_OBJDUMP_CANDIDATES = (
    "/opt/homebrew/opt/llvm/bin/llvm-objdump",
    "/opt/homebrew/bin/llvm-objdump",
    "/usr/local/bin/llvm-objdump",
    "/usr/bin/llvm-objdump",
)


def fail(message: str) -> "NoReturn":
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def resolve_tool(explicit: str | None, candidates: tuple[str, ...], name: str) -> str:
    if explicit:
        path = shutil.which(explicit) or (explicit if Path(explicit).is_file() else None)
        if not path:
            fail(f"{name} not found: {explicit}")
        return path
    for candidate in candidates:
        if Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    path = shutil.which(name)
    if path:
        return path
    fail(f"{name} not found; pass --{name.replace('-', '_')}")


def run_capture(command: list[str]) -> tuple[int, bytes, bytes]:
    completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return completed.returncode, completed.stdout, completed.stderr


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def address_from_line(line: str) -> int | None:
    match = re.match(r"^\s*([0-9a-f]+):", line)
    return int(match.group(1), 16) if match else None


def address_slice(lines: list[str], start: int, end: int) -> str:
    selected = []
    for line in lines:
        address = address_from_line(line)
        if address is not None and start <= address < end:
            selected.append(line)
    return "".join(selected)


def decode_ioctl(request: int) -> dict[str, int | str]:
    direction = (request >> 30) & 0x3
    direction_name = {0: "none", 1: "write", 2: "read", 3: "read|write"}.get(
        direction, "unknown"
    )
    return {
        "request": f"0x{request:08x}",
        "direction_bits": direction,
        "direction": direction_name,
        "size": (request >> 16) & 0x3FFF,
        "magic": f"0x{(request >> 8) & 0xFF:02x}",
        "number": request & 0xFF,
    }


def write_sha256_manifest(root: Path) -> None:
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "sha256sums.txt":
            entries.append(f"{sha256_file(path)}  {path.relative_to(root)}")
    (root / "sha256sums.txt").write_text("\n".join(entries) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", required=True, help="local mtk-su64 ELF; it is only read")
    parser.add_argument("--output", required=True, help="new derived-evidence directory")
    parser.add_argument("--llvm-objdump", dest="llvm_objdump")
    parser.add_argument("--strings", dest="strings_bin")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload = Path(args.payload).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if not payload.is_file():
        fail(f"payload is not a regular file: {payload}")
    if output.exists():
        fail(f"refusing to overwrite existing output directory: {output}")

    objdump = resolve_tool(args.llvm_objdump, DEFAULT_LLVM_OBJDUMP_CANDIDATES, "llvm-objdump")
    strings_bin = resolve_tool(args.strings_bin, (), "strings")
    commands = [
        ["file", str(payload)],
        [objdump, "-d", "--no-show-raw-insn", str(payload)],
        [strings_bin, "-a", "-t", "x", str(payload)],
    ]
    if args.dry_run:
        print("HOST-ONLY DRY-RUN; the payload will not be executed or sent to a device.")
        for command in commands:
            print(" ".join(command))
        print(f"would create: {output}")
        return 0

    output.mkdir(parents=True)
    (output / "commands.txt").write_text(
        "# Host-only analysis; no ADB/device command and no payload execution.\n"
        + "\n".join(" ".join(command) for command in commands)
        + "\n",
        encoding="utf-8",
    )
    metadata = {
        "analysis": "host_only_mtk_su64_init_failure",
        "payload": str(payload),
        "payload_sha256": sha256_file(payload),
        "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "device_mutation": "none",
        "payload_executed": False,
        "adb_invoked": False,
        "llvm_objdump": objdump,
        "strings": strings_bin,
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    captured: dict[str, bytes] = {}
    for index, command in enumerate(commands):
        rc, stdout, stderr = run_capture(command)
        key = ("file" if index == 0 else "disassembly" if index == 1 else "strings")
        captured[key] = stdout
        (output / f"{key}.stdout.txt").write_bytes(stdout)
        (output / f"{key}.stderr.txt").write_bytes(stderr)
        (output / f"{key}.exit_code.txt").write_text(f"{rc}\n", encoding="utf-8")
        if rc != 0:
            fail(f"{key} failed with exit code {rc}")

    disassembly_lines = captured["disassembly"].decode("utf-8", errors="replace").splitlines(keepends=True)
    (output / "entry-wrapper-0x17a0-0x1924.txt").write_text(
        address_slice(disassembly_lines, 0x17A0, 0x1924), encoding="utf-8"
    )
    (output / "init-allocator-0x2f80-0x30a0.txt").write_text(
        address_slice(disassembly_lines, 0x2F80, 0x30A0), encoding="utf-8"
    )
    (output / "init-context-0x3300-0x34bc.txt").write_text(
        address_slice(disassembly_lines, 0x3300, 0x34BC), encoding="utf-8"
    )
    (output / "cleanup-free-0x34c0-0x35f0.txt").write_text(
        address_slice(disassembly_lines, 0x34C0, 0x35F0), encoding="utf-8"
    )

    findings = {
        "entry_wrapper": {
            "call_site": "0x17d8: bl 0x3300",
            "failure_test": "0x17dc: tbnz w0, #0x1f, 0x180c",
            "reported_message": "0x1818 loads rodata offset 0xb0dd; 0x181c saves w0; 0x181c/0x1820 negates w0 for %d",
            "observed_mapping": "reported step 3 corresponds to helper return -3",
        },
        "context_initializer": {
            "allocator": "0x33d8 calls 0x2f80 with w1=0x3000",
            "failure_branch": "0x33e0 cbz w0, 0x34c0",
            "failure_return": "0x34c8 sets w21=-3, then frees the context buffers",
            "interpretation": "the critical step 3 is the allocator helper returning zero, not a later credential/SELinux diagnostic branch",
        },
        "allocator_helper": {
            "syscall": "0x2fd0 sets syscall number 29 (ioctl)",
            "file_descriptor": "loaded from context offset 0x00",
            "argument": "context offset 0x208",
            "request": decode_ioctl(0x40087807),
            "input_count": "0x2fac shifts caller w1=0x3000 right by two and stores 0x0c00 in context offset 0x208",
            "fallback": "on EINVAL and a request at least 0x1000, retries the same request with 0x400",
            "return_semantics": "successful ioctl path returns the requested size; failed allocation path returns zero",
        },
        "cleanup": {
            "request": decode_ioctl(0x40087808),
            "call_sites": ["0x3508", "0x3564"],
            "interpretation": "the cleanup path uses the CMDQ free-write-address request",
        },
        "classification": {
            "confirmed": [
                "T03 emitted Failed critical init step 3 and exit code 1",
                "the static wrapper maps step 3 to the -3 return branch at 0x34c0",
                "the branch reaches an ioctl request with magic x and number 7",
                "the request encoding matches CMDQ_IOCTL_ALLOC_WRITE_ADDRESS in the public MediaTek header",
            ],
            "strong_evidence": [
                "the archived payload's initialization failure is a CMDQ write-address allocation failure",
            ],
            "unknown": [
                "the exact errno returned by the PS7330 driver was not emitted by the payload",
                "whether the running kernel still contains CVE-2020-0069",
                "whether a different payload would be compatible with this exact CMDQ implementation",
            ],
        },
    }
    (output / "findings.json").write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
    (output / "public-cmdq-reference.md").write_text(
        "# Public CMDQ ioctl reference\n\n"
        "The request at `0x2f80` is decoded as `_IOW('x', 7, 8-byte struct)`; "
        "the corresponding public MediaTek header names this request "
        "`CMDQ_IOCTL_ALLOC_WRITE_ADDRESS`. The cleanup request is number 8, "
        "`CMDQ_IOCTL_FREE_WRITE_ADDRESS`. These references identify the ioctl "
        "encoding only; they do not prove the PS7330 driver is vulnerable.\n\n"
        "- https://android.googlesource.com/kernel/mediatek/+/android-mtk-3.18/drivers/misc/mediatek/cmdq/v2/cmdq_driver.h\n"
        "- https://blog.quarkslab.com/cve-2020-0069-autopsy-of-the-most-stable-mediatek-rootkit.html\n",
        encoding="utf-8",
    )
    metadata["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    write_sha256_manifest(output)
    print(f"Wrote host-only derived evidence to {output}")
    print(f"Payload was read but not executed: {payload}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
