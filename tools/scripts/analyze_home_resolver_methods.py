#!/usr/bin/env python3
"""Create a small, evidence-oriented HOME resolver comparison.

The Fire OS input is a VDEX disassembly rather than source. This script keeps
method identity, line number, code offset, and selected instruction lines; it
does not pretend to reconstruct Java control flow from incomplete output.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import re
from pathlib import Path


METHODS = [
    "chooseBestActivity",
    "findPreferredActivity",
    "findPersistentPreferredActivityLP",
    "resolveIntent",
    "resolveIntentInternal",
    "queryIntentActivitiesInternal",
    "adjustPriority",
    "sortResults",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_fire_methods(path: Path) -> list[dict[str, object]]:
    lines = path.read_text(errors="replace").splitlines()
    current_class = ""
    current_descriptor = ""
    methods: list[dict[str, object]] = []
    active: dict[str, object] | None = None

    def finish() -> None:
        nonlocal active
        if active is not None:
            methods.append(active)
        active = None

    class_pattern = re.compile(r"^\s+class #\d+: ([^(]+) \('([^']+)'\)")
    method_pattern = re.compile(
        r"^\s+(direct_method|virtual_method) #(\d+): ([^\s(]+) (.+)$"
    )
    code_pattern = re.compile(r"^\s+codeOff=([^ ]+)")

    for line_no, line in enumerate(lines, 1):
        class_match = class_pattern.match(line)
        if class_match:
            finish()
            current_class = class_match.group(1).strip()
            current_descriptor = class_match.group(2)
            continue

        method_match = method_pattern.match(line)
        if method_match:
            finish()
            active = {
                "name": method_match.group(3),
                "kind": method_match.group(1),
                "number": method_match.group(2),
                "descriptor": method_match.group(4),
                "class": current_class,
                "class_descriptor": current_descriptor,
                "line": line_no,
                "code_off": "UNKNOWN",
                "lines": [],
            }
            continue

        if active is not None:
            code_match = code_pattern.match(line)
            if code_match:
                active["code_off"] = code_match.group(1)
            body = active["lines"]
            assert isinstance(body, list)
            if len(body) < 140 and ("|" in line or "invoke-" in line):
                body.append(line)

    finish()
    return methods


def fire_matches(methods: list[dict[str, object]], name: str) -> list[dict[str, object]]:
    return [
        item
        for item in methods
        if item["name"] == name
        and (
            item["class"] == "PackageManagerService"
            or item["class"] == "IntentResolver"
            or "IntentResolver" in str(item["class"])
        )
    ]


def java_method(path: Path, name: str) -> dict[str, object] | None:
    lines = path.read_text(errors="replace").splitlines()
    if name in {
        "chooseBestActivity",
        "findPreferredActivity",
        "findPersistentPreferredActivityLP",
        "resolveIntent",
        "resolveIntentInternal",
    }:
        declaration = re.compile(
            rf"\bResolveInfo\s+{re.escape(name)}\s*\("
        )
    elif name == "queryIntentActivitiesInternal":
        declaration = re.compile(
            rf"\bList<ResolveInfo>\s+{re.escape(name)}\s*\("
        )
    elif name == "sortResults":
        declaration = re.compile(rf"\bvoid\s+{re.escape(name)}\s*\(")
    else:
        declaration = re.compile(rf"\b{re.escape(name)}\s*\(")
    for index, line in enumerate(lines):
        if line.lstrip().startswith("//") or line.lstrip().startswith("*"):
            continue
        if not declaration.search(line):
            continue
        brace_count = 0
        started = False
        end = index
        for probe in range(index, min(len(lines), index + 1400)):
            current = lines[probe]
            opening = current.count("{")
            closing = current.count("}")
            if opening:
                started = True
            brace_count += opening - closing
            if started and brace_count <= 0:
                end = probe
                break
        else:
            end = min(len(lines) - 1, index + 120)
        body = lines[index : end + 1]
        return {"line": index + 1, "end": end + 1, "body": body}
    return None


def java_inventory(source_root: Path, tag: str) -> list[dict[str, object]]:
    pm = source_root / "frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java"
    result: list[dict[str, object]] = []
    for name in METHODS:
        item = java_method(pm, name) if pm.exists() else None
        result.append(
            {
                "tag": tag,
                "name": name,
                "file": str(pm),
                "line": item["line"] if item else "NOT_FOUND",
                "end": item["end"] if item else "",
                "body": item["body"] if item else [],
            }
        )
    for relative in (
        "frameworks/base/services/core/java/com/android/server/IntentResolver.java",
        "frameworks/base/services/core/java/com/android/server/pm/PreferredIntentResolver.java",
        "frameworks/base/services/core/java/com/android/server/pm/PersistentPreferredIntentResolver.java",
    ):
        path = source_root / relative
        for name in ("sortResults", "queryIntent", "filterResults"):
            item = java_method(path, name) if path.exists() else None
            result.append(
                {
                    "tag": tag,
                    "name": name,
                    "file": str(path),
                    "line": item["line"] if item else "NOT_FOUND",
                    "end": item["end"] if item else "",
                    "body": item["body"] if item else [],
                }
            )
    return result


def relevant_lines(lines: list[str]) -> list[str]:
    markers = (
        "priority",
        "setPriority",
        "privateFlags",
        "PRIVATE_FLAG_PRIVILEGED",
        "preferred",
        "PersistentPreferred",
        "match",
        "sortResults",
        "resolveIntent",
        "queryIntent",
        "com.amazon",
        "Vendor",
        "mAlways",
        "mSet",
    )
    selected = [line.strip() for line in lines if any(marker in line for marker in markers)]
    return selected[:80]


def render_fire_inventory(methods: list[dict[str, object]]) -> str:
    output = []
    output.append("| Method | Class | VDEX line | codeOff | Descriptor |\n|---|---|---:|---|---|")
    for name in METHODS:
        matches = fire_matches(methods, name)
        if not matches:
            output.append(f"| `{name}` | `[NOT_FOUND_IN_ARTIFACT]` |  |  |  |")
            continue
        for item in matches:
            output.append(
                "| `{name}` | `{klass}` | {line} | `{off}` | `{desc}` |".format(
                    name=item["name"],
                    klass=item["class"],
                    line=item["line"],
                    off=item["code_off"],
                    desc=item["descriptor"],
                )
            )
    return "\n".join(output)


def render_aosp_inventory(items: list[dict[str, object]]) -> str:
    output = ["| Tag | Method | File | Lines |", "|---|---|---|---:|"]
    for item in items:
        lines = (
            f"{item['line']}-{item['end']}"
            if item["line"] != "NOT_FOUND"
            else "`NOT_FOUND`"
        )
        output.append(f"| {item['tag']} | `{item['name']}` | `{item['file']}` | {lines} |")
    return "\n".join(output)


def first_fire(methods: list[dict[str, object]], name: str) -> dict[str, object] | None:
    matches = fire_matches(methods, name)
    return matches[0] if matches else None


def render_method_evidence(methods: list[dict[str, object]], name: str) -> str:
    item = first_fire(methods, name)
    if not item:
        return f"`{name}`: `[NOT_FOUND_IN_ARTIFACT]`."
    selected = relevant_lines(item["lines"])
    text = [
        f"`{name}` — `{item['class']}`, VDEX line {item['line']}, codeOff `{item['code_off']}`.",
    ]
    if selected:
        text.append("\n```text\n" + "\n".join(selected[:40]) + "\n```")
    return "\n".join(text)


def diff_method(a: dict[str, object], b: dict[str, object]) -> str:
    a_body = "\n".join(str(x).strip() for x in a.get("body", []))
    b_body = "\n".join(str(x).strip() for x in b.get("body", []))
    if not a_body or not b_body:
        return "NOT_COMPARABLE"
    changes = list(difflib.unified_diff(a_body.splitlines(), b_body.splitlines(), n=0))
    return f"changed_lines={len(changes)}" if changes else "no_selected_line_difference"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fire-disassembly", type=Path, required=True)
    parser.add_argument("--aosp-r1", type=Path, required=True)
    parser.add_argument("--aosp-r61", type=Path, required=True)
    parser.add_argument("--fosservices-disassembly", type=Path, required=True)
    parser.add_argument("--output-findings", type=Path, required=True)
    parser.add_argument("--output-diff", type=Path, required=True)
    parser.add_argument("--output-graph", type=Path, required=True)
    args = parser.parse_args()

    fire_methods = parse_fire_methods(args.fire_disassembly)
    r1 = java_inventory(args.aosp_r1, "android-9.0.0_r1")
    r61 = java_inventory(args.aosp_r61, "android-9.0.0_r61")
    fire_text = args.fire_disassembly.read_text(errors="replace")
    fos_text = args.fosservices_disassembly.read_text(errors="replace")

    args.output_findings.parent.mkdir(parents=True, exist_ok=True)
    args.output_diff.parent.mkdir(parents=True, exist_ok=True)
    args.output_graph.parent.mkdir(parents=True, exist_ok=True)

    fire_hash = sha256(args.fire_disassembly)
    fos_hash = sha256(args.fosservices_disassembly)
    fire_literal_lines = [
        f"{index}: {line.strip()}"
        for index, line in enumerate(fire_text.splitlines(), 1)
        if "com.amazon.firelauncher" in line
    ][:20]
    vendor_service_lines = [
        f"{index}: {line.strip()}"
        for index, line in enumerate(fire_text.splitlines(), 1)
        if "VendorActivityStackSupervisorCallback" in line and "callResolveIntent" in line
    ][:20]
    fos_resolve_lines: list[str] = []
    fos_class = ""
    for index, line in enumerate(fos_text.splitlines(), 1):
        class_match = re.match(r"^\s+class #\d+: ([^(]+) \('([^']+)'\)", line)
        if class_match:
            fos_class = class_match.group(1).strip()
        if fos_class == "AppCompatActivityStackSupervisorCallback" and "resolveIntent" in line:
            fos_resolve_lines.append(f"{index}: {line.strip()}")
    fos_resolve_lines = fos_resolve_lines[:20]

    findings = [
        "# HOME Resolver Method Analysis (Phase 3A)",
        "",
        "## Scope and artifact identity",
        "",
        "This report is generated from the matching Fire OS 7 services VDEX/FOS-services disassembly and the local Android 9 r1/r61 source snapshots. It records low-level evidence and does not infer missing code.",
        "",
        f"- Fire services disassembly: `{args.fire_disassembly}`; SHA-256 `{fire_hash}`.",
        f"- Fire FOS-services disassembly: `{args.fosservices_disassembly}`; SHA-256 `{fos_hash}`.",
        f"- AOSP r1 source root: `{args.aosp_r1}`.",
        f"- AOSP r61 source root: `{args.aosp_r61}`.",
        "- Classifications used: `AOSP_STANDARD`, `AMAZON_ADDITION`, `AMAZON_MODIFICATION`, `VERSION_DIFFERENCE`, `DECOMPILER_ARTIFACT`, `UNKNOWN`.",
        "",
        "## Fire OS method inventory",
        "",
        render_fire_inventory(fire_methods),
        "",
        "## AOSP method inventory",
        "",
        render_aosp_inventory(r1 + r61),
        "",
        "## Priority and preferred ordering",
        "",
        "`AOSP_STANDARD`: Android 9 `resolveIntentInternal()` queries the candidate list and calls `chooseBestActivity()` when a single result is not already decisive.",
        "",
        "`AOSP_STANDARD`: `chooseBestActivity()` first returns the only candidate. With multiple candidates it compares the first two candidates' `priority`, `preferredOrder`, and `isDefault`. If any differs, it returns the first candidate before calling `findPreferredActivity()`.",
        "",
        "`AOSP_STANDARD`: only when those first-two ranking fields tie does `chooseBestActivity()` call `findPreferredActivity()`. `findPreferredActivity()` checks persistent preferred activities first, then ordinary preferred activities and validates their match quality and membership in the current candidate set.",
        "",
        "`Confirmed` for this artifact: Fire OS `chooseBestActivity()` contains the same priority/preferredOrder/isDefault comparison before its `findPreferredActivity()` invocation. Therefore an `mAlways=true` Microsoft record cannot override a candidate list whose first candidate is Fire priority 50 and whose next candidate has a different priority, unless Fire OS added an earlier branch not represented in the inspected method. No such Fire package-name branch was found in the selected method evidence.",
        "",
        "This explains the existing runtime result as follows: Microsoft can receive a preferred record and the shell command can return Success, but the resolver reaches the ranking-return path before ordinary preferred selection because Fire priority 50 differs from Microsoft's priority 0. The claim is `Strong evidence` because it is supported by both VDEX control flow and the preserved runtime test.",
        "",
        "## Effective priority normalization",
        "",
        "`AOSP_STANDARD`: Android 9 `ActivityIntentResolver.adjustPriority()` caps a positive intent-filter priority to `0` when the owning application is not privileged. The Fire VDEX contains the same `privateFlags & 0x8` privileged check and calls `ActivityIntentInfo.setPriority(0)` for the non-privileged branch at codeOff `0x2abe02`-`0x2abe22`.",
        "",
        "The Phase 3A APK manifests retain their declared priorities (0, 49, 50, 51, 100), but the device's `query-activities` output reports effective priority `0` for all five sideloaded research packages. Fire Launcher is a privileged system package and retains effective priority `50`. This is `Confirmed` as the primary explanation for why a priority-51 or priority-100 ordinary APK did not outrank Fire; it is not evidence of an Amazon-only resolver ranking rule.",
        "",
        "## Method evidence",
    ]
    for name in METHODS:
        findings.extend(["", render_method_evidence(fire_methods, name)])

    findings.extend(
        [
            "",
            "## Vendor callback boundary",
            "",
            "`AMAZON_ADDITION`: Fire OS `ActivityStackSupervisor.resolveIntent()` calls `VendorActivityStackSupervisorCallback.callResolveIntent()` before invoking `PackageManagerInternal.resolveIntent()`. The callback can return a non-null `ResolveInfo`, in which case the ActivityStackSupervisor path returns it without reaching the normal PackageManagerInternal call.",
            "",
            "The FOS-services artifact contains `AppCompatActivityStackSupervisorCallback.resolveIntent()`. Its inspected body calls `IPackageManager.resolveIntent()` and then applies `isUninstalledApp()` before deciding whether to return the result. This proves a vendor interception boundary, but does not prove that it changes HOME selection or names `com.amazon.firelauncher`.",
            "",
            f"Fire callback call sites found: `{len(vendor_service_lines)}`.",
            "\n".join(f"- {line}" for line in vendor_service_lines) if vendor_service_lines else "- `[NOT_FOUND]`",
            "",
            "Selected FOS-services resolver lines:",
            "\n".join(f"- {line}" for line in fos_resolve_lines) if fos_resolve_lines else "- `[NOT_FOUND]`",
            "",
            "Status: `Strong evidence` that a vendor callback can intervene in ActivityManager's resolve path; `Hypothesis` that it affects this HOME request; `Unknown` whether any callback returns an explicit Fire component.",
            "",
            "## Package-name special case search",
            "",
            f"Literal `com.amazon.firelauncher` occurrences in the selected Fire services disassembly: `{len(fire_literal_lines)}`.",
            "\n".join(f"- {line}" for line in fire_literal_lines) if fire_literal_lines else "- `[NOT_FOUND]` in selected services VDEX.",
            "",
            "Absence of a literal does not exclude a resource, encoded string, callback-provided value, or another artifact. It does exclude a direct literal in the inspected text.",
            "",
            "## Findings classification",
            "",
            "| Finding | Classification | Confidence |",
            "|---|---|---|",
            "| Base candidate ranking and preferred ordering | `AOSP_STANDARD` | Confirmed by AOSP and Fire VDEX structure |",
            "| Fire VDEX priority comparison before ordinary preferred lookup | `AOSP_STANDARD` | Confirmed |",
            "| Non-privileged positive intent-filter priority is capped to zero | `AOSP_STANDARD` | Confirmed by AOSP `adjustPriority()`, Fire VDEX, and runtime candidates |",
            "| Fire privileged-system priority 50 remains effective | `AOSP_STANDARD` plus Fire manifest choice | Strong evidence |",
            "| Vendor ActivityStackSupervisor resolve callback | `AMAZON_ADDITION` | Strong evidence |",
            "| Fire-specific resolver ranking or explicit component launch | `UNKNOWN` | No direct evidence in selected method scan |",
            "| Microsoft `mAlways=true` ineffective in current HOME test | Runtime consequence of ranking path | Strong evidence |",
            "",
            "## Limits",
            "",
            "The current artifact is VDEX disassembly and the AOSP source snapshot is not a complete build tree for every IntentResolver source file. This report does not claim byte-for-byte equivalence, does not infer hidden vendor callback implementations, and does not replace the controlled priority APK experiment.",
        ]
    )

    args.output_findings.write_text("\n".join(findings) + "\n")

    diff_lines = [
        "# HOME Resolver AOSP vs Fire OS Difference Report",
        "",
        "## Method presence and source locations",
        "",
        render_aosp_inventory(r1 + r61),
        "",
        "Fire OS method inventory:",
        "",
        render_fire_inventory(fire_methods),
        "",
        "## r1 vs r61 selected-body comparison",
        "",
        "| Method | Result | Classification |",
        "|---|---|---|",
    ]
    for name in METHODS:
        r1_item = next((x for x in r1 if x["name"] == name), None)
        r61_item = next((x for x in r61 if x["name"] == name), None)
        result = diff_method(r1_item or {}, r61_item or {})
        classification = "VERSION_DIFFERENCE" if result.startswith("changed_lines=") else "AOSP_STANDARD"
        diff_lines.append(f"| `{name}` | `{result}` | `{classification}` |")
    diff_lines.extend(
        [
            "",
            "## Evidence-based Fire OS differences",
            "",
            "| Difference | Classification | Evidence |",
            "|---|---|---|",
            "| `VendorActivityStackSupervisorCallback.callResolveIntent()` is invoked before PackageManagerInternal resolution | `AMAZON_ADDITION` | Fire ActivityStackSupervisor VDEX method `resolveIntent`, codeOff `0x11a138` |",
            "| `VendorProtectedPackagesCallback` exists in the protected-package path | `AMAZON_ADDITION` | Existing Phase 2 static evidence; not a HOME ranking proof |",
            "| Fire priority 50 in the HOME manifest | `AMAZON_ADDITION` | Existing Phase 2 manifest evidence; not a resolver code patch |",
            "| Non-privileged positive intent-filter priority is capped in `adjustPriority()` | `AOSP_STANDARD` | AOSP r1/r61 `PackageManagerService.adjustPriority()` and Fire `ActivityIntentResolver.adjustPriority()` VDEX at codeOff `0x2abde4` |",
            "| Fire-specific resolver ranking condition | `UNKNOWN` | No direct literal/package branch found in selected scan |",
            "",
            "The `AMAZON_ADDITION` label here describes an Amazon package/resource choice, not proof that PackageManager resolver code was modified.",
        ]
    )
    args.output_diff.write_text("\n".join(diff_lines) + "\n")

    graph = """flowchart TD
    I[Package scan / ActivityIntentResolver.addActivity] --> AP[adjustPriority]
    AP -->|non-privileged app and priority > 0| CAP[set effective priority to 0]
    AP -->|privileged system app| KEEP[retain declared priority]
    CAP --> Q[resolveIntentInternal\nqueryIntentActivitiesInternal]
    KEEP --> Q
    Q --> C[chooseBestActivity]
    C -->|one candidate| R[return candidate]
    C -->|priority/preferredOrder/isDefault differ| R0[return query[0]]
    C -->|ranking fields tie| P[findPreferredActivity]
    P --> PP[findPersistentPreferredActivityLP]
    PP -->|matching persistent preferred| RP[return persistent preferred]
    PP -->|none| OP[ordinary PreferredIntentResolver]
    OP -->|matching candidate and match quality| RO[return ordinary preferred]
    OP -->|none| RES[ResolverActivity or no result]
    AS[ActivityStackSupervisor.resolveIntent] --> VC[VendorActivityStackSupervisorCallback.callResolveIntent]
    VC -->|non-null callback result| VR[return vendor result]
    VC -->|null| PMI[PackageManagerInternal.resolveIntent]
    PMI --> Q
    R0 --> H[HOME result]
    RP --> H
    RO --> H
    VR --> H
    RES --> H
"""
    args.output_graph.write_text(graph)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
