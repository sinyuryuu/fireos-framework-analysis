# Phase 6AW：PS7331 官方 OTA write contract

## 範圍與安全狀態

本階段只解析已保存的 PS7331 OTA `updater-script`、`metadata`、`ota.prop` 及
先前保存的 `update-binary` host-only call-edge 分析。沒有執行 updater、recovery
或 OTA，沒有把檔案放入裝置，沒有發送 broadcast，沒有讀寫任何 block device。

工具與輸出：

- `tools/scripts/build_phase6aw_ota_write_contract.py`
- `artifacts/phase6aw/ota-write-contract-20260805-02/`
- `output/tables/phase6aw-ota-write-contract.csv`
- `output/call-graphs/phase6aw-ota-write-contract.mmd`

## 版本與前置條件

保存的 package metadata：

- `pre-device=trona`
- `post-build=Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- `post-build-incremental=0031575863172`
- `post-security-patch-level=2024-08-01`
- `ota-type=BLOCK`
- `ota.prop`: `Fire OS 7.3.3.1 (PS7331.4463N/4463)`、`release-keys`、`full`

`updater-script` 另有 `ro.build.date.utc` 與 `ro.product.device == "trona"`
前置檢查。這些是相容性／生命週期 gate，不是 shell 可寫的 launcher state。

## 已證實（靜態）

1. script 的 `block_image_update()` 目標是：
   `/dev/block/platform/bootdevice/by-name/system` 與 `vendor`。

2. script 的 `package_extract_file()` 直接指向：
   `boot`、`preloader`、`lk`、`tee1`、`tee2`、`spmfw`、`sspm_1`、
   `cam_vpu1`、`cam_vpu2`、`cam_vpu3`，並寫入 `/cache/recovery/last_blocklist`。

3. 既有 Phase 6AH 的 `update-binary` 靜態 call-edge／bounded disassembly 已
   對上函式註冊、expression evaluation、block-image handlers、verification
   helpers 及 `ota_open`／`ota_write`／`ota_fsync` I/O 邊界。這證明 binary 具有
   這些操作的程式能力，但不表示在設備上已執行。

## 判定

### 高可信推論

這不是可逆的 ADB launcher workaround，也不是適合用來測試 system service 的
普通 userspace package。即使 package 是官方 signed artifact，執行它仍進入
recovery／OTA 的高影響寫入生命週期。

### 待驗證

- recovery native layer 的完整 canonicalization、signature／AVB 前置檢查與
  atomicity control flow；這些不應在 retail device 上用 crafted package 補測。
- 自然官方 OTA 後的 OOBE 時序；目前沒有人工觸發 `BOOT_AFTER_SYSTEM_OTA`。

### 因風險拒絕測試

- OTA install／sideload、recovery execution、malformed 或 symlink payload、
  downgrade、bootloader／fastboot、任何 partition write。

## 結論

7.3.3.1 的 source／boot／OTA provenance 對離線研究很有價值，但它沒有提供一個
可安全執行的 root 或 launcher 控制入口。以目前證據，OTA／OOBE 應維持為高影響
lifecycle boundary，而非 workaround。
