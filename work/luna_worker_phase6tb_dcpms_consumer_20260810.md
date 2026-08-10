# Phase 6TB — DCPMS CDE consumer closure

## Scope and result

Host-only, read-only static review of the exact-build DCPMS JADX source, saved VDEX disassembly, the exact DCPMS manifest/permission evidence, and Phase6SV. No broadcast, component start, settings mutation, or test was performed.

The four Phase6SV routes close at DCPMS CDE attribute persistence and/or CDE policy/evaluation. No downstream caller from these routes was found that invokes PackageManager state mutation, HOME/preferred-component selection, component enable/disable, platform SettingsProvider writes, or OTA apply/recovery. This is a bounded static negative, not a claim that no other independent system path can reach those sinks.

## Exact-build chain

`PCAActiveProfileReceiver` dispatches to `UpdatePCAProfileTypeAndEvalHelper`: `PROGRAM_ID` selects device PCA/profile and OS-user attributes; `PACKAGE_NAME` selects active-app-list update. Both paths call `DeviceExperienceModeEvaluator.evaluate()`.

`DeviceUserSwitchReceiver` and `AccountPropertyChangeReceiver` dispatch to `UpdateOSUserTypeAndEvalHelper`. That helper persists OS-user type, conditionally PCA profile type, clears the child active-app list, and calls the evaluator. The user-switch receiver also enqueues `UpdateOSUserTypeService`; this remains the same DCPMS helper path.

`GlobalContentSyncEventReceiver` only enqueues `GlobalContentSyncEventService`; its `onHandleWork` calls `ArcusSyncService.syncCDEPolicy()`. The remote-config callback/persistence route is CDE policy synchronization, not OTA installation or recovery.

`CDEAttributesPersistenceService` uses DCPMS `KeyValueStore` instances backed by `Context.createDeviceProtectedStorageContext().getSharedPreferences(...)`. The stores contain CDE policy, computed profile/user/target/op-mode/active-app attributes, and the computed CDE decision. They are not platform SettingsProvider writes.

The evaluator reads those stores, computes a `DeviceChildExperienceModeDecision`, persists it, and on a changed decision sends: (1) the permission-protected DCPMS Android broadcast `com.amazon.dcpms.ACTION_DEVICE_CDE_DECISION_UPDATED`, (2) registered DCPMS Binder callbacks, and (3) an optional ODOT cloud enqueue when policy enables it. These are the observed non-platform CDE outputs; none is a HOME/PMS/preferred/component-enabled/OTA sink.

## VDEX and manifest/permission cross-check

The saved VDEX disassembly has no `DCPMS`, `DeviceExperienceMode`, `ACTION_DEVICE_CDE`, `GET_DEVICE_CDE`, or CDE endpoint class/string hit. It does show an independent `AmazonUserManagerService.BinderService.enableKftLauncherComponent` method using `setComponentEnabledSetting`/`setApplicationEnabledSetting` for `com.amazon.firelauncher` (both normal and OTA-PS7331 disassembly rows). No call edge from the DCPMS CDE chain to that method was established. Therefore that VDEX launcher sink is explicitly out of this closure.

The exact DCPMS manifest declares the three lifecycle receivers and the global-sync receiver as exported; account-property and global-sync receivers carry their respective receiver permissions. The DCPMS service and JobIntentServices are separately permissioned. Phase6SV and the saved permission evidence identify `com.amazon.dcp.sso.action.AmazonAccountPropertyService.property.changed` as protected/signature-level in the observed package state; this does not change the downstream sink result. `USER_SWITCHED` is a protected framework action. No manifest or permission declaration adds a HOME, preferred-activity, PackageManager mutation, SettingsProvider, or OTA/recovery call to the DCPMS route.

## Bounded negative and residual boundary

Within the reviewed exact-build sources and saved VDEX evidence: **no DCPMS CDE consumer sink was found beyond CDE persistence/evaluation, DCPMS decision notification/Binder, ODOT enqueue, and CDE remote-policy sync**. In particular, no evidence connects any of the four routes to Home resolver selection, preferred activity state, package/component enabled state, platform settings, OTA apply, or recovery execution. This is a static bounded negative; it does not infer ordinary-app reachability or prove producer authorization beyond the cited permission/protected-action evidence.

## Evidence index

- Exact DCPMS APK/extraction: `artifacts/phase6it-missing-priv-apps-20260807-01/extraction-manifest.tsv`; APK SHA-256 `15ca17549bc377360d9213eb95b5e0468d1352839386e1d968bcb25282218997`.
- Exact JADX source root: `artifacts/phase6it-missing-priv-apps-20260807-01/jadx/sources/com/amazon/dcpms/fos/service/`.
- Exact manifest: `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/010_com.amazon.dcpms.fos.service.xmltree.txt`; SHA-256 `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`.
- Phase6SV baseline: `work/luna_worker_phase6sv_exported_surface_20260810.md` and `.csv`.
- VDEX method evidence: `artifacts/phase6bk/ipc-ota-closure-20260810-01/method-map.csv`; launcher component mutation rows 15 and 199. VDEX disassembly roots: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` and `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log`.
- Permission/protected-action evidence: `artifacts/phase6ac/protected-broadcast-source-audit-20260805-02/protected-broadcasts.csv`, `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/protected-broadcast-inventory.csv`, and saved read-only package evidence referenced by Phase6SV.

