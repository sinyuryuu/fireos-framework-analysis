# Phase 10 read-only device baseline

## Capture

- Test ID: `PHASE10-BASELINE-20260810-01`
- Serial: `G001LT0511550CFT`
- Capture directory: `adb/phase10/PHASE10-BASELINE-20260810-01/`
- Collection script: `tools/scripts/capture_phase6ee_current_baseline.py`
- Commands: 16 read-only ADB commands
- Binder transaction: not performed
- Package/settings mutation: not performed
- Reboot/OTA/kernel/driver operation: not performed
- Per-file SHA-256 manifest: `5978a74ee80c167dcd9aa65e28f2748cb240f1c2319dedc56e17bf0abda6fcb3`

## Observed state

- Build fingerprint: `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- Current user: `0`
- SELinux: `Enforcing`
- User 0 HOME resolver: `com.amazon.firelauncher/.Launcher`
- Fire Launcher resolver priority: `50`
- User 10 HOME result: preserved in the raw capture; no user switch was performed.

## Evidence interpretation

**Confirmed:** the device was connected and in the expected PS7331 build state at
capture time; User 0 still resolves HOME to Fire Launcher.

**Not tested:** no new permission path, Binder route, package state mutation,
driver interface, OTA operation, or root/exploit behavior was exercised by this
baseline.
