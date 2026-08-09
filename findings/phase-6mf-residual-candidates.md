# Phase 6MF — residual candidate disposition

Date: 2026-08-10
Scope: host-only review of the existing PS7331 corpus after Phase 6ME.

No ADB command, network request, Binder transaction, `service call`, ioctl,
OTA/recovery operation, reboot, package mutation, Fire Launcher mutation, or
partition write was performed in this review. Phase 3A–6ME experiments were
not repeated.

## Candidate status

| ID | Candidate | Disposition | Reason |
|---|---|---|---|
| R1 | `PackageHelper.setComponentEnabledSetting()` user scope and `BootAfterSystemOTAReceiver` → OOBE helper data flow | **待驗證；因風險拒絕 live 驗證** | The preserved JADX shows no explicit user argument, but the client-side `PackageManager` user mapping is not in the bounded source set. The receiver is guarded by the system OTA/OOBE lifecycle. |
| R2 | Runtime-loaded `fosinit` callback/manifest completeness | **已由目前 corpus audit 收斂；無新具體 writer** | The full PS7331 image audit covered 123 `*_fosinit.xml` registrations and correlated relevant callback implementations. No new User-0 HOME, preferred-activity, Fire component-state, or package-state sink was found. |
| R3 | Exact `PackageManagerDenyList` membership for `com.amazon.firelauncher` | **待驗證；因風險拒絕直接取得內容** | Existing evidence proves the protected-package rejection path and the shell caller boundary, but the system-owned deny-list entry itself is not available in the preserved shell-readable evidence. This is provenance only, not a new writer or bypass. |

## Closed or non-repeating routes

- KFT `enableKftLauncherComponent(UserInfo)` remains a child/profile-scoped
  writer. Its supplied `UserInfo.id` is not evidence of a User-0 HOME writer.
- Product Policy has an internal enable/disable action, but the exact PS7331
  policy inputs contain no `com.amazon.firelauncher` entry and the service
  publishes a local system-server service rather than a shell-facing Binder
  endpoint. See `findings/phase-6ce-product-policy-firelauncher-boundary.md`.
- The standard PMS shell path, preferred HOME/DPM path, AppCompat/Eve resolver
  callbacks, ordinary prewarm, and private-service reachability were already
  closed in prior phases. They were not re-run.
- OTA/updater/recovery, manual OOBE activation, unknown Binder transactions,
  Fire package state changes, driver ioctl/DMA/race testing, Root, and
  partition writes remain out of scope and were rejected.

## Next smallest safe question

The only useful remaining host-only question in this branch is the exact user
mapping of the OOBE helper's `ContentResolver` and `PackageManager` calls. It
must be answered from the matching framework client implementation and
context construction; the `FG` method suffix is not sufficient evidence for
User 0. No live OOBE trigger is justified by the current evidence.

## Evidence

- `work/luna_worker_phase6mf_residual_candidates_20260810.md` — worker
  inventory, SHA-256 `13878d2dab921f4a838b6e37c5d457bf3e25610824e0e51d5a84f93fa008d11b`.
- `findings/phase-6n-oobe-helper-analysis.md` — corrected phase-550 and
  OOBE lifecycle analysis.
- `findings/phase-6jd-fosinit-registration-audit-closure.md` — full 123-file
  registration audit.
- `findings/phase-6ce-product-policy-firelauncher-boundary.md` — exact
  Product Policy input and local-service boundary.
