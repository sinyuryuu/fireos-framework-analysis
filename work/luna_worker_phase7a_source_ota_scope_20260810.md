# Phase 7A — 7.3.3.1 source/installer host-only scope audit

日期：2026-08-10。範圍限於 host-only、唯讀 artifact scope/provenance；沒有執行 source/build/update-binary/recovery，沒有 ADB、Binder、driver open/ioctl、root、裝置或 partition mutation。

## 結果摘要

- 官方 source archive `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` 存在，大小 2,563,328,975 bytes，SHA-256 `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`；既有 Phase 5BT provenance 記錄其 HTTP Content-Length/MD5-ETag 一致。
- 已保存 source tree 不是只含 kernel：存在 `platform/system/core`、MT8183 4.4 kernel、`platform/device/amazon/kernel/driver`、`fireos/kernel` 與 `apps`。既有 source-tree index 記錄 173,535 files；本輪只作 bounded name/existence/hash checks。
- nested `platform.tar` 含 system/core、kernel/init/drivers、Amazon driver 與 `trona_defconfig` 等 source；nested `fireos.tar` 含 FireOS/AOSP-style userspace source。兩個 nested tar 的 SHA-256 分別為 `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` 與 `bb7030296545dd45edcf47d3e742043e7813852844f4b0fbbe8d223899b369`。
- source bundle 中未找到 OTA installer 成員（`META-INF/.../update-binary`、`updater-script`、`payload.bin`、`.new.dat`、`otacert` 等）；`recovery.c` 命中僅是 kernel/filesystem recovery source 名稱，不能當作 recovery image 或執行入口。
- 保存的官方 PS7331 OTA 是另一個 SignApk-signed ZIP/JAR，SHA-256 `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`；含 `update-binary`、`updater-script`、system/vendor block payload、boot 與 preloader/LK/TEE 等 images。其 `updater-script` 靜態寫入路徑與 gate 已在既有 Phase 6X/6X2 OTA ledger 覆蓋，本輪只記錄 source-to-installer provenance 缺口，不重報既有 OTA surface。
- OTA 內 `boot.img` SHA-256 `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` 與保存 extracted boot 一致；source `rtmutex.c` SHA-256 `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` 與既有 nested-source semantic evidence 一致。這支持 artifact identity/semantic comparison，不等於完整可重現 build 或 exact installed PS7330 binary provenance。

## 未閉合邊界（去重後）

1. source tree → shipped OTA installer/userspace 的映射仍 UNKNOWN：source bundle 有 kernel/system/core/FireOS/apps，但沒有 installer scripts 或一份完整 build/output manifest 將它們連到 OTA ZIP member。
2. build scripts → signed boot 的可重現 provenance 仍 UNKNOWN：`README.txt`/`build_kernel.sh` 只證明建置材料與命令描述存在；本輪未執行 build，也沒有 toolchain lock、完整 config/output manifest 或 reproducible-build attestation。
3. Amazon driver source → shipped runtime caller/gate/sink 仍 UNKNOWN：`amzn_drv_test.c` 有 OTA reboot 字串/測試路徑，並不證明 production caller、UID/domain、SELinux gate、open/ioctl reachability 或敏感 sink。能力不作漏洞判定。
4. source archive/official PS7331 OTA 與目前保存的 exact installed target 仍是版本邊界：既有 provenance 將本地裝置標為 PS7330、下載物標為 PS7331；因此 PS7331 source/boot/OTA 不能單獨升格為 exact installed PS7330 evidence。

## 既有結論不重複

Phase 6X/6X2 已保存的 OTA controller、signature/device/build checks、recovery/native execution boundary、HOME/package-state routes 及 signed OTA inventory 不在本輪重列。Phase 5 source semantic conclusion（PS7331 `remove_waiter()` pre-fix shape）也只作 hash/provenance cross-check；本報告不把 source capability、driver test code 或 installer write capability 說成漏洞。
