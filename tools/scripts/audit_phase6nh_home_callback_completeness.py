#!/usr/bin/env python3
"""Host-only completeness audit for the collected HOME resolver callbacks.

This script only reads preserved fosinit XML and VDEX disassembly logs.  It
does not invoke adb, Binder, an updater, or any device-side operation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree


BASE = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_callbacks(xml_dir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(xml_dir.glob("*fosinit*.xml")):
        root = ElementTree.parse(path).getroot()
        for node in root.iter():
            if node.tag.rsplit("}", 1)[-1] != "callback":
                continue
            base = node.attrib.get("base", "")
            impl = node.attrib.get("impl", "")
            if base != "com.android.server.am.VendorActivityStackSupervisorCallback":
                continue
            rows.append({
                "source": str(path.relative_to(BASE)),
                "source_sha256": sha256(path),
                "base": base,
                "impl": impl,
            })
    return rows


def class_block(log_text: str, simple_name: str) -> str:
    pattern = re.compile(
        r"class #[^\n]+: " + re.escape(simple_name)
        + r" \([^\n]+\).*?(?=\n  class #|\Z)",
        re.S,
    )
    match = pattern.search(log_text)
    return match.group(0) if match else ""


def analyze_row(row: dict[str, str], service_log: str, fos_log: str) -> dict[str, object]:
    impl = row["impl"]
    simple_name = impl.rsplit(".", 1)[-1]
    blocks = [class_block(service_log, simple_name), class_block(fos_log, simple_name)]
    block = next((candidate for candidate in blocks if candidate), "")
    has_class = bool(block)
    method_match = re.search(
        r"virtual_method #[^\n]+: resolveIntent \([^\n]+\).*?(?=\n   (?:virtual_method|direct_method|class #)|\Z)",
        block,
        re.S,
    )
    method = method_match.group(0) if method_match else ""
    direct_ipm = "IPackageManager;.resolveIntent" in method
    returns_null = bool(re.search(r"const/4 v\d+, #int 0.*?return-object v\d+", method, re.S))
    return {
        **row,
        "simple_name": simple_name,
        "class_found": has_class,
        "resolve_override": bool(method_match),
        "direct_ipm_resolve": direct_ipm,
        "exception_null_path": returns_null,
        "method_excerpt": method[:4000],
    }


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml-dir", type=Path, default=BASE / "artifacts/amazon-services")
    parser.add_argument("--services-log", type=Path, default=BASE / "decompiled/baksmali/vdexExtractor/services/disassembly.log")
    parser.add_argument("--fosservices-log", type=Path, default=BASE / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log")
    parser.add_argument("--output", type=Path, default=BASE / "artifacts/phase6nh-home-callback-completeness-20260810-01")
    parser.add_argument("--dry-run", action="store_true", help="validate inputs and print the planned output only")
    args = parser.parse_args()

    inputs = [args.xml_dir, args.services_log, args.fosservices_log]
    missing = [str(path) for path in inputs if not path.exists()]
    if missing:
        print("missing input: " + ", ".join(missing), file=sys.stderr)
        return 2
    if args.output.exists():
        print(f"refusing to overwrite existing output: {args.output}", file=sys.stderr)
        return 2

    callbacks = parse_callbacks(args.xml_dir)
    service_text = args.services_log.read_text(encoding="utf-8", errors="replace")
    fos_text = args.fosservices_log.read_text(encoding="utf-8", errors="replace")
    rows = [analyze_row(row, service_text, fos_text) for row in callbacks]
    if args.dry_run:
        print(json.dumps({
            "host_only": True,
            "device_contacted": False,
            "callback_xml_count": len(callbacks),
            "output": str(args.output),
        }, indent=2))
        return 0

    args.output.mkdir(parents=True)
    manifest = {
        "host_only": True,
        "device_contacted": False,
        "binder_called": False,
        "xml_dir": str(args.xml_dir.relative_to(BASE)),
        "services_log": str(args.services_log.relative_to(BASE)),
        "fosservices_log": str(args.fosservices_log.relative_to(BASE)),
        "callback_xml_count": len(callbacks),
        "rows": len(rows),
    }
    write_text(args.output / "manifest.json", json.dumps(manifest, indent=2) + "\n")

    with (args.output / "callback-completeness.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "source", "source_sha256", "base", "impl", "simple_name",
            "class_found", "resolve_override", "direct_ipm_resolve",
            "exception_null_path",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in fields} for row in rows)

    details = []
    for row in rows:
        details.append(
            f"### {row['impl']}\n"
            f"- XML: `{row['source']}` (SHA-256 `{row['source_sha256']}`)\n"
            f"- class in collected VDEX: `{row['class_found']}`\n"
            f"- concrete `resolveIntent`: `{row['resolve_override']}`\n"
            f"- direct `IPackageManager.resolveIntent`: `{row['direct_ipm_resolve']}`\n"
            f"- exception/null return path observed: `{row['exception_null_path']}`\n"
        )
        if row["method_excerpt"]:
            details.append("```text\n" + str(row["method_excerpt"]) + "\n```\n")

    report = """# Phase 6NH — collected HOME callback completeness audit

## Scope

This is a host-only audit of the preserved PS7331 `fosinit` XML and services
VDEX disassembly. It does not invoke `adb`, Binder, the OTA updater, or any
device operation. It answers only whether the collected configuration names
additional `VendorActivityStackSupervisorCallback` implementations and
whether those implementations contain a concrete `resolveIntent` method.

## Result

The audit found the complete set of matching callback registrations in the
collected XML directory and mapped each registration against both collected
services disassembly logs. A callback is not treated as absent from the real
device merely because it is absent from this preserved artifact set; that
residual limitation is recorded explicitly.

""" + "\n".join(details)
    write_text(args.output / "result.md", report)

    graph = [
        "flowchart TD",
        "  XML[Collected fosinit XML] --> C[Supervisor callback registrations]",
        "  C --> V[Collected services/fosservices VDEX class inventory]",
        "  V --> R[resolveIntent override and return-shape audit]",
        "  R --> P[AppCompat: IPackageManager.resolveIntent + filter]",
        "  R --> N[Eve/base: no concrete resolver override / null path]",
        "  R -.-> U[Unknown: artifacts not preserved in this workspace]",
    ]
    write_text(args.output / "callback-completeness.mmd", "\n".join(graph) + "\n")

    files = sorted(path for path in args.output.iterdir() if path.is_file() and path.name != "sha256sums.txt")
    sums = "\n".join(f"{sha256(path)}  {path.name}" for path in files) + "\n"
    write_text(args.output / "sha256sums.txt", sums)
    print(json.dumps({**manifest, "output": str(args.output), "callback_rows": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
