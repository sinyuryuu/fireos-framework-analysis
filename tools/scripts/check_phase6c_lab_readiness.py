#!/usr/bin/env python3
"""Host-only Phase 6C LAB_ONLY readiness audit.

This script inspects local source/config and host tool availability only. It
never invokes ADB, compiles or boots a kernel, creates a futex trigger, or
modifies/deletes files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_config(path: Path) -> dict[str, str | bool]:
    values: dict[str, str | bool] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("CONFIG_") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = True if value == "y" else False if value == "n" else value
        elif line.startswith("# CONFIG_") and line.endswith(" is not set"):
            values[line[2:-11]] = False
    return values


def tool_version(path: str | None) -> str | None:
    if not path:
        return None
    try:
        result = subprocess.run([path, "--version"], capture_output=True,
                                text=True, timeout=3, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"unavailable: {exc}"
    return (result.stdout or result.stderr).splitlines()[0] if (result.stdout or result.stderr) else str(result.returncode)


def build(source: Path, config_path: Path) -> dict:
    config = parse_config(config_path)
    names = ["clang", "clang++", "make", "qemu-system-aarch64", "qemu-img",
             "llvm-objdump", "llvm-readelf", "aarch64-linux-gnu-gcc", "python3"]
    tools = {}
    for name in names:
        path = shutil.which(name)
        tools[name] = {"path": path, "version": tool_version(path)}
    required = ["kernel/futex.c", "kernel/locking/rtmutex.c",
                "kernel/locking/rtmutex_common.h", "Makefile", "arch/arm64",
                "tools/testing/selftests/futex"]
    gates = ["CONFIG_ARM64", "CONFIG_MMU", "CONFIG_SMP", "CONFIG_PREEMPT",
             "CONFIG_FUTEX", "CONFIG_RT_MUTEXES", "CONFIG_SLUB", "CONFIG_ION",
             "CONFIG_RANDOMIZE_BASE", "CONFIG_KASAN", "CONFIG_DEBUG_INFO",
             "CONFIG_USERFAULTFD", "CONFIG_FTRACE", "CONFIG_FUNCTION_TRACER"]
    qemu = tools["qemu-system-aarch64"]["path"] is not None
    debug = config.get("CONFIG_KASAN") is True and config.get("CONFIG_DEBUG_INFO") is True
    present = all((source / item).exists() for item in required)
    usage = shutil.disk_usage(Path.cwd())
    reasons = []
    if not qemu:
        reasons.append("qemu-system-aarch64 missing")
    if not debug:
        reasons.append("CONFIG_KASAN and CONFIG_DEBUG_INFO are not both enabled")
    if not present:
        reasons.append("required source tree is incomplete")
    return {
        "schema": "phase6c-lab-readiness-v1",
        "scope": {"host_only": True, "lab_only": True, "device_execution": False,
                   "kernel_build": False, "kernel_boot": False, "futex_trigger": False,
                   "file_mutation": False, "installation": False},
        "host": {"system": platform.system(), "machine": platform.machine(),
                 "python": sys.version.split()[0], "cwd_free_bytes": usage.free},
        "inputs": {"source": str(source), "source_exists": source.is_dir(),
                   "config": str(config_path), "config_sha256": sha256(config_path),
                   "required_tree_present": present},
        "config": {key: config.get(key) for key in gates},
        "tools": tools,
        "readiness": {"status": "READY_FOR_SEPARATE_REVIEW" if qemu and debug and present else "NOT_READY",
                       "qemu_aarch64_available": qemu,
                       "debug_symbols_and_kasan_enabled": debug,
                       "reasons": reasons},
        "safety": ["No ADB/device command", "No source/config mutation",
                    "No kernel build/boot", "No futex/race/panic/memory/root payload"],
    }


def write_output(output: Path, result: dict, command: str) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    (output / "commands.txt").write_text(command + "\n", encoding="utf-8")
    (output / "readiness.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    readiness = result["readiness"]
    lines = [
        "# Phase 6C LAB_ONLY readiness audit", "", f"Status: **{readiness['status']}**", "",
        "Host-only audit; no ADB, source mutation, kernel build/boot, futex trigger,",
        "race, panic, memory operation, or root payload was performed.", "",
        "## Current result", "",
        f"- Host: `{result['host']['system']} {result['host']['machine']}`",
        f"- Free space at audit time: `{result['host']['cwd_free_bytes']}` bytes",
        f"- QEMU AArch64 available: `{readiness['qemu_aarch64_available']}`",
        f"- KASAN + DEBUG_INFO both enabled: `{readiness['debug_symbols_and_kasan_enabled']}`",
        f"- Required source tree present: `{result['inputs']['required_tree_present']}`", "",
        "## Reasons", "",
    ]
    lines.extend(f"- {reason}" for reason in readiness["reasons"] or ["No blocking reason recorded."])
    lines.extend(["", "Even if later prepared, any instrumented kernel or runtime test must remain",
                  "LAB_ONLY and must not be copied to or run on the stock PS7331 tablet."])
    (output / "result.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = []
    for path in sorted(output.iterdir()):
        if path.name != "sha256sums.txt":
            manifest.append(f"{sha256(path)}  {path.name}")
    (output / "sha256sums.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "device_execution": False,
                          "source_root": str(args.source_root), "config": str(args.config),
                          "output": str(args.output)}, indent=2))
        return 0
    if not args.source_root.is_dir() or not args.config.is_file():
        parser.error("source root/config input is missing")
    write_output(args.output, build(args.source_root, args.config), " ".join(sys.argv))
    print(f"wrote host-only Phase 6C readiness audit: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
