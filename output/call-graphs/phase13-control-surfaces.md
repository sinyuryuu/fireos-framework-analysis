# Phase 13 call graph (plain text)

```text
Unknown external caller [UNCONFIRMED]
  -> amazonusermanagerservice tx3 [caller/UID/package UNCONFIRMED]
AmazonUserManagerImpl.createChildUser
  -> IAmazonUserManager.Proxy.enableKftLauncher(UserInfo)
  -> Parcel(UserInfo) + transact(3)
  -> IAmazonUserManager.Stub.onTransact(3)
  -> BinderService.enableKftLauncher(UserInfo)
  -> tryEnableKftLauncherComponent(UserInfo) [authz UNCONFIRMED]
  -> AmazonPackageManagerImpl
  -> standard package Binder / IPackageManager
  -> PMS setters
     -> Tahoe FreeTimeLauncher enabled for supplied user
     -> Fire Launcher disabled for supplied user
     -> Launcher3 disabled for supplied user
No formal HOME setter; User-0 external reachability UNCONFIRMED.
```
