# Phase 6O — KFT per-user and OTA fixed-target boundary

Date: 2026-08-10

## Scope

This is a host-only closure of two remaining research surfaces: the KFT launcher state writer and the PS7331 OTA/OOBE update boundary. It consumes preserved artifacts and a prior, rolled-back child-user observation. It does not contact the device, send Binder transactions, execute an OTA, or mutate Fire Launcher.

## Findings

- **已證實：** `enableKftLauncherComponent(UserInfo)` is a private per-user state writer. Its static call sites request Tahoe's FreeTime launcher and state 2 for `com.amazon.firelauncher` and `com.android.launcher3` for the supplied user.
- **已證實：** the preserved runtime profile-switch result is user-scoped: User 10 resolved Tahoe at priority 975, while returning to User 0 resolved Fire Launcher at priority 50; rollback succeeded. This does not provide a User-0 replacement.
- **已證實：** the PS7331 updater script is fixed-target recovery logic for system/vendor block updates and fixed boot/firmware partitions. The preserved audit found no archive traversal/symlink path or post-install executor.
- **已證實：** OTA control receivers/service are behind `signature|privileged` controller permission and single-user policy. OTA lifecycle broadcasts are system-protected.
- **已排除（目前證據範圍）：** no ordinary shell/App caller to the KFT writer, no ordinary caller to the OTA writer, and no evidence that these paths change User-0 HOME.
- **待驗證：** a complete CFG review of the native `update-binary` parser and a byte-complete audit of the outer source archive remain host-only gaps; neither justifies device execution.

## Evidence

| ID | Source | Classification | Confidence |
|---|---|---|---|
| 6O-KFT-001 | `artifacts/phase6ay/launcher-state-services-20260805-02/launcher-state-service-methods.csv:lines 54297-54325` | KFT_PER_USER_STATE_WRITER | Confirmed (static) |
| 6O-KFT-002 | `artifacts/phase6ay/launcher-state-services-20260805-02/launcher-state-service-methods.csv:lines 55053-55105` | INTERNAL_LIFECYCLE_ONLY | Strong evidence |
| 6O-USER-001 | `adb/phase6gr/PHASE6GR-GUI-SYSTEMUI-SWITCH-20260807-07/result.json:result.json fields child_home_last / after_owner_home` | PER_USER_HOME_SEPARATION | Confirmed (runtime) |
| 6O-OTA-001 | `artifacts/phase6bp/ota-manifest-20260805-01/META-INF/com/google/android/updater-script:lines 1-25` | FIXED_TARGET_RECOVERY_LOGIC | Confirmed (static) |
| 6O-OTA-002 | `artifacts/phase6bp/ota-path-audit-20260805-02/ota-path-audit.json:assessment / blocklist fields` | OTA_INPUT_BOUNDARY_CLOSED_FOR_SAFE_SCOPE | Strong evidence |
| 6O-OTA-003 | `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/011_com.amazon.device.software.ota__0_DeviceSoftwareOTA.xmltree.txt:lines 12-37, 114-164` | PRIVILEGED_OTA_CONTROL_PLANE | Confirmed (static) |
| 6O-OTA-004 | `artifacts/phase6bk/protected-broadcast-union-20260810-02/protected-broadcast-inventory.csv:protected-broadcast inventory rows containing BOOT_AFTER_SYSTEM_OTA and OTA status actions` | SYSTEM_PROTECTED_LIFECYCLE_SIGNAL | Confirmed (static) |

## Safety boundary

No root attempt, unknown Binder transaction, malformed ioctl, synthetic protected broadcast, recovery/sideload, partition write, Fire Launcher disable/hide/suspend/uninstall/clear, or factory reset was performed. The child-user evidence used here records a prior successful rollback; no new profile mutation was performed.

## Decision

The highest-value remaining safe work is host-only completion of the native updater CFG and broader artifact inventory. If it does not identify a legitimate unprivileged writer, the research should return to measuring a reversible launcher foreground fallback rather than retrying protected package-state routes.
