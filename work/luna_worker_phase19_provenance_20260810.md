# Phase 19E — PS7331 provenance/build alignment（host-only）

日期：2026-08-10。只讀核對工作區已保存的 source、OTA、image、config、manifest 與 runtime fingerprint；未下載、未執行保存的 ELF/script/tool、未連接或操作設備，亦未修改既有檔案。此輪只新增本報告與同名 CSV。

## 結論

保存的 `Fire_HD10-7.3.3.1-20250617.tar.bz2`、其 `platform.tar`/`fireos.tar`、PS7331 kernel source/config、PS7331 `boot.img`/kernel/Image、PS7331 OTA/bin、`ota.prop`、`build.prop` 與 selected/compiled extraction manifests，均對齊 PS7331 的版本族：Fire OS 7.3.3.1、`PS7331.4463N`、product/device `trona`、Amazon/MTK8183、Android API 28、security patch 2024-08-01。

它們不是 exact installed PS7330 artifacts。保存的 2026-08-03 PS7330 baseline 是 Fire OS 7.3.3.0 / `PS7330.4104N` / incremental `0030099376128` / security patch 2024-02-01；PS7330 source archive 亦是另一個 7.3.3.0 input。PS7331 與 PS7330 共享 `trona`/MT8183 等 product family，不能因此互標 exact-match。

保存的 runtime fingerprint 有兩個時間切片：

- 2026-08-03 baseline：`Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys`，exact PS7330 baseline。
- 2026-08-10 多個唯讀 fingerprint logs：`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`，exact PS7331 identity；這是已保存輸出，不是本輪重新查設備，也不以此推論未保存的現況。

## Provenance / SHA-256 對照

| 項目 | 保存檔案／證據 | SHA-256 或內容 | 判定 |
|---|---|---|---|
| PS7331 outer source tar | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`；2,563,328,975 bytes；35 members；reached EOF | **exact PS7331 source input** |
| PS7331 platform source tar | `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` | **exact PS7331 nested source member** |
| PS7331 FireOS source tar | `firmware/extracted/PS7331-SOURCE-20250617/fireos.tar` | `bb7030296545dd45edcf47d3e742043e7813852844f4b0fbbe8d223899b369` | **exact PS7331 nested source member** |
| PS7330 comparison source | `firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2` | `569eca7321910b095f7af8905592f92e47610d302e6930fd27a6a5dee9593665` | **not PS7331; exact PS7330 source input** |
| PS7331 kernel config | `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config` | `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04` | **PS7331 config evidence** |
| PS7331 boot image | `firmware/extracted/PS7331/boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` | **PS7331 adjacent/reference boot; not exact PS7330 boot** |
| PS7331 unpacked kernel | `firmware/extracted/PS7331/boot_unpacked/kernel` | `a608a5f99c155dc8e8b12b308528cbd17175b47199985d017613f9e2fbb1edba` | **PS7331 unpacked kernel; not exact PS7330 booted kernel** |
| PS7331 unpacked ARM64 Image | `firmware/extracted/PS7331/boot_unpacked/Image` | `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d` | **PS7331 Image; not exact PS7330 Image** |
| PS7331 OTA/bin | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | **exact PS7331 full BLOCK OTA package** |
| OTA property file | `firmware/extracted/PS7331/ota.prop` | `f91b4c792339c605d81a2d6d5e819fee5d522a7514111daa1468717e07319ded`; `product=trona`, `Fire OS 7.3.3.1 (PS7331.4463N/4463)`, `version_number=0031575863172`, `release-keys` | **exact PS7331 OTA metadata** |
| System build properties | `firmware/extracted/PS7331/system/build.prop` | SHA-256 not present in the saved manifests reviewed in this phase; content gives `ro.build.mktg.fireos=Fire OS 7.3.3.1`, `ro.build.id/display.id=PS7331.4463N`, `ro.product.name/device/board=trona`, fingerprint below, `ro.build.version.security_patch=2024-08-01` | **PS7331 content; hash not re-computed under no-external-tool constraint** |
| selected manifest | `firmware/extracted/PS7331/selected/manifest.sha256` | `b098f85287a729d03cfac1ac6f767a3ba6a15ce8c65d7f9e581cbbed75448a74` (hash of `selected/extraction-manifest.tsv`) | **PS7331 selected extraction manifest** |
| compiled manifest | `firmware/extracted/PS7331/compiled-02/manifest.sha256` | `7da7040b4c7454084d8c30452edc05d4c68ce3813fe20700d4016036e4097716` (hash of `compiled-02/extraction-manifest.tsv`) | **PS7331 compiled extraction manifest** |

註：outer source tar 的保存摘要明確記錄 `extracted=false`, `executed=false`, `device_mutation=false`；這是 provenance boundary，不是對 source member 內容的 build/reproducibility attestation。

## Version / device / product / fingerprint alignment

| 欄位 | PS7331 saved OTA/source/image side | PS7330 saved baseline | Alignment |
|---|---|---|---|
| Fire OS | `7.3.3.1` | `7.3.3.0` | 不同版本；PS7331 side exact only |
| Build ID | `PS7331.4463N` | `PS7330.4104N` | 不同 build；不可互標 |
| Incremental | OTA `0031575863172`; post-build incremental `0031575863172` | `0030099376128` | 不同 |
| Product/device/board | `trona` / `trona` / `trona` | `trona` / `trona` / `trona` | family 相同，非 exact build |
| Product model | source/OTA properties identify Amazon trona package; saved PS7330 model is `KFTRWI` | `KFTRWI` | product family context only |
| SoC/kernel | MT8183; Android 9/API 28; Linux 4.4.146+ evidence | MT8183; Android 9/API 28; Linux 4.4.146+ baseline evidence | family/config scope aligns, binary exactness未證 |
| Build fingerprint | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` | `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys` | exact identities differ |
| Security patch | `2024-08-01` (`ota.prop`, `metadata`, `build.prop`) | `2024-02-01` (baseline properties) | 明確不同 |
| Signing/build tags | `user/amz-p,release-keys`; `release-keys` | `user/amz-p,release-keys` | signing/tag family same; version仍不同 |

## Kernel source/config/build alignment

PS7331 source build path保存了 `platform/kernel/mediatek/mt8183/4.4` 與 `arch/arm64/configs/trona_defconfig`；保存的 merged/embedded config hash 是 `eefb8d…d013d04`，且 config content 具備 ARM64、Linux 4.4.146、FUTEX/RT_MUTEXES 等選項。這可支持「PS7331 source/config scope 與 PS7331 image provenance 對齊」；不能支持 source-to-signed-Image 的可重現 build attestation，也不能產生 exact PS7330 signed kernel。

既有 source comparison 顯示 PS7330 build-selected 與 PS7331 build-selected 的 `rtmutex.c`/`futex.c` bytes 相同，但兩者仍來自不同 release source archives；此結果是 scoped source-path equality，不是兩個完整 Fire OS builds 或 signed images 的 exact identity。

## 明確分類

### Exact PS7331（保存證據可直接支持）

- 7.3.3.1 outer source tar 與其 `platform.tar`、`fireos.tar` nested source members。
- PS7331 `kernel.config`、PS7331 `boot.img`、其 unpacked `kernel`/`Image`。
- PS7331 full BLOCK OTA/bin、`ota.prop`、`META-INF/com/android/metadata` 的 PS7331 post-build/security patch identity。
- PS7331 `system/build.prop` 的 version/product/fingerprint/security-patch fields。
- PS7331 selected/compiled extraction manifests 及其保存 manifest hashes。
- 2026-08-10 保存的 runtime fingerprint logs（內容為 PS7331.4463N）；僅代表保存時的 runtime evidence。

### 不是 exact PS7330（不可拿來代表已安裝 PS7330）

- 上述所有 PS7331 source/OTA/image/config/prop/manifest artifacts。
- PS7331 `boot.img` 或 `Image` 單獨替代 PS7330 boot/kernel。
- PS7331 OTA/bin 作為 PS7330 exact package；版本、incremental、fingerprint、security patch 均不同。
- PS7331 source/config 對 PS7330 的完整 build/reproducible provenance；目前沒有 exact PS7330 signed `boot.img`/`Image` hash。

### Exact PS7330 baseline（僅保存的基線）

- `device/baseline/BASELINE-20260803-04` 的 properties：Fire OS 7.3.3.0、`PS7330.4104N`、`0030099376128`、fingerprint `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys`、security patch 2024-02-01、device/product/board `trona`、model `KFTRWI`。
- `firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2`，SHA-256 `569eca7321910b095f7af8905592f92e47610d302e6930fd27a6a5dee9593665`。
- 2026-08-03 baseline 是保存的 PS7330 runtime slice；本輪未重新查設備，亦未把 2026-08-10 PS7331 log 解讀成 live state。

## Scope gaps / handoff

1. `build.prop` 的 SHA-256 未在既有 selected/compiled manifest 或 phase manifest 中保存；在「不執行外部工具」約束下本輪不重算，故只做內容欄位核對。
2. 工作區保存的是 PS7331 signed/derived boot artifacts，沒有 exact PS7330 signed `boot.img`、PS7330 kernel/Image 的可核對 hash。
3. source/config/image 對齊是 provenance/version alignment，不是 reproducible build proof；未執行 build、ELF、recovery、updater 或 device validation。
4. runtime fingerprint 的 PS7330/PS7331 差異按保存日期分層記錄；若需判定設備此刻狀態，必須另行取得授權且本 Phase 不執行。
