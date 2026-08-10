# Phase 6UL — prior-test reconciliation

Date: 2026-08-10 (Asia/Taipei)

This is a host-only reconciliation of the preserved `adb/`, `findings/`,
`artifacts/`, scripts, and public ledgers. No device was contacted in this
pass. No mutation, reboot, private Binder transaction, driver/node operation,
OTA/OOBE delivery, recovery/updater execution, root, or partition operation
was performed.

The row-level ledger is [the CSV](./luna_worker_phase6ul_test_reconciliation_20260810.csv).
The status vocabulary is intentionally narrow: `CONFIRMED` means the bounded
claim is directly supported by saved evidence; `DISPROVED` means the tested
route did not produce the stated target effect in its recorded scope;
`UNKNOWN` means a read-only evidence join is still missing; and
`REJECTED_RISK` means the operation was not performed because it would cross
the stated safety boundary. A rejected operation is not a negative runtime
result.

## Reconciled conclusion

The existing corpus does not close an ordinary app or shell path of the form
`ordinary caller → accepted privileged identity → User-0 HOME/package/root/
partition sink`. Fire remains the saved User-0 HOME winner at priority 50;
ordinary preferred-HOME and package-state attempts did not establish a durable
third-party replacement. The only launcher-specific Amazon writer closed by
runtime evidence is KFT and it is target-user/child/profile scoped. Switching
back to User 0 preserved Fire state.

The strongest evidence for a broader non-Launcher privileged sink is static,
not an end-to-end ordinary-caller result:

* AmazonActivityManager prewarm has an `APP_PREWARM` gate and a privileged Alexa
  caller in the preserved source/caller audit. Its downstream identity,
  user propagation, and sensitive sink are not closed.
* DPM/Profile Owner and PMS paths show trusted owner/admin/UID gates and
  system-side writers, but no ordinary relay or active backup-restore writer
  was demonstrated.
* OTA/OOBE/updater artifacts contain real lifecycle and partition-writer sinks,
  while protected/signature/phase gates, native handoff, exact numeric user,
  and caller provenance remain unresolved.
* Driver/ION source, ELF, and SELinux artifacts show conditional capability
  edges only. No retail native client, node access, active branch, or sensitive
  effect is joined.

## Duplicate and superseded test families

The following are duplicate families when build fingerprint, user/profile
topology, package candidate set, and rollback state are unchanged: HOME
resolver/foreground snapshots; preferred/set-home matrices; Fire package and
component guards; service list/check/find visibility; child/Tahoe/KFT state
captures; accessibility monitor/redirect iterations; and before/after/final
guards. A new filename does not create a new test result. Keep one canonical
capture per exact condition and use the other captures only for corroboration.

The following routes are explicitly closed for replay: priority APK and
ordinary `set-home`; package/PMS setters; child creation/switch/unlock and
raw KFT transactions; unknown Amazon Binder calls; accessibility isolation or
secure-setting replay; DPM owner provisioning/removal; protected OOBE/OTA
broadcasts; OTA/recovery/updater/partition actions; driver ioctl/node access;
and root/exploit/bootloader paths.

## Exact confirmed negatives and bounded positives

* Fire repeatedly resolves/resumes as User-0 HOME at saved priority 50.
* Ordinary preferred-HOME records did not displace Fire, and saved Fire
  protected-package/component gates rejected the attempted state changes.
* Child/Tahoe HOME is a positive child-scoped result, not a User-0 result;
  the broad launcher-replacement interpretation is disproved by the saved
  switch-back and final guards.
* The installed Accessibility service had a bind/no-callback observation;
  the ADB/Accessibility fallback was foreground-only and not a formal HOME
  writer.
* Shell service lookup did not yield a callable private handle; service-name
  visibility is not transaction reachability.
* The H2 custom `BIND_SERVICE` declaration is signature-gated. Holder,
  grant, external production caller, and downstream sink remain unknown.

## Untested read-only questions

1. Can the preserved exact-build source and decompiled artifacts identify the
   complete production caller → gate/identity → user → HOME/package chain for
   KFT, PMS/HOME, prewarm, DPM, and private services?
2. Which package owns and grants the H2 permission, and is there a production
   requesting package with a compatible signature?
3. Does the ION/native graph join to an actually loaded retail process/domain,
   `/dev/ion` policy, and a sensitive effect?
4. What exact numeric user and caller are propagated by OOBE/BootAfterSystemOTA,
   and what is the native updater/fosinit handoff in the preserved files?
5. Do Settings resources/overlays expose an unindexed Home-picker or default-
   home gate? Existing evidence does not establish a runtime selection.

Only host-side path existence, SHA-256/manifest/schema checks, report-to-raw
reference checks, saved snapshot comparison, archive EOF/provenance review,
and source/permission/caller/user/sink joins are safe next targets. Any target
requiring a new lifecycle event or device state change remains out of scope.

