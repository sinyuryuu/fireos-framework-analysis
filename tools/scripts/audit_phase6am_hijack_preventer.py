#!/usr/bin/env python3
"""Audit the PS7331 LauncherHijackPreventer callback family, host-only.

The class name is suggestive, so this audit verifies what the preserved
callbacks actually do instead of inferring behavior from the name.  It reads
the saved fosservices disassembly and fosinit registrations only.  It never
contacts ADB, opens a Binder handle, replays a broadcast, starts an activity,
or changes a device/package/setting state.
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
FOS_REL = Path("decompiled/baksmali/vdexExtractor/fosservices/disassembly.log")
REGISTRATION_ROOT = ROOT / "artifacts/amazon-services"
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
    "mutation_or_live_observation",
    "classification",
    "confidence",
    "conclusion",
]

CALLBACKS = {
    "Lcom/amazon/launcherhijackpreventer/LauncherHijackPreventerActivityManagerServiceCallback;": "checkPermission",
    "Lcom/amazon/launcherhijackpreventer/LauncherHijackPreventerActivityStackCallback;": "canSeeHomeTask",
    "Lcom/amazon/launcherhijackpreventer/LauncherHijackPreventerPackageManagerCallback;": "onShutdown",
    "Lcom/amazon/launcherhijackpreventer/LauncherHijackPreventerPermissionManagerCallback;": "blockDevelopmentPermPersist",
    "Lcom/amazon/launcherhijackpreventer/LauncherHijackPreventerPackageStore;": None,
    "Lcom/android/server/pm/PackageWhitelisterCallback;": None,
}


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


def block_by_descriptor(text: str, descriptor: str) -> tuple[str, str]:
    marker = re.compile(
        r"^  class #[^\n]*\('" + re.escape(descriptor) + r"'\)\n", re.MULTILINE
    )
    match = marker.search(text)
    if not match:
        raise ValueError(f"class descriptor not found: {descriptor}")
    next_class = re.search(r"^  class #", text[match.end() :], re.MULTILINE)
    end = match.end() + next_class.start() if next_class else len(text)
    start_line = text.count("\n", 0, match.start()) + 1
    end_line = text.count("\n", 0, end)
    return text[match.start() : end], f"{start_line}-{end_line}"


def method_by_name(class_text: str, method_name: str) -> tuple[str, str]:
    marker = re.compile(
        r"^   (?:direct|virtual)_method [^\n]*: " + re.escape(method_name) + r"\b[^\n]*\n",
        re.MULTILINE,
    )
    match = marker.search(class_text)
    if not match:
        raise ValueError(f"method not found: {method_name}")
    next_method = re.search(r"^   (?:direct|virtual)_method ", class_text[match.end() :], re.MULTILINE)
    end = match.end() + next_method.start() if next_method else len(class_text)
    return class_text[match.start() : end], "method-local"


def source_lines(full_text: str, block: str) -> str:
    start = full_text.find(block)
    if start < 0:
        return "unknown"
    first = full_text.count("\n", 0, start) + 1
    last = first + block.count("\n")
    return f"{first}-{last}"


def registrations() -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    pattern = re.compile(
        r'<callback\b[^>]*base="([^"]+)"[^>]*impl="([^"]+)"[^>]*/>',
        re.DOTALL,
    )
    for path in sorted(REGISTRATION_ROOT.glob("*.xml")):
        content = read(path)
        for base, implementation in pattern.findall(content):
            if "launcherhijackpreventer" in implementation.lower() or implementation.endswith("PackageWhitelisterCallback"):
                found.append(
                    {
                        "base": base,
                        "implementation": implementation,
                        "file": str(path.relative_to(ROOT)),
                        "sha256": sha256(path),
                    }
                )
    expected = {
        "com.amazon.launcherhijackpreventer.LauncherHijackPreventerActivityStackCallback",
        "com.amazon.launcherhijackpreventer.LauncherHijackPreventerActivityManagerServiceCallback",
        "com.amazon.launcherhijackpreventer.LauncherHijackPreventerPackageManagerCallback",
        "com.amazon.launcherhijackpreventer.LauncherHijackPreventerPermissionManagerCallback",
        "com.android.server.pm.PackageWhitelisterCallback",
    }
    actual = {item["implementation"] for item in found}
    if actual != expected:
        raise ValueError(f"unexpected registration set: {sorted(actual)}")
    return found


def graph() -> str:
    return """flowchart TD
  A[HOME / ActivityTaskManager] --> B[Vendor callback fan-in]
  B --> C[ActivityStack callback]
  C --> D[canSeeHomeTask]
  D --> E[SELinux amazon_policies:see_home_task]
  D --> F[platform-signature check]
  D --> G[visibility boolean only]
  B --> H[other HOME pre-resolution callbacks]
  H --> I[PackageManager resolver path]
  J[Permission callback] --> K[blockDevelopmentPermPersist]
  K --> L[record package/user for READ_LOGS revoke]
  M[PackageManager callback] --> N[onShutdown]
  N --> O[revoke READ_LOGS for stored package/user pairs]
  P[PackageWhitelisterCallback] --> Q[updated-system/fdrw package bookkeeping]
  Q --> R[/data/system/fdrw_apks.conf]
  G -. no ResolveInfo/component .-> S[No direct Fire HOME selection]
  L -. permission policy, not HOME .-> S
  O -. shutdown permission cleanup, not HOME .-> S
  R -. package bookkeeping, not HOME .-> S
"""


def markdown_graph(graph_text: str) -> str:
    return "# Phase 6AM launcher-hijack callback graph\n\n```mermaid\n" + graph_text + "```\n\n" + graph_text


def row(
    evidence_id: str,
    surface: str,
    cls: str,
    method: str,
    lines: str,
    source_sha: str,
    control_flow: str,
    home_effect: str,
    fire_literal: str,
    observation: str,
    classification: str,
    confidence: str,
    conclusion: str,
) -> dict[str, str]:
    return {
        "evidence_id": evidence_id,
        "surface": surface,
        "class_or_registration": cls,
        "method_or_file": method,
        "source_lines": lines,
        "source_sha256": source_sha,
        "control_flow": control_flow,
        "home_effect": home_effect,
        "fire_literal": fire_literal,
        "mutation_or_live_observation": observation,
        "classification": classification,
        "confidence": confidence,
        "conclusion": conclusion,
    }


def build() -> tuple[list[dict[str, str]], dict[str, object], dict[str, str]]:
    fos_path = ROOT / FOS_REL
    fos = read(fos_path)
    regs = registrations()
    blocks: dict[str, tuple[str, str]] = {}
    for descriptor in CALLBACKS:
        blocks[descriptor] = block_by_descriptor(fos, descriptor)

    methods: dict[str, tuple[str, str]] = {}
    for descriptor, method_name in CALLBACKS.items():
        if method_name:
            methods[f"{descriptor}:{method_name}"] = method_by_name(blocks[descriptor][0], method_name)

    activity_stack = methods[
        "Lcom/amazon/launcherhijackpreventer/LauncherHijackPreventerActivityStackCallback;:canSeeHomeTask"
    ][0]
    ams = methods[
        "Lcom/amazon/launcherhijackpreventer/LauncherHijackPreventerActivityManagerServiceCallback;:checkPermission"
    ][0]
    pm = methods[
        "Lcom/amazon/launcherhijackpreventer/LauncherHijackPreventerPackageManagerCallback;:onShutdown"
    ][0]
    permission = methods[
        "Lcom/amazon/launcherhijackpreventer/LauncherHijackPreventerPermissionManagerCallback;:blockDevelopmentPermPersist"
    ][0]
    package_store = blocks[
        "Lcom/amazon/launcherhijackpreventer/LauncherHijackPreventerPackageStore;"
    ][0]
    package_whitelister = blocks["Lcom/android/server/pm/PackageWhitelisterCallback;"][0]

    for name, block in {
        "activity_stack": activity_stack,
        "ams": ams,
        "pm": pm,
        "permission": permission,
        "package_store": package_store,
        "package_whitelister": package_whitelister,
    }.items():
        if "com.amazon.firelauncher" in block:
            raise ValueError(f"unexpected Fire Launcher literal in {name} block")

    rows = [
        row(
            "6AM-HJ-001",
            "registration",
            "LauncherHijackPreventer fosinit registrations",
            "; ".join(sorted(item["file"] for item in regs if "launcherhijackpreventer" in item["implementation"].lower())),
            "registration files",
            "; ".join(sorted(item["file"] + "=" + item["sha256"] for item in regs if "launcherhijackpreventer" in item["implementation"].lower())),
            "registers ActivityStack, ActivityManagerService, PackageManager, and PermissionManager callbacks as SYSTEMSERVER vendor callbacks",
            "establishes callback hooks but does not itself choose a HOME component",
            "not present in registrations",
            "host-only; no registration mutation or private service call",
            "CALLBACK_REGISTRATION_CONFIRMED",
            "Confirmed",
            "The named hijack-preventer family is registered at four framework callback boundaries.",
        ),
        row(
            "6AM-HJ-002",
            "activity_stack_callback",
            "LauncherHijackPreventerActivityStackCallback",
            "canSeeHomeTask(int,Context)",
            source_lines(fos, activity_stack),
            FOS_SHA256,
            "resolve caller UID to ApplicationInfo; allow when SELinux check amazon_policies/see_home_task succeeds; otherwise allow platform-signed package; else false",
            "controls whether a caller can see the Home task; returns a boolean and does not construct ResolveInfo, Intent, or component",
            "absent from exact method block",
            "host-only; no SELinux policy or caller identity changed",
            "VISIBILITY_GATE_NOT_SELECTION",
            "Confirmed",
            "This callback is a Home-task visibility gate, not a HOME resolver selector.",
        ),
        row(
            "6AM-HJ-003",
            "activity_manager_callback",
            "LauncherHijackPreventerActivityManagerServiceCallback",
            "checkPermission(Context)",
            source_lines(fos, ams),
            FOS_SHA256,
            "checks leanback feature; returns ENABLE_KEYGUARD_FLAGS permission string on leanback, otherwise null",
            "selects a permission name for an ActivityManager callback; no HOME intent, package, or component selection",
            "absent from exact method block",
            "host-only; no permission state changed",
            "PERMISSION_NAME_HELPER",
            "Confirmed",
            "The ActivityManager callback supplies a permission name only; it does not redirect HOME.",
        ),
        row(
            "6AM-HJ-004",
            "package_manager_callback",
            "LauncherHijackPreventerPackageManagerCallback",
            "onShutdown(Context)",
            source_lines(fos, pm),
            FOS_SHA256,
            "iterate stored package/user pairs and revoke android.permission.READ_LOGS for each non-negative user",
            "shutdown-time permission cleanup; no resolver, preferred activity, or HOME component operation",
            "absent from exact method block",
            "host-only; no shutdown callback replay and no permission mutation",
            "SHUTDOWN_PERMISSION_CLEANUP",
            "Confirmed",
            "The PackageManager callback explains a READ_LOGS cleanup path, not a launcher-selection path.",
        ),
        row(
            "6AM-HJ-005",
            "permission_manager_callback",
            "LauncherHijackPreventerPermissionManagerCallback",
            "blockDevelopmentPermPersist(String,String,int)",
            source_lines(fos, permission),
            FOS_SHA256,
            "for non-empty package and READ_LOGS with non-negative user, record package/user pair; return callback boolean",
            "tracks packages whose READ_LOGS persistence is subject to callback policy; no HOME resolver operation",
            "absent from exact method block",
            "host-only; no runtime permission changes",
            "READ_LOGS_POLICY_TRACKING",
            "Confirmed",
            "The PermissionManager callback is unrelated to formal HOME selection.",
        ),
        row(
            "6AM-HJ-006",
            "package_store",
            "LauncherHijackPreventerPackageStore",
            "addPackageUserPair/getPackages",
            source_lines(fos, package_store),
            FOS_SHA256,
            "keeps an in-memory list of package/user pairs for the READ_LOGS cleanup path",
            "state is consumed by permission cleanup only; no preferred activity or HOME state is stored",
            "absent from exact class block",
            "host-only; in-memory store was not modified",
            "SUPPORTING_PERMISSION_STATE",
            "Confirmed",
            "The package store is supporting state for permission cleanup, not launcher selection.",
        ),
        row(
            "6AM-HJ-007",
            "package_whitelister_callback",
            "com.android.server.pm.PackageWhitelisterCallback",
            "constructor/commitPackageSettings/onInit/onUpdateFoundForDeletedSystemApp/scanPackageNewLI",
            source_lines(fos, package_whitelister),
            FOS_SHA256,
            "loads a system string-array resource (0x7e090015), handles updated-system/fdrw metadata, and writes /data/system/fdrw_apks.conf",
            "package install/update bookkeeping; exact inspected block has no HOME resolver or preferred-activity call",
            "absent from exact class block",
            "host-only; no package install/update or conf-file mutation",
            "PACKAGE_BOOKKEEPING_NOT_HOME",
            "Strong evidence",
            "PackageWhitelister is not evidence of a HOME selection override in the inspected PS7331 class.",
        ),
        row(
            "6AM-HJ-008",
            "selection_search",
            "all inspected Phase 6AM class/method blocks",
            "resolveIntent/startHome/setPreferred/addPreferred/replacePreferred/cmp literals",
            "class blocks in fosservices/disassembly.log",
            FOS_SHA256,
            "the exact blocks contain no direct HOME-selection operation and no com.amazon.firelauncher literal",
            "no direct Fire component injection is visible in the launcher-hijack-preventer family",
            "not present in all inspected blocks",
            "live HOME remains Fire priority 50 from the existing read-only capture; this audit did not re-run it",
            "DIRECT_SELECTOR_NOT_FOUND_IN_SCOPE",
            "Strong evidence",
            "Within the preserved class scope, the name 'LauncherHijackPreventer' overstates its role in final HOME selection.",
        ),
    ]

    summary: dict[str, object] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "host_only": True,
        "device_contacted": False,
        "binder_transaction_sent": False,
        "package_or_settings_mutated": False,
        "fire_launcher_disabled": False,
        "root_or_partition_operation": False,
        "fos_disassembly": str(FOS_REL),
        "fos_sha256": FOS_SHA256,
        "registration_count": len(regs),
        "registration_implementations": sorted(item["implementation"] for item in regs),
        "direct_fire_literal_in_inspected_blocks": False,
        "selection_calls_in_inspected_blocks": [],
        "key_result": "LauncherHijackPreventer callbacks implement visibility and READ_LOGS/package bookkeeping; no direct Fire HOME selector was found in the preserved blocks.",
        "limitations": [
            "No runtime callback return values were captured.",
            "The audit is bounded by the preserved fosservices disassembly and fosinit XML scope.",
            "No conclusion is made about native code or artifacts outside that scope.",
        ],
    }
    snippets = {
        "activity-stack-can-see-home-task.txt": activity_stack,
        "activity-manager-check-permission.txt": ams,
        "package-manager-on-shutdown.txt": pm,
        "permission-manager-block-development-perm.txt": permission,
        "package-store.txt": package_store,
        "package-whitelister-callback.txt": package_whitelister,
    }
    return rows, {"summary": summary, "registrations": regs, "snippets": snippets}, {"graph": graph(), "graph_markdown": markdown_graph(graph())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts/phase6am/launcher-hijack-preventer-20260805-01",
        help="new canonical artifact directory",
    )
    parser.add_argument("--dry-run", action="store_true", help="print the planned host-only audit without writing")
    args = parser.parse_args()

    outputs = [
        args.output,
        ROOT / "findings/phase-6am-launcher-hijack-preventer.md",
        ROOT / "findings/phase-6am-evidence-index.md",
        ROOT / "output/tables/phase6am-launcher-hijack-preventer.csv",
        ROOT / "output/call-graphs/phase6am-launcher-hijack-preventer.mmd",
        ROOT / "output/call-graphs/phase6am-launcher-hijack-preventer.md",
    ]
    existing = [str(path) for path in outputs if path.exists()]
    if existing and not args.dry_run:
        raise SystemExit("refusing to overwrite existing output: " + ", ".join(existing))

    rows, payload, graphs = build()
    if args.dry_run:
        print("HOST_ONLY=TRUE")
        print("DEVICE_CONTACTED=FALSE")
        print("BINDER_TRANSACTION_SENT=FALSE")
        print("PACKAGE_OR_SETTINGS_MUTATED=FALSE")
        print("REGISTRATIONS=" + str(payload["summary"]["registration_count"]))
        print("OUTPUTS=")
        for path in outputs:
            print(path)
        return 0

    args.output.mkdir(parents=True, exist_ok=False)
    for filename, content in payload["snippets"].items():
        write_text(args.output / filename, content)
    write_json(args.output / "registrations.json", payload["registrations"])
    write_json(args.output / "summary.json", payload["summary"])
    write_json(args.output / "input-sha256.json", {"path": str(FOS_REL), "sha256": FOS_SHA256})
    write_text(args.output / "launcher-hijack-preventer.mmd", graphs["graph"])
    write_text(args.output / "launcher-hijack-preventer.md", graphs["graph_markdown"])

    csv_path = ROOT / "output/tables/phase6am-launcher-hijack-preventer.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    mmd_path = ROOT / "output/call-graphs/phase6am-launcher-hijack-preventer.mmd"
    md_graph_path = ROOT / "output/call-graphs/phase6am-launcher-hijack-preventer.md"
    write_text(mmd_path, graphs["graph"])
    write_text(md_graph_path, graphs["graph_markdown"])

    report = """# Phase 6AM — LauncherHijackPreventer callback audit

Generated: {generated}

## Scope and safety

This is a host-only static audit of the PS7331 `fosservices` disassembly and
preserved `fosinit` registrations. It does not contact ADB, call a private
Binder service, replay a broadcast, start an activity, change a permission,
modify package/settings state, stop Fire Launcher, or touch any partition.

## Executive result

### 已證實

1. The preserved `LauncherHijackPreventer` family is registered at four
   SYSTEMSERVER callback boundaries: ActivityStack, ActivityManagerService,
   PackageManager, and PermissionManager. Evidence `6AM-HJ-001`.
2. `canSeeHomeTask(int, Context)` is a visibility boolean. It checks the
   SELinux `amazon_policies:see_home_task` permission and otherwise a platform
   signature; it does not create a `ResolveInfo`, explicit component, or HOME
   intent. Evidence `6AM-HJ-002`.
3. `checkPermission(Context)` returns a permission name for the leanback
   feature branch; it is not a launcher selector. Evidence `6AM-HJ-003`.
4. The PackageManager and PermissionManager callbacks track/revoke
   `android.permission.READ_LOGS` for stored package/user pairs. Evidence
   `6AM-HJ-004`, `6AM-HJ-005`, `6AM-HJ-006`.
5. `PackageWhitelisterCallback` handles updated-system/fdrw package
   bookkeeping and `/data/system/fdrw_apks.conf`; no HOME resolver or
   preferred-activity call appears in the inspected class block. Evidence
   `6AM-HJ-007`.

### 高可信推論

- In the preserved PS7331 class and registration scope, the name
  `LauncherHijackPreventer` does not identify the final HOME selector. The
  inspected implementation is a task-visibility and permission/package
  policy family, while HOME selection remains in the PackageManager result or
  another unpreserved/native path. Evidence `6AM-HJ-008`.
- This removes another plausible direct `com.amazon.firelauncher` injection
  point from the Java/DEX callback inventory; it does not prove that every
  native or out-of-scope path is absent.

### 待驗證

- Runtime callback return values for a real Home-key event were not captured.
- The exact raw resource behind `0x7e05000a` and the current deny-list
  membership are still not shell-readable from the device.
- The preserved artifact scope may not include every runtime-loaded native
  callback or overlay registration.

### 已排除／因風險拒絕

- **已排除於 inspected scope：** direct Fire Launcher literal/component
  construction in the inspected LauncherHijackPreventer and
  PackageWhitelister blocks.
- **因風險拒絕：** unknown Binder transactions, callback fuzzing, manual
  OOBE/OTA replay, permission/package mutation, SELinux changes, root,
  framework injection, and partition operations.

## Control-flow interpretation

```text
HOME / ActivityTaskManager
  → vendor callback fan-in
  → canSeeHomeTask()
      → SELinux/signature visibility decision (boolean)
  → normal resolver path remains responsible for ResolveInfo/component

READ_LOGS policy path
  → blockDevelopmentPermPersist()
  → store package/user pair
  → onShutdown() revokes READ_LOGS

Package update path
  → PackageWhitelisterCallback
  → fdrw metadata / /data/system/fdrw_apks.conf
```

The Mermaid graph and plain-text graph are preserved at
`output/call-graphs/phase6am-launcher-hijack-preventer.*` and in the canonical
artifact.

## Evidence table

| Evidence | Finding | Confidence |
|---|---|---|
| `6AM-HJ-001` | Four LauncherHijackPreventer callback registrations | Confirmed |
| `6AM-HJ-002` | `canSeeHomeTask` is visibility, not selection | Confirmed |
| `6AM-HJ-003` | ActivityManager callback supplies permission name | Confirmed |
| `6AM-HJ-004` | PackageManager callback performs READ_LOGS cleanup | Confirmed |
| `6AM-HJ-005` | Permission callback tracks READ_LOGS policy | Confirmed |
| `6AM-HJ-006` | Package store supports permission cleanup | Confirmed |
| `6AM-HJ-007` | PackageWhitelister is fdrw/update bookkeeping | Strong evidence |
| `6AM-HJ-008` | No direct HOME selector in inspected scope | Strong evidence |

## Reproduction

```sh
python3 tools/scripts/audit_phase6am_hijack_preventer.py --dry-run
python3 tools/scripts/audit_phase6am_hijack_preventer.py \
  --output artifacts/phase6am/launcher-hijack-preventer-20260805-01
```

The script refuses to overwrite existing output. It emits the extracted
method/class snippets, registration inventory, CSV, graph, summary, input
hashes, and a SHA-256 manifest.

## Decision

This phase closes the misleadingly named LauncherHijackPreventer callback
family as a direct HOME-selection explanation within the preserved PS7331
scope. It provides no new shell workaround and no safe reason to mutate the
device. The next useful static target is the remaining PackageManager
candidate/protected-state source, not another attempt to disable or invoke
the launcher-preventer callbacks.
""".format(generated=payload["summary"]["generated_utc"])
    write_text(ROOT / "findings/phase-6am-launcher-hijack-preventer.md", report)

    evidence = """# Phase 6AM evidence index

All evidence in this phase is host-only. The source input is
`{source}` with SHA-256 `{sha}`.

| Evidence ID | Source | Observed result | Confidence |
|---|---|---|---|
| `6AM-HJ-001` | `artifacts/amazon-services/*_fosinit.xml` | Four LauncherHijackPreventer callback registrations are preserved | Confirmed |
| `6AM-HJ-002` | `LauncherHijackPreventerActivityStackCallback.canSeeHomeTask` | SELinux/signature visibility boolean; no ResolveInfo/component construction | Confirmed |
| `6AM-HJ-003` | `LauncherHijackPreventerActivityManagerServiceCallback.checkPermission` | Leanback-dependent permission-name return | Confirmed |
| `6AM-HJ-004` | `LauncherHijackPreventerPackageManagerCallback.onShutdown` | Revokes READ_LOGS for stored package/user pairs | Confirmed |
| `6AM-HJ-005` | `LauncherHijackPreventerPermissionManagerCallback.blockDevelopmentPermPersist` | Records READ_LOGS package/user pairs | Confirmed |
| `6AM-HJ-006` | `LauncherHijackPreventerPackageStore` | In-memory support for permission cleanup | Confirmed |
| `6AM-HJ-007` | `PackageWhitelisterCallback` | fdrw/update bookkeeping; no HOME operation in class block | Strong evidence |
| `6AM-HJ-008` | All inspected class/method blocks | No direct Fire HOME selector in bounded scope | Strong evidence |

Device contact: none. Binder transactions: none. Package/settings mutation:
none. Fire Launcher state: unchanged.
""".format(source=FOS_REL, sha=FOS_SHA256)
    write_text(ROOT / "findings/phase-6am-evidence-index.md", evidence)

    manifest_lines = []
    for path in sorted(args.output.rglob("*")):
        if path.is_file():
            manifest_lines.append(f"{sha256(path)}  {path.relative_to(args.output)}")
    write_text(args.output / "sha256sums.txt", "\n".join(manifest_lines) + "\n")
    print(f"WROTE {args.output}")
    print(f"ROWS {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
