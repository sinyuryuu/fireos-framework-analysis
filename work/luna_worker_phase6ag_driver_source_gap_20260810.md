# Phase 6AG — GPL driver source / boot Image / policy / caller gap audit

日期：2026-08-10（Asia/Taipei）  
範圍：PS7331 source、保存的 boot `Image`/`boot.img`、vendor policy artifacts、既有 Phase 5/6 driver/native rows。僅 host-side 靜態稽核；未開 `/dev`，未 ioctl，未寫 proc/sysfs/debugfs，未執行 ELF，未 push binary，未觸發 kernel race/root/panic。詳細去重 rows 見同名 CSV。

## 結論

本輪掃描 `device/amazon/kernel/driver`、`kernel/mediatek/mt8183/4.4/drivers/{input,power,usb,char,misc}` 及其中 ION/CMDQ/RPMB/debugfs/proc/sysfs registrations。archive 沒有 literal `drivers/amazon/`；Amazon source 的實際位置是 `device/amazon/kernel/driver/`，並由 staging Kconfig/Makefile 接線。這是 source/build evidence，不是 shipped node 或 caller proof。

CSV 將四件事分開：

* **source capability**：registration、fops、ioctl、`.store`、`copy_from_user` 或 source mode。
* **shipped artifact**：trona/merged config、保存 boot Image marker、node metadata、vendor file_contexts/CIL；缺失 final object/module/DT/init 時不補推論。
* **caller reachability**：只接受 exact shipped native ELF 的 path-specific open/read/write/ioctl 或既有 runtime evidence；library symbol、package 名稱、HAL 名稱不算 caller。
* **security effect**：只記錄 source 可影響的硬體/持久/輸入/電源/診斷狀態；沒有 caller 或 policy 時為 `UNKNOWN`，不宣稱 package/HOME/root effect。

## 去重後 gap

1. `uinput` 與 power-supply sysfs 已有 Phase 6XG rows；本報告只保留它們作為 cross-check，不重複 row。兩者均沒有 exact shipped native writer/caller 與 package/UID/domain join。
2. RPMB、perf ioctl、AUXADC、PMIC debugfs、Amazon IDME/driver-test、touch/input factory proc/sysfs 仍存在 source-visible sinks，但既有 rows 沒有同時閉合 caller、final policy 與 identity，因此列入 CSV。
3. CMDQ、ION、Amazon-LD 等既有 rows 不重複；本輪只記錄 requested-scope 的 artifact/policy gap（例如 Image kernel string 不能證明 node delivery，ION library 不能證明 top-level consumer）。
4. `drivers/amazon`、Android userspace `system/core/init`、完整 matching `ueventd*.rc`/`file_contexts`/vendor-TE caller tuple 在本 scope 沒有可將 source 連到普通 app 的完整鏈。缺 caller 或 policy 的欄位一律 `UNKNOWN`。

## 重要 negative / boundary

* `CONFIG_AMZN_DRV_TEST` 在 `trona_defconfig` 未見 `y/m`；source 的 writable `/proc/amzn_drvs/*` 因而只能是 conditional/source-only，不能當成 shipped reachability。
* Amazon IDME/lifecycle/metrics source 多為 read/read-only 或 policy-dependent；`mac_sec`/DT permission、file context、TE、HAL caller 需 exact product artifact 才能定身份。
* RPMB userspace ABI 由 `unlocked_ioctl` 提供，`rpmb_fops` 沒有 `.read`/`.write`；既有 `rpmb_svc` 名稱或存在不等於 exact open/ioctl caller。
* power-supply writable sysfs 由 provider `property_is_writeable()` 決定；generic `.store` 不等於所有 battery properties 可寫。
* boot `Image` literal、embedded config、source `device_create()`、policy allow 或 node metadata 各自都不是 runtime invocation。沒有 row 證明 ordinary app → driver → PMS/AMS/HOME/Fire Launcher、root 或 credential transition。

## Provenance

主要輸入：`firmware/extracted/PS7331-SOURCE-20250617/platform.tar`（既有 hash `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`）、`firmware/extracted/PS7331/boot_unpacked/Image`（既有 hash `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d`）、`artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config`（既有 hash `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04`），以及 `phase6xg/6so/6wi/6uk` driver/native CSV 與 `phase6vc`/`phase6qe` policy reports。Source member exact paths、行號、hash 與狀態在 CSV。

## Safe disposition

本輪沒有新 runtime probe，也沒有 exploitability、root、panic、race 或 package/HOME 結論。後續若要縮小 UNKNOWN，只能增加 exact matching product 的 final init/ueventd/file_contexts/TE、DT/object/module manifest 與 shipped native ELF path-specific callsite 的靜態證據；不需要也不應以開 node、發 ioctl 或 binary push 取代此缺口。
