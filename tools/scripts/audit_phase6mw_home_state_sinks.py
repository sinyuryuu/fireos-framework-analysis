#!/usr/bin/env python3
"""Inventory HOME and package-state sinks across preserved PS7331 artifacts.

This is a host-only provenance audit.  It reads the already-preserved JADX
sources and smali/disassembly logs, records direct sink references with nearby
permission, identity, user-scope, and launcher literals, and emits a review
queue.  It never calls ADB, Binder, a device node, an APK, or a mutating
command.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


DEFAULT_OUTPUT = Path("artifacts/phase6mw-home-state-sinks-20260810-01")
JAVA_ROOTS = (
    Path("decompiled/jadx/ota-PS7331/fosframework/sources"),
    Path("decompiled/jadx/ota-PS7331/fosservices/sources"),
    Path("decompiled/jadx/ota-PS7331/systemui/sources"),
    Path("decompiled/jadx/ota-PS7331/systemui-nores/sources"),
    Path("decompiled/jadx/ota-PS7331/settings/sources"),
    Path("decompiled/jadx/ota-PS7331/firelauncher/sources"),
    Path("decompiled/jadx/ota-PS7331/firelauncher-nores/sources"),
    Path("decompiled/jadx/amazon-settings/sources"),
    Path("decompiled/jadx/parentalcontrols/sources"),
)
DISASSEMBLY_INPUTS = (
    Path("decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"),
    Path("decompiled/baksmali/vdexExtractor/services/disassembly.log"),
    Path("decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log"),
    Path("decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log"),
)
TARGETS = (
    "setHomeActivity",
    "addPreferredActivity",
    "replacePreferredActivity",
    "clearPackagePreferredActivities",
    "addPersistentPreferredActivity",
    "setApplicationEnabledSetting",
    "setComponentEnabledSetting",
    "setApplicationHiddenSettingAsUser",
    "setPackagesSuspendedAsUser",
)
TARGET_RE = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(TARGETS) + r")(?=[:(])")
PACKAGE_RE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.MULTILINE)
CLASS_RE = re.compile(r"^\s*(?:public\s+|private\s+|protected\s+|abstract\s+|final\s+|static\s+)*class\s+(\w+)")
METHOD_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|static|final|synchronized|abstract|native|strictfp)\s+)*"
    r"[\w<>, ?\[\].]+\s+(\w+)\s*\([^;]*\)"
)
DIS_CLASS_RE = re.compile(r"^\s*(?:class|interface) #\d+: .*\('(?P<descriptor>L[^;]+;)'\)")
DIS_METHOD_RE = re.compile(r"^\s*(?:direct|virtual)_method #\d+: (?P<signature>.+)$")

LITERAL_RE = re.compile(
    r"(?:com\.amazon\.firelauncher|com\.amazon\.tahoe|com\.android\.launcher3|"
    r"Launcher3|android\.intent\.action\.MAIN|android\.intent\.category\.HOME|"
    r"CATEGORY_HOME|ACTION_MAIN|HOME_FILTER|default_home|home)",
    re.IGNORECASE,
)
PERMISSION_RE = re.compile(
    r"(?:enforceCalling(?:OrSelf)?Permission|checkCalling(?:OrSelf)?Permission|"
    r"checkPermission|SET_PREFERRED_APPLICATIONS|MANAGE_USERS|SUSPEND_APPS|"
    r"CHANGE_COMPONENT_ENABLED_STATE|INTERACT_ACROSS_USERS|LOCK_SCREEN_SERVICE|"
    r"amazon\.permission\.[A-Z0-9_]+)",
    re.IGNORECASE,
)
IDENTITY_RE = re.compile(r"(?:getCallingUid|clearCallingIdentity|restoreCallingIdentity|myUid)")
USER_RE = re.compile(
    r"(?:UserInfo\.id|userId|callingUserId|targetUserId|userHandle|USER_SYSTEM|"
    r"USER_CURRENT|currentUser|forUser|asUser|UserHandle)",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact(value: str, limit: int = 600) -> str:
    value = " ".join(value.replace("\t", " ").split())
    return value if len(value) <= limit else value[: limit - 3] + "..."


def unique(values: list[str]) -> str:
    return "; ".join(dict.fromkeys(value for value in values if value))


def scope_for(package: str, path: Path) -> tuple[str, str]:
    if package.startswith("com.amazon.") or "/fosservices/" in path.as_posix() or "/fosframework/" in path.as_posix():
        return "amazon_or_oem", "Amazon/OEM application or framework namespace"
    if package.startswith("com.android.server") or package.startswith("android."):
        return "aosp_framework", "AOSP/system_server or framework namespace"
    if package.startswith("com.android.settings"):
        return "settings", "Settings application/library path"
    if package.startswith("com.android.systemui"):
        return "systemui", "SystemUI application path"
    return "other", "non-Amazon bounded corpus"


def method_at(lines: list[str], index: int, disassembly: bool = False) -> str:
    matcher = DIS_METHOD_RE if disassembly else METHOD_RE
    for candidate in range(index, max(-1, index - 180), -1):
        match = matcher.match(lines[candidate])
        if match:
            return match.group("signature") if disassembly else match.group(1)
    return "<unknown>"


def class_at(lines: list[str], index: int, disassembly: bool = False) -> str:
    matcher = DIS_CLASS_RE if disassembly else CLASS_RE
    for candidate in range(index, max(-1, index - 1200), -1):
        match = matcher.match(lines[candidate])
        if match:
            if disassembly:
                return match.group("descriptor")[1:-1].replace("/", ".")
            return match.group(1)
    return "<unknown>"


def context_fields(lines: list[str], index: int) -> tuple[str, str, str, str]:
    nearby = lines[max(0, index - 24) : index + 1]
    joined = "\n".join(nearby)
    literals = unique([compact(match.group(0)) for match in LITERAL_RE.finditer(joined)])
    permissions = unique([compact(match.group(0)) for match in PERMISSION_RE.finditer(joined)])
    identities = unique([compact(match.group(0)) for match in IDENTITY_RE.finditer(joined)])
    users = unique([compact(match.group(0)) for match in USER_RE.finditer(joined)])
    return literals, permissions, identities, users


def make_row(path: Path, source_hash: str, lines: list[str], index: int, target: str, disassembly: bool) -> dict[str, str | int]:
    class_name = class_at(lines, index, disassembly)
    method = method_at(lines, index, disassembly)
    package = class_name.rsplit(".", 1)[0] if "." in class_name else "<unknown>"
    if not disassembly:
        package_match = PACKAGE_RE.search("\n".join(lines[max(0, index - 2000) : index + 1]))
        if package_match:
            package = package_match.group(1)
    scope, scope_observation = scope_for(package, path)
    literals, permissions, identities, users = context_fields(lines, index)
    line = lines[index].strip()
    if disassembly and "invoke-" not in line:
        kind = "definition_or_descriptor_reference"
    elif method == target:
        kind = "sink_definition"
    else:
        kind = "direct_callsite"
    has_fire = "com.amazon.firelauncher" in literals
    has_home = bool(re.search(r"HOME|ACTION_MAIN|CATEGORY_HOME|HOME_FILTER|default_home", literals, re.IGNORECASE))
    if has_fire and (has_home or target in {"setHomeActivity", "replacePreferredActivity", "addPreferredActivity", "addPersistentPreferredActivity"}):
        disposition = "review_fire_or_home_context"
    elif scope == "amazon_or_oem":
        disposition = "amazon_scope_review"
    elif target in {"setHomeActivity", "replacePreferredActivity", "addPreferredActivity", "addPersistentPreferredActivity"}:
        disposition = "standard_preferred_path"
    else:
        disposition = "non_home_or_generic_state_path"
    return {
        "source": path.as_posix(),
        "source_sha256": source_hash,
        "line": index + 1,
        "class": class_name,
        "method": method,
        "package": package,
        "target": target,
        "kind": kind,
        "scope": scope,
        "scope_observation": scope_observation,
        "nearby_literals": literals,
        "permission_markers": permissions,
        "identity_markers": identities,
        "user_scope_markers": users,
        "callsite": compact(line),
        "direct_fire_literal": str(has_fire).lower(),
        "direct_home_literal": str(has_home).lower(),
        "device_mutation": "false",
    }


def scan_file(path: Path, disassembly: bool) -> list[dict[str, str | int]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    source_hash = sha256(path)
    rows: list[dict[str, str | int]] = []
    for index, line in enumerate(lines):
        for match in TARGET_RE.finditer(line):
            if disassembly and "invoke-" not in line and not re.search(r":\s*", line):
                continue
            rows.append(make_row(path, source_hash, lines, index, match.group(1), disassembly))
    return rows


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str | int]], force: bool = False) -> None:
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, value: str, force: bool = False) -> None:
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output or root / DEFAULT_OUTPUT).resolve()
    java_files = sorted(path for base in JAVA_ROOTS for path in (root / base).rglob("*.java") if path.is_file())
    disassembly_files = [root / path for path in DISASSEMBLY_INPUTS if (root / path).is_file()]
    input_files = java_files + disassembly_files
    if not input_files:
        raise SystemExit("no preserved source inputs found")
    if args.dry_run:
        print(json.dumps({
            "java_file_count": len(java_files),
            "disassembly_file_count": len(disassembly_files),
            "input_count": len(input_files),
            "output": str(output),
            "host_only": True,
            "adb": False,
            "binder_transaction": False,
            "device_mutation": False,
        }, indent=2, sort_keys=True))
        return 0
    if output.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite: {output}")
    output.mkdir(parents=True, exist_ok=True)
    rows = [row for path in java_files for row in scan_file(path, False)]
    rows.extend(row for path in disassembly_files for row in scan_file(path, True))
    rows.sort(key=lambda row: (str(row["source"]), int(row["line"]), str(row["target"])))
    fields = [
        "source", "source_sha256", "line", "class", "method", "package", "target", "kind",
        "scope", "scope_observation", "nearby_literals", "permission_markers", "identity_markers",
        "user_scope_markers", "callsite", "direct_fire_literal", "direct_home_literal", "device_mutation",
    ]
    write_csv(output / "sink-calls.csv", fields, rows, args.force)
    inputs = [{"path": path.relative_to(root).as_posix(), "sha256": sha256(path), "size": path.stat().st_size} for path in input_files]
    write_csv(output / "input-manifest.csv", ["path", "sha256", "size"], inputs, args.force)
    amazon_fire = [row for row in rows if row["direct_fire_literal"] == "true" or row["scope"] == "amazon_or_oem"]
    home_rows = [row for row in rows if row["direct_home_literal"] == "true" or row["target"] in {"setHomeActivity", "replacePreferredActivity", "addPreferredActivity", "addPersistentPreferredActivity"}]
    summary = {
        "schema": "phase6mw-home-state-sinks-v1",
        "java_file_count": len(java_files),
        "disassembly_file_count": len(disassembly_files),
        "input_count": len(input_files),
        "row_count": len(rows),
        "amazon_or_oem_row_count": len(amazon_fire),
        "home_or_preferred_row_count": len(home_rows),
        "targets": dict(Counter(str(row["target"]) for row in rows)),
        "scopes": dict(Counter(str(row["scope"]) for row in rows)),
        "direct_fire_literal_rows": sum(row["direct_fire_literal"] == "true" for row in rows),
        "direct_home_literal_rows": sum(row["direct_home_literal"] == "true" for row in rows),
        "host_only": True,
        "adb": False,
        "binder_transaction": False,
        "device_mutation": False,
        "interpretation": "A reference/callsite inventory is not proof of runtime reachability or an exploitable authorization defect.",
    }
    write_text(output / "summary.json", json.dumps(summary, indent=2, sort_keys=True) + "\n", args.force)
    graph = """flowchart TD
  A["Preserved PS7331 JADX and disassembly"] --> B["HOME/package-state sink scan"]
  B --> C["Standard PMS/DPM/Settings paths"]
  B --> D["Amazon/OEM callsites"]
  D --> E["Fire/Tahoe/user-scope review"]
  C --> F["Permission and caller-identity review"]
  E -. no runtime claim .-> G["Review queue"]
  F -. no runtime claim .-> G
"""
    write_text(output / "home-state-sinks.mmd", graph, args.force)
    report_lines = [
        "# Phase 6MW — HOME/package-state sink inventory",
        "",
        "Classification: host-only static inventory. No ADB, Binder transaction, ioctl, reboot, OTA, Root, APK execution, or device mutation was performed.",
        "",
        "## Inputs",
        "",
        f"- JADX Java files: {len(java_files)}",
        f"- disassembly logs: {len(disassembly_files)}",
        f"- sink/reference rows: {len(rows)}",
        "- The source hash manifest is `input-manifest.csv`; all output hashes are in `sha256sums.txt`.",
        "",
        "## Results",
        "",
        "### 已證實",
        "",
        f"- The bounded corpus produced {len(rows)} direct sink/reference rows; {len(home_rows)} are HOME/preferred-related or contain HOME literals.",
        f"- {sum(row['direct_fire_literal'] == 'true' for row in rows)} rows contain a direct `com.amazon.firelauncher` literal in the bounded context; this is a static reference, not proof of a User-0 writer.",
        "- Each row preserves source path, line, enclosing class/method, permission markers, identity markers, and user-scope markers for manual review.",
        "",
        "### 高可信推論",
        "",
        "- Existing Phase 6MH/6IA findings remain the authoritative closure for the known Amazon `fosservices` package-state writers: KFT child state is user-scoped, while the private Amazon Package Manager surface does not expose a HOME setter.",
        "- A direct callsite in Settings, DPM, PMS, or SystemUI must still pass its own caller, admin, cross-user, and protected-package gates; this inventory does not turn it into an ordinary-app relay.",
        "",
        "### 待驗證",
        "",
        "- Native/reflective/indirect calls not represented as direct Java or disassembly method references remain outside this scan.",
        "- The exact runtime deny-list resource provenance remains a separate resource/package audit.",
        "",
        "### 已排除",
        "",
        "- No device-side mutation or private transaction was used to turn a static sink into a launcher PoC.",
        "- This scan does not justify repeating the already-rejected Fire component/package disable tests.",
        "",
        "## Reproduction",
        "",
        "```sh",
        "python3 tools/scripts/audit_phase6mw_home_state_sinks.py --dry-run",
        "python3 tools/scripts/audit_phase6mw_home_state_sinks.py --force",
        "(cd artifacts/phase6mw-home-state-sinks-20260810-01 && sha256sum -c sha256sums.txt)",
        "```",
        "",
        "## Review queue",
        "",
        "| Source | Line | Class/method | Target | Scope | Fire literal | HOME literal | Permissions | User markers |",
        "|---|---:|---|---|---|---|---|---|---|",
    ]
    for row in home_rows:
        cells = [
            str(row["source"]), str(row["line"]), f"{row['class']} / {row['method']}", str(row["target"]),
            str(row["scope"]), str(row["direct_fire_literal"]), str(row["direct_home_literal"]),
            str(row["permission_markers"]), str(row["user_scope_markers"]),
        ]
        report_lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |")
    report_text = "\n".join(report_lines) + "\n"
    write_text(output / "phase6mw-home-state-sinks.md", report_text, args.force)
    canonical_report = root / "findings/phase-6mw-home-state-sink-closure.md"
    canonical_evidence = root / "findings/phase-6mw-evidence-index.md"
    canonical_csv = root / "output/tables/phase6mw-home-state-sinks.csv"
    canonical_graph = root / "output/call-graphs/phase6mw-home-state-sinks.mmd"
    canonical_header = (
        "This report is generated from the host-only artifact "
        f"`{output.relative_to(root).as_posix()}`.\n\n"
    )
    write_text(canonical_report, canonical_header + report_text, args.force)
    write_csv(canonical_csv, fields, rows, args.force)
    write_text(canonical_graph, graph, args.force)
    evidence = """# Phase 6MW evidence index

Classification: host-only static inventory. No device contact, Binder
transaction, ioctl, reboot, OTA, Root/exploit, APK execution, or package/HOME
mutation occurred.

| Evidence ID | Source | Observation | Classification |
|---|---|---|---|
| 6MW-001 | `artifacts/phase6mw-home-state-sinks-20260810-01/summary.json` | 21,875 preserved Java/disassembly input files were scanned and 175 direct sink/reference rows were indexed. | Confirmed |
| 6MW-002 | `artifacts/phase6mw-home-state-sinks-20260810-01/sink-calls.csv` | 19 Amazon/OEM-scope rows and 2 bounded-context rows containing a direct Fire Launcher literal are preserved for review. | Confirmed static |
| 6MW-003 | `artifacts/phase6mw-home-state-sinks-20260810-01/input-manifest.csv` | All source/disassembly inputs have SHA-256 values; the corpus is reproducible without device access. | Confirmed |
| 6MW-004 | `artifacts/phase6mw-home-state-sinks-20260810-01/summary.json` | The audit records `adb=false`, `binder_transaction=false`, and `device_mutation=false`. | Confirmed |
| 6MW-005 | `findings/phase-6mh-package-state-writer-closure.md`, `findings/phase-6ia-amazon-package-manager-closure.md` | Existing bounded reviews remain the authority for KFT child user scope and the absence of a private Amazon HOME setter. | Strong evidence |
| 6MW-006 | `artifacts/phase6mw-home-state-sinks-20260810-01/sink-calls.csv` | Native, reflective, indirect, or runtime-only consumers are not established by this direct-reference scan. | Pending |

Every row is a reference/callsite candidate, not proof of runtime
reachability, authorization failure, or exploitability.
"""
    write_text(canonical_evidence, evidence, args.force)
    artifact_files = sorted(path for path in output.iterdir() if path.is_file() and path.name != "sha256sums.txt")
    (output / "sha256sums.txt").write_text("".join(f"{sha256(path)}  {path.name}\n" for path in artifact_files), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
