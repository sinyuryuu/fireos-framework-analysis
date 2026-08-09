# Phase 6MO evidence index

Generated: 2026-08-10
Schema: `phase6mo-oobe-context-user-scope-v1`
Scope: host-only; no device contact or state mutation.

| Evidence ID | File / method | Location | Observation | Confidence |
|---|---|---:|---|---|
| 6MO-E01 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` / `AmazonPackageManagerService.onBootPhase` | 96087-96126 | Phase 550 + `isUpgrade()` + `mContext.sendBroadcast` | Confirmed |
| 6MO-E02 | `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log` / `ContextImpl.sendBroadcast` | 452691-452721 | `getUserId()` is passed to `IActivityManager.broadcastIntent` | Confirmed |
| 6MO-E03 | `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log` / `ActivityThread.handleReceiver` | 435176-435236 | Receiver context is built and `getReceiverRestrictedContext()` is passed to `onReceive` | Confirmed |
| 6MO-E04 | `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log` / `ContextImpl` constructor and `createAppContext` | 449212-449298;449515-449534 | `UserHandle` is stored; null defaults to `Process.myUserHandle()` | Confirmed |
| 6MO-E05 | `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log` / `ApplicationContentResolver` + `getUserId` | 449092-449185;452137-452150 | Provider acquisition derives user from ContextImpl | Strong evidence |
| 6MO-E06 | `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log` / `createDeviceProtectedStorageContext` | 450958-450975 | Derived storage context copies `mUser` | Strong evidence |
| 6MO-E07 | `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java` / `enableIncrementalFlow` | 56-61 | OOBE component and setup helper receive same Context | Confirmed |
| 6MO-E08 | `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java` / `activateOOBEIF` | 53-56 | Secure setting writes receive context-derived ContentResolver | Confirmed |
| 6MO-E09 | `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/oobe/commons/utils/PackageHelper.java` / `PackageHelper` | 11-22 | Component state calls use context package manager | Confirmed |
| 6MO-E10 | `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java; artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java; artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/oobe/commons/utils/SettingsDBUtils.java; artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/oobe/commons/utils/PackageHelper.java` | bounded corpus | No direct ordinary Fire Launcher HOME/preferred writer found | Disproved (bounded hypothesis) |

## Interpretation

The evidence establishes a context-derived user boundary, not an exact User-0 claim. The exact user mapping remains `待驗證`.
