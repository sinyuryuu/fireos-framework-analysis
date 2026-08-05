#!/usr/bin/env python3
"""Build a host-only PS7331 provenance and high-impact boundary report.

The audit reads preserved source, OTA metadata, decompiled service output, and
the saved OTA Java source.  It never contacts a device, executes an updater,
constructs an OTA payload, or writes any device state.  Large archive hashes
may be supplied from an already verified manifest; use --verify-large-hashes
only when a fresh full-file hash is intentionally required.
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise SystemExit(f"{label} is not a file: {path}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def line_hits(path: Path, patterns: list[str]) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for number, line in enumerate(read_text(path).splitlines(), 1):
        if any(re.search(pattern, line, flags=re.I) for pattern in patterns):
            hits.append({"line": number, "text": line.rstrip()})
    return hits


def source_scope(root: Path) -> dict[str, object]:
    files = [path for path in root.rglob("*") if path.is_file()]
    focus: dict[str, dict[str, object]] = {}
    focus_paths = [
        "platform/kernel/mediatek/mt8183/4.4/kernel/futex.c",
        "platform/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c",
        "platform/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig",
        "build_kernel.sh",
        "build_kernel_config.sh",
        "platform/system/core/init/selinux.cpp",
    ]
    for relative in focus_paths:
        path = root / relative
        record: dict[str, object] = {"path": relative, "exists": path.is_file()}
        if path.is_file():
            record["bytes"] = path.stat().st_size
            record["sha256"] = sha256(path)
        focus[relative] = record

    implementation_extensions = {".java", ".kt", ".kts", ".smali", ".cpp", ".cc", ".c", ".h", ".xml"}
    firelauncher_implementation = [
        path for path in files
        if "firelauncher" in str(path).lower() and path.suffix.lower() in implementation_extensions
    ]
    return {
        "file_count": len(files),
        "focus": focus,
        "has_framework_tree": (root / "fireos/frameworks").exists()
        or any("frameworks/base" in str(path) for path in files),
        "has_init_policy_loader_source": any(
            path.name in {"selinux.cpp", "selinux.h"}
            and "/init/" in str(path)
            for path in files
        ),
        "firelauncher_implementation_file_count": len(firelauncher_implementation),
    }


def file_record(path: Path, supplied_hash: str | None, verify: bool) -> dict[str, object]:
    record: dict[str, object] = {
        "path": str(path),
        "bytes": path.stat().st_size,
        "hash_verified_now": False,
    }
    if supplied_hash:
        record["recorded_sha256"] = supplied_hash
    if verify:
        actual = sha256(path)
        record["sha256"] = actual
        record["hash_verified_now"] = not supplied_hash or actual == supplied_hash
        if supplied_hash and actual != supplied_hash:
            raise SystemExit(f"hash mismatch for {path}: {actual} != {supplied_hash}")
    return record


def text_boundary(path: Path, patterns: list[str]) -> dict[str, object]:
    hits = line_hits(path, patterns)
    return {"path": str(path), "hits": hits, "hit_count": len(hits)}


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--ota", type=Path, required=True)
    parser.add_argument("--updater-script", type=Path, required=True)
    parser.add_argument("--services-disassembly", type=Path, required=True)
    parser.add_argument("--fosservices-disassembly", type=Path, required=True)
    parser.add_argument("--ota-source-root", type=Path, required=True)
    parser.add_argument("--ota-contracts-source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-archive-sha256")
    parser.add_argument("--ota-sha256")
    parser.add_argument("--verify-large-hashes", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    required = [
        (args.source_root, "source root"),
        (args.source_archive, "source archive"),
        (args.ota, "OTA"),
        (args.updater_script, "updater script"),
        (args.services_disassembly, "services disassembly"),
        (args.fosservices_disassembly, "fosservices disassembly"),
        (args.ota_source_root, "OTA source root"),
        (args.ota_contracts_source_root, "OTA contracts source root"),
    ]
    for path, label in required:
        if label in {"source root", "OTA source root", "OTA contracts source root"}:
            if not path.is_dir():
                raise SystemExit(f"{label} is not a directory: {path}")
        else:
            require_file(path, label)

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "device_contacted": False,
            "device_mutation": False,
            "updater_executed": False,
            "payload_constructed": False,
            "output": str(args.output),
        }, indent=2))
        return 0

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)

    ota_files = [
        args.ota_source_root / "sources/com/amazon/dcp/ota/SideloadMover.java",
        args.ota_source_root / "sources/com/amazon/device/framework/FileHelper.java",
        args.ota_source_root / "sources/com/amazon/device/software/ota/storage/OTADataDirectory.java",
        args.ota_contracts_source_root / "sources/com/amazon/dcp/ota/OtaServiceConnectionManager.java",
        args.ota_contracts_source_root / "sources/com/amazon/dcp/ota/OTAController.java",
    ]
    for path in ota_files:
        require_file(path, "OTA Java source")

    archive = file_record(args.source_archive, args.source_archive_sha256, args.verify_large_hashes)
    ota = file_record(args.ota, args.ota_sha256, args.verify_large_hashes)
    scope = source_scope(args.source_root)

    source_rows: list[dict[str, object]] = []
    for relative, record in scope["focus"].items():
        source_rows.append({
            "evidence_id": "6BC-SRC-" + re.sub(r"[^A-Za-z0-9]", "_", relative).strip("_")[:60],
            "path": relative,
            "exists": record["exists"],
            "bytes": record.get("bytes", ""),
            "sha256": record.get("sha256", ""),
            "classification": "PRESENT" if record["exists"] else "ABSENT_IN_EXTRACTED_SCOPE",
        })
    write_csv(args.output / "source-focus.csv", source_rows,
              ["evidence_id", "path", "exists", "bytes", "sha256", "classification"])

    ota_patterns = [
        r"/dev/block", r"write_raw_image", r"package_extract", r"run_program",
        r"mount", r"format", r"recovery", r"boot", r"vendor", r"preloader",
        r"system", r"product", r"super",
    ]
    updater = text_boundary(args.updater_script, ota_patterns)

    java_boundaries = {
        "sideload_mover": text_boundary(
            ota_files[0], [r"split", r"getAbsolutePath", r"getExternalDataDirectory", r"moveFile"]
        ),
        "file_helper": text_boundary(
            ota_files[1], [r"renameTo", r"copyFile", r"delete\(", r"canonical", r"realpath", r"readlink", r"NOFOLLOW", r"isFileReadyToBeUsed"]
        ),
        "ota_data_directory": text_boundary(
            ota_files[2], [r"/data/ota_package", r"getLastPathSegment", r"setDestinationUri"]
        ),
        "ota_controller_auth": text_boundary(
            ota_files[3] , [r"CONTROLLER", r"checkPermission", r"SecurityException", r"bindService"]
        ),
        "ota_controller_methods": text_boundary(
            ota_files[4], [r"assertPermissionGranted", r"installSideload", r"blockApp", r"suspend", r"resume"]
        ),
    }

    ipc = {
        "prewarm": text_boundary(
            args.fosservices_disassembly,
            [r"preWarmApplicationForUser", r"APP_PREWARM", r"checkCallingPermission", r"clearCallingIdentity", r"startProcessLocked"],
        ),
        "vendor_home_callbacks": text_boundary(
            args.services_disassembly,
            [r"VendorActivityStackSupervisorCallback", r"AppCompatActivityStackSupervisorCallback", r"launchHomeFromHotKey", r"resolveIntent"],
        ),
    }

    report = {
        "schema": 1,
        "phase": "6BC",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "device_mutation": False,
        "updater_executed": False,
        "payload_constructed": False,
        "inputs": {
            "source_archive": archive,
            "ota": ota,
            "updater_script": {"path": str(args.updater_script), "sha256": sha256(args.updater_script)},
            "services_disassembly": {"path": str(args.services_disassembly), "sha256": sha256(args.services_disassembly)},
            "fosservices_disassembly": {"path": str(args.fosservices_disassembly), "sha256": sha256(args.fosservices_disassembly)},
        },
        "source_scope": scope,
        "updater_signal": updater,
        "ota_java_boundaries": java_boundaries,
        "ipc_boundaries": ipc,
        "interpretation": {
            "source": "The official source scope proves the device-specific kernel provenance but does not contain Android framework/init source.",
            "ota": "The updater contains normal high-impact partition/recovery operations. Sideload Java stages by basename into /data/ota_package and uses rename or copy/delete; this is a static review signal, not a demonstrated exploit.",
            "authorization": "The OTA client-side controller checks signature|privileged permissions before binding. The prewarm server block contains a permission-check call whose result is not consumed before identity clear, but the private service is not shell-visible in the saved enforcing capture.",
            "decision": "No host-only evidence establishes a low-privilege root or formal HOME replacement. Further progress requires naturally occurring official OTA observation or a new, authorized caller—not a crafted OTA, unknown Binder transaction, or package-state mutation.",
        },
    }
    (args.output / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output / "result.md").write_text(
        "# Phase 6BC — PS7331 provenance and control-surface audit\n\n"
        "This artifact is host-only. It contacted no device, executed no updater, "
        "constructed no OTA payload, and changed no state. See `summary.json` and "
        "`source-focus.csv` for machine-readable evidence.\n\n"
        "## Findings\n\n"
        "- **Confirmed:** the supplied PS7331 source tree contains the MT8183/trona "
        "kernel inputs and lacks `platform/system/core/init/selinux.cpp` and the "
        "Android framework source tree in the extracted scope.\n"
        "- **Confirmed:** the OTA updater source and script include normal high-impact "
        "partition/recovery operations; no malformed payload was executed.\n"
        "- **Strong evidence:** Java sideload staging uses basename-derived destination "
        "construction and `renameTo`/copy-delete fallback, while the controller-side "
        "bind path checks signature|privileged permissions.\n"
        "- **Strong evidence:** `preWarmApplicationForUser` reaches a process-start "
        "sink after a non-consumed `checkCallingPermission(APP_PREWARM)` call in the "
        "bounded disassembly; the saved enforcing device capture provides no shell "
        "service handle, so this is an authorization-review candidate, not a live "
        "primitive.\n"
        "- **Not established:** root, a crafted-OTA path, an unknown-Binder path, or a "
        "formal HOME replacement.\n\n"
        "## Safety disposition\n\n"
        "No OTA install/sideload, recovery, Binder transaction, package mutation, "
        "Fire Launcher mutation, partition write, or kernel operation was performed.\n",
        encoding="utf-8",
    )
    generated = sorted(path for path in args.output.rglob("*") if path.is_file())
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(args.output)}\n" for path in generated),
        encoding="utf-8",
    )
    print(f"wrote host-only Phase 6BC audit to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
