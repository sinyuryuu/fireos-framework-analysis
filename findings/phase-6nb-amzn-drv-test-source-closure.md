# Phase 6NB — Amazon `amzn_drv_test` source closure

日期：2026-08-10
範圍：PS7331 GPL source，主機端、唯讀、未接觸裝置

## 結論

**已證實（Confirmed）**：Amazon source 的
`device/amazon/kernel/driver/amzn_drv_test.c` 定義了 `/proc/amzn_drvs`
概念上的三個 child：`sign_of_life`、`idme`、`logger`。三者均接到共用
`test_fops.write = proc_write`；`proc_write` 會做長度檢查、複製輸入、解析
一個十進位 index，再 dispatch 到相應測試函式。source 也在
`Kconfig` 宣告 `AMZN_DRV_TEST`，並在 `Makefile` 將它映射至
`amzn_drv_test.o`。

**高可信負面證據（Strong evidence）**：指定的
`kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig` 選取了
`CONFIG_AMZN` 及其 metrics/sign-of-life/IDME 相依項，但沒有
`CONFIG_AMZN_DRV_TEST=y` 或 `=m`。這只否定該 defconfig 的選取，不等於
否定其他 generated config、product overlay 或 module packaging。

**未知（Unknown）**：目前沒有證據證明 test object 被編入或載入 PS7331
零售映像、`/proc/amzn_drvs` 在實機存在、實際 SELinux label/權限、caller
UID/GID，或任何 userspace 可達路徑。source 中的 `factory reset`、`OTA`
或 `reboot` 測試名稱不代表實機可達，也不構成漏洞或提權證據。

## 輸入與雜湊

* Archive：`firmware/extracted/PS7331-SOURCE-20250617/platform.tar`
* Archive SHA-256：
  `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`
* `amzn_drv_test.c`：
  `6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e`
* `Kconfig`：
  `70ccd0fca0c20f90c867efe7e1d69167aa1e99954f277e56ee0b83d57b61da89`
* `Makefile`：
  `0f50ca76a8028be56db580f288aa81e231b0c9892b5517f4c5e0984c13fb861b`
* `trona_defconfig`：
  `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac`

## 證據位置

完整 worker 原始報告：[luna_worker source closure](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/work/luna_worker_phase6na_amzn_drv_test_closure_20260810.md)

可重跑的 host-only 稽核：[audit_phase6nb_amzn_drv_test_source.py](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/tools/scripts/audit_phase6nb_amzn_drv_test_source.py)

生成物：[phase6nb source closure artifact](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/artifacts/phase6nb-amzn-drv-test-source-closure-20260810-03/phase6nb-amzn-drv-test-source-closure.md)

證據表：[phase6nb source evidence CSV](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/artifacts/phase6nb-amzn-drv-test-source-closure-20260810-03/phase6nb-amzn-drv-test-source.csv)

## 安全邊界

本階段沒有執行 ADB、`service call`、Binder transaction、ioctl、device
node 存取、APK 安裝、root、reboot、OTA、flash、分割區寫入或系統修改。
下一個最小研究目標是離線確認完整 build pipeline 是否可能選取
`AMZN_DRV_TEST`；不是向實機 `/proc` 寫入任何 index。
