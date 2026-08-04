#!/usr/bin/env python3
"""Compare preserved PS7331 SELinux policy variants without touching a device.

This is a host-only text comparison.  It does not compile or load SELinux
policy, execute an extracted binary, contact ADB, or infer that a file named
"rootable" is active at runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


MAX_TEXT_BYTES = 64 * 1024 * 1024


def digest(file_path: Path) -> str:
    value = hashlib.sha256()
    with file_path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read_text(file_path: Path) -> str:
    if file_path.stat().st_size > MAX_TEXT_BYTES:
        raise ValueError(f"text file exceeds limit: {file_path}")
    return file_path.read_text(encoding="utf-8", errors="replace")


def policy_summary(standard: Path, variant: Path) -> dict[str, object]:
    standard_text = read_text(standard)
    variant_text = read_text(variant)
    standard_lines = standard_text.splitlines()
    variant_lines = variant_text.splitlines()
    standard_su_lines = [line for line in standard_lines if re.search(r"\bsu(?:_|\b)", line)]
    variant_su_lines = [line for line in variant_lines if re.search(r"\bsu(?:_|\b)", line)]
    return {
        "standard": str(standard),
        "standard_sha256": digest(standard),
        "standard_bytes": standard.stat().st_size,
        "standard_lines": len(standard_lines),
        "standard_su_related_lines": len(standard_su_lines),
        "variant": str(variant),
        "variant_sha256": digest(variant),
        "variant_bytes": variant.stat().st_size,
        "variant_lines": len(variant_lines),
        "variant_su_related_lines": len(variant_su_lines),
        "byte_identical": standard.read_bytes() == variant.read_bytes(),
        "line_count_delta": len(variant_lines) - len(standard_lines),
    }


def find_literal_references(roots: list[Path], names: list[str]) -> list[str]:
    hits: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else [item for item in root.rglob("*") if item.is_file()]
        for file_path in candidates:
            if file_path.stat().st_size > MAX_TEXT_BYTES:
                continue
            try:
                blob = file_path.read_bytes()
            except OSError:
                continue
            if any(name.encode("utf-8") in blob for name in names):
                hits.append(str(file_path))
    return sorted(set(hits))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--standard-plat", type=Path, required=True)
    parser.add_argument("--rootable-plat", type=Path, required=True)
    parser.add_argument("--standard-vendor", type=Path, required=True)
    parser.add_argument("--rootable-vendor", type=Path, required=True)
    parser.add_argument("--scan-root", action="append", type=Path, default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [args.standard_plat, args.rootable_plat, args.standard_vendor, args.rootable_vendor]
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "host_only": True,
            "device_contacted": False,
            "policy_loaded": False,
            "output": str(args.output),
            "inputs": [str(item) for item in inputs],
        }, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    for item in inputs:
        if not item.is_file():
            raise SystemExit(f"missing input: {item}")

    names = [args.rootable_plat.name, args.rootable_vendor.name]
    result = {
        "schema": "phase6c-selinux-policy-variant-audit-v1",
        "host_only": True,
        "device_contacted": False,
        "policy_loaded": False,
        "binary_executed": False,
        "comparisons": [
            policy_summary(args.standard_plat, args.rootable_plat),
            policy_summary(args.standard_vendor, args.rootable_vendor),
        ],
        "literal_variant_filename_references": find_literal_references(args.scan_root, names),
        "interpretation": [
            "A rootable_* filename is an artifact name, not proof of an active runtime policy.",
            "Text differences identify an alternate policy variant but do not establish which policy init or the kernel loaded.",
            "This audit does not alter, compile, load, or test SELinux policy.",
        ],
    }
    args.output.mkdir(parents=True)
    (args.output / "selinux-policy-variant-audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "result.md").write_text(
        "# Phase 6C SELinux policy variant audit\n\n"
        "Host-only comparison of preserved text policy variants. No policy was "
        "compiled, loaded, executed, or sent to a device.\n\n"
        f"- Literal variant filename references outside the variant inputs: "
        f"{len(result['literal_variant_filename_references'])}\n"
        "- Runtime policy selection: UNKNOWN\n",
        encoding="utf-8",
    )
    manifest_lines = []
    for file_path in sorted(args.output.iterdir()):
        if file_path.is_file():
            manifest_lines.append(f"{digest(file_path)}  {file_path.name}")
    (args.output / "sha256sums.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "comparisons": len(result["comparisons"]),
        "literal_variant_filename_references": len(result["literal_variant_filename_references"]),
        "host_only": True,
        "device_contacted": False,
        "policy_loaded": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
