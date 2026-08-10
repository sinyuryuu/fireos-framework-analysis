# Phase 6QD-B — GPL custom driver surface host-only inventory

日期：2026-08-10（Asia/Taipei）  
範圍：`firmware/extracted/PS7331-SOURCE-20250617/platform/kernel`、`platform/device/amazon`、`platform/vendor/mediatek`、`fireos/kernel` 的 source/defconfig/manifest 靜態盤點。

## 結論

本次 source-only review 找到 9 個相關 rows（見同名 CSV）。理論上最可能影響 system/device state 的 sinks 是：

- CMDQ/MDP：`/dev/mtk_cmdq` 路徑的 async job、readback slots 與 MDP register write；可影響顯示/硬體狀態，但本次未證實 package-state 寫入。
- M4U：活動 source path 是 `/proc/m4u`，可處理 MVA、port、monitor、power/TF 設定；DMA/IOMMU 影響屬高風險理論 sink，但 proc mode/SELinux/最終 build 尚未證實。
- Amazon driver test：若 `CONFIG_AMZN_DRV_TEST` 被產品 build 啟用，`/proc/amzn_drvs/sign_of_life` owner-writable test dispatcher 的 index 21 可寫 factory-reset special mode，index 23 可直接寫 RTC special-mode bits。`trona_defconfig` 未見 `CONFIG_AMZN_DRV_TEST=y`，因此 shipped reachability 是 conditional/bounded unknown。

沒有 source 證據證明一般低權限 caller 可到達上述高影響 sink。沒有在 scoped source 中找到 `capable()`/SELinux caller proof 可將其升格為 confirmed low-privileged path；缺少最終 image 的 ueventd、file_contexts/te allow 與實際 shipped client 時，統一標為 bounded unknown。未執行任何 device-node open/ioctl/probe，也未修改裝置。

## Access-control observations

- CMDQ device 是 `alloc_chrdev_region` + `device_create`，source 未指定 node mode；proc debug entries 為 `0440`，sysfs debug attrs 為 owner-only `S_IRUSR|S_IWUSR`。
- M4U 的 `#define __M4U_USE_PROC_NODE` 使 active registration 為 `proc_create("m4u", 0, ...)`；`misc_register(/dev/m4u)` 位於 `#ifndef` 分支、在該 source path 不活躍。mode `0` 不能推論為 world access。
- perf ioctl 建立 `/proc/perfmgr/perf_ioctl` mode `0664`，fops 同時提供 write/ioctl/compat_ioctl；這是 owner/group writable、world-readable，並非 world-writable。
- Amazon IDME fops 只有 read；DT permission 會清除所有 write bits，`mac_sec` 強制 `0400` 並設 uid 1000。
- Amazon lifecycle reason 是 `0444` read-only；M4U debugfs entries 全為 `0600`。

## Defconfig/manifest evidence

`platform/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig` 明確啟用 `CONFIG_MTK_CMDQ=y`、`CONFIG_MTK_CMDQ_TAB=y`、`CONFIG_ION=y`、`CONFIG_MTK_ION=y`、`CONFIG_AMZN_SIGN_OF_LIFE=y`、`CONFIG_AMZN_SIGN_OF_LIFE_RTC=y`、`CONFIG_AMZN_METRICS_LOG=y`、`CONFIG_AMZN_MINERVA_METRICS_LOG=y`、`CONFIG_AMZN_IDME=y`（lines 139-140, 463-464, 524-528）。同一 defconfig 未找到 `CONFIG_AMZN_DRV_TEST=y`；因此 Amazon driver-test factory surface 不能當作已 shipped confirmed。

Scoped extracted tree 未提供可直接對應上述 nodes 的 final `ueventd*.rc`、`file_contexts`/SELinux allow 或 init service manifest；這是 caller/permission 判定的主要 residual uncertainty。CSV 每 row 附 source file SHA-256；hash 是 evidence source file hash，不是 runtime image hash。

## Row-level audit

詳細欄位（exact path/line、symbol/ioctl、node、permission/capability、caller、sink、confidence、next safe step、hash）在同名 CSV；共 9 rows。分類使用：

- `High-impact sink; access control unresolved`：理論上可影響硬體/DMA/system state，但低權限可達性未證實。
- `Factory/engineering writable ioctl`：測試/校準/工程控制可寫狀態，caller/build gate 未證實。
- `Read-only / bounded negative` 或 `Owner-only debug surface`：source mode/fops 對低權限直接寫入形成負證據，但不替代最終 SELinux/runtime verification。

## Safe next steps

1. 只讀取得與產品 variant 完全匹配的 final `ueventd*.rc`、`file_contexts`、`*.te` allow 規則與 init manifest，映射 `/dev/mtk_cmdq`、`/proc/m4u`、`/proc/perfmgr/perf_ioctl`、`/dev/gsensor`、`/proc/amzn_drvs/*`。
2. 靜態找 shipped framework/HAL/native clients，建立 caller uid/domain → node → ioctl/fops → sink call graph；不需開 node 或執行 ioctl。
3. 對 `CONFIG_AMZN_DRV_TEST` 做產品 defconfig/Makefile/manifest 三方確認；production build 若啟用，應移除或限制 test dispatcher。
4. 針對 CMDQ/MDP/M4U 僅做 code review：檢查 command allowlist、register-range validation、per-file ownership、LSM hooks；不做 exploit 或 device interaction。

