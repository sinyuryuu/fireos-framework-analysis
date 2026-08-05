AmazonUserManagerService
  -> private KFT/child-user lifecycle
  -> enableKftLauncher(UserInfo)
  -> isMMDevice / isTv / existsKftLauncher
  -> tryEnableKftLauncherComponent
  -> enable com.amazon.tahoe FreeTimeLauncherActivity
  -> setApplicationEnabledSetting(com.amazon.firelauncher, DISABLED, user)
  -> setApplicationEnabledSetting(com.android.launcher3, DISABLED, user)
  -> DPM setActiveAdmin / setProfileOwner after clearCallingIdentity

AmazonPackageManagerService
  -> onBootPhase(550)
  -> PackageManagerService.isUpgrade()
  -> sendBroadcast(amazon.intent.action.BOOT_AFTER_SYSTEM_OTA,
                   com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA)

Saved enforcing live evidence: ordinary shell uid=2000 cannot find the private
Amazon user/package-manager services. No Binder transaction or lifecycle trigger
was sent. These are high-impact internal paths, not ADB launcher selectors.
