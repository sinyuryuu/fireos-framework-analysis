#!/usr/bin/env python3
"""Build a host-only write contract for the official PS7331 OTA.

The script parses the preserved updater-script and metadata and joins them with
the already-saved update-binary analysis.  It never executes update-binary,
recovery, an OTA package, or any device command.  The output is a safety and
provenance report, not an OTA validator or exploit tester.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULTS = {
    "updater_script": ROOT / "firmware/extracted/PS7331/META-INF/com/google/android/updater-script",
    "metadata": ROOT / "firmware/extracted/PS7331/META-INF/com/android/metadata",
    "ota_prop": ROOT / "firmware/extracted/PS7331/ota.prop",
    "update_binary_analysis": ROOT / "artifacts/phase6ah/update-binary-validation-20260805-01/analysis.json",
    "script_commands": ROOT / "artifacts/phase6ah/update-binary-validation-20260805-01/script-commands.csv",
    "call_edges": ROOT / "artifacts/phase6s/ota-call-edges-20260805-01/call-edges.csv",
}

FIELDS = [
    "sequence",
    "command",
    "source_entry",
    "target",
    "impact_class",
    "precondition_or_gate",
    "execution_status",
    "evidence",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_hash_manifest(output: Path, names: list[str]) -> None:
    with (output / "sha256sums.txt").open("w", encoding="utf-8") as stream:
        for name in names:
            stream.write(f"{sha256(output / name)}  {name}\n")


def public_path(path: Path) -> str:
    """Return a repository-relative path for public evidence metadata."""
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def metadata_map(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default in DEFAULTS.items():
        parser.add_argument(f"--{name.replace('_', '-')}", type=Path, default=default)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = {name: getattr(args, name) for name in DEFAULTS}
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "host_only": True,
            "device_contacted": False,
            "updater_executed": False,
            "partition_written": False,
            "output": str(args.output),
        }, indent=2))
        return 0

    missing = [str(path) for path in inputs.values() if not path.is_file()]
    if missing:
        raise SystemExit("missing preserved input(s):\n" + "\n".join(missing))
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)

    script = read(inputs["updater_script"])
    metadata = metadata_map(read(inputs["metadata"]))
    ota_prop = metadata_map(read(inputs["ota_prop"]))
    analysis = json.loads(read(inputs["update_binary_analysis"]))
    command_rows = list(csv.DictReader(inputs["script_commands"].open(newline="", encoding="utf-8")))

    rows: list[dict[str, str]] = []
    sequence = 0
    for number, line in enumerate(script.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("block_image_update("):
            target_match = re.search(r'block_image_update\("([^"]+)"', stripped)
            target = target_match.group(1) if target_match else "NOT_OBSERVED"
            sequence += 1
            rows.append({
                "sequence": str(sequence),
                "command": "block_image_update",
                "source_entry": f"updater-script:{number}",
                "target": target,
                "impact_class": "system_or_vendor_block_image_write",
                "precondition_or_gate": "device/date guards plus recovery/update-binary execution context",
                "execution_status": "NOT_EXECUTED",
                "evidence": "saved updater-script and Phase 6AH static analysis",
            })
        if stripped.startswith("package_extract_file("):
            args_match = re.search(r'package_extract_file\("([^"]+)",\s*"([^"]+)"', stripped)
            if not args_match:
                continue
            source, target = args_match.groups()
            sequence += 1
            impact = "recovery_metadata_write" if target.startswith("/cache/") else "boot_or_firmware_partition_write"
            rows.append({
                "sequence": str(sequence),
                "command": "package_extract_file",
                "source_entry": f"updater-script:{number}:{source}",
                "target": target,
                "impact_class": impact,
                "precondition_or_gate": "device/date guards plus recovery/update-binary execution context",
                "execution_status": "NOT_EXECUTED",
                "evidence": "saved updater-script and Phase 6AH static analysis",
            })

    input_hashes = {public_path(path): sha256(path) for path in inputs.values()}
    target_names = [row["target"] for row in rows]
    summary = {
        "phase": "6AW",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "updater_executed": False,
        "recovery_executed": False,
        "partition_written": False,
        "script_row_count": len(command_rows),
        "write_operation_count": len(rows),
        "targets": target_names,
        "device_gate": "trona",
        "post_build": metadata.get("post-build", "NOT_OBSERVED"),
        "post_incremental": metadata.get("post-build-incremental", "NOT_OBSERVED"),
        "post_security_patch": metadata.get("post-security-patch-level", "NOT_OBSERVED"),
        "ota_version": ota_prop.get("version_name", "NOT_OBSERVED"),
        "binary_classification": analysis.get("classification", "static analysis"),
        "input_sha256": input_hashes,
    }

    csv_path = args.output / "ota-write-contract.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    (args.output / "input-sha256.json").write_text(json.dumps(input_hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    result = [
        "# Phase 6AW — PS7331 official OTA write contract",
        "",
        "This is a host-only provenance and safety analysis. The updater, recovery, OTA package, and device were not executed or modified.",
        "",
        "## Gates",
        "",
        f"- `pre-device`: `{metadata.get('pre-device', 'NOT_OBSERVED')}`",
        f"- `post-build`: `{metadata.get('post-build', 'NOT_OBSERVED')}`",
        f"- `post-build-incremental`: `{metadata.get('post-build-incremental', 'NOT_OBSERVED')}`",
        f"- `post-security-patch-level`: `{metadata.get('post-security-patch-level', 'NOT_OBSERVED')}`",
        f"- OTA description: `{ota_prop.get('version_name', 'NOT_OBSERVED')}`",
        "",
        "## Static result",
        "",
        "- **已證實（靜態）：** the script contains block-image update operations for system and vendor and direct extraction targets for boot-chain/firmware partitions.",
        "- **已證實（靜態）：** the saved update-binary analysis contains registration, expression evaluation, block-image handlers, verification helpers, and raw I/O helper edges.",
        "- **高可信推論：** this package is a full/high-impact update transaction, not a reversible ADB launcher or settings control surface.",
        "- **無法由本階段確認：** complete recovery-side signature/canonicalization behavior and any hypothetical future updater defect.",
        "- **因風險拒絕測試：** OTA install/sideload, recovery execution, malformed or symlink payloads, downgrade attempts, and all partition writes.",
        "",
        "## Target list",
        "",
    ]
    result.extend(f"- `{row['target']}` — `{row['impact_class']}`" for row in rows)
    result.extend([
        "",
        "## Consequence",
        "",
        "The official package does provide signed boot and source provenance for analysis, but that does not make it a safe runtime experiment. It remains a high-impact lifecycle boundary; no shell/ADB launcher workaround or privilege transition is established by this static contract.",
        "",
        "## Reproduction",
        "",
        "```sh",
        "python3 tools/scripts/build_phase6aw_ota_write_contract.py --dry-run --output /tmp/phase6aw-dry-run",
        "python3 tools/scripts/build_phase6aw_ota_write_contract.py --output artifacts/phase6aw/ota-write-contract-YYYYMMDD-01",
        "shasum -a 256 -c artifacts/phase6aw/ota-write-contract-YYYYMMDD-01/sha256sums.txt",
        "```",
    ])
    result_path = args.output / "result.md"
    result_path.write_text("\n".join(result) + "\n", encoding="utf-8")
    write_hash_manifest(args.output, ["ota-write-contract.csv", "input-sha256.json", "summary.json", "result.md"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
