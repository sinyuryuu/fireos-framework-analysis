# Phase 6C runtime evidence index

All entries refer to the selected Fire tablet only. The capture did not run
`adb devices -l`, so no unrelated device serial was included in the raw
evidence.

## P6C-RO-001

- Source: selected-device state check
- File: `adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/state.stdout.txt`
- SHA-256: `c98373c1abef78070f6beef6b4ae4fbf3de348dac280195c7f93441920584af9`
- Test ID: `PHASE6C-BOUNDARY-RO-20260804-05`
- Timestamp: `2026-08-04T13:03:53Z`
- Command: `adb -s G001LT0511550CFT get-state`
- Observed result: `device`
- Interpretation: the explicitly selected serial was connected for the read-only capture.
- Confidence: **Confirmed**
- Related hypothesis: runtime boundary can be sampled without changing device state.

## P6C-RO-002

- Source: build properties
- File: `adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/props.stdout.txt`
- SHA-256: `eff54128ec883e000ebc1efc10b90806aa2526bd280557ecffa83051125ab4a2`
- Test ID: `PHASE6C-BOUNDARY-RO-20260804-05`
- Timestamp: `2026-08-04T13:03:53Z`
- Command: `adb -s G001LT0511550CFT shell getprop`
- Observed result: PS7331 fingerprint, KFTRWI/trona, Android 9, patch 2024-08-01, verified boot green, non-debuggable.
- Interpretation: the captured runtime identity matches the analyzed PS7331 target.
- Confidence: **Confirmed**
- Related hypothesis: source/image provenance is the primary remaining uncertainty.

## P6C-RO-003

- Source: shell identity and SELinux
- File: `adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/identity.stdout.txt`, `selinux.stdout.txt`
- SHA-256: `7bb4a293663f02c546ed9222fac711bbc22aa451bbfdada564d7019e8e4daff8`, `4fefafd0dcddf54b31a0fef448083e7b77576d86a9ec97c14bfd92479c404290`
- Test ID: `PHASE6C-BOUNDARY-RO-20260804-05`
- Timestamp: `2026-08-04T13:03:53Z`
- Command: `adb -s G001LT0511550CFT shell id`; `adb -s G001LT0511550CFT shell getenforce`
- Observed result: UID 2000 shell, context `u:r:shell:s0`, SELinux `Enforcing`.
- Interpretation: the test process has no system/root identity in this capture.
- Confidence: **Confirmed**
- Related hypothesis: an untrusted/shell process may form the required proxy state.

## P6C-RO-004

- Source: kernel release metadata
- File: `adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/kernel_version.stdout.txt`
- SHA-256: `dc109e99fe3314f2fce639c9fff371b67b224a833f04a34a779b4e07c661a0d7`
- Test ID: `PHASE6C-BOUNDARY-RO-20260804-05`
- Timestamp: `2026-08-04T13:03:53Z`
- Command: `adb -s G001LT0511550CFT shell cat /proc/version`
- Observed result: Linux `4.4.146+`, AArch64, PS7331 build timestamp 2025-05-03.
- Interpretation: the runtime kernel version is consistent with the Phase 5/6 source analysis.
- Confidence: **Confirmed**
- Related hypothesis: PS7331 source/config analysis targets the running kernel family.

## P6C-RO-005

- Source: kernel symbol visibility
- File: `adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/proc_kallsyms_head.stderr.txt`
- SHA-256: `d7be6ebe9c2155a294ac142db8a18b3ae708d4e2ee7553ff59234b81e530d1e2`
- Test ID: `PHASE6C-BOUNDARY-RO-20260804-05`
- Timestamp: `2026-08-04T13:03:53Z`
- Command: `adb -s G001LT0511550CFT shell head -n 5 /proc/kallsyms`
- Observed result: `Permission denied`.
- Interpretation: shell cannot observe kernel symbol addresses through this path.
- Confidence: **Confirmed**
- Related hypothesis: runtime address recovery is available to an untrusted process.

## P6C-RO-006

- Source: slab visibility
- File: `adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/proc_slabinfo_head.stderr.txt`
- SHA-256: `8f02e39810fb9e87ed32ec33aa27e62cf268122c37d0ddb50c135bb4ee89d649`
- Test ID: `PHASE6C-BOUNDARY-RO-20260804-05`
- Timestamp: `2026-08-04T13:03:54Z`
- Command: `adb -s G001LT0511550CFT shell head -n 20 /proc/slabinfo`
- Observed result: `No such file or directory`.
- Interpretation: shell cannot use this proc interface to observe live slab state.
- Confidence: **Confirmed**
- Related hypothesis: live SLUB occupancy can be measured from the stock shell.

## P6C-RO-007

- Source: KASLR sysctl visibility
- File: `adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/kaslr_setting.stderr.txt`
- SHA-256: `fa962956d0f0e729eadaaacb253b1f2b942c0c11aceaa6900e05f6af12594e88`
- Test ID: `PHASE6C-BOUNDARY-RO-20260804-05`
- Timestamp: `2026-08-04T13:03:54Z`
- Command: `adb -s G001LT0511550CFT shell cat /proc/sys/kernel/randomize_va_space`
- Observed result: `Permission denied`.
- Interpretation: shell cannot read this KASLR setting through the selected proc path.
- Confidence: **Confirmed**
- Related hypothesis: KASLR runtime state is directly observable to shell.

## P6C-RO-008

- Source: HOME resolver
- File: `adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/home_resolution.stdout.txt`
- SHA-256: `50db8de21b17ab5cefc377ea3432e912d9d99a3146805bcfee473c42950482fe`
- Test ID: `PHASE6C-BOUNDARY-RO-20260804-05`
- Timestamp: `2026-08-04T13:03:54Z`
- Command: `adb -s G001LT0511550CFT shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME`
- Observed result: OOBE Home at priority 100.
- Interpretation: the current resolver context is setup/OOBE-sensitive.
- Confidence: **Confirmed**
- Related hypothesis: OOBE state is the reason the normal Fire Launcher result is not returned in this snapshot.

## P6C-RO-009

- Source: HOME candidate query
- File: `adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/home_candidates.stdout.txt`
- SHA-256: `f177904785bba1d7a142caf4b28d635bedf14da8ff51a639a9b52344125e7890`
- Test ID: `PHASE6C-BOUNDARY-RO-20260804-05`
- Timestamp: `2026-08-04T13:03:54Z`
- Command: `adb -s G001LT0511550CFT shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME`
- Observed result: OOBE priority 100, Fire Launcher priority 50, sideloaded launcher candidates effective priority 0, plus existing test candidates.
- Interpretation: candidate inclusion and resolver selection are distinct in the current state.
- Confidence: **Confirmed**
- Related hypothesis: a preferred record alone can defeat the priority-100 OOBE candidate.

## P6C-RO-010

- Source: setup state
- File: `adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/setup_state.stdout.txt`, `setup_state_global.stdout.txt`
- SHA-256: `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`, `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
- Test ID: `PHASE6C-BOUNDARY-RO-20260804-05`
- Timestamp: `2026-08-04T13:03:54Z`
- Command: `settings get secure user_setup_complete`; `settings get global device_provisioned`
- Observed result: `0`; `1`.
- Interpretation: device provisioning is marked complete while user setup is not complete in the captured state.
- Confidence: **Confirmed**
- Related hypothesis: OOBE is selected because user setup is incomplete.

## P6C-RO-011

- Source: activity/window state
- File: `adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/activity_activities.stdout.txt`, `window_windows.stdout.txt`
- SHA-256: `fef364fd1538e14bd8c4c1aea58e12188d0e4601b3c60d2f27117d5f5ecd4867`, `70f6181530c2f2339a1da97ea744aac411f4693e896ec241f99dbd8da939afe9`
- Test ID: `PHASE6C-BOUNDARY-RO-20260804-05`
- Timestamp: `2026-08-04T13:03:55Z`
- Command: `dumpsys activity activities`; `dumpsys window windows`
- Observed result: Microsoft Launcher was resumed/current focus; Fire Launcher task/window remained present; records include `mUserSetupComplete=false`.
- Interpretation: current foreground state is not the same thing as the resolver result captured by a new query.
- Confidence: **Confirmed**
- Related hypothesis: the mismatch itself proves an Amazon callback or kernel issue.

## P6C-RO-012

- Source: Fire Launcher path/package dump
- File: `adb/phase6c/PHASE6C-BOUNDARY-RO-20260804-05/firelauncher_path.stdout.txt`, `firelauncher_package.stdout.txt`
- SHA-256: `a742d1a2dfee2310e701201e4a1fdf3c34fee3280914a599c314cb512deb3a38`, `a980e8e2501d29672048909707042a25f3863918627bb0fd55551569af076d8c`
- Test ID: `PHASE6C-BOUNDARY-RO-20260804-05`
- Timestamp: `2026-08-04T13:03:54Z`
- Command: `pm path com.amazon.firelauncher`; `dumpsys package com.amazon.firelauncher`
- Observed result: Fire Launcher is under `/system/priv-app`, UID 10120, privileged/system flags, launcher `.Launcher` present.
- Interpretation: the package has a system/privileged identity unlike a sideloaded launcher.
- Confidence: **Confirmed**
- Related hypothesis: package identity and privilege contribute to HOME ranking or protection.
