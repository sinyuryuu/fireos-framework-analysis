# Phase 7 — broad privilege and system-control route audit

Generated UTC: `2026-08-10T07:38:11.136185+00:00`

## Scope and safety

This phase broadens the search beyond Launcher to Amazon IPC, OTA/source provenance, kernel/driver surfaces, package-state/watchdog paths, and previously measured runtime workarounds. The source/IPC/kernel/watchdog audits are host-only; the device evidence is a serial-bound read-only baseline. No exploit, root attempt, unknown Binder/service transaction, driver open/ioctl, updater/recovery execution, package/settings mutation, reboot, remount, or partition write was performed in this phase.

Every candidate is evaluated as `caller → gate → Binder identity → user scope → exact sink → observed effect`. Static source capability, an exported component, a permission declaration, a native writer, or an address/string hit is not treated as a privilege transition without the missing edges.

## Evidence counts

- Combined ledger rows: **276**; unique IDs: **276**.
- Prior public Phase 6X4 rows: **212**.
- New Phase 7 rows: **64**.
- Input manifest: `output/tables/phase7-input-manifest.sha256`.

| Phase | Rows |
|---|---:|
| 6WL | 48 |
| 6X-IPC | 3 |
| 6X-LIVE | 6 |
| 6X-OTA | 4 |
| 6X2 | 48 |
| 6X3 | 56 |
| 6X4 | 30 |
| 6XG-GPL | 5 |
| 6Y-PERM | 4 |
| 6Z-COMPONENT | 8 |
| 7 | 64 |

| New surface | Rows |
|---|---:|
| 7.3.3.1 source/installer scope | 8 |
| AUXADC ioctl/sysfs | 1 |
| Amazon DSP debugfs | 1 |
| Amazon Framework/System Services IPC | 15 |
| Amazon driver test proc | 1 |
| Amazon liquid-detection sysfs | 1 |
| Amazon package-state/HOME watchdog | 8 |
| CMDQ/MDP | 1 |
| ION MediaTek custom | 1 |
| ION generic | 1 |
| Input evdev | 1 |
| M4U ioctl/proc | 1 |
| MediaTek performance ioctl | 1 |
| PMIC debugfs/sysfs | 1 |
| RPMB char ABI | 1 |
| Thermal writable sysfs | 1 |
| USB devio | 1 |
| existing runtime/workaround reconciliation | 18 |
| uinput | 1 |

## Current read-only device baseline

The serial-bound capture `adb/phase7/PHASE7-BASELINE-20260810-01/` reports PS7331.4463N, SELinux Enforcing, User 0 current, User 0 HOME `com.amazon.firelauncher/.Launcher` at priority 50, Microsoft at 0, and Settings FallbackHome at -1000. User 10 resolves FallbackHome in this snapshot. The capture contains original stdout/stderr, metadata, and a verified SHA-256 manifest; it is not a vulnerability result.

## Findings

- **7A source/installer provenance — status follows the worker evidence:** the official 7.3.3.1 source/package scope is recorded without executing an updater or constructing an OTA. Absence from a bounded archive listing is only a bounded negative; build provenance and signed-image equivalence remain separate questions.
- **7B IPC — residual edges, no completed low-privilege chain:** 15 routes retain a small set of unknown caller/user-validation joins (prewarm, KFT tx3, DPM→PMS, SettingsProvider caller, DCPMS bind). The remainder are duplicate or bounded-negative. No route establishes an ordinary App/shell caller reaching User-0 Fire package/HOME state.
- **7C kernel/driver — capability without reachability:** 15 user-facing surfaces retain UNKNOWN for at least one final shipped object/node policy/caller-domain join. No driver or kernel runtime was touched, and no route establishes a package/HOME/UID-0 sink.
- **7D runtime/workarounds — confirmed scope:** User 0 formal HOME remains Fire. Accessibility and ADB monitor behavior are foreground redirects only; Accessibility HOME consumption failed 0/3. Child/Tahoe HOME is per-user and does not replace User 0.
- **7E watchdog/config — no new User-0 writer:** the only new Fire-targeted literal is a package-scoped external-app availability notification. KFT child writers, deny-list resource/property reads, and LauncherHijackPreventer callbacks do not close a Fire User-0 HOME/package-state writer.

## Main verdict

The expanded evidence still does not establish a reproducible ordinary-App or shell route to disable Fire Launcher, replace User-0 HOME, obtain UID 0, or write a protected partition. The best verified rootless behavior remains a foreground redirect that is not a formal HOME replacement. The remaining unknowns are provenance/authorization joins, not a demonstrated exploit. Running unknown Binder payloads, driver ioctls, malformed OTA packages, or root exploits would add device risk without closing those missing edges and is rejected.

## Next smallest evidence targets

1. Host-only recover the exact production bind client and permission/grant path for prewarm, DCPMS, H2, and SettingsProvider; do not call the services.
2. Host-only map final DTB/ueventd/file_contexts/TE allow and shipped native caller for the highest-value driver surfaces; do not open nodes.
3. If a future authorized test is needed, perform only the existing read-only HOME/package/accessibility foreground guard; do not repeat closed disable/priority/DPM/Accessibility-consume tests.

## Reproduction

Use `python3 tools/scripts/build_phase7_surface.py --dry-run` to verify inputs and `--force` to regenerate the host-only bundle. The device baseline was captured with `tools/scripts/capture_phase6ee_current_baseline.py --serial G001LT0511550CFT --output adb/phase7/PHASE7-BASELINE-20260810-01`; its per-file manifest was verified inside the capture directory.

## Explicitly not claimed

This phase does not claim that every kernel driver, Amazon service, permission, or updater path is safe, nor that no future vulnerability exists. It records only joined evidence and preserves every unresolved edge as UNKNOWN.
