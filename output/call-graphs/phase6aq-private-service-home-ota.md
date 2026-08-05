# Phase 6AQ／6AR plain-text call graph

```text
Home key
  -> TabletKeyPolicyManager / KeyInterceptorCallback
  -> KeyPolicyManagerCommon.launchHomeFromHotKey()
  -> Intent(ACTION_MAIN)
       + CATEGORY_HOME
       + flags 0x10200000
  -> Context.startActivityAsUser(..., UserHandle.CURRENT)
  -> standard Android HOME resolver
  -> com.amazon.firelauncher/.Launcher (live baseline, priority 50)

HomeEventHandler.handleCustomHome()
  -> foreground ComponentName
  -> getCustomHomeReceiver(package)
  -> AmazonPackageManager.checkPermission(RECEIVE_CUSTOM_HOME, package)
  -> explicit com.amazon.tablet.action.CUSTOM_HOME
  -> sendBroadcastAsUser(..., RECEIVE_CUSTOM_HOME)
  -> foreground app receiver only

LauncherHijackPreventerActivityStackCallback.canSeeHomeTask()
  -> ApplicationInfo.seInfo
  -> SELinux.getAppContext()
  -> SELinux.checkSELinuxAccess(amazon_policies, see_home_task)
  -> PackageManager.checkSignatures(packageName, android)
  -> Home task visibility allow/deny

fosinit
  -> AmazonActivityManagerService / DevicePolicyManagerService /
     PackageManagerService / WindowManagerService callbacks
  -> private Binder service publication
  -> shell UID 2000 service check
  -> SELinux service_manager find deny
  -> no shell Binder handle for private services

fosdebug
  -> standard dumpsys fosdebug
  -> vendor service inventory
  -> read-only diagnostics only in the observed scope

Official OTA staging
  -> metadata/package/device checks
  -> RecoverySystemWrapper.verifyPackage (verification path)
  -> staging move
  -> UpdateSystem.install boundary
  -> natural post-system-OTA lifecycle
  -> BootAfterSystemOTAReceiver
  -> OOBE/setup-state branch
  -> not an ordinary shell HOME selector
```
