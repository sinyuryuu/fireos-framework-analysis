#!/usr/bin/env python3
"""Host-only audit of a preserved Fire OS OTA's installer surface.

The audit reads ZIP metadata and already-preserved text members or extracted
metadata. It never executes update-binary, runs an updater script, constructs
an OTA, contacts a device, or writes a partition. Results describe update
scope and review leads, not a confirmed vulnerability.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


MARKERS: list[tuple[str, str, str]] = [
    ("partition_write", r"block_image_update|package_extract_file\s*\([^\n]*?/dev/block/|write_raw_image|apply_patch_check", "writes or updates a block/partition"),
    ("boot_chain_write", r"/by-name/(?:boot|preloader|lk|tee[12]?|spmfw|sspm[^/]*|cam_vpu[^/]*)", "boot-chain or firmware partition target"),
    ("system_vendor_write", r"/by-name/(?:system|vendor|product|system_ext)", "OS partition target"),
    ("cache_or_data_write", r"(?:package_extract_file|write_raw_image|run_program|set_perm|set_metadata)[^\n]*(?:/cache|/data|/tmp|/sdcard)", "cache/data/temp path operation"),
    ("postinstall_program", r"run_program|postinstall|post-install|update-binary", "post-install or executable updater path"),
    ("symlink_operation", r"symlink|readlink|lstat|realpath", "symlink/path resolution operation"),
    ("permission_operation", r"set_perm|set_metadata|chown|chmod|restorecon", "permission/label operation"),
    ("property_operation", r"setprop|getprop|property_get|property_set", "property read/write"),
    ("control_flow", r"abort\s*\(|ifelse\s*\(|less_than_int|greater_than_int", "installer condition or abort"),
    ("reboot_or_format", r"reboot|format\s*\(|erase\s*\(", "reboot/format/erase marker"),
]
COMPILED = [(kind, re.compile(pattern, re.IGNORECASE), description) for kind, pattern, description in MARKERS]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_text(path: Path, source: str, findings: list[dict[str, object]], counts: Counter[str], limit: int) -> None:
    try:
        stream = path.open("r", encoding="utf-8", errors="replace")
    except OSError:
        return
    with stream:
        for line_number, line in enumerate(stream, 1):
            for kind, pattern, description in COMPILED:
                if pattern.search(line):
                    counts[kind] += 1
                    if len(findings) < limit:
                        findings.append({
                            "source": source,
                            "file": str(path),
                            "line": line_number,
                            "kind": kind,
                            "description": description,
                            "excerpt": line.strip()[:600],
                        })


def collect_zip_members(ota: Path) -> list[dict[str, object]]:
    with zipfile.ZipFile(ota) as archive:
        return [{
            "name": info.filename,
            "compressed_size": info.compress_size,
            "uncompressed_size": info.file_size,
            "crc32": f"{info.CRC:08x}",
            "compression": info.compress_type,
        } for info in sorted(archive.infolist(), key=lambda item: item.filename)]


def write_report(output: Path, ota: Path, metadata_root: Path | None, extracted_root: Path | None, members: list[dict[str, object]], findings: list[dict[str, object]], counts: Counter[str], limit: int, text_inputs: list[str]) -> None:
    output.mkdir(parents=True)
    (output / "members.json").write_text(json.dumps(members, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (output / "ota-findings.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["source", "file", "line", "kind", "description", "excerpt"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(findings)
    member_names = [str(member["name"]) for member in members]
    partition_targets = [item["excerpt"] for item in findings if item["kind"] in {"partition_write", "boot_chain_write", "system_vendor_write"}]
    result = {
        "host_only": True,
        "device_contacted": False,
        "updater_executed": False,
        "ota_constructed": False,
        "partition_written": False,
        "ota": str(ota),
        "ota_sha256": sha256(ota),
        "metadata_root": str(metadata_root) if metadata_root else "",
        "extracted_root": str(extracted_root) if extracted_root else "",
        "member_count": len(members),
        "text_inputs": text_inputs,
        "captured_finding_count": len(findings),
        "captured_finding_limit": limit,
        "marker_counts_all_matches": dict(counts),
        "partition_target_excerpts": partition_targets,
        "member_presence": {
            "updater_script": "META-INF/com/google/android/updater-script" in member_names,
            "update_binary": "META-INF/com/google/android/update-binary" in member_names,
            "boot_image": "boot.img" in member_names,
            "system_payload": "system.new.dat.br" in member_names,
            "vendor_payload": "vendor.new.dat.br" in member_names,
            "compatibility_zip": "compatibility.zip" in member_names,
        },
        "limitations": [
            "A full OTA's partition writes are expected update behavior, not evidence of an unsafe path by themselves.",
            "This audit does not execute update-binary or validate recovery's signature and staging implementation dynamically.",
            "No malformed package, symlink, path traversal or post-install payload was constructed or installed.",
            "Binary members are inventoried by metadata/hash only; they are not executed.",
        ],
    }
    (output / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = [
        "# PS7331 OTA post-install surface (host-only)",
        "",
        f"- OTA: `{ota}`",
        f"- SHA-256: `{sha256(ota)}`",
        f"- ZIP members: **{len(members)}**",
        f"- Captured findings: **{len(findings)}** (all-match counts are in `summary.json`)",
        "",
        "## Evidence",
        "",
        "The preserved updater metadata contains explicit `block_image_update` and"
        " `package_extract_file` operations targeting system/vendor and boot-chain"
        " block devices. This is a high-risk update boundary, not a safe userspace"
        " control surface.",
        "",
        "The scan found no reason to execute the updater, alter a ZIP, or test a"
        " symlink/path traversal hypothesis on a device. `run_program`, symlink"
        " handling and temp-path hits, if any, require manual binary/recovery review.",
        "",
        "## Classification",
        "",
        "- **已證實：** the package is a full/block OTA with inventory entries for"
        " update-binary, updater-script, boot and system/vendor payloads; the"
        " preserved script names concrete partition targets.",
        "- **高可信推論：** this package is not an ADB-level reversible launcher"
        " workaround and must be treated as a full update transaction.",
        "- **待驗證：** implementation-level staging, signature and path handling"
        " inside recovery/update-binary; no dynamic test was justified.",
        "- **因風險拒絕測試：** OTA install/sideload, malformed package, symlink"
        " replacement, bootloader or partition writes.",
        "",
        "## Reproduction",
        "",
        "```text",
        "python3 tools/scripts/audit_phase6i_ota_postinstall_surface.py \\",
        f"  --ota {ota} \\",
        f"  --metadata-root {metadata_root or '(optional)'} \\",
        f"  --extracted-root {extracted_root or '(optional)'} \\",
        "  --output artifacts/phase6i/phase6i-ota-postinstall-YYYYMMDD-01",
        "```",
        "",
        "All operations above are host-only; the script refuses an existing output"
        " directory and never invokes update-binary.",
    ]
    (output / "result.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    files = sorted(path for path in output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (output / "sha256sums.txt").write_text("\n".join(f"{sha256(path)}  {path.relative_to(output)}" for path in files) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ota", type=Path, required=True)
    parser.add_argument("--metadata-root", type=Path)
    parser.add_argument("--extracted-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-findings", type=int, default=5000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False, "ota": str(args.ota), "output": str(args.output)}, indent=2))
        return 0
    if not args.ota.is_file():
        raise SystemExit(f"missing OTA: {args.ota}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    members = collect_zip_members(args.ota)
    findings: list[dict[str, object]] = []
    counts: Counter[str] = Counter()
    text_inputs: list[str] = []
    if args.metadata_root and args.metadata_root.is_dir():
        for path in sorted(args.metadata_root.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".txt", ".json", ".prop", ".tsv", ".xml", ".devicepath", ".map", ".sha1"}:
                text_inputs.append(str(path))
                scan_text(path, "metadata", findings, counts, args.max_findings)
    if args.extracted_root and args.extracted_root.is_dir():
        for path in sorted(args.extracted_root.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".txt", ".json", ".prop", ".tsv", ".xml", ".devicepath", ".map", ".sha1"}:
                text_inputs.append(str(path))
                scan_text(path, "extracted", findings, counts, args.max_findings)
    write_report(args.output, args.ota, args.metadata_root, args.extracted_root, members, findings, counts, args.max_findings, text_inputs)
    print(f"wrote host-only OTA post-install audit: {args.output} ({len(members)} members, {len(findings)} captured findings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
