# Phase 6X3 — broad privilege route continuation

Generated UTC: `2026-08-10T07:13:07.249774+00:00`

## Scope and safety

This phase adds four disjoint host-only audits to the public Phase 6X2 ledger. The four delegated audits performed no device command, private Binder transaction, driver open/ioctl, OTA/recovery execution, exploit/root attempt, package mutation, reboot, remount, or partition write.

The acceptance rule is still `caller → gate → Binder identity → user scope → exact sink → observed effect`. Missing edges are retained as UNKNOWN; they do not become a vulnerability claim.

## Evidence counts

- Combined ledger rows: **182**; unique IDs: **182**.
- Prior Phase 6X2 rows: **126**.
- New Phase 6X3 rows: **56**.
- Input manifest: `output/tables/phase6x3-input-manifest.sha256`.

| Phase | Rows |
|---|---:|
| 6WL | 48 |
| 6X-IPC | 3 |
| 6X-LIVE | 6 |
| 6X-OTA | 4 |
| 6X2 | 48 |
| 6X3 | 56 |
| 6XG-GPL | 5 |
| 6Y-PERM | 4 |
| 6Z-COMPONENT | 8 |

## New audit conclusions

- **IPC residuals — 待驗證/高可信靜態邊界:** eight deduplicated routes retain lifecycle, profile-policy, prewarm, permission-declaration, and OTA staging sinks, but no new ordinary caller-to-User-0 package/HOME/root chain.
- **OTA verifier — 因風險拒絕 runtime:** date/product checks, cache error branches, indirect dispatch, canonicalization markers, and named-writer argument provenance are more precisely mapped; this is not evidence of signature, AVB, rollback, symlink, or shell bypass.
- **Kernel/driver — capability/provenance gap:** eleven rows cover Amazon/MediaTek debug, performance, AUXADC, PMIC, touchscreen, power-supply, uinput, and CMDQ/ION surfaces. Exact shipped object, node policy, caller UID/domain, and package/HOME/root effect remain unjoined.
- **Legacy routes — 已排除/待驗證:** 29 route families confirm that User 0 formal HOME remains Fire; User 10/11 child state and consented foreground assist are scoped alternatives, not a privilege transition.

## Main verdict

No new evidence closes a low-privilege path to User-0 package-state mutation, formal HOME replacement, UID 0, or partition writing. The most useful remaining work is host-only closure of exact service publication/SELinux joins and the six route gaps already identified in Phase 6X2; running risky payloads would not repair the missing provenance and is therefore rejected.

A separate post-synthesis serial-bound read-only check is recorded in `findings/phase-6x3-readonly-check.md`: User 0 still resolves Fire Launcher at priority 50, with Microsoft at 0 and FallbackHome at -1000; Fire's saved User 0 state remains enabled. The check did not mutate package/settings state, call Binder transactions, reboot, or access a driver.

## Explicitly not claimed

This report does not claim that every driver or updater path is safe, that every permission is correctly protected, or that no future vulnerability exists. It records only the evidence that was actually joined and the minimum missing edge for each route.

## Reproduction

Use `python3 tools/scripts/build_phase6x3_surface.py --dry-run` to verify inputs, then `--force` to regenerate the host-only outputs. Raw worker CSV/Markdown files are included as separate evidence inputs.
