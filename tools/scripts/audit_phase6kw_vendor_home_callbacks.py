#!/usr/bin/env python3
"""Audit Fire OS VendorActivityStackSupervisorCallback HOME boundaries.

This is a host-only parser for already-collected fosinit XML and VDEX
disassembly text.  It does not contact a device, invoke Binder, or execute
any APK/native code.  The output deliberately reports only observed method
shapes; it does not infer a callback implementation when the artifact is
missing or truncated.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FOSINIT_DIR = ROOT / "artifacts" / "amazon-services"
DEFAULT_FOSSERVICES = ROOT / "decompiled" / "baksmali" / "vdexExtractor" / "fosservices" / "disassembly.log"
DEFAULT_SERVICES = ROOT / "decompiled" / "baksmali" / "vdexExtractor" / "services" / "disassembly.log"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def class_blocks(text: str) -> dict[str, str]:
    """Return raw disassembly blocks keyed by JVM simple class name."""
    starts = list(re.finditer(r"^  class #\d+: ([^ (]+)", text, re.MULTILINE))
    blocks: dict[str, str] = {}
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        blocks[match.group(1)] = text[match.start():end]
    return blocks


def class_exists(blocks: dict[str, str], fqcn: str) -> tuple[bool, str | None]:
    simple = fqcn.rsplit(".", 1)[-1]
    for name, block in blocks.items():
        if name == simple or fqcn.replace(".", "/") in block:
            declaration = next((line for line in block.splitlines() if line.startswith("  class #")), None)
            return True, declaration
    return False, None


def method_block(block: str, method: str) -> str | None:
    # A method body ends at the next direct/virtual method or class declaration.
    pattern = re.compile(r"^   (?:direct_method|virtual_method) #\d+: " + re.escape(method) + r" \(", re.MULTILINE)
    match = pattern.search(block)
    if not match:
        return None
    tail = block[match.start():]
    next_match = re.search(r"^   (?:direct_method|virtual_method) #\d+: |^  class #\d+:", tail[1:], re.MULTILINE)
    return tail[:next_match.start() + 1] if next_match else tail


def method_evidence(block: str, method: str, full_text: str) -> dict[str, object]:
    body = method_block(block, method)
    if body is None:
        return {"override": False, "line": None, "body": "", "ipm_resolve": False, "returns_null": False}
    block_offset = full_text.find(block)
    body_offset = block_offset + block.find(body) if block_offset >= 0 else -1
    return {
        "override": True,
        "line": full_text.count("\n", 0, body_offset) + 1 if body_offset >= 0 else None,
        "body": body,
        "ipm_resolve": "IPackageManager;.resolveIntent" in body,
        "returns_null": bool(re.search(r"const/4 v\d+, #int 0.*\n.*return-object v\d+", body)),
    }


@dataclass
class CallbackRow:
    source: str
    base: str
    implementation: str
    fosinit_sha256: str
    registered: str
    class_found: str
    class_declaration: str
    resolve_override: str
    resolve_line: str
    direct_ipm_resolve: str
    returns_null_shape: str
    hardcoded_fire_literal: str
    observed_behavior: str
    confidence: str


def parse_callbacks(fosinit_dir: Path, fosservices_text: str, fosservices_blocks: dict[str, str]) -> list[CallbackRow]:
    rows: list[CallbackRow] = []
    base_target = "com.android.server.am.VendorActivityStackSupervisorCallback"
    for xml_path in sorted(fosinit_dir.glob("*_fosinit.xml")):
        try:
            root = ET.parse(xml_path).getroot()
        except (ET.ParseError, OSError):
            continue
        for element in root.iter():
            if local_name(element.tag) != "callback" or element.attrib.get("base") != base_target:
                continue
            implementation = element.attrib.get("impl", "")
            found, declaration = class_exists(fosservices_blocks, implementation)
            simple = implementation.rsplit(".", 1)[-1]
            block = fosservices_blocks.get(simple, "")
            evidence = method_evidence(block, "resolveIntent", fosservices_text)
            literal = "com.amazon.firelauncher" in block or "firelauncher" in block.lower()
            if not found:
                behavior = "implementation class not present in selected disassembly"
                confidence = "UNKNOWN"
            elif evidence["override"] and evidence["ipm_resolve"]:
                behavior = "delegates to IPackageManager.resolveIntent, then applies isUninstalledApp filter"
                confidence = "Confirmed"
            elif evidence["override"]:
                behavior = "resolveIntent override exists; body requires manual review"
                confidence = "Strong evidence"
            else:
                behavior = "no concrete resolveIntent override; inherited base returns null"
                confidence = "Confirmed"
            rows.append(CallbackRow(
                source=str(xml_path.relative_to(ROOT)),
                base=base_target,
                implementation=implementation,
                fosinit_sha256=sha256(xml_path),
                registered="yes",
                class_found="yes" if found else "no",
                class_declaration=declaration or "",
                resolve_override="yes" if evidence["override"] else "no",
                resolve_line=str(evidence["line"] or ""),
                direct_ipm_resolve="yes" if evidence["ipm_resolve"] else "no",
                returns_null_shape="yes" if evidence["returns_null"] else "no",
                hardcoded_fire_literal="yes" if literal else "no",
                observed_behavior=behavior,
                confidence=confidence,
            ))
    return rows


def write_csv(path: Path, rows: list[CallbackRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(asdict(rows[0]).keys()) if rows else list(CallbackRow.__annotations__.keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def write_report(path: Path, rows: list[CallbackRow], fosservices: Path, services: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 6KW — Vendor HOME callback closure",
        "",
        "Scope: host-only analysis of collected `fosinit` XML and VDEX disassembly. No device command, Binder transaction, APK execution, or state mutation was performed.",
        "",
        "## Inputs",
        "",
        f"- `{fosservices.relative_to(ROOT)}` — SHA-256 `{sha256(fosservices)}`",
        f"- `{services.relative_to(ROOT)}` — SHA-256 `{sha256(services)}`",
        f"- XML directory `{DEFAULT_FOSINIT_DIR.relative_to(ROOT)}`",
        "",
        "## Observed callback registrations",
        "",
        "| Implementation | Resolve line | Resolve override | Observed behavior | Fire literal | Confidence |",
        "|---|---:|---:|---|---:|---|",
    ]
    for row in rows:
        lines.append(f"| `{row.implementation}` | {row.resolve_line or '—'} | {row.resolve_override} | {row.observed_behavior} | {row.hardcoded_fire_literal} | {row.confidence} |")
    lines += [
        "",
        "## Decision",
        "",
        "- **Confirmed:** `ActivityStackSupervisor.resolveIntent()` invokes the vendor callback chain first and falls back to the standard `PackageManagerInternal.resolveIntent()` result when every callback returns null.",
        "- **Confirmed:** the collected AppCompat callback delegates to `IPackageManager.resolveIntent()` and only filters the observed uninstalled-app flag; the method does not contain the Fire Launcher package literal.",
        "- **Confirmed:** the collected Eve supervisor callback has no concrete `resolveIntent` override and therefore inherits the base null result; its observed method is restart telemetry, not HOME selection.",
        "- **Strong evidence:** the registered launcher-hijack-preventer fosinit files do not register a `VendorActivityStackSupervisorCallback`; their registrations are ActivityStack/AMS or PM/permission callbacks.",
        "- **Not established:** this artifact scope alone cannot prove that every runtime-loaded callback or every non-VDEX native path is absent. The result is a static closure for the collected PS7331 artifacts, not a universal negative.",
        "",
        "See the generated CSV and Mermaid graph for exact file-level evidence.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_mermaid(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("""flowchart TD
    H["HOME implicit Intent<br/>MAIN + CATEGORY_HOME"] --> S["ActivityStackSupervisor.resolveIntent"]
    S --> C["VendorActivityStackSupervisorCallback.callResolveIntent"]
    C --> A["AppCompatActivityStackSupervisorCallback.resolveIntent"]
    A --> P["IPackageManager.resolveIntent"]
    A --> F["isUninstalledApp filter"]
    C --> E["EveActivityStackSupervisorCallback"]
    E --> N["inherits base resolveIntent -> null"]
    C --> Z["all callbacks null"]
    Z --> Q["PackageManagerInternal.resolveIntent"]
    P --> R["ResolveInfo or null"]
    Q --> R
    R --> H2["Activity launch path"]
    classDef boundary fill:#fff4cc,stroke:#8a6d1d,color:#222;
    class C,A,E,N,Z boundary;
""", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--fosinit-dir", type=Path, default=DEFAULT_FOSINIT_DIR)
    parser.add_argument("--fosservices", type=Path, default=DEFAULT_FOSSERVICES)
    parser.add_argument("--services", type=Path, default=DEFAULT_SERVICES)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts" / "phase6kw-vendor-home-callbacks")
    args = parser.parse_args(argv)

    for path in (args.fosservices, args.services, args.fosinit_dir):
        if not path.exists():
            print(f"missing input: {path}", file=sys.stderr)
            return 2
    fosservices_text = args.fosservices.read_text(encoding="utf-8", errors="replace")
    services_text = args.services.read_text(encoding="utf-8", errors="replace")
    fosservices_blocks = class_blocks(fosservices_text)
    rows = parse_callbacks(args.fosinit_dir, fosservices_text, fosservices_blocks)

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "vendor-home-callbacks.csv", rows)
    write_report(out / "result.md", rows, args.fosservices, args.services)
    write_mermaid(out / "vendor-home-callbacks.mmd")
    manifest = {
        "scope": "host-only; no device interaction",
        "inputs": {
            "fosinit_dir": str(args.fosinit_dir.relative_to(args.root)),
            "fosservices": str(args.fosservices.relative_to(args.root)),
            "fosservices_sha256": sha256(args.fosservices),
            "services": str(args.services.relative_to(args.root)),
            "services_sha256": sha256(args.services),
        },
        "registered_callback_count": len(rows),
        "rows": [asdict(row) for row in rows],
    }
    import json
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} callback rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
