# Phase 6BA control-surface graph (text form)

```text
HOME key / explicit HOME
  -> implicit MAIN + CATEGORY_HOME
  -> ActivityStackSupervisor callback pre-hook
  -> PackageManager resolver
  -> Fire Launcher priority 50
  -> Fire Launcher resumed

shell enabled-state request
  -> PackageManager protected path
  -> Amazon deny-list callback
  -> system/privileged + deny-list membership + caller UID 2000
  -> reject before state mutation

KFT child-user/upgrade lifecycle
  -> enableKftLauncherComponent
  -> disable Fire Launcher and Launcher3
  [static only; not invoked]

post-system-OTA lifecycle
  -> BootAfterSystemOTAReceiver
  -> OobeHomeActivity/setup-state mutation
  [replay rejected]

ADB monitor
  -> observe Fire Launcher resumed
  -> explicit research Activity
  -> temporary foreground redirect
  [resolver unchanged; not HOME replacement]
```
