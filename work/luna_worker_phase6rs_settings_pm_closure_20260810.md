# Phase 6RS — SettingsProvider / PMS / Amazon PM writer closure

Date: 2026-08-10. Host-only static review. Inputs were limited to the decompiled JADX/baksmali trees, saved artifacts, AOSP reference notes, and existing findings. No adb, Binder/service call, broadcast, Settings/package mutation, APK/OTA/recovery, root, or exploit action was performed.

## Closure result

The writer topology is closed at the evidence level requested:

`caller/API → permission or gate → Binder identity handling → explicit user propagation → first sink`.

SettingsProvider has separate global, secure, and system mutation paths. The API entrypoints propagate `UserHandle.getCallingUserId()` or a requested user into `resolveCallingUserIdEnforcingPermissionsLocked`; cross-user handling is delegated to `ActivityManager.handleIncomingUser`. Global and secure writes require `WRITE_SECURE_SETTINGS`; system writes require the secure-settings or write-settings operation gate. The bounded mutation slices do not show a `clearCallingIdentity()` before the permission/user checks, so no identity-clearing bypass is inferred. Their first sink is the SettingsRegistry/SettingsState persistence path, not HOME or PMS package state.

PMS HOME writers are distinct from SettingsProvider keys. `setHomeActivity()` validates the target against the selected user's HOME candidates and calls `replacePreferredActivity()`. The latter enforces cross-user permission and `SET_PREFERRED_APPLICATIONS`, then writes the per-user preferred resolver. `com.android.server.pm.Settings` persists preferred state in the preferred-activity XML sections. This is a preferred-activity sink; resolver ranking can still select Fire, so persistence is not equivalent to effective HOME selection.

The Amazon PM metadata surface has four mutators: `set/removeAmazonFlagsForUser` and `set/removeAmazonMetadataForUser`. Each checks `amazon.permission.ADD_RM_PKG_METADATA`, accepts an explicit user argument, and calls `AmazonApplicationFlags`. No `clearCallingIdentity()` is shown in the bounded mutator slices. The exact-build production caller and legitimate permission holder provenance remain UNKNOWN. Existing evidence confirms an Amazon flags/metadata sink, but does not establish a bridge to PMS enabled state, preferred HOME, Fire Launcher state, or a User-0 package-state writer.

## Important disposition

`UNKNOWN`, `NOT_FOUND`, and `production caller not found` are retained where the corpus does not close the edge. They are evidence gaps, not vulnerability findings. The detailed row-level closure is in [luna_worker_phase6rs_settings_pm_closure_20260810.csv](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/work/luna_worker_phase6rs_settings_pm_closure_20260810.csv).

## Priority evidence anchors

- SettingsProvider entrypoints and user propagation: `decompiled/jadx/settings-provider/sources/com/android/providers/settings/SettingsProvider.java:238-264`, `:344-418`, `:658-704`, `:881-920`, `:965-1015`, `:1229-1302`.
- PMS HOME gate and sink: `decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/pm/PackageManagerService.java:13120-13143`, `:13817-13838`.
- Amazon PM mutator gate and facade calls: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:95866-96037`, especially `:95962-96025`; `artifacts/phase6mu-amazon-application-flags-20260810-01/evidence/package-mutators.txt`.
- Package-state writer inventory: `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv`.
- Existing HOME/settings comparison: `work/luna_worker_settings_home_resource_followup_20260810.md`.
- Existing Amazon PM boundary: `work/luna_worker_phase6ms_inventory_20260810.md`, `work/luna_worker_ipc_unclosed_sink_inventory_20260810.md`.
- AOSP baseline scope: `aosp/references/aosp-baseline.md`.

## Safe next step

Only if a new exact-build offline artifact is supplied: trace `AmazonApplicationFlags` consumers and any PMS bridge, and enumerate exact permission holders from manifests/permission tables. Do not dispatch private transactions or alter Settings/package state.
