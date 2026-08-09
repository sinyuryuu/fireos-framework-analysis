#!/usr/bin/env python3
"""Build a host-only matrix for bounded Amazon Framework IPC candidates.

This audit maps preserved AIDL-style proxy methods to the corresponding
Amazon system-service BinderService methods for five interfaces that are
adjacent to the HOME/package-state research surface.  It records transaction
codes, permission/identity markers, bounded sinks, and HOME relevance without
contacting a device or invoking any Binder transaction.

It deliberately does not prove that a shell or ordinary APK can obtain a
service handle.  It also does not treat a missing permission marker as an
authorization bypass: runtime publication, SELinux, native checks, and
caller reachability remain separate questions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


SCHEMA = "phase6mt-amazon-ipc-candidates-v1"
DEFAULT_OUT = "artifacts/phase6mt-amazon-ipc-candidates-20260810-01"
BOOT_REL = "decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log"
FOS_REL = "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"

HEADER_RE = re.compile(r"\s+(?:direct_method|virtual_method) #\d+: (\S+) (.+)$")


@dataclass(frozen=True)
class Candidate:
    key: str
    interface: str
    service_class: str
    service_name: str
    proxy_start: int
    proxy_end: int
    service_start: int
    service_end: int
    publication_start: int
    publication_end: int


CANDIDATES = (
    Candidate(
        "accessibility", "IAmazonAccessibilityManager",
        "AmazonAccessibilityManagerService.BinderService",
        "amazonaccessibilitymanager", 394117, 394235, 35287, 35344, 35427, 35435,
    ),
    Candidate(
        "activity", "IAmazonActivityManager",
        "AmazonActivityManagerService.BinderService",
        "amazonactivitymanager", 394353, 394854, 39645, 40680, 41078, 41084,
    ),
    Candidate(
        "device-policy", "IAmazonDevicePolicyManager",
        "AmazonDevicePolicyManagerService.BinderService",
        "amazondevicepolicymanager", 397105, 397251, 45935, 46107, 46142, 46157,
    ),
    Candidate(
        "window", "IAmazonWindowManager",
        "AmazonWindowManagerService.BinderService",
        "amazonwindowmanager", 400006, 400233, 56070, 56178, 56240, 56245,
    ),
    Candidate(
        "package", "IAmazonPackageManager",
        "AmazonPackageManagerService.BinderService",
        "amazonpackagemanager", 402917, 403367, 95866, 96036, 96131, 96137,
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_lines(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        return handle.read().split("\n")


def window(lines: list[str], start: int, end: int) -> str:
    return "\n".join(lines[start - 1:end])


def require_markers(lines: list[str], label: str, start: int, end: int, markers: list[str]) -> None:
    text = window(lines, start, end)
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"input drift for {label}:{start}-{end}; missing {missing}")


def method_blocks(lines: list[str], start: int, end: int) -> list[dict[str, object]]:
    heads: list[tuple[int, str, str]] = []
    for index in range(start - 1, end):
        match = HEADER_RE.match(lines[index])
        if match:
            heads.append((index, match.group(1), match.group(2)))
    blocks: list[dict[str, object]] = []
    for position, (index, name, descriptor) in enumerate(heads):
        next_index = heads[position + 1][0] if position + 1 < len(heads) else end
        blocks.append({
            "start": index + 1,
            "end": next_index,
            "name": name,
            "descriptor": descriptor,
            "text": "\n".join(lines[index:next_index]),
        })
    return blocks


def transaction_code(block: dict[str, object]) -> tuple[int | None, int | None]:
    rows = str(block["text"]).split("\n")
    for position, row in enumerate(rows):
        if "IBinder;.transact" not in row:
            continue
        registers = re.search(r"\{([^}]*)\}", row)
        if not registers:
            continue
        args = [item.strip() for item in registers.group(1).split(",")]
        if len(args) < 2:
            continue
        code_register = args[1]
        for previous in reversed(rows[max(0, position - 80):position]):
            match = re.search(r"const(?:/\w+)?\s+([vp]\d+), #int (-?\d+)", previous)
            if match and match.group(1) == code_register:
                return int(match.group(2)), int(block["start"]) + position
    return None, None


def const_strings(text: str) -> list[str]:
    return re.findall(r'const-string v\d+, "([^"]*)"', text)


def unique(values: list[str]) -> str:
    return "; ".join(dict.fromkeys(values)) if values else "none observed"


def permission_info(text: str) -> tuple[str, str]:
    strings = const_strings(text)
    literals = [value for value in strings if (
        "permission" in value.lower()
        or "MANAGE_USERS" in value
        or "ADD_RM_PKG_METADATA" in value
    )]
    calls: list[str] = []
    for marker in (
        "enforceCallingPermission",
        "enforceCallingOrSelfPermission",
        "checkCallingPermission",
        "checkCallingOrSelfPermission",
        "checkPermission",
    ):
        if marker in text:
            calls.append(marker)
    if "setUserRestrictionForUser" in text and "setUserRestrictionForUser" not in calls:
        calls.append("setUserRestrictionForUser helper")
    if not calls:
        if literals:
            return f"{unique(literals)} [external/helper call not in bounded method]", "external-helper"
        return "none observed in bounded BinderService method", "not-applicable"

    result_consumption = "not-applicable"
    rows = text.split("\n")
    for index, row in enumerate(rows):
        if "checkCallingPermission" in row or "checkCallingOrSelfPermission" in row:
            # A return value is consumed only when the immediately following
            # instruction is move-result*.  Looking farther ahead can
            # incorrectly attribute a later, unrelated result (for example
            # Binder.clearCallingIdentity()) to the permission check.
            following = rows[index + 1:index + 2]
            result_consumption = "consumed" if any("move-result" in item for item in following) else "not seen in adjacent instructions"
            break
    if any("checkCallingPermission" in call or "checkCallingOrSelfPermission" in call for call in calls):
        if result_consumption == "not seen in adjacent instructions":
            calls.append("return-value consumption not seen in adjacent instructions")
    if literals:
        return f"{unique(literals)} [{unique(calls)}]", result_consumption
    return f"permission/helper call present; literal unresolved [{unique(calls)}]", result_consumption


def identity_info(text: str) -> str:
    markers: list[str] = []
    for needle, label in (
        ("Binder;.getCallingUid", "Binder.getCallingUid"),
        ("Binder;.getCallingPid", "Binder.getCallingPid"),
        ("Binder;.getCallingUserHandle", "Binder.getCallingUserHandle"),
        ("clearCallingIdentity", "Binder.clearCallingIdentity"),
        ("restoreCallingIdentity", "Binder.restoreCallingIdentity"),
    ):
        if needle in text:
            markers.append(label)
    return unique(markers) if markers else "no caller-identity marker observed"


SINK_PATTERNS = (
    "setApplicationEnabledSetting", "setComponentEnabledSetting",
    "setHomeActivity", "replacePreferredActivity", "addPreferredActivity",
    "startActivity", "startProcessLocked", "killApp", "PackageManager",
    "ActivityManager", "RemoteCallbackList", "onActivityResume",
    "sendMessage", "setPipVisibility", "stopAppPinningMode",
    "setUserRestriction", "JournaledFile", "setAmazonMetadataForUser",
    "setAmazonFlagsForUser", "removeAmazonMetadataForUser",
    "removeAmazonFlagsForUser", "native", "MagnificationCanvas",
    "mLastActivity", "ComponentName",
)


HOME_PATTERNS = (
    "isOnHomeStack", "onActivityResume", "notifyActivitySwitch",
    "registerActivitySwitchObserver", "unregisterActivitySwitchObserver",
    "setHomeActivity", "replacePreferredActivity", "CATEGORY_HOME",
    "ACTION_MAIN", "com.amazon.firelauncher", "startHome",
)


PACKAGE_STATE_PATTERNS = (
    "setApplicationEnabledSetting", "setComponentEnabledSetting",
    "setHomeActivity", "replacePreferredActivity", "addPreferredActivity",
    "removeAmazonMetadataForUser", "setAmazonMetadataForUser",
    "removeAmazonFlagsForUser", "setAmazonFlagsForUser",
)


def classify(name: str, text: str, permission: str, permission_result: str) -> tuple[str, str]:
    if permission_result == "not seen in adjacent instructions" and "checkCallingPermission" in text:
        return "permission check result not consumed in bounded instructions; potential authorization anomaly, no HOME/package-state writer", "Strong evidence (bounded; not exploit proof)"
    if any(pattern in text for pattern in ("setHomeActivity", "replacePreferredActivity", "addPreferredActivity", "CATEGORY_HOME", "ACTION_MAIN")):
        return "direct HOME/package-state marker; method-level review required", "Strong evidence (bounded)"
    if any(pattern in text for pattern in PACKAGE_STATE_PATTERNS):
        return "Amazon package metadata/state surface; not shown as enabled-state or HOME writer", "Strong evidence (bounded)"
    if name in {"isOnHomeStack", "onActivityResume", "notifyActivitySwitch", "registerActivitySwitchObserver", "unregisterActivitySwitchObserver"}:
        return "HOME-adjacent observer/callback surface; no HOME selector", "Strong evidence (bounded)"
    if "none observed" not in permission:
        return "explicit permission/helper marker; no HOME/package-state writer", "Confirmed static"
    return "no permission marker in bounded method; caller reachability unresolved", "Unknown authorization (bounded)"


def build_inputs(root: Path) -> list[Path]:
    paths = [
        root / BOOT_REL,
        root / FOS_REL,
        root / "findings/phase-6mn-ipc-user-scope-closure.md",
        root / "findings/phase-6kv-pms-home-caller-closure.md",
        root / "findings/phase-6bk-evidence-index.md",
        root / "findings/phase-6mq-profile-launcher-helper-closure.md",
        root / "findings/phase-6mr-amazon-input-manager-static-closure.md",
        root / "work/luna_worker_phase6mp_inventory_20260810.md",
    ]
    optional = root / "work/luna_worker_phase6ms_inventory_20260810.md"
    if optional.is_file():
        paths.append(optional)
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing required inputs:\n" + "\n".join(map(str, missing)))
    return paths


def graph_text() -> str:
    return """flowchart TD
  P["Amazon AIDL Stub.Proxy"] -->|"IBinder.transact(code)"| E["published Amazon service"]
  E --> B["BinderService method"]
  B --> G["permission / caller identity markers"]
  B --> S["bounded sink or state access"]
  B -.-> H["No direct HOME selector in candidate slices"]
  B -.-> U["runtime handle, SELinux, native and UID reachability unresolved"]
"""


def write_text(path: Path, value: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]], force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--generated-date", default=str(date.today()))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    output = (args.output or root / DEFAULT_OUT).resolve()
    inputs = build_inputs(root)
    boot = root / BOOT_REL
    fos = root / FOS_REL
    boot_lines = read_lines(boot)
    fos_lines = read_lines(fos)
    for candidate in CANDIDATES:
        require_markers(boot_lines, f"{candidate.interface}.Stub.Proxy", candidate.proxy_start, candidate.proxy_end, [candidate.interface, "transact"])
        require_markers(fos_lines, candidate.service_class, candidate.service_start, candidate.service_end, [candidate.service_class])
        require_markers(fos_lines, f"{candidate.service_class}.publication", candidate.publication_start, candidate.publication_end, ["publishBinderService"])

    input_hashes = {str(path.relative_to(root)): sha256(path) for path in inputs}
    rows: list[dict[str, object]] = []
    evidence: dict[str, str] = {}
    candidate_summaries: list[dict[str, object]] = []

    for candidate in CANDIDATES:
        proxy_blocks = method_blocks(boot_lines, candidate.proxy_start, candidate.proxy_end)
        service_blocks = method_blocks(fos_lines, candidate.service_start, candidate.service_end)
        service_by_name = {str(block["name"]): block for block in service_blocks}
        remote_blocks = [block for block in proxy_blocks if str(block["name"]) not in {"<init>", "asBinder", "getInterfaceDescriptor"}]
        missing: list[str] = []
        for block in remote_blocks:
            name = str(block["name"])
            service = service_by_name.get(name)
            if service is None:
                missing.append(name)
                continue
            service_text = str(service["text"])
            tx, tx_line = transaction_code(block)
            permission, permission_result = permission_info(service_text)
            identity = identity_info(service_text)
            sinks = [pattern for pattern in SINK_PATTERNS if pattern in service_text]
            home_hits = [pattern for pattern in HOME_PATTERNS if pattern in service_text]
            state_hits = [pattern for pattern in PACKAGE_STATE_PATTERNS if pattern in service_text]
            classification, confidence = classify(name, service_text, permission, permission_result)
            rows.append({
                "candidate": candidate.key,
                "interface": candidate.interface,
                "published_service": candidate.service_name,
                "proxy_method": name,
                "descriptor": str(block["descriptor"]),
                "transaction_code": tx if tx is not None else "UNRESOLVED",
                "proxy_line": block["start"],
                "transaction_line": tx_line if tx_line is not None else "UNRESOLVED",
                "implementation_method": f"{candidate.service_class}.{name}",
                "implementation_range": f"{service['start']}-{service['end']}",
                "permission_or_gate": permission,
                "permission_result_consumption": permission_result,
                "identity_markers": identity,
                "sink_markers": unique(sinks),
                "home_markers": unique(home_hits),
                "package_state_markers": unique(state_hits),
                "caller_reachability": "not established from proxy/publication alone",
                "classification": classification,
                "confidence": confidence,
            })
        candidate_summaries.append({
            "candidate": candidate.key,
            "interface": candidate.interface,
            "published_service": candidate.service_name,
            "proxy_remote_method_count": len(remote_blocks),
            "service_method_count": len(service_blocks) - 1,
            "unmatched_proxy_methods": missing,
            "proxy_range": f"{candidate.proxy_start}-{candidate.proxy_end}",
            "service_range": f"{candidate.service_start}-{candidate.service_end}",
            "publication_range": f"{candidate.publication_start}-{candidate.publication_end}",
        })
        evidence[f"{candidate.key}-proxy.txt"] = window(boot_lines, candidate.proxy_start, candidate.proxy_end)
        evidence[f"{candidate.key}-service.txt"] = window(fos_lines, candidate.service_start, candidate.service_end)
        evidence[f"{candidate.key}-publication.txt"] = window(fos_lines, candidate.publication_start, candidate.publication_end)

    if any(row["transaction_code"] == "UNRESOLVED" for row in rows):
        raise RuntimeError("one or more proxy transaction codes are unresolved")
    if any(summary["unmatched_proxy_methods"] for summary in candidate_summaries):
        raise RuntimeError("one or more proxy methods have no matching service method")

    report_path = root / "findings/phase-6mt-amazon-ipc-candidate-closure.md"
    evidence_path = root / "findings/phase-6mt-evidence-index.md"
    table_path = root / "output/tables/phase6mt-amazon-ipc-candidates-20260810-01.csv"
    graph_path = root / "output/call-graphs/phase6mt-amazon-ipc-candidates-20260810-01.mmd"
    artifact_files = [
        output / "candidate-summary.csv",
        output / "method-matrix.csv",
        output / "input-manifest.csv",
        output / "summary.json",
        output / "route-flow.mmd",
        output / "sha256sums.txt",
    ] + [output / "evidence" / name for name in sorted(evidence)]
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
        print(f"candidate_count={len(CANDIDATES)}")
        print(f"remote_method_count={len(rows)}")
        for summary in candidate_summaries:
            print(f"candidate={summary['candidate']} methods={summary['proxy_remote_method_count']} service={summary['published_service']}")
        print("outputs:")
        for path in generated:
            print(f"  {path}")
        return 0

    existing = [path for path in generated if path.exists()]
    if existing and not args.force:
        raise SystemExit("refusing to overwrite existing outputs:\n" + "\n".join(map(str, existing)))
    output.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    write_csv(output / "method-matrix.csv", fields, rows, args.force)
    write_csv(output / "candidate-summary.csv", list(candidate_summaries[0].keys()), candidate_summaries, args.force)
    write_csv(output / "input-manifest.csv", ["path", "sha256", "size"], [
        {"path": str(path.relative_to(root)), "sha256": sha256(path), "size": path.stat().st_size}
        for path in inputs
    ], args.force)
    for name, content in evidence.items():
        write_text(output / "evidence" / name, content, args.force)
    write_text(output / "route-flow.mmd", graph_text(), args.force)

    summary = {
        "schema": SCHEMA,
        "generated_date": args.generated_date,
        "scope": "host-only preserved disassembly audit",
        "candidate_count": len(CANDIDATES),
        "remote_method_count": len(rows),
        "candidate_summaries": candidate_summaries,
        "device_contacted": False,
        "binder_or_service_call": False,
        "input_injection": False,
        "ioctl": False,
        "mutation": False,
        "reboot": False,
        "root_or_exploit": False,
        "conclusion": "Five Amazon IPC proxy/publication surfaces are mapped to bounded BinderService methods; no candidate is proven to be a shell-accessible HOME or Fire Launcher state writer from this static corpus alone",
    }
    write_text(output / "summary.json", json.dumps(summary, indent=2, sort_keys=True) + "\n", args.force)

    table = "\n".join([
        "| Candidate | Interface | Service | Remote methods | Unmatched |",
        "|---|---|---|---:|---|",
    ] + [
        f"| `{item['candidate']}` | `{item['interface']}` | `{item['published_service']}` | "
        f"{item['proxy_remote_method_count']} | {', '.join(item['unmatched_proxy_methods']) or 'none'} |"
        for item in candidate_summaries
    ])
    method_lines = [
        "| Candidate | Method | Tx | Permission/gate | Identity | HOME/package-state markers | Classification |",
        "|---|---|---:|---|---|---|---|",
    ]
    for row in rows:
        method_lines.append(
            f"| `{row['candidate']}` | `{row['proxy_method']}` | {row['transaction_code']} | {row['permission_or_gate']} | "
            f"{row['identity_markers']} | {row['home_markers']} / {row['package_state_markers']} | {row['classification']} |"
        )
    report = f"""# Phase 6MT — Amazon IPC candidate closure

Date: {args.generated_date}
Schema: `{SCHEMA}`

## Scope and safety

This is host-only analysis of preserved PS7331 disassembly and existing
reports. No device connection, ADB command, Binder/service call, private
transaction, ioctl, input injection, settings/package mutation, reboot,
OTA/recovery operation, exploit, Root attempt, or partition write was done.

The interface/publication mapping proves only a static system-service surface;
it does not prove that shell or an ordinary APK can obtain a handle.

## Executive result

**已證實（static）：** five proxy interfaces map to their corresponding
Amazon `BinderService` methods and published service names. The machine-readable
matrix records each transaction code, method range, permission marker, caller
identity marker, and bounded sink.

**高可信推論（bounded）：** the candidate slices contain no direct
`setHomeActivity`, `replacePreferredActivity`, `CATEGORY_HOME`,
`ACTION_MAIN`, or `com.amazon.firelauncher` writer. `IAmazonActivityManager`
does contain HOME-adjacent observation/callback methods such as
`isOnHomeStack`, `onActivityResume`, and `registerActivitySwitchObserver`;
these update/observe activity state but do not select a HOME component in the
bounded methods.

**已證實（static）：** explicit Amazon permission markers are present on many
mutating or callback methods, including accessibility magnification,
activity/PiP/prewarm/observer paths, DPM helper paths, and package metadata
writers. The exact caller reachability and effective UID remain separate.

**待驗證：** methods with no local permission marker (notably selected window,
activity callback, and package proxy methods) require service-handle, SELinux,
caller, and surrounding-class analysis before any authorization conclusion.
Missing local markers are not treated as a bypass.

**因風險拒絕測試：** no `service call`, guessed transaction, private API
replay, input or package-state mutation was attempted. Such actions are not
needed to answer the bounded static question and could alter system control.

## Notable bounded authorization anomaly

`preWarmApplicationForUser` invokes `Context.checkCallingPermission` for
`com.amazon.permission.APP_PREWARM` at
`fosservices/disassembly.log:40473`. The immediately following instruction is
`Binder.clearCallingIdentity` at `:40474`; no adjacent `move-result*` consumes
the permission result in the preserved method block. This is **Strong evidence
(bounded; not exploit proof)** of a local authorization-check anomaly. The
method still requires a reachable service handle, accepts package/user inputs,
and delegates into process-start logic; no HOME or Fire Launcher writer is
present. No transaction replay is justified or performed.

## Candidate summary

{table}

## Method matrix

{chr(10).join(method_lines)}

## Decision boundary for HOME research

```text
Stub.Proxy → published service → BinderService method
  → local permission/identity checks (where observed)
  → callback/state/native/package-metadata sink
  → [no direct HOME component writer in these bounded slices]
```

The results narrow, but do not eliminate, other surfaces outside these class
ranges: caller-side proxy invocations, native code, framework LocalServices,
system-server call sites, policy/SELinux, and Amazon services not represented
by the five selected interfaces.

## Inputs

```json
{json.dumps(input_hashes, indent=2, sort_keys=True)}
```

## Reproduction

```sh
python3 tools/scripts/audit_phase6mt_amazon_ipc_candidates.py --dry-run
python3 tools/scripts/audit_phase6mt_amazon_ipc_candidates.py
```

Generated artifact: `artifacts/phase6mt-amazon-ipc-candidates-20260810-01`.
"""
    write_text(report_path, report, args.force)
    write_text(graph_path, graph_text(), args.force)
    write_csv(table_path, fields, rows, args.force)

    evidence = f"""# Phase 6MT evidence index — Amazon IPC candidate closure

Generated: {args.generated_date}
Test ID: `PHASE6MT-STATIC-20260810-01`
Scope: host-only; no device/Binder/ioctl/mutation/reboot.

## 6MT-E01 — proxy-to-implementation mapping

- Source: `{BOOT_REL}` and `{FOS_REL}` at the candidate ranges recorded in `candidate-summary.csv`.
- Observed: {len(rows)} remote methods across {len(CANDIDATES)} interfaces map to service methods; no unmatched proxy method remains.
- Interpretation: interface shape and transaction mapping are reproducible from preserved disassembly.
- Confidence: Confirmed static

## 6MT-E02 — permission and identity matrix

- Source: bounded `BinderService` method blocks in the artifact evidence directory.
- Observed: permission/helper calls, literals, return-value consumption markers, Binder identity calls, and sinks are recorded per method.
- Interpretation: absence of a local marker is an unresolved authorization question, not proof of shell access.
- Confidence: Confirmed static / bounded

## 6MT-E03 — HOME boundary

- Source: all five service ranges.
- Observed: no direct HOME resolver/preferred/Fire Launcher writer token in the candidate slices; activity observation methods are recorded separately.
- Interpretation: these bounded candidates do not close the HOME selection path.
- Confidence: Strong evidence (bounded)

## 6MT-E04 — prewarm permission-result observation

- Source: `fosservices/disassembly.log:40453-40534`, especially `:40473-40474`.
- Observed: `checkCallingPermission("com.amazon.permission.APP_PREWARM")` is
  followed immediately by `Binder.clearCallingIdentity`; the bounded block has
  no adjacent `move-result*` for that check.
- Interpretation: a static authorization anomaly is present, but service
  handle reachability, caller identity, surrounding validation, and impact are
  unresolved. It is not an exploit or HOME replacement finding.
- Confidence: Strong evidence (bounded; not exploit proof)

## Safety disposition

No device command, `service call`, unknown transaction, private API replay,
input injection, package/settings mutation, Fire Launcher state change, Root or
exploit execution, OTA/recovery/fastboot action, or partition write was done.
"""
    write_text(evidence_path, evidence, args.force)

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
        "candidate_count": len(CANDIDATES),
        "remote_method_count": len(rows),
        "device_contacted": False,
        "binder_or_service_call": False,
        "mutation": False,
        "reboot": False,
        "sha256_manifest": str(output / "sha256sums.txt"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
