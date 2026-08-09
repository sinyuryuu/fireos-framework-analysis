# Phase 6 — OTA/Post-install 與 GPL/kernel source audit

日期：2026-08-10；scope：Fire OS 7.3.3.1 / PS7331 / trona，僅主機端唯讀
firmware、artifacts、decompiled、findings 與既有 ADB 證據。沒有執行 OTA、Recovery、
`update-binary`、`otadexopt` mutating command、Binder replay、ioctl、root、reboot、
partition write、symlink/traversal test 或安裝任何 payload。本檔是本次唯一輸出。

## 結論摘要

| 問題 | 判定 | 信心 |
|---|---|---|
| 7.3.3.1 OTA 資料格式 | official Java/JAR-like BIN，內含 ZIP OTA members；此包是傳統 Edify/block-image，不是 A/B `payload.bin` 路徑 | 高（member inventory、hash、script） |
| `META-INF/update-binary` / block-image | `main → RegisterInstallFunctions/RegisterBlockImageFunction → function registry → handlers → extraction/write`；固定 system/vendor/boot-chain targets | 高（static CFG/offset） |
| post-install | package 有 native updater 與 `/cache/recovery/last_blocklist` extraction；未觀察到獨立 `postinstall`、`payload.bin` 或 dynamic post-install helper | 中高（known members；外層 source tar EOF limitation 不可外推） |
| `otadexopt` | `SystemServer → OtaDexoptService`，可見標準 shell bridge；是 dexopt state/artifact surface，不是 partition writer、HOME writer 或 root route | 高（VDEX locations + saved Test） |
| shell/普通 APK 高權限 writer | 未建立普通 shell/APK → recovery updater/partition writer 的 caller chain；高權限 writer capability 存在，但 reachability 不成立 | 高（6BK/6KT/6KU） |
| GPL source | 含 MT8183 4.4 kernel、Amazon driver、MTK drivers；沒有 Android userspace `system/core/init` 或完整 Amazon framework source | 高（archive member scope） |
| debug/factory ioctl surface | source-visible：AUXADC ioctl、MTK proc/sysfs/debug、Amazon test proc；量產 config、node mode、SELinux、caller 未完全閉合，不作 exploit 結論 | 高（source）；中（shipped/reachable） |

核心限制：以下「有 capability」不等於「低權限可達」；static string、proc/ioctl
marker、缺少 local `capable()` 或存在 service name 都不能單獨升格為漏洞。

## 1. 7.3.3.1 OTA format 與實際 package path

主要 package：

* `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`
  SHA-256 `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`。
* extracted `firmware/extracted/PS7331/` 的 `members.json`（既有 artifact
  `artifacts/phase6i/phase6i-ota-postinstall-20260804-01/members.json`）列出
  `META-INF/com/android/metadata`、`otacert`、`META-INF/com/google/android/update-binary`
  （compressed 806075 / uncompressed 1749792）、`updater-script`、`system.new.dat.br`、
  `vendor.new.dat.br`、兩個 transfer list、`boot.img`、`images/*.img`、`ota.prop`。
* `update-binary` SHA-256
  `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`；
  `updater-script` SHA-256
  `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`；
  `META-INF/com/android/otacert` SHA-256
  `5d52405362dcc9e755a4d972074ac7f886a5450e18fb6a6c2c2dad2b55730fe1`。

`artifacts/phase6i/.../ota-findings.csv:1-36` 與
`artifacts/phase6i/.../summary.json` 保存了 format/member、target 與狀態：
`partition_written=false`、`updater_executed=false`。`updater-script` 的實際 lines
為 1-24（Phase 6KT table；report hash
`484273958f44898c6b94a208da4e144936df09a191e03efe6316c18d167fe732`）：

```text
6   block_image_update(/dev/block/.../system, system.transfer.list, system.new.dat.br, system.patch.dat)
10  block_image_update(/dev/block/.../vendor, vendor.transfer.list, vendor.new.dat.br, vendor.patch.dat)
13  package_extract_file(boot.img, /dev/block/.../boot)
15-23 package_extract_file(images/*.img, /dev/block/.../preloader,lK,tee1,tee2,spmfw,sspm_1,cam_vpu1-3)
24  package_extract_file(META-INF/com/amazon/android/target.blocklist, /cache/recovery/last_blocklist)
```

因此這是傳統 signed Edify/block-image OTA：有 `system.new.dat.br` / transfer-list，
但既有 member set 沒有 `payload.bin`、A/B `postinstall` executable 或 dynamic
post-install script。這是 package-scoped finding，不排除未分析 corpus 的其他 OTA。

## 2. `update-binary`、block-image、verification 與權限邊界

### 2.1 Static code path

既有 Phase 6MK report（SHA-256
`443c69127293d18903d469f7a670a4b58b208cdbf6402c240ecaeec6e307ecb3`）與 Phase 6MM
（SHA-256 `f0caa7e810d02f0022180371e0b564f2cef13cd19ed7320fde107a8073d58601`）給出：

```text
main 0x400cb0
 ├─ RegisterInstallFunctions 0x400cac
 │   └─ RegisterFunction 0x41d528
 │       └─ package_extract_file → PackageExtractFileFn 0x401fb8–0x402788
 │           └─ ota_open → libc open at 0x426354; extract → fsync → close
 └─ RegisterBlockImageFunction 0x40d0a8
     └─ RegisterFunction 0x41d528
         ├─ block_image_verify  cell 0x5af670 → 0x407c48
         ├─ block_image_update cell 0x5af678 → 0x40b8b8
         ├─ block_image_recover cell 0x5af680 → 0x40cbc0
         ├─ check_first_block cell 0x5af688 → 0x40c858
         └─ range_sha1       cell 0x5af690 → 0x40c328
             └─ PerformBlockImageUpdate → CacheSizeCheck → … → WriteToPartition
```

可重現位置：`artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt:216-218`
（main registration）、Phase 6MM report registration table，及
`artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv`。
`PackageExtractFileFn` direct sites 為 focus disassembly `:938-945,1008-1015,1056-1064,1100-1115`
與 Phase 6MK report；`WriteToPartition` 為 `0x413c40–0x4142f0`，`ota_open` 為
`0x426338–0x426528`、`open` call `0x426354`（Phase 6KT）。

### 2.2 Verification/canonicalization boundary

Java-side provenance 是：

```text
OSUpdateValidator.java:42-48,72-77
  → RecoverySystemWrapper.java:21-22
  → RecoverySystem.verifyPackage()
SideloadInstaller.java:65-74
  → SideloadVerifier.verifySideloadWithoutRecoveryCheck()
  → SideloadMover.java:29-43
  → UpdateSystemWrapper.java:32-43
  → UpdateSystem.install()
```

這些位置來自 Phase 6KT（report SHA-256 `484273...fe732`）；Java verification/staging
與 recovery/native updater handoff 是分開 boundary，平台 verifier implementation
未在本 scope 執行或完整 recover。`MakeFreeSpaceOnCache + 0x478 = 0x417bf0 →
__readlink_chk 0x4ce4e8` 已證實；Phase 6MM selected graph 未見其直接連到 write
sink，但 `CacheSizeCheck` body、indirect dispatch、input provenance 未閉合。故不宣稱
symlink bypass、traversal、任意 file/partition write 或 signature bypass。

### 2.3 Post-install / A/B disposition

Phase 6FE report（SHA-256 `1de3ecc97b520f45981a906f09800d646c4f60d02fb58bcdf3a900a282526d23`）
的 bounded source-tar/member audit 對 known top-level/nested members 找不到
`postinstall`、`run_program`、`otadexopt`、`payload.bin`、recovery/system/vendor helper；
已知 18 nested archives 也沒有 system-server/PMS/HOME writer。外層 bzip2 未完成 EOF，
所以只可作 known-member negative，不能作完整 archive negative。

## 3. `otadexopt` 實際 path、shell/API boundary

Phase 6AF report（SHA-256 `77e4cb0b922ce78485c786379e366590af7a55bc1d585e589d9d9eb0f3f6892b`）
與 `artifacts/phase6af/otadexopt-implementation-closure-20260805-02/implementation.json`
保存：

* installed PS7331 services VDEX 有 `com.android.server.pm.OtaDexoptService`；
  `main(Context, PackageManagerService)` 在 disassembly `:482249-482263` 建立並發布
  `otadexopt`，同時移動 A/B artifacts。
* `SystemServer` 啟動 gate 在 `:107990-108045`（`mOnlyCore` / `config.disable_otadexopt`）。
* `onShellCommand()` `:482598-482611` 委派 `OtaDexoptShellCommand`；
  `prepare()` `:482613-482734` 會建立 dexopt command list、低空間時可能刪除 OAT；
  `nextDexoptCommand()` `:482533-482597` 可移除/清空 command state；`cleanup()`
  `:482460-482478` 清理 state；本次未呼叫 mutating commands。
* 已保存 Test ID `PHASE6AE-STATUS-20260805-01` 的唯讀 capture：
  `cmd otadexopt done` 到達 `OtaDexoptService.java:176`、
  `OtaDexoptShellCommand.java:76`、`IOtaDexopt$Stub.onTransact` 並回傳
  `IllegalStateException: done() called before prepare()`；`progress` 回傳 `1.00`。
  這證明 shell-visible service/precondition path，不證明低權限可做 package/partition write。

Phase 6BK saved service check `adb/phase6bk/PHASE6BK-SERVICE-RO-20260810-01/service_list.stdout.txt:155`
記錄 `otadexopt`，而 Amazon private services 對 shell 查找是 `not found`；
`findings/phase-6bk-report.md` SHA-256 `16c9084559cf7014682c7a6755dd2fcfbaad63024277d48acb7abf8b4550e5b5`。
這條 service visibility 不應被解讀為 arbitrary Binder transaction 或 recovery updater
authority。Phase 6AF 也明確沒有 HOME selector、Fire Launcher comparison、privilege
transition 或 root path。

## 4. 是否存在 shell / ordinary APK 可達高權限 writer

### 判定：未建立；capability 與 reachability 分離

已證實的 writer capability：

1. native `WriteToPartition`、`PackageExtractFileFn`、`block_image_update`：recovery/update
   context 的 named partition writer；不是 ordinary shell API。
2. `BootAfterSystemOTAReceiver` 是 system-server upgrade lifecycle writer：
   `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96107-96126`；
   receiver 可寫 OOBE/setup state、啟用 `OobeHomeActivity`，但 sender 在 boot phase
   550 且 `PackageManagerService.isUpgrade()` gate，並非普通 HOME API。
3. `OtaDexoptService` 可改 dexopt command/OAT state，但未見 partition/HOME/root sink。

既有可達性 evidence：

* Phase 6BK OTA section：沒有 ordinary app/shell → recovery updater/partition write
  完整 caller chain；未做 malformed OTA、sideload、recovery 或 partition write。
* Phase 6KU（work inventory 收錄於 `work/luna_worker_ota_inventory_20260810.md`）
  將 ordinary prewarm 限於 process/resource effect，KFT tx3 受 PMS gates，private
  Amazon PM 沒有 HOME/package-state setter；updater 是 recovery-context capability。
* `BootAfterSystemOTAReceiver` 的 receiver-permission argument 不是 sender authentication；
  action 名稱不構成 shell/app caller proof。既有 Test IDs `6U-OOBE-001`, `6U-OOBE-002`,
  `6U-OTA-001`, `6W-PB-001`, `6Y-OTA-001..009` 僅支持 lifecycle/provenance boundary。

所以答案是：**沒有目前證據支持 shell 或普通 APK 可達的高權限 partition/HOME writer**。
這是 saved corpus 的 bounded negative，不是對未保存 components 的宇宙性否定。

## 5. GPL/source provenance 與 kernel surfaces

### 5.1 Archive scope

官方 source archive：`firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2`
SHA-256 `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`。
Nested `platform.tar` SHA-256
`69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`；
`fireos.tar` SHA-256 `bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369`。

`platform.tar` 有 generic `system/core`（主要 libcutils/logwrapper），但沒有
`platform/system/core/init/`、`selinux.cpp`、frameworks/base 或 Amazon framework。
`fireos.tar` 亦無 Android userspace `system/core/init`。存在的是 kernel `init/main.c`
（不是 Android `/init`）及 build-side `install_policy.sh`；不能把它們當成量產 Android
init policy-loader source。此判定由 `work/luna_worker_phase6mv_gpl_ota_inventory_20260810.md`
（SHA-256 `d151b1aef4295d15c5ff4efc7c59ab2b0a66cce8c4da2273046b8a76c6d97378`）與
`findings/phase-6an-gpl-scope.md`（SHA-256 `b310fb2eb5e6024ec3426755db53782d1d2019ed61987f1b464969496620e342`）一致。

### 5.2 Amazon drivers

Build-selected root 是
`firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4`，
`kernel/source-manifest.json` SHA-256
`ada254be9c56572282704924eea66e2852889ec73c0a65be4558f36f77d8250a`。
Amazon path 實際是 `drivers/staging/amazon/` / `device/amazon/kernel/driver/`，不是
`drivers/amazon/`。代表 source hashes：

* `amzn_idme.c` `ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e`；
  `idme_init():302-356`，proc root `:316`，child permission 剝除 write bits `:337-344`，
  restricted child owner `:346-347`。
* `amzn_drv_test.c` `6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e`；
  `proc_write():747-781` 使用 `copy_from_user():762-763`，`test_fops.write():784-790`；
  `amzn_drv_test_init():792-843` 建立 `/proc/amzn_drv` 下三個 `S_IRUGO|S_IWUSR`
  children `:811-812,825-826,840-841`，module init `:866`。
  這是 source-visible test writer，非已證量產 node 或普通 APK-to-root route。

### 5.3 MediaTek debug/factory/ioctl surface

代表 source：`drivers/misc/mediatek/auxadc/mtk_auxadc.c` SHA-256
`5ffbce942417fc6aca773d90e4c6935f508087f9a80d96138a7ecc30561ed327`。

* `auxadc_cali_unlocked_ioctl():553-625` 有 calibration commands、
  `copy_from_user()` `:568-569,583-584,593-594,609-612`；fops 綁定
  `:661-668`。這證明 ioctl source surface，不證明量產 device node 的 Unix mode、
  SELinux label 或 ordinary caller。
* `mtk_memcfg.c` SHA-256 `fb1f13f8a15c79554461235a6a6487f4cf36e5e05e4139f3b93c97445b59df08`：
  `CONFIG_MTK_ENG_BUILD` 下 `:671-703` 有 writable debug fops；`/proc/mtk_memcfg`
  建立與 mode `S_IRUGO|S_IWUSR` entries 在 `:705-765`。config gate 與量產 exposure
  未完整閉合，故不當成 debug route。
* 既有 `artifacts/phase6g/phase6g-cmdq-static-20260804-01/cmdq-static.json`
  SHA-256 `021e02c2143901a757cd63eb79fae975b52d01b6efda7fef1c2113fb42d3c638` 保存
  `/dev/mtk_cmdq`、`unlocked_ioctl`、named CMDQ requests；這只支持 source/static
  driver surface。

既有 driver-wide inventory（Phase 6ME）為 1,671 files、1,726 ioctl markers、703
proc/sysfs/debugfs markers，且明確寫 `runtime_reachability: not-derived-from-source`
與無 framework/launcher sink。這些 surfaces 不得轉述成 exploit、root 或 HOME writer。

## 6. 最終 provenance / reachability matrix

| Route | Sink/capability | caller / gate | 判定 |
|---|---|---|---|
| Signed OTA → updater | named block/boot partition writes | recovery/update context；Java verify/stage 與 native handoff 分離 | capability 高；ordinary reachability 未建立（高） |
| OTA package → post-install | `/cache/recovery/last_blocklist`; no known `postinstall`/A-B payload member | fixed script lines 6-24；no execution | known package negative（中高） |
| SystemServer → otadexopt | dexopt command/OAT state | published `otadexopt`; shell command bridge; mutating commands not called | shell-visible adjacent service；非 partition/HOME writer（高） |
| BOOT_AFTER_SYSTEM_OTA | OOBE prefs/component state | boot phase 550 + `isUpgrade()` + system lifecycle | trusted lifecycle writer；ordinary replay 未建立（高） |
| Amazon test proc | driver test state | source Kconfig/default and final config/image/node/SELinux unresolved | source-only capability（中） |
| MTK AUXADC/mem/CMDQ | ioctl/proc/sysfs/debug controls | node mode/SELinux/config/caller unresolved | static surface only（高） |
| GPL `system/core/init` | userspace init provenance | absent from released source corpus | source absent；binary modification unknown（高） |

## 7. Scope stop / non-claims

不宣稱：symlink/traversal bypass、任意 file/partition write、signature/version bypass、
普通 APK 提權、root、HOME replacement、Amazon `/init` modification、任何 driver ioctl
漏洞。未來若要縮小 OTA gap，只允許 host-only 選取 `CacheSizeCheck`、
`MakeFreeSpaceOnCache` callers、function-pointer/return-value dataflow；不得用 crafted
OTA、updater execution、Recovery、sideload、ioctl payload、symlink 或 partition write
補足靜態缺口。

## 8. Evidence/Test ID index

`6I-POST`、`6P-OTA-001..004`、`6P-PATH-001`、`6KT-001`、`6MK-001`、`6MM-001..002`、
`6AF-OTADEXOPT`（既有 `PHASE6AE-STATUS-20260805-01` capture）、`6BK-OTA-001`、
`6U-OOBE-001/002/005/006/007`、`6U-OTA-001`、`6W-PB-001`、`6Y-OTA-001..009`、
`6N`、`6BR`、`6ME`、`6G`。Test IDs 是既有 evidence labels；本次沒有新增 device test。
