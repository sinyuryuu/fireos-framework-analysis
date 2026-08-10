# Phase 6PZ — kernel、IPC/OTA 與 workaround broad-surface closure

日期：2026-08-10
公開基準：`79955c534ec852563caf52d388587bccf12a231d`
裝置 comparator：`G001LT0511550CFT` / `KFTRWI` / `trona` / `PS7331.4463N`

## Executive result

本輪依照「任何可能的高權限路徑都要分開驗證」的原則，把三組 host-only
worker 輸出整合：

- 13 個 PS7331 kernel/driver user-surface rows；
- 6 個仍未完全閉合的 Amazon IPC/OTA/OOBE rows；
- 22 個既有 HOME／package／Accessibility／child-profile workaround rows。

合計 41 rows。**沒有新增已證實的低權限 caller → system/root identity →
User-0 package state、HOME 或 partition sink。** 這不是「所有漏洞不存在」的
宣稱，而是目前 exact-build evidence 的 caller、gate、identity、sink closure。

目前最好的實際結果仍是：

1. child profile 內的 Tahoe HOME（per-user，不是 User 0 replacement）；
2. 需要使用者明確授權、時序敏感的 Accessibility/ADB foreground redirect；
3. User 0 正式 HOME 仍為 Fire Launcher，未找到可持久替換的無 Root shell route。

本輪沒有執行 adb、device-node open、ioctl、Binder/service call、broadcast、
OTA/recovery/update-binary、Root/exploit、reboot、package/settings mutation、
user provisioning 或分割區操作。

## Evidence classification

### 已證實（Confirmed）

- PS7331 官方 7.3.3.1 source archive、platform source、boot image 與官方 OTA
  artifact 的 provenance 已有 hash；source archive 的 outer stream 已由
  Phase 6MI 讀到真正 EOF，共 35 members，沒有 hidden updater/post-install
  outer member。
- selected kernel source 沒有直接 `driver → PMS/AMS/ATMS/HOME/Fire Launcher`
  source edge。GED `/proc/ged` 只有保存的 shell read-only telemetry evidence。
- Fire protected package / KFT child writer / Amazon IPC closure 的既有結論未被
  新資料推翻。
- 22 個 workaround 的正式 HOME、child HOME、foreground redirect、static-only
  與 risk-rejected 類別已分開；沒有一個新 row 證明 User-0 formal HOME replacement。

### 高可信推論（Strong evidence / Probable）

- CMDQ、ION、RPMB、evdev、USB、debugfs/sysfs、Amazon test/proc surfaces 是
  hardware/telemetry/debug/storage capabilities，不是已證明的 launcher control
  plane。
- `IAmazonPackageManager` proxy receiver、Vending exported receiver/service、
  OTA handoff 與 post-OTA OOBE 是 bounded unknown 或 trusted lifecycle；目前沒有
  low-privilege caller provenance。
- source 中的 `unlocked_ioctl`、`copy_from_user`、`device_create`、writable mode
  或缺少局部 permission marker，不能單獨升級為 LPE、root 或 Fire disable。

### 待驗證（Hypothesis / bounded unknown）

- `IAmazonPackageManager` tx6/tx7 proxy receiver 的完整 external caller、identity
  relay 與第一個 state consumer；
- Play Store `LauncherConfigurationReceiver`／`DseService` skipped body 的 exact
  smali/data-flow；
- OTA Java→native/recovery handoff 的 indirect dispatch（不能以實機 OTA 補洞）；
- `BOOT_AFTER_SYSTEM_OTA` receiver 的 exact delivered numeric user 與自然 OTA
  後 resolver timeline；
- 每個 kernel node 的 exact file-context/SELinux/caller，尤其 ION/RPMB/USB/CMDQ；
- workaround reports 中 4 個仍有最小 host-only 價值的 evidence normalization gaps。

### 已排除（Disproved within reviewed scope）

- 7.3.3.1 outer source archive 中藏有新的 updater/post-install launcher writer；
  Phase 6MI 已達 EOF，outer members 為 source/build material。
- selected driver source 直接寫 Android PackageManager/HOME；
- 既有普通 priority、`set-home-activity`、component-disable、DeviceConfig/role
  與普通 Settings 嘗試能形成新的 User-0 formal HOME route；
- GED read-only query 本身是 root 或 launcher primitive；
- child Tahoe HOME 可被誤稱為 User-0 replacement。

### 因風險拒絕測試（Risk-rejected）

- private Binder transaction guessing/replay；
- protected broadcast/OOBE replay；
- crafted OTA、recovery/update-binary、symlink/path traversal；
- CMDQ/ION/RPMB/USB/GED write、DMA、secure-world 或 kernel race；
- Fire Launcher disable/hide/suspend/uninstall/clear；
- Root exploit、SELinux bypass、reboot、flash、partition write。

## 1. Kernel and driver surface

### Source and image provenance

Worker 保留的 exact artifacts：

| Artifact | SHA-256 |
|---|---|
| `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` |
| `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` |
| `firmware/extracted/PS7331/boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` |
| `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` |

Phase 6MI 的 outer-archive EOF result 是更強的 archive completeness evidence：
35 members、23 files、12 directories、0 symlink/hardlink；只見 source/build
payload 與已知 launcher source，沒有 `update-binary`、`updater-script`、
`postinstall`、`system/`、`vendor/`、`boot/` 或 `recovery/` outer member。

### Driver-to-HOME boundary

Selected source scopes include CMDQ, ION, GED, Amazon IDME/logger/lifecycle,
input/evdev, USB devio, RPMB、debugfs/sysfs 與 Amazon test surfaces。它們的
source capability 仍必須經過：

```text
registration → fops/attribute → Kconfig/build inclusion
  → file-context + Unix mode → SELinux caller policy
  → preserved user caller → hardware/storage/telemetry effect
  -X→ PMS / AMS / ATMS / HOME / Fire Launcher
```

保存的 runtime only confirms `/proc/ged` read-only shell telemetry under
`u:r:shell:s0` and SELinux Enforcing. No write/reset/DMA/secure-world path was
called. The 13-row kernel matrix is therefore a reachability-aware inventory,
not an exploit list.

## 2. IPC / OTA / OOBE residuals

The six bounded rows are deliberately retained rather than falsely closed:

| Surface | Current status | Why it is not a root/HOME result |
|---|---|---|
| `IAmazonPackageManager` tx6/tx7 | **待驗證** | external authorization, caller universe and receiver consumer incomplete |
| Vending `LauncherConfigurationReceiver` | **待驗證** | exported manifest exists, but body was skipped; no Fire/HOME sink recovered |
| Vending `DseService` | **待驗證** | permission-gated bookkeeping; complete target flow unavailable |
| OTA verifier → recovery/native updater | **待驗證 / risk-rejected** | privileged capability seen; shell/ordinary caller handoff absent |
| `BOOT_AFTER_SYSTEM_OTA` | **Confirmed static, user timeline unknown** | system-server phase 550 + `isUpgrade`; OOBE/setup sink, not ordinary HOME writer |
| outer source archive tail | **Superseded/closed by Phase 6MI** | EOF-complete source audit already exists; no need to rerun archive listing |

The absence of a permission marker in a decompiler slice is not treated as an
authorization bypass. The only valid continuation is host-only recovery of
skipped methods, manifest ownership, static callers and first persistence
consumer. No private transaction or broadcast should be guessed.

## 3. Workaround classification

The 22-row evidence matrix confirms:

| Class | Result |
|---|---|
| True HOME / User 0 | Fire remains resolver winner at priority 50 |
| True HOME / child user | Tahoe works per child profile only |
| Preferred/set-home | record may persist but does not displace Fire |
| Accessibility/ADB foreground | temporary, timing-sensitive redirect; not resolver replacement |
| Lock Task | foreground retention only; not persistent HOME |
| Static-only | Settings/SystemUI/Amazon helper/package writer observations without runtime HOME sink |
| Risk-rejected | KFT private tx, DPM owner, Reset App Preferences, OTA/OOBE |
| Remaining minimal-safe gaps | Settings resource diff, timestamp normalization, child user-ID reconciliation, OTA/DPM first-consumer trace |

These four remaining gaps are host-only evidence normalization tasks. They do
not justify repeating reboot, Accessibility, child switch, DPM, OTA or package
mutation tests. The best practical rootless approximation remains the explicit
user-authorized foreground redirect, with Fire still remaining the formal HOME.

## 4. Reproducibility

Combined matrix:

`output/tables/phase6pz-broad-surface-closure.csv`

Generator:

`tools/scripts/build_phase6pz_broad_surface_closure.py`

Safe regeneration:

```sh
python3 -m py_compile tools/scripts/build_phase6pz_broad_surface_closure.py
python3 tools/scripts/build_phase6pz_broad_surface_closure.py \
  --kernel work/luna_worker_kernel_driver_surface_followup2_20260810.csv \
  --ipc-ota work/luna_worker_ipc_ota_unclosed_followup_20260810.csv \
  --workarounds work/luna_worker_workaround_gap_followup_20260810.csv \
  --output output/tables/phase6pz-broad-surface-closure.csv \
  --manifest output/tables/phase6pz-broad-surface-closure.csv.manifest.json \
  --dry-run
```

The generator refuses to overwrite existing outputs and reports:
`device_contacted=false`, `mutation=false`, `binder_or_driver_operation=false`,
`ota_or_recovery_executed=false`, `root_or_exploit=false`.

## 5. Decision and next safe value

No evidence currently supports a safe live Root PoC or an official User-0
launcher replacement. The remaining research value is host-only completion of
the six IPC unknowns and four workaround evidence gaps. If any future result
contains a concrete low-privilege caller, an explicit permission/gate pass, a
system identity transition and a package/HOME/root sink in the same chain, it
can be evaluated for a read-only or reversible device test. Until then,
executing unknown Binder, driver, OTA or Root payloads would add risk without
answering the launcher question.
