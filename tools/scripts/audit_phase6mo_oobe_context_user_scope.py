#!/usr/bin/env python3
"""Host-only closure of the PS7331 OOBE Context/user-scope boundary.

This script reads preserved JADX and baksmali artifacts only.  It never opens
an ADB connection, invokes Binder, sends a broadcast, mutates settings, or
touches a device.  The generated report deliberately leaves the final user
mapping open when the preserved artifacts do not identify it.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path


SCHEMA = "phase6mo-oobe-context-user-scope-v1"
DEFAULT_OUT = "artifacts/phase6mo-oobe-context-user-scope-20260810-01"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def line_range(path: Path, start: int, end: int) -> str:
    selected = []
    # The disassembly contains a small number of bare CR bytes.  Match the
    # line numbering emitted by `nl -ba` by treating only LF as a separator.
    with path.open("r", encoding="utf-8", errors="replace", newline="\n") as handle:
        for number, line in enumerate(handle, 1):
            if number > end:
                break
            if number >= start:
                selected.append(line.rstrip("\n"))
    return "\n".join(selected)


def require_markers(path: Path, start: int, end: int, markers: list[str]) -> None:
    text = line_range(path, start, end)
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(
            f"input drift in {path}:{start}-{end}; missing markers: {missing}"
        )


def rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]], force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def copy_bytes(source: Path, destination: Path, force: bool) -> None:
    if destination.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing output: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source.read_bytes())


def build_inputs(root: Path) -> list[Path]:
    source_root = root / "artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources"
    paths = [
        source_root / "com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java",
        source_root / "com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java",
        source_root / "com/amazon/oobe/commons/utils/SettingsDBUtils.java",
        source_root / "com/amazon/oobe/commons/utils/PackageHelper.java",
        source_root / "com/amazon/oobe/commons/utils/ContextUtils.java",
        root / "decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log",
        root / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log",
        root / "findings/phase-6mg-oobe-helper-scope.md",
        root / "findings/phase-6r-bootafter-system-ota-authorization.md",
        root / "findings/phase-6mn-ipc-user-scope-closure.md",
    ]
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing required inputs:\n" + "\n".join(map(str, missing)))
    return paths


def validate_inputs(root: Path) -> None:
    source_root = root / "artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources"
    receiver = source_root / "com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java"
    helper = source_root / "com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java"
    settings = source_root / "com/amazon/oobe/commons/utils/SettingsDBUtils.java"
    package = source_root / "com/amazon/oobe/commons/utils/PackageHelper.java"
    context_utils = source_root / "com/amazon/oobe/commons/utils/ContextUtils.java"
    framework = root / "decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log"
    fosservices = root / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"
    foservices = fosservices

    require_markers(receiver, 27, 46, ["onReceive(Context context, Intent intent)", "getPackageManager", "setComponentEnabledSetting"])
    require_markers(receiver, 56, 61, ["enableComponent(context, OobeHomeActivity.class)", "activateOOBEIF(context)"])
    require_markers(helper, 29, 34, ["context.getContentResolver()", "USER_SETUP_COMPLETE", "device_provisioned"])
    require_markers(helper, 53, 61, ["setSettingSecurePutIntFG", "IS_OOBE_ACTIVE", "setSettingGlobalPutInt"])
    require_markers(settings, 21, 64, ["Settings.Secure.putString", "Settings.Secure.putInt", "Settings.Global.putInt"])
    require_markers(package, 11, 22, ["setComponentEnabledSetting", "getComponentEnabledSetting"])
    require_markers(context_utils, 11, 24, ["createDeviceProtectedStorageContext"])

    require_markers(framework, 430612, 430638, ["ActivityThread.ReceiverData", "<init>", "Intent", "PendingResult"])
    require_markers(framework, 435176, 435236, ["handleReceiver", "getPackageInfoNoCheck", "makeApplication", "getReceiverRestrictedContext", "onReceive"])
    require_markers(framework, 449092, 449185, ["ApplicationContentResolver", "resolveUserIdFromAuthority", "getUserIdFromAuthority"])
    require_markers(framework, 449212, 449298, ["ContextImpl", "UserHandle", "mUser", "Process;.myUserHandle"])
    require_markers(framework, 449515, 449534, ["createAppContext", "ContextImpl", "getResources"])
    require_markers(framework, 450958, 450975, ["createDeviceProtectedStorageContext", "mUser", "ContextImpl;.<init>"])
    require_markers(framework, 451429, 451434, ["getContentResolver", "mContentResolver"])
    require_markers(framework, 452137, 452150, ["getUser", "getUserId", "mUser", "getIdentifier"])
    require_markers(framework, 452691, 452721, ["sendBroadcast", "getUserId", "IActivityManager;.broadcastIntent"])
    require_markers(fosservices, 96087, 96126, ["onBootPhase", "isUpgrade", "BOOT_AFTER_SYSTEM_OTA", "sendBroadcast"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--generated-date", default=str(date.today()))
    parser.add_argument("--dry-run", action="store_true", help="validate and list outputs without writing")
    parser.add_argument("--force", action="store_true", help="overwrite only this script's generated outputs")
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output or (root / DEFAULT_OUT)).resolve()

    inputs = build_inputs(root)
    validate_inputs(root)

    report_path = root / "findings/phase-6mo-oobe-context-user-scope.md"
    evidence_path = root / "findings/phase-6mo-evidence-index.md"
    review_table = root / "output/tables/phase6mo-oobe-context-user-scope-20260810-01.csv"
    review_graph = root / "output/call-graphs/phase6mo-oobe-context-user-scope-20260810-01.mmd"
    generated = [
        output / "context-user-scope.csv",
        output / "method-evidence.csv",
        output / "summary.json",
        output / "input-manifest.csv",
        output / "route-flow.mmd",
        output / "sha256sums.txt",
        report_path,
        evidence_path,
        review_table,
        review_graph,
    ]
    if args.dry_run:
        print(f"schema={SCHEMA}")
        print(f"root={root}")
        print(f"output={output}")
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

    output.mkdir(parents=True, exist_ok=True)
    if not args.force:
        existing = [path for path in generated if path.exists()]
        if existing:
            raise FileExistsError("refusing to overwrite existing outputs:\n" + "\n".join(map(str, existing)))

    source_root = root / "artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources"
    receiver = source_root / "com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java"
    helper = source_root / "com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java"
    settings = source_root / "com/amazon/oobe/commons/utils/SettingsDBUtils.java"
    package = source_root / "com/amazon/oobe/commons/utils/PackageHelper.java"
    context_utils = source_root / "com/amazon/oobe/commons/utils/ContextUtils.java"
    framework = root / "decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log"
    fosservices = root / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"

    foservices = fosservices
    rows = [
        {
            "route_id": "6MO-R01",
            "caller_receiver": "AmazonPackageManagerService.onBootPhase(550)",
            "lifecycle_guard": "phase == 550 AND mPackageManagerService != null AND isUpgrade()",
            "permission_identity": "system-server service context; protected-broadcast membership is separately documented",
            "context_provenance": "mContext.sendBroadcast(Intent, permission)",
            "user_handle_provenance": "ContextImpl.sendBroadcast passes mContext.getUserId(); exact service-context user not encoded in this callsite",
            "concrete_sink": "IActivityManager.broadcastIntent(..., userId)",
            "home_relevance": "lifecycle trigger only; not a direct HOME writer",
            "scope_verdict": "CONTEXT_DERIVED_EXACT_ID_UNCONFIRMED",
            "confidence": "Confirmed",
            "evidence": "fosservices:96087-96126; boot-framework:452691-452721",
        },
        {
            "route_id": "6MO-R02",
            "caller_receiver": "BootAfterSystemOTAReceiver.onReceive(Context, Intent)",
            "lifecycle_guard": "action == BOOT_AFTER_SYSTEM_OTA AND !isOOBEAlreadyRunning AND isNotInDemoMode",
            "permission_identity": "receiver receives framework-delivered receiver context; no receiver android:permission claim here",
            "context_provenance": "ActivityThread builds application context from ReceiverData.info.applicationInfo, then passes receiver-restricted Context",
            "user_handle_provenance": "context is process/user scoped; no explicit UserHandle argument in onReceive",
            "concrete_sink": "enableIncrementalFlow(context) or error-path component disable",
            "home_relevance": "enables OobeHomeActivity only under guarded OOBE flow",
            "scope_verdict": "CONTEXT_BOUND_EXACT_ID_UNCONFIRMED",
            "confidence": "Confirmed",
            "evidence": "BootAfterSystemOTAReceiver.java:27-46; boot-framework:435176-435236",
        },
        {
            "route_id": "6MO-R03",
            "caller_receiver": "BootAfterSystemOTAReceiver.enableIncrementalFlow(Context)",
            "lifecycle_guard": "reachable only from guarded onReceive branch",
            "permission_identity": "inherits receiver context",
            "context_provenance": "same Context object passed to both helper calls",
            "user_handle_provenance": "no explicit user override",
            "concrete_sink": "PackageHelper.enableComponent(context, OobeHomeActivity.class)",
            "home_relevance": "OOBE HOME component state, not Fire Launcher state",
            "scope_verdict": "CONTEXT_BOUND_EXACT_ID_UNCONFIRMED",
            "confidence": "Confirmed",
            "evidence": "BootAfterSystemOTAReceiver.java:56-61; PackageHelper.java:11-22",
        },
        {
            "route_id": "6MO-R04",
            "caller_receiver": "OOBEActivationHelper.activateOOBEIF(Context)",
            "lifecycle_guard": "called by enableIncrementalFlow",
            "permission_identity": "inherits caller-supplied ContentResolver",
            "context_provenance": "context.getContentResolver() passed to SettingsDBUtils FG helpers",
            "user_handle_provenance": "SettingsDBUtils does not add an explicit ForUser/userId at these callsites",
            "concrete_sink": "Settings.Secure.putInt(contentResolver, user_setup_complete/isOOBEActive)",
            "home_relevance": "OOBE setup state; no preferred/HOME API in reviewed helper",
            "scope_verdict": "CONTEXT_BOUND_EXACT_ID_UNCONFIRMED",
            "confidence": "Confirmed",
            "evidence": "OOBEActivationHelper.java:53-56; SettingsDBUtils.java:51-64",
        },
        {
            "route_id": "6MO-R05",
            "caller_receiver": "ContextImpl.ApplicationContentResolver",
            "lifecycle_guard": "framework client path",
            "permission_identity": "provider acquisition through ActivityThread",
            "context_provenance": "ApplicationContentResolver is constructed with ContextImpl and ActivityThread",
            "user_handle_provenance": "resolveUserIdFromAuthority calls getUserId(); getUserId reads mUser.getIdentifier()",
            "concrete_sink": "ActivityThread.acquireProvider/acquireExistingProvider(userId)",
            "home_relevance": "proves settings/provider operations retain Context-derived user scope",
            "scope_verdict": "CONTEXT_USER_SCOPED",
            "confidence": "Strong evidence",
            "evidence": "boot-framework:449092-449185; 451429-451434; 452137-452150",
        },
        {
            "route_id": "6MO-R06",
            "caller_receiver": "ContextUtils.getLockedContext(Context)",
            "lifecycle_guard": "Build.VERSION.SDK_INT >= 26",
            "permission_identity": "no identity change visible",
            "context_provenance": "createDeviceProtectedStorageContext() returns a derived ContextImpl",
            "user_handle_provenance": "derived context constructor copies mUser",
            "concrete_sink": "device-protected storage access only",
            "home_relevance": "does not change user identity; affects storage domain",
            "scope_verdict": "USER_HANDLE_PRESERVED",
            "confidence": "Strong evidence",
            "evidence": "ContextUtils.java:11-24; boot-framework:450958-450975",
        },
    ]

    method_rows = [
        {"evidence_id": "6MO-E01", "source": rel(root, fosservices), "line_range": "96087-96126", "method": "AmazonPackageManagerService.onBootPhase", "observed_markers": "550; isUpgrade; BOOT_AFTER_SYSTEM_OTA; mContext.sendBroadcast", "classification": "Confirmed"},
        {"evidence_id": "6MO-E02", "source": rel(root, receiver), "line_range": "27-46", "method": "BootAfterSystemOTAReceiver.onReceive", "observed_markers": "Context; guarded action; getPackageManager; receiver component", "classification": "Confirmed"},
        {"evidence_id": "6MO-E03", "source": rel(root, receiver), "line_range": "56-61", "method": "enableIncrementalFlow", "observed_markers": "PackageHelper.enableComponent; activateOOBEIF", "classification": "Confirmed"},
        {"evidence_id": "6MO-E04", "source": rel(root, helper), "line_range": "29-34;53-61", "method": "OOBEActivationHelper", "observed_markers": "ContentResolver; Secure/Global setup writes", "classification": "Confirmed"},
        {"evidence_id": "6MO-E05", "source": rel(root, package), "line_range": "11-22", "method": "PackageHelper", "observed_markers": "setComponentEnabledSetting; component state 1/2", "classification": "Confirmed"},
        {"evidence_id": "6MO-E06", "source": rel(root, framework), "line_range": "435176-435236", "method": "ActivityThread.handleReceiver", "observed_markers": "ApplicationInfo; LoadedApk; ContextImpl; receiver-restricted Context; onReceive", "classification": "Confirmed"},
        {"evidence_id": "6MO-E07", "source": rel(root, framework), "line_range": "449212-449298;449515-449534", "method": "ContextImpl constructor/createAppContext", "observed_markers": "UserHandle parameter; null defaults to Process.myUserHandle; mUser storage", "classification": "Confirmed"},
        {"evidence_id": "6MO-E08", "source": rel(root, framework), "line_range": "449092-449185;452137-452150", "method": "ApplicationContentResolver/ContextImpl.getUserId", "observed_markers": "provider user resolution from ContextImpl.mUser", "classification": "Strong evidence"},
        {"evidence_id": "6MO-E09", "source": rel(root, framework), "line_range": "452691-452721", "method": "ContextImpl.sendBroadcast", "observed_markers": "getUserId passed to IActivityManager.broadcastIntent", "classification": "Confirmed"},
        {"evidence_id": "6MO-E10", "source": rel(root, context_utils), "line_range": "11-24", "method": "ContextUtils storage-context helpers", "observed_markers": "createDeviceProtectedStorageContext", "classification": "Confirmed"},
    ]

    manifest_rows = [{"path": rel(root, path), "size_bytes": path.stat().st_size, "sha256": sha256(path)} for path in inputs]
    manifest_fields = ["path", "size_bytes", "sha256"]
    table_fields = list(rows[0].keys())
    method_fields = list(method_rows[0].keys())

    graph = """flowchart TD\n  S[\"AmazonPackageManagerService.onBootPhase(550)\"] --> G[\"isUpgrade()\"]\n  G --> B[\"mContext.sendBroadcast(BOOT_AFTER_SYSTEM_OTA, permission)\"]\n  B --> U[\"ContextImpl.sendBroadcast -> getUserId()\"]\n  U --> A[\"IActivityManager.broadcastIntent(userId)\"]\n  A -.-> Q[\"exact delivered user mapping: UNCONFIRMED\"]\n  A --> R[\"ActivityThread.handleReceiver(ReceiverData)\"]\n  R --> C[\"LoadedApk.makeApplication -> ContextImpl.mUser\"]\n  C --> RR[\"getReceiverRestrictedContext()\"]\n  RR --> O[\"BootAfterSystemOTAReceiver.onReceive(context, intent)\"]\n  O --> E[\"PackageHelper.enableComponent(OobeHomeActivity)\"]\n  O --> H[\"OOBEActivationHelper.activateOOBEIF(context)\"]\n  H --> D[\"SettingsDBUtils -> Settings.Secure.putInt(ContentResolver)\"]\n  E --> P[\"Context.getPackageManager -> setComponentEnabledSetting\"]\n"""

    summary = {
        "schema": SCHEMA,
        "generated_date": args.generated_date,
        "scope": "host-only static artifact provenance",
        "inputs": len(inputs),
        "routes": len(rows),
        "method_evidence": len(method_rows),
        "device_contacted": False,
        "binder_or_service_call": False,
        "ioctl": False,
        "mutation": False,
        "reboot": False,
        "broadcast_sent": False,
        "oobe_started": False,
        "exact_user_id_proven": False,
        "bounded_conclusion": "OOBE settings/package sinks are Context-derived and user-scoped by framework client semantics; the preserved artifacts do not prove the exact broadcast delivery user.",
        "negative_scope": "No direct Fire Launcher HOME/preferred writer was found in the four reviewed OOBE sources; this is corpus-bounded.",
    }

    report = f"""# Phase 6MO — OOBE Context / user-scope provenance closure\n\nDate: {args.generated_date}\n\n## Scope and safety\n\nThis is host-only static analysis of preserved PS7331 JADX and baksmali artifacts. No ADB connection, Binder/service call, broadcast, ioctl, OTA/recovery execution, reboot, settings mutation, package mutation, or partition write was performed.\n\n## Executive result\n\n**已證實：** the Amazon post-OTA sender reaches `Context.sendBroadcast(Intent, permission)` only from the guarded `AmazonPackageManagerService.onBootPhase(550)` → `isUpgrade()` branch. The Android framework implementation passes the sending `ContextImpl.getUserId()` into `IActivityManager.broadcastIntent`.\n\n**已證實：** `ActivityThread.handleReceiver()` constructs the receiver application context from `ReceiverData.info.applicationInfo`, creates the application, derives a receiver-restricted `Context`, and invokes `BootAfterSystemOTAReceiver.onReceive(context, intent)`. The OOBE source passes that same context into `PackageHelper` and `SettingsDBUtils`.\n\n**高可信推論：** the settings and component-state operations are context/process-user scoped. `ContextImpl` stores a `UserHandle`; `getUserId()` returns its identifier; `ApplicationContentResolver` uses that value when acquiring providers. Device-protected context creation preserves `mUser`.\n\n**待驗證：** the exact user ID delivered by the post-OTA broadcast on this Fire OS build. The selected static sender does not explicitly pass `USER_SYSTEM`, `USER_CURRENT`, or `USER_ALL`, and the preserved app-side receiver path has no explicit user argument. Therefore this report does **not** claim User 0.\n\n## Evidence chain\n\n```text\nAmazonPackageManagerService.onBootPhase(550)\n  -> isUpgrade()\n  -> mContext.sendBroadcast(BOOT_AFTER_SYSTEM_OTA, permission)\n  -> ContextImpl.sendBroadcast -> getUserId()\n  -> IActivityManager.broadcastIntent(..., userId)\n  -> ActivityThread.handleReceiver(ReceiverData)\n  -> LoadedApk.makeApplication -> ContextImpl.mUser\n  -> getReceiverRestrictedContext()\n  -> BootAfterSystemOTAReceiver.onReceive(context, intent)\n  -> PackageHelper / SettingsDBUtils sinks\n```\n\nExact locations: sender `{rel(root, fosservices)}:96087-96126`; framework receiver delivery `{rel(root, framework)}:435176-435236`; `ContextImpl` constructor/default `{rel(root, framework)}:449212-449298, 449515-449534`; provider user mapping `{rel(root, framework)}:449092-449185, 452137-452150`; broadcast user argument `{rel(root, framework)}:452691-452721`.\n\n## Sink analysis\n\n`BootAfterSystemOTAReceiver.enableIncrementalFlow()` calls `PackageHelper.enableComponent(context, OobeHomeActivity.class)` and `OOBEActivationHelper.activateOOBEIF(context)` (`BootAfterSystemOTAReceiver.java:56-61`). `PackageHelper` calls `context.getPackageManager().setComponentEnabledSetting(...)` (`PackageHelper.java:11-22`). The OOBE activation helper passes `context.getContentResolver()` into `SettingsDBUtils.setSettingSecurePutIntFG()` (`OOBEActivationHelper.java:53-56`), which calls `Settings.Secure.putInt(contentResolver, key, value)` (`SettingsDBUtils.java:51-64`).\n\nThe four reviewed OOBE sources contain no `setHomeActivity`, `addPreferredActivity`, `replacePreferredActivity`, or `com.amazon.firelauncher` reference. This is **已排除／bounded negative** for “the reviewed OOBE helper is the ordinary Fire Launcher preferred/HOME writer”; it is not a binary-wide absence claim.\n\n## Decision table\n\n| Finding | Verdict | Evidence |\n|---|---|---|\n| Post-OTA sender has phase and upgrade guards | 已證實 | `fosservices:96087-96126` |\n| Sender uses explicit `sendBroadcast(..., permission)` rather than `sendBroadcastAsUser` | 已證實 | `fosservices:96124-96126` |\n| Framework derives broadcast user argument from sender ContextImpl | 已證實 | `boot-framework:452691-452721` |\n| Receiver callback receives a receiver-restricted Context | 已證實 | `boot-framework:435176-435236` |\n| ContextImpl retains a UserHandle and exposes getUserId | 已證實 | `boot-framework:449212-449298;452137-452150` |\n| Settings provider operations retain that context-derived user scope | Strong evidence | `boot-framework:449092-449185`; `SettingsDBUtils.java:51-64` |\n| Exact post-OTA delivery user is User 0 | 待驗證 | no explicit user in selected sender/delivery evidence |\n| OOBE helper directly rewrites ordinary Fire Launcher HOME preference | 已排除（bounded） | four OOBE source files |\n| Manual replay is safe | 因風險拒絕測試 | prior Phase 6R authorization report |\n\n## Remaining minimal target\n\nThe remaining question can only be closed by a stronger host artifact showing how the system-service `mContext` is created and which broadcast user is selected by the corresponding ActivityManager path, or by observing a naturally occurring official OTA transition with read-only captures. Do not manually replay `BOOT_AFTER_SYSTEM_OTA`; it changes OOBE, component, accessibility, and secure-setting state.\n\n## Reproduction\n\n```sh\npython3 tools/scripts/audit_phase6mo_oobe_context_user_scope.py --dry-run\npython3 tools/scripts/audit_phase6mo_oobe_context_user_scope.py\n```\n\nGenerated artifact: `{rel(root, output)}`.\n"""

    evidence = f"""# Phase 6MO evidence index\n\nGenerated: {args.generated_date}\nSchema: `{SCHEMA}`\nScope: host-only; no device contact or state mutation.\n\n| Evidence ID | File / method | Location | Observation | Confidence |\n|---|---|---:|---|---|\n| 6MO-E01 | `{rel(root, fosservices)}` / `AmazonPackageManagerService.onBootPhase` | 96087-96126 | Phase 550 + `isUpgrade()` + `mContext.sendBroadcast` | Confirmed |\n| 6MO-E02 | `{rel(root, framework)}` / `ContextImpl.sendBroadcast` | 452691-452721 | `getUserId()` is passed to `IActivityManager.broadcastIntent` | Confirmed |\n| 6MO-E03 | `{rel(root, framework)}` / `ActivityThread.handleReceiver` | 435176-435236 | Receiver context is built and `getReceiverRestrictedContext()` is passed to `onReceive` | Confirmed |\n| 6MO-E04 | `{rel(root, framework)}` / `ContextImpl` constructor and `createAppContext` | 449212-449298;449515-449534 | `UserHandle` is stored; null defaults to `Process.myUserHandle()` | Confirmed |\n| 6MO-E05 | `{rel(root, framework)}` / `ApplicationContentResolver` + `getUserId` | 449092-449185;452137-452150 | Provider acquisition derives user from ContextImpl | Strong evidence |\n| 6MO-E06 | `{rel(root, framework)}` / `createDeviceProtectedStorageContext` | 450958-450975 | Derived storage context copies `mUser` | Strong evidence |\n| 6MO-E07 | `{rel(root, receiver)}` / `enableIncrementalFlow` | 56-61 | OOBE component and setup helper receive same Context | Confirmed |\n| 6MO-E08 | `{rel(root, helper)}` / `activateOOBEIF` | 53-56 | Secure setting writes receive context-derived ContentResolver | Confirmed |\n| 6MO-E09 | `{rel(root, package)}` / `PackageHelper` | 11-22 | Component state calls use context package manager | Confirmed |\n| 6MO-E10 | `{rel(root, receiver)}; {rel(root, helper)}; {rel(root, settings)}; {rel(root, package)}` | bounded corpus | No direct ordinary Fire Launcher HOME/preferred writer found | Disproved (bounded hypothesis) |\n\n## Interpretation\n\nThe evidence establishes a context-derived user boundary, not an exact User-0 claim. The exact user mapping remains `待驗證`.\n"""

    write_csv(output / "context-user-scope.csv", table_fields, rows, args.force)
    write_csv(output / "method-evidence.csv", method_fields, method_rows, args.force)
    write_csv(output / "input-manifest.csv", manifest_fields, manifest_rows, args.force)
    write_text(output / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2) + "\n", args.force)
    write_text(output / "route-flow.mmd", graph, args.force)
    copy_bytes(output / "context-user-scope.csv", review_table, args.force)
    write_text(review_graph, graph, args.force)
    write_text(report_path, report, args.force)
    write_text(evidence_path, evidence, args.force)

    manifest_paths = [
        output / "context-user-scope.csv",
        output / "method-evidence.csv",
        output / "summary.json",
        output / "input-manifest.csv",
        output / "route-flow.mmd",
        report_path,
        evidence_path,
        review_table,
        review_graph,
    ]
    checksum_lines = [f"{sha256(path)}  {rel(root, path)}" for path in manifest_paths]
    write_text(output / "sha256sums.txt", "\n".join(checksum_lines) + "\n", args.force)
    print(json.dumps({"output": str(output), "routes": len(rows), "method_evidence": len(method_rows), "device_contacted": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
