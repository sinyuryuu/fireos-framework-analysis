# Phase 7 read-only device baseline

## Capture

- Test directory: `adb/phase7/PHASE7-BASELINE-20260810-01/`
- Serial: `G001LT0511550CFT`
- Capture script: `tools/scripts/capture_phase6ee_current_baseline.py`
- Device command count: 16
- Device mutation: none
- Binder transaction: none
- Package/settings mutation: none
- Reboot/OTA/kernel/driver operation: none
- SHA-256 manifest: `adb/phase7/PHASE7-BASELINE-20260810-01/sha256sums.txt`
- Manifest SHA-256: `7cdb9f573a0d1a371e0e4a78bc7ed30d5f4b2c17cef98e91164a137628fe5959`

The manifest was verified from inside the capture directory with `shasum -a
256 -c sha256sums.txt`; all listed files passed.

## Observed state

- ADB state: `device`
- Build fingerprint: `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- Current user: `0`
- Users: User 0 `sinyu` running; User 10 `test` present but not running in this capture.
- SELinux: `Enforcing`
- User 0 HOME: `com.amazon.firelauncher/.Launcher`, priority `50`, match `0x108000`, `isDefault=true`.
- User 0 candidates: Fire Launcher priority `50`; Microsoft Launcher priority `0`; Settings FallbackHome priority `-1000`.
- User 10 HOME: Settings FallbackHome priority `-1000` in this snapshot.

## Reproduction

```sh
python3 tools/scripts/capture_phase6ee_current_baseline.py \
  --serial G001LT0511550CFT \
  --output adb/phase7/PHASE7-BASELINE-20260810-01
```

The output directory is append-free and contains the original stdout/stderr,
metadata, and per-file hashes. It is not evidence of a vulnerability; it is
the Phase 7 before-state for any later, separately approved low-risk test.
