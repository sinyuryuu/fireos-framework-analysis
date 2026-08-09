# Phase 6ND — `amzn_drv_test` official kernel-image marker closure

日期：2026-08-10  
範圍：主機端 raw-byte provenance；未執行任何 kernel/source binary

## Result

**已證實（Confirmed）**：GPL source 的
`device/amazon/kernel/driver/amzn_drv_test.c` 定義了獨特 marker
`amzn_drvs`、`logger_loop`、`sign_of_life_test`、`idme_test`、`logger_test`
及 `no this test item`；這些 marker 在已從官方 PS7331 boot image 解出的
kernel `Image` 中均未觀察到。

**高可信負面證據（Strong evidence）**：在「未被編譯器消除、且 literal
保留於 built-in kernel」的情況下，該 test driver 很可能沒有被編入這個
official `Image`。這不是 generated `.config`、可載入 module、SELinux、
procfs 或 runtime 的完整證明。

**未知（Unknown）**：目前未證明 `AMZN_DRV_TEST` 的其他 product config、
module packaging、映像內未展開的檔案或實機 `/proc/amzn_drvs` 狀態。

## Inputs

* Source archive：`firmware/extracted/PS7331-SOURCE-20250617/platform.tar`
* Archive SHA-256：`69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`
* Official kernel Image：`firmware/extracted/PS7331/boot_unpacked/Image`
* Image SHA-256：`10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d`

## Evidence

完整 marker table 與 raw input manifest：
[Phase 6ND artifact](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/artifacts/phase6nd-amzn-drv-test-image-marker-20260810-01/)

可重跑腳本：
[audit_phase6nd_amzn_drv_test_image_markers.py](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/tools/scripts/audit_phase6nd_amzn_drv_test_image_markers.py)

## Safety boundary

本次只讀 tar member 與官方 kernel Image 的 bytes；未執行
`boot_unpacked` 內任何既有程式、未讀寫 driver/proc/ioctl/device node、未
ADB、未 root、未 reboot、未 OTA、未寫入分割區。結果不能轉化為實機寫入
`/proc/amzn_drvs` 的建議。

