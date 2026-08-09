# Phase 6MT — Amazon IPC candidate closure

Date: 2026-08-10
Schema: `phase6mt-amazon-ipc-candidates-v1`

## Scope and safety

This is host-only analysis of preserved PS7331 disassembly and existing
reports. No device connection, ADB command, Binder/service call, private
transaction, ioctl, input injection, settings/package mutation, reboot,
OTA/recovery operation, exploit, Root attempt, or partition write was done.

The interface/publication mapping proves only a static system-service surface;
it does not prove that shell or an ordinary APK can obtain a handle.

## Executive result

**已證實（static）：** five proxy interfaces map to their corresponding
Amazon `BinderService` methods and published service names. The machine-readable
matrix records each transaction code, method range, permission marker, caller
identity marker, and bounded sink.

**高可信推論（bounded）：** the candidate slices contain no direct
`setHomeActivity`, `replacePreferredActivity`, `CATEGORY_HOME`,
`ACTION_MAIN`, or `com.amazon.firelauncher` writer. `IAmazonActivityManager`
does contain HOME-adjacent observation/callback methods such as
`isOnHomeStack`, `onActivityResume`, and `registerActivitySwitchObserver`;
these update/observe activity state but do not select a HOME component in the
bounded methods.

**已證實（static）：** explicit Amazon permission markers are present on many
mutating or callback methods, including accessibility magnification,
activity/PiP/prewarm/observer paths, DPM helper paths, and package metadata
writers. The exact caller reachability and effective UID remain separate.

**待驗證：** methods with no local permission marker (notably selected window,
activity callback, and package proxy methods) require service-handle, SELinux,
caller, and surrounding-class analysis before any authorization conclusion.
Missing local markers are not treated as a bypass.

**因風險拒絕測試：** no `service call`, guessed transaction, private API
replay, input or package-state mutation was attempted. Such actions are not
needed to answer the bounded static question and could alter system control.

## Notable bounded authorization anomaly

`preWarmApplicationForUser` invokes `Context.checkCallingPermission` for
`com.amazon.permission.APP_PREWARM` at
`fosservices/disassembly.log:40473`. The immediately following instruction is
`Binder.clearCallingIdentity` at `:40474`; no adjacent `move-result*` consumes
the permission result in the preserved method block. This is **Strong evidence
(bounded; not exploit proof)** of a local authorization-check anomaly. The
method still requires a reachable service handle, accepts package/user inputs,
and delegates into process-start logic; no HOME or Fire Launcher writer is
present. No transaction replay is justified or performed.

## Candidate summary

| Candidate | Interface | Service | Remote methods | Unmatched |
|---|---|---|---:|---|
| `accessibility` | `IAmazonAccessibilityManager` | `amazonaccessibilitymanager` | 3 | none |
| `activity` | `IAmazonActivityManager` | `amazonactivitymanager` | 14 | none |
| `device-policy` | `IAmazonDevicePolicyManager` | `amazondevicepolicymanager` | 3 | none |
| `window` | `IAmazonWindowManager` | `amazonwindowmanager` | 6 | none |
| `package` | `IAmazonPackageManager` | `amazonpackagemanager` | 11 | none |

## Method matrix

| Candidate | Method | Tx | Permission/gate | Identity | HOME/package-state markers | Classification |
|---|---|---:|---|---|---|---|
| `accessibility` | `magnificationCanvasAddLine` | 1 | com.amazon.logan.permission.DRAW_MAGNIFICATION_RECT [external/helper call not in bounded method] | no caller-identity marker observed | none observed / none observed | explicit permission/helper marker; no HOME/package-state writer |
| `accessibility` | `magnificationCanvasAddRect` | 2 | com.amazon.logan.permission.DRAW_MAGNIFICATION_RECT [external/helper call not in bounded method] | no caller-identity marker observed | none observed / none observed | explicit permission/helper marker; no HOME/package-state writer |
| `accessibility` | `magnificationCanvasClear` | 3 | com.amazon.logan.permission.DRAW_MAGNIFICATION_RECT [external/helper call not in bounded method] | no caller-identity marker observed | none observed / none observed | explicit permission/helper marker; no HOME/package-state writer |
| `activity` | `checkKillAppGoingIntoBg` | 3 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `activity` | `disablePipWindows` | 13 | com.amazon.permission.CONTROL_PIP_WINDOW; Requires com.amazon.permission.CONTROL_PIP_WINDOW permission [enforceCallingOrSelfPermission] | Binder.clearCallingIdentity; Binder.restoreCallingIdentity | none observed / none observed | explicit permission/helper marker; no HOME/package-state writer |
| `activity` | `dismissMultiWindow` | 11 | com.amazon.permission.DISMISS_MULTIWINDOW [enforceCallingPermission] | no caller-identity marker observed | none observed / none observed | explicit permission/helper marker; no HOME/package-state writer |
| `activity` | `dismissPipWindow` | 12 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `activity` | `enablePipWindows` | 14 | com.amazon.permission.CONTROL_PIP_WINDOW; Requires com.amazon.permission.CONTROL_PIP_WINDOW permission [enforceCallingOrSelfPermission] | Binder.clearCallingIdentity; Binder.restoreCallingIdentity | none observed / none observed | explicit permission/helper marker; no HOME/package-state writer |
| `activity` | `getCpuLoad` | 8 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `activity` | `getRecentCrashes` | 4 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `activity` | `isOnHomeStack` | 9 | none observed in bounded BinderService method | Binder.clearCallingIdentity; Binder.restoreCallingIdentity | isOnHomeStack / none observed | HOME-adjacent observer/callback surface; no HOME selector |
| `activity` | `onActivityResume` | 7 | none observed in bounded BinderService method | no caller-identity marker observed | onActivityResume / none observed | HOME-adjacent observer/callback surface; no HOME selector |
| `activity` | `packageLifetimeHint` | 2 | com.amazon.permission.SMARTOOM_HINTING; No permission to call packageLifetimeHint [checkCallingOrSelfPermission] | Binder.clearCallingIdentity; Binder.restoreCallingIdentity | none observed / none observed | explicit permission/helper marker; no HOME/package-state writer |
| `activity` | `preWarmApplicationForUser` | 1 | com.amazon.permission.APP_PREWARM [checkCallingPermission; return-value consumption not seen in adjacent instructions] | Binder.clearCallingIdentity; Binder.restoreCallingIdentity | none observed / none observed | permission check result not consumed in bounded instructions; potential authorization anomaly, no HOME/package-state writer |
| `activity` | `registerActivitySwitchObserver` | 5 | com.amazon.permission.ACTIVITY_SWITCH_WATCHER [enforceCallingPermission] | no caller-identity marker observed | onActivityResume; registerActivitySwitchObserver / none observed | HOME-adjacent observer/callback surface; no HOME selector |
| `activity` | `requestCpuBoost` | 10 | com.amazon.permission.USE_PERFBOOST; Requires com.amazon.permission.USE_PERFBOOST permission [checkCallingOrSelfPermission] | no caller-identity marker observed | none observed / none observed | explicit permission/helper marker; no HOME/package-state writer |
| `activity` | `unregisterActivitySwitchObserver` | 6 | com.amazon.permission.ACTIVITY_SWITCH_WATCHER [enforceCallingPermission] | no caller-identity marker observed | registerActivitySwitchObserver; unregisterActivitySwitchObserver / none observed | HOME-adjacent observer/callback surface; no HOME selector |
| `device-policy` | `clearRestrictionForUser` | 2 | permission/helper call present; literal unresolved [setUserRestrictionForUser helper] | no caller-identity marker observed | none observed / none observed | explicit permission/helper marker; no HOME/package-state writer |
| `device-policy` | `getBackedUpPoliciesFile` | 3 | android.permission.MANAGE_USERS; Need to have MANAGE_USERS permission in Manifest [checkPermission] | no caller-identity marker observed | none observed / none observed | explicit permission/helper marker; no HOME/package-state writer |
| `device-policy` | `setRestrictionForUser` | 1 | permission/helper call present; literal unresolved [setUserRestrictionForUser helper] | no caller-identity marker observed | none observed / none observed | explicit permission/helper marker; no HOME/package-state writer |
| `window` | `getLidState` | 3 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `window` | `isPipActive` | 4 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `window` | `lockNow` | 1 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `window` | `setOverscan` | 2 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `window` | `setPipVisibility` | 5 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `window` | `stopAppPinningMode` | 6 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `package` | `deregisterProxyReceiver` | 7 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `package` | `getAmazonFlagsForUser` | 3 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `package` | `getConfigurationHelper` | 11 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `package` | `isFtvSpecApp` | 9 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `package` | `isPreInstalledAppWithFtvSpec` | 10 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `package` | `registerProxyReceiver` | 6 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |
| `package` | `removeAmazonFlagsForUser` | 2 | amazon.permission.ADD_RM_PKG_METADATA; Permission denied to remove amazon flags. [checkCallingOrSelfPermission] | no caller-identity marker observed | none observed / removeAmazonFlagsForUser | Amazon package metadata/state surface; not shown as enabled-state or HOME writer |
| `package` | `removeAmazonMetadataForUser` | 5 | amazon.permission.ADD_RM_PKG_METADATA; Permission denied. [checkCallingOrSelfPermission] | no caller-identity marker observed | none observed / removeAmazonMetadataForUser | Amazon package metadata/state surface; not shown as enabled-state or HOME writer |
| `package` | `setAmazonFlagsForUser` | 1 | amazon.permission.ADD_RM_PKG_METADATA; Permission denied to set amazon flags. [checkCallingOrSelfPermission] | no caller-identity marker observed | none observed / setAmazonFlagsForUser | Amazon package metadata/state surface; not shown as enabled-state or HOME writer |
| `package` | `setAmazonMetadataForUser` | 4 | amazon.permission.ADD_RM_PKG_METADATA; Permission denied. [checkCallingOrSelfPermission] | no caller-identity marker observed | none observed / setAmazonMetadataForUser | Amazon package metadata/state surface; not shown as enabled-state or HOME writer |
| `package` | `shouldAllowMicAccess` | 8 | none observed in bounded BinderService method | no caller-identity marker observed | none observed / none observed | no permission marker in bounded method; caller reachability unresolved |

## Decision boundary for HOME research

```text
Stub.Proxy → published service → BinderService method
  → local permission/identity checks (where observed)
  → callback/state/native/package-metadata sink
  → [no direct HOME component writer in these bounded slices]
```

The results narrow, but do not eliminate, other surfaces outside these class
ranges: caller-side proxy invocations, native code, framework LocalServices,
system-server call sites, policy/SELinux, and Amazon services not represented
by the five selected interfaces.

## Inputs

```json
{
  "decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log": "fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71",
  "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log": "ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c",
  "findings/phase-6bk-evidence-index.md": "60374990674ef5bb8aefdc7123248ca2ab2118ea84497358d7002017f00ebb40",
  "findings/phase-6kv-pms-home-caller-closure.md": "a3c3d90315895c8295c8cee73f889f020b96f31cded80fa9e1672dc9ae598ef1",
  "findings/phase-6mn-ipc-user-scope-closure.md": "2adc3dd733dbc310da2706a14e9e7f12759198c09f37a63970f35c97855f383e",
  "findings/phase-6mq-profile-launcher-helper-closure.md": "a8b51750e7d626a971e32937c09c5c459930df88f072d73dfe15d55aa0b07a7a",
  "findings/phase-6mr-amazon-input-manager-static-closure.md": "f8bbb1775d56a40d0e4056b27acfb7a14b26a4aeda4f235934922f03e30cf5d2",
  "work/luna_worker_phase6mp_inventory_20260810.md": "16eb678a5d79fb5dd8344ea41a95028e1c9dda4717e92b3c68a01396ac44757e",
  "work/luna_worker_phase6ms_inventory_20260810.md": "7c088485220290659cbbd5e5c195b5849ebaa89a04e0c5e5c1a1f9ed301d8368"
}
```

## Reproduction

```sh
python3 tools/scripts/audit_phase6mt_amazon_ipc_candidates.py --dry-run
python3 tools/scripts/audit_phase6mt_amazon_ipc_candidates.py
```

Generated artifact: `artifacts/phase6mt-amazon-ipc-candidates-20260810-01`.
