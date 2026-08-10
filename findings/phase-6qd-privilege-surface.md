# Phase 6QD — IPC、GPL driver 與高影響權限面審計

日期：2026-08-10

公開基準：`0511bc0ab7a769a91ab5c1f506a3a2c3237593ae`（Phase 6QC）

裝置：`G001LT0511550CFT` / `KFTRWI` / `trona` / PS7331.4463N

## Executive result

本輪把範圍擴展到 Launcher 以外的三組面：

- 未閉合 Amazon Framework/System Services IPC：12 rows；
- 7.3.3.1 GPL source 的 Amazon/MediaTek custom driver、ioctl、procfs/sysfs/
  debugfs：9 rows；
- 既有 Phase 6K–6QC 的高影響 residual gap：12 rows。

合併為 33-row matrix。結果沒有閉合出：

```text
low-privilege app/shell
  -> accepted gate or missing caller validation
  -> system/root identity
  -> PackageManager/HOME/package state/credential/SELinux/partition write
```

這是保存 artifacts 與本輪 host-only 搜尋的 bounded conclusion，不是對所有
未取得的 Amazon code、native code 或 kernel 漏洞作不存在性證明。

## 已證實（Confirmed）

1. `trona_defconfig` 啟用 `CONFIG_MTK_CMDQ=y`、`CONFIG_MTK_CMDQ_TAB=y`、
   `CONFIG_ION=y`、`CONFIG_MTK_ION=y`、`CONFIG_AMZN_SIGN_OF_LIFE=y`、
   `CONFIG_AMZN_SIGN_OF_LIFE_RTC=y` 與 `CONFIG_AMZN_IDME=y`。
2. M4U source 在 `__M4U_USE_PROC_NODE` 定義下走 `proc_create("m4u", 0, ...)`；
   `misc_register` 位於 `#ifndef __M4U_USE_PROC_NODE` 分支，不能把 `/dev/m4u`
   宣稱為本 build 的 active node。
3. perf ioctl 建立 `/proc/perfmgr/perf_ioctl`，source mode 為 `0664`；這是
   owner/group write、world read，並非 world write。
4. IDME proc fops 是 read-only，lifecycle reason proc 是 `0444` read-only，
   M4U debugfs entries 為 owner-only `0600`。
5. `amzn_drv_test.c` 包含 test index 21 factory-reset special mode 與 index 23
   RTC special-mode path，但 Makefile 以 `CONFIG_AMZN_DRV_TEST` 條件式加入；
   `trona_defconfig` 未找到 `CONFIG_AMZN_DRV_TEST=y`。因此它是 conditional
   engineering source，不是已證實的 shipped control。
6. Amazon IPC 中的 flags/metadata、DPM restriction、profile picker、OOBE/OTA
   writer、Vending generic enabled-state writer、OTA recovery sink 均已定位；
   但 caller、permission、user scope 或 trusted lifecycle 邊界仍有明確的
   `UNKNOWN`／risk-rejected 標記。

## 高可信推論（Strong evidence / Probable）

- CMDQ/MDP、M4U、sensor factory 與 perf 具備硬體、DMA/IOMMU、calibration 或
  scheduling state sink 的能力，但目前沒有 final image 的 ueventd、
  file_contexts、service_contexts、TE allow 與 shipped client 完整對照，不能
  把 source 的 `copy_from_user` 或缺少 `capable()` 直接轉成低權限可達性。
- `/proc/m4u` 的 mode literal `0` 不能單獨解讀為 world-access；實際 proc
  ownership、LSM/SELinux 與 mount policy 仍待 final image evidence。
- `CONFIG_AMZN_DRV_TEST` 未在 trona defconfig 啟用，factory-reset proc test
  path 對 PS7331 production reachability 的可信度很低；不應在真機嘗試
  `/proc/amzn_drvs` 或任何 factory index。
- Phase 6QD 的 read-only device snapshot 與 Phase 6QB 在 build fingerprint、
  HOME resolver、HOME candidate、Fire Launcher package dump、SELinux selected
  outputs 上 SHA-256 完全一致，表示本輪沒有觀察到狀態漂移。

## 待驗證（Hypothesis / bounded unknown）

- Amazon PM flags/metadata 的第一個 consumer、Vending generic writer 的真實
  caller/target、H2/Profile caller 與 `BootAfterSystemOTAReceiver` user mapping
  尚未完全閉合。
- `setPipVisibility`、WMS overscan/PIP wrapper 的完整 Stub/onTransact 與
  permission holder 尚未完成；目前 sink 仍是 PIP/window state，沒有 HOME/root
  sink 證據。
- CMDQ/MDP、M4U、perf、`/dev/gsensor` 的 final node owner/group、SELinux
  domain/allow 與 shipped framework/HAL clients 尚未取得；這是可達性缺口，不是
  exploit 證據。
- OTA `readlink`/canonicalization 間接 data-flow、recovery caller identity 與
  AVB/SELinux updater handoff 仍是 host-only gap。

## 已排除（Disproved within reviewed scope）

- 沒有證據顯示上述 GPL driver 直接寫 PackageManager、HOME resolver、Fire
  Launcher component state、credentials 或 Android root identity。
- `CONFIG_AMZN_DRV_TEST` source presence 不能視為 production enablement；目前
  defconfig 反證其未被選入該 variant 的設定檔。
- `/proc/perfmgr/perf_ioctl` 的 `0664` 不是 world-writable 證據。
- IDME、lifecycle reason 與 M4U debugfs 的 source fops/mode 不支持普通低權限
  寫入結論。
- 本輪沒有找到新的 low-privilege IPC → sensitive sink 完整鏈；未知 caller
  不得被稱為 confused deputy 或 root path。

## 因風險拒絕測試（Risk-rejected）

- 不開啟 `/dev/mtk_cmdq`、`/proc/m4u`、`/proc/perfmgr/perf_ioctl`、
  `/dev/gsensor` 或任何 `/proc/amzn_drvs`；不執行 ioctl、DMA/IOMMU、MDP register
  write、sensor calibration、factory-reset index 或 RTC special mode。
- 不猜測或重播 Amazon private Binder transaction、protected broadcast、
  Vending/OOBE workflow 或 DPM/KFT owner path。
- 不執行 OTA/recovery/update-binary、crafted package、symlink/traversal、
  reboot、Root/exploit、remount、SELinux 修改、分割區寫入，亦不再重做已排除
  的 priority、set-home、Fire disable 或普通 Launcher 測試。

## 1. Driver surface decision

```text
source / defconfig
  -> driver registration / procfs / misc / debugfs
  -> final node mode + owner + SELinux (not fully available)
  -> shipped client/domain (not established)
  -> hardware/DMA/calibration sink
```

這條鏈目前只到 capability。即使 future final-image mapping 證明某個 node
可被一般 domain 讀寫，也仍需獨立證明 validation flaw、可控 memory effect 與
system/root sink；本輪不製作 exploit。

## 2. IPC decision

```text
external caller (mostly UNKNOWN)
  -> private Binder/service boundary
  -> permission/role/user validation (partial or explicit)
  -> bounded sink
```

可確認的敏感 downstream 主要是 trusted OTA/recovery、OOBE package/settings
writer、DPM/UserManager restriction；它們都沒有被 ordinary app/shell caller
閉合。Profile、WMS、Vending 與 ProxyReceiver 的 sinks 不等於 Fire Launcher 或
root control。

## 3. Runtime evidence

本輪新增 read-only capture：
`adb/phase6qd/PHASE6QD-READONLY-20260810-01/`。

- fingerprint：`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- command count：31；`mutating_commands=false`；`binder_transactions_invoked=false`
- `home_resolve.stdout.txt` SHA-256：`d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6`
- `home_candidates_cmd.stdout.txt` SHA-256：`e85ea12c0b49b54392725c6f2f440f7c2b84ae4fdf47f604b9571c17427957e6`
- `firelauncher_package_dump.stdout.txt` SHA-256：`73cf239df6f218c345fad253d707e852ba50cdbacdefe5a93a91a99456734db5`
- `target_selinux.stdout.txt` SHA-256：`4fefafd0dcddf54b31a0fef448083e7b77576d86a9ec97c14bfd92479c404290`
- `metadata.json` SHA-256：`e2aacb3ac241db3dcc85cfa7d2e979ede9b823a66b0227e24b9adc4aa4f4cc70`

這四個 state outputs 與 Phase 6QB 對應檔案完全相同；Fire HOME 與 package
state 沒有新變化。

## 4. 最小安全下一步

1. 從 exact PS7331 image 補 final `ueventd*.rc`、`file_contexts`、
   `service_contexts`、TE allow 與 init manifest；若 artifacts 不含這些檔案，
   明確記為 evidence unavailable。
2. host-only 對 CMDQ/MDP/M4U/perf/sensor 建立 shipped client → UID/domain →
   node → fops/ioctl → sink graph；不開 node、不送 ioctl。
3. host-only 完成未閉合 IPC 的 Stub/onTransact、caller provenance、user scope
   和 first consumer；不 replay private APIs。
4. 若未出現 low-privilege caller + sensitive sink 的完整鏈，正式維持「無 Root
   正式 HOME replacement 未找到；driver/OTA 只剩能力或風險邊界」結論。

## Reproducibility

```sh
python3 tools/scripts/build_phase6qd_privilege_surface.py --dry-run \
  --ipc work/luna_worker_ipc_unclosed_sink_inventory_20260810.csv \
  --drivers work/luna_worker_gpl_driver_surface_inventory_20260810.csv \
  --residual work/luna_worker_residual_high_impact_gap_audit_20260810.csv \
  --output output/tables/phase6qd-privilege-surface.csv \
  --manifest output/tables/phase6qd-privilege-surface.csv.manifest.json
```
