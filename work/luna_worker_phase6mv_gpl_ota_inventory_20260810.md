# Phase 6MV — PS7331 GPL / official package / boot-image inventory

日期：2026-08-10  
基準 worktree HEAD：`65c61429fb53769b0ac5bb0adb051dd5371e5c9c`

## Scope and safety

本報告只整理目前 worktree 已保存的檔案與既有 host-only 結果。沒有執行
`adb`、`service call`、Binder transaction、`ioctl`、reboot、settings/package
mutation、Root/exploit，也沒有停用或 force-stop Fire Launcher；沒有執行
`update-binary`、Recovery、OTA、sideload、flash 或任何分割區寫入。未修改既有
檔案；本報告是唯一新增檔案。

分類：**Confirmed** = 檔案內容/雜湊/靜態命中直接可見；**Strong** = 多份既有
靜態或保存結果相互支持，但不是 runtime 執行證據；**Pending** = corpus 或
控制流仍不足；**Rejected** = 在本安全範圍或該輸入中已排除，不代表宇宙性不存在。

## 1. 官方 source tarball

### 外層官方 source archive — Confirmed / 已被 Phase 6MI、6IV 引用

| 檔案 | SHA-256 | 實際內容/命中 |
|---|---|---|
| `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` | 2,563,328,975 bytes；35 members（23 regular、12 directories、0 symlink、0 hardlink）；`README.txt`、`build_kernel.sh`、`build_kernel_config.sh`、`fireos.tar`、`platform.tar`、apps source roots |
| `artifacts/phase6mi-source-tar-eof-20260810-03/summary.json` | `409ed81ede46db87a0ef8a05cc33b99df2b66e068d1edc1ac481a42e0606169b` | 完整讀至 tar EOF；0 post-install/update/recovery/partition member-name hits；2 launcher hits |
| `artifacts/phase6mi-source-tar-eof-20260810-03/sensitive-member-hits.tsv` | （由 phase6mi sha manifest 保存） | `apps/com.amazon.firelauncher`；`apps/com.amazon.firelauncher/javax.annotation-api-1.2.tar.gz` |

外層未命中 `META-INF`、`updater-script`、`update-binary`、`postinstall`、
`run_program`、partition/image control、`payload.bin`、`system/`、`vendor/`、
`boot/` 或 `recovery/`。這是 **Confirmed/Rejected** 的負面 member-name
boundary：source archive 不是第二份可安裝 OTA，也不是隱藏的 launcher writer。

### GPL nested archives — Confirmed / 已被 Phase 6AN、6C.5、6MI 引用

| 檔案 | SHA-256 | 實際內容/搜尋命中 |
|---|---|---|
| `firmware/extracted/PS7331-SOURCE-20250617/fireos.tar` | `bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369` | 53,549 members；`packages/apps` 僅 `SpareParts` 三個 path；無 `system/core/init`、`frameworks/base`、Amazon namespace、`selinux.cpp`、deny-list symbols |
| `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` | 138,574 members；150 generic `system/core` paths，主要為 `libcutils`/`logwrapper` 等；無 `system/core/init`、`selinux.cpp`、`frameworks/base`、Amazon namespace、`PackageWhitelister`/`DenyListArcus`/`fdrw` member path |
| `output/tables/phase6an-gpl-scope.csv` | `16fc58fcfb0390896cadaabbb6a47769fd584c9bc0c8aa7335d24f3bdb5ca6e0` | 機器可讀的 member-path scope 結果 |
| `findings/phase-6an-gpl-scope.md` | `b310fb2eb5e6024ec3426755db53782d1d2019ed61987f1b464969496620e342` | Phase 6AN 結論：有限 kernel/platform/open-source release，不是完整 Amazon framework/resource source |
| `findings/phase-6c5-gpl-source-scope.md` | `54cf005f30ebf85ac4e8a592097f527cb2ef8f0d1d4f36fabbc049e79ae32786` | Phase 6C.5 結論：本 tarball 沒有 Amazon `/init` source；不能由此否定 binary `/init` modification |

### Source files with direct PS7331 relevance — Confirmed

| 檔案 | SHA-256 | 命中/結論 |
|---|---|---|
| `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/kernel/futex.c` | `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96` | MT8183 4.4 futex/PI-requeue implementation；kernel surface evidence，非 HOME/OTA writer |
| `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | `remove_waiter()`、proxy-lock path；Phase 5BT 的 GhostLock provenance source |
| `firmware/extracted/PS7331-SOURCE-20250617/platform/device/amazon/kernel/driver/amzn_idme.c` | `ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e` | Amazon IDME driver source；Phase 6N kernel userspace-surface inventory scope |
| `firmware/extracted/PS7331-SOURCE-20250617/platform/device/amazon/kernel/driver/amzn_keycombo.c` | `09e19712f177e0740a96964f420f74adda3412442b65d6df5cec8187e38e6071` | Amazon key-combo driver source；未形成 PackageManager/HOME chain |
| `firmware/extracted/PS7331-SOURCE-20250617/platform/system/core/libcutils/android_reboot.cpp` | `1ced73c938e3b607672ee8ab28aee778e081127bad2ceadaa262ac2b8ad08f20` | generic reboot helper source；非 Amazon `/init` policy loader，未執行 |

`findings/phase-5bt-ps7331-full-source-audit.md`（SHA-256
`3dbf2cb0601fee687350a6ddff1f42e732c44f225171a1227242d387d872ce00`）已引用
`rtmutex.c` 與 boot image cross-check。`findings/phase-6n-kernel-surface-index.md`
已引用 source root 與 Amazon driver surface；它明確沒有找到新的 HOME-control
path。

**結論（Confirmed/Strong）：** GPL source 可支持 PS7331 kernel、Amazon
device-driver 與有限 platform provenance；不能支持 Amazon `/init`、private
framework、package deny-list resource 或 OTA post-install implementation 的
完整 source provenance。將「沒有 `system/core/init`」解讀成「binary `/init`
沒有 Amazon 修改」是 **Rejected**。

## 2. Official installation package and extracted payloads

### Official package container — Confirmed / 已被 Phase 5BH、6I 引用

| 檔案 | SHA-256 | 實際內容 |
|---|---|---|
| `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | Java/JAR-format official OTA package；Phase 5BH records official PS7331 mapping and source metadata |
| `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` | native updater binary；未執行 |
| `firmware/extracted/PS7331/META-INF/com/google/android/updater-script` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` | 27-member package contract；包含 `block_image_update`/`package_extract_file` targets |
| `firmware/extracted/PS7331/META-INF/com/android/otacert` | `5d52405362dcc9e755a4d972074ac7f886a5450e18fb6a6c2c2dad2b55730fe1` | OTA certificate member |
| `firmware/extracted/PS7331/ota.prop` | `f91b4c792339c605d81a2d6d5e819fee5d522a7514111daa1468717e07319ded` | package metadata |
| `firmware/extracted/PS7331/system.transfer.list` | `b1121308588b1ded9bc497a13fe971d2269f2e63ec0236f9d7bed2d3fef91105` | system block-image transfer metadata |
| `firmware/extracted/PS7331/vendor.transfer.list` | `82d5326c371b02ee7dbfe8f90ac43033f11906fef4783c70d6e00f488210d14c` | vendor block-image transfer metadata |

既有 Phase 6I（`findings/phase-6i-ota-postinstall.md`, SHA-256
`577f0f09ff35ecae081249faf165d717e24e04beab80b7c4a2da2a2b47f38129`）確認：
OTA 具有 boot/system/vendor 與 firmware targets；唯一 cache/data-like extraction
是 `/cache/recovery/last_blocklist`，不是 launcher selector。其狀態為
`partition_written=false`、`updater_executed=false`。

### Extracted images — Confirmed; execution status Rejected

| 檔案 | SHA-256 | `file`/內容摘要 |
|---|---|---|
| `firmware/extracted/PS7331/boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` | Android boot image；gzip kernel；9,885,696 bytes；cmdline `buildvariant=user` |
| `firmware/extracted/PS7331/system.img` | `da8a935484de24251e890fbf4e7dd9155567ebe158fc255d43684ea14c62b1e5` | ext2/extents system image，UUID `6158e611-cc57-5d86-97e0-2b567b360d4d` |
| `firmware/extracted/PS7331/vendor.img` | `d1db5a5349d046361710bd6966adb7ef88dc4ddc550295e8c1926cb279f213eb` | ext2/extents vendor image，label `vendor` |
| `firmware/extracted/PS7331/compatibility.zip` | `587223c87a1b3a266539abd0325c370c77a1cb132bf05128bcd3f3301596f112` | compatibility metadata |
| `firmware/extracted/PS7331/images/preloader.img` / `lk.img` / `tee.img` / `spmfw.img` / `sspm.img` / `cam_vpu1.img`–`3.img` | 個別檔案存在；本報告未重複展開 hash 表 | firmware image members referenced by updater script |

Boot metadata：`artifacts/phase5/ps7331-boot-image-inspection-20260804-01/boot-image-metadata.json`
SHA-256 `32831b97cd2af84897889a69b480c2c2af60dbb3598e444678c41cba3ec7305c`；其中
kernel SHA-256 `a608a5f99c155dc8e8b12b308528cbd17175b47199985d017613f9e2fbb1edba`。
`findings/phase-5bt-ps7331-full-source-audit.md` 已用此 boot image 做 source/Image
semantic cross-check；不代表單獨 boot image 等價於完整 OTA。

### Selected system/framework and launcher payload — Confirmed / 已被既有 launcher reports 引用

| 檔案 | SHA-256 | 實際內容 |
|---|---|---|
| `firmware/extracted/PS7331/selected/system/framework/fosframework.jar` | `ef1491b8850be6d6cab0101d6b4fcf34e1dabb13cd2d08e3d72e615ddb21d188` | Amazon framework selected payload |
| `firmware/extracted/PS7331/selected/system/framework/fosservices.jar` | `364603c0228058973ed976ff1bef51c3cab2fa8fc163ec63c727157bb92dec96` | Amazon system-service selected payload |
| `firmware/extracted/PS7331/selected/system/framework/framework-res.apk` | `7a405abe0f721719cb5d8a280ac551f86880a70227d923e04dd922109ce8a35e` | framework resources, including runtime resource evidence used by deny-list work |
| `firmware/extracted/PS7331/selected/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk` | `ee8201f5499b9d01d2f6fe1685a3e756d7429990c68e6b490b2f38466d09b8d3` | Fire Launcher APK |
| `firmware/extracted/PS7331/selected/system/priv-app/TabletSystemUI/TabletSystemUI.apk` | `2c4f9940d9d7e57192300771ce856a9fde68a877a666191553992d9959dc3b0d` | Tablet SystemUI APK |
| `firmware/extracted/PS7331/selected/system/priv-app/TabletSettings/TabletSettings.apk` | `26aefbf94b32de342f568eff4ec46e97212e3cbb2cc2c44b2558058076bf0c3e` | Tablet Settings APK |
| `firmware/extracted/PS7331/selected/system/priv-app/SettingsProvider/SettingsProvider.apk` | `71022834bbea12ebba134988decc682dd1d70ce57cdedc95ad92eadd1b67800a` | SettingsProvider APK |

Additional metadata: `firmware/extracted/PS7331/system/build.prop` SHA-256
`068b257362514773113671a7be67ff1288c484382ee43694872a19dbcb93e15e`.
Compiled copies are present under `firmware/extracted/PS7331/compiled-02/system/`
and include `fosservices.vdex`, `services.vdex`, `boot-fosframework.vdex`, and the
Fire Launcher oat/vdex pair. These paths are the runtime artifacts used by the Phase
6 framework/launcher static reports; they are not GPL source.

## 3. Kernel/system/init/OTA/post-install search ledger

| Surface | Host paths / hits | Status | Existing citation |
|---|---|---|---|
| Kernel source | `platform/kernel/mediatek/mt8183/4.4/`; futex/rtmutex/reboot and Amazon driver files | **Confirmed** | Phase 5BT, 6N, 6FU; no HOME/PackageManager feed established |
| Amazon device kernel | `platform/device/amazon/kernel/driver/{amzn_idme.c,amzn_keycombo.c,amzn_logger.c,amzn_sign_of_life*.c}` plus headers/docs | **Confirmed** | Phase 6N/6BR; userspace surfaces are driver/node evidence, not launcher control |
| `/init` GPL source | No `platform/system/core/init/`, `selinux.cpp`, `selinux.h` in `fireos.tar` or `platform.tar` | **Confirmed absence in tar member scope** | Phase 6AN/6C.5; binary `/init` diff remains **Pending** |
| Generic system/core | `platform/system/core/libcutils`, `logwrapper`, headers; `android_reboot.cpp` present | **Confirmed** | Phase 6AN; not complete init implementation |
| Official updater | `META-INF/.../update-binary`, `updater-script`, block-image and extraction functions | **Confirmed static** | Phase 6MK/6MM/6MD/6AH |
| Post-install member | No new top-level source member; OTA metadata contains fixed updater contract and cache recovery blocklist extraction | **Confirmed / Rejected as hidden source post-install** | Phase 6FE/6I |
| Path/canonicalization | updater markers `readlink`, `readlinkat`, `realpath`, `symlink_realpath`; Phase 6MM has `MakeFreeSpaceOnCache → __readlink_chk` | **Strong; full dataflow Pending** | Phase 6MK/6MM/6MD; no traversal or bypass conclusion |
| Amazon framework/services | selected jars and compiled `fosservices`/`services` artifacts; private service methods analyzed in Phases 6BK/6MN–6MU | **Confirmed artifacts; caller/runtime reachability varies** | Phase 6 reports; no OTA execution implied |
| Fire Launcher OTA prefix | `apps/com.amazon.firelauncher/` source prefix only contains `javax.annotation-api-1.2.tar.gz` nested dependency | **Confirmed bounded negative** | `output/tables/phase6fw-firelauncher-ota-prefix.csv`, SHA-256 `28858056a5f04cd42166c12fc215fdf2811fe516659ba70b8b25b4dfedae7d4d` |

## 4. Existing Phase 6 / launcher test evidence

The following are preserved results, not actions performed in this inventory:

* `output/rendered/phase-1-report.phase2-final10.md`, SHA-256
  `fceb478a496783037c5236c6688ff123f0b8714e5b8469303d5d82ecd6e7ee41`: recorded
  unlocked HOME tests resolving to `com.amazon.firelauncher/.Launcher`, preferred
  Microsoft record not outranking Fire, and protected-package failures. These are
  historical device-test artifacts and were not rerun.
* `output/tables/phase5ax-boot-readonly.csv`, SHA-256
  `9ff5405c4d838e5001d76e6703f666ae39cec635972dc1162e74dc89729f41b9`: preserved
  read-only boot/partition metadata boundary and Fire foreground snapshot.
* `output/tables/phase6mi-source-tar-summary-20260810-03.csv`, SHA-256
  `8b577855f3ef674380231c89b65c86d233309d59984ef07fb38601408e9061d9`: 35-member
  EOF-complete source summary, 0 post-install hits, 2 launcher-name hits.
* `output/tables/phase6fe-ota-top-level-postinstall.csv`, SHA-256
  `14190aa9edcce090c8c8c1b760a7af6d33bdb7cf5d89b3394646b84dd37863b7`: 0 new
  top-level post-install/update members; nested archives deferred in that phase.
* `output/tables/phase6fw-firelauncher-ota-prefix.csv` (hash above): launcher source
  prefix negative result; other app archive prefixes were outside that bounded phase.

## 5. Supported conclusions and remaining gaps

### Confirmed

1. The saved 7.3.3.1 GPL distribution is complete at the outer tar EOF and contains
   finite nested `fireos.tar`/`platform.tar` source scopes.
2. The GPL release contains selected MT8183 kernel and Amazon device-driver source,
   but no Amazon framework, complete `/init`, or package deny-list source tree.
3. The official installation package contains boot/system/vendor and firmware update
   payloads, an updater binary, and a script whose static target set includes
   partition writes.
4. Boot/system/vendor images and selected Amazon framework/Fire Launcher payloads are
   present locally with the hashes above.

### Strong

1. Existing Phase 6 static analyses establish updater dispatch, block-image handlers,
   extraction, partition-I/O edges, and a separate cache/path helper boundary.
2. Existing launcher evidence establishes Fire Launcher as the tested HOME result and
   a protected package boundary; the source/OTA inventory adds no alternate launcher
   writer.

### Pending

1. Complete system/product/vendor resource inventory for resource package ID `0x7e`
   and exact deny-list provenance remains a binary/resource task, not a GPL-source
   task.
2. Full indirect-call/dataflow and argument/order analysis from updater
   canonicalization markers to extraction/write paths remains bounded by the existing
   Phase 6MK/6MM reports; no runtime OTA test is appropriate.
3. Any release-CI, private overlay, generated source, or post-processing absent from
   the saved GPL corpus remains outside this inventory.
4. The saved source outer archive's nested third-party archives are inventory members;
   no new nested archive execution or expansion was performed here.

### Rejected

* GPL tarball as a complete Amazon `/init`/framework source release.
* Outer source archive as a hidden installable OTA or post-install launcher writer.
* Standalone `boot.img` as an equivalent full PS7331 upgrade.
* Any claim that static updater write capability proves the official OTA was executed,
  or that it provides an ADB/shell/Binder launcher replacement route.
* Any exploit, Root, recovery, reboot, package mutation, Fire Launcher disable or
  force-stop action.

## Worktree handoff

Only `work/luna_worker_phase6mv_gpl_ota_inventory_20260810.md` was added. No existing
file was edited; no commit or push was performed.
