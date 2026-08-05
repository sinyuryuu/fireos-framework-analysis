#!/usr/bin/env python3
"""Join Amazon service registrations, service contexts and read-only runtime evidence.

This is a host-only evidence normalizer.  It does not connect to a device and
does not invoke Binder transactions.  Missing authorization markers are kept as
unknowns; they are never treated as vulnerabilities.
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


SERVICE_LINE = re.compile(r"(?:^|\s)\d+\s+([^\s:]+):\s*\[(.*?)\]\s*$")
CONTEXT_LINE = re.compile(r"^\s*([^\s#]+)\s+(u:object_r:[^\s#]+)")
AVC_FIND = re.compile(
    r"avc:\s+denied\s+\{\s*find\s*\}.*?service=([^\s]+).*?uid=(\d+)"
)
AVC_TCTX = re.compile(r"tcontext=([^\s]+)")

# These aliases are deliberately limited to names corroborated by the saved
# service-list/AVC evidence.  They are not inferred from arbitrary class names.
KNOWN_CLASS_SERVICE_ALIASES = {
    "AmazonActivityManagerService": ["amazonactivitymanager"],
    "AmazonDevicePolicyManagerService": ["amazondevicepolicymanager"],
    "AmazonPackageManagerService": ["amazonpackagemanager"],
    "AmazonWindowManagerService": ["amazonwindowmanager"],
    "AmazonUserManagerService": ["amazonusermanagerservice"],
    "AmazonInputManagerService": ["amazon_input", "amazon_keyevent"],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def parse_fosinit(directory: Path) -> dict[str, list[str]]:
    """Return implementation class -> registration files."""
    registrations: dict[str, list[str]] = {}
    for path in sorted(directory.glob("*fosinit.xml")):
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError as exc:
            raise SystemExit(f"invalid fosinit XML: {path}: {exc}")
        for node in root.iter():
            if node.tag.rsplit("}", 1)[-1] != "service":
                continue
            impl = node.attrib.get("impl")
            if impl:
                registrations.setdefault(impl, []).append(str(path))
                # The VDEX inventory stores simple class names while fosinit
                # stores fully-qualified names.  Keep both keys so the join
                # remains explicit and reproducible.
                registrations.setdefault(impl.rsplit(".", 1)[-1], []).append(str(path))
    return registrations


def parse_contexts(image_root: Path) -> dict[str, dict[str, str]]:
    """Return service name -> context and source files."""
    out: dict[str, dict[str, str]] = {}
    for path in sorted(image_root.rglob("*")):
        if not path.is_file() or path.name not in {
            "plat_service_contexts",
            "vendor_service_contexts",
            "vndservice_contexts",
        }:
            continue
        for line_no, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            match = CONTEXT_LINE.match(line)
            if not match:
                continue
            name, context = match.groups()
            out[name] = {
                "context": context,
                "source": str(path),
                "line": str(line_no),
            }
    return out


def parse_runtime_services(path: Path | None) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path or not path.exists():
        return out
    for line in path.read_text(errors="replace").splitlines():
        match = SERVICE_LINE.match(line)
        if match:
            out[match.group(1)] = match.group(2)
    return out


def parse_avc(path: Path | None) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not path or not path.exists():
        return out
    for line_no, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        match = AVC_FIND.search(line)
        if not match:
            continue
        service, uid = match.groups()
        tctx = AVC_TCTX.search(line)
        out[service] = {
            "uid": uid,
            "tcontext": tctx.group(1) if tctx else "UNKNOWN",
            "source": str(path),
            "line": str(line_no),
        }
    return out


def service_names_from_evidence(inventory_rows: list[dict[str, str]]) -> set[str]:
    names: set[str] = set()
    for row in inventory_rows:
        evidence = row.get("published_name_evidence", "")
        if evidence in {"", "NOT_LITERAL_OR_DELEGATED"}:
            continue
        for value in re.split(r"\s*\|\s*", evidence):
            if value and value not in {"NOT_LITERAL_OR_DELEGATED"}:
                names.add(value)
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fosinit-dir", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--runtime-service-list", type=Path)
    parser.add_argument("--avc", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.output.exists() and not args.dry_run:
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")

    with args.inventory.open(newline="") as f:
        inventory_rows = list(csv.DictReader(f))
    registrations = parse_fosinit(args.fosinit_dir)
    contexts = parse_contexts(args.image_root)
    runtime = parse_runtime_services(args.runtime_service_list)
    avc = parse_avc(args.avc)

    rows: list[dict[str, str]] = []
    known_names = set(runtime) | set(avc) | service_names_from_evidence(inventory_rows)
    for row in inventory_rows:
        evidence = row.get("published_name_evidence", "")
        names = [n for n in re.split(r"\s*\|\s*", evidence) if n and n != "NOT_LITERAL_OR_DELEGATED"]
        names.extend(KNOWN_CLASS_SERVICE_ALIASES.get(row.get("service_impl_class", ""), []))
        names = list(dict.fromkeys(names))
        if not names:
            names = ["UNKNOWN_PUBLISHED_NAME"]
        for name in names:
            known_names.add(name)
        reg = registrations.get(row.get("service_impl_class", ""), [])
        for name in names:
            ctx = contexts.get(name, {})
            denied = avc.get(name, {})
            rows.append({
                "service_name": name,
                "service_impl_class": row.get("service_impl_class", ""),
                "fosinit_registered": "YES" if reg else "NO_OR_DELEGATED",
                "fosinit_files": ";".join(reg),
                "published_name_evidence": evidence,
                "runtime_service_list": "YES" if name in runtime else "NO_OR_NOT_CAPTURED",
                "service_context": ctx.get("context", "NOT_FOUND_IN_EXTRACTED_TEXT_CONTEXTS"),
                "service_context_source": ctx.get("source", ""),
                "service_context_line": ctx.get("line", ""),
                "shell_uid2000_find_denied": "YES" if denied.get("uid") == "2000" else "NO_OR_NOT_OBSERVED",
                "avc_tcontext": denied.get("tcontext", ""),
                "avc_source": denied.get("source", ""),
                "avc_line": denied.get("line", ""),
                "binder_inventory_auth_markers": row.get("class_auth_markers", "UNKNOWN"),
                "binder_inventory_assessment": row.get("assessment", "UNKNOWN"),
                "confidence": "STRONG_EVIDENCE" if name in runtime and name in avc else "EVIDENCE_JOIN_PENDING",
            })

    # Add runtime/AVC names not mapped to a VDEX service row so the absence is explicit.
    represented = {r["service_name"] for r in rows}
    for name in sorted(known_names - represented):
        ctx = contexts.get(name, {})
        denied = avc.get(name, {})
        rows.append({
            "service_name": name,
            "service_impl_class": "UNMAPPED",
            "fosinit_registered": "UNKNOWN",
            "fosinit_files": "",
            "published_name_evidence": "",
            "runtime_service_list": "YES" if name in runtime else "NO_OR_NOT_CAPTURED",
            "service_context": ctx.get("context", "NOT_FOUND_IN_EXTRACTED_TEXT_CONTEXTS"),
            "service_context_source": ctx.get("source", ""),
            "service_context_line": ctx.get("line", ""),
            "shell_uid2000_find_denied": "YES" if denied.get("uid") == "2000" else "NO_OR_NOT_OBSERVED",
            "avc_tcontext": denied.get("tcontext", ""),
            "avc_source": denied.get("source", ""),
            "avc_line": denied.get("line", ""),
            "binder_inventory_auth_markers": "UNKNOWN",
            "binder_inventory_assessment": "NOT_MAPPED_TO_VDEX_INVENTORY",
            "confidence": "STRONG_EVIDENCE" if name in runtime and name in avc else "EVIDENCE_JOIN_PENDING",
        })

    fields = list(rows[0]) if rows else ["service_name"]
    if args.dry_run:
        print(json.dumps({
            "fosinit_files": len(list(args.fosinit_dir.glob("*fosinit.xml"))),
            "inventory_rows": len(inventory_rows),
            "runtime_services": len(runtime),
            "avc_denied_find_services": len(avc),
            "context_entries": len(contexts),
            "output": str(args.output),
        }, indent=2))
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: r["service_name"]))
    print(f"wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
