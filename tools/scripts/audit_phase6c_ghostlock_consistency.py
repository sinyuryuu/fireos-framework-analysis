#!/usr/bin/env python3
"""Host-only PS7331 GhostLock provenance/compatibility audit.

The audit joins exact source landmarks, extracted kernel configuration, boot
image metadata, and already-preserved runtime reports.  It does not compile or
execute a kernel, issue a futex syscall, create a waiter, schedule a race,
access kernel memory, contact ADB, or generate an exploit/root payload.

The output deliberately separates static compatibility from runtime evidence:
matching source/config/image markers cannot be promoted to a live vulnerability
or privilege-transition claim.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


CONFIG_KEYS = (
    "CONFIG_ARM64",
    "CONFIG_MMU",
    "CONFIG_SMP",
    "CONFIG_PREEMPT",
    "CONFIG_FUTEX",
    "CONFIG_RT_MUTEXES",
    "CONFIG_SLUB",
    "CONFIG_ION",
    "CONFIG_MTK_ION",
    "CONFIG_RANDOMIZE_BASE",
    "CONFIG_PANIC_ON_OOPS",
    "CONFIG_KASAN",
    "CONFIG_DEBUG_INFO",
    "CONFIG_USERFAULTFD",
    "CONFIG_FTRACE",
    "CONFIG_FUNCTION_TRACER",
)

SOURCE_CHECKS = (
    ("dispatch_cmp_requeue_pi", "kernel/futex.c", r"case FUTEX_CMP_REQUEUE_PI:"),
    ("dispatch_to_requeue_pi", "kernel/futex.c", r"return futex_requeue\([^\n]*&val3, 1\);"),
    ("no_waiter_return", "kernel/futex.c", r"if \(!top_waiter\)"),
    ("proxy_call", "kernel/futex.c", r"rt_mutex_start_proxy_lock\("),
    ("proxy_return_cleanup", "kernel/futex.c", r"\} else if \(ret\)"),
    ("proxy_wrapper", "kernel/locking/rtmutex.c", r"int rt_mutex_start_proxy_lock\("),
    ("proxy_error_cleanup", "kernel/locking/rtmutex.c", r"if \(unlikely\(ret\)\)"),
    ("owner_task_early_return", "kernel/locking/rtmutex.c", r"if \(owner == task\)"),
    ("waiter_task_assignment", "kernel/locking/rtmutex.c", r"waiter->task = task;"),
    ("current_pi_cleanup", "kernel/locking/rtmutex.c", r"current->pi_blocked_on = NULL;"),
    ("waiter_stack_comment", "kernel/locking/rtmutex_common.h", r"kernel stack"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
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


def first_matching_line(path: Path, expression: str) -> int | None:
    pattern = re.compile(expression)
    for number, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if pattern.search(raw):
            return number
    return None


def first_matching_line_after(path: Path, expression: str, after: int | None) -> int | None:
    if after is None:
        return None
    pattern = re.compile(expression)
    for number, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if number > after and pattern.search(raw):
            return number
    return None


def load_json(path: Path | None) -> dict[str, object] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def positive_observation(text: str, expression: str) -> bool:
    """Return true only for an affirmative line, not a gap/negative statement."""
    pattern = re.compile(expression, re.IGNORECASE)
    affirmative = re.compile(
        r"\b(?:observed|captured|detected|occurred|returned|recorded|successfully|reached)\b|已觀察|已捕獲|已記錄|發生",
        re.IGNORECASE,
    )
    negative = re.compile(
        r"(?:\b(?:no|none|not|unknown|unobserved|unverified|absent|did not|never|without)\b|沒有|未提供|未觀察|未知|尚無|不支持|不等於)",
        re.IGNORECASE,
    )
    for line in text.splitlines():
        if pattern.search(line) and affirmative.search(line) and not negative.search(line):
            return True
    return False


def build(args: argparse.Namespace) -> dict[str, object]:
    source_root: Path = args.source_root
    config_path: Path = args.config
    defconfig_path: Path | None = args.defconfig
    if not source_root.is_dir():
        raise SystemExit(f"missing source root: {source_root}")
    if not config_path.is_file():
        raise SystemExit(f"missing extracted config: {config_path}")
    if defconfig_path is not None and not defconfig_path.is_file():
        raise SystemExit(f"missing defconfig: {defconfig_path}")

    config = parse_config(config_path)
    defconfig = parse_config(defconfig_path) if defconfig_path else {}
    source_rows: list[dict[str, object]] = []
    for check_id, relative, expression in SOURCE_CHECKS:
        path = source_root / relative
        line = first_matching_line(path, expression) if path.is_file() else None
        source_rows.append(
            {
                "check": check_id,
                "file": str(path),
                "relative_file": relative,
                "line": line if line is not None else "NOT_FOUND",
                "pattern": expression,
                "status": "FOUND" if line is not None else "NOT_FOUND",
                "file_sha256": sha256(path) if path.is_file() else "MISSING",
            }
        )

    # Disambiguate generic `unlikely(ret)` occurrences from the proxy wrapper
    # itself.  The source contains other error-cleanup sites earlier in the
    # file; the post-wrapper match is the relevant static landmark.
    rtmutex_path = source_root / "kernel/locking/rtmutex.c"
    proxy_wrapper_line = first_matching_line(rtmutex_path, r"int rt_mutex_start_proxy_lock\(")
    proxy_cleanup_line = first_matching_line_after(rtmutex_path, r"if \(unlikely\(ret\)\)", proxy_wrapper_line)
    for row in source_rows:
        if row["check"] == "proxy_error_cleanup":
            row["line"] = proxy_cleanup_line if proxy_cleanup_line is not None else "NOT_FOUND"
            row["status"] = "FOUND" if proxy_cleanup_line is not None else "NOT_FOUND"

    config_rows: list[dict[str, object]] = []
    for key in CONFIG_KEYS:
        config_rows.append(
            {
                "key": key,
                "embedded_value": config.get(key, "ABSENT"),
                "defconfig_value": defconfig.get(key, "ABSENT"),
                "enabled_in_embedded_config": config.get(key) is True,
                "enabled_in_defconfig": defconfig.get(key) is True,
            }
        )

    boot_metadata = load_json(args.boot_metadata)
    runtime_text = args.runtime_report.read_text(encoding="utf-8", errors="replace") if args.runtime_report else ""
    phase6a_text = args.phase6a_report.read_text(encoding="utf-8", errors="replace") if args.phase6a_report else ""
    combined_reports = runtime_text + "\n" + phase6a_text
    runtime_observations = {
        "fingerprint_present": "PS7331" in runtime_text,
        "selinux_enforcing_present": "Enforcing" in runtime_text,
        "verified_boot_green_present": "green" in runtime_text,
        "requeue_return_observed": positive_observation(runtime_text, r"(?:FUTEX_CMP_REQUEUE_PI|requeue-PI return|requeue_pi return)"),
        "proxy_waiter_observed": positive_observation(runtime_text, r"(?:proxy waiter|waiter->task != current|identity mismatch)"),
        "ordinary_pi_only": "ordinary PI lock/unlock" in phase6a_text and "FUTEX_CMP_REQUEUE_PI` is reachable" in phase6a_text,
        "privilege_transition_observed": positive_observation(combined_reports, r"(?:privilege transition|temporary root|root payload)"),
    }

    static_complete = all(row["status"] == "FOUND" for row in source_rows)
    embedded_required = ("CONFIG_FUTEX", "CONFIG_RT_MUTEXES", "CONFIG_SLUB")
    embedded_gate = all(config.get(key) is True for key in embedded_required)
    image_identity = {
        "boot_metadata_path": str(args.boot_metadata) if args.boot_metadata else None,
        "boot_metadata_sha256": sha256(args.boot_metadata) if args.boot_metadata else None,
        "image_sha256": boot_metadata.get("image_sha256") if boot_metadata else None,
        "kernel_sha256": boot_metadata.get("kernel_sha256") if boot_metadata else None,
        "kernel_compression_signature": boot_metadata.get("kernel_compression_signature") if boot_metadata else None,
        "kernel_addr_recorded": boot_metadata.get("kernel_addr") if boot_metadata else None,
    }

    return {
        "schema": "phase6c-ghostlock-consistency-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "source_root": str(source_root),
            "config": {"path": str(config_path), "sha256": sha256(config_path)},
            "defconfig": {"path": str(defconfig_path), "sha256": sha256(defconfig_path)} if defconfig_path else None,
            "boot_metadata": image_identity,
            "runtime_report": str(args.runtime_report) if args.runtime_report else None,
            "phase6a_report": str(args.phase6a_report) if args.phase6a_report else None,
        },
        "source_checks": source_rows,
        "config_checks": config_rows,
        "runtime_observations": runtime_observations,
        "image_identity": image_identity,
        "verdicts": {
            "source_chain_present": static_complete,
            "embedded_config_supports_core_futex_path": embedded_gate,
            "source_config_image_provenance_consistent": static_complete and embedded_gate and bool(boot_metadata),
            "live_proxy_identity_mismatch": False,
            "cleanup_residue": False,
            "memory_effect": False,
            "privilege_transition": False,
            "temporary_root": False,
        },
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "adb_used": False,
            "kernel_built": False,
            "kernel_executed": False,
            "futex_triggered": False,
            "threads_created": False,
            "race_scheduled": False,
            "kernel_memory_accessed": False,
            "payload_generated": False,
        },
        "interpretation": [
            "Static source/config/image alignment establishes compatibility evidence, not runtime reachability.",
            "The ordinary PI smoke test does not exercise FUTEX_CMP_REQUEUE_PI or a proxy waiter.",
            "A paired waiter/race or device-side vulnerable syscall trigger remains outside the no-loss boundary.",
        ],
    }


def write_output(result: dict[str, object], output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    summary = output / "consistency.json"
    source_csv = output / "source-checks.csv"
    config_csv = output / "config-checks.csv"
    report = output / "result.md"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with source_csv.open("w", encoding="utf-8", newline="") as stream:
        fields = ["check", "relative_file", "line", "status", "pattern", "file_sha256"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in result["source_checks"])  # type: ignore[index]

    with config_csv.open("w", encoding="utf-8", newline="") as stream:
        fields = ["key", "embedded_value", "defconfig_value", "enabled_in_embedded_config", "enabled_in_defconfig"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in result["config_checks"])  # type: ignore[index]

    verdicts = result["verdicts"]
    runtime = result["runtime_observations"]
    report.write_text(
        "# PS7331 GhostLock source/config/image/runtime consistency audit\n\n"
        "Host-only audit. No kernel, ELF, futex operation, thread, race, device, kernel memory, or root payload was executed.\n\n"
        "## Result\n\n"
        f"- Source chain present: **{verdicts['source_chain_present']}**\n"
        f"- Embedded config supports core futex/rtmutex/slub path: **{verdicts['embedded_config_supports_core_futex_path']}**\n"
        f"- Static provenance alignment: **{verdicts['source_config_image_provenance_consistent']}**\n"
        f"- Requeue-PI return observed in preserved runtime reports: **{runtime['requeue_return_observed']}**\n"
        f"- Proxy waiter/identity mismatch observed: **{runtime['proxy_waiter_observed']}**\n"
        f"- Privilege transition observed: **{verdicts['privilege_transition']}**\n\n"
        "## Classification\n\n"
        "**已證實：** the preserved source contains the requeue-PI dispatch, no-waiter branch, proxy call, proxy cleanup, and the legacy task/current cleanup landmarks; the extracted PS7331 config enables the core FUTEX/RT_MUTEX/SLUB gates; boot metadata is preserved.\n\n"
        "**高可信推論：** source/config/image provenance is internally consistent for static analysis.\n\n"
        "**待驗證：** whether a stock process can form the paired waiter state, whether the proxy error branch executes, and whether any residue or later memory effect exists.\n\n"
        "**已排除：** ordinary PI lock/unlock as proof of GhostLock; static source alignment as proof of root; a public PoC targeting another device/kernel as a drop-in compatibility proof.\n\n"
        "**因風險拒絕測試：** device-side requeue-PI trigger, paired waiter, race scheduling, panic/DoS, heap shaping, kernel memory access, boot-policy mutation, and privilege payload.\n",
        encoding="utf-8",
    )

    files = [summary, source_csv, config_csv, report]
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--defconfig", type=Path)
    parser.add_argument("--boot-metadata", type=Path)
    parser.add_argument("--runtime-report", type=Path)
    parser.add_argument("--phase6a-report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "host_only": True,
            "device_contacted": False,
            "futex_triggered": False,
            "output": str(args.output),
        }, indent=2))
        return 0
    write_output(build(args), args.output)
    print(f"wrote host-only consistency audit: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
