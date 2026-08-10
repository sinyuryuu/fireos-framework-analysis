# Phase 6TH — PS7331 kernel/native residual surface host-only audit

日期：2026-08-10（Asia/Taipei）  
目標：KFTRWI / trona / MT8183 / Fire OS 7.3.3.1。  
安全範圍：只讀本機 GPL source、boot-image analysis、native inventories、driver caller ledgers，以及既有 GhostLock/MTK findings。未開啟 device node，未執行 open/ioctl/proc/sysfs/debugfs write、kernel probe、Binder、exploit、root、reboot、OTA/recovery 或任何設備命令；未寫 exploit。

## 結論

在保存的 host corpus 中，沒有新的、已完整閉合的「exact shipped native caller → device node/ioctl → privileged effect」production chain。唯一保留的 positive 是既有 /dev/ion 的 **library-level** 靜態 caller（libion.so 與 libion_mtk.so）；它尚未閉合到 top-level production process、實際 runtime invocation、有效 credential/domain 或下游敏感 state。

尚未閉合的 residual 主要是：CMDQ/MDP、M4U、perfmgr、RPMB，以及 GED/Vcodec/camera/sensor/thermal/USB-Type-C/PMIC 等 driver surfaces。Amazon IDME、lifecycle、metrics/vitals 是 source-bounded read-only/negative；CONFIG_AMZN_DRV_TEST 在保存的 trona/merged config 未選入，故 diagnostics 只能列為 conditional source surface。GhostLock 參考材料屬不同 Qualcomm/4.14 image family，不能提升為 PS7331 production native caller；PS7331 的 rtmutex/futex 只支持 defensive source provenance。

逐列機器可讀證據在 [CSV](./luna_worker_phase6th_kernel_residual_20260810.csv)。UNKNOWN_RESIDUAL 表示 caller、final node/policy 或 downstream effect 仍缺，不表示不存在；POSITIVE_LIBRARY_ONLY 表示 library-to-node/ioctl 靜態證據成立，但不能外推 process-level reachability。

## 核心判定規則

只有同時具備以下四段才可標示 production caller positive：

1. exact-build GPL source + selected config 的 registration/fops/ioctl/proc/sysfs/debugfs operation；
2. 同一 shipped node/entry 與 image metadata；
3. final ueventd/file-context/SELinux/credential boundary；
4. exact shipped native ELF 的 path-specific open/read/write/ioctl callsite，並能連到 privileged effect。

source symbol、config、file-context、SELinux allow、service/package/library 名稱、proc mode、shell query telemetry 或 rpmb_svc process presence 都不單獨算 caller。OTA updater 的 partition writer 另列為 adjacent boundary，不混入 driver residual。

## 重要 residual 與關係判讀

### /dev/ion：已到 library-level，仍未到 production process

libion.so 對 /dev/ion、ion_open 與 ION ioctl request sites 的證據，加上 shipped node metadata、ION source/config，足以標為 POSITIVE_LIBRARY_ONLY。libion_mtk.so 同樣有 mt_ion_open、ion_custom_ioctl 與 ioctl callsite。這兩列的未閉合點是 top-level consumer、caller UID/domain、實際 invocation 與下游 effect；既有資料沒有 Fire Launcher、PMS/HOME/package-state、credential escalation 或 OTA edge。

### CMDQ/MDP、M4U、perfmgr、RPMB：source/policy ≠ caller

CMDQ/MDP 可到 async job、readback 與 hardware/register sink；M4U 可到 DMA/IOMMU mapping/port/power；perfmgr 可到 FPSGO/fbc/touch_boost controls；RPMB 有 service/thread metadata。但保存的 native inventory 沒有 exact shipped ELF path-specific caller（RPMB 亦沒有 service-to-driver callsite），且 final policy/ownership/credential 多處未完整。這些是高價值 static residual candidates，不是已證實低權限 reachability，也沒有 launcher/package/HOME effect。

### GED/Vcodec/camera/sensor/thermal/USB-Type-C/PMIC：library/HAL 名稱不足

Phase 6SW/6TC 找到 source/config 與部分 file-context/debugfs/sysfs/node markers，但 libged*.so、libvcodec*.so、camera/sensor HAL、USB/thermal/PMIC service/library 只有 inventory presence；沒有 exact path + ELF callsite/relocation chain。因此全部維持 UNKNOWN_RESIDUAL。沒有發現通往 launcher、package state、credential 或 OTA 的 native edge。

### Amazon surfaces：讀取負面與 conditional test 分開

amzn_idme.c 移除 write bits、owner 0400；/proc/life_cycle_reason 是 0444 read/seq-only；/dev/metrics//dev/vitals 的 source fops 是 read/poll/release-only。這些不能形成 privileged write chain。相反，amzn_drv_test.c 的 lifecycle factory-reset/RTC special-mode write 是高影響 source capability，但 CONFIG_AMZN_DRV_TEST 未在保存的 trona/merged config 選入，且 shipped /proc/amzn_drvs 未被建立；不能當 production caller。

### GhostLock 與 OTA 邊界

既有 GhostLock boot analysis 描述的是 Qualcomm SM6125/4.14、不同 boot.img/image family；PS7331 是 MT8183/4.4.146+。PS7331 defensive port 只比較 futex/rtmutex task-identity invariant，沒有 kernel address、credential offset、write primitive、payload 或 runtime privilege transition。故 GhostLock row 是 NOT_A_SHIPPED_NATIVE_CALLER。

官方 OTA 的 update-binary/updater-script 確有 static partition/block-image writer，但沒有執行，也沒有把它連成 driver node/ioctl caller；BootAfterSystemOTAReceiver 是 guarded lifecycle boundary，沒有保存的 launcher/package-state writer。故 OTA row 只作 adjacent context。

## 證據強度與安全下一步

- **Strong static**：ION library-level join、Amazon read-only source semantics、GhostLock cross-device boundary、OTA static writer metadata。
- **Medium static**：CMDQ/M4U/perfmgr/RPMB 與 GED/Vcodec/camera/sensor/thermal/USB/PMIC 的 source/config/policy/native inventory residual；缺 exact production caller 或 final policy join。
- **低風險下一步**：只在 host 上補算既有 ELF reverse-dependency、path-specific string/relocation/callsite、final ueventd/file-context/TE 與 product manifest/config join；保存每個輸入 SHA-256。不得以此轉向 device node、ioctl、Binder、OTA/recovery、root、reboot 或 exploit。

## Provenance anchors

- GPL platform.tar：SHA-256 69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd。
- merged kernel.config：SHA-256 eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04。
- PS7331 boot.img：SHA-256 cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b。
- kernel/source-manifest.json：PS7331 futex/rtmutex/source boundary；reference_ghostlock/docs/BOOT_ANALYSIS.md：異機 Qualcomm/4.14 reference，非 PS7331 production evidence。
- 詳細 row-level source line、native artifact、分類、hash、gap 與 safe next step 見 companion CSV；既有 ledger 主要為 phase6so_driver_native、phase6sl_driver_callers、phase6sw_kernel_surface、phase6tc_native_caller_join。

本報告是 bounded host-only residual audit，不是漏洞確認、root 路徑、低權限可達性或 OTA 執行證明。

