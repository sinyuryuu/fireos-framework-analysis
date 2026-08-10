# Phase 10 — broad privilege-control closure

Generated UTC: `2026-08-10T08:26:44.845919+00:00`

## Safety

Worker analyses are host-only. The only device activity in this phase was a serial-bound read-only baseline: no Binder transaction, package/settings mutation, driver open/ioctl, OTA/recovery execution, reboot, root, exploit, or partition write.

Acceptance rule: `caller → gate → Binder identity → user scope → exact sink → observed effect`. Missing edges remain UNKNOWN.

Combined ledger rows: **381**; unique IDs: **381**. New Phase 10 rows: **40**.

| New surface | Rows |
|---|---:|
| AmazonPackageManager/package-state closure | 10 |
| DevicePolicy/Profile IPC closure | 8 |
| MTK/Amazon driver caller closure | 10 |
| OTA post-install/update closure | 12 |

## Current device baseline

Raw capture: `/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/findings/phase-10-readonly-baseline.md`. The saved PS7331 fingerprint is `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`; SELinux is Enforcing; current user is 0; User 0 HOME resolves to `com.amazon.firelauncher/.Launcher` at priority 50. The capture manifest is independently hash-verified.

## Findings

- AmazonPackageManager metadata mutators retain a signature-level `ADD_RM_PKG_METADATA` gate and no joined ordinary caller. KFT package-state writers remain child/profile scoped through `UserInfo.id`; no User-0 writer was found.
- DevicePolicy/Profile and remaining system-service paths must be read as trusted lifecycle or policy surfaces until their external caller, owner/admin gate, and target-user join is recovered. A missing method-local UID check alone is not a usable route.
- OTA/update-binary artifacts expose privileged recovery-time sinks, but the fixed release OTA, verifier handoff, product/version gates, and absent external recovery caller do not establish an untrusted arbitrary-write path. Malformed/symlink/OTA execution was not performed.
- Driver candidates remain UNKNOWN unless the final node, mode/SELinux policy, shipped native caller, input boundary, and sensitive effect all join. No device node was opened.

## Verdict

Phase 10 adds evidence across non-Launcher privilege surfaces but does not establish a reproducible ordinary-App or shell path to disable Fire Launcher, replace User-0 HOME, obtain UID 0, or write a protected partition. Existing rootless foreground redirect behavior remains the closest workaround; it is not formal HOME replacement.

## Reproduction

Run `python3 tools/scripts/build_phase10_surface.py --dry-run` and then `--force` after all four worker CSVs are present. No device is required for the host-side bundle.
