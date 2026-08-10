# Phase 7E — Amazon package-state / HOME watchdog and settings-source closure

Date: 2026-08-10  
Baseline: `6aa818a0f` and Phase 6X4 ledger.  
Method: host-only, read-only review of preserved framework/system APK JADX/smali, fosinit/config artifacts, deny-list artifacts, and existing Phase 6 writer ledgers. No binder transaction, broadcast, service call, setting/package mutation, APK install, exploit, or root action was performed.

## Result

No new complete caller→sink was found for `com.amazon.firelauncher` User 0 enable, disable, hidden, suspended, preferred, or HOME writes. The only exact Fire literal outside the existing ledger is a package-scoped notification broadcast from `MigrationService.appsAvailable`; it reports external-app availability and does not call a PackageManager state setter or HOME resolver. The exact Fire disable writer in `AmazonUserManagerService` is the already-covered KFT child-user path and is duplicate evidence, not a User 0 watchdog.

The preserved deny-list path reads `persist.sys.denylist_arcusid`, imports a resource JSON list into device-protected `PackageManagerDenyList` preferences, and registers/synchronizes with Arcus. It has no property setter, no shell-controlled file input, and no demonstrated Fire/HOME target. `LauncherHijackPreventer` is a visibility/permission policy callback: its HOME-task gate is SELinux `amazon_policies:see_home_task` or Android-signature based, while shutdown handling revokes `READ_LOGS`; neither writes package state or preferred HOME.

## Classification

| ID | Classification | Finding |
|---|---|---|
| 7E-001 | static capability | `MigrationService.appsAvailable` sets intent package to Fire and broadcasts to every running user ID. This is a notification edge only; receiver-side state/HOME edge is missing. |
| 7E-002/003 | duplicate | KFT child/profile lifecycle enables Tahoe FreeTime and changes Fire application state using `UserInfo.id`; already present in Phase 6MH/6AY evidence. No User 0 or HOME resolver edge. |
| 7E-004/005 | static capability | LauncherHijackPreventer gates HOME-task visibility by SELinux/signature and revokes READ_LOGS for tracked package/user pairs on shutdown. No Fire state sink. |
| 7E-006/007 | bounded negative / static capability | PackageManagerDenyList is resource/property-read plus device-protected preference/Arcus synchronization. No shell-writable property setter or Fire target was found. |
| 7E-008 | duplicate | Standard shell PM setters and `setHomeActivity` remain caller/permission/protected-package-gated baseline surfaces; no new Fire-specific caller was found. |

## Exact evidence notes

1. `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:33627-33718` identifies private `MigrationService.appsAvailable(Z)`, constructs either `android.intent.action.EXTERNAL_APPLICATIONS_AVAILABLE` or `...UNAVAILABLE`, calls `Intent.setPackage("com.amazon.firelauncher")`, obtains `IActivityManager.getRunningUserIds()`, and calls `broadcastIntent` once per running user. The method does not call `setApplicationEnabledSetting`, `setComponentEnabledSetting`, `setPackageSuspended`, `setApplicationHidden`, `setHomeActivity`, or a preferred-activity writer.
2. `...disassembly.log:54297-54434` shows `AmazonUserManagerService$BinderService.enableKftLauncherComponent(UserInfo)` using `UserInfo.id`, enabling Tahoe's `FreeTimeLauncherActivity`, and setting Fire application state. The same two callsites are recorded in `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv:4-6`; this is duplicate Phase 6 evidence and is bounded to child/profile lifecycle.
3. `...disassembly.log:136888-136954` shows `LauncherHijackPreventerActivityStackCallback.canSeeHomeTask(int,Context)`: it resolves the calling UID's package and allows visibility when SELinux grants `amazon_policies` / `see_home_task` or the package signature matches `android`. This returns a boolean; it is not a package-state or HOME writer.
4. `...disassembly.log:136954-137013` shows `LauncherHijackPreventerPackageManagerCallback.onShutdown(Context)` iterating recorded package/user pairs and revoking `android.permission.READ_LOGS`; it has no Fire literal and no package-state setter.
5. `...disassembly.log:97240-97345` and `artifacts/phase6ap/consumer-snippet-20260805-01/fosservices-denylist-consumer.snippet.txt` show `DenyListArcusHelper` reading the device-protected `PackageManagerDenyList`, importing `packages_deny_list` from the resource JSON, committing a `DenyListKeyPackages` set, reading (not setting) `persist.sys.denylist_arcusid`, then registering/syncing Arcus. The resource identity is independently recorded in `artifacts/phase6ap/denylist-resource-closure-20260805-01/resource-table-targets.json`.

## Settings/property/receiver conclusion

Within the requested preserved artifacts, the shell-writable-looking surfaces are only the standard `PackageManagerShellCommand` setter commands already covered by Phase 6X4. No exact shell caller reaches a Fire User 0 state sink. The new Fire-targeted receiver edge is a system-service broadcast notification from `MigrationService`; its receiver permission/handler and any state mutation are not preserved, so it cannot be promoted to a complete caller→sink. No settings provider write, HOME preferred write, or Fire watchdog property setter was identified.

## Evidence hashes

- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` — `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv` — `39ce24194ecead7109894d6bae3cfcf631118c9181ec446dc70a6dd3354f231a`
- `artifacts/phase6ap/consumer-snippet-20260805-01/fosservices-denylist-consumer.snippet.txt` — `860e30444f8c23a5e990e1b0f5ed0ff0feb330436d9e2f222aa7ea49d2e0be78`
- `artifacts/phase6ap/denylist-resource-closure-20260805-01/res/raw/package_manager_deny_list.json` — `16086fecbfce0a20c0b37535e25d690635d398b30d582fa6d231736dc9bdf710`

## Missing edges / residual risk

The preserved inputs do not include Fire Launcher receiver implementation/manifest, a complete `MigrationService` caller chain, or a deny-list consumer edge that targets Fire. These are evidence gaps, not positive capabilities. Closing them would require new artifacts; no runtime probing is warranted under the Phase 7E constraints.
