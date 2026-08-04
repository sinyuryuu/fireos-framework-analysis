#!/usr/bin/env python3
"""Bound the saved PS7331 GhostLock binary evidence.

This is a host-only evidence normalizer.  It consumes the already-produced,
address-sanitized marker files and the source control-flow result.  It does
not reconstruct an ELF, disassemble a kernel, contact a device, derive
addresses, trigger futexes, or create a payload.

The important distinction is deliberate: the saved binary result proves the
primary pre-fix markers, but it does not retain the raw branch/return
disassembly needed to prove the CVE-2026-53163 follow-up guard at binary level.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


PRIMARY_MARKERS = (
    ("remove_waiter", "current_task_source"),
    ("remove_waiter", "current_task_blocked_on_clear"),
    ("rt_mutex_start_proxy_lock", "proxy_error_calls_remove_waiter"),
)

CONFIG_KEYS = (
    "CONFIG_KALLSYMS",
    "CONFIG_FUTEX",
    "CONFIG_RT_MUTEXES",
    "CONFIG_PREEMPT",
    "CONFIG_PREEMPT_COUNT",
    "CONFIG_SECCOMP",
    "CONFIG_SECCOMP_FILTER",
    "CONFIG_RANDOMIZE_BASE",
    "CONFIG_RANDOMIZE_KSTACK_OFFSET",
    "CONFIG_RANDOMIZE_KSTACK_OFFSET_DEFAULT",
    "CONFIG_VMAP_STACK",
    "CONFIG_ARM64_4K_PAGES",
    "CONFIG_ARM64_VA_BITS",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise SystemExit(f"{label} is not a regular file: {path}")


def config_observation(lines: list[str], key: str) -> tuple[str, str]:
    present = re.compile(rf"^{re.escape(key)}(?:=|$)")
    not_set = re.compile(rf"^#\s+{re.escape(key)}\s+is\s+not\s+set$")
    for line in lines:
        if present.match(line):
            return "present", line
        if not_set.match(line):
            return "explicit_not_set", line
    return "not_observed", ""


def load_patterns(path: Path) -> set[tuple[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return {
            (row.get("symbol", ""), row.get("pattern", ""))
            for row in csv.DictReader(stream)
        }


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patterns", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--source-result", type=Path, required=True)
    parser.add_argument("--parser-metadata", type=Path, required=True)
    parser.add_argument("--kernel-image", type=Path, required=True)
    parser.add_argument("--kernel-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.output in {Path("/"), Path("."), Path("..")}:  # defensive scope check
        parser.error("refusing broad output path")
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "inputs": {
                "patterns": str(args.patterns),
                "summary": str(args.summary),
                "source_result": str(args.source_result),
                "parser_metadata": str(args.parser_metadata),
                "kernel_image": str(args.kernel_image),
                "kernel_config": str(args.kernel_config),
            },
            "output": str(args.output),
            "device_execution": False,
        }, indent=2, sort_keys=True))
        return 0

    for path, label in (
        (args.patterns, "patterns"),
        (args.summary, "summary"),
        (args.source_result, "source result"),
        (args.parser_metadata, "parser metadata"),
        (args.kernel_image, "kernel Image"),
        (args.kernel_config, "kernel config"),
    ):
        require_file(path, label)
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    patterns = load_patterns(args.patterns)
    binary_summary = load_json(args.summary)
    source_result = load_json(args.source_result)
    metadata = args.parser_metadata.read_text(encoding="utf-8", errors="replace")
    config_lines = args.kernel_config.read_text(encoding="utf-8", errors="replace").splitlines()

    marker_rows: list[dict[str, object]] = []
    for symbol, marker in PRIMARY_MARKERS:
        observed = (symbol, marker) in patterns
        marker_rows.append({
            "scope": "saved_address_sanitized_binary_output",
            "symbol": symbol,
            "marker": marker,
            "observed": observed,
            "interpretation": (
                "pre-fix current-task/proxy relationship is present"
                if observed else "expected marker is absent from saved output"
            ),
            "confidence": "Confirmed" if observed else "Disproved",
        })

    primary_markers_complete = all(row["observed"] for row in marker_rows)
    raw_disassembly_omitted = (
        "raw disassembly" in metadata and "omitted" in metadata
    ) or binary_summary.get("address_output") == "intentionally omitted"
    followup_binary_status = (
        "NOT_OBSERVABLE_FROM_SAVED_SANITIZED_OUTPUT"
        if raw_disassembly_omitted else
        "NOT_ESTABLISHED"
    )

    config_rows: list[dict[str, object]] = []
    for key in CONFIG_KEYS:
        status, line = config_observation(config_lines, key)
        config_rows.append({
            "key": key,
            "status": status,
            "source_line": line,
            "interpretation": (
                "configuration is present in extracted IKCONFIG"
                if status == "present" else
                "configuration is explicitly disabled in extracted IKCONFIG"
                if status == "explicit_not_set" else
                "key was not observed; absence is not proof of disabled behavior"
            ),
            "confidence": "Confirmed" if status != "not_observed" else "Unknown",
        })

    result = {
        "scope": "PS7331 only; host-only normalization of preserved evidence",
        "device_execution": False,
        "runtime_exploitability_proven": False,
        "root_or_privilege_gain_proven": False,
        "binary_input": {
            "kernel_image_sha256": sha256(args.kernel_image),
            "patterns_sha256": sha256(args.patterns),
            "summary_sha256": sha256(args.summary),
            "parser_metadata_sha256": sha256(args.parser_metadata),
            "symbols_present": binary_summary.get("symbols_present", []),
        },
        "source_input": {
            "source_result_sha256": sha256(args.source_result),
            "primary_fix_present": source_result.get("primary_fix_present"),
            "primary_fix_shape": source_result.get("primary_fix_shape"),
            "follow_up_guard_review_needed": source_result.get("follow_up_guard_review_needed"),
            "classification": source_result.get("classification"),
        },
        "primary_binary_markers_complete": primary_markers_complete,
        "followup_guard_binary_status": followup_binary_status,
        "followup_guard_binary_reason": (
            "The preserved parser output intentionally omits raw disassembly, branch targets, "
            "and addresses; it records no return-value guard relation."
            if raw_disassembly_omitted else
            "The supplied binary evidence does not contain a guard-level observation."
        ),
        "classification": (
            "PRIMARY_PRE_FIX_MARKERS_CONFIRMED_FOLLOW_UP_BINARY_UNRESOLVED"
            if primary_markers_complete else
            "PRIMARY_PRE_FIX_MARKERS_INCOMPLETE"
        ),
        "config_observations": config_rows,
        "safety_boundary": [
            "No device command was executed.",
            "No futex race or reproducer was compiled or run.",
            "No kernel address, offset, gadget, credential target, or payload was produced.",
            "No image, partition, bootloader, SELinux, or system state was modified.",
        ],
    }

    args.output.mkdir(parents=True)
    (args.output / "analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_csv(
        args.output / "binary-evidence.csv",
        ["scope", "symbol", "marker", "observed", "interpretation", "confidence"],
        marker_rows,
    )
    write_csv(
        args.output / "config-observations.csv",
        ["key", "status", "source_line", "interpretation", "confidence"],
        config_rows,
    )
    (args.output / "result.md").write_text(
        "# PS7331 binary evidence boundary\n\n"
        f"- Classification: **{result['classification']}**\n"
        f"- Primary pre-fix markers complete: **{primary_markers_complete}**\n"
        f"- Follow-up guard binary status: **{followup_binary_status}**\n"
        "- Runtime exploitability proven: **False**\n"
        "- Root/privilege gain proven: **False**\n\n"
        "The follow-up guard is not inferred from missing data.  The preserved "
        "binary result is intentionally address-sanitized and does not retain "
        "the branch/return relation needed for that claim.\n",
        encoding="utf-8",
    )
    (args.output / "README.txt").write_text(
        "Host-only Phase 5BZ artifact.\n"
        "Inputs are preserved source/config/Image evidence; no device I/O.\n"
        "Raw reconstructed ELF and disassembly are intentionally not stored.\n"
        "Do not treat NOT_OBSERVABLE_FROM_SAVED_SANITIZED_OUTPUT as a claim that\n"
        "the follow-up guard is present or absent.\n",
        encoding="utf-8",
    )
    files = sorted(path for path in args.output.iterdir() if path.is_file())
    (args.output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
