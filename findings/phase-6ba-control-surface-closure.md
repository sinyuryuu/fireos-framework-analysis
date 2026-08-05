# Phase 6BA — PS7331 IPC／OTA／ADB fallback control-surface closure

Generated 2026-08-05. This is a synthesis of the bounded PS7331 static audits,
the matched 7.3.3.1 source/image artifacts, and the already completed
read-only or reversible runtime measurements. It does not introduce a new
private Binder call or a new Fire Launcher mutation.

## Result at a glance

| Surface | Result | Status |
|---|---|---|
| PackageManager protected gate | Fire Launcher is in the matched PS7331 deny-list resource; Amazon callback rejects the shell enabled-state path before mutation | **Confirmed** |
| KFT user-management path | Static method explicitly disables Fire Launcher and Launcher3 for an eligible child user, after enabling FreeTime launcher | **Confirmed static; device invocation rejected** |
| HOME pre-resolution callbacks | ActivityStackSupervisor hook exists; inspected AppCompat callback delegates to PackageManager and Eve/base return null; no direct Fire component construction | **Strong evidence; bounded scope** |
| Amazon input/key services | Key interception/filter paths have permission, UID/package, whitelist, foreground, or signature/Amazon gates; shell service lookup is denied | **Confirmed / Strong evidence** |
| Amazon ActivityManager | No bounded formal HOME setter; `preWarmApplicationForUser` has an unconsumed permission-result candidate but only prewarms a target app | **Strong evidence candidate; not an exploit finding** |
| OOBE/OTA lifecycle | Protected post-OTA receiver can enable priority-100 OOBE Home and change setup state; updater has high-impact partition-write capability | **Confirmed static; unsafe to replay** |
| ADB fallback | Host monitor observed Fire Launcher first, then explicitly started a research Activity in 30/30 iterations | **Confirmed temporary workaround** |

## 1. Amazon IPC review

### 1.1 Shell boundary

The saved enforcing-policy capture reports `service_manager find` denial for
the selected private services, including `amazonactivitymanager`,
`amazon_input`, `amazon_keyevent`, `amazonprofileservice`,
`amazonusermanagerservice`, and `amazonwindowmanager`. A name in `service list`
or `dumpsys fosdebug` inventory is not a shell Binder handle.

The reviewed methods add a second boundary in the cases relevant to HOME:

```text
shell UID 2000
  -> service_manager find
  -> SELinux enforcing denial
  -> no private Binder handle

trusted Amazon caller
  -> private Binder method
  -> signature/Amazon permission, UID/package, foreground, or profile gate
  -> bounded input/profile/prewarm/lifecycle effect
```

`AmazonInputManagerService.registerKeyEventInterceptor()` checks
`GET_KEYEVENTS`, maps calling UID to package, checks a package whitelist and,
when required, the foreground package. `setInputFilter()` is closed by the
located `validateInputFilterAccessPermission()` path: system/updated-system
app or `FILTER_INPUT_EVENTS` (`signature|amazon`). These are input-control
surfaces, not formal HOME setters.

`AmazonActivityManagerService` has no bounded `set-home-activity`,
`replacePreferredActivity`, or explicit Fire component writer. Its
`isOnHomeStack()` method queries state, and `onActivityResume()` records and
notifies the supplied component. The only remaining static authorization
candidate is `preWarmApplicationForUser()`:

```text
checkCallingPermission(APP_PREWARM)
  -> clearCallingIdentity()
  -> getApplicationInfo(target, ..., user)
  -> PreWarmCacheHelper
  -> startProcessLocked(..., "prewarm", ...)
```

The saved instruction stream shows no result move/denial branch between the
permission call and identity clear. This is a legitimate code-review finding,
but not a demonstrated vulnerability: the service is not shell-findable, the
known caller is privileged Alexa, its target candidates are filtered by Amazon
permissions, and the effect is starting the target application under its own
application identity—not obtaining system or root identity. No transaction was
sent.

`AmazonUserManagerService.enableKftLauncherComponent()` is intentionally
separate. Its static effect is real, but it is reached through child-user/
upgrade/profile-owner lifecycle logic and would disable Fire Launcher. It was
not invoked.

## 2. HOME resolver and callbacks

The bounded Android 9 Home-key path builds an implicit `MAIN + CATEGORY_HOME`
intent and calls `startActivityAsUser`. `ActivityStackSupervisor.resolveIntent`
has a vendor callback pre-hook, but the inspected registrations are:

* `AppCompatActivityStackSupervisorCallback`, which calls PackageManager and
  filters an uninstalled result; and
* `EveActivityStackSupervisorCallback`, which does not override `resolveIntent`
  in the preserved class block.

No inspected callback constructs `com.amazon.firelauncher/.Launcher` or writes
a preferred activity. The current best explanation remains the privileged Fire
Launcher candidate/effective priority 50 plus the normal PackageManager
resolution path; the deny-list is a separate mutation-protection mechanism.

`LauncherHijackPreventer` is also not the selector in the inspected scope. Its
ActivityStack callback controls Home-task visibility using SELinux/signature
checks; its PackageManager/PermissionManager callbacks track `READ_LOGS` and
package bookkeeping. No direct HOME component injection was found.

## 3. OTA/OOBE boundary

The post-system-OTA sender is gated by system-server boot phase 550 and
`PackageManagerService.isUpgrade()`. `BootAfterSystemOTAReceiver` then checks
OOBE predicates and can enable `OobeHomeActivity` (priority 100,
`MAIN + SETUP_WIZARD + HOME + DEFAULT`) and change setup state. This is a
provisioning lifecycle, not a general third-party HOME setter.

The matched official 7.3.3.1 updater has static write intent for system/vendor
block images and boot/firmware-related files. `update-binary` contains
verification and block-image I/O boundaries. These artifacts are valuable for
provenance, but executing them, replaying the protected OTA action, or testing
crafted/symlink payloads would cross the recovery/partition safety boundary.

The official GPL package was also checked: it contains kernel/platform source
but not Amazon `system/core/init`, complete framework source, or the deny-list
resource. The binary/resource artifacts therefore remain the authoritative
source for the Amazon-specific logic.

## 4. Best available ADB result

Phase 6AT measured a host-side monitor for 30 iterations:

```text
KEYCODE_HOME
  -> Fire Launcher becomes resumed
  -> monitor observes the event over ADB
  -> am start -W -n research-component
  -> research component is foreground
```

Observed: Fire event 30/30, explicit redirect 30/30, target in final
foreground dump 30/30. HOME resolver remained Fire Launcher before and after.
The route requires a live ADB connection and can visibly hand off after Fire
Launcher; it is therefore classified as a **temporary foreground redirect**,
not a persistent HOME replacement or privilege transition.

No formal HOME replacement was found that is simultaneously shell-configurable,
reboot-persistent, reversible, and independent of Fire Launcher package state.

## 5. Explicit dispositions

### 已證實

* Fire Launcher is explicitly present in the matched PS7331 PackageManager
  deny-list resource and is consumed by the Amazon protected-package callback.
* KFT static code includes the Fire Launcher disabled-state call, but the device
  was not touched through that path.
* Selected Amazon private services are blocked from shell service lookup under
  enforcing SELinux.
* The ADB foreground monitor achieved 30/30 measured handoffs without
  modifying Fire Launcher or settings.

### 高可信推論

* The ordinary HOME result is controlled by the privileged Fire candidate and
  standard resolver ranking, while package protection, input callbacks, task
  visibility, and OOBE are separate boundaries.
* The `preWarmApplicationForUser` check-result omission is a real static review
  candidate but not a root/HOME route under the captured caller and SELinux
  conditions.

### 待驗證

* Complete native/recovery canonicalization details for OTA staging.
* Runtime values returned by private callbacks during a naturally occurring
  official OTA.
* Whether any out-of-scope native Amazon component has a different caller
  contract. No current evidence points to a safe shell route.

### 已排除

* Ordinary `set-home-activity`, priority manipulation, shortcut cache clearing,
  and the tested Accessibility/PendingIntent route as formal HOME replacement.
* `fosdebug` as a discovered mutating/root service.
* Inspected Amazon input, ActivityManager, profile, and hijack-preventer paths
  as direct shell HOME setters.

### 因風險拒絕測試

KFT Binder invocation, unknown Binder transactions, OOBE/OTA broadcast replay,
OOBE activation, updater/recovery execution, crafted OTA, symlink payloads,
Fire Launcher disable/hide/suspend/uninstall/clear/force-stop, Root, SELinux
changes, remounts, and partition writes.

## Reproduction sources

The phase-specific scripts and manifests are listed in the public repository:

* `tools/scripts/audit_phase6aj_input_home_boundary.py`
* `tools/scripts/audit_phase6ak_launcher_user_service.py`
* `tools/scripts/audit_phase6al_home_resolve_callbacks.py`
* `tools/scripts/audit_phase6am_hijack_preventer.py`
* `tools/scripts/audit_phase6av_ipc_method_closure.py`
* `tools/scripts/audit_phase6ab_ota_input_validation.py`
* `tools/scripts/audit_phase6aw_ota_write_contract.py`
* `tools/scripts/run_adb_home_monitor.py`

All are host-only or require an explicit serial and provide dry-run modes;
the ADB monitor refuses a Fire Launcher target.
