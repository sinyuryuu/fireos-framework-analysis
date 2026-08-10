# Phase 19C — MTK/Amazon driver caller closure audit

日期：2026-08-10（Asia/Taipei）

本輪只讀分析 preserved GPL/source、`trona_defconfig`、PS7331 Image marker、DTS 變體、既有 extracted `file_contexts`/CIL/init、selected native ELF inventory。沒有 `/dev` open/ioctl，沒有 proc/sysfs/debugfs 讀寫，沒有 module、root、Binder、實機或狀態變更。逐行 canonical ledger 在同名 CSV。

## 結論

Phase 18 已閉合的 ION generic/MTK library→node/ioctl rows 不重複計入。本輪只保留其未閉合的 process-level caller：`gralloc.mt8183.so` 與 `hwcomposer.mt8183.so` 確有 ION ELF dependency/relocation，但 service→implementation load、實際 process invocation、selected heap/DT 與下游效果仍 UNKNOWN。

其餘指定面沒有取得完整 caller closure：CMDQ、M4U、uinput/evdev、AUXADC/gsensor、RPMB、USB、performance 與 Amazon liquid detection 均缺至少一項 exact shipped native opener、selected DTB/object、最終 node owner/mode/context 或 caller domain/TE edge。Amazon `amzn_drv_test` 是唯一明確的 `BOUNDED_NEGATIVE`：config 未選、官方 Image 的 `amzn_drvs` marker 為 0；不能把 source test dispatcher 或 connectivitydiag package 當成 shipped caller。

## Caller-to-sink boundary

| 面 | 最強 host-side caller 證據 | 未閉合的 sink 邊界 |
|---|---|---|
| ION | gralloc/hwcomposer ELF 對 `libion`/`libion_mtk` 的 NEEDED、relocation、symbols | service loader、runtime invocation、heap/DT、下游 display/camera consumer |
| CMDQ/MDP | source/config/Image/node/policy markers | exact `/dev/mtk_cmdq` opener + ioctl ELF、selected DTB/object、caller TE |
| M4U | source proc handlers；DTS M4U node source | compiled delivery、`/proc/m4u` policy、native writer |
| uinput/evdev | source fops/config；native inventory negative | ueventd mode/label、TE allow、concrete creator/writer |
| AUXADC/gsensor | config/Image AUXADC markers；DTS variant compatibles | selected DTB/object、node policy、calibration writer |
| RPMB | shipped `rpmb_svc` identity/service evidence；kernel ioctl ABI | exact native open/ioctl、domain/capability/auth validation |
| USB | USB/XHCI config and controller DTS source | usbfs client ELF, node policy, controller delivery |
| performance | source proc writer and genfscon candidates | final proc instance, exact writer/trigger/domain |
| Amazon diagnostic/liquid | test negative; `amzn,ld` only in source DTS variants | test object/proc policy; selected liquid node, sysfs writer/TE |

所有 sinks 都停留在硬體、DMA、input、persistent storage、scheduler、diagnostic 或 liquid/USB control state；本輪沒有任何 driver→PackageManager、ActivityManager、SettingsProvider、Fire Launcher、HOME replacement 或 privilege-transition sink。

## 判定規則

`UNKNOWN` 表示 source/config/image/policy 中有部分證據，但 caller closure 缺邊；`BOUNDED_NEGATIVE` 僅表示 preserved config/Image 對 named Amazon test route 的強負面，不是普遍 runtime absence。`file_contexts` type、候選 domain、DTS compatible、Image literal、DT_NEEDED 或 library symbol 均不能單獨提升為實際 invocation。

## Reproducibility

- GPL/source與config：`work/ps7331-kasan-tree-20260810/platform/kernel/mediatek/mt8183/4.4`、`platform/device/amazon/kernel/driver`。
- ION loader graph/native ELF：`work/luna_worker_phase6tn_ion_loader_graph_20260810.{md,csv}`。
- prior final joins：`work/luna_worker_phase13_driver_join_20260810.csv`、`work/luna_worker_phase17_driver_policy_20260810.md`、`work/luna_worker_phase18_kernel_driver_callers_20260810.csv`。
- Amazon test marker：`artifacts/phase6nd-amzn-drv-test-image-marker-20260810-01/phase6nd-image-marker-audit.md`。

CSV 共 11 筆新 caller-focused rows；欄位皆以 RFC 4180 風格 quoting 處理，並保留 UNKNOWN/BOUNDED_NEGATIVE 邊界。
