# Phase 17 KFT to PMS identity flow

Ordinary APK / shell
  -> ServiceManager/Binder handle
  -> Amazon private service
  -> IAmazonUserManager tx3
  -> enableKftLauncher(UserInfo)
  -> tryEnableKftLauncherComponent
  -> AmazonPackageManagerImpl / IPackageManager
  -> PackageManagerService.setComponentEnabledSetting
  -> caller, cross-user, protected-package checks
  -> ordinary UID rejected before state mutation

Trusted child lifecycle
  -> child-flagged UserInfo + supplied user id
  -> Tahoe enabled; Fire/Launcher3 disabled for child scope
  -> clearCallingIdentity only for later DPM/profile-owner work

Driver / OTA capability
  -> shipped object + selected DTB/DTBO + merged policy + native caller
  -> missing low-privilege edge

Ordinary-app prewarm
  -> temporary process/resource effect
  -> no package, HOME, UID0, or persistent privilege effect
