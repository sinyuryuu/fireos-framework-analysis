#!/usr/bin/env python3
"""Host-only inventory of preserved PS7331 installed-artifact policy surfaces.

This audit reads already-preserved firmware/APK/JAR/VDEX/ODEX artifacts.  It
does not contact ADB, mount an image, execute an ELF, invoke a syscall, unpack
to a device, or generate exploit data.  Large raw images are metadata-only by
default because their contents are not currently available as a read-only
filesystem tree in this workspace.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path


MARKERS = {
    "FUTEX_CMP_REQUEUE_PI": re.compile(rb"\bFUTEX_CMP_REQUEUE_PI\b"),
    "FUTEX_WAIT_REQUEUE_PI": re.compile(rb"\bFUTEX_WAIT_REQUEUE_PI\b"),
    "FUTEX_LOCK_PI": re.compile(rb"\bFUTEX_LOCK_PI(?:2)?(?:_PRIVATE)?\b"),
    "FUTEX_UNLOCK_PI": re.compile(rb"\bFUTEX_UNLOCK_PI(?:_PRIVATE)?\b"),
    "SECCOMP": re.compile(rb"\b(?:SECCOMP|seccomp)\b"),
    "SECCOMP_FILTER": re.compile(rb"\b(?:SECCOMP_FILTER|seccomp_filter)\b"),
    "ZYGOTE": re.compile(rb"\bzygote\b", re.IGNORECASE),
    "APP_PROCESS": re.compile(rb"\bapp_process(?:32|64)?\b"),
    "NO_NEW_PRIVS": re.compile(rb"\b(?:no_new_privs|PR_SET_NO_NEW_PRIVS)\b"),
    "PRCTL": re.compile(rb"\bprctl\b"),
}

PATH_MARKERS = (
    "seccomp", "zygote", "sandbox", "policy", "allowlist", "denylist",
    "sepolicy", "selinux", "app_process", "sysconfig", "permissions",
)

TEXT_SUFFIXES = {
    ".c", ".h", ".cc", ".cpp", ".S", ".s", ".mk", ".bp", ".xml",
    ".te", ".cil", ".policy", ".txt", ".json", ".rc", ".prop", ".conf",
}

DEFAULT_MAX_SCAN = 256 * 1024 * 1024
ZIP_MEMBER_LIMIT = 16 * 1024 * 1024
ZIP_TOTAL_LIMIT = 64 * 1024 * 1024


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_zip_candidate(path: Path) -> bool:
    return path.suffix.lower() in {".apk", ".jar", ".zip", ".vdex"}


def path_flags(path: Path) -> list[str]:
    lowered = str(path).lower()
    return [marker for marker in PATH_MARKERS if marker in lowered]


def marker_counts(blob: bytes) -> dict[str, int]:
    return {name: len(pattern.findall(blob)) for name, pattern in MARKERS.items()}


def scan_blob(blob: bytes, source: str, hits: list[dict[str, object]], limit: int = 100) -> dict[str, int]:
    counts = marker_counts(blob)
    for name, count in counts.items():
        if count and len(hits) < limit:
            hits.append({
                "source": source,
                "marker": name,
                "count": count,
                "scope": "binary-or-archive-member",
            })
    return counts


def add_counts(total: dict[str, int], current: dict[str, int]) -> None:
    for key, value in current.items():
        total[key] += value


def scan_zip(path: Path, hits: list[dict[str, object]], total: dict[str, int]) -> list[str]:
    members: list[str] = []
    consumed = 0
    try:
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                members.append(info.filename)
                member_path_flags = [m for m in PATH_MARKERS if m in info.filename.lower()]
                if member_path_flags and len(hits) < 100:
                    hits.append({
                        "source": f"{path}!{info.filename}",
                        "marker": "PATH_POLICY_NAME",
                        "count": len(member_path_flags),
                        "scope": "archive-member-name",
                        "flags": ",".join(member_path_flags),
                    })
                if info.is_dir() or info.file_size > ZIP_MEMBER_LIMIT:
                    continue
                if consumed + info.file_size > ZIP_TOTAL_LIMIT:
                    break
                with archive.open(info) as member:
                    blob = member.read(ZIP_MEMBER_LIMIT + 1)
                if len(blob) > ZIP_MEMBER_LIMIT:
                    continue
                add_counts(total, scan_blob(blob, f"{path}!{info.filename}", hits))
                consumed += len(blob)
    except (OSError, zipfile.BadZipFile, RuntimeError):
        return members
    return members


def audit_file(path: Path, max_scan: int, hits: list[dict[str, object]], total: dict[str, int]) -> dict[str, object]:
    stat = path.stat()
    row: dict[str, object] = {
        "path": str(path),
        "size": stat.st_size,
        "sha256": sha256(path),
        "path_markers": ",".join(path_flags(path)),
        "scan_status": "metadata-only",
        "archive_members": 0,
        "error": "",
    }
    if stat.st_size > max_scan:
        row["scan_status"] = "skipped-large-file"
        row["error"] = f"size>{max_scan}"
        return row
    try:
        if is_zip_candidate(path):
            before = len(hits)
            members = scan_zip(path, hits, total)
            row["archive_members"] = len(members)
            row["scan_status"] = "archive-member-scan"
            if len(hits) == before and not members:
                row["scan_status"] = "binary-scan"
        else:
            with path.open("rb") as stream:
                blob = stream.read(max_scan + 1)
            if len(blob) > max_scan:
                row["scan_status"] = "skipped-large-file"
                row["error"] = f"read>{max_scan}"
                return row
            add_counts(total, scan_blob(blob, str(path), hits))
            row["scan_status"] = "binary-scan"
    except OSError as exc:
        row["scan_status"] = "read-error"
        row["error"] = str(exc)
    return row


def collect_files(roots: list[Path]) -> list[Path]:
    found: set[Path] = set()
    for root in roots:
        if root.is_file():
            found.add(root)
        elif root.is_dir():
            found.update(path for path in root.rglob("*") if path.is_file())
    return sorted(found)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-scan-bytes", type=int, default=DEFAULT_MAX_SCAN)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "device_contacted": False,
            "elf_executed": False,
            "image_mounted": False,
            "futex_triggered": False,
            "input_roots": [str(root) for root in args.input_root],
            "output": str(args.output),
        }, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    for root in args.input_root:
        if not root.exists():
            raise SystemExit(f"missing input: {root}")
    if args.max_scan_bytes <= 0:
        raise SystemExit("--max-scan-bytes must be positive")

    files = collect_files(args.input_root)
    hits: list[dict[str, object]] = []
    totals = {name: 0 for name in MARKERS}
    rows = [audit_file(path, args.max_scan_bytes, hits, totals) for path in files]
    policy_paths = [row["path"] for row in rows if row["path_markers"]]
    skipped = [row["path"] for row in rows if row["scan_status"] == "skipped-large-file"]
    archive_members = sum(int(row["archive_members"]) for row in rows)
    result = {
        "schema": "phase6c-installed-artifact-policy-audit-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": [{"root": str(root), "exists": root.exists()} for root in args.input_root],
        "inventory": {
            "files_seen": len(rows),
            "policy_named_paths": len(policy_paths),
            "archive_members_seen": archive_members,
            "large_files_skipped": len(skipped),
            "max_scan_bytes": args.max_scan_bytes,
        },
        "marker_counts": totals,
        "path_policy_candidates": policy_paths,
        "large_files_skipped": skipped,
        "safety": {
            "host_only": True,
            "device_contacted": False,
            "image_mounted": False,
            "elf_executed": False,
            "futex_triggered": False,
            "kernel_memory_accessed": False,
            "payload_or_address_generated": False,
        },
        "interpretation": [
            "A marker or path hit identifies an artifact surface, not an executed runtime policy.",
            "A zero marker count is bounded to the supplied files and scan method; stripped, encoded, indirect, or unpulled policy remains unknown.",
            "Raw system/vendor/boot images are not content-scanned unless explicitly supplied; an explicitly supplied file above the scan limit is metadata-only because no read-only filesystem extractor is used by this audit.",
            "The audit does not establish whether Android seccomp filters permit or deny any futex opcode.",
        ],
    }
    args.output.mkdir(parents=True)
    summary = args.output / "installed-artifact-policy.json"
    inventory = args.output / "artifact-inventory.csv"
    marker_file = args.output / "marker-hits.csv"
    report = args.output / "result.md"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with inventory.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "path", "size", "sha256", "path_markers", "scan_status", "archive_members", "error",
        ], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with marker_file.open("w", encoding="utf-8", newline="") as stream:
        fieldnames = ["source", "marker", "count", "scope", "flags"]
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(hits)
    report.write_text(
        "# Phase 6C installed-artifact policy audit\n\n"
        "Host-only audit of preserved PS7331 artifacts. No ADB, image mount, ELF execution, futex call, kernel-memory access, or payload.\n\n"
        f"- Files seen: {len(rows)}\n"
        f"- Policy-named paths: {len(policy_paths)}\n"
        f"- Archive members inspected: {archive_members}\n"
        f"- Large files skipped: {len(skipped)}\n"
        f"- Named `FUTEX_CMP_REQUEUE_PI` hits: {totals['FUTEX_CMP_REQUEUE_PI']}\n"
        f"- Named `FUTEX_WAIT_REQUEUE_PI` hits: {totals['FUTEX_WAIT_REQUEUE_PI']}\n"
        f"- `SECCOMP` hits: {totals['SECCOMP']}\n\n"
        "A zero or nonzero result is bounded evidence only; it is not an execution or policy-enforcement proof.\n",
        encoding="utf-8",
    )
    outputs = (summary, inventory, marker_file, report)
    (args.output / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in outputs),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
