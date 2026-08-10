# Phase 6WL evidence index

- **6WG Framework IPC residual:** `work/luna_worker_phase6wg_ipc_residual_20260810.md` (93a0840c4737258ac5c481f3e23a3c00cb7784f3b1489b7f7552c614b851079a); `work/luna_worker_phase6wg_ipc_residual_20260810.csv` (c87c7df3d0f94272b233775646454f5b03f35a19639f277f6da71b9317a26d76); 3 row(s).
- **6WH OTA residual:** `work/luna_worker_phase6wh_ota_residual_20260810.md` (4cd5e96655d50dcbf7f0e9e293af8f7183fa3d0c6eb2e094bd853b2cff7139d2); `work/luna_worker_phase6wh_ota_residual_20260810.csv` (226903b904fe99968ff0842c9345f76249b11b8ac8ab2060c59b5811b5463b70); 6 row(s).
- **6WI native driver caller:** `work/luna_worker_phase6wi_driver_caller_20260810.md` (23065fa5808b5b5ef6d5040ecc151be2a1a931741383891597a03755436eee8a); `work/luna_worker_phase6wi_driver_caller_20260810.csv` (97e7a355e1ffa06de3a94c5eab3ef4fcb288b8a4f65fbe4157a399f6de21884b); 7 row(s).
- **6WJ test reconciliation:** `work/luna_worker_phase6wj_test_reconciliation_20260810.md` (d22944d4d214aae0719eb98bedd734364f6acb99ae4e77f19d9746faf6753aba); `work/luna_worker_phase6wj_test_reconciliation_20260810.csv` (844bbbffa47066e663c65f6fdaced9ea48fc90746fe9be01b39a065332aa8760); 10 row(s).
- **6WK broad surface:** `work/luna_worker_phase6wk_broad_surface_20260810.md` (0f59e466f210a0f09d1aa10ef8859af633490350de09786c4285297cbc4e01c7); `work/luna_worker_phase6wk_broad_surface_20260810.csv` (413bf7a4e9150ea0046fef4d44d8f306b595610a4e8593d3078952f5de762d57); 17 row(s).

## Live policy evidence

- `artifacts/phase6wf-product-policy-readonly-20260810-01/` — exact serial read-only capture.
- `findings/phase-6wf-product-policy-live-readonly.md` — static-to-live interpretation.

## Acceptance rules

- Static capability, registration, or a missing local check is not external reachability.
- `UNKNOWN` is bounded missing evidence, not proof of absence.
- No row authorizes live Binder, driver, OTA/recovery, Root, or partition execution.
