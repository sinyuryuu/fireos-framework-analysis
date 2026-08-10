# Phase 6RH — 7.3.3.1 host-only source/package index

日期：2026-08-10。範圍是 Fire OS 7.3.3.1 / PS7331 / trona 的本機 source、已解包 boot image、既有 package/decompiled/config artifacts。只做靜態 grep、索引與既有 artifact 交叉驗收；沒有執行 \`boot_unpacked/src\`、exploit/root/diagnostic binary，沒有 adb、Binder、ioctl、OTA/recovery、root、partition 或裝置寫入。

## 結論

- Amazon/MTK driver 的 source registration、Kconfig/Makefile wiring 與部分 proc/ioctl capability 已確認；\`amzn_drv_test\` 在 \`trona_defconfig\` 未選取，官方 Image 亦缺少其主要 marker。這不等於 runtime module、node、SELinux 或 caller 可達。
- Android userspace \`system/core/init\`、完整 \`file_contexts\`/CIL 與 Amazon framework source 不在已解包 GPL/source scope；因此 init、label、allow、permission grant provenance 未閉合的欄位保留 UNKNOWN。
- OTA package 是傳統 Edify/block-image 形態：metadata gate、system/vendor/boot/boot-chain targets 與 \`/cache/recovery/last_blocklist\` extraction 均有既有靜態證據；未執行 updater/recovery，也未建立普通 APK/shell 到 writer 的 caller chain。
- \`OtaDexoptService\` 與 \`BootAfterSystemOTAReceiver\` 是 framework lifecycle surfaces；service visibility、receiver action 或 holder permission 不足以推導任意 Binder、root、partition 或 protected-package sink。
- package/permission/config 資產只以保存的清單、XML 與 decompiled evidence 表示；holder、protection level、writer callsite、caller、sink 分開記錄。CSV 共 12 rows。

## Provenance anchors

| artifact | SHA-256 |
|---|---|
| \`firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2\` | \`02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea\` |
| \`firmware/extracted/PS7331-SOURCE-20250617/platform.tar\` | \`69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd\` |
| \`firmware/extracted/PS7331/boot_unpacked/Image\` | \`10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d\` |
| \`firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin\` | \`9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5\` |

Source member hashes already recorded by the preceding driver audit include \`amzn_drv_test.c\` (\`6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e\`), \`amzn_idme.c\` (\`ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e\`) and \`mtk_auxadc.c\` (\`5ffbce942417fc6aca773d90e4c6935f508087f9a80d96138a7ecc30561ed327\`).

## Evidence boundaries

The CSV is the row-level index. \`source_ref\` records source capability; \`image_ref\` records shipped-image/package evidence; \`init_or_config\` records build/init/config provenance; \`selinux_or_permission\` records explicit policy/permission evidence or UNKNOWN; \`client_or_caller\` records a caller only when the existing artifacts support it; \`sink\` records the downstream effect without conflating capability with reachability; \`remainder\` preserves bounded-negative and missing-corpus limitations.

No payload, exploit sequence, device command, recovery invocation, node access, or write recipe is included. Safe follow-up is limited to host-side extraction/indexing of already preserved files or a newly supplied complete image/archive.
