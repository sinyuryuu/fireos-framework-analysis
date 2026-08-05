# Phase 6AK — Amazon launcher/user Binder authorization closure

Generated: 2026-08-05T00:33:24.243748+00:00

## Scope and safety

This phase is a host-only analysis of preserved Fire OS PS7331 VDEX
disassembly and saved read-only service/SELinux captures.  It did not use ADB,
look up a private Binder handle, send a transaction, create a user, alter a
package, alter a profile, replay an OTA/OOBE broadcast, or change settings.

## Executive result

### 已證實

1. `AmazonUserManagerService` publishes
   `amazonusermanagerservice` from `onStart()`.  The saved service list shows
   the endpoint, while the saved SELinux AVC shows shell UID 2000 is denied
   `service_manager find` for the service.  Evidence: `6AK-UM-001`.
2. `IAmazonUserManager.Stub.onTransact()` dispatches transaction code `3` to
   `enableKftLauncher(UserInfo)` after interface enforcement and unmarshalling.
   The generated stub block contains no permission check.  Evidence:
   `6AK-UM-002`.
3. The server method contains an explicit KFT path.  Its helper enables
   `com.amazon.tahoe.launcher.FreeTimeLauncherActivity` and calls
   `setApplicationEnabledSetting` with state `2` for
   `com.amazon.firelauncher` and `com.android.launcher3`.  Evidence:
   `6AK-UM-003`, `6AK-UM-004`.
4. The KFT path is entered from child-user creation and from the system-server
   upgrade/child-user lifecycle path, not from ordinary HOME resolution.
   Evidence: `6AK-UM-005`, `6AK-UM-007`.
5. `AmazonProfileService.BinderService.initiateLauncher()` is protected by
   `com.amazon.device.permission.PROFILE_INTERACTION` and, in its bounded
   method body, only enforces the permission, logs, and returns success.  No
   formal HOME write or Fire Launcher explicit start appears there. Evidence:
   `6AK-PROF-002`.

### 高可信推論

- `enableKftLauncher` is a high-impact static method-auth review candidate,
  but it is not a shell-accessible workaround under the saved production
  policy.  The correct boundary is **method-local auth candidate plus
  service-manager/SELinux reachability denial**, not “unauthorized shell root”.
- The explicit Fire Launcher state mutation belongs to KFT/child-user
  provisioning.  It does not explain the ordinary user-0 resolver result by
  itself and does not demonstrate a standard default-HOME writer.

### 待驗證

- Whether every trusted caller of `enableKftLauncher` is independently
  constrained by a higher-level package/signature policy outside the generated
  stub.  No private transaction was sent to answer this.
- Whether the current tablet exposes the multimodal feature branch that makes
  `enableKftLauncher` return early.  This is not needed for the shell-boundary
  result and was not changed or probed through private APIs.

### 已排除 / 因風險拒絕測試

- No evidence supports using `enableKftLauncher` as an ordinary HOME
  replacement.
- No attempt was made to invoke transaction code 3, forge a `UserInfo`, create
  a child user, set a profile owner, or disable Fire Launcher.  Those tests are
  outside the approved safe boundary.

## Detailed control paths

### AmazonUserManagerService

```text
AmazonUserManagerService.onStart()
  -> publishBinderService("amazonusermanagerservice")
  -> shell uid=2000 service_manager find denied (saved AVC)

trusted framework client
  -> IAmazonUserManager.Proxy.transact(code=3)
  -> Stub.onTransact
  -> BinderService.enableKftLauncher(UserInfo)
  -> KFT checks / tryEnableKftLauncherComponent
  -> enableKftLauncherComponent
     -> enable FreeTime launcher component
     -> disable Fire Launcher and Launcher3 for supplied user
  -> DPM active-admin/profile-owner path after clearCallingIdentity
```

The separate `checkManageUsersPermission(String)` method explicitly permits
UID 1000 and UID 0, otherwise checks `android.permission.MANAGE_USERS` and
throws `SecurityException`.  It is used by selected user-list methods and is
not called in the bounded `enableKftLauncher` method.  That asymmetry is
recorded as a static review item, not as a device exploit finding.

### AmazonProfileService

```text
AmazonProfileService.BinderService.initiateLauncher()
  -> enforceProfileInteractionPermissions()
  -> Context.checkPermission(com.amazon.device.permission.PROFILE_INTERACTION)
  -> log "Initiate launcher"
  -> return AmazonProfileManager.SUCCESS
```

Other profile-service methods can explicitly start configured profile-picker
activities for the current user, but that is a profile UI path and not a
formal HOME resolver setter.

## Why this does not produce a new workaround

The method that contains the explicit Fire Launcher disable calls is behind a
private system-server service.  Existing live evidence shows shell cannot even
obtain the service handle under enforcing SELinux.  The allowed route would
also cross KFT child-user/DPM semantics and could alter protected package
state, so it is not an acceptable experiment on the production user.

This closes the highest-value static candidate without repeating the already
disproved component-disable or ordinary `set-home-activity` tests.

## Reproduction

```sh
python3 tools/scripts/audit_phase6ak_launcher_user_service.py --dry-run
python3 tools/scripts/audit_phase6ak_launcher_user_service.py \
  --output artifacts/phase6ak/launcher-user-service-20260805-02
```

The command reads only the four preserved inputs listed in the evidence index.
The generated artifact contains input hashes, method snippets, a CSV, a
control-flow graph, and a SHA-256 manifest.

## Next minimal research target

If more launcher research is justified, the next safe target is a host-only
comparison of the KFT path against the current user-0 HOME resolver and the
saved `BootAfterSystemOTAReceiver`/OOBE lifecycle evidence.  Do not invoke the
private Binder method; first identify all trusted callers and their package /
signature constraints from static artifacts.
