# Phase 6AX Activity Manager HOME boundary (plain text)

AmazonActivityManagerService.onStart
  -> publish amazonactivitymanager
  -> saved enforcing AVC: shell uid=2000 cannot find service
  -> trusted/internal callers only in observed deployment

BinderService methods
  -> isOnHomeStack(): reads focused stack activity type; no resolver write
  -> onActivityResume(ComponentName): writes mComponentInForeground, queues observer notification
  -> register/unregisterActivitySwitchObserver(): ACTIVITY_SWITCH_WATCHER permission
  -> packageLifetimeHint(): SMARTOOM_HINTING permission, process-LRU adjustment
  -> preWarmApplicationForUser(): APP_PREWARM check result not consumed locally; process prewarm only
  -> checkKillAppGoingIntoBg(): process-control candidate; no local permission literal in bounded body
  -> PIP/multi-window methods: CONTROL_PIP_WINDOW permission

No method in this BinderService bounded class body calls a HOME resolver, writes a
preferred activity, selects a Fire Launcher component, or calls startHomeActivity.
