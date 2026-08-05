# Phase 6AZ call graph (text form)

```text
ordinary shell package-state request
  -> PackageManagerService protected-package path
  -> VendorProtectedPackagesCallback.callShouldProtectPackage()
  -> ControlProtectedPackagesCallback.shouldProtectPackage()
  -> system/privileged check
  -> PackageManagerDenyList:DenyListKeyPackages contains(package)
  -> caller UID 2000 check
  -> protected=true
  -> rejection before enabled-state mutation

AmazonPackageManagerService.onBootPhase()
  -> DenyListArcusHelper.processJSON()
  -> Resources.getSystem().openRawResource(0x7e05000a)
  -> amazon.fireos:raw/package_manager_deny_list
  -> packages_deny_list contains com.amazon.firelauncher
  -> persisted PackageManagerDenyList
  -> callback consumer

AmazonUserManagerService.onBootPhase(500)
  -> upgrade + child-user eligibility
  -> enableKftLauncherComponent(UserInfo)
  -> enable FreeTimeLauncherActivity
  -> setApplicationEnabledSetting(com.amazon.firelauncher, 2, 0, userId)
  -> setApplicationEnabledSetting(com.android.launcher3, 2, 0, userId)
```

The KFT branch is a distinct privileged lifecycle path. It was not invoked in
the Phase 6AZ live capture.
