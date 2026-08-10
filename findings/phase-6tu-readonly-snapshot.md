# Phase 6TU read-only device snapshot

This is a redacted summary. The raw snapshot remains local because settings and service output may contain account- or device-specific data.

## Safety

The capture used only `getprop`, `dumpsys`, `cmd package` query/resolve, `pm list users`, `service list`, `cmd overlay list`, and settings list commands. No package, component, preferred activity, setting, user, Binder, driver, OTA, reboot, or partition state was changed.

## Observed state

- **model:** `KFTRWI`
- **device:** `trona`
- **build_fingerprint:** `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- **build_incremental:** `0031575863172`
- **android_release:** `9`
- **android_sdk:** `28`
- **security_patch:** `2024-08-01`
- **verified_boot_state:** `green`
- **selinux:** `Enforcing`
- **home_resolve:** `priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true`
- **home_candidates_fire:** `yes`
- **user_list:** `UserInfo{REDACTED} running; UserInfo{REDACTED}`

`home_resolve` is the complete first line of the resolver output; the raw candidate and preferred dumps remain in the local snapshot. The table records SHA-256 for each selected raw evidence file.
