# Phase 5 — Amazon protection and launcher-hijack chain

## Result boundary

The available Fire OS artifacts show two distinct Amazon mechanisms:

1. a PackageManager callback that protects deny-listed system packages from
   shell enabled-state mutation; and
2. Activity/task visibility and package/permission callbacks registered by
   `LauncherHijackPreventer`.

The inspected `LauncherHijackPreventerActivityStackCallback` does not itself
construct or start `com.amazon.firelauncher/.Launcher`. It is therefore not
evidence of a direct Fire launch in the normal User 0 HOME path.

## Registration evidence

The FOS init registrations are preserved in:

- `artifacts/amazon-services/amazonpackagemanager_fosinit.xml:22-24` — registers
  `VendorProtectedPackagesCallback` with
  `com.amazon.android.service.pm.ControlProtectedPackagesCallback`.
- `artifacts/amazon-services/launcherhijackpreventer_fosinit.xml:9-18` —
  registers the ActivityStack and ActivityManager callbacks.
- `artifacts/amazon-services/tabletlauncherhijackpreventer_fosinit.xml:9-16` —
  registers PackageManager and PermissionManager callbacks.

The XML files are configuration evidence, not a claim that every callback is
called for every HOME request.

## Protected enabled-state path

The runtime/static chain is:

```text
pm/cmd package (shell UID 2000)
  -> PackageManagerShellCommand.runSetEnabledSetting(I)
  -> IPackageManager.setComponentEnabledSetting()
  -> PackageManagerService.setComponentEnabledSetting()
  -> PackageManagerService.setEnabledSetting()
  -> ProtectedPackages.isPackageStateProtected()
  -> ProtectedPackages.isProtectedPackage()
  -> VendorProtectedPackagesCallback.callShouldProtectPackage()
  -> ControlProtectedPackagesCallback.shouldProtectPackage()
  -> SecurityException before package/component state mutation
```

Evidence locations:

- `decompiled/baksmali/vdexExtractor/services/disassembly.log:953377-953546`
  contains the state mutation gate and the exception path.
- `decompiled/baksmali/vdexExtractor/services/disassembly.log:505771-505837`
  contains the protected-package vendor callback path.
- `decompiled/baksmali/vdexExtractor/services/disassembly.log:539225-539250`
  contains callback aggregation.
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96950-97049`
  contains the Amazon implementation.

The Amazon callback's control flow is:

```text
getSharedPrefPackages(context)
  -> device-protected /data/system/PackageManagerDenyList
  -> SharedPreferences key DenyListKeyPackages

shouldProtectPackage(callingUid, packageName, context)
  -> isSystemApp(packageName, context)
  -> shouldDisableAmazonApp(packageName, context)
  -> callingUid == 2000
  -> true / false
```

`isSystemApp()` obtains `ApplicationInfo` and checks system/updated-system
flags. `shouldDisableAmazonApp()` checks membership in the deny-list set. The
shell-visible package dump proves Fire Launcher is system/privileged; the
deny-list file itself was not readable by shell, so the exact stored set
membership remains **高可信推論**, not a directly pulled file.

## LauncherHijackPreventer behavior

`LauncherHijackPreventerActivityStackCallback.canSeeHomeTask(int, Context)` is
at `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:136880-136953`.
Its observed decision sequence is:

1. resolve the UID to `ApplicationInfo`;
2. derive the app's SELinux context;
3. call `SELinux.checkSELinuxAccess(..., "amazon_policies", "see_home_task")`;
4. accept a successful policy result or an Android-signature fallback;
5. otherwise deny visibility.

The method returns a visibility decision. It does not contain a `ComponentName`
for Fire Launcher, a `startActivityAsUser` call, or an explicit Fire launch.
The prior dynamic SELinux denials for `see_home_task` are consistent with this
visibility path, while separate logs show the standard HOME start/resumption.

The PackageManager callback in the same component tracks package/user pairs;
the PermissionManager callback later revokes `android.permission.READ_LOGS` for
stored pairs on shutdown. Those callbacks are not evidence of HOME resolver
selection.

## Explicit Fire references outside the normal resolver

Two literal Fire references are present in the inspected FOS services:

1. `MigrationService.appsAvailable()` creates an external-applications
   broadcast and calls `Intent.setPackage("com.amazon.firelauncher")` around
   `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:33638-33652`.
   This is a package-scoped availability broadcast, not a HOME launch.
2. `AmazonUserManagerService$BinderService.enableKftLauncherComponent(UserInfo)`
   at `.../disassembly.log:54297-54324` enables the KFT FreeTime launcher and
   calls `AmazonPackageManager.setApplicationEnabledSetting` for
   `com.amazon.firelauncher` and `com.android.launcher3`. The caller is the
   KFT/child-user launcher-management path, not evidence of the normal User 0
   HOME resolver.

The second finding is important: a global statement that “Amazon never
hard-codes Fire Launcher anywhere” would be false. The narrower statement
that no Fire hard-code was found in the inspected core HOME chooser remains
supported by the current artifact set.

## Determination

- **已證實：** Amazon inserts a protected-package callback into the
  PackageManager path and its callback reads a device-protected deny-list,
  checks system-app status, and gates shell UID 2000.
- **已證實：** the tested package/component disable request is rejected before
  enabled state changes; this is separate from a watchdog re-enabling a package.
- **高可信推論：** Fire Launcher is in the effective deny-list set because the
  callback's conditions match the preserved Fire Launcher package and the
  prior runtime exception.
- **已證實（範圍限定）：** the inspected LauncherHijackPreventer activity-stack
  callback is a task-visibility policy, not a direct Fire launch method.
- **已證實（範圍限定）：** Amazon has a literal Fire package state mutation in
  a KFT/child-user path; it does not establish the User 0 HOME selection cause.
- **待驗證：** the exact runtime registration order and whether a concrete
  vendor resolve callback returns a HOME result for the main user.
- **因風險拒絕測試：** reading protected `/data/system` files through a
  bypass, changing the deny list, stopping Amazon services, or mutating Fire
  package state.
