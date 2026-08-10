# Phase 7C — PS7331 GPL kernel/driver surface closure

日期：2026-08-10（Asia/Taipei）  
範圍：host-only 靜態分析；讀取 `work/ps7331-kasan-source-20260810`、`firmware/extracted/PS7331` / `PS7331-SOURCE-20250617`、boot `Image` provenance、trona config、SELinux/file-contexts artifacts，以及 phase6NB/phase6AG/既有 driver-surface artifacts。

## 結論

CSV 共 15 條優先 user-facing surface。每條均按 `source → shipped artifact → node/entry → policy → caller UID/domain → gate → sink → effect` 交叉 join；任一段無證據即填 `UNKNOWN`，不由 source mode、Kconfig、Image literal、library marker 或 package 名稱補推。結果全部維持 `UNKNOWN`，其中 Amazon driver-test 是 config/Image marker 的 conditional negative，而非 shipped confirmation。

最重要的 source/config signals：CMDQ、ION/MTK-ION、AUXADC、uinput、evdev、thermal writable trips、USB、Amazon LD 與 IDME 相關 config/markers 可在保存的 trona config 或 Image/source artifacts 找到；但 exact final object/module/DTB、node mode/label、SELinux allow、以及 shipped native caller 的完整四方 join 不在 scoped evidence 中。`CONFIG_AMZN_DRV_TEST` 在 trona defconfig 未見 `y/m`，phase6NB 亦顯示 Kconfig default n 與 Image test-marker negative，因此列為 conditional/source-capable，不列為 shipped surface。

## Policy / caller boundary

保存的 policy artifacts 證實產品會載入 split `plat/vendor/odm/fireos` policy 路徑，但未提供可將本表每個 `/dev`、`/proc`、`/sys`、debugfs entry 與 exact type/allow/caller domain/UID 完整對上的證據。Source-side `0400/0444/0600/0664` 只描述 registration 或 file mode，不能替代 file_contexts、TE allow 或實際 owner/group。`libion`、HAL/library、Java package 與 service 名稱也不算 native open/ioctl caller。

## Static-only boundary

未執行 kernel、QEMU exploit、driver open/ioctl、ADB、root、boot/partition 操作；未設計或執行利用 payload。Effect 欄只描述 source-visible sensitive sink，不宣稱低權限可達、root、PMS/AMS/HOME 或 package-state effect。證據 SHA-256 是對應 source/evidence file 的 hash；每列的 `missing_edge` 是縮小 UNKNOWN 所需的下一個靜態 join。

## Evidence set

- `firmware/extracted/PS7331/boot_unpacked/Image`：`10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d`
- `work/ps7331-kasan-source-20260810/arch/arm64/configs/trona_defconfig`：`09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac`
- `artifacts/phase6nb-amzn-drv-test-source-closure-20260810-04/phase6nb-amzn-drv-test-source.csv`：`70b74c679b5b036397e23e737477d102b0f67076d5fa475556e56fad144f6daa`
- 既有 Phase 6AG/6UK/GPL inventory 用於 line-level cross-check；本輪輸出只新增 Phase 7C schema，不覆寫或回退既有 artifact。

