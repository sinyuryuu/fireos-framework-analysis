# Phase 3C evidence index

All raw command output is preserved under adb/phase3c. Each snapshot and
experiment has a SHA-256 manifest. Unavailable command output is not treated
as negative runtime evidence.

## P3C-BASE-001 — canonical baseline

- Source: Phase 3C-0 read-only snapshot
- File: adb/phase3c/PHASE3C-BASELINE-20260803-02/summary.md and adb/phase3c/PHASE3C-BASELINE-20260803-02/sha256sums.txt
- SHA-256: 0b07de740d4a6939d5bfc1b107666daaa8d51cabc8ace1c718611973c8cae351
- Test ID: PHASE3C-BASELINE-20260803-02
- Command: capture_phase3c_state.sh with explicit serial
- Observed: Fire HOME resolver priority 50; settings, package, activity,
  role, policy, overlay, appops, user and XML probes preserved.
- Interpretation: canonical pre-mutation state
- Confidence: Confirmed

## P3C-ROLE-001 — role/device_config availability

- Source: read-only command probes
- File: adb/phase3c/PHASE3C-BASELINE-20260803-02/config/home_role_holders.stdout.txt,
  adb/phase3c/PHASE3C-BASELINE-20260803-02/config/home_role_holders.exit_code.txt,
  adb/phase3c/PHASE3C-BASELINE-20260803-02/config/device_config.exit_code.txt
- Test ID: PHASE3C-BASELINE-20260803-02
- Command: cmd role holders android.app.role.HOME --user 0; device_config list
- Observed: no HOME holder output and device_config command unavailable
- Interpretation: no safe role/device_config mutation target on this build
- Confidence: Confirmed availability result

## P3C-PREF-001 — ordinary preferred record writes but does not win

- Source: controlled p0 experiment
- File: adb/phase3c/PHASE3C-PREFERRED-P0-02/after_preferred/package/preferred_xml.stdout.txt,
  adb/phase3c/PHASE3C-PREFERRED-P0-02/after_preferred/package/preferred_activities.stdout.txt,
  adb/phase3c/PHASE3C-PREFERRED-P0-02/after_preferred/package/home_resolve.stdout.txt
- SHA-256: preferred XML 66bd351ba7a4845b9031d14aeb4931afd25d3befc8fddca192f6ad8a5469e76c; resolver d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6
- Test ID: PHASE3C-PREFERRED-P0-02
- Command: cmd package set-home-activity --user 0 org.fireosresearch.home.p0/org.fireosresearch.home.HomeActivity
- Observed: success; exact MAIN+HOME+DEFAULT record selected p0 with
  mAlways=true; resolver still selected Fire priority 50
- Interpretation: preferred storage is not the decisive selection layer
- Confidence: Confirmed

## P3C-HOME-001 — Home entry paths remain Fire

- Source: p0 experiment snapshots
- File: adb/phase3c/PHASE3C-PREFERRED-P0-02/after_home_key, adb/phase3c/PHASE3C-PREFERRED-P0-02/after_explicit_home,
  adb/phase3c/PHASE3C-PREFERRED-P0-02/after_lock_unlock
- Test ID: PHASE3C-PREFERRED-P0-02
- Command: input keyevent 3; am start MAIN+HOME; power key lock/unlock
- Observed: resolver, task, and foreground remained Fire
- Interpretation: preferred mutation did not change either tested HOME path
- Confidence: Confirmed

## P3C-REBOOT-001 — preferred record persists but is ineffective

- Source: one controlled reboot after safe preferred mutation
- File: adb/phase3c/PHASE3C-PREFERRED-P0-02/after_reboot/package/preferred_xml.stdout.txt,
  adb/phase3c/PHASE3C-PREFERRED-P0-02/after_reboot/package/home_resolve.stdout.txt,
  adb/phase3c/PHASE3C-PREFERRED-P0-02/after_reboot/activity/activities.stdout.txt
- Test ID: PHASE3C-PREFERRED-P0-02
- Command: adb reboot; wait for sys.boot_completed=1
- Observed: p0 record persisted; resolver and foreground were Fire
- Interpretation: persistence is distinct from resolver effectiveness
- Confidence: Confirmed

## P3C-ROLLBACK-001 — explicit rollback

- Source: restore plan and final snapshot
- File: adb/phase3c/PHASE3C-PREFERRED-P0-02/mutations/restore.exit_code.txt,
  adb/phase3c/PHASE3C-PREFERRED-P0-02/mutations/uninstall_test.exit_code.txt,
  adb/phase3c/PHASE3C-PREFERRED-P0-02/after_rollback/package/home_resolve.stdout.txt
- SHA-256: restore status 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa
- Test ID: PHASE3C-PREFERRED-P0-02
- Command: restore Fire preferred; pm uninstall --user 0 p0
- Observed: both exit 0; p0 absent; Fire installed/enabled/visible/unsuspended
- Interpretation: complete rollback succeeded
- Confidence: Confirmed

## P3C-HARNESS-001 — rejected pilot

- Source: first runner attempt
- File: adb/phase3c/PHASE3C-PREFERRED-P0-01/mutations/set_preferred.stderr.txt
- Test ID: PHASE3C-PREFERRED-P0-01
- Observed: IllegalArgumentException because the runner used the wrong class
  name; emergency restore/uninstall exit 0
- Interpretation: test harness failure, not Fire behavior
- Confidence: Confirmed

## P3C-SETTINGS-001 — settings inventory boundary

- Source: baseline settings and static search
- File: output/tables/phase-3c-settings-matrix.csv,
  findings/phase-3c-settings-key-inventory.csv and
  findings/phase-3c-settings-key-analysis.md
- Test ID: PHASE3C-BASELINE-20260803-02
- Observed: launcher-shaped custom keys had no HOME-selector reader/writer in
  inspected code; no settings mutation was executed
- Interpretation: random settings writes were rejected by evidence standard
- Confidence: Strong evidence

## P3C-OVERLAY-001 — overlay boundary

- Source: overlay list/dump
- File: adb/phase3c/PHASE3C-BASELINE-20260803-02/overlay/list.stdout.txt and adb/phase3c/PHASE3C-BASELINE-20260803-02/overlay/dump.stdout.txt
- Test ID: PHASE3C-BASELINE-20260803-02
- Observed: only internal cutout and SystemUI dark overlays; no HOME-specific
  mutable overlay
- Interpretation: no justified overlay mutation
- Confidence: Confirmed observation

## P3C-CALLBACK-001 — Amazon callback remains open

- Source: Phase 3B static evidence
- File: decompiled/jadx/systemui/sources/com/android/server/am/ActivityStackSupervisor.java:745-772;
  decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:41093-41138
- Test ID: PHASE3B
- Observed: vendor resolve callback boundary exists; inspected implementation
  delegates to PM and does not name Fire
- Interpretation: callback participation possible, direct override unproven
- Confidence: Strong evidence / unresolved return value


## P3C-LOGCAT-001 — logged preferred experiment

- Source: supplemental controlled p0 experiment with event logcat capture
- File: adb/phase3c/PHASE3C-PREFERRED-P0-03/logs/set_preferred.logcat.txt,
  adb/phase3c/PHASE3C-PREFERRED-P0-03/logs/home_key.logcat.txt,
  adb/phase3c/PHASE3C-PREFERRED-P0-03/logs/explicit_home.logcat.txt,
  adb/phase3c/PHASE3C-PREFERRED-P0-03/logs/after_reboot.logcat.txt,
  adb/phase3c/PHASE3C-PREFERRED-P0-03/logs/restore.logcat.txt and final SHA-256
  manifest
- Test ID: PHASE3C-PREFERRED-P0-03
- Command: clear logcat, perform one controlled event, dump all buffers;
  repeat for the recorded mutation and rollback boundaries
- Observed: all logcat dump commands exited 0; the matching snapshots still
  resolved Fire before, after preferred write, after Home/explicit HOME,
  after lock/unlock, after reboot, and after rollback
- Interpretation: event-level raw logcat is preserved, but the state
  snapshots remain the authoritative resolver result; no callback override is
  inferred from logcat alone
- Confidence: Confirmed evidence preservation; Strong evidence for unchanged
  observed result
