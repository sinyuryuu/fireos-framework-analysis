AmazonActivityManagerImpl
  -> ServiceManager.getService(amazonactivitymanager)
  -> IAmazonActivityManager.Stub.Proxy
  -> preWarmApplicationForUser(...)
  -> Binder.transact(code=1)
  -> AmazonActivityManagerService.BinderService
  -> checkCallingPermission(APP_PREWARM)
  -> clearCallingIdentity
  -> getApplicationInfo / PreWarmCacheHelper
  -> startProcessLocked(..., "prewarm", ...)

Saved caller scope:
  Alexa ExplicitIntentAction.prewarmApplicationProcess
  -> preWarmApplicationForUser(targetPackage, 0, foregroundProfileId)

No ordinary sideloaded caller, Binder invocation, or device mutation was established.
