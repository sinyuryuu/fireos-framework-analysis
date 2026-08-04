#!/usr/bin/env python3
"""Host-only GhostLock reachability review.

This tool reads already-collected kernel source and configuration artifacts.  It
does not connect to ADB, execute an input binary, compile code, derive kernel
addresses, or create an exploit payload.  The output is deliberately limited to
source/config reachability evidence and an exact-signed-binary boundary.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


CONFIG_KEYS = (
    "CONFIG_FUTEX",
    "CONFIG_RT_MUTEXES",
    "CONFIG_FUTEX_PI",
    "CONFIG_PREEMPT",
    "CONFIG_RANDOMIZE_BASE",
    "CONFIG_ARM64_4K_PAGES",
    "CONFIG_ARM64_VA_BITS",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def line_records(lines: list[str], needles: Iterable[str], start: int = 1, end: int | None = None) -> list[dict]:
    wanted = tuple(needles)
    upper = len(lines) if end is None else min(end, len(lines))
    records = []
    for number in range(max(start, 1), upper + 1):
        text = lines[number - 1]
        if any(needle in text for needle in wanted):
            records.append({"line": number, "text": text.strip()})
    return records


def function_span(lines: list[str], name: str, signature: str | None = None) -> tuple[int, int] | None:
    if signature is None:
        signature = rf"\b{name}\s*\("
    start = None
    for index, text in enumerate(lines, start=1):
        if re.search(signature, text):
            start = index
            break
    if start is None:
        return None

    depth = 0
    opened = False
    for number in range(start, len(lines) + 1):
        text = lines[number - 1]
        # The selected functions are ordinary C functions; counting braces is
        # sufficient for these bounded source observations and avoids parsing
        # or compiling untrusted source.
        depth += text.count("{")
        if "{" in text:
            opened = True
        depth -= text.count("}")
        if opened and depth == 0:
            return start, number
    return start, len(lines)


def parse_config(path: Path) -> dict[str, dict[str, object]]:
    lines = read_lines(path)
    result: dict[str, dict[str, object]] = {}
    for key in CONFIG_KEYS:
        value = None
        raw = None
        line = None
        for number, text in enumerate(lines, start=1):
            match = re.match(rf"^{re.escape(key)}=(.*)$", text)
            if match:
                value = match.group(1)
                raw = text
                line = number
                break
            if text == f"# {key} is not set":
                value = "not_set"
                raw = text
                line = number
                break
        result[key] = {
            "value": value,
            "raw": raw,
            "line": line,
            "present": line is not None,
        }
    return result


def safe_output(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    forbidden = {Path("/"), Path("/tmp"), Path("/var/tmp"), Path.cwd().resolve()}
    if resolved in forbidden:
        raise ValueError(f"refusing broad or temporary output path: {resolved}")
    if resolved.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {resolved}")
    return resolved


def relative_or_absolute(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path.resolve())


def source_observations(path: Path, config: dict[str, dict[str, object]]) -> tuple[dict, list[dict]]:
    lines = read_lines(path)
    remove_span = function_span(
        lines,
        "remove_waiter",
        r"(?:static\s+)?void\s+(?:__sched\s+)?remove_waiter\s*\(",
    )
    proxy_span = function_span(
        lines,
        "rt_mutex_start_proxy_lock",
        r"\b(?:int|long)\s+rt_mutex_start_proxy_lock\s*\(",
    )
    observations: list[dict] = []

    if remove_span:
        start, end = remove_span
        current_cleanup = line_records(lines, ("current->pi_blocked_on",), start, end)
        waiter_task = line_records(lines, ("waiter->task",), start, end)
        observations.append({
            "symbol": "remove_waiter",
            "span": {"start_line": start, "end_line": end},
            "current_task_cleanup": bool(current_cleanup),
            "current_task_cleanup_lines": current_cleanup,
            "waiter_task_reference": bool(waiter_task),
            "waiter_task_reference_lines": waiter_task,
            "classification": "PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN" if current_cleanup and not waiter_task else "FIXED_OR_DIFFERENT_PATTERN",
        })
    else:
        observations.append({
            "symbol": "remove_waiter",
            "span": None,
            "current_task_cleanup": False,
            "current_task_cleanup_lines": [],
            "waiter_task_reference": False,
            "waiter_task_reference_lines": [],
            "classification": "NOT_FOUND",
        })

    if proxy_span:
        start, end = proxy_span
        proxy_calls = line_records(lines, ("remove_waiter",), start, end)
        observations.append({
            "symbol": "rt_mutex_start_proxy_lock",
            "span": {"start_line": start, "end_line": end},
            "remove_waiter_call": bool(proxy_calls),
            "remove_waiter_call_lines": proxy_calls,
            "classification": "PROXY_ERROR_PATH_PRESENT" if proxy_calls else "PROXY_CALL_NOT_FOUND",
        })
    else:
        observations.append({
            "symbol": "rt_mutex_start_proxy_lock",
            "span": None,
            "remove_waiter_call": False,
            "remove_waiter_call_lines": [],
            "classification": "NOT_FOUND",
        })

    pi_tokens = line_records(
        lines,
        (
            "FUTEX_WAIT_REQUEUE_PI",
            "FUTEX_CMP_REQUEUE_PI",
            "futex_requeue",
            "rt_mutex_start_proxy_lock",
        ),
    )
    observations.append({
        "symbol": "futex_pi_dispatch_and_requeue",
        "pi_operation_or_requeue_lines": pi_tokens,
        "classification": "PI_REQUEUE_SOURCE_PATH_PRESENT" if pi_tokens else "PI_REQUEUE_SOURCE_PATH_NOT_FOUND",
    })

    observations.append({
        "symbol": "config_focus",
        "values": config,
        "classification": "CONFIG_CAPTURED",
    })
    return {"line_count": len(lines)}, observations


def fixed_reference_observation(path: Path) -> dict:
    lines = read_lines(path)
    span = function_span(
        lines,
        "remove_waiter",
        r"(?:static\s+)?void\s+(?:__sched\s+)?remove_waiter\s*\(",
    )
    if not span:
        return {
            "symbol": "remove_waiter",
            "span": None,
            "waiter_task_reference": False,
            "current_task_cleanup": False,
            "classification": "FIXED_REFERENCE_NOT_FOUND",
        }
    start, end = span
    current_cleanup = line_records(lines, ("current->pi_blocked_on",), start, end)
    waiter_task = line_records(lines, ("waiter->task",), start, end)
    return {
        "symbol": "remove_waiter",
        "span": {"start_line": start, "end_line": end},
        "waiter_task_reference": bool(waiter_task),
        "waiter_task_reference_lines": waiter_task,
        "current_task_cleanup": bool(current_cleanup),
        "current_task_cleanup_lines": current_cleanup,
        "classification": "WAITER_TASK_CLEANUP_REFERENCE" if waiter_task and not current_cleanup else "FIXED_REFERENCE_DIFFERENT_OR_INCOMPLETE",
    }


def build_result(args: argparse.Namespace) -> tuple[dict, list[dict]]:
    source = Path(args.rtmutex).expanduser().resolve()
    futex = Path(args.futex).expanduser().resolve()
    config_path = Path(args.config).expanduser().resolve()
    fixed = Path(args.fixed_reference).expanduser().resolve()
    for path in (source, futex, config_path, fixed):
        if not path.is_file():
            raise FileNotFoundError(f"input file not found: {path}")

    config = parse_config(config_path)
    source_meta, rtmutex_obs = source_observations(source, config)
    futex_lines = read_lines(futex)
    futex_obs = {
        "line_count": len(futex_lines),
        "pi_dispatch_lines": line_records(
            futex_lines,
            ("FUTEX_WAIT_REQUEUE_PI", "FUTEX_CMP_REQUEUE_PI", "futex_requeue", "rt_mutex_start_proxy_lock"),
        ),
    }
    fixed_obs = fixed_reference_observation(fixed)

    remove = next(item for item in rtmutex_obs if item["symbol"] == "remove_waiter")
    proxy = next(item for item in rtmutex_obs if item["symbol"] == "rt_mutex_start_proxy_lock")
    pi_source = next(item for item in rtmutex_obs if item["symbol"] == "futex_pi_dispatch_and_requeue")
    config_futex = config["CONFIG_FUTEX"]["value"] == "y"
    config_rtmutex = config["CONFIG_RT_MUTEXES"]["value"] == "y"
    old_pattern = remove["current_task_cleanup"] and not remove["waiter_task_reference"]
    pi_path = bool(pi_source["pi_operation_or_requeue_lines"] or futex_obs["pi_dispatch_lines"])
    proxy_path = bool(proxy["remove_waiter_call"])
    source_candidate = old_pattern and pi_path and proxy_path and config_futex and config_rtmutex

    observations = []
    for item in rtmutex_obs:
        observations.append({"source": relative_or_absolute(source), **item})
    observations.append({"source": relative_or_absolute(futex), "symbol": "futex.c", **futex_obs})
    observations.append({"source": relative_or_absolute(fixed), **fixed_obs})

    input_meta = []
    for path, kind in ((source, "target_rtmutex_source"), (futex, "target_futex_source"), (config_path, "device_config"), (fixed, "fixed_reference")):
        input_meta.append({
            "kind": kind,
            "path": relative_or_absolute(path),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        })

    result = {
        "analysis": {
            "name": "Phase 5BF GhostLock source/config reachability review",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "device_io": False,
            "executed_input": False,
            "compiled_code": False,
            "addresses_or_offsets": False,
            "payload_or_reproducer": False,
            "scope": "host-only source and configuration evidence; not an exploitability or root result",
        },
        "inputs": input_meta,
        "target_source": source_meta,
        "futex_source": futex_obs,
        "fixed_reference": fixed_obs,
        "observations": observations,
        "classification": {
            "source_and_config_reachability": "SOURCE_AND_CONFIG_REACHABILITY_CANDIDATE" if source_candidate else "INSUFFICIENT_SOURCE_OR_CONFIG_EVIDENCE",
            "exact_signed_binary_proven": False,
            "runtime_exploitability_proven": False,
            "root_or_privilege_gain_proven": False,
            "config_futex_pi_literal": config["CONFIG_FUTEX_PI"],
            "config_futex_pi_note": "The old tree's PI operation dispatch is assessed from source. An absent literal CONFIG_FUTEX_PI line is not treated as proof that the PI path is disabled.",
        },
        "safety": {
            "no_adb": True,
            "no_flash": True,
            "no_bootloader": True,
            "no_kernel_memory_access": True,
            "no_exploit_offsets": True,
            "no_unknown_ioctl": True,
        },
    }
    return result, observations


def write_outputs(result: dict, observations: list[dict], output: Path) -> None:
    output.mkdir(parents=True)
    json_path = output / "reachability.json"
    csv_path = output / "observations.csv"
    result_path = output / "result.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("source", "symbol", "line", "observation", "classification"),
            lineterminator="\n",
        )
        writer.writeheader()
        for item in observations:
            source = item.get("source", "")
            symbol = item.get("symbol", "")
            classification = item.get("classification", "")
            line_items = []
            for key in ("current_task_cleanup_lines", "waiter_task_reference_lines", "remove_waiter_call_lines", "pi_operation_or_requeue_lines"):
                line_items.extend(item.get(key, []))
            if not line_items:
                writer.writerow({"source": source, "symbol": symbol, "line": "", "observation": "", "classification": classification})
            else:
                for line_item in line_items:
                    writer.writerow({
                        "source": source,
                        "symbol": symbol,
                        "line": line_item.get("line", ""),
                        "observation": line_item.get("text", ""),
                        "classification": classification,
                    })

    classification = result["classification"]
    result_path.write_text(
        "# Phase 5BF GhostLock reachability review\n\n"
        "This artifact is host-only. It does not execute a reproducer, derive an address, "
        "touch the device, or claim root.\n\n"
        f"- Source/config classification: `{classification['source_and_config_reachability']}`\n"
        f"- Exact signed binary proven: `{classification['exact_signed_binary_proven']}`\n"
        f"- Runtime exploitability proven: `{classification['runtime_exploitability_proven']}`\n"
        f"- Root/privilege gain proven: `{classification['root_or_privilege_gain_proven']}`\n"
        "- Safety: no ADB, flash, bootloader, kernel-memory, offset, payload, or unknown-ioctl operation.\n",
        encoding="utf-8",
    )

    manifest_lines = []
    for path in (json_path, csv_path, result_path):
        manifest_lines.append(f"{sha256(path)}  {path.name}")
    (output / "sha256sums.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rtmutex", required=True, help="target build-selected rtmutex.c")
    parser.add_argument("--futex", required=True, help="target build-selected futex.c")
    parser.add_argument("--config", required=True, help="read-only device kernel.config artifact")
    parser.add_argument("--fixed-reference", required=True, help="read-only fixed reference rtmutex.c")
    parser.add_argument("--output", required=True, help="new output directory")
    parser.add_argument("--dry-run", action="store_true", help="print the plan without reading inputs or writing output")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY-RUN: would read four source/config files and write a new reachability artifact directory")
        print("DRY-RUN: no ADB, device execution, compilation, address extraction, payload, or flash operation")
        return 0

    try:
        output = safe_output(Path(args.output))
        result, observations = build_result(args)
        write_outputs(result, observations, output)
    except (FileExistsError, FileNotFoundError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
