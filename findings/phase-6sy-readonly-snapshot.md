# Phase 6SY read-only device snapshot

This is a redacted summary generated from a serial-bound, read-only ADB snapshot.
The raw directory is intentionally not included in the public commit because its
settings dumps may contain account-related values.

Snapshot manifest (`sha256sums.txt`) SHA-256: `fb1bfd362128ea2a641076fe6ffeb8b60e94fe096365f7672fb0e55c982bc00f`
Raw snapshot directory (local): `adb/phase6sy/PHASE6SY-DEVICE-READONLY-20260810-01`

## Safety and provenance

Only getprop, read-only dumpsys, resolver queries, package/user/service/overlay
lists, and settings list commands were captured. No package, settings, Binder,
driver, OTA, recovery, reboot, or partition mutation was performed.

## Selected results

| Field | Value | Classification |
|---|---|---|
| `product_model` | `KFTRWI` | Confirmed |
| `product_device` | `trona` | Confirmed |
| `build_fingerprint` | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` | Confirmed |
| `security_patch` | `2024-08-01` | Confirmed |
| `verified_boot_state` | `green` | Confirmed |
| `home_resolved_component` | `com.amazon.firelauncher/.Launcher` | Confirmed |
| `home_resolved_priority` | `50` | Confirmed |
| `fire_activity_resumed` | `com.amazon.firelauncher/.Launcher` | Confirmed |
| `current_focus` | `com.amazon.firelauncher/com.amazon.firelauncher.Launcher` | Confirmed |
| `fire_user0_enabled_state` | `0` | Confirmed |
| `fire_activity_info_enabled` | `true` | Confirmed |
| `user_count` | `2` | Confirmed |

`fire_user0_enabled_state=0` is the PackageManager default state, not a claim
that the package is disabled; the HOME candidate and ActivityInfo remain enabled
and the resolver still selects Fire Launcher.

The full command list, raw outputs, return codes, and per-file hashes remain in
the local snapshot directory.
