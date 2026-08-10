# Phase 6PV evidence index

本階段只整合已保存的 host/device-readonly evidence。worker 原始輸出保持不變；
normalized table 由 `tools/scripts/build_phase6pv_route_closure.py` 重現。

| Evidence ID | Source | File | SHA-256 | Result | Confidence |
|---|---|---|---|---|---|
| PV-KERNEL-01 | Faraday worker | `work/luna_worker_kernel_gpl_driver_surface_followup_20260810.md` | `16ccc5ab63b6cd7e902532965a25b24d06d7dcc1b8ccbdf4e8362ee9b3bc5272` | GPL path correction, driver source capability, no framework/HOME edge | Strong evidence |
| PV-KERNEL-02 | Faraday worker | `work/luna_worker_kernel_gpl_driver_surface_followup_20260810.csv` | `f4b82cc8a9ae50f85866bc2b1b7710587e4d71c644424968a9f60b4c42636aba` | 11 normalized kernel surface rows | Strong evidence |
| PV-IPC-01 | Banach worker | `work/luna_worker_ipc_sink_inventory_followup_20260810.md` | `aa3c818b841c1567422fcd58b7d2dc34fc844bd2abd4b8d03083f8ed9935cf27` | 8 caller/gate/identity/sink routes, including two confirmed bounded deputies | Strong evidence |
| PV-IPC-02 | Banach worker | `work/luna_worker_ipc_sink_inventory_followup_20260810.csv` | `e665872e3aaea9bff6d546b89524474e7111bed3f6b68fafc4dac807c14d4197` | Machine-readable IPC matrix | Strong evidence |
| PV-OTA-01 | Boyle worker | `work/luna_worker_ota_postinstall_followup_20260810.md` | `b78c08a419ebd84558c35a002615c0c3bdc61db22a7607dac8d6a0205d29897c` | Recovery capability present; no untrusted caller route | Strong evidence |
| PV-OTA-02 | Boyle worker | `work/luna_worker_ota_postinstall_followup_20260810.csv` | `195b29bd633575d8de0cc691abbe6a1d989dd65e90ac89d61c5b98bc85b06c88` | 10 OTA/path/OOBE rows; ARCH-01 corrected below by Phase 6MI | Strong evidence |
| PV-SOURCE-01 | existing Phase 6MI EOF audit | `artifacts/phase6mi-source-tar-eof-20260810-03/summary.json` | `409ed81ede46db87a0ef8a05cc33b99df2b66e068d1edc1ac481a42e0606169b` | 35 source-tar members, `reached_eof=true`, no extraction/execution/device mutation | Confirmed |
| PV-LIVE-01 | current device readonly capture | `adb/phase6pt/PHASE6PT-READONLY-20260810-01/metadata.json` | `a42109fa1935f18d7485955bc5d514bc9c2f6f949602b8c748278a6fe631aaf2` | Capture flags show no mutation, Binder transaction, reboot or OTA | Confirmed |
| PV-LIVE-02 | current device readonly capture | `adb/phase6pt/PHASE6PT-READONLY-20260810-01/home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | HOME remains Fire priority 50 | Confirmed |
| PV-OUT-01 | normalized integration | `output/tables/phase6pv-broad-route-closure.csv` | `25ab02e4086da1a9d88dc6b0e3065e6397a036b2915c70fc33d515459a20ba49` | 29 rows across kernel, IPC, OTA/post-install | Strong evidence |
| PV-OUT-02 | normalized integration | `output/call-graphs/phase6pv-broad-route.mmd` | `8a073336016d0d5e63945d9b684e07cf60cad3d668a1e45546bc88f6667c3409` | Broad route graph with risk-rejected edges explicit | Strong evidence |
| PV-OUT-03 | reproducibility script | `tools/scripts/build_phase6pv_route_closure.py` | `2c6edbe1ec3292658eb278ef61b5c7b3e98583211f809e0e502e7289dfc9e7ee` | Host-only CSV normalization; refuses overwrite | Confirmed |

## Correction rule

The worker OTA CSV retains Phase 6FE's earlier bounded-listing wording for
`ARCH-01`. The normalized output explicitly replaces that row with the later
Phase 6MI EOF-complete result. The worker file is raw evidence and is not edited.
