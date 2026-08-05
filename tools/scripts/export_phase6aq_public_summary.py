#!/usr/bin/env python3
"""Export a small, reproducible public summary from Phase 6AQ evidence.

The full ADB captures remain local because they include broad device state and
logcat.  This exporter keeps only the build/HOME state, relevant service
lookups, relevant diagnostic service inventory and a bounded AVC subset.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


KEY_SERVICES = {
    "amazonpackagemanager", "amazonactivitymanager", "amazonwindowmanager",
    "amazondevicepolicymanager", "amazonprofileservice", "amazonusermanagerservice",
    "amazon_input", "amazon_keyevent", "fosdebug", "otadexopt",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_once(path: Path, data: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing output: {path}")
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def redact_public_properties(text: str) -> str:
    """Remove direct device identifiers before publishing a getprop excerpt."""
    redacted = []
    for line in text.splitlines():
        if re.match(r"^\[ro(?:\.boot)?\.serialno\]:", line):
            line = re.sub(r"\[\[[^]]*\]\]$", "[REDACTED]", line)
            line = re.sub(r"(\]:\s*)\[[^]]*\]$", r"\1[REDACTED]", line)
        redacted.append(line)
    return "\n".join(redacted) + ("\n" if text.endswith("\n") else "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runtime-capture", type=Path, required=True)
    ap.add_argument("--service-capture", type=Path, required=True)
    ap.add_argument("--matrix", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.output.exists() and not args.dry_run:
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    matrix_rows = []
    with args.matrix.open(newline="") as f:
        matrix_rows = [r for r in csv.DictReader(f) if r.get("service_name") in KEY_SERVICES]
    if args.dry_run:
        print(json.dumps({
            "runtime_capture": str(args.runtime_capture),
            "service_capture": str(args.service_capture),
            "matrix_rows": len(matrix_rows),
            "output": str(args.output),
            "writes_device": False,
        }, indent=2))
        return 0

    args.output.mkdir(parents=True)
    runtime = args.runtime_capture
    service = args.service_capture
    # Keep the exact command outputs for the small set of observations used in
    # the report.  Broad package/activity/logcat dumps remain local.
    selected_files = [
        runtime / "build_properties.stdout.txt",
        runtime / "home_resolve.stdout.txt",
        runtime / "home_candidates_cmd.stdout.txt",
        runtime / "preferred_xml.stdout.txt",
        runtime / "activity_activities.stdout.txt",
        runtime / "window_windows.stdout.txt",
        runtime / "role_dump.stdout.txt",
        service / "id.stdout.txt",
        service / "getenforce.stdout.txt",
        service / "fingerprint.stdout.txt",
    ]
    home_lines: list[str] = []
    for path in selected_files:
        if path.exists():
            content = read(path)
            if path.name == "build_properties.stdout.txt":
                content = redact_public_properties(content)
            home_lines.append(f"--- {path.name} ---\n{content}")
    write_once(args.output / "home-and-build-state.txt", "\n".join(home_lines))

    checks: list[str] = []
    for name in sorted(KEY_SERVICES):
        path = service / f"service_check_{name}.stdout.txt"
        if path.exists():
            checks.append(f"{name}: {read(path).strip()}")
    write_once(args.output / "service-check-results.txt", "\n".join(checks) + "\n")

    fosdebug = service / "dumpsys_fosdebug.stdout.txt"
    if fosdebug.exists():
        text = read(fosdebug)
        bounded = []
        keep = False
        for line in text.splitlines():
            if line.startswith("Vendor Services:") or line.startswith("VendorManagers:"):
                keep = True
            if keep:
                bounded.append(line)
        write_once(args.output / "fosdebug-service-inventory.txt", "\n".join(bounded) + "\n")

    logcat = service / "logcat_targeted.stdout.txt"
    if logcat.exists():
        relevant = [
            line for line in read(logcat).splitlines()
            if re.search(r"service=(amazon(packagemanager|activitymanager|windowmanager|devicepolicymanager|profileservice|usermanagerservice)|amazon_(input|keyevent))", line, re.I)
        ]
        write_once(args.output / "amazon-service-avc.txt", "\n".join(relevant) + "\n")

    matrix_fields = list(matrix_rows[0]) if matrix_rows else ["service_name"]
    matrix_out = args.output / "service-context-key-rows.csv"
    with matrix_out.open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=matrix_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(matrix_rows, key=lambda r: r["service_name"]))

    inputs = {}
    for path in [
        args.matrix,
        service / "metadata.json",
        service / "sha256sums.txt",
        runtime / "metadata.json",
        runtime / "sha256sums.txt",
        Path("decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"),
        Path("decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log"),
        Path("artifacts/phase6j/phase6j-service-visibility-20260805-01/filtered_avc.matches.txt"),
    ]:
        if path.exists():
            inputs[str(path)] = sha256(path)
    write_once(args.output / "input-sha256.json", json.dumps(inputs, indent=2, sort_keys=True) + "\n")
    write_once(args.output / "scope.txt", "Host-only export; no Binder transaction, broadcast, settings write, package mutation, reboot, OTA, or partition operation was performed by this exporter.\n")
    files = sorted(p for p in args.output.iterdir() if p.is_file())
    write_once(
        args.output / "sha256sums.txt",
        "".join(f"{sha256(p)}  {p.name}\n" for p in files),
    )
    print(json.dumps({"output": str(args.output), "matrix_rows": len(matrix_rows), "device_mutation": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
