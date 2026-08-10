# Phase 6RG — 廣域權限路徑與 7.3.3.1 資產交叉驗證

日期：2026-08-10
公開基準：`1aa7b4ae0ac6733f6e1f5835679f74fadbb88769`
裝置：Amazon Fire HD 10 2021 / `KFTRWI` / `trona` / PS7331 / Android 9 API 28

## Executive summary

本輪將研究範圍擴展到所有可能影響系統控制權的已保存路徑，而不只限於
Launcher：Amazon Framework/System Services IPC、KFT/profile、DPM、SettingsProvider、
SystemUI、OOBE/OTA、MTK/Amazon driver、SELinux/client、安裝包與既有實機測試。

三個 `luna_worker` host-only ledger 加上新的 exact-device read-only snapshot，正規化
為 38 rows：

| domain | rows |
|---|---:|
| Amazon IPC residual | 14 |
| PS7331 source/package/policy | 12 |
| existing runtime evidence | 10 |
| exact-device read-only snapshot | 1 |
| source/package provenance | 1 |

目前沒有閉合出以下高影響鏈：

```text
ordinary app / shell UID 2000
  → accepted caller / SELinux / permission gate
  → system/root identity or trusted relay
  → PackageManager / HOME / package state / credential / OTA / partition sink
```

這是對目前 exact-build corpus 的有界結論，不是所有未知漏洞不存在的證明。所有
caller、client、permission-holder、user propagation 或 first consumer 缺口都保留
`UNKNOWN`，不得解讀成低權限可達。

## 1. 已證實：目前裝置與資產邊界

### 1.1 Exact-device read-only snapshot

新快照：`adb/phase6rg/PHASE6RG-DEVICE-READONLY-20260810-01/`。

使用既有 `tools/scripts/capture_phase6qe_device_readonly.py`，明確指定 serial
`G001LT0511550CFT`。12 個命令全部是 metadata/state read；metadata 記錄：

- `device_nodes_opened=false`
- `driver_data_read=false`
- `binder_transactions_invoked=false`
- `settings_or_package_mutation=false`
- `reboot=false`
- `ota_or_recovery=false`
- `root_or_exploit=false`

直接觀察：

- Build：`PS7331.4463N`，fingerprint
  `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`。
- Security patch：`2024-08-01`，API 28，device/product `trona`，model `KFTRWI`。
- HOME resolver：`com.amazon.firelauncher/.Launcher`，effective priority 50。
- HOME candidates 仍包括 Microsoft priority 0 與 Settings fallback -1000。
- `/dev/mtk_cmdq`：`0644 system:system`、`mtk_cmdq_device`。
- `/dev/gsensor`：`0660 radio:system`、`gsensor_device`。
- `/proc/perfmgr/perf_ioctl`：root-owned、`proc_perfmgr`。
- `/dev/m4u`、`/dev/M4U_device`、`/proc/amzn_drvs` 不存在於 snapshot。

與 Phase 6QE 的 HOME 結果相同；node metadata 僅有 timestamp 差異，沒有狀態漂移。

主要 hash：

```text
9e111a842ff4ae9a20feae960e11cafe4a42240d69eb59d1ee7247d39c3ef3e3  metadata.json
8b511989fa23e1cf5602beefbef2f24fff54ea18889377c1efdd15cba937d44d  sha256sums.txt
d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6  home_resolve.stdout.txt
116aad758a208ebefce151f322bee8da0434382878fc984ae5f7cd577b4a5264  node_metadata.stdout.txt
```

### 1.2 Official package/source 與本地研究檔案分離

`firmware/extracted/PS7331/ota.prop`、`boot.img`、`system.img`、`vendor.img` 與
`compiled-02/extraction-manifest.tsv` 是目前 7.3.3.1 package/image provenance。
`firmware/extracted/PS7331-SOURCE-20250617/` 是 GPL/source tree，包含 MT8183 4.4
kernel、Amazon/MTK driver 與部分 FireOS material。

有界搜尋顯示 source 的 `platform/system/core` 只有部分 `libcutils`/`logwrapper` 等
內容，沒有完整 `system/core/init` 或 `init/selinux.cpp`；因此不能把此 GPL 包當成
完整 `/init` 或 Amazon framework source release。

`firmware/extracted/PS7331/boot_unpacked/README.md` 明確說明 target headers 從本地
`exploit/` 目錄複製。其 `src/exploit_main.c`、`src/root.c` 等檔案不是官方 OTA/GPL
證據，沒有執行、建置成裝置 payload 或推送到平板。

Asset note：`work/phase6rg_asset_scope_20260810.md`。

## 2. IPC residual audit

### 2.1 已證實或高可信的邊界

- Amazon PM metadata/proxy Stub 與 method-local gate 存在，但 production caller、
  cross-user acceptance、first HOME consumer 未閉合。
- KFT `enableKftLauncher(UserInfo)` 的 trusted child-user caller 與 component/package
  sink 可見；其作用域是 supplied child/profile `UserInfo.id`，不是 ordinary shell 的
  User-0 HOME setter。
- `setUserSetupComplete` 可清除 calling identity 後寫入 Settings，但 exact caller
  provenance 與 User-0 HOME sink 未閉合。
- Amazon Profile Service 有 `PROFILE_INTERACTION` 或 downstream
  `INTERACT_ACROSS_USERS` gate；profile picker 可啟動 activity，但不是 Fire HOME
  package-state writer。
- DPM restriction path 受 owner/admin/permission/user gate 約束；DPM/PMS trusted
  identity path 不能被 shell fake admin 取代。
- SettingsProvider generic write path 受 `WRITE_SECURE_SETTINGS`、cross-user、AppOps
  與 restricted-setting checks 約束；Amazon/SystemUI/OOBE 的實際 writer caller仍是
  provenance gap。
- OOBE/OTA 是 system-server lifecycle/protected receiver；Vending/DSE 的 exported
  metadata 不等於任意 sender，內部 token/creator/UID/package qualification 仍存在。

### 2.2 判定

**高可信推論**：本輪 14 rows 中沒有 `ordinary app/shell → accepted gate → trusted
identity → User-0 Fire HOME/package sink` 的閉合鏈。

**待驗證**：PM metadata permission holder、KFT 合法 caller、Profile user propagation、
SystemUI configured service 的 downstream IPC、OOBE receiver user mapping、Vending/DSE
accepted sender。這些是 host-only provenance 待辦，不是可直接測試的提權入口。

## 3. Source/package/driver/OTA audit

### 3.1 Driver 與 policy

Source registration、Kconfig/Makefile wiring、proc/ioctl capability 只能證明 source
capability。要形成可達控制鏈，還必須同時有：

```text
shipped config → init/node mode → file_context/CIL allow → compiled client → caller
```

目前 `amzn_drv_test` 不在 `trona_defconfig`；generic node/type、source `copy_from_user`
或沒有看到 local `capable()` 都不能推論 shell 可達或能轉成 system/root。

### 3.2 OTA/post-install

7.3.3.1 package 是 Edify/block-image 形態。metadata gate、system/vendor/boot/boot-chain
target、post-install/cache 與 `OtaDexoptService`/`BootAfterSystemOTAReceiver` lifecycle
均有靜態 evidence；但沒有 ordinary APK/shell 到 privileged writer/recovery/partition
sink 的 caller chain。

任何異常封包、symlink/traversal、OTA replay、recovery/updater 或 partition 測試都未
執行。這些被標記為 **因風險拒絕測試**，不能解讀為 runtime negative。

### 3.3 Init source gap

GPL source 缺少完整 `/init` source，故以下仍是 `UNKNOWN`：

- rootable policy selector 的完整 CFG；
- boot property/cmdline 到 policy-loader 的實際 data flow；
- retail boot image 中是否有可由 userspace 控制的 policy branch。

這不允許把 local `boot_unpacked` research code 當成官方 `/init` 後門。

## 4. 既有測試重新整理

10-row existing-evidence ledger 將已完成路徑分類如下：

- **已排除（在指定 build/caller scope）**：普通 package/component/force-stop 不能改
  Fire state；priority 0/ordinary preferred 不能勝過 Fire；service list visibility 不能
  直接取得 private Binder handle；Accessibility foreground redirect 不是 formal HOME。
- **已確認但非目標**：KFT child/profile per-user writer；DPM/Profile Owner trusted
  path；OOBE/OTA protected lifecycle；driver metadata；Settings/Home picker/overlay
  等既有觀察。
- **待驗證**：User-0 Fire restoration writer provenance、合法 Profile Owner relay、
  native OTA handoff、exact driver client/SELinux allow。
- **未重跑**：priority APK 矩陣、普通 `set-home-activity`、Fire Launcher mutation、
  KFT tx3、DPM raw transaction、Accessibility enable、OOBE/OTA replay、driver ioctl、
  root/exploit。

## 5. 對「只要拿到權限就能關閉」的直接回答

**已證實**：若呼叫者已經是 system/root 或被信任的 PackageManager internal path，
其抽象能力足以修改 package/component/HOME 狀態；這解釋了為何受保護的 Fire Launcher
會在高權限作用域被控制。

**尚未證實**：本輪沒有找到如何由 shell 或 ordinary app 取得該身份。不能把上述
capability 反推成 ADB 提權、App 漏洞、Binder confused deputy 或 driver exploit。

**最佳目前 rootless 結果**：Accessibility/ADB foreground redirect 仍是較實用的
近似方案，但它不改 resolver、不停用 Fire、不跨重啟成為正式 HOME，也不提供 system/root
identity。

## 6. Risk-rejected operations

本輪沒有執行：

- unknown/private Binder transaction、`service call` payload、protected broadcast；
- `/dev/mtk_cmdq`、`/dev/gsensor`、`/proc/m4u`、`/proc/perfmgr/perf_ioctl` 或
  `/proc/amzn_drvs` 的 open/read/write/ioctl；
- OTA/recovery/updater replay、異常封包、symlink/traversal、partition write；
- Root/kernel exploit、bootloader/fastboot、remount、SELinux mutation；
- Fire Launcher disable/hide/suspend/uninstall/force-stop/clear 或清除其資料。

這些是 **因風險拒絕測試**，不是「已成功驗證漏洞」或「已證明不存在」。

## 7. Reproduction

新 snapshot：

```sh
python3 tools/scripts/capture_phase6qe_device_readonly.py \
  --serial G001LT0511550CFT \
  --output adb/phase6rg/PHASE6RG-DEVICE-READONLY-20260810-01
```

host-only matrix：

```sh
python3 tools/scripts/build_phase6rg_privilege_surface.py --dry-run \
  --ipc work/luna_worker_phase6rg_ipc_residual_20260810.csv \
  --source work/luna_worker_phase6rh_source_package_20260810.csv \
  --existing work/luna_worker_phase6ri_existing_results_20260810.csv \
  --device-snapshot adb/phase6rg/PHASE6RG-DEVICE-READONLY-20260810-01 \
  --asset-scope work/phase6rg_asset_scope_20260810.md \
  --output output/tables/phase6rg-privilege-surface.csv \
  --manifest output/tables/phase6rg-privilege-surface.csv.manifest.json
```

腳本的 manifest 宣告不接觸裝置、不開 node、不呼叫 Binder/settings/package、不做
mutation、不執行 Root/exploit。

## 8. 最小下一步

仍有價值、且不重複既有測試的下一步是 host-only 補齊：

1. PM metadata mutator 的 permission holder、production caller 與 first consumer；
2. KFT/Profile 的合法 caller 與 User-0 propagation；
3. SystemUI resource service array 到 downstream IPC；
4. exact PS7331 compiled client/domain/SELinux allow；
5. 官方完整 `/init` artifact 的 CFG，而不是 local research source。

若這些仍無法閉合 ordinary caller 到高影響 sink，則應把 ADB 正式 HOME replacement
標記為目前不可行，並只保留可還原的 foreground fallback；不應用未知 Binder、驅動或
OTA mutation 來填補證據缺口。

## 9. Artifact index

- `findings/phase-6rg-report.md`
- `findings/phase-6rg-evidence-index.md`
- `output/tables/phase6rg-privilege-surface.csv`
- `output/tables/phase6rg-privilege-surface.csv.manifest.json`
- `output/call-graphs/phase6rg-privilege-transition.mmd`
- `output/call-graphs/phase6rg-privilege-transition.md`
- `tools/scripts/build_phase6rg_privilege_surface.py`
- `work/luna_worker_phase6rg_ipc_residual_20260810.md/.csv`
- `work/luna_worker_phase6rh_source_package_20260810.md/.csv`
- `work/luna_worker_phase6ri_existing_results_20260810.md/.csv`
- `work/phase6rg_asset_scope_20260810.md`
- `adb/phase6rg/PHASE6RG-DEVICE-READONLY-20260810-01/`
