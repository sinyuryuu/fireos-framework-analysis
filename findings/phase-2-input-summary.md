# Phase 2 Input Summary

Status: `READ_ONLY_INPUT_REVIEW_COMPLETE`

Date: 2026-08-03 (Asia/Taipei)

Device serial: `G001LT0511550CFT`

This document records the material that was read before Phase 2 analysis. The original reports, raw test directories, and SHA-256 manifests were not modified. The already-disproved component-disable experiment was not repeated.

## 1. Inputs read

| Input | Purpose | Integrity |
|---|---|---|
| `findings/component-protection.md` | Existing interpretation of package/component rejection | Read; source report hash recorded in Phase 2 evidence index |
| `findings/phase-1-report.md` | Phase 1 device, HOME, Settings and framework findings | Read; source report hash recorded in Phase 2 evidence index |
| `output/rendered/phase-1-report.phase2-final10.md` | Rendered Phase 1 report used for cross-checking | Read; source report hash recorded in Phase 2 evidence index |
| `tools/scripts/test_component_disable.sh` | Existing test implementation and safety behavior | Read; source hash recorded in Phase 2 evidence index |
| `adb/component-tests/COMPONENT-T01/` | `pm disable-user` component test | Read; manifest passed SHA verification |
| `adb/component-tests/COMPONENT-T02/` | `cmd package disable-user` component test | Read; manifest passed SHA verification |
| `adb/baseline/BASELINE-20260803-07/` | Latest device/package/HOME baseline | Read; manifest passed SHA verification |
| `device/baseline/BASELINE-20260803-07/` | Latest device property baseline | Read; manifest passed SHA verification |

The static inputs used after this review are separately identified in `findings/evidence-index-phase2.md`; they include the Fire OS services VDEX, Amazon FOS services VDEX, Fire Launcher manifest, Amazon `fosinit` registration, and AOSP Android 9 source.

## 2. Existing test purposes and commands

### COMPONENT-T01

Purpose: determine whether the shell can disable only the Fire Launcher HOME component through `pm` and whether the component state, HOME resolver, activity, or window state changes.

Test metadata: `2026-08-03T04:50:46Z`–`2026-08-03T04:50:49Z`, user 0.

The command manifest records these state-changing commands:

```text
adb -s G001LT0511550CFT shell pm disable-user --user 0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher
adb -s G001LT0511550CFT shell pm default-state --user 0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher
```

The test also captured package state, disabled-package list, HOME resolution, activity state, and window state before and after each operation, then sent `input keyevent 3`.

### COMPONENT-T02

Purpose: determine whether the `cmd package` shell entry point bypasses the `pm` path for the same component.

Test metadata: `2026-08-03T04:51:59Z`–`2026-08-03T04:52:02Z`, user 0.

The command manifest records:

```text
adb -s G001LT0511550CFT shell cmd package disable-user --user 0 com.amazon.firelauncher/com.amazon.firelauncher.Launcher
```

The restore operation was skipped because the disable request was rejected before any state change. The same before/after package, resolver, activity, window, and `input keyevent 3` evidence was captured.

### Existing HOME preferred-activity tests

`HOME-DEFAULT-T01` and `HOME-PREF-T17` attempted:

```text
adb -s G001LT0511550CFT shell cmd package set-home-activity com.microsoft.launcher/.Launcher
adb -s G001LT0511550CFT shell input keyevent 3
adb -s G001LT0511550CFT shell cmd package set-home-activity com.amazon.firelauncher/.Launcher
```

These are existing controlled tests. They are not being repeated merely to reproduce the same result.

## 3. Actual rejection

Both component-disable entry points returned exit status `255` and the same error:

```text
Security exception: Cannot disable a protected package: com.amazon.firelauncher

java.lang.SecurityException: Cannot disable a protected package: com.amazon.firelauncher
```

The recorded runtime stack is:

```text
com.android.server.pm.PackageManagerService.setEnabledSetting(PackageManagerService.java:21128)
com.android.server.pm.PackageManagerService.setComponentEnabledSetting(PackageManagerService.java:21057)
com.android.server.pm.PackageManagerShellCommand.runSetEnabledSetting(PackageManagerShellCommand.java:1624)
com.android.server.pm.PackageManagerShellCommand.onCommand(...)
com.android.server.pm.PackageManagerService.onShellCommand(...)
android.content.pm.IPackageManager$Stub.onTransact(...)
```

The `pm default-state` restore request in T01 also returned the same protected-package exception. Since the disable request had not changed the state, the final state comparison, rather than the restore command status alone, is the authority for restoration.

## 4. Before/after state comparison

| Observation | COMPONENT-T01 | COMPONENT-T02 | Phase 2 interpretation |
|---|---|---|---|
| Package enabled state | No change | No change | `Confirmed`: rejection precedes package-state mutation |
| `.Launcher` enabled state / disabled-components entry | No new entry | No new entry | `Confirmed`: component-state mutation did not occur |
| `pm list packages -d` | No Fire Launcher transition | No Fire Launcher transition | `Confirmed` |
| HOME resolver | Fire Launcher before/after/final | Fire Launcher before/after/final | `Confirmed` |
| `mResumedActivity` | Fire Launcher before/after/final | Fire Launcher before/after/final | `Confirmed` |
| `mCurrentFocus` | Fire Launcher window state unchanged | Fire Launcher window state unchanged | `Confirmed` |
| Home key after rejected request | Fire Launcher | Fire Launcher | `Confirmed`; not evidence of a watchdog |

The package-dump hashes for the T01 before and after package snapshots are identical (`d09b1b6d857888cd85c77f2045a5d0e87246e95e0014f119f84789406ed5325f`). The complete per-file hashes remain in each original test directory.

## 5. Existing confirmed and disproved conclusions

### Confirmed

1. `pm disable-user` cannot disable the tested Fire Launcher component on user 0.
2. `cmd package disable-user` reaches an equivalent rejection for the same component.
3. Both errors are raised by the PackageManager service before the observed package/component state changes.
4. The resolver remains `com.amazon.firelauncher/.Launcher` with priority 50 in the captured state.
5. The latest baseline is restored to normal Fire Launcher foreground state.
6. The test did not execute root, data clearing, factory reset, flashing, system remount, or boot-image modification.

### Disproved

The hypothesis that disabling only `com.amazon.firelauncher/.Launcher`, while leaving the rest of the package intact, is a working no-root ADB HOME workaround is `Disproved` for the tested build and caller conditions.

The same test must not be repeated unless a material precondition changes, such as the caller UID, DevicePolicy state, Fire OS framework, overlay, or protected-package data.

### Still unknown before static Phase 2 analysis

- The exact protected-package helper and its input conditions.
- The source that adds Fire Launcher to the protected set.
- Whether the set contains a literal Fire Launcher entry or is supplied at runtime.
- Whether the gate is only AOSP behavior, an Amazon extension, or both.
- Whether HOME is fixed by priority, normal preferred state, persistent preferred state, filtering, or a custom launcher path.
- Whether a physical hardware Home key differs from the ADB keyevent path.
- Whether a permitted API outside enabled-state mutation can change the effective HOME.

## 6. Evidence IDs introduced by this summary

The following IDs are used by subsequent Phase 2 documents:

| Evidence ID | Meaning |
|---|---|
| `P2-SHA-001` | Existing T01, T02, and latest baseline SHA-256 manifests pass |
| `P2-RUN-001` | T01 `pm` protected-package rejection |
| `P2-RUN-002` | T02 `cmd package` protected-package rejection |
| `P2-STATE-001` | Package/component state unchanged before/after rejection |
| `P2-STATE-002` | HOME resolver/activity/window state unchanged |
| `P2-HOME-003` | Existing `set-home-activity` attempt accepted but effective resolver remained Fire |

Confidence labels in this document follow the project standard: `Confirmed`, `Strong evidence`, `Probable`, `Hypothesis`, and `Disproved`.
