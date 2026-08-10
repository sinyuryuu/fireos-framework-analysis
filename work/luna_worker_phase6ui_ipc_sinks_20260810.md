# Fire OS 7.3.3.1 Framework/system-service IPC sink audit

Date: 2026-08-10. Scope: preserved host artifacts only; Amazon Framework/system-service IPC beyond Launcher. No adb Binder/service transactions, driver invocation, payload construction, exploit development/testing, or device mutation was performed.

## Result

The evidence supports a bounded inventory of Binder contracts, Stub/Proxy transaction mappings, implementation methods, authorization markers, identity handling, and privileged sinks. The strongest state-affecting paths are:

- `IAmazonUserManager` tx3 reaches a KFT child-user helper that enables Tahoe and sets Fire Launcher and Launcher3 application state to `2` for the supplied `UserInfo.id`.
- `IDevicePolicyManager` tx100 reaches `DevicePolicyManagerService.addPersistentPreferredActivity()` only after active-admin/profile-owner validation, then clears identity and delegates to PMS. The PMS persistent-preferred sink requires calling UID 1000.
- PMS package/component state setters and ordinary preferred-activity replacement are concrete state sinks with explicit user/caller/permission gates in the preserved JADX.

Other reviewed Binder surfaces terminate in profile ordering, Amazon metadata/flags, input injection, lock/window state, storage migration, power/MTP/telemetry or queries. A marker such as `onTransact`, `getCallingUid`, or `clearCallingIdentity` alone was not treated as evidence of a low-privilege route.

## Evidence matrix

The companion CSV records 12 evidence rows and includes the requested evidence ID, package/class/method, source path plus line/offset, caller, gate, identity behavior, sink, confidence, and bounded limitations. It intentionally includes negative/nearby candidates where the sink or implementation is incomplete, so they are not mistaken for confirmed attack paths.

Notable service evidence:

| Surface | Preserved evidence | Conservative interpretation |
|---|---|---|
| `IAmazonUserManager` | tx1/tx3/tx5 mapping; `enableKftLauncherComponent` at disassembly `54297-54325`; `checkManageUsersPermission` around profile helpers | Child/profile lifecycle state control; tx3 is not evidence of ordinary User-0 reachability. |
| `IAmazonPackageManager` | 11-method contract mapping; implementation region `95866-96009` | Amazon per-user flags/metadata surface; no formal HOME writer identified. |
| `IAmazonActivityManager` | 14 methods mapped in `artifacts/phase6l/.../contract-methods.csv` | Activity/PIP/CPU/observer/query effects; no direct package/component/HOME writer in selected contract. |
| `IAmazonWindowManager` | 6 methods mapped; lock/overscan/PIP/pinning regions | Window/lock effects only; potentially disruptive methods were not called. |
| `AmazonInputManagerService` | `inject`/`injectSequence` at `19508-19714`; UID/permission markers | Input effects can influence event flow, but no direct state sink or reachable ordinary-app path was established. |
| `MigrationService` | tx1 permission gate and storage migration body; Fire availability refresh callback | Storage/lifecycle sink; fixed refresh broadcast is not a package-state or HOME writer. |

## Binder, gate, and identity observations

- The preserved contract audit maps Proxy transaction codes to Stub dispatch lines and implementation lines for Amazon activity, window, package, and user-manager contracts. Registration evidence exists for Amazon activity/window/package services; existing runtime captures record shell service-manager denial for private services. This audit did not repeat those checks and did not request handles.
- `getCallingUid()` appears in PMS, Amazon input/activity/package candidates, and user/profile code. `checkCallingPermission`, `checkCallingOrSelfPermission`, `enforceCallingPermission`, `checkComponentPermission`, `SecurityException`, and signature/privileged markers appear across the candidate inventory. Missing markers are bounded uncertainty, not a vulnerability finding.
- `clearCallingIdentity()` is explicit in DPM before PMS persistent-preferred delegation and is paired with restore. The clear follows admin validation and does not remove the PMS system-UID requirement documented in the inspected sink.

## Manifest/service evidence

The preserved service inventory covers published names, `onStart`/registration evidence, implementation classes, Binder class counts, and authorization-marker summaries. Manifest evidence was not treated as proof of Binder reachability: exported status, service-manager visibility, SELinux service-manager policy, caller UID, and method-local gates remain separate conditions. No new manifest component was inferred to relay into the listed state sinks.

## Hashes of examined inputs

SHA-256 values below preserve the exact inputs examined for this report:

```text
ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c  decompiled/baksmali/vdexExtractor/fosservices/disassembly.log
83a43bca710a8a273d5d06c9eeadcdb239f09a74b3c9292b35bf1f465ec7b5f8  decompiled/jadx/systemui/sources/com/android/server/devicepolicy/DevicePolicyManagerService.java
f0efc633c75524540dd8a5703e5db528bb81ed80c9c49ad34e5cdf4d2078b074  decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java
062b74661247122a670d8f16c5d2547a7f192be02de3d6e66ff8dc76d41b3957  artifacts/phase6l/binder-contract-audit-20260805-02/contract-methods.csv
16ab023aa5aedb7123a07ffd4e934d8e7bab7ac2e82a8d1462a82a6391f8b531  artifacts/phase6q/binder-service-audit-20260805-03/binder-service-inventory.csv
d72839a9a936d8f338f5496f62f960b6e91b00501ffbb05069ef8088a6e050b7  artifacts/phase6q/binder-service-audit-20260805-03/binder-method-candidates.csv
5d212c94f047aee7abc85ef6dc99aa92ca61e3e3d9318bb69db3c10d9e0da411  artifacts/amazon-services/amazonactivitymanager_fosinit.xml
2a5b62e67f460a5bd12ab4d5872b315a03b123cab13e74a18835826ed0cf8dbe  artifacts/amazon-services/amazonwindowmanager_fosinit.xml
```

## Limitations

The corpus is disassembly/JADX and preserved captures, not source plus a live symbolically verified build. Some JADX methods are explicitly incomplete, some Amazon service rows have only bounded implementation excerpts, and manifest/exported evidence does not establish SELinux or runtime reachability by itself. The audit did not inspect every framework Binder method body exhaustively; it enumerated preserved service/contract evidence and prioritized sinks relevant to package/component state, user/profile policy, settings, OTA, and privileged effects. No dynamic transaction result is claimed.

## Conservative verdict

The preserved artifacts show privileged IPC sinks and a real child-user KFT launcher-state writer, but they do not establish an unauthorised Binder route from an ordinary app or shell to User-0 package/component state, preferred HOME, profile policy, settings, or OTA control. This is a static, artifact- and build-scoped boundary—not an exploit claim.
