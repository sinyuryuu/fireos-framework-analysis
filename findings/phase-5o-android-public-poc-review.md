# Phase 5O — public Android PoC reference review

## Scope

這份附錄專門記錄 GitHub 上可查到的 Android implementation，避免把
「Android app detector」、「generic target generator」和「已在特定手機驗證
的 root port」混稱為同一種證據。所有 repository 以 pinned commit、README
SHA-256 與 target scope 記錄；沒有下載或執行第三方二進位檔。

## Findings

1. **已證實：** `CakesTwix/Android-CVE-2026-43499` 是 Android detector，
   不是通用 root implementation；它將 native test library 放入 Android
   app，依 ABI 選擇 arm64/armv7，並以 process termination behavior 判斷。
2. **已證實：** `xianwan1314/CVE-2026-43499-Poc-Analysis` 是以 exact
   `boot.img` 和 profile 產生 target header 的 Android arm64 porting
   framework；沒有本機 `KFTRWI/trona` profile。
3. **已證實：** `soralis0912/CVE-2026-43499-aristotle` 是 MediaTek Android
   12／5.10.136 的另一個 target，README 自稱 code-complete from static
   analysis but not yet validated on hardware；不能把它當 Fire HD 10 POC。
4. **高可信推論：** 對本機最有價值的是其「每個 build 重新推導 offset、
   phys-load、KASLR/stack 假設」的方法，而不是任何常數或 payload。
5. **已證實：** 多個 Android port都把 compiler/PGO/LTO、kernel generation、
   SoC、stack frame、physmap alias視為 target-specific；這支持本專案不把
   Pixel／Samsung／OPPO／Xiaomi target header移植到 MT8183。
6. **待驗證：** GitHub 未來是否出現 exact `trona` target；目前搜索只代表
   pinned repository set，不是全站完備搜尋。

## Safety result

本次沒有安裝 detector APK，沒有執行 `LD_PRELOAD`、futex trigger、native
library、root daemon 或 KernelSU payload。原因是 detector README 也明示在
脆弱 kernel 上可能造成 kernel crash/reboot，而本機 exact signed binary
patch status與runtime layout仍未確認。

完整 pinned metadata位於
[`artifacts/phase5/android-public-poc-review-20260804-01/`](../artifacts/phase5/android-public-poc-review-20260804-01/)。
