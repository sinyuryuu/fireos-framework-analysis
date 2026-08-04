#!/usr/bin/env python3
"""Classify PS7331 /init policy-loader scenarios from host-only evidence.

This is a conservative evidence joiner. It does not execute /init, alter boot
properties, select a policy, mount a partition, or contact a device.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_strings(path: Path) -> str:
    completed = subprocess.run(
        ["strings", "-a", str(path)], check=True, capture_output=True, text=True
    )
    return completed.stdout


def build(audit_json: Path, init_binary: Path, device_capture: Path | None) -> dict[str, object]:
    audit = json.loads(audit_json.read_text(encoding="utf-8"))
    strings = read_strings(init_binary)
    string_markers = {
        marker: len(re.findall(re.escape(marker), strings))
        for marker in (
            "rootable_plat_sepolicy.cil",
            "rootable_vendor_sepolicy.cil",
            "androidboot.selinux",
            "permissive",
            "FsManagerAvbHandle",
            "avb_slot_verify",
            "SIGNATURE_MISMATCH",
            "efuse",
            "eFuse",
            "persist.",
            "/data/",
        )
    }
    landmarks = {entry["classification"]: entry for entry in audit.get("static_landmarks", [])}
    scenarios = [
        {
            "id": "S1",
            "name": "userspace-controlled selector",
            "verdict": "待驗證",
            "confidence": "Hypothesis",
            "evidence": "No source-level selector is available; the binary contains no direct proof that a shell/untrusted-writable persist or data marker controls the rootable branch.",
            "next_minimum": "Recover the exact stripped caller/branch semantics from a matching symbolized build or a legally available debug artifact; do not mutate properties.",
        },
        {
            "id": "S2",
            "name": "boot/kernel cmdline-dependent selector",
            "verdict": "高可信推論",
            "confidence": "Strong evidence",
            "evidence": "The image contains an androidboot.selinux/permissive parser candidate and separate standard/rootable path-builder call sites; the stock capture is locked/enforcing and shell cannot read cmdline.",
            "next_minimum": "Map the property-parser return/field to the policy helper in a host-only disassembly; no boot-property injection.",
        },
        {
            "id": "S3",
            "name": "AVB/signature/fuse-bound selector",
            "verdict": "待驗證",
            "confidence": "Hypothesis",
            "evidence": "AVB/BoringSSL verification markers are compiled into /init, but the current stripped CFG evidence does not connect those calls to rootable policy selection or an eFuse check.",
            "next_minimum": "Map AVB call sites and data/control dependencies to the policy-loader window on the host; do not bypass verification.",
        },
        {
            "id": "S4",
            "name": "dead-code/compiler-residue",
            "verdict": "已排除（純字串殘留版本）／待驗證（執行可達性）",
            "confidence": "Strong evidence",
            "evidence": "Rootable path literals have ADRP/ADD code references and a call into the common helper with w5=1, so they are not string-only residue; exact runtime branch reachability remains unresolved.",
            "next_minimum": "Complete host CFG recovery around 0x41ad00–0x41bf30 and validate callers; do not execute /init.",
        },
    ]
    return {
        "schema": "phase6d-policy-loader-scenarios-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "audit_json": str(audit_json),
            "audit_json_sha256": sha256(audit_json),
            "init_binary": str(init_binary),
            "init_binary_sha256": sha256(init_binary),
            "device_capture": str(device_capture) if device_capture else None,
        },
        "string_markers": string_markers,
        "static_landmarks": landmarks,
        "scenarios": scenarios,
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "device_mutated": False,
            "init_executed": False,
            "boot_property_changed": False,
            "policy_loaded": False,
            "verification_bypassed": False,
            "root_payload": False,
        },
    }


def write(result: dict[str, object], output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    summary = output / "policy-scenarios.json"
    table = output / "policy-scenarios.csv"
    report = output / "result.md"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["id", "name", "verdict", "confidence", "evidence", "next_minimum"]
    with table.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["scenarios"])
    report.write_text(
        "# PS7331 `/init` policy-loader scenario classification\n\n"
        "Host-only evidence join. The binary was not executed and no boot/property,\n"
        "SELinux policy, partition, kernel-memory, or privilege operation was attempted.\n\n"
        "## Conservative classification\n\n"
        "- **S1 userspace-controlled selector — 待驗證 / Hypothesis.** No evidence\n"
        "  currently connects a shell/untrusted-writable setting to the rootable branch.\n"
        "- **S2 boot/cmdline selector — 高可信推論 / Strong evidence.** The image has\n"
        "  an `androidboot.selinux`/`permissive` parser candidate and separate standard\n"
        "  and rootable path-builder call sites; the exact selector remains unresolved.\n"
        "- **S3 AVB/signature/fuse binding — 待驗證 / Hypothesis.** AVB and crypto\n"
        "  markers are present, but no current CFG edge proves they guard the rootable\n"
        "  path or read an eFuse.\n"
        "- **S4 dead code — string-only residue is 已排除; runtime reachability is\n"
        "  待驗證.** ADRP/ADD references and a common-helper call make a pure strings-only\n"
        "  explanation insufficient.\n\n"
        "## Safety boundary\n\n"
        "Boot-property injection, alternate-policy selection, verification bypass,\n"
        "remount, bootloader/fastboot, image writes, kernel races, panic tests and\n"
        "root payloads remain rejected.\n",
        encoding="utf-8",
    )
    files = [summary, table, report]
    (output / "sha256sums.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-json", type=Path, required=True)
    parser.add_argument("--init-binary", type=Path, required=True)
    parser.add_argument("--device-capture", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False}, indent=2))
        return 0
    for path in (args.audit_json, args.init_binary):
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")
    write(build(args.audit_json, args.init_binary, args.device_capture), args.output)
    print(f"wrote policy scenario classification: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
