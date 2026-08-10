# Phase 6PS evidence index

所有本輪設備輸出均為指定序號 `G001LT0511550CFT` 的唯讀命令；
`adb/phase6pr/PHASE6PR-VENDING-READONLY-20260810-01/sha256sums.txt`
驗證通過。

| Evidence ID | Source | File | SHA-256 | Command / observation | Interpretation | Confidence |
|---|---|---|---|---|---|---|
| PS-VEND-LIVE-01 | current device | `adb/phase6pr/PHASE6PR-VENDING-READONLY-20260810-01/vending_package.stdout.txt` | `d3075425f6980289611f8163858c9ff637901ccb4648ec482fb844973c50c361` | `adb -s G001LT0511550CFT shell dumpsys package com.android.vending` | Play Store UID 10180、`/data/app`、無 captured `PRIVATE_FLAG_PRIVILEGED`，且多項 package-management grants | Confirmed |
| PS-VEND-LIVE-02 | current device | `.../permission_definition.stdout.txt` | `62d133892d6488861e85bc7e9aeb9418e258e930e0cda507a695aac1e2e406cc` | `dumpsys package permissions` | `CHANGE_COMPONENT_ENABLED_STATE` 是 `sourcePackage=android` 的 `signature|privileged` permission | Confirmed |
| PS-VEND-LIVE-03 | current device | `.../home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | `cmd package resolve-activity ... HOME` | HOME 仍為 `com.amazon.firelauncher/.Launcher` priority 50 | Confirmed |
| PS-VEND-LIVE-04 | current device | `.../home_candidates.stdout.txt` | `e868693c97bce5ec4c93c6e5e144225797c2219fafde54d46fdbd3bdf462442c` | `cmd package query-activities ... HOME` | candidate set 為 Fire 50、Microsoft 0、FallbackHome -1000 | Confirmed |
| PS-VEND-LIVE-05 | current device | `.../metadata.json` | `281f5bcd1399d91d67d7305682b23f6866a159067766f35607c330555e92a844` | capture metadata | 沒有 Binder transaction、package/settings mutation、reboot 或 OTA/partition 操作 | Confirmed |
| PS-BINDER-01 | saved static/runtime evidence | `findings/phase-6pr-privilege-surface-synthesis.md` | `06ec5c0091005424580a635b7c03c674f43812bad30a283a8ed4d89de5f12a82` | Phase 6PR synthesis | A1/U4 是受限 ordinary-app deputies；KFT tx3 downstream rejected | Confirmed / bounded |
| PS-BINDER-02 | host-only worker | `work/luna_worker_binder_sink_closure_20260810.md` | `4f55d1ea0bc76184fafee664fad46fed57c69b390146a30cc8866a69a2940252` | saved disassembly closure | 16 個 Binder/service surfaces 分類為 deputy、trusted、query 或 unknown | Strong evidence |
| PS-BINDER-03 | host-only worker | `work/luna_worker_binder_sink_closure_20260810.csv` | `dd6f37c66367f82326b836761444a6a7e1c410e260f1d9fa7eaa8de9539c70c1` | machine-readable closure table | 16 個 surface rows 可重現讀取 | Strong evidence |
| PS-PERM-01 | host-only worker | `work/luna_worker_component_permission_provenance_20260810.md` | `67477698f8ec3dbfa10edbffeec0efcfdd082272b1e75d6583be93648a7bff62` | package dump/manifest/privapp provenance | Vending grant confirmed；來源、實際 caller、Fire target acceptance unknown | Strong evidence / Unknown |
| PS-PERM-02 | host-only worker | `work/luna_worker_component_permission_matrix_20260810.csv` | `2825742ee065928ad1f7b96484b199f3e05644a5da59fdc20e44869fcd5a7c0d` | machine-readable permission matrix | holder、placement、sink 與 confidence 欄位分開保存 | Strong evidence |
| PS-KERNEL-01 | host-only worker | `work/luna_worker_kernel_ota_unclosed_closure_20260810.md` | `35bf53964eae6f3413248ce13b4346394f9f05794bf85660b1661d62e7ac318e` | PS7331 source/OTA/init corpus | 8 個候選均未閉合 untrusted caller→privileged sink | Strong evidence |
| PS-KERNEL-02 | host-only worker | `work/luna_worker_kernel_ota_unclosed_closure_20260810.csv` | `a54a4fe8783263d3f75109c1a9f67bf9991f24cb2e7e242aaf9d251ebd1b64fb` | machine-readable kernel/OTA closure | 8 個 candidate rows 及 safe-test disposition | Strong evidence |
| PS-SCRIPT-01 | reproducibility script | `tools/scripts/capture_phase6pr_vending_provenance.py` | `21ebc4484d3c9d69623a3df20e79043f9f0667d3f763e00d15bbafbb609cff62` | script source | 只執行明確列出的 read-only ADB queries，拒絕覆寫 evidence dir | Confirmed |

## Explicit negative / rejected paths

* `com.android.vending` exported component、generic package writer、permission
  grant/revoke：未呼叫。
* KFT private Binder transaction、未知 transaction code、DPM owner/provisioning：
  未呼叫。
* updater/recovery/OTA、driver write/ioctl、`/init` property/policy mutation、
  GhostLock race/DoS：因風險拒絕。
