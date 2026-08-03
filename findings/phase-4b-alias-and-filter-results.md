# Phase 4B — multi-activity alias and filter result

## Test boundary

`PHASE4-ALIAS-T04` installed one APK only:
`org.fireosresearch.phase4.alias`. It did not call `set-home-activity`, did not
modify settings, did not change Fire Launcher state, and did not reboot. The
raw before/installed/after snapshots, explicit start output, logcat, and
rollback SHA-256 are under `adb/phase4/PHASE4-ALIAS-T04/`.

## Device result — 已證實

The installed package contributed four ordinary HOME query entries: the direct
activity, the DEFAULT alias, the HOME-only alias, and the direct-boot activity.
All had effective priority 0; the HOME-only alias was marked `isDefault=false`.
The data-specific filter was not a data-less ordinary HOME candidate, and the
`SECONDARY_HOME` activity was not in the ordinary HOME query. Every declared
component was explicitly startable; the two aliases delivered to the target
activity because it is `singleTask`.

With all these candidates present, implicit MAIN+HOME resolved to
`com.amazon.firelauncher/.Launcher`, and `input keyevent 3` returned to Fire.
After `pm uninstall --user 0 org.fireosresearch.phase4.alias`, the package path
was absent and the resolver again returned Fire. No test APK remained installed.

## Interpretation

Alias multiplicity, direct-boot awareness, DEFAULT omission, a data-specific
filter, and a secondary HOME category did not form a legal priority-0 path to
replace the privileged priority-50 Fire candidate. This supports the ranking
model, but it does not test persistent preferred or alternate profile policy.

Evidence: `P4B-ALIAS-001`, `P4B-ALIAS-ROLLBACK-001`.
