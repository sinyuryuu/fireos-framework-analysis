# Phase 5T — PS7330 OTA／boot-chain metadata 只讀採集

## 結果

本輪使用新的 read-only collector，沒有啟動 OTA、sideload、reboot、fastboot
或任何寫入。原始輸出位於：

`adb/phase5/PHASE5T-OTA-METADATA-20260804-01/`

關鍵 metadata：

| 欄位 | 值 |
|---|---|
| Build fingerprint | `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys` |
| Fire OS marketing | `Fire OS 7.3.3.0` |
| Build name | `Fire OS 7.3.3.0 (PS7330/4104)` |
| Lab project | `trona_fireos_ship_7330` |
| Build date | `Sat Jul 13 02:04:35 UTC 2024` |
| Incremental | `0030099376260` |
| Security patch | `2024-02-01` |
| MediaTek branch | `alps-mp-p0.mp1.tc6sp` |
| MediaTek release | `alps-mp-p0.mp1.tc6sp-of.p12` |
| Preloader descriptor | `d1a4a4b-20231011_072631`, version `0x010b` |
| LK descriptor | `79172a1-20231008_072039`, version `0x010a` |
| HOME | `com.amazon.firelauncher/.Launcher`, effective priority 50 |

## OTA/cache 可見性

Shell 只讀列舉結果：

- `/cache`：Permission denied；
- `/data/ota`：Permission denied；
- `/data/ota_package`：Permission denied；
- `/data/local/tmp` 可列舉，但沒有 OTA image；只看到既有 `.flo` 檔與
  shell 可用的暫存目錄；
- package path 可確認 OTA／provisioning 相關 APK 存在，但沒有從 package
  metadata 得到 exact PS7330 update payload URL。

因此這次採集沒有取得新的 PS7330 `boot.img`、`lk.img`、preloader 或 DA。
它也沒有把任何受限目錄的 Permission denied 誤判成「檔案不存在」。

## 分級結論

### 已證實

- 裝置 build identity 可以更精確地連到 `trona_fireos_ship_7330`、build
  4104 與 MediaTek branch/release。
- Android shell 可以讀取 PL/LK descriptor，但不能由此取得 boot-chain image。
- OTA/cache 目錄對 shell 不可讀，HOME 仍解析到 Fire Launcher。
- collector 只讀取 property、package path、目錄 listing 與 HOME resolver；
  沒有裝置狀態變更。

### 高可信推論

- 這些 metadata 可用來驗證未來取得的官方 artifact 是否宣稱對應 PS7330，
  但 descriptor 本身不足以重建或選擇 DA/preloader。
- 沒有 exact signed PS7330 boot-chain image，`fenrir`、`lkpatcher` 或 offset
  payload 仍不能進入可解釋的 live test。

### 待驗證

- `d1a4a4b` PL 與 `79172a1` LK descriptor 對應的官方 binary 是否仍可合法
  取得，以及其 hash 是否與裝置匹配。
- Amazon 是否有未公開的 update service endpoint 只在受控權限下回傳 payload。

### 因風險拒絕測試

- 讀取 block device、提取 `/dev/block/.../lk` 或 preloader；
- 進入 BROM/DA、上傳 loader、修改 seccfg/RPMB；
- 使用 PS7331 或其他版本的 boot-chain image 做 PS7330 測試。

## 重現

```sh
tools/scripts/capture_phase5t_ota_metadata.sh \
  --serial G001LT0511550CFT \
  --test-id PHASE5T-OTA-METADATA-YYYYMMDD-01 \
  --output adb/phase5/PHASE5T-OTA-METADATA-YYYYMMDD-01 \
  --dry-run
```

移除 `--dry-run` 後才會執行同樣的唯讀採集；腳本拒絕覆寫既有輸出，要求
明確 serial，並保存每條命令、stdout、stderr、exit code 與 SHA-256。
