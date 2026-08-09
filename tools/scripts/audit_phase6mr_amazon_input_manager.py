#!/usr/bin/env python3
"""Build a host-only IAmazonInputManager caller/sink matrix for PS7331.

The audit parses preserved AIDL-style proxy disassembly and the matching
AmazonInputManagerService.BinderService implementation.  It maps method names
to transaction codes, records bounded permission/identity/sink markers, and
keeps native enforcement unresolved where the Java disassembly does not prove
it.  It never contacts a device, invokes Binder, opens an input node, runs an
ioctl, injects an event, or mutates device state.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path


SCHEMA = "phase6mr-amazon-input-manager-v1"
DEFAULT_OUT = "artifacts/phase6mr-amazon-input-manager-20260810-01"
BOOT_REL = "decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log"
FOS_REL = "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"

PROXY_RANGE = (388887, 389899)
SERVICE_RANGE = (19198, 20547)
CHECK_INJECT_RANGE = (21718, 21776)
CHECK_PERMISSION_RANGE = (21775, 21794)
PUBLISH_RANGE = (22640, 22656)

HEADER_RE = re.compile(r"\s+(?:direct_method|virtual_method) #\d+: (\S+) (.+)$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_lines(path: Path) -> list[str]:
    # Do not use splitlines(): the preserved disassembly includes bare CR
    # bytes, while the line references are LF-based `nl -ba` references.
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        return handle.read().split("\n")


def window(lines: list[str], start: int, end: int) -> str:
    return "\n".join(lines[start - 1:end])


def require_markers(lines: list[str], label: str, start: int, end: int, markers: list[str]) -> None:
    text = window(lines, start, end)
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"input drift for {label}:{start}-{end}; missing {missing}")


def parse_method_blocks(lines: list[str], start: int, end: int) -> list[dict[str, object]]:
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
    text = str(block["text"])
    rows = text.split("\n")
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
            match = re.search(r"const(?:/\w+)?\s+(v\d+), #int (-?\d+)", previous)
            if match and match.group(1) == code_register:
                # The absolute source line is recovered from the block start.
                absolute = int(block["start"]) + position
                return int(match.group(2)), absolute
    return None, None


def const_strings(text: str) -> list[str]:
    return re.findall(r'const-string v\d+, "([^"]*)"', text)


def marker_list(text: str, markers: list[str]) -> list[str]:
    return [marker for marker in markers if marker in text]


def build_inputs(root: Path) -> list[Path]:
    paths = [
        root / BOOT_REL,
        root / FOS_REL,
        root / "findings/phase-6aj-input-home-boundary.md",
        root / "artifacts/phase6aj/input-home-boundary-20260805-05/input-home-boundary.csv",
        root / "findings/phase-6mn-ipc-user-scope-closure.md",
        root / "work/luna_worker_phase6mp_inventory_20260810.md",
    ]
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing required inputs:\n" + "\n".join(map(str, missing)))
    return paths


def validate(root: Path) -> tuple[Path, Path, list[str], list[str], list[dict[str, object]], list[dict[str, object]]]:
    boot = root / BOOT_REL
    fos = root / FOS_REL
    boot_lines = read_lines(boot)
    fos_lines = read_lines(fos)

    require_markers(boot_lines, "IAmazonInputManager.Proxy", *PROXY_RANGE, [
        "IAmazonInputManager.Stub.Proxy",
        "virtual_methods=28",
        "createKeyboardDevice ()Z",
        "inject (IIII)I",
        "unRegisterNextKeyEventListener",
    ])
    require_markers(fos_lines, "AmazonInputManagerService.BinderService", *SERVICE_RANGE, [
        "AmazonInputManagerService.BinderService",
        "createKeyboardDevice ()Z",
        "inject (IIII)I",
        "unRegisterNextKeyEventListener",
    ])
    require_markers(fos_lines, "checkInjectEventsPermission", *CHECK_INJECT_RANGE, [
        "checkInjectEventsPermission (II)Z",
        "android.permission.INJECT_EVENTS",
        "com.amazon.permission.INJECT_EVENTS",
    ])
    require_markers(fos_lines, "checkPermission", *CHECK_PERMISSION_RANGE, [
        "checkPermission (Ljava/lang/String;)V",
        "checkCallingOrSelfPermission",
        "SecurityException",
    ])
    require_markers(fos_lines, "onStart", *PUBLISH_RANGE, [
        "onStart ()V",
        'const-string v0, "amazon_input"',
        "publishBinderService",
    ])

    proxy_blocks = parse_method_blocks(boot_lines, *PROXY_RANGE)
    service_blocks = parse_method_blocks(fos_lines, *SERVICE_RANGE)
    return boot, fos, boot_lines, fos_lines, proxy_blocks, service_blocks


def permission_for(service_text: str) -> str:
    permissions = [
        value for value in const_strings(service_text)
        if "permission" in value.lower() or "PERMISSION" in value
    ]
    if "checkCallingOrSelfPermission" in service_text:
        if permissions:
            return "; ".join(dict.fromkeys(permissions))
        return "private permission helper; literal unresolved in this method block"
    if "checkInjectEventsPermission" in service_text:
        return "checkInjectEventsPermission helper (callsite marker)"
    return "none observed in BinderService method block"


def identity_for(name: str, text: str) -> str:
    markers = []
    if "Binder;.getCallingPid" in text:
        markers.append("Binder.getCallingPid")
    if "Binder;.getCallingUid" in text:
        markers.append("Binder.getCallingUid")
    if "getCallingUid" in text and "Binder;.getCallingUid" not in text:
        markers.append("getCallingUid")
    if "clearCallingIdentity" in text:
        markers.append("clearCallingIdentity")
    if "restoreCallingIdentity" in text:
        markers.append("restoreCallingIdentity")
    if not markers:
        return "no caller-identity marker observed"
    return "; ".join(markers)


def sink_for(name: str, text: str) -> str:
    patterns = [
        "nativeCreateKeyboardDevice",
        "nativeCreateMouseDevice",
        "nativeDispose",
        "nativeInjectSequence",
        "nativeInject",
        "RemoteCallbackList",
        "KeyEventCallback",
        "IKeyEventCallback",
        "IKeyEventIdleCallback",
        "IKeyEventNextCallback",
        "mInterceptKeyMap",
        "mCurrentPackageName",
        "mBlockListEntries",
        "setInputFilter",
        "registerTouchListener",
        "setLedStateImp",
        "AudioManager",
        "mLastEventTime",
        "mToggleBitButtonMap",
        "mToggleBitRegister",
    ]
    hits = [pattern for pattern in patterns if pattern in text]
    return "; ".join(dict.fromkeys(hits)) if hits else "return/state-only or sink unresolved in method block"


def home_relevance(name: str, text: str) -> str:
    if name in {"inject", "injectSequence"}:
        return "indirect input injection; could carry a key code if authorized, but no HOME resolver/component writer"
    if "KeyEvent" in name or "InputFilter" in name or "Listener" in name or "Interceptor" in name:
        return "indirect key/callback path; no HOME resolver/component writer"
    if "Volume" in name:
        return "not HOME; volume/audio path"
    return "not HOME; no resolver/preferred/component writer in method block"


def classify(name: str, text: str) -> str:
    if name in {"inject", "injectSequence"}:
        return "Strong evidence: Java Binder block has caller pid/uid and native sink; direct permission/native enforcement unresolved"
    if "checkCallingOrSelfPermission" in text:
        return "Confirmed: explicit Amazon permission check"
    if name == "registerKeyEventInterceptor":
        return "Confirmed: permission plus system-app/whitelist/foreground gates"
    return "Confirmed static method mapping; no direct permission marker in this bounded block"


def graph_text() -> str:
    return """flowchart TD
  P["IAmazonInputManager.Stub.Proxy\n28 virtual methods\n26 remote + 2 inherited"] -->|"Binder transact"| S["published service: amazon_input"]
  S --> B["AmazonInputManagerService.BinderService"]
  B --> I["inject / injectSequence\nBinder calling pid+uid"]
  I --> N["nativeInject*\nJava/native enforcement unresolved"]
  B --> K["register key listeners/interceptor"]
  K --> G["GET_KEYEVENTS + system-app/whitelist/foreground checks"]
  G --> C["callback / interceptor state"]
  B --> D["create/destroy virtual input devices"]
  D --> F["nativeCreate* / nativeDispose"]
  B --> E["event-register methods"]
  E --> Q["ACCESS_EVENT_REGISTER"]
  B -.-> H["No direct HOME resolver, preferred-activity, or Fire Launcher writer in bounded BinderService slice"]
"""


def report_text(root: Path, boot: Path, fos: Path, input_hashes: dict[str, str], rows: list[dict[str, object]], generated_date: str) -> str:
    permission_gap = any(row["method"] in {"inject", "injectSequence"} and "unresolved" in str(row["permission_check"]).lower() for row in rows)
    table_lines = [
        "| Method | Tx | Permission / gate | Identity | Sink | HOME relevance | Classification |",
        "|---|---:|---|---|---|---|---|",
    ]
    for row in rows:
        table_lines.append(
            f"| `{row['method']}` | {row['transaction_code']} | {row['permission_check']} | "
            f"{row['identity_handling']} | {row['sink']} | {row['home_relevance']} | {row['classification']} |"
        )
    table = "\n".join(table_lines)
    gap_result = "**已證實（bounded）：**" if permission_gap else "**待驗證：**"
    return f"""# Phase 6MR — IAmazonInputManager static caller/sink closure

Date: {generated_date}
Schema: `{SCHEMA}`

## Scope and safety

This is **host-only static analysis** of preserved PS7331 boot-framework and
fosservices disassembly. No ADB, Binder/service call, private transaction,
input injection, device-node access, ioctl, settings/package mutation, reboot,
OTA/recovery, exploit, Root attempt, or partition write was performed.

## Executive result

**已證實：** `IAmazonInputManager.Stub.Proxy` contains 28 virtual methods;
two are inherited Binder helpers (`asBinder` and `getInterfaceDescriptor`) and
the parser maps 26 remote methods to transaction codes 1–26. The service publishes
the matching Binder endpoint as `amazon_input` in
`AmazonInputManagerService.onStart()`.

**已證實：** the corresponding `BinderService` methods are a key/input
control surface. Key-list/listener/interceptor methods perform explicit
`com.amazon.permission.GET_KEYEVENTS` checks. Event-register methods perform
`com.amazon.permission.ACCESS_EVENT_REGISTER` checks. The interceptor method
also contains the bounded system-app, whitelist, and foreground checks recorded
in the method body.

{gap_result} `inject()` and `injectSequence()` read Binder calling PID/UID and
pass them into `nativeInject`/`nativeInjectSequence`, but their Binder method
windows do not contain a direct permission call. A separate
`checkInjectEventsPermission(II)` helper exists and checks Android and Amazon
inject-event permissions plus a system-UID condition, but no callsite to that
helper was found inside the two bounded Binder method blocks. Native-side
enforcement and any other caller remain **待驗證**; this is not evidence of an
accessible or safe shell route.

**高可信推論（bounded）：** the `AmazonInputManagerService.BinderService`
slice has no `setHomeActivity`, preferred-activity writer, `ACTION_MAIN`,
`CATEGORY_HOME`, or `com.amazon.firelauncher` token. Input callbacks can be
HOME-adjacent only after their authorization/whitelist/foreground conditions;
the slice does not select the HOME component.

**已排除（bounded）：** the presence of `amazon_input`, its proxy, or its
native injection names alone does not establish a shell-accessible HOME
replacement or a Fire Launcher selector.

**因風險拒絕測試：** no `service call amazon_input`, guessed transaction,
`nativeInject*`, device-node, or input event was attempted. Such actions could
alter input routing or foreground control and would not be a necessary test of
the static question.

## Method matrix

{table}

The complete machine-readable matrix is
`artifacts/phase6mr-amazon-input-manager-20260810-01/method-matrix.csv`.

## Exact source anchors

| Evidence | File / lines | Meaning | Classification |
|---|---|---|---|
| 6MR-E01 | `{root.relative_to(root) / BOOT_REL}:{PROXY_RANGE[0]}-{PROXY_RANGE[1]}` | Proxy class, 28 virtual methods, transaction code constants | Confirmed static |
| 6MR-E02 | `{FOS_REL}:{SERVICE_RANGE[0]}-{SERVICE_RANGE[1]}` | BinderService implementations | Confirmed static |
| 6MR-E03 | `{FOS_REL}:{CHECK_INJECT_RANGE[0]}-{CHECK_INJECT_RANGE[1]}` | Android/Amazon inject permission helper and UID condition | Confirmed static |
| 6MR-E04 | `{FOS_REL}:{CHECK_PERMISSION_RANGE[0]}-{CHECK_PERMISSION_RANGE[1]}` | generic `checkCallingOrSelfPermission` → SecurityException helper | Confirmed static |
| 6MR-E05 | `{FOS_REL}:{PUBLISH_RANGE[0]}-{PUBLISH_RANGE[1]}` | `amazon_input` Binder publication | Confirmed static |
| 6MR-E06 | `{FOS_REL}:{SERVICE_RANGE[0]}-{SERVICE_RANGE[1]}` | bounded absence of HOME/preferred/Fire component tokens | Strong evidence (bounded) |

## Decision points relevant to HOME

```text
IAmazonInputManager.Proxy
  → IBinder.transact(code)
  → ServiceManager endpoint "amazon_input"
  → BinderService method
  → permission / identity / whitelist checks where present
  → input callback or native input sink
  → [no HOME resolver or preferred-activity writer in this slice]
```

`registerKeyEventInterceptor` is the closest input-side HOME boundary: the
method checks `GET_KEYEVENTS`, resolves the caller/package context, requires a
system-app condition, checks whitelist entries, and requires the caller's
foreground package in the preserved code. This can explain why privileged
Amazon components may observe or consume a key, but it does not prove a direct
Fire Launcher launch.

`inject` and `injectSequence` are distinct: they route event data to native
input devices. Their Java blocks carry Binder caller identity into the native
call, while the separate permission helper is not called in those blocks. The
native implementation, SELinux device access, service-handle availability, and
runtime behavior remain unobserved. Do not infer an exploit, input bypass, or
HOME replacement from this static gap.

## Scope limits and next minimal target

The matrix closes this interface's proxy→transaction→BinderService mapping and
records its bounded authorization/sink shape. It does not prove which clients
obtain the service handle at runtime, which UID owns the service process, or
what the native implementation enforces. The next safe target, if research
continues, is host-only mapping of the remaining unindexed Amazon service
interfaces; no private transaction replay is justified by this result.

## Input hashes

```text
{json.dumps(input_hashes, indent=2, sort_keys=True)}
```

## Reproduction

```sh
python3 tools/scripts/audit_phase6mr_amazon_input_manager.py --dry-run
python3 tools/scripts/audit_phase6mr_amazon_input_manager.py
```

Generated artifact: `artifacts/phase6mr-amazon-input-manager-20260810-01`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--generated-date", default=str(date.today()))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    output = (args.output or (root / DEFAULT_OUT)).resolve()
    inputs = build_inputs(root)
    boot, fos, boot_lines, fos_lines, proxy_blocks, service_blocks = validate(root)
    input_hashes = {str(path.relative_to(root)): sha256(path) for path in inputs}

    service_by_name = {str(block["name"]): block for block in service_blocks}
    rows: list[dict[str, object]] = []
    for block in proxy_blocks:
        name = str(block["name"])
        descriptor = str(block["descriptor"])
        code, tx_line = transaction_code(block)
        if name in {"<init>", "asBinder", "getInterfaceDescriptor"}:
            continue
        service = service_by_name.get(name)
        if service is None:
            raise RuntimeError(f"proxy method has no matching BinderService method: {name}")
        service_text = str(service["text"])
        permission = permission_for(service_text)
        if name in {"inject", "injectSequence"}:
            permission += "; separate checkInjectEventsPermission helper exists; no callsite in bounded method block"
        row = {
            "interface": "IAmazonInputManager",
            "proxy_method": name,
            "method": name,
            "descriptor": descriptor,
            "transaction_code": code if code is not None else "UNRESOLVED",
            "proxy_line": block["start"],
            "transaction_line": tx_line if tx_line is not None else "UNRESOLVED",
            "published_service": "amazon_input",
            "implementation_method": f"AmazonInputManagerService.BinderService.{name}",
            "implementation_range": f"{service['start']}-{service['end']}",
            "permission_check": permission,
            "identity_handling": identity_for(name, service_text),
            "user_package_argument": "Binder caller PID/UID observed" if "getCalling" in service_text else "no explicit user/package argument observed",
            "sink": sink_for(name, service_text),
            "home_relevance": home_relevance(name, service_text),
            "caller_evidence": "proxy method + published Binder endpoint; runtime caller not established",
            "classification": classify(name, service_text),
        }
        rows.append(row)

    if len(rows) != 26:
        raise RuntimeError(f"expected 26 remote methods, parsed {len(rows)}")
    if sorted(int(row["transaction_code"]) for row in rows if row["transaction_code"] != "UNRESOLVED") != list(range(1, 27)):
        raise RuntimeError("transaction code set drifted; expected 1..26")

    class_text = window(fos_lines, *SERVICE_RANGE)
    home_tokens = [
        "setHomeActivity", "replacePreferredActivity", "addPreferredActivity",
        "ACTION_MAIN", "CATEGORY_HOME", "com.amazon.firelauncher", "startHomeActivity",
        "startHomeOnAllDisplays", "resolveActivity", "resolveIntent",
    ]
    bounded_negative = {token: [
        SERVICE_RANGE[0] + index for index, line in enumerate(class_text.split("\n")) if token in line
    ] for token in home_tokens}
    inject_helper_in_binder = {
        name: "checkInjectEventsPermission" in str(service_by_name[name]["text"])
        for name in ("inject", "injectSequence")
    }

    report_path = root / "findings/phase-6mr-amazon-input-manager-static-closure.md"
    evidence_path = root / "findings/phase-6mr-evidence-index.md"
    table_path = root / "output/tables/phase6mr-amazon-input-manager-20260810-01.csv"
    graph_path = root / "output/call-graphs/phase6mr-amazon-input-manager-20260810-01.mmd"
    artifact_files = [
        output / "method-matrix.csv",
        output / "proxy-transaction-map.csv",
        output / "input-manifest.csv",
        output / "summary.json",
        output / "route-flow.mmd",
        output / "evidence/proxy-class.txt",
        output / "evidence/binder-service-class.txt",
        output / "evidence/inject-permission-helper.txt",
        output / "evidence/generic-permission-helper.txt",
        output / "evidence/service-publication.txt",
        output / "evidence/home-token-scan.txt",
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
        print("input_injection=false")
        print("mutation=false")
        print("reboot=false")
        print("parsed_remote_methods=26")
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
    write_csv(output / "proxy-transaction-map.csv", [
        "method", "descriptor", "transaction_code", "proxy_line", "transaction_line", "implementation_range"
    ], [{
        "method": row["method"],
        "descriptor": row["descriptor"],
        "transaction_code": row["transaction_code"],
        "proxy_line": row["proxy_line"],
        "transaction_line": row["transaction_line"],
        "implementation_range": row["implementation_range"],
    } for row in rows], args.force)
    write_csv(output / "input-manifest.csv", ["path", "sha256", "size"], [{
        "path": str(path.relative_to(root)), "sha256": sha256(path), "size": path.stat().st_size
    } for path in inputs], args.force)

    snippets = {
        "proxy-class.txt": window(boot_lines, *PROXY_RANGE),
        "binder-service-class.txt": window(fos_lines, *SERVICE_RANGE),
        "inject-permission-helper.txt": window(fos_lines, *CHECK_INJECT_RANGE),
        "generic-permission-helper.txt": window(fos_lines, *CHECK_PERMISSION_RANGE),
        "service-publication.txt": window(fos_lines, *PUBLISH_RANGE),
        "home-token-scan.txt": json.dumps({
            "bounded_range": f"{SERVICE_RANGE[0]}-{SERVICE_RANGE[1]}",
            "tokens": bounded_negative,
            "inject_helper_call_in_binder_method_blocks": inject_helper_in_binder,
        }, indent=2, sort_keys=True) + "\n",
    }
    for name, text in snippets.items():
        write_text(output / "evidence" / name, text, args.force)
    write_text(output / "route-flow.mmd", graph_text(), args.force)

    summary = {
        "schema": SCHEMA,
        "generated_date": args.generated_date,
        "scope": "host-only preserved disassembly audit",
        "input_count": len(inputs),
        "remote_method_count": len(rows),
        "proxy_virtual_method_count": 28,
        "transaction_code_range": "1..26",
        "published_service": "amazon_input",
        "device_contacted": False,
        "binder_or_service_call": False,
        "input_injection": False,
        "ioctl": False,
        "mutation": False,
        "reboot": False,
        "root_or_exploit": False,
        "bounded_home_token_scan": bounded_negative,
        "inject_helper_call_in_binder_method_blocks": inject_helper_in_binder,
        "conclusion": "Input Binder surface is statically mapped; inject native enforcement and runtime caller reachability remain unresolved; no direct HOME writer is present in the bounded BinderService slice",
    }
    write_json(output / "summary.json", summary, args.force)
    write_text(report_path, report_text(root, boot, fos, input_hashes, rows, args.generated_date), args.force)
    write_text(graph_path, graph_text(), args.force)
    write_csv(table_path, fields, rows, args.force)

    evidence = f"""# Phase 6MR evidence index — IAmazonInputManager static closure

Generated: {args.generated_date}
Test ID: `PHASE6MR-STATIC-20260810-01`
Scope: host-only; no device/Binder/input/ioctl/mutation/reboot.

## 6MR-E01 — proxy and transaction map

- Source: `{BOOT_REL}:{PROXY_RANGE[0]}-{PROXY_RANGE[1]}`
- SHA-256: `{sha256(boot)}`
- Command: `python3 tools/scripts/audit_phase6mr_amazon_input_manager.py`
- Observed: 28 virtual methods including `asBinder` and `getInterfaceDescriptor`; 26 remote methods carry codes 1–26.
- Interpretation: proxy/transaction shape is statically reproducible.
- Confidence: Confirmed static
- Related hypothesis: the interface is a HOME resolver writer — not shown.

## 6MR-E02 — BinderService implementation map

- Source: `{FOS_REL}:{SERVICE_RANGE[0]}-{SERVICE_RANGE[1]}`
- SHA-256: `{sha256(fos)}`
- Command: same host-only audit
- Observed: all 26 proxy remote method names have matching `AmazonInputManagerService.BinderService` method blocks.
- Interpretation: interface-to-implementation mapping is name/descriptor aligned in the preserved disassembly.
- Confidence: Confirmed static
- Related hypothesis: proxy existence proves caller reachability — Disproved.

## 6MR-E03 — injection permission helper

- Source: `{FOS_REL}:{CHECK_INJECT_RANGE[0]}-{CHECK_INJECT_RANGE[1]}`
- SHA-256: `{sha256(fos)}`
- Observed: helper reads Binder calling PID/UID, checks `android.permission.INJECT_EVENTS` and `com.amazon.permission.INJECT_EVENTS`, and allows system UID condition on the shown branch.
- Interpretation: a separate native/injection authorization helper exists.
- Confidence: Confirmed static
- Related hypothesis: helper call is proven from `inject()` — not proven; bounded callsite scan is negative.

## 6MR-E04 — generic permission helper

- Source: `{FOS_REL}:{CHECK_PERMISSION_RANGE[0]}-{CHECK_PERMISSION_RANGE[1]}`
- SHA-256: `{sha256(fos)}`
- Observed: `checkCallingOrSelfPermission` followed by `SecurityException`.
- Interpretation: explicit permission enforcement pattern used by selected event-registration methods.
- Confidence: Confirmed static

## 6MR-E05 — service publication

- Source: `{FOS_REL}:{PUBLISH_RANGE[0]}-{PUBLISH_RANGE[1]}`
- SHA-256: `{sha256(fos)}`
- Observed: Binder endpoint `amazon_input` is published.
- Interpretation: published service name is known; shell/ordinary-app handle availability is not inferred.
- Confidence: Confirmed static

## 6MR-E06 — bounded HOME negative

- Source: `{FOS_REL}:{SERVICE_RANGE[0]}-{SERVICE_RANGE[1]}`
- SHA-256: `{sha256(fos)}`
- Observed: no direct HOME resolver/preferred/Fire Launcher token in the BinderService slice.
- Interpretation: input service is not shown as the direct HOME selection writer in this corpus slice.
- Confidence: Strong evidence (bounded)

## Safety disposition

`service call`, guessed transaction codes, `nativeInject*`, input-device access,
ioctl, Accessibility injection, package/settings mutation, Fire Launcher state
changes, Root/exploit execution, OTA/recovery/fastboot, and partition writes
were not performed and remain outside this static closure.
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
        "remote_method_count": len(rows),
        "device_contacted": False,
        "binder_or_service_call": False,
        "input_injection": False,
        "mutation": False,
        "reboot": False,
        "sha256_manifest": str(output / "sha256sums.txt"),
    }, indent=2))
    return 0


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


if __name__ == "__main__":
    raise SystemExit(main())
