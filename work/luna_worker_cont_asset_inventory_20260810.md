# Host-only asset inventory — PS7331 / PS7330

盤點日期：2026-08-10（Asia/Taipei）  
範圍：`/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire`  
執行者：inventory worker

## 結論

- PS7331（Fire OS 7.3.3.1）主機端資產完整度高：有官方 source tarball `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2`、完整 OTA `.bin`、已解包 source tree、`boot.img`/`boot_unpacked`、重建的 `system.img`/`vendor.img`、`images/`、selected APK/JAR 與 compiled ODEX/VDEX。
- PS7331 OTA：1,301,005,356 bytes，SHA-256 `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`；其 OTA metadata 顯示 27 個 ZIP members，且已有 `ota.prop`、`system/build.prop`、compatibility manifests、updater script、target blocklist/path 等可供 OTA 靜態分析。
- PS7331 source tar：2,563,328,975 bytes，SHA-256 `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`。已解開 `platform.tar`、`fireos.tar` 並保留完整 source tree；source tree 檔案數約 173,559。
- `selected/system` 已保留 `framework-res.apk`、`framework.jar`、`services.jar`、`fosframework.jar`、`fosservices.jar`，以及 `com.amazon.firelauncher`、`TabletSystemUI`、`TabletSettings`、`SettingsProvider` APK。`compiled-02/system` 有 services/fosservices/boot framework 及 Amazon app 的 ODEX/VDEX。
- 7.3.3.0：有官方 source tar `firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2`，SHA-256 `569eca7321910b095f7af8905592f92e47610d302e6930fd27a6a5dee9593665`；已有 source member 抽取與 build/config 比較線索，但盤點證據顯示沒有可獨立驗證的同版 OTA、boot.img、preloader、LK、DA 或 recovery。
- 沒有執行 adb、root、Binder/service call、driver/ioctl、刷機、OTA/recovery，也沒有下載或執行檔案；本次只讀取既有 filesystem metadata、hash、manifest 與文字報告。新增/寫入的只有本報告與同名 CSV。

## 主要資產

| 類別 | 路徑 | 盤點結果與分析價值 |
|---|---|---|
| 官方 7.3.3.1 source tarball | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | 存在；可作 PS7331 kernel/source provenance、rtmutex/futex、build/config 與 Amazon driver source 分析輸入。 |
| PS7331 install/update `.bin` | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | 存在；與官方下載 route 的 content length 一致，hash 已由既有 manifest 保存；可作 OTA metadata、payload、APK/JAR 與 update flow 靜態分析輸入。 |
| 已解包 PS7331 source | `firmware/extracted/PS7331-SOURCE-20250617/` | 存在；含 `platform/`、`fireos/`、`apps/`、`platform.tar`、`fireos.tar`、kernel 4.4 source、Amazon driver source、build scripts。 |
| boot | `firmware/extracted/PS7331/boot.img` | 存在；Android boot image，既有 metadata 顯示 9,885,696 bytes，kernel gzip，kernel hash 亦已保存。 |
| boot_unpacked | `firmware/extracted/PS7331/boot_unpacked/` | 存在；含 `Image`、kernel/source-like headers、symbol/offset scripts、輸出與分析輔助檔；可作 boot/kernel 靜態分析。 |
| system/vendor images | `firmware/extracted/PS7331/system.img`, `vendor.img` | 存在；由 OTA transfer/new.dat 重建，既有 README 保存 image hashes；可作 filesystem/framework/vendor 靜態分析。 |
| low-level images | `firmware/extracted/PS7331/images/` | 存在；含 `preloader.img`、`lk.img`、`tee.img`、`sspm.img`、`spmfw.img`、`cam_vpu*.img`；屬高 mutation risk，只宜離線分析。 |
| framework/APK/JAR selected | `firmware/extracted/PS7331/selected/system/` | 存在；包含 Android framework、Fire OS framework/services 與 Amazon/Fire system priv-app，可直接支援 resolver/IPC/permission/system-server 靜態分析。 |
| compiled ODEX/VDEX | `firmware/extracted/PS7331/compiled-02/system/` | 存在；含 `services`、`fosservices`、`boot-framework`、`boot-fosframework` 及 Fire Launcher/TabletSystemUI/TabletSettings ODEX/VDEX；可支援 bytecode/inline/static correlation。 |
| hash/manifests | `firmware/manifests/`, `firmware/extracted/PS7331/{selected,compiled-02}/*manifest*` | 存在；有 OTA/source provenance、extraction manifests、sha256sums、build/command manifests。 |
| resolver/IPC/OTA analysis | `artifacts/phase6r/ota-ipc-static-audit-20260805-01/`, `artifacts/phase6bk/ipc-ota-closure-20260810-01/`, `artifacts/phase6j/ota-contracts-ps7331-jadx-20260805-01/`, `decompiled/jadx/ota-PS7331/`, `decompiled/baksmali/ota-PS7331/` | 存在；是既有主機端報告/反編譯輸出，可直接用於 resolver、IPC、OTA contract/receiver/method map 靜態分析；不得誤標為 PS7330 精確證據。 |

## 7.3.3.0 差異線索（非完整重解包）

1. 7.3.3.0 source archive 已存在，且既有 `ps7330-full-source-members-20260804-01` 保存 selected member extraction metadata；7.3.3.1 source archive 另有完整 source tree 與 PS7331 selected members。
2. 既有比較 `artifacts/phase5/phase5ba-ps7331-upgrade-comparison-20260804-01/comparison.csv` 顯示 kernel config 為 `DIFFERENT_NORMALIZED`；PS7330 的 exact rtmutex source 比較輸入缺失，因此該線索不能推導完整 binary diff。
3. 7.3.3.0 build identity 線索為 `PS7330.4104N/0030099376128`；PS7331 OTA metadata 線索為 `PS7331.4463N/0031575863040`。PS7331 OTA 是 adjacent/reference artifact，不應當作 7.3.3.0 installed firmware。
4. 7.3.3.0 目前沒有同版、可獨立驗證的 OTA/boot/system/vendor 影像；其 source archive 可作 source-level 對比，但不能填補 binary/image 缺口。

## Missing edges / limitations

- 官方 PS7331 source tarball 本體、OTA 本體與解包映像均是高 mutation-risk artifact；本次未重建、覆寫或執行任何內容。
- 目錄與 aggregate artifact 的 `sha256` 欄位填 `UNKNOWN`，因 `sha256sum` 對目錄不提供單一 canonical digest；可用其內部 manifest 或個別檔案 hash。
- 7.3.3.1 source tree 內存在大量第三方/一般 framework JAR；本盤點只列與 Fire framework、system APK/JAR、resolver/IPC/OTA 直接相關的集合，不將所有 173,559 個 source file 展開成 CSV rows。
- 「是否可直接用於分析」僅表示檔案在主機端存在且可被離線工具讀取，不表示已執行或驗證其內容，也不表示可安全寫回裝置。

## 產出

- [CSV inventory](luna_worker_cont_asset_inventory_20260810.csv)
- 本檔案與 CSV 均為本次新建輸出；既有資產未修改。
