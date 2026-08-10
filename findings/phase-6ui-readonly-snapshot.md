# Phase 6UI read-only device snapshot

This redacted summary was generated from a serial-bound read-only ADB capture.
The raw snapshot remains local because settings, service and package dumps may contain
device-specific or account-related values.

Snapshot manifest SHA-256: `a8b9dae5887672c5f937e38662331f9f45da414b02bbc04c6cb2086317907195`
Raw snapshot (local): `/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/adb/phase6ui/PHASE6UI-DEVICE-READONLY-20260810-01`

## Safety

Only getprop, read-only dumpsys, resolver queries, package/user/service/overlay lists,
and settings list commands were used. No package, component, preferred activity, setting,
user, Binder, driver, OTA, reboot, or partition state was changed.

## Selected results

| Field | Value | Classification |
|---|---|---|
| `model` | `KFTRWI` | Confirmed |
| `device` | `trona` | Confirmed |
| `build_fingerprint` | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` | Confirmed |
| `build_incremental` | `0031575863172` | Confirmed |
| `android_release` | `9` | Confirmed |
| `android_sdk` | `28` | Confirmed |
| `security_patch` | `2024-08-01` | Confirmed |
| `verified_boot_state` | `green` | Confirmed |
| `selinux` | `Enforcing` | Confirmed |
| `home_resolve` | `priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true` | Confirmed |
| `home_priority` | `50` | Confirmed |
| `home_candidate_count` | `3` | Confirmed |
| `fire_home_candidate` | `yes` | Confirmed |
| `resumed_activity` | `com.amazon.firelauncher/.Launcher` | Observed |
| `current_focus` | `com.amazon.firelauncher/com.amazon.firelauncher.Launcher` | Observed |
| `fire_user0_state_line` | `User 0: ceDataInode=852182 installed=true hidden=false suspended=false stopped=false notLaunched=false enabled=0 instant=false virtual=false` | Observed |
| `user_count` | `2` | Confirmed |

The complete command list, raw outputs, return codes and per-file hashes remain in the
local snapshot directory. This summary does not claim that a visible service or static
sink is reachable by shell or an ordinary application.
