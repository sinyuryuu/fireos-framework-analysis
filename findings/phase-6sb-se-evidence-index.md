# Phase 6SB–SE evidence index

所有新 worker 輸出均為 host-only。`source_sha256` 是 worker 保存的來源 hash；
worker raw CSV 與本輪 merged matrix 的 hash 由生成器 manifest 再驗證。Confidence
不把 static sink 自動提升為 caller reachability。

## Worker inputs

| Input | Rows | SHA-256 | Scope |
|---|---:|---|---|
| `work/luna_worker_phase6sb_ipc_20260810.csv` | 6 | `4a8ad5fdf0d6fe7b8d4d5f8428464d00102d8de5b235c4e43a760d0229252886` | IPC/permission/KFT |
| `work/luna_worker_phase6sc_kernel_20260810.csv` | 11 | `0f4faed5207fb9977c54ad4f6c8205d14d517ca8bec1fe42fd5f3f2224ede6cc` | kernel/driver joins |
| `work/luna_worker_phase6sd_ota_20260810.csv` | 10 | `3b98444d587a1376b4bb257de9dea647f5880480f30fcd41de6ac78284f536f6` | OTA/install/OOBE |
| `work/luna_worker_phase6se_catalog_20260810.csv` | 12 | `1180107dcb15842e95e406a87fc56a4c927c9968ce7d7f22b30d11875bb33e57` | evidence quality |
| `output/tables/phase6ry-sa-control-surface.csv` | 45 | `2a7cff4d64d8872c746421fedf2e12be0895c08ca5cbbdd76a36df7de993026b` | prior integrated ledger |

## Fresh device snapshot

| Artifact | SHA-256 |
|---|---|
| `adb/phase6se/PHASE6SE-DEVICE-READONLY-20260810-01/metadata.json` | `9749f073aed3f562b47c83396d9cf820dcf62fbd5dbb792b8739a7b698c857a2` |
| `adb/phase6se/PHASE6SE-DEVICE-READONLY-20260810-01/sha256sums.txt` | `9d9525f771ae203e23be73a1b249fc7d4f656bd0742a61cf85cd5f829b5a8a15` |
| `home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` |
| `preferred.stdout.txt` | `ab4c4d71d54faa5b5339dda54f4e3cc14c95a671e71ef1640627adf4c0e2e519` |
| `home_candidates.stdout.txt` | `e85ea12c0b49b54392725c6f2f440f7c2b84ae4fdf47f604b9571c17427957e6` |
| `package_state.stdout.txt` | `73cf239df6f218c345fad253d707e852ba50cdbacdefe5a93a91a99456734db5` |

The snapshot metadata records `read_only=true` and false values for node access,
driver reads, Binder transactions, settings/package mutation, reboot, OTA/recovery,
and root/exploit.

## Row-level IDs

`6SB-001`–`6SB-006` cover permission/holder gaps, KFT scope, shell service-manager
visibility and identity relay. `6SC` rows 1–11 cover CMDQ, gsensor, perfmgr,
M4U, ION, RPMB, IDME, diagnostic, metrics, lifecycle and GED. `6SD` covers OTA
controller, verifier, staging, updater, OOBE and receivers. `6SE-001`–`6SE-012`
are review corrections/normalization candidates, not new exploit findings.

## Direct device evidence reused

The prior public Phase 6RY snapshot remains the only device contact referenced in
the new merged ledger:

- serial `G001LT0511550CFT`
- PS7331.4463N / KFTRWI / trona / Android 9 API 28
- SELinux Enforcing
- HOME `com.amazon.firelauncher/.Launcher`, priority 50
- no driver node open, Binder transaction, setting/package mutation or reboot by
  the new generator or workers.

## Data quality rules

- Every worker CSV is parsed with the standard Python `csv` module and each row
  must match the header width.
- Duplicate `record_id` values fail generation.
- `UNKNOWN` remains a valid bounded evidence result; it is not converted into a
  negative claim.
- The manifest records false safety flags for device contact, Binder, mutation,
  driver-node access, OTA/recovery execution and root/exploit.
