# Phase 6BB prewarm call graph

```text
Alexa ExplicitIntentAction.prewarmApplicationProcess(target)
  → AmazonActivityManagerImpl.preWarmApplicationForUser(target, 0, foregroundProfileId)
  → IAmazonActivityManager.Stub.Proxy
  → Binder transaction 1
  → AmazonActivityManagerService.BinderService.preWarmApplicationForUser
  → Context.checkCallingPermission(APP_PREWARM)
  → Binder.clearCallingIdentity()
  → IPackageManager.getApplicationInfo(target, 1024, user)
  → PreWarmCacheHelper.getKeepIfLargeValue(target)
  → ActivityManagerService.startProcessLocked(..., "prewarm", ...)
```

Boundary notes:

- `amazonactivitymanager` is registered by `fosinit`; the saved live shell capture records
  SELinux service-manager `find` denial.
- The graph is static. No Binder transaction or process start was performed.
- No HOME intent, preferred-activity write, or Fire Launcher component appears in this path.
