#!/usr/bin/env python3
"""Close the preserved BootAfterSystemOTAReceiver -> PackageHelper path.

This is a host-only, static audit.  It reads the already-preserved PS7331
JADX, manifest, and baksmali artifacts; it never contacts ADB, sends a
broadcast, invokes Binder, executes an updater, or changes a package or
setting.  The output intentionally distinguishes an OOBE component writer
from a Fire Launcher/HOME writer.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date
from pathlib import Path


SCHEMA = "phase6my-bootafter-ota-package-helper-v1"
DEFAULT_OUTPUT = Path("artifacts/phase6my-bootafter-ota-package-helper-20260810-01")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def require(path: Path, markers: list[str]) -> None:
    text = read(path)
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"input drift in {path}: missing {missing}")


def write_text(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]], force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def paths(root: Path) -> dict[str, Path]:
    source = root / "artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources"
    return {
        "receiver": source / "com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java",
        "activation": source / "com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java",
        "package_helper": source / "com/amazon/oobe/commons/utils/PackageHelper.java",
        "settings_helper": source / "com/amazon/oobe/commons/utils/SettingsDBUtils.java",
        "manifest": root / "artifacts/phase6j/ota-oobe-manifest-audit-20260805-01/manifest.txt",
        "fosservices": root / "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log",
        "boot_framework": root / "decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log",
        "scope_report": root / "findings/phase-6mo-oobe-context-user-scope.md",
        "authorization_report": root / "findings/phase-6r-bootafter-system-ota-authorization.md",
    }


def validate(inputs: dict[str, Path]) -> None:
    for path in inputs.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    require(inputs["receiver"], [
        "public void onReceive(Context context, Intent intent)",
        "BOOT_AFTER_SYS_OTA.equals(intent.getAction())",
        "enableIncrementalFlow(context)",
        "setComponentEnabledSetting",
    ])
    require(inputs["activation"], [
        "activateOOBEIF(Context context)",
        "setSettingSecurePutIntFG",
        "USER_SETUP_COMPLETE",
        "IS_OOBE_ACTIVE",
    ])
    require(inputs["package_helper"], [
        "setComponentEnabledSetting",
        "public static void enableComponent",
        "public static void disableComponent",
    ])
    require(inputs["settings_helper"], [
        "Settings.Secure.putInt",
        "Settings.Global.putInt",
    ])
    require(inputs["manifest"], [
        "com.amazon.kindle.otter.oobe.BootAfterSystemOTAReceiver",
        "amazon.intent.action.BOOT_AFTER_SYSTEM_OTA",
        "android:name=\"com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA\"",
        "android:permission=\"android.permission.MANAGE_USERS\"",
    ])
    require(inputs["fosservices"], [
        "onBootPhase",
        "isUpgrade",
        "BOOT_AFTER_SYSTEM_OTA",
        "sendBroadcast",
    ])
    require(inputs["boot_framework"], [
        "handleReceiver",
        "getReceiverRestrictedContext",
        "resolveUserIdFromAuthority",
        "getIdentifier",
        "IActivityManager;.broadcastIntent",
    ])


def build_edges(root: Path) -> list[dict[str, object]]:
    receiver = "artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java"
    activation = "artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java"
    package_helper = "artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/oobe/commons/utils/PackageHelper.java"
    settings = "artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/oobe/commons/utils/SettingsDBUtils.java"
    fosservices = "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log"
    framework = "decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log"
    manifest = "artifacts/phase6j/ota-oobe-manifest-audit-20260805-01/manifest.txt"
    return [
        {
            "edge_id": "6MY-E01",
            "caller": "AmazonPackageManagerService.onBootPhase",
            "callee": "BootAfterSystemOTAReceiver.onReceive",
            "operation": "mContext.sendBroadcast(BOOT_AFTER_SYSTEM_OTA, RECEIVE_BOOT_AFTER_SYSTEM_OTA)",
            "scope_or_guard": "boot phase 550 AND PackageManagerService.isUpgrade()",
            "source": fosservices,
            "location": "96087-96126",
            "home_effect": "lifecycle trigger only",
            "verdict": "CONFIRMED_STATIC",
        },
        {
            "edge_id": "6MY-E02",
            "caller": "BootAfterSystemOTAReceiver.onReceive",
            "callee": "BootAfterSystemOTAReceiver.enableIncrementalFlow",
            "operation": "guarded action branch",
            "scope_or_guard": "BOOT_AFTER_SYS_OTA AND !isOOBEAlreadyRunning AND isNotInDemoMode",
            "source": receiver,
            "location": "27-46",
            "home_effect": "enters incremental OOBE only",
            "verdict": "CONFIRMED_STATIC",
        },
        {
            "edge_id": "6MY-E03",
            "caller": "BootAfterSystemOTAReceiver.enableIncrementalFlow",
            "callee": "PackageHelper.enableComponent",
            "operation": "enableComponent(context, OobeHomeActivity.class)",
            "scope_or_guard": "inherits receiver Context",
            "source": receiver,
            "location": "56-61",
            "home_effect": "enables OobeHomeActivity, not Fire Launcher",
            "verdict": "CONFIRMED_STATIC",
        },
        {
            "edge_id": "6MY-E04",
            "caller": "PackageHelper.enableComponent",
            "callee": "PackageManager.setComponentEnabledSetting",
            "operation": "state=1, flags=1, ComponentName(context, OobeHomeActivity)",
            "scope_or_guard": "context-derived user; no explicit user argument",
            "source": package_helper,
            "location": "16-18",
            "home_effect": "OOBE component-state mutation only",
            "verdict": "CONFIRMED_STATIC",
        },
        {
            "edge_id": "6MY-E05",
            "caller": "BootAfterSystemOTAReceiver.enableIncrementalFlow",
            "callee": "OOBEActivationHelper.activateOOBEIF",
            "operation": "activateOOBEIF(context)",
            "scope_or_guard": "inherits receiver Context",
            "source": receiver,
            "location": "56-61",
            "home_effect": "writes OOBE setup state; no preferred/HOME API",
            "verdict": "CONFIRMED_STATIC",
        },
        {
            "edge_id": "6MY-E06",
            "caller": "OOBEActivationHelper.activateOOBEIF",
            "callee": "SettingsDBUtils.setSettingSecurePutIntFG",
            "operation": "user_setup_complete=0; isOOBEActive=1",
            "scope_or_guard": "ContentResolver from supplied Context",
            "source": activation,
            "location": "53-56",
            "home_effect": "OOBE setup state only",
            "verdict": "CONFIRMED_STATIC",
        },
        {
            "edge_id": "6MY-E07",
            "caller": "SettingsDBUtils.setSettingSecurePutIntFG",
            "callee": "Settings.Secure.putInt",
            "operation": "putInt(ContentResolver, key, value)",
            "scope_or_guard": "no explicit putIntForUser at reviewed callsite",
            "source": settings,
            "location": "51-64",
            "home_effect": "OOBE setup state only",
            "verdict": "CONFIRMED_STATIC",
        },
        {
            "edge_id": "6MY-E08",
            "caller": "ActivityThread.handleReceiver / ContextImpl",
            "callee": "PackageManager and Settings provider calls",
            "operation": "receiver-restricted Context retains mUser; provider uses getUserId()",
            "scope_or_guard": "exact numeric user remains unencoded in preserved callsite",
            "source": framework,
            "location": "435176-435236; 449092-449185; 452137-452150",
            "home_effect": "context-bound user scope, not a User-0 proof",
            "verdict": "STRONG_CONTEXT_SCOPE",
        },
        {
            "edge_id": "6MY-E09",
            "caller": "BootAfterSystemOTAReceiver.onReceive catch(Throwable)",
            "callee": "PackageManager.setComponentEnabledSetting",
            "operation": "state=2, flags=1, BootAfterSystemOTAReceiver",
            "scope_or_guard": "only exception path; receiver self-disables",
            "source": receiver,
            "location": "43-46",
            "home_effect": "receiver self-disable; no Fire Launcher reference",
            "verdict": "CONFIRMED_STATIC",
        },
        {
            "edge_id": "6MY-E10",
            "caller": "OOBE manifest receiver declaration",
            "callee": "BootAfterSystemOTAReceiver",
            "operation": "enabled directBootAware receiver for BOOT_AFTER_SYSTEM_OTA",
            "scope_or_guard": "APK requests RECEIVE_BOOT_AFTER_SYSTEM_OTA; receiver block has no android:permission",
            "source": manifest,
            "location": "279-283; 531-541",
            "home_effect": "protected lifecycle metadata; not a shell selector",
            "verdict": "CONFIRMED_METADATA",
        },
    ]


def build_home_rows() -> list[dict[str, object]]:
    return [
        {
            "subject": "Fire Launcher literal in reviewed receiver/helper chain",
            "observed": False,
            "scope": "four OOBE source files and direct helper chain",
            "classification": "BOUNDED_NEGATIVE",
            "confidence": "CONFIRMED_WITHIN_SCOPE",
        },
        {
            "subject": "ordinary setHomeActivity/addPreferredActivity/replacePreferredActivity",
            "observed": False,
            "scope": "BootAfterSystemOTAReceiver, OOBEActivationHelper, PackageHelper, SettingsDBUtils",
            "classification": "BOUNDED_NEGATIVE",
            "confidence": "CONFIRMED_WITHIN_SCOPE",
        },
        {
            "subject": "OobeHomeActivity HOME relevance",
            "observed": True,
            "scope": "manifest OobeHomeActivity priority 100 and MANAGE_USERS",
            "classification": "SETUP_WIZARD_HOME_ONLY",
            "confidence": "CONFIRMED_STATIC",
        },
        {
            "subject": "exact numeric user receiving post-OTA state changes",
            "observed": False,
            "scope": "preserved sender/context path",
            "classification": "UNRESOLVED_CONTEXT_USER",
            "confidence": "PENDING",
        },
        {
            "subject": "safe live replay of BOOT_AFTER_SYSTEM_OTA",
            "observed": False,
            "scope": "device operation",
            "classification": "RISK_REJECTED",
            "confidence": "CONFIRMED_SAFETY_BOUNDARY",
        },
    ]


def write_outputs(root: Path, output: Path, inputs: dict[str, Path], force: bool) -> list[Path]:
    edges = build_edges(root)
    home_rows = build_home_rows()
    output.mkdir(parents=True, exist_ok=True)
    edge_fields = ["edge_id", "caller", "callee", "operation", "scope_or_guard", "source", "location", "home_effect", "verdict"]
    home_fields = ["subject", "observed", "scope", "classification", "confidence"]
    write_csv(output / "call-edges.csv", edge_fields, edges, force)
    write_csv(output / "home-relevance.csv", home_fields, home_rows, force)

    manifest_path = output / "input-manifest.csv"
    manifest_rows = [
        {"key": key, "path": path.as_posix(), "sha256": sha256(path)}
        for key, path in sorted(inputs.items())
    ]
    write_csv(manifest_path, ["key", "path", "sha256"], manifest_rows, force)

    graph = """flowchart LR
  S["AmazonPackageManagerService.onBootPhase(550)\\nPackageManagerService.isUpgrade()"] -->|protected explicit broadcast| R["BootAfterSystemOTAReceiver.onReceive"]
  R -->|guarded branch| E["enableIncrementalFlow(context)"]
  E --> P["PackageHelper.enableComponent"]
  P -->|state=1 flags=1| O["OobeHomeActivity"]
  E --> A["OOBEActivationHelper.activateOOBEIF"]
  A --> U["SettingsDBUtils / OOBE setup keys"]
  U -. context-derived user .-> C["ContextImpl.mUser / provider user mapping"]
  R -. exception only, state=2 .-> X["self-disable receiver"]
  P -. no Fire literal in bounded chain .-> F["Fire Launcher HOME writer not established"]
"""
    write_text(output / "call-graph.mmd", graph, force)

    summary = {
        "schema": SCHEMA,
        "input_count": len(inputs),
        "edge_count": len(edges),
        "home_relevance_row_count": len(home_rows),
        "receiver_to_package_helper": "CONFIRMED_STATIC",
        "direct_fire_launcher_write_in_bounded_chain": False,
        "direct_preferred_home_write_in_bounded_chain": False,
        "oobe_home_component_write": True,
        "exact_post_ota_user": "PENDING",
        "live_broadcast_replay": "RISK_REJECTED",
        "device_contacted": False,
        "adb": False,
        "binder_transaction": False,
        "ota_executed": False,
        "package_mutation": False,
        "settings_mutation": False,
        "reboot": False,
    }
    write_text(output / "summary.json", json.dumps(summary, indent=2, sort_keys=True) + "\n", force)

    generated = [path for path in output.iterdir() if path.is_file() and path.name != "sha256sums.txt"]
    checks = "".join(f"{sha256(path)}  {path.name}\n" for path in sorted(generated))
    write_text(output / "sha256sums.txt", checks, force)
    return sorted(generated + [output / "sha256sums.txt"])


def write_canonical(root: Path, output: Path, inputs: dict[str, Path], force: bool) -> list[Path]:
    report = root / "findings/phase-6my-ota-receiver-package-helper-closure.md"
    evidence = root / "findings/phase-6my-evidence-index.md"
    table = root / "output/tables/phase6my-ota-receiver-package-helper.csv"
    graph = root / "output/call-graphs/phase6my-ota-receiver-package-helper.mmd"
    generated = [report, evidence, table, graph]
    edges = build_edges(root)
    write_csv(table, ["edge_id", "caller", "callee", "operation", "scope_or_guard", "source", "location", "home_effect", "verdict"], edges, force)
    graph_text = (output / "call-graph.mmd").read_text(encoding="utf-8")
    write_text(graph, graph_text, force)
    input_lines = "; ".join(f"`{key}` `{sha256(path)}`" for key, path in sorted(inputs.items()))
    report_text = f"""# Phase 6MY — BootAfterSystemOTAReceiver → PackageHelper closure

Date: {date.today().isoformat()}

Scope: host-only static analysis of the preserved PS7331 OOBE/OTA artifacts.
No ADB, broadcast, Binder transaction, updater, reboot, package mutation,
settings mutation, Fire Launcher mutation, or partition write was performed.

## Result

**已證實（bounded static path）:**

```text
AmazonPackageManagerService.onBootPhase(550)
  → guarded BOOT_AFTER_SYSTEM_OTA broadcast
  → BootAfterSystemOTAReceiver.onReceive
  → enableIncrementalFlow(context)
  → PackageHelper.enableComponent(context, OobeHomeActivity.class)
  → PackageManager.setComponentEnabledSetting(state=1, flags=1)
```

The same branch calls `OOBEActivationHelper.activateOOBEIF(context)`, which
writes OOBE setup keys through `Settings.Secure`/`Settings.Global` using a
context-derived `ContentResolver`. The receiver catch path can disable the
receiver itself (`state=2`), not Fire Launcher.

**已證實（bounded negative):** the reviewed receiver, OOBE activation helper,
PackageHelper, and SettingsDBUtils contain no `com.amazon.firelauncher`,
`setHomeActivity`, `addPreferredActivity`, or `replacePreferredActivity`
reference. Therefore this path is an OOBE/Setup Wizard component-state writer,
not evidence of a normal Fire Launcher HOME writer.

**高可信推論:** the state operations retain a context-derived user scope;
the preserved framework client path shows `ContextImpl.mUser` flowing into
provider/user resolution. The exact numeric post-OTA user is not encoded in
the selected sender callsite and remains **待驗證**.

**因風險拒絕測試:** replaying `BOOT_AFTER_SYSTEM_OTA` or executing the OTA
transition is rejected because the branch can enable `OobeHomeActivity` and
write `user_setup_complete`, `device_provisioned`, and `isOOBEActive`.

## Evidence and locations

| Edge | Evidence |
|---|---|
| Sender guard and broadcast | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96087-96126` |
| Receiver branch and error path | `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-61` |
| Package state helper | `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/oobe/commons/utils/PackageHelper.java:11-22` |
| OOBE setting helper | `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:53-56`; `SettingsDBUtils.java:51-64` |
| Context/user propagation | `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log:435176-435236,449092-449185,452137-452150` |
| Manifest metadata | `artifacts/phase6j/ota-oobe-manifest-audit-20260805-01/manifest.txt:279-283,531-541` |

Input hashes: {input_lines}

Generated artifact: `{output.relative_to(root)}`. Its `sha256sums.txt` must
pass before publication.

## Consequence for launcher/root research

This branch does not provide a supported or demonstrated ADB route to disable
`com.amazon.firelauncher`, change the ordinary HOME preferred record, or gain
root. It should not be replayed as a launcher workaround. The remaining safe
next step is provenance analysis of the exact framework service-context user
selection or a naturally occurring official OTA observation; neither justifies
manual broadcast injection.
"""
    write_text(report, report_text, force)
    evidence_text = f"""# Phase 6MY evidence index

All entries are host-only and refer to immutable preserved inputs. No device
was contacted.

| Evidence ID | Source | Observation | Classification | Confidence |
|---|---|---|---|---|
| 6MY-E01 | `fosservices:96087-96126` | Phase 550 + `isUpgrade()` sends the post-OTA action with permission | guarded lifecycle sender | Confirmed |
| 6MY-E02 | `BootAfterSystemOTAReceiver.java:27-61` | Guarded branch calls OOBE enablement; catch disables only receiver | OOBE state path | Confirmed |
| 6MY-E03 | `PackageHelper.java:11-22` | Standard component-state API receives OOBE component and state 1/2 | component writer | Confirmed |
| 6MY-E04 | `OOBEActivationHelper.java:53-56`; `SettingsDBUtils.java:51-64` | OOBE setup keys are written through context ContentResolver | settings writer | Confirmed |
| 6MY-E05 | `boot-framework-dis:435176-435236,449092-449185,452137-452150` | Receiver context retains user scope into PM/provider calls | user mapping | Strong evidence |
| 6MY-E06 | bounded source scan | No Fire Launcher or ordinary preferred-HOME writer in reviewed chain | bounded negative | Confirmed within scope |
| 6MY-E07 | safety boundary | Manual broadcast/OTA replay can change setup and component state | rejected experiment |因風險拒絕測試|

Input/output integrity is recorded in `{output.relative_to(root)}/sha256sums.txt`.
"""
    write_text(evidence, evidence_text, force)
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    inputs = paths(root)
    validate(inputs)
    output = (args.output or (root / DEFAULT_OUTPUT)).resolve()
    canonical = [
        root / "findings/phase-6my-ota-receiver-package-helper-closure.md",
        root / "findings/phase-6my-evidence-index.md",
        root / "output/tables/phase6my-ota-receiver-package-helper.csv",
        root / "output/call-graphs/phase6my-ota-receiver-package-helper.mmd",
    ]
    if args.dry_run:
        print(f"schema={SCHEMA}")
        print(f"output={output}")
        print("device_contacted=false")
        print("broadcast_sent=false")
        print("binder_transaction=false")
        print("ota_executed=false")
        print("package_mutation=false")
        print("settings_mutation=false")
        print("reboot=false")
        print("inputs:")
        for key, path in sorted(inputs.items()):
            print(f"  {key}: {path}")
        print("canonical_outputs:")
        for path in canonical:
            print(f"  {path}")
        return 0
    existing = [path for path in [
        output / "call-edges.csv", output / "home-relevance.csv", output / "input-manifest.csv",
        output / "call-graph.mmd", output / "summary.json", output / "sha256sums.txt", *canonical,
    ] if path.exists()]
    if existing and not args.force:
        raise FileExistsError("refusing to overwrite existing outputs:\n" + "\n".join(map(str, existing)))
    write_outputs(root, output, inputs, args.force)
    write_canonical(root, output, inputs, args.force)
    print(json.dumps({"schema": SCHEMA, "output": str(output), "edge_count": 10, "device_contacted": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
