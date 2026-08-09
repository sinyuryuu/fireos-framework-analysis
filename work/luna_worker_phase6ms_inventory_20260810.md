# Phase 6MS host-only IPC inventory — 2026-08-10

## Scope and baseline

This is a read-only host inventory at `HEAD a38854ed89c6f663b75725746c14080e76f68585` (`Add Phase 6MQ profile closure and 6MR input IPC matrix`). The preceding public baseline is `36d354adf0f3b7ee54491f3f79cc84478632e5f4`. No device, ADB, Binder/service call, transaction, ioctl, OTA/recovery, root, reboot, or runtime mutation was used. Only this report is added.

The primary disassembly sources are:

| Source | SHA-256 | Relevant ranges |
|---|---|---|
| `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` | `IAmazonAccessibilityManager.Stub.Proxy` 394117–394266; `IAmazonActivityManager.Stub.Proxy` 394353–394885; `IAmazonDevicePolicyManager.Stub.Proxy` 397105–397282; `IAmazonWindowManager.Stub.Proxy` 400006–400264; `IAmazonPackageManager.Stub.Proxy` 402917–403398 |
| `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | Accessibility publication 35432; ActivityManager publication 41083; DevicePolicy publication 46156; WindowManager publication 56244; PackageManager publication 96136 |

Evidence labels mean: **Confirmed** = the cited static artifact directly shows the publication/proxy or permission-to-local-call edge; **Strong** = a bounded caller/permission/identity/sink edge is visible, but persistence, consumer, or HOME effect is not proven; **Unknown** = the relevant edge or runtime identity/behavior is not established by these host artifacts.

## Existing coverage and exclusions

* Phase 6MN is a 42-row user-scope route matrix. Its route matrix is `artifacts/phase6mn-ipc-user-scope-20260810-01/route-matrix.csv`, SHA-256 `a156538f89cff05e098a01fce169fda4e88f65b86fe4b06054d740cbd615e56b`; summary SHA-256 `36e2c71079b4482fbb64e4672a57a00d9a2d9e5b233395e3cce3fa4089dbe669`. It does not prove a selected untrusted route to a User-0 Fire Launcher/HOME/package sink or the complete private Amazon caller universe.
* Phase 6KV’s package-manager HOME caller table is `output/tables/phase6kv-pms-home-callers.csv`, SHA-256 `dc1a86ea85904e3775704944fa86364a9a89033f6146eed0dac8b324b7028382`. It has 25 standard/static invoke sites and no additional Amazon `setHomeActivity`, `replacePreferredActivity`, or `addPersistentPreferredActivity` site. It does not close Amazon package metadata/flags or Amazon DPM restriction paths below.
* Phase 6BK’s method map is `artifacts/phase6bk/ipc-ota-closure-20260810-02/method-map.csv`, SHA-256 `b487531c8ae8dbf55812feb463f666810eb63acca98d3ce57dbffddf37567acf`; its evidence-index SHA-256 is `60374990674ef5bb8aefdc7123248ca2ab2118ea84497358d7002017f00ebb40`. It records `preWarmApplicationForUser`, `setPipVisibility`, profile methods, and service boundaries, but does not provide a complete five-interface caller→permission→identity→sink ledger.
* Phase 6MQ closes the profile-launcher helper boundary: `findings/phase-6mq-profile-launcher-helper-closure.md`, SHA-256 `a8b51750e7d626a971e32937c09c5c459930df88f072d73dfe15d55aa0b07a7a`; its bounded slice shows `PROFILE_INTERACTION` enforcement and explicit profile-picker start, not HOME/preferred/package-state mutation.
* Phase 6MR already closes `IAmazonInputManager`; it is deliberately not redone. Its method matrix `artifacts/phase6mr-amazon-input-manager-20260810-01/method-matrix.csv` has SHA-256 `10a7ea5396f498e2c00fac94844519b3db6e5386e2d7901a49e973286a618ae3`; summary SHA-256 `e5888be4f032cee8fe4ce546199893924898521f2c2183e68d4aaa714e016beb`. That closure records `amazon_input`, 26 remote transactions, event permissions, Binder pid/uid reads for injection, and no HOME/package sink.
* Phase 6R remains a host-only OTA authorization/static boundary, not an invocation of these services: `findings/phase-6r-evidence-index.md`, SHA-256 `fc51d7b8fe40f7c5eb8f89f40ef0bfe187f02b64637fdcc07168f7443e295b6c`; its OTA receiver matrix SHA-256 is `8c793682c38b20c60bb0d6f793217bda129669da12e35fd803d319b9cce29a34`.

## Five requested Amazon interfaces

### `IAmazonPackageManager` — strongest package-state-adjacent gap

**Confirmed:** The proxy exposes 11 remote methods in `boot-fosframework/disassembly.log:402917–403398`: `getAmazonFlagsForUser`, `setAmazonFlagsForUser`, `removeAmazonFlagsForUser`, `setAmazonMetadataForUser`, `removeAmazonMetadataForUser`, `registerProxyReceiver`, `deregisterProxyReceiver`, `isFtvSpecApp`, `isPreInstalledAppWithFtvSpec`, `shouldAllowMicAccess`, and `getConfigurationHelper`. The service is published at `fosservices/disassembly.log:96136`.

**Strong:** In the service slice `fosservices/disassembly.log:95866–96037`, the four mutators call `Context.checkCallingOrSelfPermission` for `amazon.permission.ADD_RM_PKG_METADATA`, accept explicit user IDs, and call the following local sinks: `AmazonApplicationFlags.setAmazonFlagsForUser`, `removeAmazonFlagsForUser`, `setAmazonMetadataForUser`, and `removeAmazonMetadataForUser` (disassembly around `06988a–069974`). This is a direct caller→permission→argumented user→Amazon application-flags/metadata edge. The artifact does not yet establish whether `AmazonApplicationFlags` persists to package state, is consumed by launcher selection, or reaches preferred HOME/component state; no `clearCallingIdentity` is shown in these bounded methods.

**Unknown:** `registerProxyReceiver`/`deregisterProxyReceiver` have a receiver/broadcast-adjacent sink but their effective authorization and caller identity are not closed here. The read methods expose package decisions but do not prove a HOME sink. This interface is not closed by the 6KV 25-site HOME table.

### `IAmazonDevicePolicyManager`

**Confirmed:** The proxy has `setRestrictionForUser` and `clearRestrictionForUser` in `boot-fosframework/disassembly.log:397105–397282`; publication is `fosservices/disassembly.log:46156`.

**Strong:** The service slice `fosservices/disassembly.log:45935–46108` delegates both methods to `setUserRestrictionForUser`. The Amazon-restriction branch calls `DevicePolicyManagerService.setUserRestrictionForUser`; the mapped-restriction branch checks a mapped permission, calls `UserManager.setUserRestriction` with an explicit `UserHandle(int)`, and brackets the write with `clearCallingIdentity`/`restoreCallingIdentity` (around `03bf7a–03bfee`). `checkPermission` reads `Binder.getCallingUid` and has a system/root-style allow path (around `03bef4–03bf58`). This closes a policy-state sink, not a HOME/package-state sink.

**Unknown:** No static edge here proves Fire Launcher selection, preferred activity, package enablement, or the exact non-system caller capable of reaching this service. The 6KV DPM package-enable rows do not cover this Amazon restriction interface.

### `IAmazonActivityManager`

**Confirmed:** The proxy has 14 remote methods in `boot-fosframework/disassembly.log:394353–394885`, including `preWarmApplicationForUser`, `onActivityResume`, `isOnHomeStack`, PIP/multi-window controls, activity-switch observer registration, and CPU/process helpers. Publication is `fosservices/disassembly.log:41083`.

**Strong:** `preWarmApplicationForUser` is already represented in Phase 6BK/6MN (`fosservices/disassembly.log:40453–40534`): permission check, `clearCallingIdentity`/restore, and `startProcessLocked`; it is process-start, not HOME selection. The PIP controls show permission/enforcement and state/control sinks in the ActivityManager service slice (around `037072` onward), but their caller identity and relation to Fire Launcher/package state are not closed.

**Unknown:** `onActivityResume` and activity-switch observers are HOME-adjacent candidates, but the current artifacts do not prove a caller→permission→identity→HOME/package sink chain. No new preferred-HOME writer was found in Phase 6KV.

### `IAmazonWindowManager`

**Confirmed:** The proxy at `boot-fosframework/disassembly.log:400006–400264` exposes `getLidState`, `isPipActive`, `lockNow`, `setOverscan`, `setPipVisibility`, and `stopAppPinningMode`; publication is `fosservices/disassembly.log:56244`.

**Strong:** The service slice `fosservices/disassembly.log:56070–56179` reaches WMS `lockNow`/`setOverscan`, a PIP visibility state setter, and status-bar `stopAppPinningMode` with status-bar permission enforcement downstream. `setPipVisibility` is present in the 6BK map. These are display/window/pinning sinks, not demonstrated HOME/package-state sinks.

**Unknown:** Effective permission at each wrapper, Binder caller identity, and any launcher/package-state consumer are unresolved. No static evidence here establishes preferred HOME mutation.

### `IAmazonAccessibilityManager`

**Confirmed:** The proxy at `boot-fosframework/disassembly.log:394117–394266` exposes three remote methods: `magnificationCanvasAddLine`, `magnificationCanvasAddRect`, and `magnificationCanvasClear`; publication is `fosservices/disassembly.log:35432`. The service name is `amazonaccessibilitymanager` (`fosservices/disassembly.log:032804–032808`).

**Strong:** The three methods check `com.amazon.logan.permission.DRAW_MAGNIFICATION_RECT` through the service permission helper (`fosservices/disassembly.log:032760–0328e4`) and call the magnification-canvas line/rectangle/clear sinks. No caller UID or identity transition is shown in the bounded wrapper.

**Unknown / out of target path:** Nothing in this slice connects the canvas sink to Fire Launcher, HOME, package state, or component preference. It is recorded for completeness but is not a useful next HOME/package closure.

## Smallest non-overlapping next closure

Recommend one bounded host-only task: **trace `AmazonApplicationFlags` from the four `IAmazonPackageManager` mutators to its first persistence and first consumer, then test only by static references whether a consumer gates launcher/HOME/component/package state.** Use the existing `fosservices` disassembly hash above, starting from the four callsites around `06988a–069974`; record method, explicit user argument, permission, Binder identity handling, storage writer/reader, and any call to package/component/preferred-activity APIs. Stop at the first proven sink or at an unresolved external/native boundary. Do not invoke the interface or infer runtime UID/state.

This task is smaller and non-overlapping because 6KV already exhausts the known standard HOME-callers, 6MN covers user-scope rows, 6MQ covers profile-picker/helper behavior, 6MR closes InputManager, and the current five-interface scan has not yet closed Amazon flags/metadata persistence or consumption. A result showing “metadata-only, no HOME/package consumer” is itself a useful negative closure.

## Worktree / validation

No existing file was edited, no test/device action was run, and no commit or push was performed. The only intended new path is `work/luna_worker_phase6ms_inventory_20260810.md`.
