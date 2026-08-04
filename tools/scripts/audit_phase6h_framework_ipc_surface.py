#!/usr/bin/env python3
"""Host-only inventory of Fire OS framework and Amazon IPC surfaces.

This tool scans preserved decompiler output, VDEX disassembly and XML metadata.
It does not connect to ADB, execute APK/JAR/DEX/native code, invoke Binder, or
alter a device.  Findings are leads for manual review, not exploitability
claims.  Existing output is never overwritten.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


TEXT_SUFFIXES = {
    ".java", ".kt", ".xml", ".smali", ".log", ".txt", ".tsv", ".md",
    ".json", ".prop", ".cil", ".fosinit", ".xsd", ".aidl",
}
SKIP_NAMES = {"R.java", "BuildConfig.java"}

PATTERNS: list[tuple[str, str, str]] = [
    ("permission_check", r"check(?:Calling|CallingOrSelf|Permission)|enforce(?:Calling|CallingOrSelf|Permission)", "permission boundary API"),
    ("caller_identity", r"Binder\.getCalling(?:Uid|Pid)|getCallingUid|getCallingPid|Process\.SHELL_UID", "caller identity"),
    ("binder_service", r"publishBinderService|ServiceManager\.(?:getService|addService)|LocalServices\.(?:getService|addService)|onTransact|\.Stub;", "Binder/service registration or dispatch"),
    ("broadcast_receiver", r"registerReceiver(?:AsUser)?|sendBroadcast(?:AsUser)?|BroadcastReceiver|onReceive", "broadcast receiver or sender"),
    ("intent_dispatch", r"startActivity(?:AsUser)?|startService(?:AsUser)?|bindService|resolveIntent|resolveActivity|setComponentEnabledSetting|setApplicationEnabledSetting|setPreferredActivity|addPreferredActivity|replacePreferredActivity", "activity/package state dispatch"),
    ("pending_intent", r"PendingIntent|send(?:AndCancel)?\s*\(|getActivity|createPendingResult", "PendingIntent or callback dispatch"),
    ("settings_write", r"Settings\.(?:System|Secure|Global)|put(?:String|Int|Long|Float)ForUser|WRITE_(?:SECURE_)?SETTINGS|WRITE_GSERVICES", "settings read/write surface"),
    ("high_privilege_permission", r"(?:android|amazon|com\.amazon)[.\w]*\b(?:MANAGE_PROFILE_AND_DEVICE_OWNERS|MANAGE_DEVICE_ADMINS|INSTALL_PACKAGES|DELETE_PACKAGES|CHANGE_COMPONENT_ENABLED_STATE|MASTER_CLEAR|REBOOT|INJECT_EVENTS|INTERNAL_SYSTEM_WINDOW|WRITE_SECURE_SETTINGS|READ_LOGS|DUMP|RECOVERY|MODIFY_PHONE_STATE|FORCE_STOP_PACKAGES|CLEAR_APP_USER_DATA|MANAGE_USERS|INTERACT_ACROSS_USERS_FULL)\b", "high-privilege permission reference"),
    ("home_control", r"(?:startHome|launchHome|handleShortPressOnHome|CATEGORY_HOME|ACTION_MAIN|defaultHome|homeIntent|firelauncher|LauncherHijack|KeyPolicy)", "HOME/launcher control marker"),
]
COMPILED = [(kind, re.compile(pattern, re.IGNORECASE), description) for kind, pattern, description in PATTERNS]

ANDROID_NS = "http://schemas.android.com/apk/res/android"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def attr(element: ET.Element, name: str) -> str:
    return element.attrib.get(f"{{{ANDROID_NS}}}{name}", element.attrib.get(name, ""))


def current_context(line: str, state: dict[str, str]) -> None:
    class_match = re.search(r"(?:^|\s)(?:class|interface|enum)\s+([\w$.-]+)", line)
    smali_class = re.search(r"\.class\s+[^;]*L([^;]+);", line)
    if class_match:
        state["class"] = class_match.group(1)
    elif smali_class:
        state["class"] = smali_class.group(1).replace("/", ".")

    method_match = re.search(r"(?:direct_method|virtual_method).*?:\s*([\w$<>-]+)\s*\(([^)]*)\)(.*)$", line)
    if method_match:
        state["method"] = f"{method_match.group(1)}({method_match.group(2)}){method_match.group(3)}"
        return
    java_method = re.search(r"^\s*(?:public|private|protected|static|final|synchronized|native|abstract|\s)+[\w$<>\[\]., ?]+\s+([\w$<>-]+)\s*\([^;]*\)\s*(?:throws[^\{]+)?[\{;]?\s*$", line)
    if java_method and java_method.group(1) not in {"if", "for", "while", "switch", "catch"}:
        state["method"] = java_method.group(1)


def is_probably_text(path: Path) -> bool:
    if path.name in SKIP_NAMES:
        return False
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    try:
        sample = path.read_bytes()[:8192]
    except OSError:
        return False
    return b"\x00" not in sample


def scan_text(path: Path, root_label: str, findings: list[dict[str, object]], marker_counts: Counter[str], max_findings: int) -> None:
    try:
        stream = path.open("r", encoding="utf-8", errors="replace")
    except OSError:
        return
    state = {"class": "", "method": ""}
    with stream:
        for line_number, line in enumerate(stream, 1):
            current_context(line, state)
            for kind, pattern, description in COMPILED:
                if pattern.search(line):
                    marker_counts[kind] += 1
                    if len(findings) < max_findings:
                        findings.append({
                            "root": root_label,
                            "file": str(path),
                            "line": line_number,
                            "class": state["class"],
                            "method": state["method"],
                            "kind": kind,
                            "description": description,
                            "excerpt": line.strip()[:500],
                        })


def scan_manifest(path: Path, root_label: str) -> list[dict[str, object]]:
    components: list[dict[str, object]] = []
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return components
    package = root.attrib.get("package", "")
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag not in {"activity", "activity-alias", "service", "receiver", "provider", "permission"}:
            continue
        name = attr(element, "name")
        if not name and tag != "permission":
            continue
        actions = []
        for child in element:
            child_tag = child.tag.rsplit("}", 1)[-1]
            if child_tag == "intent-filter":
                actions.extend(attr(grandchild, "name") for grandchild in child if grandchild.tag.rsplit("}", 1)[-1] == "action")
        components.append({
            "root": root_label,
            "file": str(path),
            "package": package,
            "type": tag,
            "name": name,
            "exported": attr(element, "exported"),
            "permission": attr(element, "permission"),
            "read_permission": attr(element, "readPermission"),
            "write_permission": attr(element, "writePermission"),
            "protection_level": attr(element, "protectionLevel"),
            "process": attr(element, "process"),
            "actions": ",".join(action for action in actions if action),
            "home_marker": any("HOME" in action or "MAIN" in action for action in actions),
        })
    return components


def scan_fosinit(path: Path, root_label: str) -> list[dict[str, object]]:
    edges: list[dict[str, object]] = []
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return edges
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag == "callback":
            edges.append({"root": root_label, "file": str(path), "edge_type": "callback", "base": element.attrib.get("base", ""), "impl": element.attrib.get("impl", ""), "service": "", "permission": ""})
        elif tag == "service":
            edges.append({"root": root_label, "file": str(path), "edge_type": "vendor_service", "base": "", "impl": element.attrib.get("impl", ""), "service": element.attrib.get("name", ""), "permission": ""})
        elif tag == "instance":
            edges.append({"root": root_label, "file": str(path), "edge_type": "vendor_instance", "base": element.attrib.get("base", ""), "impl": element.attrib.get("impl", ""), "service": "", "permission": ""})
    return edges


def collect_files(roots: list[Path]) -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = []
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            candidates = [root]
        else:
            candidates = sorted(path for path in root.rglob("*") if path.is_file())
        for path in candidates:
            if is_probably_text(path):
                files.append((path, str(root)))
    return files


def write_outputs(output: Path, roots: list[Path], files: list[tuple[Path, str]], findings: list[dict[str, object]], marker_counts: Counter[str], components: list[dict[str, object]], edges: list[dict[str, object]], max_findings: int) -> None:
    output.mkdir(parents=True)
    (output / "scan-inputs.json").write_text(json.dumps({"roots": [str(root) for root in roots], "files": len(files), "generated_at_utc": datetime.now(timezone.utc).isoformat()}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (output / "ipc-findings.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["root", "file", "line", "class", "method", "kind", "description", "excerpt"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(findings)
    with (output / "manifest-components.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["root", "file", "package", "type", "name", "exported", "permission", "read_permission", "write_permission", "protection_level", "process", "actions", "home_marker"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(components)
    with (output / "fosinit-edges.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["root", "file", "edge_type", "base", "impl", "service", "permission"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(edges)
    result = {
        "host_only": True,
        "device_contacted": False,
        "code_executed": False,
        "binder_invoked": False,
        "file_count": len(files),
        "captured_finding_count": len(findings),
        "captured_finding_limit": max_findings,
        "marker_counts_all_matches": dict(marker_counts),
        "manifest_component_count": len(components),
        "fosinit_edge_count": len(edges),
        "limitations": [
            "A marker is not proof that a caller can reach the API.",
            "Absence of a nearby permission check is not proof of an authorization bug; checks may be in a parent method, Binder stub, framework, SELinux or manifest.",
            "Decompiler and disassembly context may be incomplete.",
            "No Binder transaction, broadcast, package state or settings mutation was attempted.",
        ],
    }
    (output / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    graph_lines = ["flowchart LR"]
    seen: set[tuple[str, str, str]] = set()
    for edge in edges:
        base = str(edge["base"]) or "base"
        impl = str(edge["impl"]) or "impl"
        key = (str(edge["edge_type"]), base, impl)
        if key in seen:
            continue
        seen.add(key)
        base_id = re.sub(r"[^A-Za-z0-9_]", "_", base)[:70] or "base"
        impl_id = re.sub(r"[^A-Za-z0-9_]", "_", impl)[:70] or "impl"
        graph_lines.append(f'  {base_id}["{base}"] -->|{edge["edge_type"]}| {impl_id}["{impl}"]')
    if len(graph_lines) == 1:
        graph_lines.append('  N["No parseable fosinit edges"]')
    (output / "ipc-edges.mmd").write_text("\n".join(graph_lines) + "\n", encoding="utf-8")
    files_to_hash = sorted(path for path in output.rglob("*") if path.is_file() and path.name != "sha256sums.txt")
    (output / "sha256sums.txt").write_text("\n".join(f"{sha256(path)}  {path.relative_to(output)}" for path in files_to_hash) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", type=Path, required=True, help="host-side directory or text artifact to scan; repeatable")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-findings", type=int, default=15000, help="cap retained line-level findings; all-match counts remain in summary")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps({"dry_run": True, "host_only": True, "device_contacted": False, "roots": [str(root) for root in args.root]}, indent=2))
        return 0
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    files = collect_files(args.root)
    findings: list[dict[str, object]] = []
    marker_counts: Counter[str] = Counter()
    components: list[dict[str, object]] = []
    edges: list[dict[str, object]] = []
    for path, label in files:
        scan_text(path, label, findings, marker_counts, args.max_findings)
        if path.name == "AndroidManifest.xml":
            components.extend(scan_manifest(path, label))
        if path.suffix.lower() in {".xml", ".fosinit"} and ("fosinit" in path.name.lower() or "amazon-services" in str(path)):
            edges.extend(scan_fosinit(path, label))
    write_outputs(args.output, args.root, files, findings, marker_counts, components, edges, args.max_findings)
    print(f"wrote host-only IPC surface audit: {args.output} ({len(files)} files, {len(findings)} captured markers; all-match counts in summary)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
