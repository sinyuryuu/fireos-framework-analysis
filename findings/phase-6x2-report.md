# Phase 6X2 — broad privilege surface continuation

Generated UTC: `2026-08-10T07:05:08.025903+00:00`

## Scope and safety

This is a host-only synthesis of the prior public Phase 6X ledger and four disjoint residual audits. It does not contact a device, execute an OTA, call a private Binder transaction, open a driver node, run an exploit, mutate Fire Launcher, reboot, or write a partition.

The acceptance rule remains `caller → gate → identity/user scope → exact sink → observed effect`. A capability, declaration, exported component, or source-level writer without that chain is not an elevation finding.

## Evidence inventory

- Combined rows: **126** (including the prior Phase 6X corpus).
- New worker inputs: `work/luna_worker_phase6aa_ipc_residual_20260810.csv`, `work/luna_worker_phase6ab_ota_exact_20260810.csv`, `work/luna_worker_phase6ac_accessibility_review_20260810.csv`, `work/luna_worker_phase6ad_untested_routes_20260810.csv`, `work/luna_worker_phase6aa_ipc_residual_20260810.md`, `work/luna_worker_phase6ab_ota_exact_20260810.md`, `work/luna_worker_phase6ac_accessibility_review_20260810.md`, `work/luna_worker_phase6ad_untested_routes_20260810.md`, `adb/phase6x2/PHASE6X2-DEVICE-READONLY-20260810-01/metadata.txt`, `adb/phase6x2/PHASE6X2-DEVICE-READONLY-20260810-01/getprop.stdout.txt`, `adb/phase6x2/PHASE6X2-DEVICE-READONLY-20260810-01/home_resolve.stdout.txt`, `adb/phase6x2/PHASE6X2-DEVICE-READONLY-20260810-01/home_candidates.stdout.txt`, `adb/phase6x2/PHASE6X2-DEVICE-READONLY-20260810-01/preferred_xml.stdout.txt`, `adb/phase6x2/PHASE6X2-DEVICE-READONLY-20260810-01/firelauncher_package.stdout.txt`, `adb/phase6x2/PHASE6X2-DEVICE-READONLY-20260810-01/sha256sums.txt`
- Prior corpus: `output/tables/phase6x-control-surface.csv`.
- Fresh exact-serial read-only capture: `adb/phase6x2/PHASE6X2-DEVICE-READONLY-20260810-01`

| Surface | Rows |
|---|---:|
| 6WF live ProductPolicy | 5 |
| 6WG Framework IPC residual | 3 |
| 6WH OTA residual | 6 |
| 6WI native driver caller | 7 |
| 6WJ test reconciliation | 10 |
| 6WK broad surface | 17 |
| ADB-connected host foreground monitor | 1 |
| Accessibility consume/key-event path | 1 |
| Accessibility timeout 50 ms A/B | 1 |
| AmazonActivityManager preWarmApplicationForUser -> identity/user propagation -> process/state sink | 1 |
| DCPMS exported lifecycle receiver -> producer/permission -> profile-policy sink | 1 |
| Fire Launcher per-user state | 1 |
| HOME User 0 | 1 |
| HOME candidates User 0 | 1 |
| HOME candidates User 10 | 1 |
| IAmazonKeyguardService.dismissWithPendingIntent (Stub method; Proxy method; tx UNKNOWN) | 1 |
| IAmazonKeyguardService.setAccessibilityInfo (Stub method; Proxy method; tx UNKNOWN) | 1 |
| IAmazonKeyguardService.setForegroundColor (Stub method; Proxy method; tx UNKNOWN) | 1 |
| IPC | 8 |
| Microsoft retry Accessibility 350/1000/1800 ms | 1 |
| OOBE receiver -> exact numeric user -> setup/component sink | 1 |
| OOBE-OTA-receiver | 1 |
| OOBE-settings | 1 |
| OTA | 23 |
| OTA verifier/canonicalization -> indirect extraction/write sink | 1 |
| Original Phase 4 Accessibility direct redirect | 1 |
| PendingIntent GUI consent boundary | 1 |
| ProductPolicy fosinit registration -> Binder publication -> caller gate | 1 |
| ProductPolicy-system-server-init | 1 |
| RPMB char device precise negative | 1 |
| Reboot plus owner unlock Accessibility retry | 1 |
| Settings-HOME-resource-and-PMS-state | 1 |
| Transparent resident assist candidate | 1 |
| USE_SDK / PLUGIN / PLUGIN_CONSUMER declaration -> consumer/holder/grant -> sensitive sink | 1 |
| Unlock workaround / keyguard bypass | 1 |
| UsageStats public third-party route | 1 |
| User 0 MAIN+HOME resolver | 1 |
| device identity | 1 |
| exported-permissioned-receiver | 2 |
| exported-protected-action-receiver | 1 |
| exported-receiver | 1 |
| host extraction provenance | 1 |
| input/uinput | 1 |
| permission-definition | 4 |
| post-install/native updater/recovery | 1 |
| power-supply sysfs | 1 |
| preferred HOME record | 1 |
| temporary path/symlink/canonicalization | 1 |
| uinput native/SELinux caller join negative | 1 |
| vendor/mediatek archive path | 1 |
| version/provenance | 1 |

## Classification rules

- **已證實** is reserved for a directly observed, reproducible effect or a complete static authorization/sink chain.
- **高可信推論** means the static path is coherent but a required runtime edge remains open.
- **待驗證** records a missing caller, publication, SELinux/service-manager rule, numeric user scope, or downstream writer.
- **已排除** records a negative result within a stated bounded search; it is not a universal absence claim.
- **因風險拒絕測試** covers OTA/recovery execution, unknown Binder payloads, driver ioctls, exploit attempts, and destructive package/partition operations.

## New residual audit summary

- `6X2-IPC-001` — **IPC** — POSITIVE sink and gate; NEGATIVE for HOME/package/OTA (UNKNOWN).
- `6X2-IPC-002` — **IPC** — POSITIVE (UNKNOWN).
- `6X2-IPC-003` — **IPC** — POSITIVE bounded callback sink; NEGATIVE external Binder reachability (UNKNOWN).
- `6X2-IPC-004` — **IPC** — POSITIVE exported declaration; NEGATIVE complete target sink (UNKNOWN).
- `6X2-IPC-005` — **IPC** — POSITIVE policy sink; NEGATIVE target sink (UNKNOWN).
- `6X2-IPC-006` — **IPC** — POSITIVE gate markers; NEGATIVE target sink (UNKNOWN).
- `6X2-IPC-007` — **IPC** — POSITIVE workflow sink; NEGATIVE HOME/package sink (UNKNOWN).
- `6X2-IPC-008` — **IPC** — POSITIVE bounded non-HOME sink; NEGATIVE target sink (UNKNOWN).
- `6X2-OTA-001` — **OTA** — Historical README separately marks installed PS7330 mismatch (UNKNOWN).
- `6X2-OTA-002` — **OTA** — Traditional signed BLOCK OTA (UNKNOWN).
- `6X2-OTA-003` — **OTA** — Postinstall executable route is negative for package-shape scope (UNKNOWN).
- `6X2-OTA-004` — **OTA** — Static script gate only (UNKNOWN).
- `6X2-OTA-005` — **OTA** — Transition/downgrade controls are OTASettings gated (UNKNOWN).
- `6X2-OTA-006` — **OTA** — Platform verifier implementation not present in preserved Java (UNKNOWN).
- `6X2-OTA-007` — **OTA** — Call order is exact in source (UNKNOWN).
- `6X2-OTA-008` — **OTA** — No Java canonicalPath realpath lstat or O_NOFOLLOW marker (UNKNOWN).
- `6X2-OTA-009` — **OTA** — WithoutRecoveryCheck branch is not proof of bypass because normal integrity path is separate (UNKNOWN).
- `6X2-OTA-010` — **OTA** — Recovery/native exec caller remains separate boundary (UNKNOWN).
- `6X2-OTA-011` — **OTA** — Holder evidence is privileged/controller capability (UNKNOWN).
- `6X2-OTA-012` — **OTA** — Static registration not execution (UNKNOWN).
- `6X2-OTA-013` — **OTA** — Capability not reachability (UNKNOWN).
- `6X2-OTA-014` — **OTA** — No execution or partition write (UNKNOWN).
- `6X2-OTA-015` — **OTA** — No arbitrary target conclusion (UNKNOWN).
- `6X2-OTA-016` — **OTA** — Callsite is path-related but impact is unknown (UNKNOWN).
- `6X2-OTA-017` — **OTA** — Not binary-wide absence and not traversal proof (UNKNOWN).
- `6X2-OTA-018` — **OTA** — No symlink/traversal test (UNKNOWN).
- `6X2-OTA-019` — **OTA** — Do not infer AVB bypass (UNKNOWN).
- `6X2-OTA-020` — **OTA** — Full cryptographic implementation unknown (UNKNOWN).
- `6X2-OTA-021` — **OTA** — Date/version gates are not equivalent to anti-rollback proof (UNKNOWN).
- `6X2-OTA-022` — **OTA** — Bounded negative not universal absence (UNKNOWN).
- `6X2-OTA-023` — **OTA** — Keep historical mismatch separate from current PS7331 package facts (UNKNOWN).
- `AC-001` — **User 0 MAIN+HOME resolver** — TRUE_HOME_FIRE (confirmed).
- `AC-002` — **Original Phase 4 Accessibility direct redirect** — FAILED_FOREGROUND_REDIRECT (confirmed).
- `AC-003` — **PendingIntent GUI consent boundary** — UNKNOWN_NOT_MEASURED (confirmed-boundary).
- `AC-004` — **Microsoft retry Accessibility 350/1000/1800 ms** — FOREGROUND_REDIRECT (confirmed-but-nondeterministic).
- `AC-005` — **Reboot plus owner unlock Accessibility retry** — UNLOCK_AFTER_REDIRECT (confirmed-foreground-only).
- `AC-006` — **Accessibility timeout 50 ms A/B** — FOREGROUND_REDIRECT_NOT_ADOPTED (confirmed-negative-optimization).
- `AC-007` — **Accessibility consume/key-event path** — FAILED_OR_PARTIAL_FOREGROUND (confirmed-boundary).
- `AC-008` — **UsageStats public third-party route** — UNKNOWN_NOT_VALIDATED (unknown).
- `AC-009` — **ADB-connected host foreground monitor** — FOREGROUND_REDIRECT_CLOSED (confirmed-but-not-approved).
- `AC-010` — **Unlock workaround / keyguard bypass** — UNKNOWN_NOT_A_WORKAROUND (unknown).
- `AC-011` — **Transparent resident assist candidate** — SAFE_FOREGROUND_ASSIST_ONLY (conditional).
- `6X2-ROUTES-001` — **OOBE receiver -> exact numeric user -> setup/component sink** — untested_host_only (UNKNOWN).
- `6X2-ROUTES-002` — **DCPMS exported lifecycle receiver -> producer/permission -> profile-policy sink** — untested_host_only (UNKNOWN).
- `6X2-ROUTES-003` — **ProductPolicy fosinit registration -> Binder publication -> caller gate** — untested_host_only (UNKNOWN).
- `6X2-ROUTES-004` — **AmazonActivityManager preWarmApplicationForUser -> identity/user propagation -> process/state sink** — untested_host_only (UNKNOWN).
- `6X2-ROUTES-005` — **USE_SDK / PLUGIN / PLUGIN_CONSUMER declaration -> consumer/holder/grant -> sensitive sink** — untested_host_only (UNKNOWN).
- `6X2-ROUTES-006` — **OTA verifier/canonicalization -> indirect extraction/write sink** — untested_host_only (UNKNOWN).

## Main conclusion

The broad search remains useful only when it closes a real caller-to-sink chain. On the current evidence, no new ordinary app/shell path has demonstrated User-0 package-state mutation, formal HOME replacement, root identity, or partition effect. Any residual row with UNKNOWN caller/publication/identity/sink must remain a research lead rather than a bypass claim.

The new exact-serial capture records `mutation=false`, `binder_transaction=false`, and `reboot=false`; it is a fresh observation only, not a new mutation experiment.

## Reproduction

All inputs and hashes are listed in `output/tables/phase6x2-input-manifest.sha256`. The generator is host-only and supports `--dry-run`; it refuses to overwrite outputs unless `--force` is supplied.
