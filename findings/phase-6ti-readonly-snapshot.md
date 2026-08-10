# Phase 6TI read-only device snapshot

This is a redacted summary generated from a serial-bound, read-only ADB snapshot.
Raw settings and dumps remain local because they may contain account-related values.

Snapshot manifest (`sha256sums.txt`) SHA-256: `acede526eb2d785fb5cccb049d213ebecfd0329e6e6fc9f9807e577331546145`
Raw snapshot directory (local): `adb/phase6ti/PHASE6TI-DEVICE-READONLY-20260810-01`

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
| `user_count` | `2` | Confirmed |

`fire_user0_enabled_state=0` is PackageManager's default state; it is not a
claim that Fire Launcher is disabled. The resolver and foreground evidence
still select `com.amazon.firelauncher/.Launcher`.

The full command list, raw outputs, return codes, and per-file hashes remain
in the local snapshot directory.
