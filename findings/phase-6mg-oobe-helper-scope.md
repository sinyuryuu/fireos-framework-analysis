# Phase 6MG — OOBE helper scope closure

Date: 2026-08-10
Classification: host-only static analysis; no device mutation.

## Result

The four preserved PS7331 JADX sources contain 29 relevant signals. The
reviewed helper code has no `Settings.*put*ForUser` call and no explicit user
ID argument at the `PackageHelper` component-state callsite. That establishes
the shape of the helper, but **does not prove that it targets User 0**. The
effective scope is bound to the supplied `Context`/`ContentResolver` and the
framework client implementation; that mapping remains **待驗證**.

The OOBE path is a guarded setup/OTA lifecycle path, not evidence of a normal
HOME-selection API or a shell-writable Fire Launcher writer.

## Exact observations

| Source | Location | Observation | Classification |
|---|---:|---|---|
| `SettingsDBUtils.java` | 51–64 | `Settings.Secure.putString`, `Settings.Secure.putInt`, and `Settings.Global.putInt` receive a `ContentResolver`, key, and value; no `ForUser` overload is visible. | **已證實** |
| `PackageHelper.java` | 11–22 | `disableComponent` uses state `2`, `enableComponent` uses state `1`, both with flags `1`, and both construct a `ComponentName` from the supplied `Context`. | **已證實** |
| `OOBEActivationHelper.java` | 29–34, 53–74 | The helper reads `user_setup_complete` and `device_provisioned`, and the IF path writes `user_setup_complete=0` and `isOOBEActive=1`; it does not write HOME/preferred state in the reviewed source. | **已證實** |
| `BootAfterSystemOTAReceiver.java` | 27–80 | The receiver performs guarded migration/action/OOBE checks, enables `OobeHomeActivity`, and calls `activateOOBEIF(context)`. | **已證實** |
| `AmazonPackageManagerService` | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96107-96126` | The sender uses boot phase `550`, `isUpgrade()`, and the protected OTA broadcast permission. | **已證實** |

The generated inventory is reproducible:

- Script: `tools/scripts/audit_phase6mg_oobe_helper_scope.py`
- Table: `output/tables/phase6mg-oobe-helper-scope.csv`
- Graph: `output/call-graphs/phase6mg-oobe-helper-scope.mmd`
- Artifact: `artifacts/phase6mg-oobe-helper-scope-20260810-01/`
- Schema: `phase6mg-oobe-helper-scope-v1`
- Signal count: `29`
- Explicit user-scope signals: `0`
- Device mutation: `false`

## User-scope boundary

The `FG` suffix in helper method names is only a naming signal. It must not be
read as “foreground user” or “User 0” without tracing the `Context` creation,
the `ContentResolver` user handle, and the framework PackageManager client.
Likewise, the absence of `ForUser` in an app-side call does not by itself
identify the current user. The generated graph therefore records:

```text
OOBE receiver
  -> PackageHelper / SettingsDBUtils
       -> context-bound user scope
            -> exact user mapping pending
```

## HOME relevance

`OobeHomeActivity` is a setup-only HOME candidate with a lifecycle guard and a
saved baseline in which it is disabled after provisioning. The reviewed helper
sources contain no `setHomeActivity`, `addPreferredActivity`,
`replacePreferredActivity`, or `com.amazon.firelauncher` HOME write. This
supports **已排除** for “OOBE helper is the ordinary User-0 Fire Launcher
restoration mechanism” on the current evidence. It does not claim that an OTA
OOBE transition is harmless; that transition was intentionally not triggered.

## Safety disposition

The following were not executed: manual `BOOT_AFTER_SYSTEM_OTA` broadcast,
OOBE component enable, provisioning-key write, OTA/recovery, or reboot. Those
operations would change setup state or lifecycle state and are not required to
answer the static scope question.
