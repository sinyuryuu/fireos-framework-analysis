# Phase 6X4 — privilege-surface closure and residual route audit

Generated UTC: `2026-08-10T07:25:59.669752+00:00`

## Scope and safety

This phase adds four host-only closure audits to the public Phase 6X3 ledger. No worker executed an ADB command, private Binder transaction, service-call payload, driver open/ioctl, OTA/recovery updater, exploit/root attempt, package mutation, reboot, remount, or partition write.

The acceptance rule remains `caller → gate → Binder identity → user scope → exact sink → observed effect`. A capability, exported component, permission declaration, local system-server service, or native writer is not treated as an elevation path until every relevant edge is joined.

The raw permission-consumer CSV is preserved byte-for-byte as an input. Three rows do not match its declared CSV header; the generator reconciles only the unambiguous fields, marks those rows in `scope`, and leaves missing caller/scope/status data explicitly unknown rather than silently shifting columns.

## Evidence counts

- Combined ledger rows: **212**; unique IDs: **212**.
- Prior public Phase 6X3 rows: **182**.
- New Phase 6X4 rows: **30**.
- Input manifest: `output/tables/phase6x4-input-manifest.sha256`.

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

| New surface | Rows |
|---|---:|
| OOBE/prewarm user-scope closure | 3 |
| OTA indirect/update closure | 8 |
| ProductPolicy/DCPMS closure | 7 |
| permission consumer/holder closure | 12 |

## New closure conclusions

- **ProductPolicy/DCPMS — 已證實的邊界:** `productpolicyservice_fosinit.xml` loads Amazon ProductPolicy into system_server as a local service; the recovered `onStart` publishes a local service, not an external Binder service. Its trusted component/application setters are internal event/user/profile sinks and do not contain a Fire Launcher, HOME, or User-0 restoration edge. The separate beta-build factory-reset branch is trusted boot policy and was not executed.
- **OOBE/prewarm user scope — 待驗證:** OOBE receivers inherit a lifecycle `Context` without a recovered numeric `UserHandle`; the prewarm contract carries an explicit integer user argument and calls package/process APIs after `clearCallingIdentity`, but the saved slice does not prove the caller, cross-user validation, or a User-0/User-10 target. This is a scope gap, not a shell bypass.
- **Permission consumer/holder — 高可信靜態邊界:** normal/dangerous/custom Amazon permission declarations do not close a requester → grant → exported consumer → method check → sensitive sink chain. The separate H2 service has an exported signature|amazon surface and a profile/user-creation sink, but no recovered edge to HOME, package/component state, or UID 0; actual bind caller remains unknown.
- **OTA indirect/update — 已證實的能力邊界:** the saved native graph closes cache-size error handling, indirect registries, fixed updater-script arguments, and the signed-recovery writer chain. It does not close untrusted input control, AVB/rollback verifier handoff, canonicalization-to-writer control, or low-privilege reachability. No updater or recovery runtime was run.

## Main verdict

Phase 6X4 adds useful exclusions and explicitly bounded unknowns, but no new evidence establishes an ordinary-app or shell route to User-0 package-state mutation, formal HOME replacement, UID 0, or partition writing. The ProductPolicy external-Binder hypothesis is rejected for the recovered build; the trusted local setter is not an externally callable confused deputy. H2 and prewarm remain static follow-up surfaces only until their real caller and user-scope edges are recovered.

The correct next step is further host-only artifact closure (exact requester/bind client, SELinux/service publication, and native verifier handoff), not a risky payload. A driver ioctl, updater execution, unknown Binder transaction, Fire Launcher mutation, or root attempt would add risk without repairing the missing evidence edges and is therefore rejected.

## Explicitly not claimed

This report does not claim that every Amazon service, permission, driver, or updater path is safe, and it does not claim that no future vulnerability exists. It records only the evidence actually joined in the preserved artifacts and identifies the minimum missing edge for each residual route.

## Reproduction

Use `python3 tools/scripts/build_phase6x4_surface.py --dry-run` to verify all inputs, then `--force` to regenerate the host-only outputs. The four raw worker CSV/Markdown files are included as separate evidence inputs; no device access is required.
