# Phase 6I：PS7331 OTA post-install surface

## 範圍

這是主機端 ZIP metadata、既有 updater-script 與已解包檔案的靜態稽核。
沒有執行 `update-binary`，沒有製造 malformed OTA、symlink/path-traversal
package，也沒有 sideload、recovery、fastboot 或任何分割區寫入。

輸入 OTA：

`firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`

SHA-256：`9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`。

Canonical artifact：`artifacts/phase6i/phase6i-ota-postinstall-20260804-01/`。

## 已證實

- ZIP 有 27 個 members。
- 存在 `update-binary`、`updater-script`、boot image、system payload、vendor
  payload 與 compatibility metadata。
- updater metadata 包含 `block_image_update`／`package_extract_file`，目標
  包括：

```text
system vendor boot preloader lk tee1 tee2 spmfw sspm_1
cam_vpu1 cam_vpu2 cam_vpu3
```

- 唯一 cache/data 類輸出是 recovery blocklist 到
  `/cache/recovery/last_blocklist` 的 package extraction；這不是安全的
  launcher/userspace selector。
- `partition_written=false`、`updater_executed=false`：本次 artifact 只保留
  分析結果，沒有寫入裝置。

## 判定

### 高可信推論

這是完整更新交易，不是可以在 ADB shell 內安全、局部還原的控制面。即使
官方 package 可信，執行它仍可能更新 boot chain 與 system/vendor，不能當成
`/init` rootable policy 研究的低風險實驗。

### 待驗證

recovery/update-binary 的 staging、簽章與 path handling implementation 尚未
做動態驗證；這些不是目前需要在真機上驗證的問題。

### 因風險拒絕測試

- OTA install/sideload。
- 修改 OTA ZIP、替換 symlink 或測試 traversal。
- 執行 update-binary。
- bootloader/fastboot、recovery 或分割區寫入。

## 可重現命令

```text
python3 tools/scripts/audit_phase6i_ota_postinstall_surface.py \
  --ota firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin \
  --metadata-root artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01 \
  --extracted-root firmware/extracted/PS7331 \
  --output artifacts/phase6i/phase6i-ota-postinstall-YYYYMMDD-01
```

工具只做 host-only inventory，且不執行 OTA member。
