# Phase 16 capability-to-sink graph (text form)

```text
Kernel/driver capability
  -> caller + UID/domain + SELinux/node gate [missing in saved corpus]
  -> no low-privilege kernel sink claim

Ordinary APK/service reachability
  -> Amazon Binder method gate
  -> preWarmApplicationForUser
  -> startProcessLocked/resource effect
  -> confirmed process/resource deputy; no HOME/package/root sink

KFT child/profile lifecycle
  -> supplied UserInfo.id and child/profile scope
  -> enabled-state setters
  -> Tahoe enabled; Fire/Launcher3 disabled for child/profile
  -> no closed ordinary User-0 relay

User-0 package/HOME mutation
  -> PMS protected-package/caller gate
  -> existing shell/component tests rejected; state unchanged

Signed OTA/recovery updater
  -> verification and recovery/system context
  -> block-image/boot-chain partition capability
  -> ordinary caller not closed; no execution performed

Historical Phase 1-15 tests
  -> evidence reconciliation and no-repeat policy
  -> next safe candidate is passive natural observation only
```
