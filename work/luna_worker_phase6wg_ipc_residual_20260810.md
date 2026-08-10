# Phase 6WG — residual Amazon/system-server Binder interface scan

Date: 2026-08-10. Host-only exact-build static inspection from public Phase 6VF commit `3cf0580d9` (`3cf0580d925c98a2006748433f1ba9f2c15efdb0`). No adb, Binder/service call, driver/ioctl, OTA/recovery, reboot, package/settings mutation, or exploit/root payload was used.

## Result

The companion CSV has 3 normalized residual rows. These are beyond the 6VE inventory (SHA-256 `42d609d5d427fb691031e54caf9d25ee62718f9be64f7bf32fbc53d7eb88ab6a`) and are not duplicate enabled-state, HOME/preferred, KFT/user-setup, or OTA rows.

Each row records caller/publisher, gate, identity or user scope, and exact sink. `UNKNOWN` is retained where the decompilation does not prove the value.

- WG-001: `FireOsDisplayPowerController` is published as a Binder service. Its `dump()` checks `android.permission.DUMP`; `--set-brightness` reaches `Settings.System.putInt(..., "screen_brightness", ...)`. The transaction number, SELinux rule, and effective caller UID are UNKNOWN.
- WG-002: `InputFilterMonitorInputManagerServiceCallback.notifyCameraCoverSwitchChanged` stores the camera lens-cover state through `Settings.Secure.putInt(..., "camera_shutter_state", ...)`. It is reached through the Amazon input-manager/local callback path; the callback’s external Binder publication is not independently recovered. Caller authorization, transaction, user scope, and SELinux rule are UNKNOWN.
- WG-003: `AlexaModeSwitchManagerService` publishes `alexa_modeswitch` backed by `IAlexaModeSwitchAPI.Stub`. API methods enforce `com.amazon.alexa.permission.MODE_SWITCH`; orientation handling reaches `SecureSettingsHelper.putIntForUser` for `orientation_in_previous_mode` with `USER_CURRENT` (`-2`). The transaction number, permission protection level, service-manager and SELinux rules remain UNKNOWN.

## Reconciliation and limits

The prior Binder inventory identifies the exact-build service classes and publication candidates (`artifacts/phase6q/binder-service-audit-20260805-03/binder-service-inventory.csv`, SHA-256 `16ab023aa5aedb7123a07ffd4e934d8e7bab7ac2e82a8d1462a82a6391f8b531`). The exact decompiled source used here is `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`, SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`.

Residual candidates that only read settings, dispatch input, or lack a bounded state sink were not promoted. No runtime reachability, live service-manager visibility, package signature, enforcing SELinux decision, or stable Binder transaction integer is inferred.

## CSV validation

Schema matches the 15-column 6VE inventory schema. Parsed row count: **3 data rows** (4 physical lines including the header). All rows have 15 fields; IDs are unique (`WG-001` through `WG-003`).
