# Phase 6UM evidence index

## 6UI IPC privileged sinks

Report SHA-256: `29d374ae81f2a30733dd25bab7f8ba955e2b3aeb7c9d24ce35d75140d85eeaaf`

CSV SHA-256: `5dc944d2f618ede728cf83de0d8c9f00af9f9aad51c32d596936c2e7a7deed82`

Sources: `work/luna_worker_phase6ui_ipc_sinks_20260810.md`, `work/luna_worker_phase6ui_ipc_sinks_20260810.csv`

## 6UJ OTA post-install

Report SHA-256: `3446ecd40b4ff65decd2b958deb5f369ab16981ab33fe05f08168b5711c3e257`

CSV SHA-256: `437c6aeb639b38fb1203261d75d129d3b4047376b2396c3bf0e7f1c82cbb568e`

Sources: `work/luna_worker_phase6uj_ota_postinstall_20260810.md`, `work/luna_worker_phase6uj_ota_postinstall_20260810.csv`

## 6UK GPL driver surface

Report SHA-256: `8117fe52ca293d5886e9a2f76eae4344068b5c0ae20e1860a7f43b28a47d9950`

CSV SHA-256: `021d5d2ef514959202e19867ccec9784b9bb302e847c66c1bc6103bb4538a6f2`

Sources: `work/luna_worker_phase6uk_driver_surface_20260810.md`, `work/luna_worker_phase6uk_driver_surface_20260810.csv`

## 6UL historical test reconciliation

Report SHA-256: `1c7372db02db19ca7c74b0b7e181dd83544c51c948b9793ab2533e2fd42846c3`

CSV SHA-256: `6de2b11fc924413e4a33cdcfdba99353785f1f66826d875db3fe46bc4b36416b`

Sources: `work/luna_worker_phase6ul_test_reconciliation_20260810.md`, `work/luna_worker_phase6ul_test_reconciliation_20260810.csv`

## Acceptance rules

- A capability row is not a reachability or exploit row without caller, gate, identity/user scope and effect evidence.
- A missing method-local check is not evidence that an external caller can obtain a handle.
- A static partition writer, driver ioctl or system-server lifecycle writer is not an ADB workaround.
- `UNKNOWN` is a bounded evidence state, not a universal absence claim.
- No row authorizes a live private Binder call, driver operation, OTA/recovery action or exploit.
