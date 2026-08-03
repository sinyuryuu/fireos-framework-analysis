# Phase 2 Mutation Test Summary

Status: `CONTROLLED_MUTATION_REVIEW_COMPLETE`

No new Fire Launcher component-disable mutation was executed in Phase 2 because `COMPONENT-T01` and `COMPONENT-T02` already proved that the tested shell paths enter the same protected-package gate and that the component state never changed.

## 1. Existing reversible preferred-home tests

| Test ID | Mutation | Before | Command result | After mutation | Reboot check | Restore | Evidence |
|---|---|---|---|---|---|---|---|
| `HOME-DEFAULT-T01` | Set Microsoft as HOME | Fire resolver and Fire preferred record | `Success` | Microsoft preferred record was written, but effective resolver remained Fire and Home returned Fire | Not performed in this test | Set Fire returned `Success`; final resolver/foreground Fire | `P2-HOME-003` |
| `HOME-PREF-T17` | Set Microsoft as HOME, send keyevent 3 | Fire resolver; Fire preferred record | `Success` | Microsoft record had `mAlways=true`, but resolver still reported Fire priority 50; Home returned Fire | Not performed in this test | Set Fire returned `Success`; final state Fire | `P2-HOME-003` |
| `COMPONENT-T01` | Disable Fire HOME component with `pm` | Enabled/default | Exit 255, protected-package exception | No state mutation | Not applicable | Restore command also rejected; final state comparison unchanged | `P2-RUN-001`, `P2-STATE-001` |
| `COMPONENT-T02` | Disable Fire HOME component with `cmd package` | Enabled/default | Exit 255, same exception | No state mutation | Not applicable | Restore skipped because disable was rejected | `P2-RUN-002`, `P2-STATE-001` |

## 2. Preferred record detail

`HOME-PREF-T17` demonstrates a meaningful distinction:

```text
After setting Microsoft:
  Preferred Activities User 0 -> com.microsoft.launcher/.Launcher
  mAlways=true

Effective HOME resolve:
  priority=50 ...
  com.amazon.firelauncher/.Launcher
```

Thus the preferred API write and the effective resolver result diverged. This is the central Phase 2 mutation observation.

## 3. Recovery framework

`tools/scripts/capture_mutation_snapshot.sh` was added. It:

- requires `--serial`, `--test-id`, and `--output`;
- refuses to reuse an output directory;
- verifies the selected serial is in `device` state;
- captures fingerprint, HOME candidates/resolver, preferred state, package state, activity/window/input state, settings, DeviceConfig, overlays, and AppOps;
- writes a restore template rather than executing a restore;
- supports `--dry-run` and never runs a state-changing command.

For each future Level 2 mutation, the mutation-specific runner must add the exact command, original value, expected state, restore command, and post-reboot verification to the test directory. A generic restore command must not be invented.

## 4. No new reboot

No reboot was needed to establish the current preferred-state result. A reboot remains a permitted Level 2 operation only after a complete pre-state snapshot and a test-specific restore plan. It was not run in this Phase 2 pass.

## 6. Phase 3A priority experiment status

The Phase 3A mutation runner and per-test restore framework are implemented in
`tools/scripts/run_home_priority_experiment.sh`. A read-only pre-snapshot was
captured at `adb/mutation-tests/HOME-PRIORITY-PRE/` and verified with its local
SHA-256 manifest. Five APK variants were built with the local SDK/OpenJDK 26
toolchain and tested one at a time.

P49, P50, P51, and P100 completed install, ordinary preferred-home write,
explicit HOME, Home key, lock/wake, reboot, post-reboot Home, Fire restore,
and uninstall. P0 was interrupted after reboot during the first runner
attempt; its raw evidence was retained and its generated restore sequence
completed successfully. All final resolver checks returned
`com.amazon.firelauncher/.Launcher`, and no test APK remained installed.

The APK manifest declarations 49/50/51/100 were preserved, but all ordinary
sideloaded candidates were reported by PackageManager at effective priority 0.
The matching AOSP/Fire `adjustPriority()` path explains this as the standard
non-privileged priority cap. The preferred record could be written with
`mAlways=true`, including across reboot, but it did not become effective HOME.

`cmd package clear-package-preferred-activities` is unavailable on this build;
the exact `Unknown command` output is preserved. Restoration used supported
Fire `set-home-activity` followed by test-package uninstall.

## 5. Stop conditions

The following conditions stop further mutation work:

- ADB serial changes state from `device` to `offline`/`unauthorized`.
- The selected package is SystemUI, Settings, SettingsProvider, Setup Wizard, Package Installer, Permission Controller, lock screen, input method, or another core package without a verified recovery path.
- A proposed step would require Root, a system remount, boot/recovery/partition writes, factory reset, userdata erase, sideload, downgrade, or bootloader change.
- The before-state cannot be captured or the restore command cannot be validated.
