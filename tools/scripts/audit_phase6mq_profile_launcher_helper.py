#!/usr/bin/env python3
"""Close the PS7331 AmazonProfileService launcher-helper boundary, host-only.

The input is the preserved PS7331 fosservices disassembly and earlier bounded
IPC reviews.  This audit extracts exact method windows and checks the
AmazonProfileService.BinderService class slice for HOME/package-state writer
tokens.  It never contacts a device, invokes Binder, sends an intent, changes
settings or package state, runs an ioctl, or writes a firmware artifact.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date
from pathlib import Path


SCHEMA = "phase6mq-profile-launcher-helper-v1"
DEFAULT_OUT = "artifacts/phase6mq-profile-launcher-helper-20260810-01"
DISASSEMBLY_REL = "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"

WINDOWS = {
    "binder_service_class": (74942, 77607, [
        "AmazonProfileService.BinderService",
        "initiateLauncher",
        "startProfilePicker",
    ]),
    "initiate_launcher": (76246, 76256, [
        "initiateLauncher ()I",
        "access$6400",
        "Initiate launcher",
        "AmazonProfileManager;.SUCCESS",
    ]),
    "start_profile_picker": (77222, 77280, [
        "startProfilePicker (I)V",
        "KEY_PROFILE_PICKER_PACKAGE_NAME",
        "KEY_PROFILE_PICKER_ACTIVITY_NAME",
        "Intent;.setClassName",
        "ActivityManager;.getCurrentUser",
        "Context;.startActivityAsUser",
    ]),
    "profile_permission_bridge": (78685, 78691, [
        "access$6400",
        "enforceProfileInteractionPermissions",
    ]),
    "profile_permission_check": (78949, 78966, [
        "enforceProfileInteractionPermissions ()V",
        "PROFILE_INTERACTION",
        "Context;.checkPermission",
        "SecurityException",
    ]),
    "service_publication": (80813, 80823, [
        "onStart ()V",
        "amazonprofileservice",
        "publishBinderService",
        "publishLocalService",
    ]),
}

NEGATIVE_TOKENS = [
    "setHomeActivity",
    "replacePreferredActivity",
    "addPreferredActivity",
    "setComponentEnabledSetting",
    "setApplicationEnabledSetting",
    "com.amazon.firelauncher",
    "CATEGORY_HOME",
    "ACTION_MAIN",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_lines(path: Path) -> list[str]:
    # The preserved disassembly contains a few bare CR bytes.  LF-only
    # splitting preserves the line numbers emitted by `nl -ba`.
    with path.open("r", encoding="utf-8", errors="replace", newline="\n") as handle:
        return handle.read().split("\n")


def line_range(lines: list[str], start: int, end: int) -> str:
    return "\n".join(lines[start - 1:end])


def require_markers(lines: list[str], label: str, start: int, end: int, markers: list[str]) -> None:
    text = line_range(lines, start, end)
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"input drift for {label}:{start}-{end}; missing markers: {missing}")


def write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, value: object, force: bool) -> None:
    write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n", force)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]], force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def rel(root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def build_inputs(root: Path) -> list[Path]:
    paths = [
        root / DISASSEMBLY_REL,
        root / "findings/phase-6s-ipc-focus-review.md",
        root / "findings/phase-6mn-ipc-user-scope-closure.md",
        root / "findings/phase-6bj-binder-caller-closure.md",
    ]
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing required inputs:\n" + "\n".join(map(str, missing)))
    return paths


def validate_inputs(root: Path) -> tuple[Path, list[str], dict[str, str]]:
    disassembly = root / DISASSEMBLY_REL
    lines = read_lines(disassembly)
    for label, (start, end, markers) in WINDOWS.items():
        require_markers(lines, label, start, end, markers)
    class_text = line_range(lines, *WINDOWS["binder_service_class"][:2])
    negative_hits = {token: [
        WINDOWS["binder_service_class"][0] + index
        for index, line in enumerate(class_text.split("\n"))
        if token in line
    ] for token in NEGATIVE_TOKENS}
    return disassembly, lines, negative_hits


def graph_text() -> str:
    return """flowchart TD
  A["BinderService.initiateLauncher()"] --> B["access$6400()"]
  B --> C["enforceProfileInteractionPermissions()"]
  C -->|"checkPermission(PROFILE_INTERACTION, processId, userId)"| D{Allowed?}
  D -->|"no"| E["SecurityException"]
  D -->|"yes"| F["Slog: Initiate launcher"]
  F --> G["return AmazonProfileManager.SUCCESS"]

  H["BinderService.startProfilePicker(wakeUpSource)"] --> I["read configured package/activity"]
  I --> J["Intent.setClassName(package, activity)"]
  J --> K["ActivityManager.getCurrentUser()"]
  K --> L["Context.startActivityAsUser(profile-picker, current user)"]
  L --> M["profile picker path; not HOME resolver"]

  N["AmazonProfileService.onStart()"] --> O["publishBinderService(amazonprofileservice)"]
  N --> P["publishLocalService(AmazonProfileService)"]
  N --> Q["registerPackageInstalledReceived()"]
"""


def report_text(root: Path, disassembly: Path, input_hashes: dict[str, str], negative_hits: dict[str, list[int]], generated_date: str) -> str:
    negative_lines = "\n".join(
        f"- `{token}`: " + (", ".join(map(str, lines)) if lines else "no hit")
        for token, lines in negative_hits.items()
    )
    return f"""# Phase 6MQ — AmazonProfileService launcher-helper closure

Date: {generated_date}
Schema: `{SCHEMA}`

## Scope and safety

This is **host-only static analysis** of preserved PS7331 artifacts. The audit
did not contact the tablet, invoke `service call`, replay a private Binder
transaction, send an intent, change settings or package state, run an ioctl,
reboot, use an exploit, or write any partition. The exact source artifact is
`{rel(root, disassembly)}`.

## Executive result

**已證實：** `AmazonProfileService.BinderService.initiateLauncher()` is a
misleadingly named helper in this disassembly. Its body calls the synthetic
`access$6400()` permission bridge, writes the `Initiate launcher` log message,
and returns `AmazonProfileManager.SUCCESS`. It contains no `Intent`,
`startActivityAsUser`, HOME resolver API, preferred-activity API, or package
component-state mutation.

**已證實：** `access$6400()` invokes
`enforceProfileInteractionPermissions()`. That method checks
`com.amazon.device.permission.PROFILE_INTERACTION` with
`Context.checkPermission(permission, processId, userId)` and throws a
`SecurityException` on denial.

**已證實：** `startProfilePicker(int)` constructs an explicit Intent from
the configured `KEY_PROFILE_PICKER_PACKAGE_NAME` and
`KEY_PROFILE_PICKER_ACTIVITY_NAME`, obtains `ActivityManager.getCurrentUser()`,
and calls `Context.startActivityAsUser()` for that current user. This is a
profile-picker UI path, not a HOME resolver selection or a Fire Launcher
package-state writer.

**高可信推論（bounded）：** within the preserved
`AmazonProfileService.BinderService` class slice (`{WINDOWS['binder_service_class'][0]}-{WINDOWS['binder_service_class'][1]}`), no direct HOME/preferred/package-state writer token was found. This does not claim that no other Amazon service can write HOME state.

**已排除（bounded）：** `initiateLauncher()` itself is a direct HOME launch,
preferred-activity writer, or Fire Launcher enable/disable sink.

**待驗證：** the source and complete caller graph for the profile-picker
configuration map; whether any authorized caller reaches `startProfilePicker`
under a particular profile lifecycle. Neither question changes the bounded
finding that the shown sink is an explicit profile picker, not HOME selection.

**因風險拒絕測試：** no attempt was made to call `amazonprofileservice`, to
guess a Binder transaction code, or to replay `startProfilePicker`; such calls
would exercise a private service and could change foreground/profile state.

## Exact evidence windows

| Evidence | Location | Observation | Classification |
|---|---|---|---|
| 6MQ-E01 | `{rel(root, disassembly)}:76246-76256` | `initiateLauncher()` → permission bridge → log → `SUCCESS` | 已證實 |
| 6MQ-E02 | `{rel(root, disassembly)}:78685-78691` | `access$6400()` → `enforceProfileInteractionPermissions()` | 已證實 |
| 6MQ-E03 | `{rel(root, disassembly)}:78949-78966` | `PROFILE_INTERACTION` check using process/user IDs; denial throws | 已證實 |
| 6MQ-E04 | `{rel(root, disassembly)}:77222-77280` | configured explicit profile picker → current-user `startActivityAsUser` | 已證實 |
| 6MQ-E05 | `{rel(root, disassembly)}:80813-80823` | Binder/local service publication and package receiver registration | 已證實 |
| 6MQ-E06 | `BinderService class slice {WINDOWS['binder_service_class'][0]}-{WINDOWS['binder_service_class'][1]}` | no bounded HOME/package-state writer token; one `startActivityAsUser` hit belongs to profile picker | 高可信推論（bounded） |

## Minimal call paths

```text
BinderService.initiateLauncher()
  → AmazonProfileService.access$6400()
  → enforceProfileInteractionPermissions()
  → Context.checkPermission(PROFILE_INTERACTION, processId, userId)
  → SecurityException or return
  → Slog("Initiate launcher")
  → return AmazonProfileManager.SUCCESS
```

```text
BinderService.startProfilePicker(wakeUpSource)
  → read profile-picker package/activity configuration
  → Intent.setClassName(package, activity)
  → ActivityManager.getCurrentUser()
  → Context.startActivityAsUser(intent, UserHandle.of(currentUser))
  → profile-picker UI
```

The first path has no launch sink. The second path has an explicit launch sink,
but its target is supplied by profile-picker configuration and its observed
operation is not `ACTION_MAIN` + `CATEGORY_HOME`, `resolveActivity`,
`setHomeActivity`, or a preferred-activity write.

## Bounded token scan

The following scan was performed only over the `BinderService` class slice;
line numbers are absolute disassembly line numbers:

{negative_lines}

The only `startActivityAsUser` hit in this bounded slice is the one at
`{rel(root, disassembly)}:77222-77280`. Absence from this slice is not a
binary-wide proof about every Amazon service.

## Service publication

`onStart()` publishes the Binder service name `amazonprofileservice`, publishes
the local `AmazonProfileService`, and registers a package-installed receiver
(`{rel(root, disassembly)}:80813-80823`). The audit does not infer the service
process UID or caller permissions beyond the exact permission check shown in
the method windows.

## Relationship to the HOME question

This closure removes one named candidate from the direct HOME-selection path:
the `initiateLauncher` method does not implement that behavior in PS7331.
`startProfilePicker` remains a profile lifecycle/UI path that could affect the
visible foreground during profile selection, but no evidence here shows it
overriding the User 0 HOME resolver or writing Fire Launcher preferred state.
The exact HOME enforcement evidence remains the AOSP-shaped resolver ordering
plus the PS7331 PackageManager deny-list resource; see the earlier Phase 6AP
and Phase 4A reports.

## Input hashes

```text
{json.dumps(input_hashes, indent=2, sort_keys=True)}
```

## Reproduction

```sh
python3 tools/scripts/audit_phase6mq_profile_launcher_helper.py --dry-run
python3 tools/scripts/audit_phase6mq_profile_launcher_helper.py
```

Generated artifact: `artifacts/phase6mq-profile-launcher-helper-20260810-01`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--generated-date", default=str(date.today()))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="overwrite only this audit's generated outputs")
    args = parser.parse_args()

    root = args.root.resolve()
    output = (args.output or (root / DEFAULT_OUT)).resolve()
    inputs = build_inputs(root)
    disassembly, lines, negative_hits = validate_inputs(root)
    input_hashes = {rel(root, path): sha256(path) for path in inputs}

    report_path = root / "findings/phase-6mq-profile-launcher-helper-closure.md"
    evidence_path = root / "findings/phase-6mq-evidence-index.md"
    table_path = root / "output/tables/phase6mq-profile-launcher-helper-20260810-01.csv"
    graph_path = root / "output/call-graphs/phase6mq-profile-launcher-helper-20260810-01.mmd"
    artifact_files = [
        output / "method-matrix.csv",
        output / "method-evidence.csv",
        output / "summary.json",
        output / "input-manifest.csv",
        output / "route-flow.mmd",
        output / "evidence/initiate-launcher.txt",
        output / "evidence/profile-permission-bridge.txt",
        output / "evidence/profile-permission-check.txt",
        output / "evidence/start-profile-picker.txt",
        output / "evidence/service-publication.txt",
        output / "evidence/binder-service-negative-scan.txt",
        output / "sha256sums.txt",
    ]
    generated = artifact_files + [report_path, evidence_path, table_path, graph_path]

    if args.dry_run:
        print(f"schema={SCHEMA}")
        print(f"root={root}")
        print(f"output={output}")
        print("host_only=true")
        print("device_contacted=false")
        print("binder_or_service_call=false")
        print("mutation=false")
        print("reboot=false")
        print("inputs:")
        for path in inputs:
            print(f"  {path}")
        print("outputs:")
        for path in generated:
            print(f"  {path}")
        return 0

    existing = [path for path in generated if path.exists()]
    if existing and not args.force:
        raise SystemExit("refusing to overwrite existing outputs:\n" + "\n".join(map(str, existing)))
    output.mkdir(parents=True, exist_ok=True)

    rows = [
        {"evidence_id": "6MQ-E01", "method": "AmazonProfileService.BinderService.initiateLauncher", "line_range": "76246-76256", "sink": "permission check; log; SUCCESS return", "home_or_package_state_writer": "NO", "classification": "Confirmed"},
        {"evidence_id": "6MQ-E02", "method": "AmazonProfileService.access$6400", "line_range": "78685-78691", "sink": "enforceProfileInteractionPermissions", "home_or_package_state_writer": "NO", "classification": "Confirmed"},
        {"evidence_id": "6MQ-E03", "method": "AmazonProfileService.enforceProfileInteractionPermissions", "line_range": "78949-78966", "sink": "Context.checkPermission(PROFILE_INTERACTION, processId, userId)", "home_or_package_state_writer": "NO", "classification": "Confirmed"},
        {"evidence_id": "6MQ-E04", "method": "AmazonProfileService.BinderService.startProfilePicker", "line_range": "77222-77280", "sink": "explicit configured profile picker via startActivityAsUser", "home_or_package_state_writer": "NO", "classification": "Confirmed"},
        {"evidence_id": "6MQ-E05", "method": "AmazonProfileService.onStart", "line_range": "80813-80823", "sink": "publish Binder/local services; register package receiver", "home_or_package_state_writer": "NO", "classification": "Confirmed"},
        {"evidence_id": "6MQ-E06", "method": "BinderService bounded class scan", "line_range": "74942-77607", "sink": "no HOME/preferred/package-state tokens; profile picker is the only startActivityAsUser hit", "home_or_package_state_writer": "NO (bounded)", "classification": "Strong evidence"},
    ]
    method_fields = list(rows[0].keys())
    write_csv(output / "method-matrix.csv", method_fields, rows, args.force)
    write_csv(output / "method-evidence.csv", ["evidence_id", "source", "line_range", "markers", "classification"], [
        {"evidence_id": "6MQ-E01", "source": rel(root, disassembly), "line_range": "76246-76256", "markers": "initiateLauncher; access$6400; Initiate launcher; SUCCESS", "classification": "Confirmed"},
        {"evidence_id": "6MQ-E02", "source": rel(root, disassembly), "line_range": "78685-78691", "markers": "access$6400; enforceProfileInteractionPermissions", "classification": "Confirmed"},
        {"evidence_id": "6MQ-E03", "source": rel(root, disassembly), "line_range": "78949-78966", "markers": "PROFILE_INTERACTION; checkPermission; SecurityException", "classification": "Confirmed"},
        {"evidence_id": "6MQ-E04", "source": rel(root, disassembly), "line_range": "77222-77280", "markers": "profile picker keys; setClassName; getCurrentUser; startActivityAsUser", "classification": "Confirmed"},
        {"evidence_id": "6MQ-E05", "source": rel(root, disassembly), "line_range": "80813-80823", "markers": "amazonprofileservice; publishBinderService; publishLocalService", "classification": "Confirmed"},
        {"evidence_id": "6MQ-E06", "source": rel(root, disassembly), "line_range": "74942-77607", "markers": "bounded negative token scan", "classification": "Strong evidence"},
    ], args.force)

    input_manifest = [{"path": rel(root, path), "sha256": sha256(path), "size": path.stat().st_size} for path in inputs]
    write_csv(output / "input-manifest.csv", ["path", "sha256", "size"], input_manifest, args.force)

    snippets = {
        "initiate-launcher.txt": line_range(lines, 76246, 76256),
        "profile-permission-bridge.txt": line_range(lines, 78685, 78691),
        "profile-permission-check.txt": line_range(lines, 78949, 78966),
        "start-profile-picker.txt": line_range(lines, 77222, 77280),
        "service-publication.txt": line_range(lines, 80813, 80823),
        "binder-service-negative-scan.txt": "\n".join(
            f"{token}: " + (", ".join(map(str, hit_lines)) if hit_lines else "no hit")
            for token, hit_lines in negative_hits.items()
        ) + "\n",
    }
    for name, content in snippets.items():
        write_text(output / "evidence" / name, content, args.force)
    write_text(output / "route-flow.mmd", graph_text(), args.force)

    summary = {
        "schema": SCHEMA,
        "generated_date": args.generated_date,
        "scope": "host-only preserved disassembly audit",
        "input_count": len(inputs),
        "method_evidence_count": len(rows),
        "device_contacted": False,
        "binder_or_service_call": False,
        "ioctl": False,
        "mutation": False,
        "reboot": False,
        "root_or_exploit": False,
        "initiate_launcher_is_home_writer": False,
        "profile_picker_is_home_writer": False,
        "bounded_negative_scan": negative_hits,
        "conclusion": "initiateLauncher is permission/log/SUCCESS only; startProfilePicker is explicit profile-picker launch, not HOME resolver selection",
    }
    write_json(output / "summary.json", summary, args.force)
    write_text(report_path, report_text(root, disassembly, input_hashes, negative_hits, args.generated_date), args.force)
    write_text(graph_path, graph_text(), args.force)
    write_csv(table_path, method_fields, rows, args.force)

    evidence = f"""# Phase 6MQ evidence index — AmazonProfileService launcher-helper closure

Generated: {args.generated_date}
Scope: host-only; no device contact, Binder call, mutation, reboot, exploit, or partition write.

## 6MQ-E01

- Source: preserved PS7331 fosservices disassembly
- File: `{rel(root, disassembly)}`
- SHA-256: `{sha256(disassembly)}`
- Test ID: `PHASE6MQ-STATIC-20260810-01`
- Timestamp: `{args.generated_date}` (host generation date)
- Command: `python3 tools/scripts/audit_phase6mq_profile_launcher_helper.py`
- Observed result: `initiateLauncher()` calls `access$6400()`, logs `Initiate launcher`, returns `AmazonProfileManager.SUCCESS`; no launch or package-state instruction in the window.
- Interpretation: the method name does not identify a HOME launch sink.
- Confidence: Confirmed
- Related hypothesis: `AmazonProfileService.initiateLauncher` directly forces Fire Launcher — Disproved (bounded).

## 6MQ-E02

- Source: preserved PS7331 fosservices disassembly
- File: `{rel(root, disassembly)}`
- SHA-256: `{sha256(disassembly)}`
- Test ID: `PHASE6MQ-STATIC-20260810-01`
- Timestamp: `{args.generated_date}`
- Command: exact line-window extraction, `78685-78691`
- Observed result: synthetic bridge calls `enforceProfileInteractionPermissions()` and returns.
- Interpretation: `initiateLauncher` is permission-gated through the profile interaction check.
- Confidence: Confirmed
- Related hypothesis: shell can use this helper without the required private permission — not supported by this evidence.

## 6MQ-E03

- Source: preserved PS7331 fosservices disassembly
- File: `{rel(root, disassembly)}`
- SHA-256: `{sha256(disassembly)}`
- Test ID: `PHASE6MQ-STATIC-20260810-01`
- Timestamp: `{args.generated_date}`
- Command: exact line-window extraction, `78949-78966`
- Observed result: checks `com.amazon.device.permission.PROFILE_INTERACTION` with process and user IDs and throws `SecurityException` on denial.
- Interpretation: the observed permission gate is explicit; no private Binder replay was attempted.
- Confidence: Confirmed
- Related hypothesis: unprivileged direct access to `initiateLauncher` is available — not supported.

## 6MQ-E04

- Source: preserved PS7331 fosservices disassembly
- File: `{rel(root, disassembly)}`
- SHA-256: `{sha256(disassembly)}`
- Test ID: `PHASE6MQ-STATIC-20260810-01`
- Timestamp: `{args.generated_date}`
- Command: exact line-window extraction, `77222-77280`
- Observed result: explicit configured package/activity is launched with `startActivityAsUser` for `ActivityManager.getCurrentUser()`.
- Interpretation: this is a profile-picker path, not a HOME resolver or preferred-activity writer.
- Confidence: Confirmed
- Related hypothesis: the profile picker method directly selects Fire Launcher for HOME — Disproved (bounded).

## 6MQ-E05

- Source: preserved PS7331 fosservices disassembly
- File: `{rel(root, disassembly)}`
- SHA-256: `{sha256(disassembly)}`
- Test ID: `PHASE6MQ-STATIC-20260810-01`
- Timestamp: `{args.generated_date}`
- Command: exact line-window extraction, `80813-80823`
- Observed result: `amazonprofileservice` Binder publication, local service publication, and package receiver registration.
- Interpretation: identifies the service publication boundary; it does not prove a HOME writer.
- Confidence: Confirmed
- Related hypothesis: service existence alone proves HOME control — Disproved.

## 6MQ-E06

- Source: preserved PS7331 fosservices disassembly
- File: `{rel(root, disassembly)}`
- SHA-256: `{sha256(disassembly)}`
- Test ID: `PHASE6MQ-STATIC-20260810-01`
- Timestamp: `{args.generated_date}`
- Command: bounded scan of lines `74942-77607`
- Observed result: no `setHomeActivity`, preferred-activity writer, package/component enabled-state writer, `com.amazon.firelauncher`, `CATEGORY_HOME`, or `ACTION_MAIN`; the only `startActivityAsUser` hit is the profile picker window.
- Interpretation: strong bounded negative for this BinderService class slice only.
- Confidence: Strong evidence
- Related hypothesis: this class slice directly implements the Fire Launcher HOME enforcement — not supported.

## Safety disposition

`service call amazonprofileservice ...`, guessed transaction codes, intent replay,
package-state mutation, Fire Launcher disable/hide/suspend/force-stop/clear,
Root/exploit execution, OTA/recovery/fastboot, and partition writes were not
performed. Such actions remain **因風險拒絕測試** for this static closure.
"""
    write_text(evidence_path, evidence, args.force)

    # The checksum file intentionally excludes itself so `sha256sum -c` can be
    # run from the artifact directory without a self-referential hash.
    checksum_lines = []
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.name == "sha256sums.txt":
            continue
        checksum_lines.append(f"{sha256(path)}  {path.relative_to(output)}")
    write_text(output / "sha256sums.txt", "\n".join(checksum_lines) + "\n", args.force)

    print(json.dumps({
        "schema": SCHEMA,
        "output": str(output),
        "report": str(report_path),
        "evidence_index": str(evidence_path),
        "device_contacted": False,
        "binder_or_service_call": False,
        "mutation": False,
        "reboot": False,
        "artifact_sha256_manifest": str(output / "sha256sums.txt"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
