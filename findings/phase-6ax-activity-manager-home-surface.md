# Phase 6AX — Amazon Activity Manager HOME control surface

## Scope

This is a host-only, bounded-method audit of the preserved PS7331 `services` VDEX disassembly. It separates Amazon Activity Manager foreground observation, process-control, and performance methods from a formal HOME selector.

The parser and its output do not contact ADB, obtain a Binder handle, send a transaction, start or kill a process, inject input, change settings or package state, reboot, execute OTA code, or write a partition.

Reproduction:

```sh
python3 tools/scripts/audit_phase6ax_activity_manager_home_surface.py --dry-run
python3 tools/scripts/audit_phase6ax_activity_manager_home_surface.py \
  --output artifacts/phase6ax/activity-manager-home-surface-20260805-01
(cd artifacts/phase6ax/activity-manager-home-surface-20260805-01 && shasum -a 256 -c sha256sums.txt)
```

Input: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`, SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`.

## Executive result

### 已證實

1. The bounded `AmazonActivityManagerService.BinderService` class spans disassembly lines 39645–40680 and contains 19 parsed methods (17 virtual and two direct). The generated method inventory is in `artifacts/phase6ax/activity-manager-home-surface-20260805-01/activity-manager-binder-methods.csv`.

2. `isOnHomeStack()`, lines 40336–40373, calls `ActivityManager.getService().getFocusedStackInfo()` and reads `WindowConfiguration.getActivityType()`. It is a HOME-state query. Its bounded body does not write a preferred record, resolve a HOME candidate, start a HOME activity, or select a Fire Launcher component.

3. `onActivityResume(ComponentName)`, lines 40401–40416, stores the supplied component through synthetic `access$702` into `mComponentInForeground` and posts a message to `ActivitySwitchHandler`. The handler, lines 39617–39644, calls `notifyActivitySwitch(ComponentName)`, which broadcasts to registered `IAmazonActivitySwitchObserver` callbacks. This is foreground state/observer plumbing, not a HOME resolver.

4. The normal internal caller found for `onActivityResume` is `AmazonActivityManagerAMSCallback.updateUsageStatsOnResume(ComponentName,int)`, lines 180274–180288. It initializes the callback, checks whether `mService` exists, and forwards the resumed component. The bounded caller does not construct a HOME intent or select a component.

5. The service publishes the name `amazonactivitymanager` at the outer service method `getSystemServiceName()`, lines 40954–40959. Its `onStart()` method creates the Binder service and calls `publishBinderService`, lines 41073–41084. The exact registration declaration is also preserved in `artifacts/amazon-services/amazonactivitymanager_fosinit.xml`.

6. The saved enforcing-device observation shows that shell UID 2000 cannot obtain this service: `service check` reports `Service amazonactivitymanager: not found`, and the corresponding AVC records a denied `service_manager find` for `amazonactivitymanager` with `scontext=u:r:shell:s0`, `uid=2000`, and `permissive=0`. Therefore the public Java access flag on `onActivityResume` is not evidence of shell reachability.

7. Other bounded Binder methods have explicit gates or are non-selector utilities:

   - `registerActivitySwitchObserver` / `unregisterActivitySwitchObserver`: `com.amazon.permission.ACTIVITY_SWITCH_WATCHER`.
   - `packageLifetimeHint`: `com.amazon.permission.SMARTOOM_HINTING` with a denial result.
   - `disablePipWindows` / `enablePipWindows`: `com.amazon.permission.CONTROL_PIP_WINDOW`.
   - `dismissMultiWindow`: `com.amazon.permission.DISMISS_MULTIWINDOW`.
   - `dump`: `android.permission.DUMP`.
   - `requestCpuBoost`: `com.amazon.permission.USE_PERFBOOST`.

### 高可信推論

- Within the audited `AmazonActivityManagerService.BinderService` body, no shell-accessible formal HOME setter was found. The strongest state-writing method, `onActivityResume`, records the already-resumed component and notifies observers; it does not choose the component.
- A public Amazon Binder interface is therefore insufficient to establish a HOME replacement path. Both service-manager SELinux visibility and method-level permission/caller evidence are required.
- The `checkKillAppGoingIntoBg(String,int)` path, lines 39808–39940, is a high-impact process-control candidate because its bounded body can reach `TestHelper.killApp`. It was not invoked. The saved service-manager denial is the only live reachability evidence used here. This path is not a HOME selector and is excluded from further live testing.
- `preWarmApplicationForUser(String,int,int)`, lines 40453–40534, remains a static authorization-anomaly candidate because the local `APP_PREWARM` check result is not observed being consumed before identity clearing in the bounded block. It reaches process prewarm, not HOME selection. No transaction or process start was attempted.

### 待驗證

- The complete set of callers to every `IAmazonActivityManager` method across all loaded code has not been proven exhaustively by this bounded report.
- A trusted system-server caller could invoke the service, but this audit does not claim that every such caller is semantically harmless outside the methods reviewed.
- The report does not prove that no other Amazon service, SystemUI path, or framework callback can select HOME; it only closes the reviewed Activity Manager Binder surface and its direct callback edge.

### 因風險拒絕測試

- No unknown Binder transaction code was sent to `amazonactivitymanager`.
- No attempt was made to invoke process-kill, prewarm, PIP, observer-registration, or foreground-state methods.
- No service-manager policy, SELinux policy, package state, HOME state, or system setting was modified.

## Method-level evidence

| Finding | Location | Interpretation | Confidence |
|---|---|---|---|
| 19 bounded methods, no bounded HOME setter | disassembly lines 39645–40680; generated CSV | Activity Manager Binder surface classified without assuming that “public” means shell-reachable | Confirmed |
| HOME query only | `isOnHomeStack()`, lines 40336–40373 | Reads focused stack/activity type; no selector write | Confirmed |
| Foreground state write | `onActivityResume()`, lines 40401–40416 | Stores `mComponentInForeground`, then queues observer notification | Confirmed |
| Observer fan-out | `ActivitySwitchHandler`, lines 39617–39644; `notifyActivitySwitch()`, lines 40374–40400 | Sends the supplied component to registered observers | Confirmed |
| Internal callback edge | `AmazonActivityManagerAMSCallback.updateUsageStatsOnResume()`, lines 180274–180288 | System-server callback forwards the resumed component; no HOME construction in this block | Confirmed |
| HOME resolution bridge | `AppCompatActivityStackSupervisorCallback.resolveIntent()`, lines 41123 onward | Calls `IPackageManager.resolveIntent` and checks uninstalled state; this is not an Activity Manager Binder HOME setter | Strong evidence |
| Service visibility boundary | `artifacts/phase6aq/public-summary-20260805-01/service-check-results.txt`; `amazon-service-avc.txt` | Shell cannot find `amazonactivitymanager` under enforcing SELinux | Confirmed |
| Process-control candidate | `checkKillAppGoingIntoBg*()`, lines 39808–39940 | May kill a selected background app; not a HOME selector and intentionally not invoked | Strong evidence |
| Prewarm anomaly | `preWarmApplicationForUser()`, lines 40453–40534 | Static check-result-consumption anomaly candidate; no live reachability or escalation evidence | Strong evidence |

## Boundary conclusion

The new evidence narrows the Amazon framework hypothesis. `AmazonActivityManagerService` is a meaningful Amazon control/observation service, but the reviewed Binder surface does not explain why the standard HOME resolver returns `com.amazon.firelauncher/.Launcher`. Its direct HOME-adjacent method is observational (`isOnHomeStack`); its component-writing method is a foreground notification path (`onActivityResume`). The remaining formal selection evidence should therefore remain centered on PackageManager/ActivityTaskManager resolution and on the separate, protected Home-key/input boundary—not on an assumed Activity Manager Binder setter.

This is a static boundary result, not a root or exploit result.
