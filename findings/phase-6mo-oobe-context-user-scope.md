# Phase 6MO — OOBE Context / user-scope provenance closure

Date: 2026-08-10

## Scope and safety

This is host-only static analysis of preserved PS7331 JADX and baksmali artifacts. No ADB connection, Binder/service call, broadcast, ioctl, OTA/recovery execution, reboot, settings mutation, package mutation, or partition write was performed.

## Executive result

**已證實：** the Amazon post-OTA sender reaches `Context.sendBroadcast(Intent, permission)` only from the guarded `AmazonPackageManagerService.onBootPhase(550)` → `isUpgrade()` branch. The Android framework implementation passes the sending `ContextImpl.getUserId()` into `IActivityManager.broadcastIntent`.

**已證實：** `ActivityThread.handleReceiver()` constructs the receiver application context from `ReceiverData.info.applicationInfo`, creates the application, derives a receiver-restricted `Context`, and invokes `BootAfterSystemOTAReceiver.onReceive(context, intent)`. The OOBE source passes that same context into `PackageHelper` and `SettingsDBUtils`.

**高可信推論：** the settings and component-state operations are context/process-user scoped. `ContextImpl` stores a `UserHandle`; `getUserId()` returns its identifier; `ApplicationContentResolver` uses that value when acquiring providers. Device-protected context creation preserves `mUser`.

**待驗證：** the exact user ID delivered by the post-OTA broadcast on this Fire OS build. The selected static sender does not explicitly pass `USER_SYSTEM`, `USER_CURRENT`, or `USER_ALL`, and the preserved app-side receiver path has no explicit user argument. Therefore this report does **not** claim User 0.

## Evidence chain

```text
AmazonPackageManagerService.onBootPhase(550)
  -> isUpgrade()
  -> mContext.sendBroadcast(BOOT_AFTER_SYSTEM_OTA, permission)
  -> ContextImpl.sendBroadcast -> getUserId()
  -> IActivityManager.broadcastIntent(..., userId)
  -> ActivityThread.handleReceiver(ReceiverData)
  -> LoadedApk.makeApplication -> ContextImpl.mUser
  -> getReceiverRestrictedContext()
  -> BootAfterSystemOTAReceiver.onReceive(context, intent)
  -> PackageHelper / SettingsDBUtils sinks
```

Exact locations: sender `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96087-96126`; framework receiver delivery `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log:435176-435236`; `ContextImpl` constructor/default `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log:449212-449298, 449515-449534`; provider user mapping `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log:449092-449185, 452137-452150`; broadcast user argument `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log:452691-452721`.

## Sink analysis

`BootAfterSystemOTAReceiver.enableIncrementalFlow()` calls `PackageHelper.enableComponent(context, OobeHomeActivity.class)` and `OOBEActivationHelper.activateOOBEIF(context)` (`BootAfterSystemOTAReceiver.java:56-61`). `PackageHelper` calls `context.getPackageManager().setComponentEnabledSetting(...)` (`PackageHelper.java:11-22`). The OOBE activation helper passes `context.getContentResolver()` into `SettingsDBUtils.setSettingSecurePutIntFG()` (`OOBEActivationHelper.java:53-56`), which calls `Settings.Secure.putInt(contentResolver, key, value)` (`SettingsDBUtils.java:51-64`).

The four reviewed OOBE sources contain no `setHomeActivity`, `addPreferredActivity`, `replacePreferredActivity`, or `com.amazon.firelauncher` reference. This is **已排除／bounded negative** for “the reviewed OOBE helper is the ordinary Fire Launcher preferred/HOME writer”; it is not a binary-wide absence claim.

## Decision table

| Finding | Verdict | Evidence |
|---|---|---|
| Post-OTA sender has phase and upgrade guards | 已證實 | `fosservices:96087-96126` |
| Sender uses explicit `sendBroadcast(..., permission)` rather than `sendBroadcastAsUser` | 已證實 | `fosservices:96124-96126` |
| Framework derives broadcast user argument from sender ContextImpl | 已證實 | `boot-framework:452691-452721` |
| Receiver callback receives a receiver-restricted Context | 已證實 | `boot-framework:435176-435236` |
| ContextImpl retains a UserHandle and exposes getUserId | 已證實 | `boot-framework:449212-449298;452137-452150` |
| Settings provider operations retain that context-derived user scope | Strong evidence | `boot-framework:449092-449185`; `SettingsDBUtils.java:51-64` |
| Exact post-OTA delivery user is User 0 | 待驗證 | no explicit user in selected sender/delivery evidence |
| OOBE helper directly rewrites ordinary Fire Launcher HOME preference | 已排除（bounded） | four OOBE source files |
| Manual replay is safe | 因風險拒絕測試 | prior Phase 6R authorization report |

## Remaining minimal target

The remaining question can only be closed by a stronger host artifact showing how the system-service `mContext` is created and which broadcast user is selected by the corresponding ActivityManager path, or by observing a naturally occurring official OTA transition with read-only captures. Do not manually replay `BOOT_AFTER_SYSTEM_OTA`; it changes OOBE, component, accessibility, and secure-setting state.

## Reproduction

```sh
python3 tools/scripts/audit_phase6mo_oobe_context_user_scope.py --dry-run
python3 tools/scripts/audit_phase6mo_oobe_context_user_scope.py
```

Generated artifact: `artifacts/phase6mo-oobe-context-user-scope-20260810-01`.
