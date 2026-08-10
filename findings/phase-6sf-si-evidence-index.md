# Phase 6SF–SI evidence index

日期：2026-08-10（Asia/Taipei）
基準：公開 `1214e6f1564422cf411e57305b5acc727ababb66` 及其保存的 Phase 6SE 唯讀快照。
範圍：主機端、既有 artifact 的靜態 provenance、CSV schema/hash 驗證；本輪沒有新的裝置操作。

## Safety boundary

本輪沒有執行 root exploit、kernel race、private Binder transaction、`service call`
payload、device-node `open`/`ioctl`、proc write、OTA/recovery/update-binary、sideload、
reboot、partition write、remount、SELinux 修改、package state mutation 或 Fire Launcher
停用/清除。所有 `UNKNOWN` 是證據範圍界線，不是「不存在」的全域證明。

## Device evidence reused

| Evidence ID | Source | File | SHA-256 | Observed result | Confidence |
|---|---|---|---|---|---|
| 6SE-DEVICE-READONLY-20260810-01 | exact serial readonly snapshot | `adb/phase6se/PHASE6SE-DEVICE-READONLY-20260810-01/metadata.json` | `9749f073aed3f562b47c83396d9cf820dcf62fbd5dbb792b8739a7b698c857a2` | `G001LT0511550CFT`, PS7331.4463N, `KFTRWI`/`trona`, Android 9/API 28, SELinux Enforcing; all mutation and Binder/node flags false | Confirmed |
| 6SE-HOME-001 | same snapshot | `adb/phase6se/PHASE6SE-DEVICE-READONLY-20260810-01/home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | HOME resolves to `com.amazon.firelauncher/.Launcher`, priority 50 | Confirmed |
| 6SE-PREFERRED-001 | same snapshot | `adb/phase6se/PHASE6SE-DEVICE-READONLY-20260810-01/preferred.stdout.txt` | `ab4c4d71d54faa5b5339dda54f4e3cc14c95a671e71ef1640627adf4c0e2e519` | User 0 preferred record is Fire Launcher, `mMatch=0x100000`, `mAlways=true`; selected set includes Fire/Microsoft/FallbackHome | Confirmed |

## New worker inputs

| Evidence IDs | Source file | SHA-256 | Rows | Scope |
|---|---|---:|---:|---|
| 6SF-001–6SF-020 | `work/luna_worker_phase6sf_permission_20260810.csv` | `54b04cd3c4aad132e68fac2d1da38bee6ca4bd6a3c43933d23ae8aeadeb848c9` | 20 | exact-build permission declaration, protection, holder/grant/caller boundary, metadata sink |
| 6SG-001–6SG-011 | `work/luna_worker_phase6sg_driver_join_20260810.csv` | `6cb000e68c9391a2b954966944a41facb31d9c6fed8372c07b8fb4ce07441111` | 11 | source/config → shipped node/policy → exact native caller joins |
| 6SH-001–6SH-010, HASH-001–HASH-005 | `work/luna_worker_phase6sh_recovery_20260810.csv` | `83ec5205faf95a78c38a0815e20990b23e15b2118ae02e27443f2c805d423ee3` | 15 | OTA/recovery verifier, staging, updater and post-OTA lifecycle provenance |
| P5-* / P6-* | `work/luna_worker_phase6si_test_catalog_20260810.csv` | `6af20b17073491917f9d334af0b2536d7f6de66f58ffebfdfe8772b1c561be8c` | 20 | existing test-family catalog and repeat/rejection classification |

The worker narratives are preserved beside their CSV companions:

- `work/luna_worker_phase6sf_permission_20260810.md` — SHA-256 `73dcbead028dfd009c0337d19207bbd64b4d7f0b5ae52d9582ece98e53b219fc`
- `work/luna_worker_phase6sg_driver_join_20260810.md` — SHA-256 `cbe1cb22130cb5313c9bf4bb788ced2642140943753089cf5792cd87734994f9`
- `work/luna_worker_phase6sh_recovery_20260810.md` — SHA-256 `fba0e4a1c7788043e9e7839ec6b9d60aebdde6c65048691f897fff51e0bb08a1`
- `work/luna_worker_phase6si_test_catalog_20260810.md` — SHA-256 `ef2deede4ec9203261d71883b042c5808adb6e47f69e3c00e40656d1ce3ca69a`

## Material evidence

### 6SF — exact permission provenance

- **6SF-001, 6SF-002 — Confirmed / High:** exact-build XML declares
  `amazon.permission.ADD_RM_PKG_METADATA` under `android.amazon.perm`; raw
  `protectionLevel=0x80000002`, decoded as `signature|privileged` by the Android bit
  convention. Source: `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`,
  SHA-256 `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`.
- **6SF-003–6SF-009 — Bounded not found / Medium–High:** exact custom grant/holder,
  requested/granted package join, service-level permission and production caller are not
  closed by the preserved corpus. This corrects the stale older note that the declaration
  itself was absent; it does not establish a holder or caller.
- **6SF-010–6SF-020 — Confirmed static sink plus bounded linkage:** the method-level check
  and `AmazonApplicationFlags`/`amazon_package_flags.xml` metadata writer are present;
  no bounded `ADD_RM_PKG_METADATA → HOME/preferred/component-state` edge was found.
  HOME-related permission declarations are reception/declaration facts, not mutation proof.

### 6SG — driver/source-to-client join

- **6SG-001–6SG-011 — UNKNOWN:** no target closes all four required segments:
  source/config, shipped owner/mode, file-context/TE allow, and exact native
  `open`/`ioctl` or proc writer caller. Policy allow, source capability, symbols, HAL
  presence or an adjacent init rule are not promoted to reachability.
- No driver node was opened and no ioctl/proc write was sent. The complete per-target
  evidence and confidence distinction remain in the worker CSV/MD.

### 6SH — OTA/recovery provenance

- **6SH-001 — Confirmed Java-side caller / native verifier UNKNOWN:**
  `SideloadVerifier.verifySideloadPackage()` → `RecoverySystemWrapper.verifyPackage()` →
  `android.os.RecoverySystem.verifyPackage()`.
- **6SH-002 — Confirmed handoff:** `SideloadInstaller` → `SideloadMover` →
  `UpdateSystemWrapper` → `UpdateSystem.install`.
- **6SH-003–6SH-006 — Confirmed implementation shape, security outcome UNKNOWN:** basename
  staging, `renameTo` and buffered copy/delete fallback are observed; no dynamic malformed
  path, symlink, traversal or archive test was performed.
- **6SH-007–6SH-010 — Confirmed protected lifecycle / low-privilege route not established:**
  `BOOT_AFTER_SYSTEM_OTA` system-server lifecycle and OOBE predicates exist, but this is
  not a HOME writer and no ordinary-app/shell sender chain is present in the bounded corpus.
- **HASH-001–HASH-005 — provenance only:** hashes do not establish exploitability or caller
  reachability.

### 6SI — test catalog

- **P6-KFT-CHILD-01, P6-KFT-SERVICE-01, P6-PMS-HOME-01 and P6-HOME-REGRESSION-01 —
  existing evidence:** KFT child writer is child-scoped; ordinary User 0/PMS HOME routes
  are blocked or redundant. Do not repeat without a changed user, build, policy or artifact
  premise.
- **P6-DRIVER-01, P6-OTA-OOBE-01, P6-UPDATER-01 — evidence insufficient/rejected:**
  capability and protected sinks exist, but no low-privilege caller/payload proof.
- **P6-ACCESS-REDIRECT-01 — bounded fallback:** foreground/accessibility redirect is not
  formal HOME replacement and should not be reported as one.
- The remaining P5/P6 rows are catalog classifications, not new runtime observations.

## Normalized output

`output/tables/phase6sf-si-control-surface.csv` contains 66 normalized rows (20 + 11 +
15 + 20) with the same 14-column shape used by the earlier control-surface ledger. The
generator and input/output hashes are recorded in:
`output/tables/phase6sf-si-input-manifest.sha256`.
