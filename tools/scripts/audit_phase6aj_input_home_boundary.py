#!/usr/bin/env python3
"""Close the saved AmazonInputManagerService/Home-key boundary.

This audit is deliberately host-only.  It reads preserved Fire OS VDEX
disassembly, the saved Alexa caller source, and existing read-only service/AVC
captures.  It never contacts ADB, sends a Binder transaction, injects input,
replays a broadcast, changes package state, or writes a device file.

The audit also records the already-registered BootAfterSystemOTAReceiver item
as a related lifecycle surface.  That receiver is not re-triggered here; its
analysis remains the static-only Phase 6AG/6R evidence chain.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FOS_REL = Path("decompiled/baksmali/vdexExtractor/fosservices/disassembly.log")
BOOT_REL = Path("decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log")
SERVICE_LIST_REL = Path(
    "artifacts/phase6j/phase6j-service-visibility-20260805-01/service_list.stdout.txt"
)
AVC_REL = Path(
    "artifacts/phase6j/phase6j-service-visibility-20260805-01/filtered_avc.matches.txt"
)
PERMS_REL = Path(
    "artifacts/phase6k/readonly-device-20260805-01/preferred_activities.stdout.txt"
)
ALEXA_MANIFEST_REL = Path(
    "artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/resources/AndroidManifest.xml"
)
ARIA_REL = Path(
    "artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/com/amazon/aria/AriaPartialScreen.java"
)
PARTIAL_MANAGER_REL = Path(
    "artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/com/amazon/aria/PartialScreenManager.java"
)
OOBE_REPORT_REL = Path("findings/phase-6ag-boot-after-system-ota-research-item.md")
OOBE_AUTH_REL = Path("findings/phase-6r-bootafter-system-ota-authorization.md")

DEFAULT_OUTPUT = Path("artifacts/phase6aj/input-home-boundary-20260805-01")

CSV_FIELDS = [
    "evidence_id",
    "surface",
    "symbol",
    "source_file",
    "source_location",
    "publication_or_entry",
    "method_guard",
    "affected_state",
    "home_relation",
    "shell_reachability",
    "caller_evidence",
    "confidence",
    "conclusion",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, value: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def line_numbers(text: str, needle: str) -> list[int]:
    return [number for number, line in enumerate(text.splitlines(), 1) if needle in line]


def first_line(text: str, needle: str) -> int | None:
    hits = line_numbers(text, needle)
    return hits[0] if hits else None


def all_lines(text: str, needles: list[str]) -> dict[str, list[int]]:
    return {needle: line_numbers(text, needle) for needle in needles}


def require_markers(path: Path, text: str, markers: list[str]) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{path}: missing expected marker(s): {missing}")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_absolute() else path)


def load_inputs() -> dict[Path, str]:
    paths = [
        FOS_REL,
        BOOT_REL,
        SERVICE_LIST_REL,
        AVC_REL,
        PERMS_REL,
        ALEXA_MANIFEST_REL,
        ARIA_REL,
        PARTIAL_MANAGER_REL,
        OOBE_REPORT_REL,
        OOBE_AUTH_REL,
    ]
    missing = [str(ROOT / path) for path in paths if not (ROOT / path).is_file()]
    if missing:
        raise FileNotFoundError("missing input(s): " + ", ".join(missing))
    return {path: (ROOT / path).read_text(encoding="utf-8", errors="replace") for path in paths}


def row(**values: str) -> dict[str, str]:
    result = {field: "" for field in CSV_FIELDS}
    result.update(values)
    return result


def build_rows(inputs: dict[Path, str]) -> tuple[list[dict[str, str]], dict[str, object]]:
    fos = inputs[FOS_REL]
    boot = inputs[BOOT_REL]
    services = inputs[SERVICE_LIST_REL]
    avc = inputs[AVC_REL]
    perms = inputs[PERMS_REL]
    manifest = inputs[ALEXA_MANIFEST_REL]
    aria = inputs[ARIA_REL]
    partial_manager = inputs[PARTIAL_MANAGER_REL]
    oobe_report = inputs[OOBE_REPORT_REL]
    oobe_auth = inputs[OOBE_AUTH_REL]

    require_markers(
        ROOT / FOS_REL,
        fos,
        [
            "Lcom/amazon/android/internal/server/input/AmazonInputManagerService;",
            'const-string v0, "amazon_input"',
            'const-string v0, "amazon_keyevent"',
            'const-string v2, "com.amazon.permission.GET_KEYEVENTS"',
            'const-string v1, "com.amazon.input.permission.FILTER_INPUT_EVENTS"',
            'const-string v4, "android.permission.INJECT_EVENTS"',
            'const-string v4, "com.amazon.permission.INJECT_EVENTS"',
            'const-string v1, "persist.sys.inputdebug"',
            "direct_method #3949: isCallerSystemApp ()Z",
            "direct_method #3978: validateInputFilterAccessPermission ()V",
        ],
    )
    require_markers(
        ROOT / BOOT_REL,
        boot,
        [
            "class #485: IAmazonInputManager ('Lcom/amazon/android/internal/hardware/input/IAmazonInputManager;')",
            "amazon_input",
            "amazon_keyevent",
        ],
    )
    require_markers(
        ROOT / ARIA_REL,
        aria,
        [
            'GO_HOME_ACTION = "com.amazon.tv.launcher.HOME_PRESSED"',
            "SPECIAL_BUTTON = {3, 82}",
            "registerKeyEventListListener(this, this.SPECIAL_BUTTON)",
            "registerKeyEventInterceptor(this, ALLOWED_KEYCODES, this.mRoot, true)",
            "keyCode == 3",
        ],
    )
    require_markers(ROOT / PARTIAL_MANAGER_REL, partial_manager, ["AmazonInputManager.SERVICE_NAME"])
    require_markers(ROOT / OOBE_REPORT_REL, oobe_report, ["BootAfterSystemOTAReceiver", "STATIC_ONLY / NOT_ADOPTABLE"])
    require_markers(ROOT / OOBE_AUTH_REL, oobe_auth, ["protected-broadcast", "system_server"])

    service_visibility = "amazon_input" in services and "amazon_keyevent" in services
    shell_avc = (
        "uid=2000" in avc
        and "amazon_input" in avc
        and "amazon_keyevent" in avc
        and "{ find }" in avc
    )

    class_start = first_line(fos, "Lcom/amazon/android/internal/server/input/AmazonInputManagerService;")
    publish_line = first_line(fos, "virtual_method #3980: onStart ()V") or first_line(fos, 'const-string v0, "amazon_input"')
    publish_lines = line_numbers(fos, 'const-string v0, "amazon_input"')
    keyevent_lines = line_numbers(fos, 'const-string v0, "amazon_keyevent"')
    interceptor_line = first_line(fos, "virtual_method #3827: registerKeyEventInterceptor")
    listener_line = first_line(fos, "virtual_method #3829: registerKeyEventListener")
    next_listener_line = first_line(fos, "virtual_method #3830: registerNextKeyEventListener")
    filter_line = first_line(fos, "virtual_method #3831: setInputFilter")
    inject_line = first_line(fos, "virtual_method #3823: inject")
    inject_sequence_line = first_line(fos, "virtual_method #3824: injectSequence")
    validator_line = first_line(fos, "direct_method #3978: validateInputFilterAccessPermission")
    system_app_line = first_line(fos, "direct_method #3949: isCallerSystemApp")
    debug_line = first_line(fos, 'const-string v1, "persist.sys.inputdebug"')

    rows = [
        row(
            evidence_id="6AJ-HOME-001",
            surface="service_publication",
            symbol="AmazonInputManagerService.onStart / getSystemServiceName",
            source_file=rel(FOS_REL),
            source_location=f"class line {class_start}; onStart around {publish_line}; amazon_input lines {publish_lines[:2]}; amazon_keyevent lines {keyevent_lines[:2]}",
            publication_or_entry='publishBinderService("amazon_input"), publishBinderService("amazon_keyevent"), local service',
            method_guard="none at publication; guards are in Binder methods",
            affected_state="Amazon input/key-event callback registries and secondary input filter",
            home_relation="input observation/interception surface; not a HOME resolver method",
            shell_reachability="service names listed in saved capture, but shell find denied by SELinux",
            caller_evidence="saved live service list plus source publication",
            confidence="Confirmed",
            conclusion="Amazon publishes two private input services.",
        ),
        row(
            evidence_id="6AJ-HOME-002",
            surface="service_manager_boundary",
            symbol="amazon_input / amazon_keyevent",
            source_file=rel(SERVICE_LIST_REL) + "; " + rel(AVC_REL),
            source_location="saved service list lines 55-56; saved AVC matches for uid=2000",
            publication_or_entry="ServiceManager visibility exists at the system level",
            method_guard="SELinux service_manager find denial for shell UID 2000",
            affected_state="No shell handle to the private input services in the saved capture",
            home_relation="prevents a normal ADB caller from reaching these callback paths",
            shell_reachability="denied",
            caller_evidence="uid=2000 AVC { find } for amazon_input and amazon_keyevent",
            confidence="Confirmed",
            conclusion="No legitimate shell-accessible private input Binder route was observed.",
        ),
        row(
            evidence_id="6AJ-HOME-003",
            surface="key_interceptor",
            symbol="AmazonInputManagerService.BinderService.registerKeyEventInterceptor",
            source_file=rel(FOS_REL),
            source_location=f"method line {interceptor_line}; smali codeOff 0x024c3e; guard at 0x024c56",
            publication_or_entry="IAmazonInputManager.registerKeyEventInterceptor",
            method_guard="GET_KEYEVENTS; package whitelist; foreground package when requested; per-key whitelist and collision checks",
            affected_state="mInterceptKeyMap and registered callback lists",
            home_relation="can consume selected key events for authorized Amazon callers; no Fire Launcher component selection found",
            shell_reachability="unreachable in saved live policy; shell lacks service find and permission",
            caller_evidence="saved Alexa/ARIA caller uses the public client API; no shell caller",
            confidence="Confirmed",
            conclusion="This is a privileged input callback, not a generic HOME override.",
        ),
        row(
            evidence_id="6AJ-HOME-004",
            surface="key_listener",
            symbol="AmazonInputManagerService.BinderService.registerKeyEventListener",
            source_file=rel(FOS_REL),
            source_location=f"method line {listener_line}; smali codeOff 0x025710",
            publication_or_entry="IAmazonInputManager.registerKeyEventListener",
            method_guard="Context.checkCallingOrSelfPermission(GET_KEYEVENTS); SecurityException otherwise",
            affected_state="key-event listener callback registry",
            home_relation="observation/notification path; no resolver write or explicit HOME component in method",
            shell_reachability="unreachable without private permission and service handle",
            caller_evidence="authorized Amazon clients only in saved source scope",
            confidence="Confirmed",
            conclusion="Listener registration is permission-gated and not shell-writable.",
        ),
        row(
            evidence_id="6AJ-HOME-005",
            surface="next_key_listener",
            symbol="AmazonInputManagerService.BinderService.registerNextKeyEventListener",
            source_file=rel(FOS_REL),
            source_location=f"method line {next_listener_line}; smali codeOff 0x025780",
            publication_or_entry="IAmazonInputManager.registerNextKeyEventListener",
            method_guard="Context.checkCallingOrSelfPermission(GET_KEYEVENTS); SecurityException otherwise",
            affected_state="one-shot/next key callback state",
            home_relation="input event observation only in bounded method scope",
            shell_reachability="unreachable without private permission and service handle",
            caller_evidence="no shell caller in saved artifacts",
            confidence="Confirmed",
            conclusion="The one-shot listener has the same private permission boundary.",
        ),
        row(
            evidence_id="6AJ-HOME-006",
            surface="input_filter",
            symbol="setInputFilter -> validateInputFilterAccessPermission -> InputManagerService.registerSecondaryInputFilter",
            source_file=rel(FOS_REL),
            source_location=f"setInputFilter line {filter_line}; validator line {validator_line}; isCallerSystemApp line {system_app_line}; smali 0x0257f8/0x027b6e",
            publication_or_entry="IAmazonInputManager.setInputFilter",
            method_guard="caller must be system/updated-system app OR hold com.amazon.input.permission.FILTER_INPUT_EVENTS",
            affected_state="secondary input filter",
            home_relation="could affect input routing in principle, but does not choose a HOME component in the bounded implementation",
            shell_reachability="denied by caller class/permission boundary; FILTER_INPUT_EVENTS is signature|amazon",
            caller_evidence="permission dump identifies source android.amazon.perm, UID 1000, prot signature|amazon",
            confidence="Confirmed",
            conclusion="The previously unresolved method-local authorization is now closed.",
        ),
        row(
            evidence_id="6AJ-HOME-007",
            surface="input_injection",
            symbol="checkInjectEventsPermission; inject; injectSequence",
            source_file=rel(FOS_REL),
            source_location=f"inject line {inject_line}; injectSequence line {inject_sequence_line}; checker around smali 0x02667a",
            publication_or_entry="IAmazonInputManager.inject / injectSequence",
            method_guard="system_server pid/uid fast path; otherwise INJECT_EVENTS permissions and UID 1000 check",
            affected_state="input injection request only",
            home_relation="not a HOME resolver route; injecting Home is intentionally not tested",
            shell_reachability="denied for shell UID under the saved branch conditions",
            caller_evidence="smali checks Binder calling PID/UID and both Android/Amazon injection permissions",
            confidence="Confirmed",
            conclusion="Input injection is not a safe or available shell bypass.",
        ),
        row(
            evidence_id="6AJ-HOME-008",
            surface="private_keyevent_state",
            symbol="KeyEventBinderService.setInputLockingMode / partner app APIs",
            source_file=rel(FOS_REL) + "; " + rel(PERMS_REL),
            source_location="fosservices around methods 3845-3851; permission strings at 0x025ea8/0x02602c/0x025ee4",
            publication_or_entry="amazon_keyevent Binder service",
            method_guard="SET_PARTNER_APP_INFO (signature|...); INPUT_LOCKING (signature|amzrestricted); GET_KEYEVENTS",
            affected_state="input-locking mode and partner-app metadata",
            home_relation="may change input policy for authorized integrations; no direct HOME component write observed",
            shell_reachability="not available to shell in saved capture",
            caller_evidence="permission definitions and existing service visibility evidence",
            confidence="Confirmed",
            conclusion="Private key-event state is separately protected and not a third-party launcher control surface.",
        ),
        row(
            evidence_id="6AJ-HOME-009",
            surface="authorized_home_observer",
            symbol="AriaPartialScreen.registerKeyEventInterceptor / onKeyEvent",
            source_file=rel(ARIA_REL) + "; " + rel(PARTIAL_MANAGER_REL) + "; " + rel(ALEXA_MANIFEST_REL),
            source_location="AriaPartialScreen.java:56,77,174-180,323-335; PartialScreenManager.java:175-177; Alexa manifest saved uses GET_KEYEVENTS",
            publication_or_entry="AmazonInputManager.SERVICE_NAME client obtained through Context.getSystemService",
            method_guard="caller is an authorized privileged Amazon component; service-side whitelist/foreground/key checks still apply",
            affected_state="ARIA partial-screen overlay and its key callback",
            home_relation="special key list includes 3 (HOME) and 82; key-up dismisses the partial overlay; no Fire Launcher explicit start shown",
            shell_reachability="not available to ordinary third-party/shell caller",
            caller_evidence="saved Alexa ARIA source and manifest permission use",
            confidence="Strong evidence",
            conclusion="A privileged Amazon client can observe/consume HOME for an overlay, but this does not prove resolver replacement.",
        ),
        row(
            evidence_id="6AJ-HOME-010",
            surface="resolver_scope_negative",
            symbol="AmazonInputManagerService bounded implementation scope",
            source_file=rel(FOS_REL),
            source_location="AmazonInputManagerService class block from its class header through the next class boundary",
            publication_or_entry="same private input service",
            method_guard="not applicable",
            affected_state="input callback/filter state only in bounded scope",
            home_relation="no occurrences of resolveActivity, resolveIntent, setPreferredActivity, replacePreferredActivity, startHomeActivity, or startHomeOnAllDisplays in bounded class scope",
            shell_reachability="not applicable",
            caller_evidence="negative result limited to this class scope; other SystemUI/PhoneWindowManager paths remain separate",
            confidence="Strong evidence",
            conclusion="The input service is not itself shown to perform HOME resolver selection.",
        ),
        row(
            evidence_id="6AJ-HOME-011",
            surface="system_app_foreground_gate",
            symbol="isCallerSystemApp and registerKeyEventInterceptor foreground/whitelist checks",
            source_file=rel(FOS_REL),
            source_location=f"isCallerSystemApp line {system_app_line}; interceptor smali 0x024c56-0x024d2a",
            publication_or_entry="internal service method calls",
            method_guard="ApplicationInfo.isSystemApp/isUpdatedSystemApp; mWhiteListEntries; mCurrentPackageName; allowed key map",
            affected_state="whether a callback can be registered",
            home_relation="blocks arbitrary third-party Home-key interception",
            shell_reachability="shell UID is not a system application and has no saved whitelist entry",
            caller_evidence="smali explicitly reads calling UID/package list and current foreground package",
            confidence="Confirmed",
            conclusion="Even a reachable Binder handle would not by itself grant an arbitrary caller a callback.",
        ),
        row(
            evidence_id="6AJ-HOME-012",
            surface="debug_control",
            symbol="AmazonInputManagerService.DEBUG_LOG initialization",
            source_file=rel(FOS_REL),
            source_location=f"constructor/static initialization around line {debug_line}; smali 0x026c0e-0x026c30",
            publication_or_entry="private service debug logging",
            method_guard="persist.sys.inputdebug is read only when Build.IS_DEBUGGABLE is true",
            affected_state="debug logging flag, not input authorization",
            home_relation="no production HOME control found",
            shell_reachability="current device is user/amz-p and ro.debuggable=0 in saved live baseline",
            caller_evidence="PS7331 live build properties from Phase 6AH",
            confidence="Confirmed",
            conclusion="The property is not a production shell-toggleable route to the input service.",
        ),
        row(
            evidence_id="6AJ-OTA-001",
            surface="related_ota_oobe_lifecycle",
            symbol="BootAfterSystemOTAReceiver",
            source_file=rel(OOBE_REPORT_REL) + "; " + rel(OOBE_AUTH_REL),
            source_location="Phase 6AG/6R static reports and their hashed artifacts",
            publication_or_entry="system-server phase-550/isUpgrade sender; protected OTA/OOBE action",
            method_guard="protected broadcast and OTA lifecycle conditions; receiver side effects enable OobeHomeActivity and mutate OOBE state",
            affected_state="OOBE setup state and OobeHomeActivity component state",
            home_relation="related high-risk lifecycle surface; not an input Binder path and not a normal shell HOME selector",
            shell_reachability="manual broadcast replay explicitly excluded",
            caller_evidence="existing Phase 6AG/6R evidence; no new device action",
            confidence="Confirmed",
            conclusion="Already registered as STATIC_ONLY / NOT_ADOPTABLE; retained as a related research item, not a workaround.",
        ),
    ]

    negative_terms = [
        "resolveActivity",
        "resolveIntent",
        "setPreferredActivity",
        "replacePreferredActivity",
        "startHomeActivity",
        "startHomeOnAllDisplays",
    ]
    class_scope_start = fos.find("Lcom/amazon/android/internal/server/input/AmazonInputManagerService;")
    class_scope_end = fos.find("Lcom/amazon/android/internal/server/input/", class_scope_start + 1)
    if class_scope_start < 0:
        class_scope = ""
    else:
        class_scope = fos[class_scope_start : class_scope_end if class_scope_end > class_scope_start else len(fos)]
    negative_hits = {term: line_numbers(class_scope, term) for term in negative_terms}
    summary = {
        "device_contacted": False,
        "binder_transactions_sent": False,
        "input_injected": False,
        "broadcast_replayed": False,
        "package_or_settings_mutated": False,
        "service_visibility_found_in_saved_capture": service_visibility,
        "shell_service_manager_find_denied_in_saved_capture": shell_avc,
        "bounded_resolver_negative_hits": negative_hits,
        "rows": len(rows),
        "oobe_receiver_included_as_related_static_item": True,
    }
    return rows, summary


def make_graph() -> str:
    return """flowchart TD
  A[SystemServer publishes amazon_input / amazon_keyevent] --> B[ServiceManager / SELinux boundary]
  B -->|shell find denied in saved AVC| X[No ordinary shell Binder handle]
  B --> C[Authorized Amazon caller]
  C --> D[GET_KEYEVENTS + whitelist + foreground + key checks]
  C --> E[system app OR FILTER_INPUT_EVENTS for setInputFilter]
  C --> F[ARIA partial-screen callback]
  F --> G[HOME key 3 can dismiss overlay]
  D --> H[Input callback registry]
  E --> I[Secondary input filter]
  H -. no resolver API in bounded service scope .-> J[HOME resolver remains elsewhere]
  K[BootAfterSystemOTAReceiver] -. related, static-only .-> L[OOBE state / OobeHomeActivity]
  L -. not a shell HOME selector .-> J
"""


def make_plain_graph() -> str:
    return """AmazonInputManagerService.onStart
  -> publishBinderService(amazon_input)
  -> publishBinderService(amazon_keyevent)
  -> shell service_manager find denied (saved SELinux AVC)
  -> authorized Amazon caller only
      -> GET_KEYEVENTS / whitelist / foreground / key map
      -> input callback registry
      -> ARIA may observe HOME (keycode 3) to dismiss overlay
      -> no bounded resolver API or Fire Launcher component selection

setInputFilter
  -> validateInputFilterAccessPermission
  -> system/updated-system app OR FILTER_INPUT_EVENTS(signature|amazon)
  -> InputManagerService.registerSecondaryInputFilter

BootAfterSystemOTAReceiver (related Phase 6AG/6R item)
  -> protected system-server OTA lifecycle
  -> OOBE state / OobeHomeActivity side effect
  -> not manually replayed; not a shell HOME selector
"""


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true", help="validate inputs and print the planned evidence scope without writing")
    args = parser.parse_args()

    inputs = load_inputs()
    rows, summary = build_rows(inputs)
    input_hashes = {rel(path): sha256(ROOT / path) for path in inputs}
    summary.update(
        {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "script": rel(Path(__file__).resolve()),
            "input_files": sorted(input_hashes),
            "input_sha256": input_hashes,
            "safety": "host-only; no ADB/Binder/input/broadcast/package/settings/OTA operation",
        }
    )

    if args.dry_run:
        print(json.dumps({"output": str(args.output), "summary": summary, "evidence_ids": [r["evidence_id"] for r in rows]}, ensure_ascii=False, indent=2))
        return 0

    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise FileExistsError(f"refusing to use existing output directory: {output}")
    output.mkdir(parents=True)

    write_json(output / "summary.json", summary)
    write_json(output / "input-sha256.json", input_hashes)
    write_csv(output / "input-home-boundary.csv", rows)
    write_text(output / "input-home-boundary.mmd", make_graph())
    write_text(output / "input-home-boundary.md", make_plain_graph())

    selected = []
    for path in (FOS_REL, BOOT_REL, ARIA_REL, PARTIAL_MANAGER_REL, ALEXA_MANIFEST_REL):
        text = inputs[path]
        selected.append(f"### {rel(path)}\n")
        needles = {
            FOS_REL: [
                "virtual_method #3827: registerKeyEventInterceptor",
                "virtual_method #3829: registerKeyEventListener",
                "virtual_method #3830: registerNextKeyEventListener",
                "virtual_method #3831: setInputFilter",
                "direct_method #3936: checkInjectEventsPermission",
                "direct_method #3978: validateInputFilterAccessPermission",
                "direct_method #3949: isCallerSystemApp",
            ],
            BOOT_REL: ["IAmazonInputManager"],
            ARIA_REL: ["GO_HOME_ACTION", "SPECIAL_BUTTON", "registerKeyEventListListener", "onKeyEvent"],
            PARTIAL_MANAGER_REL: ["getAmazonInputManager"],
            ALEXA_MANIFEST_REL: ["GET_KEYEVENTS"],
        }[path]
        lines = text.splitlines()
        for needle in needles:
            hits = [index for index, line in enumerate(lines) if needle in line]
            for index in hits[:2]:
                start = max(0, index - 2)
                end = min(len(lines), index + 5)
                selected.extend(
                    (
                        f"{number}: {lines[number - 1].rstrip()}"
                        if lines[number - 1].rstrip()
                        else f"{number}:"
                    )
                    for number in range(start + 1, end + 1)
                )
                selected.append("")
    write_text(output / "method-snippets.txt", "\n".join(selected))

    manifest_lines = [
        f"{sha256(path)}  {path.name}"
        for path in sorted(output.iterdir())
        if path.name != "sha256sums.txt"
    ]
    write_text(output / "sha256sums.txt", "\n".join(manifest_lines) + "\n")
    print(f"wrote {output}")
    print(f"evidence rows: {len(rows)}")
    print(f"sha256 manifest: {output / 'sha256sums.txt'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, FileExistsError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
