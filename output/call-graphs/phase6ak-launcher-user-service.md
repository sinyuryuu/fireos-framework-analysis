# Phase 6AK launcher/user service graph (plain text)

The diagram is intentionally a static call/control graph.  Dashed edges are
boundaries evidenced by the saved live SELinux capture, not invoked Binder
transactions.

```text
AmazonUserManagerService.onStart
  -> publishBinderService("amazonusermanagerservice")
  -> service_context amazonusermanager_service
  -> shell uid=2000: service_manager find denied (saved AVC)

trusted AmazonUserManagerImpl
  -> IAmazonUserManager.Proxy.transact(code=3)
  -> IAmazonUserManager.Stub.onTransact
  -> BinderService.enableKftLauncher(UserInfo)
     -> isMMDevice branch / tryEnableKftLauncherComponent
     -> enableKftLauncherComponent
        -> enable com.amazon.tahoe/...FreeTimeLauncherActivity
        -> disable com.amazon.firelauncher and com.android.launcher3
     -> clearCallingIdentity
     -> DPM active-admin/profile-owner path

AmazonProfileService.BinderService.initiateLauncher
  -> enforceProfileInteractionPermissions
  -> return SUCCESS
  -> no bounded formal HOME write or Fire Launcher explicit start
```

Mermaid source:

```mermaid
flowchart TD
    U[AmazonUserManagerService.onStart] --> P[publishBinderService
amazonusermanagerservice]
    P --> ACL[SELinux service_manager label
amazonusermanager_service]
    S[adb shell / uid 2000] -. find denied in saved AVC .-> ACL
    C[AmazonUserManagerImpl / trusted framework client] --> X[IAmazonUserManager proxy
transaction code 3]
    X --> T[IAmazonUserManager.Stub.onTransact]
    T --> E[BinderService.enableKftLauncher(UserInfo)]
    E --> F{isMMDevice?}
    F -- yes --> R[return true
no launcher mutation in this branch]
    F -- no --> K[tryEnableKftLauncherComponent]
    K --> Q[existsKftLauncher / isTv checks]
    Q --> M[enableKftLauncherComponent]
    M --> A[enable com.amazon.tahoe FreeTimeLauncherActivity]
    M --> D[disable com.amazon.firelauncher
and com.android.launcher3]
    E --> I[clearCallingIdentity]
    I --> DP[setActiveAdmin / setProfileOwner
KFT user]
    PS[AmazonProfileService.initiateLauncher] --> PG[enforce PROFILE_INTERACTION]
    PG --> PSR[return SUCCESS
no formal HOME write in bounded block]
```
