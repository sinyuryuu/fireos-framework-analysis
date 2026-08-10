# Phase 6WL — cross-surface residual closure and live policy join

Generation HEAD: `3cf0580d925c98a2006748433f1ba9f2c15efdb0`.

## Scope and safety

This phase continues the non-Launcher review. It integrates 43 new worker rows
from Framework IPC, OTA, native-driver, test-reconciliation and broad-surface
searches, plus five live ProductPolicy observations from the exact serial.
Acceptance remains:

`caller → gate → identity/user scope → exact sink → observed effect`

All worker work was host-only. The live policy capture used only `adb pull`,
`getprop`, `ls`, and hashing. No Binder transaction, guessed private code,
driver/ioctl, OTA/recovery execution, malformed input, reboot, package/settings
mutation, Fire Launcher mutation, Root/exploit attempt, or partition write was
performed.

## Integrated inputs

- **6WG Framework IPC residual:** `work/luna_worker_phase6wg_ipc_residual_20260810.md` (93a0840c4737258ac5c481f3e23a3c00cb7784f3b1489b7f7552c614b851079a); `work/luna_worker_phase6wg_ipc_residual_20260810.csv` (c87c7df3d0f94272b233775646454f5b03f35a19639f277f6da71b9317a26d76); 3 row(s).
- **6WH OTA residual:** `work/luna_worker_phase6wh_ota_residual_20260810.md` (4cd5e96655d50dcbf7f0e9e293af8f7183fa3d0c6eb2e094bd853b2cff7139d2); `work/luna_worker_phase6wh_ota_residual_20260810.csv` (226903b904fe99968ff0842c9345f76249b11b8ac8ab2060c59b5811b5463b70); 6 row(s).
- **6WI native driver caller:** `work/luna_worker_phase6wi_driver_caller_20260810.md` (23065fa5808b5b5ef6d5040ecc151be2a1a931741383891597a03755436eee8a); `work/luna_worker_phase6wi_driver_caller_20260810.csv` (97e7a355e1ffa06de3a94c5eab3ef4fcb288b8a4f65fbe4157a399f6de21884b); 7 row(s).
- **6WJ test reconciliation:** `work/luna_worker_phase6wj_test_reconciliation_20260810.md` (d22944d4d214aae0719eb98bedd734364f6acb99ae4e77f19d9746faf6753aba); `work/luna_worker_phase6wj_test_reconciliation_20260810.csv` (844bbbffa47066e663c65f6fdaced9ea48fc90746fe9be01b39a065332aa8760); 10 row(s).
- **6WK broad surface:** `work/luna_worker_phase6wk_broad_surface_20260810.md` (0f59e466f210a0f09d1aa10ef8859af633490350de09786c4285297cbc4e01c7); `work/luna_worker_phase6wk_broad_surface_20260810.csv` (413bf7a4e9150ea0046fef4d44d8f306b595610a4e8593d3078952f5de762d57); 17 row(s).

Live policy capture: `artifacts/phase6wf-product-policy-readonly-20260810-01` (five observation rows;
the raw files and SHA-256 list are retained).

## Findings

### 已證實：many privileged sinks exist across the system

The new ledgers locate settings writers, user/profile creation and switching
sinks, package hiding/deletion helpers, SettingsProvider operations, OTA native
handler registration and recovery handoff, native driver capabilities, and
Amazon/system-server Binder services. These are capabilities or static sinks;
they do not by themselves establish an external caller or accepted identity.

### 已證實：live ProductPolicy inputs do not name Fire Launcher

`global_policy.xml` is empty. `common_device_policy.xml` contains child-only
Cloud9 browser entries. `multimodal_device_policy.xml` contains adult/child
Paladin/ECS entries. `receiver_filter_policy.xml` contains a Facebook SEND
activity filter. None contains `com.amazon.firelauncher`, a HOME component, or a
User-0 package-state directive.

### 高可信推論：ProductPolicy is not the observed User-0 Fire restoration writer

The exact service has a real enabled-state writer and event dispatch, but the
live policy inputs that were accessible do not supply a Fire Launcher entry.
The `product_policy.xml` path is absent on the live device even though the OTA
file-map lists it; therefore this conclusion is bounded to the captured files.

### 待驗證：remaining artifact and external-caller gaps

The missing product-policy path/layout, OTA recovery/AVB handoff, exact native
ELF caller/policy joins, and private service transaction/caller authorization
remain unresolved. The new IPC rows also show settings sinks guarded by
`DUMP` or Amazon permissions, but exact transaction and SELinux/service-manager
boundaries are not all present. These are host-side closure targets, not a
reason to issue unknown Binder codes or open driver nodes.

### 已排除：new rows do not create a root or formal HOME route

No new row closes an ordinary app or shell caller through authorization and
identity/user scope to User-0 package state, formal HOME, root, or partition
effect. Existing equivalent mutations remain excluded by the 6WJ matrix.

### 因風險拒絕測試

Unknown Binder transactions, native device operations, OTA/recovery execution,
root/exploit payloads, Fire Launcher mutation, and any path whose rollback may
require factory reset were not executed.

## Metrics

- Worker rows: `43`
- Live policy observations: `5`
- Integrated rows: `48`
- CSV parse warnings: `0`

## Next safe minimum

1. Resolve the live/OTA `product_policy.xml` layout mismatch with exact image
   provenance, without writing or mounting system read-write.
2. Join the residual Binder rows to saved service publication and permission
   artifacts; do not call unknown transactions.
3. Close exact native DT_NEEDED/relocation and policy edges from host artifacts.
4. If all remain incomplete, archive the privileged-control branch as
   unclosed and return to ordinary ADB HOME behavior only through already
   validated reversible paths.
