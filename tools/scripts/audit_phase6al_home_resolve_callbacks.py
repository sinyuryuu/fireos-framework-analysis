#!/usr/bin/env python3
"""Close the Android 9 HOME pre-resolution callback set, host-only.

The audit reads preserved PS7331 disassembly, fosinit registrations, and a
saved HOME snapshot.  It never contacts ADB, obtains a Binder handle, sends a
transaction, starts an activity, or mutates device state.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SERVICES_REL = Path("decompiled/baksmali/vdexExtractor/services/disassembly.log")
FOS_REL = Path("decompiled/baksmali/vdexExtractor/fosservices/disassembly.log")
REGISTRATION_ROOT = ROOT / "artifacts/amazon-services"
HOME_REL = Path("artifacts/phase6k/readonly-device-20260805-01/home_resolve.stdout.txt")
CANDIDATES_REL = Path("artifacts/phase6k/readonly-device-20260805-01/home_candidates.stdout.txt")

SERVICES_SHA256 = "373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53"
FOS_SHA256 = "ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c"

CSV_FIELDS = [
    "evidence_id",
    "surface",
    "class_or_registration",
    "method_or_file",
    "source_lines",
    "source_sha256",
    "control_flow",
    "home_effect",
    "fire_literal",
    "live_observation",
    "classification",
    "confidence",
    "conclusion",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, value: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def line_range(text: str, start_marker: str, end_marker: str | None = None) -> tuple[str, str]:
    lines = text.splitlines()
    starts = [index for index, line in enumerate(lines) if start_marker in line]
    if len(starts) != 1:
        raise ValueError(f"expected one {start_marker!r}, got {len(starts)}")
    start = starts[0]
    end = len(lines)
    if end_marker:
        ends = [index for index in range(start + 1, len(lines)) if end_marker in lines[index]]
        if len(ends) != 1:
            raise ValueError(f"expected one end {end_marker!r}, got {len(ends)}")
        end = ends[0]
    else:
        for index in range(start + 1, len(lines)):
            if lines[index].startswith("   virtual_method ") or lines[index].startswith("   direct_method ") or lines[index].startswith("  class #"):
                end = index
                break
    return "\n".join(lines[start:end]) + "\n", f"{start + 1}-{end}"


def class_block(text: str, marker: str) -> tuple[str, str]:
    return line_range(text, marker, None)


def method_block(text: str, marker: str) -> tuple[str, str]:
    return line_range(text, marker, None)


def registrations() -> list[dict[str, str]]:
    pattern = re.compile(
        r'<callback\b[^>]*base="com\.android\.server\.am\.VendorActivityStackSupervisorCallback"'
        r'[^>]*impl="([^"]+)"[^>]*/>',
        re.DOTALL,
    )
    found: list[dict[str, str]] = []
    for path in sorted(REGISTRATION_ROOT.glob("*.xml")):
        content = read(path)
        for implementation in pattern.findall(content):
            found.append({"implementation": implementation, "file": str(path.relative_to(ROOT))})
    if sorted(item["implementation"] for item in found) != sorted([
        "com.amazon.android.server.am.AppCompatActivityStackSupervisorCallback",
        "com.fireos.eve.EveActivityStackSupervisorCallback",
    ]):
        raise ValueError(f"unexpected callback registration set: {found}")
    return found


def graph() -> str:
    return """flowchart TD
  A[Home key / ActivityStarter] --> B[ActivityStackSupervisor.resolveIntent]
  B --> C[VendorActivityStackSupervisorCallback.callResolveIntent]
  C --> D[AppCompatActivityStackSupervisorCallback.resolveIntent]
  D --> E[IPackageManager.resolveIntent]
  E --> F{ResolveInfo is installed?}
  F -->|yes| G[return ResolveInfo to dispatcher]
  F -->|no/error| H[return null]
  C --> I[EveActivityStackSupervisorCallback]
  I --> J[base resolveIntent returns null]
  H --> I
  J --> K[ActivityStackSupervisor fallback]
  K --> L[PackageManagerInternal.resolveIntent]
  G --> M[chosen result continues; no Fire component injected]
  L --> N[standard Android resolver result]
"""


def markdown_graph(graph_text: str) -> str:
    return "# Phase 6AL HOME callback graph\n\n```mermaid\n" + graph_text + "```\n\n" + graph_text


def build_rows(inputs: dict[Path, str], regs: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, str]]:
    services = read(ROOT / SERVICES_REL)
    fos = read(ROOT / FOS_REL)

    base_dispatch, base_lines = method_block(services, "direct_method #22969: callResolveIntent")
    base_resolve, base_resolve_lines = method_block(services, "virtual_method #22973: resolveIntent")
    supervisor, supervisor_lines = method_block(services, "virtual_method #20996: resolveIntent")
    appcompat, appcompat_lines = method_block(fos, "virtual_method #5024: resolveIntent")
    appcompat_helper, appcompat_helper_lines = method_block(fos, "direct_method #5023: isUninstalledApp")
    eve_class, eve_class_lines = class_block(fos, "class #1483: EveActivityStackSupervisorCallback")

    if "if-eqz v3" not in base_dispatch or "return-object v3" not in base_dispatch:
        raise ValueError("callback dispatcher first-non-null markers missing")
    if "const/4 v0, #int 0" not in base_resolve or "return-object v0" not in base_resolve:
        raise ValueError("base callback null-return markers missing")
    if "VendorActivityStackSupervisorCallback;.callResolveIntent" not in supervisor:
        raise ValueError("ActivityStackSupervisor callback call-site missing")
    if "PackageManagerInternal;.resolveIntent" not in supervisor:
        raise ValueError("ActivityStackSupervisor PM fallback missing")
    if "IPackageManager;.resolveIntent" not in appcompat:
        raise ValueError("AppCompat PM delegation missing")
    if "LauncherHijackPreventer" in appcompat or "com.amazon.firelauncher" in appcompat:
        raise ValueError("unexpected Fire literal in AppCompat resolveIntent block")
    if "resolveIntent" in eve_class:
        # The class may contain the string in a source descriptor in a future
        # build; the method declaration itself is the relevant signal.
        if re.search(r"\n\s+virtual_method [^\n]*: resolveIntent ", eve_class):
            raise ValueError("Eve unexpectedly overrides resolveIntent")

    rows = [
        {
            "evidence_id": "6AL-CB-001",
            "surface": "framework_dispatcher",
            "class_or_registration": "VendorActivityStackSupervisorCallback",
            "method_or_file": "callResolveIntent",
            "source_lines": base_lines,
            "source_sha256": sha256(ROOT / SERVICES_REL),
            "control_flow": "iterate callback array; return the first non-null ResolveInfo; otherwise return null",
            "home_effect": "OEM callbacks can preempt the normal ActivityStackSupervisor fallback only by returning a ResolveInfo",
            "fire_literal": "not present in dispatcher block",
            "live_observation": "saved HOME resolver is Fire priority 50; no callback transaction was executed",
            "classification": "CALLBACK_DISPATCH_CONFIRMED",
            "confidence": "Confirmed",
            "conclusion": "The callback hook is real and first-non-null, but the dispatcher itself does not choose Fire.",
        },
        {
            "evidence_id": "6AL-CB-002",
            "surface": "framework_fallback",
            "class_or_registration": "ActivityStackSupervisor",
            "method_or_file": "resolveIntent(Intent,String,int,int,int)",
            "source_lines": supervisor_lines,
            "source_sha256": sha256(ROOT / SERVICES_REL),
            "control_flow": "call callback dispatcher; return callback result when non-null; otherwise call PackageManagerInternal.resolveIntent",
            "home_effect": "Home-key ActivityTaskManager path has a pre-PM hook, then AOSP-shaped PM fallback",
            "fire_literal": "not present in method block",
            "live_observation": "saved keyevent and explicit HOME both ended at com.amazon.firelauncher/.Launcher",
            "classification": "AOSP_SHAPED_PRE_RESOLUTION",
            "confidence": "Confirmed",
            "conclusion": "The framework does not hardcode Fire in the inspected ActivityStackSupervisor method.",
        },
        {
            "evidence_id": "6AL-CB-003",
            "surface": "registered_callback",
            "class_or_registration": "com.amazon.android.server.am.AppCompatActivityStackSupervisorCallback",
            "method_or_file": "resolveIntent",
            "source_lines": appcompat_lines,
            "source_sha256": sha256(ROOT / FOS_REL),
            "control_flow": "calls IPackageManager.resolveIntent with added match flags; filters only an uninstalled ResolveInfo; returns the PM result or null on error",
            "home_effect": "Can preempt the later fallback with a PM-produced ResolveInfo; no component/package replacement is visible",
            "fire_literal": "absent from exact method block",
            "live_observation": "no live callback return object was captured",
            "classification": "DELEGATING_CALLBACK",
            "confidence": "Strong evidence",
            "conclusion": "AppCompat is a PM-delegating callback, not an observed Fire Launcher selector.",
        },
        {
            "evidence_id": "6AL-CB-004",
            "surface": "registered_callback",
            "class_or_registration": "com.fireos.eve.EveActivityStackSupervisorCallback",
            "method_or_file": "class block; no resolveIntent override",
            "source_lines": eve_class_lines,
            "source_sha256": sha256(ROOT / FOS_REL),
            "control_flow": "overrides lifecycle telemetry callOnRestartActivity; inherits base resolveIntent returning null",
            "home_effect": "does not supply a ResolveInfo to the dispatcher in the inspected class",
            "fire_literal": "no resolveIntent implementation or Fire literal in class block",
            "live_observation": "no live callback return object was captured",
            "classification": "NO_RESOLVE_OVERRIDE",
            "confidence": "Confirmed",
            "conclusion": "Eve is registered for this callback type but does not override resolveIntent in PS7331.",
        },
        {
            "evidence_id": "6AL-CB-005",
            "surface": "base_callback",
            "class_or_registration": "VendorActivityStackSupervisorCallback",
            "method_or_file": "resolveIntent",
            "source_lines": base_resolve_lines,
            "source_sha256": sha256(ROOT / SERVICES_REL),
            "control_flow": "returns null",
            "home_effect": "unimplemented callbacks fall through to PackageManagerInternal",
            "fire_literal": "not present",
            "live_observation": "not directly invoked; preserved as static input",
            "classification": "BASE_NULL_FALLTHROUGH",
            "confidence": "Confirmed",
            "conclusion": "The base callback cannot itself replace the HOME result.",
        },
        {
            "evidence_id": "6AL-CB-006",
            "surface": "registration",
            "class_or_registration": "fosinit callback registrations",
            "method_or_file": "appcompatsupport_fosinit.xml; eve_launch_time_fosinit.xml",
            "source_lines": "; ".join(item["file"] for item in regs),
            "source_sha256": "; ".join(f"{item['file']}={sha256(ROOT / item['file'])}" for item in regs),
            "control_flow": "two concrete registrations for VendorActivityStackSupervisorCallback were found in the preserved Amazon registration scope",
            "home_effect": "defines the callback set used by findCallbacks()",
            "fire_literal": "not in registration files",
            "live_observation": "saved fosdebug inventory lists AppCompat/Eve callback families; no mutation was requested",
            "classification": "REGISTRATION_SET_CLOSED_BOUNDED_SCOPE",
            "confidence": "Strong evidence",
            "conclusion": "Within the preserved fosinit scope, AppCompat and Eve are the only concrete registrations for this callback base.",
        },
        {
            "evidence_id": "6AL-CB-007",
            "surface": "callback_scope",
            "class_or_registration": "AppCompat + Eve + framework dispatcher",
            "method_or_file": "combined static control-flow review",
            "source_lines": f"services:{base_lines},{supervisor_lines}; fosservices:{appcompat_lines},{eve_class_lines}",
            "source_sha256": f"services={sha256(ROOT / SERVICES_REL)}; fosservices={sha256(ROOT / FOS_REL)}",
            "control_flow": "AppCompat delegates to PM; Eve/base return null; fallback delegates to PM",
            "home_effect": "no inspected callback creates an explicit Fire Launcher component or bypasses PM ranking",
            "fire_literal": "none in inspected resolver callback blocks",
            "live_observation": "HOME result remains Fire; cause is candidate/resolver state outside this callback set",
            "classification": "NO_DIRECT_FIRE_OVERRIDE_FOUND",
            "confidence": "Strong evidence",
            "conclusion": "The preserved callback set does not explain Fire selection by direct component injection; it narrows the remaining control point to PM candidate/preferred state or an out-of-scope native/registration path.",
        },
    ]
    snippets = {
        "dispatcher": base_dispatch,
        "base_resolve": base_resolve,
        "activity_stack_supervisor": supervisor,
        "appcompat": appcompat,
        "appcompat_helper": appcompat_helper,
        "eve_class": eve_class,
    }
    return rows, snippets


def report(rows: list[dict[str, str]], inputs: dict[Path, str], regs: list[dict[str, str]], artifact: Path) -> tuple[str, str]:
    output_label = artifact.relative_to(ROOT) if artifact.is_relative_to(ROOT) else artifact
    table_lines = [
        "| Evidence ID | Surface | Control flow | HOME effect | Confidence |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        table_lines.append(
            f"| `{row['evidence_id']}` | `{row['surface']}` | {row['control_flow']} | {row['home_effect']} | **{row['confidence']}** |"
        )
    evidence_lines = [
        "# Phase 6AL evidence index — HOME resolve callback closure",
        "",
        "This index is generated from preserved PS7331 artifacts.  No ADB command,",
        "Binder lookup/transaction, activity start, settings write, package mutation,",
        "or reboot was performed.",
        "",
        *table_lines,
        "",
        "## Input hashes",
        "",
        "| Input | SHA-256 |",
        "|---|---|",
    ]
    for path, digest in inputs.items():
        evidence_lines.append(f"| `{path.relative_to(ROOT)}` | `{digest}` |")
    evidence_lines.extend([
        "",
        "## Registrations",
        "",
        "| Implementation | Registration file |",
        "|---|---|",
    ])
    for item in regs:
        evidence_lines.append(f"| `{item['implementation']}` | `{item['file']}` |")
    evidence = "\n".join(evidence_lines) + "\n"

    report_text = f"""# Phase 6AL — HOME pre-resolution callback closure

Generated: {datetime.now(timezone.utc).isoformat()}

## Scope and safety

This is a host-only, static control-flow audit of the PS7331 Android 9
`VendorActivityStackSupervisorCallback` path.  It reads the saved
`services`/`fosservices` disassembly, preserved Amazon `fosinit` registrations,
and the saved HOME resolver snapshot.  It does not call private services,
send Binder transactions, replay broadcasts, start activities, change package
or settings state, or contact the device.

## Executive result

### 已證實

1. `ActivityStackSupervisor.resolveIntent()` calls
   `VendorActivityStackSupervisorCallback.callResolveIntent()` first.  A
   non-null callback result is returned immediately; otherwise the method
   calls `PackageManagerInternal.resolveIntent()`.  Evidence: `6AL-CB-001`,
   `6AL-CB-002`.
2. The preserved `fosinit` scope contains exactly two registrations for this
   callback base: `AppCompatActivityStackSupervisorCallback` and
   `EveActivityStackSupervisorCallback`.  Evidence: `6AL-CB-006`.
3. AppCompat calls `IPackageManager.resolveIntent()` and filters an
   uninstalled result; its exact method block contains no
   `com.amazon.firelauncher` literal and no explicit component construction.
   Evidence: `6AL-CB-003`.
4. Eve does not override `resolveIntent()` in the preserved class block; it
   records lifecycle data through `callOnRestartActivity`, while the base
   implementation returns null.  Evidence: `6AL-CB-004`, `6AL-CB-005`.

### 高可信推論

- The inspected callback set is AOSP-shaped at the selection boundary: a
  callback may return a PM-produced `ResolveInfo`, but no inspected callback
  injects Fire as an explicit component.
- The live Fire result therefore remains best explained by the PM candidate /
  preferred state (privileged Fire candidate with effective priority 50) or by
  a callback/native path outside the preserved registration and method scope.

### 待驗證

- Whether an additional registration is loaded from an artifact outside the
  preserved `artifacts/amazon-services/*.xml` scope.
- Whether AppCompat's added match flags alter a particular HOME candidate set
  in an unobserved edge case; its method still delegates to PM rather than
  selecting a package directly.
- Runtime callback return values for a real Home-key event.  No instrumentation
  or private callback invocation was used; the saved end result is only the
  final resolver observation.

### 已排除／因風險拒絕

- **已排除於 inspected scope：** a direct literal `com.amazon.firelauncher`
  injection in the callback dispatcher, ActivityStackSupervisor method,
  AppCompat resolver method, or Eve callback class.
- **因風險拒絕：** unknown Binder calls, manual callback invocation,
  OOBE/OTA replay, package-state mutation, framework injection, root, or
  SELinux changes.

## Exact control flow

```text
Home key / ActivityStarter
  → ActivityStackSupervisor.resolveIntent
  → VendorActivityStackSupervisorCallback.callResolveIntent
  → AppCompat.resolveIntent
      → IPackageManager.resolveIntent
      → uninstalled-result filter
      → ResolveInfo or null
  → Eve.resolveIntent (inherited base null)
  → PackageManagerInternal.resolveIntent fallback
  → Activity start
```

The dispatcher is first-non-null, not first-callback-wins.  Because AppCompat
delegates to the PackageManager, a returned Fire result at that point would be
the PM's result, not proof that AppCompat selected Fire.

## Evidence table

{chr(10).join(table_lines)}

## Reproduction

```sh
python3 tools/scripts/audit_phase6al_home_resolve_callbacks.py --dry-run
python3 tools/scripts/audit_phase6al_home_resolve_callbacks.py \\
  --output {output_label}
```

The script is host-only and refuses to overwrite existing output.  It writes
method snippets, registration inventory, input hashes, CSV, Mermaid graph and
SHA-256 manifest.

## Decision

Phase 6AL closes the preserved Java/DEX callback set without finding a direct
Fire Launcher selector.  The remaining high-value question is not whether the
callback hook exists—it does—but whether the PM result it receives is altered
by candidate filtering, preferred-state validation, or an unpreserved native /
registration source.  No new ADB workaround or root path was established.
"""
    return report_text, evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/phase6al/home-resolve-callback-20260805-01"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-publish", action="store_true", help="write only the canonical artifact")
    args = parser.parse_args()

    paths = [ROOT / SERVICES_REL, ROOT / FOS_REL, ROOT / HOME_REL, ROOT / CANDIDATES_REL]
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")
    regs = registrations()
    if args.dry_run:
        print(json.dumps({
            "host_only": True,
            "device_contacted": False,
            "binder_transaction_sent": False,
            "registrations": regs,
            "inputs": [str(path.relative_to(ROOT)) for path in paths],
            "output": str(args.output),
        }, indent=2))
        return 0

    services = ROOT / SERVICES_REL
    fos = ROOT / FOS_REL
    if sha256(services) != SERVICES_SHA256 or sha256(fos) != FOS_SHA256:
        raise SystemExit("source hash does not match the PS7331 expected input")
    inputs = {path: sha256(path) for path in paths}
    rows, snippets = build_rows(inputs, regs)
    artifact = (ROOT / args.output) if not args.output.is_absolute() else args.output
    artifact.mkdir(parents=True, exist_ok=False)

    table_path = artifact / "home-resolve-callbacks.csv"
    with table_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    graph_text = graph()
    write_text(artifact / "home-resolve-callback.mmd", graph_text)
    write_text(artifact / "home-resolve-callback.md", markdown_graph(graph_text))
    for name, content in snippets.items():
        write_text(artifact / f"{name}.txt", content)
    write_json(artifact / "registrations.json", regs)
    summary = {
        "phase": "6AL",
        "title": "HOME pre-resolution callback closure",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "binder_transaction_sent": False,
        "package_or_settings_mutated": False,
        "registration_count": len(regs),
        "registration_implementations": [item["implementation"] for item in regs],
        "direct_fire_literal_in_inspected_resolver_blocks": False,
        "key_result": "Preserved callback set delegates to PackageManager or returns null; no direct Fire Launcher injection found.",
        "input_hashes": {str(path.relative_to(ROOT)): digest for path, digest in inputs.items()},
        "source_hashes_match_expected": {
            str(SERVICES_REL): sha256(services) == SERVICES_SHA256,
            str(FOS_REL): sha256(fos) == FOS_SHA256,
        },
        "row_count": len(rows),
    }
    write_json(artifact / "summary.json", summary)
    manifest_paths = sorted(path for path in artifact.iterdir() if path.is_file())
    write_text(artifact / "sha256sums.txt", "".join(f"{sha256(path)}  {path.name}\n" for path in manifest_paths))

    report_text, evidence_text = report(rows, inputs, regs, artifact)
    if not args.skip_publish:
        write_text(ROOT / "findings/phase-6al-home-resolve-callbacks.md", report_text)
        write_text(ROOT / "findings/phase-6al-evidence-index.md", evidence_text)
        write_text(ROOT / "output/tables/phase6al-home-resolve-callbacks.csv", table_path.read_text(encoding="utf-8"))
        write_text(ROOT / "output/call-graphs/phase6al-home-resolve-callback.mmd", graph_text)
        write_text(ROOT / "output/call-graphs/phase6al-home-resolve-callback.md", markdown_graph(graph_text))

    print(json.dumps({
        "artifact": str(artifact.relative_to(ROOT)) if artifact.is_relative_to(ROOT) else str(artifact),
        "report": "findings/phase-6al-home-resolve-callbacks.md",
        "evidence_index": "findings/phase-6al-evidence-index.md",
        "rows": len(rows),
        "registrations": len(regs),
        "host_only": True,
        "device_contacted": False,
        "binder_transaction_sent": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
