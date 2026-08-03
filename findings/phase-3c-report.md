# Phase 3C report — HOME selection state mutation experiments

## Executive summary

No shell-writable state tested in Phase 3C produced a true third-party HOME
replacement without modifying Fire Launcher.

The controlled p0 mutation successfully wrote an exact MAIN+HOME+DEFAULT
ordinary preferred record with mAlways=true. The record survived one reboot.
Nevertheless resolver remained priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true | com.amazon.firelauncher/.Launcher, Home key and explicit HOME
remained Fire, and foreground remained Fire. This directly explains why
set-home-activity can report success without changing effective HOME.

The strongest explanation remains the Phase 3B/AOSP-shaped chooseBestActivity
ordering: Fire effective priority 50 wins before an ordinary priority-0
preferred record can be used as a tie-breaker. A concrete Amazon callback
override is not proven.

## Evidence status

- 已證實: baseline, p0 preferred write, p0 persistence, Fire result through
  Home key, explicit HOME, lock/unlock, reboot, and explicit rollback.
- 高可信推論: ordinary preferred state is lower priority than Fire in the
  observed resolver path.
- 待驗證: non-null Amazon resolve callback, native indirect settings reader,
  and intentional failure fallback.
- 已排除: p0 ordinary preferred state as a true HOME replacement.
- 因風險拒絕測試: Fire mutation, core overlays, provisioning/Device Owner,
  and crash-loop fallback.

## Device and evidence

- Model: KFTRWI
- Fingerprint: Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys
- Fire OS: 7.0
- Security patch: 2024-02-01
- Canonical snapshot: adb/phase3c/PHASE3C-BASELINE-20260803-02
- Experiment: adb/phase3c/PHASE3C-PREFERRED-P0-02
- Supplemental logged run: adb/phase3c/PHASE3C-PREFERRED-P0-03; event logcats were captured around preferred write, Home key, explicit HOME, lock/unlock, reboot, rollback, and test-package removal.

The candidate set was Fire priority 50, Microsoft priority 0, p0 priority 0
during the experiment, and FallbackHome -1000.

## Preferred mutation and rollback

Before: preferred XML selected Fire.

After write: XML selected org.fireosresearch.home.p0/org.fireosresearch.home.HomeActivity; preferred dump had mAlways=true; query
still selected Fire.

After reboot: XML still selected org.fireosresearch.home.p0/org.fireosresearch.home.HomeActivity; query and foreground remained
Fire.

Rollback: XML selected com.amazon.firelauncher/.Launcher; restore and p0 uninstall returned exit
0. Final p0 path was absent and Fire remained installed/enabled/visible/
unsuspended.

## Settings, roles, AppOps, overlays, callbacks

Settings were captured but not changed. Custom launcher-shaped keys had no
HOME-selector reader/writer evidence. HOME role holder output was empty with a
non-success status; device_config was unavailable. Overlay listing had no
relevant mutable HOME overlay. AppOps were captured but no HOME-specific
mutation was justified.

Amazon callback boundaries are documented separately. The experiment shows no
third-party or Fire-specific ResolveInfo returned by an observed callback.

## Final classification

The nearest safe route is a temporary visible explicit Launcher start, not a
HOME replacement. The next highest-value hypothesis is a positive trace of a
non-null Amazon resolveIntent callback during a HOME request, including its
caller/service and returned component.

## Reproduction

    tools/scripts/capture_phase3c_state.sh --serial SERIAL --test-id ID --output DIR
    tools/scripts/run_phase3c_preferred_experiment.sh --serial SERIAL --test-id ID --apk tools/test-launcher/dist/20260803-jdk26/org.fireosresearch.home.p0.apk --output DIR --reboot --lock-unlock --approve-state-change
    tools/scripts/compare_phase3c_state.py --before DIR/before --after DIR/after_rollback --output DIR/rollback-diff.md

The runner's restore plan contains only Fire preferred state and p0 absent
state; it never replays all settings.
