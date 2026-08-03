# Phase 5Z：Android AEE／AED 實作與 exact Fire OS 邊界

## 目的與安全範圍

本輪回答「AEE 在 Android 中實際由哪些元件實作，以及 exact
KFTRWI/trona/PS7330 是否存在 shell 可達的 Android 入口」。只做主機端
source/artifact 分析與既有唯讀證據整理；沒有開啟 `/dev/aed0`、`/dev/aed1`、
`/dev/atf_log`，沒有執行 AEE daemon、crash/race trigger、root payload 或
任何 boot-chain／分割區操作。

## Android 實作分層

```text
MediaTek kernel AEE API / driver
        |
        +--> misc_register(aed0)  [external exception / EE]
        |       \--> /dev/aed0 --read/write/ioctl--> privileged AEE reader
        |
        +--> misc_register(aed1)  [kernel exception / KE]
        |       \--> /dev/aed1 --read/write/ioctl--> privileged AEE reader
        |
        +--> /proc/aed/*          [current crash records]
        |
        +--> IPANIC / MRDUMP / ATF logger persistence
        |
        `--> init + SELinux domain/socket policy for AEE userspace, where present
```

這不是一般 Android APK 的權限模型。公開 MediaTek Android 4.4 kernel
implementation 在 `aed-main.c` 中將兩個 misc device 綁定到 file operations，
包含 `read`、`write` 和 `unlocked_ioctl`，再由 `aed_init()` 註冊；同一檔案也
建立 `/proc/aed` 的 crash-report entries。這是 kernel/vendor crash-reporting
ABI，不是 AOSP `ActivityManager`、Java service 或 sideloaded app API。

## exact device 證據

| Evidence | 觀察 | 判定 |
|---|---|---|
| `P5Z-DEVICE-001` | `/dev/aed0`、`/dev/aed1` 存在，`root:root`、`0600`，SELinux type `aed_device` | **已證實** kernel device surface 存在 |
| `P5Z-DEVICE-002` | shell 的 `test -r`／`test -w` 對三個 node 全為 `0/0` | **已證實** normal ADB shell 無讀寫權限 |
| `P5Z-SOURCE-001` | exact MT8183 defconfig 開啟 `CONFIG_MTK_AEE_FEATURE`、`CONFIG_MTK_AEE_AED`、`CONFIG_MTK_AEE_IPANIC`、`CONFIG_MTK_AEE_MRDUMP`、`CONFIG_MTK_ATF_LOGGER` | **已證實** build/config 家族啟用 |
| `P5Z-DEVICE-003` | Phase 5X process/package/service/init snapshot 沒觀察到 userspace AEE daemon endpoint | **Strong evidence**，限於正常 runtime snapshot |
| `P5Z-SOURCE-002` | official source archive path-only inventory 完成，AEE/AED/MRDUMP/IPANIC filter 為 0 matches | **已證實** published archive listing 沒有 matching path；但不代表 source code 或 compiled code 不存在 |

原始輸出與 SHA-256：

- `adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-06/aee_nodes.stdout.txt`
- `adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-06/aee_access.stdout.txt`
- `artifacts/phase5/exact-kernel-source-review-20260804-01/members/mt8183_defconfig.e1495a4e51db.txt`
- `artifacts/phase5/exact-source-aee-paths-20260804-01/path-matches.txt`
- `artifacts/phase5/android-aee-implementation-review-20260804-04/`

## 公開 Android implementation 對照

公開 MediaTek Android 4.4 的 `aed-main.c` 提供了可讀的實作對照：

- `aed_ee_fops`／`aed_ke_fops` 分別接到 `aed0`／`aed1`，並含
  `open/release/poll/read/write/unlocked_ioctl`；
- `aed_proc_init()` 建立 `/proc/aed` 及 current exception entries；
- `aed_init()` 初始化 queue／waitqueue、註冊 kernel API，然後呼叫兩次
  `misc_register()`；
- kernel-side `aee-common.c` 以 `CONFIG_MTK_AEE_AED` 控制 exception API，將
  kernel／modem／combo exception 交給註冊的 AEE API。

這些公開檔案是 MTK Android 參考，不是 Amazon PS7330 的 binary proof。公開
MediaTek SELinux branch 另可看到 `aee_aed`／`aee_aedv` domain、`init_daemon_domain`
及對 `aed_device`、crash data、socket/property 的受限規則，說明 Android
userspace 端通常由受信任 daemon/domain 消費 AEE ABI，而不是由 shell 或普通 app
直接消費。

## GhostLock 的 Android 實作邊界

GhostLock（`CVE-2026-43499`）不是 AEE 漏洞；它是 Linux futex/rtmutex path。
Android 端最多是 native/Bionic 程式進入 futex PI syscall，真正錯誤位於 kernel。
NebuSec 的公開文章目前明確把 Android-specific exploitation 列為後續內容，
不能把 generic Linux/x86 chain 當成 Android implementation。

已保存的 `CyberMeowfia` public tree 具有 AArch64/Android NDK build plumbing，
但 captured target profiles 是其他 Google Android build；沒有
`KFTRWI`、`trona`、`MT8183` 或 `PS7330.4104N` target。不同 kernel build 的
compiled layout、KASLR、KPTI/CFI、SELinux、boot image 與 target header 不能
直接互換。

因此目前能交付的是「Android implementation reference map」，不是可在這台
Fire HD 10 執行的 Android root PoC。

## 結論分類

- **已證實：** exact Fire OS 有 AEE/AED kernel configuration 與
  `/dev/aed0`、`/dev/aed1` device surface。
- **已證實：** node 由 root 擁有、mode `0600`、SELinux 標為 `aed_device`；
  shell read/write check 為 `0/0`，本輪沒有開 node。
- **高可信推論：** 若 exact Fire OS 有可用 AEE userspace reader，它應位於
  privileged init/SELinux domain，而非一般 sideloaded APK。
- **待驗證：** exact PS7330 的 AEE daemon binary、init rule、SELinux policy、
  daemon patch status，以及是否有被改名／未公開的 AEE source member。官方
  archive 的完整串流 listing 已完成，但 AEE/AED/MRDUMP/IPANIC path filter 為
  0 matches；這是公開 source provenance 的限制，不是「AEE 不存在」的證明。
- **已排除：** 公開 MTK AEE source、相鄰 Android device profile 或
  `CyberMeowfia` target 可直接形成 KFTRWI root implementation。
- **因風險拒絕測試：** AEE node `open/read/write/ioctl`、malformed message、
  race/crash、reboot/dump、SELinux/property 修改、root payload、BROM/DA、
  fastboot、remount 與 partition write。

## 可重現分析

```sh
python3 tools/scripts/analyze_phase5z_android_aee.py --dry-run
python3 tools/scripts/analyze_phase5z_android_aee.py \
  --runtime-dir adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-06 \
  --exact-source-dir artifacts/phase5/exact-source-aee-paths-20260804-01 \
  --output artifacts/phase5/android-aee-implementation-review-20260804-04
```

分析器只讀既有 artifact；不執行 ADB、network、source、binary 或 device-node
操作。
