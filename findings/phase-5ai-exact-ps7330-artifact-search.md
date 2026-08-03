# Phase 5AI：PS7330 exact boot／preloader artifact 搜尋結果

## 目的

本輪不是執行刷機或 bootloader 操作，而是確認是否已具備能支撐低層研究的 exact artifact：

- `PS7330.4104N` 對應的 `boot.img`／`vbmeta`／`dtbo`；
- exact `trona` preloader、LK、TEE、DA 或 recovery set；
- 可驗證來源、版本、簽名／hash 與 rollback context。

## 結果

**已證實：** 目前工作區沒有完整的 PS7330 OTA 或 exact PS7330 boot-chain set。`firmware/original/` 唯一完整檔案是 `update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`；其解包檔案只能標記 `VERSION_MISMATCH`。

**已證實：** Amazon 公開更新頁目前把 Fire HD 10 (11th Generation) 列為 Fire OS 7.3.3.1，提供一個手動更新入口；頁面沒有列出 PS7330.4104N 的檔名或 exact historical package：[Amazon Fire Tablet Software Updates](https://digprjsurvey.amazon.co.uk/csad/help/node/G2JXLC4L34GX73TE)。點擊公開入口時回傳 503，沒有把其內容當作已取得的檔案。

**高可信推論：** 沒有合法、完整、與 `PS7330.4104N` 完全匹配的 boot／preloader artifact，就不能可靠計算本機 GhostLock offset，也不能選擇安全的 MTK loader／DA，更不能把 PS7331 當成 recovery。

## Artifact inventory

| Artifact | 本地狀態 | Version relation | 可否作 exact PS7330 input |
|---|---|---|---|
| Installed Android runtime properties | 已保存於 `adb/phase5/PHASE5AH-DEVICE-READONLY-20260804-01/` | PS7330.4104N | 可作 identity／runtime evidence；不是 boot image |
| `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | 已保存 | PS7331.4463N / Fire OS 7.3.3.1 | 否，VERSION_MISMATCH |
| `firmware/extracted/PS7331/images/boot.img` | 已解包 | PS7331 | 否；只能作相鄰版本比較 |
| `firmware/extracted/PS7331/images/preloader.img` | 已解包 | PS7331 | 否；不能當 PS7330 loader |
| `firmware/extracted/PS7331/images/lk.img` | 已解包 | PS7331 | 否；不能當 PS7330 recovery |
| Public `PS7330` GitHub code search | 無 exact result | search-bounded | 否 |
| Public `KFTRWI/trona` preloader/DA search | 無可驗證 exact image | search-bounded | 否 |

## Search set

固定搜尋：

1. `"PS7330.4104N" firmware`
2. `"trona_fireos_ship_7330"`
3. `"Fire HD 10" "PS7330.4104N" OTA`
4. `"KFTRWI" "PS7330"`
5. GitHub `PS7330 + trona`、`KFTRWI + boot.img`、`KFTRWI + preloader`。
6. Fire HD 10 11th-gen root／bootloader／custom ROM、`MT8183 Android 9` local privilege escalation。

結果大多是使用者 agent／benchmark／一般裝置資訊、舊 Fire 世代資料或其他 MT8183 裝置；沒有可驗證的 PS7330 signed image、hash、loader、DA 或 recovery mapping。這個搜尋結論受限於公開索引與目前日期，不能證明私有或未索引資料不存在。

## Why adjacent PS7331 is not a recovery set

既有 PS7331 updater script 已證明完整 OTA 可能寫入 boot、preloader、LK、TEE、SPMFW、SSPM 等低層分割區；既有 preloader strings 也包含 DA authentication／RPMB rollback 相關邊界。這使「只因 product 同為 `trona` 就寫入 PS7331」不能被視為可逆測試。

**因風險拒絕測試：** 不 sideload PS7331、不寫入 preloader/LK/boot/vbmeta、不嘗試 seccfg／rollback、不用 generic DA 連接實機。缺 exact PS7330 recovery、loader、DA/auth 與 rollback procedure 時，寫入結果不能形成可分析的 root 證據，反而可能切斷 ADB／fastboot 恢復路徑。

## Current decision

- **已證實：** exact runtime capture 已存在，且設備仍為 `KFTRWI/trona/PS7330.4104N`、green verified boot、`flash.locked=1`、SELinux Enforcing。
- **已證實：** local firmware set 只有 PS7331 adjacent OTA。
- **高可信推論：** 目前不能安全產生本機 GhostLock／MTK boot-chain target offsets。
- **待驗證：** Amazon 是否曾公開或私下分發完整 PS7330 package；目前沒有合法 exact file。
- **已排除：** 將 PS7331 或其他 MT8183 device image 視為本機 recovery／exploit input。
- **因風險拒絕測試：** any flash／sideload／BROM／DA／preloader／LK／seccfg 操作。

## Next useful input

只有下列任一項出現，才值得重新評估 host-only low-level analysis：

1. 可驗證來源的完整 PS7330.4104N OTA／boot image；
2. 帶有 `trona/KFTRWI/PS7330` 明確 profile 的公開 root／boot-chain source；
3. 可交叉驗證的 PS7330 preloader／DA／rollback metadata。

在此之前，最小安全研究仍是維持 Android-side foreground redirect 的使用者授權測量；它不會取得 system UID，也不會改變正式 HOME resolver。
