# Phase 6AH：PS7331 `update-binary` 驗證到寫入控制流閉合

## 範圍與安全狀態

本階段完全在主機端執行，使用既有的官方 PS7331 OTA 解包檔、已保存的
AArch64 函式清單、直接 call-edge 報告與 bounded disassembly。沒有執行
`update-binary`、recovery、OTA、OOBE、分割區寫入、任何裝置命令或未知
Binder transaction。`BootAfterSystemOTAReceiver` 仍維持 Phase 6AG 的靜態、
非可採用研究項目；本階段沒有觸發它。

分析時間（UTC）：`2026-08-04T23:37:00.092164+00:00`

## 結論摘要

**已證實（靜態）：**官方 `updater-script` 請求兩個 `block_image_update`
目標（system、vendor），並請求將 `boot.img`、preloader、LK、TEE、SPMFW、
SSPM、camera VPU 等檔案寫入明確的 block-device 路徑。這是 OTA 套件的
寫入意圖，不是本機已執行證據。

**已證實（靜態）：**`main` 直接呼叫 `RegisterInstallFunctions`、
`RegisterBlockImageFunctions` 及 `Evaluate`。`RegisterInstallFunctions` 的
保存 call-edge 報告含 24 次 `RegisterFunction` 呼叫；block-image 函式則以
保存的 wrapper disassembly 將 `BlockImageVerifyFn`／`BlockImageUpdateFn`
無條件分支到 `PerformBlockImageUpdate`，分別帶入 mode 1／0。

**已證實（靜態）：**`LoadSrcTgtVersion3` 有兩條直接 edge 到
`VerifyBlocks`；`VerifyBlocks` 的 bounded disassembly 顯示 SHA-1 計算、
摘要／資料比較及 mismatch 分支。這閉合了驗證 helper 的存在與呼叫邊界。

**已證實（靜態）：**`PerformBlockImageUpdate` 直接使用 OTA I/O helper，
`WriteToPartition` 的函式本體直接呼叫 `ota_open`、`ota_write`、`ota_fsync`
及相關 `lseek`／錯誤路徑；`ota_open`／`ota_write` 又各自有 libc
`open`／`write` direct edge。這證明 binary 中存在從輸入路徑到原始 I/O
的寫入能力。

**高可信推論：**若 recovery 以該 script 啟動此 binary，資料驅動的
expression registry 可把 `package_extract_file`／`block_image_update`
導向上述函式，形成驗證後的 OTA 寫入流程。因 function-pointer／registry
dispatch 不是普通 direct BL，不能把這一段標成完整的 direct-call proof。

**無法由本階段確認：**recovery 是否在這台設備的一次實際 OTA 中執行了
此 binary；全包簽章、AVB／recovery 前置驗證的完整控制流；以及是否有任何
shell／ADB 可達入口。沒有證據支持繞過驗證或取得額外權限。

## 來源與雜湊

| 證據 | 路徑 | SHA-256 |
|---|---|---|
| OTA binary | `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` |
| updater script | `firmware/extracted/PS7331/META-INF/com/google/android/updater-script` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` |
| selected functions | `artifacts/phase6s/ota-cfg-focus-20260805-01/selected-functions.csv` | `adbf977955846e529d4a9bc44c5b499494a94e529b2e01c60b4731091dc7374d` |
| direct call edges | `artifacts/phase6s/ota-call-edges-20260805-01/call-edges.csv` | `ede44312f2f667adff552475866de0b17c06b96161854c35a17a3a1c361eaa75` |
| bounded disassembly | `artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt` | `0e780e51ced6f7b000bf0a821ffe6cfe81bc0108e6073174b7fa0cb0b94abdcd` |

## Script 寫入目標

| Script line | Command | Target | Classification | Status |
|---:|---|---|---|---|
| 13 | `package_extract_file` | `/dev/block/platform/bootdevice/by-name/boot` | `boot_or_firmware_partition_write` | `NOT_EXECUTED |
| 15 | `package_extract_file` | `/dev/block/platform/bootdevice/by-name/preloader` | `boot_or_firmware_partition_write` | `NOT_EXECUTED |
| 16 | `package_extract_file` | `/dev/block/platform/bootdevice/by-name/lk` | `boot_or_firmware_partition_write` | `NOT_EXECUTED |
| 17 | `package_extract_file` | `/dev/block/platform/bootdevice/by-name/tee1` | `boot_or_firmware_partition_write` | `NOT_EXECUTED |
| 18 | `package_extract_file` | `/dev/block/platform/bootdevice/by-name/tee2` | `boot_or_firmware_partition_write` | `NOT_EXECUTED |
| 19 | `package_extract_file` | `/dev/block/platform/bootdevice/by-name/spmfw` | `boot_or_firmware_partition_write` | `NOT_EXECUTED |
| 20 | `package_extract_file` | `/dev/block/platform/bootdevice/by-name/sspm_1` | `boot_or_firmware_partition_write` | `NOT_EXECUTED |
| 21 | `package_extract_file` | `/dev/block/platform/bootdevice/by-name/cam_vpu1` | `boot_or_firmware_partition_write` | `NOT_EXECUTED |
| 22 | `package_extract_file` | `/dev/block/platform/bootdevice/by-name/cam_vpu2` | `boot_or_firmware_partition_write` | `NOT_EXECUTED |
| 23 | `package_extract_file` | `/dev/block/platform/bootdevice/by-name/cam_vpu3` | `boot_or_firmware_partition_write` | `NOT_EXECUTED |

## 最小控制流

1. `main` 註冊函式表並呼叫 `Evaluate`。
2. `Evaluate` 依 parsed expression 查找註冊函式；此處是資料驅動 dispatch，
   保存的 direct edge 報告不假裝知道每個 function pointer 的實際 call-site。
3. `BlockImageVerifyFn`／`BlockImageUpdateFn` 以 unconditional branch 進入
   `PerformBlockImageUpdate`。
4. source/target 版本流程進入 `VerifyBlocks`；摘要不符走錯誤／拒絕分支。
5. 更新／extract 流程使用 `ota_open`、`ota_write`、`ota_fsync`；
   `WriteToPartition` 的 body 也保留原始 I/O 路徑。

精確 stage、位置、證據 ID 與限制見
`output/tables/phase6ah-update-binary-control-flow.csv` 及
`output/call-graphs/phase6ah-update-binary-control-flow.mmd`。

## 證據分級

| Finding | Confidence | 說明 |
|---|---|---|
| 官方 script 具有 system/vendor/boot/firmware 寫入目標 | 已證實（靜態） | 只表示套件內容與宣告目標 |
| main → registration → Evaluate | 已證實（direct edge） | 來自保存的 AArch64 call-edge |
| block-image wrapper → PerformBlockImageUpdate | 已證實（bounded disassembly） | 為 unconditional branch，非 BL |
| LoadSrcTgtVersion3 → VerifyBlocks | 已證實（direct edge） | 兩個保存的 call-site |
| 驗證後可進入原始 I/O 寫入 helper | 高可信推論 | registry/indirect dispatch 仍需在 host 端進一步解碼 |
| recovery 實際執行本 binary | 待驗證 | 本階段禁止以 OTA 觸發 |
| shell/ADB 可達更新寫入入口 | 已排除（目前證據） | 未找到安全、文件化的 shell caller；不是對所有未來版本的絕對否定 |
| 可繞過簽章/驗證或取得 root | 無證據 | 不由這份 CFG 得出 |

## 明確拒絕的裝置測試

以下不在本階段執行：把 OTA 放入裝置並啟動更新、手動呼叫 recovery/OOBE
流程、發送 `BOOT_AFTER_SYSTEM_OTA`、執行 `update-binary`、測試 crafted 或
malformed OTA、讀寫任何 block device、未知 Binder transaction、Root/提權
驗證。這些操作可能造成分割區改寫、無法開機或資料遺失，與目前的無損
研究邊界不相容。

## 下一個最低風險分析目標

只在主機端解碼 `RegisterBlockImageFunctions` 與 expression registry 的
字串／function-pointer 對應，並把 `package_extract_file`、
`block_image_update` 的 callback 連到已確認的 helper。這可以縮小
`高可信推論` 的不確定性，仍不需要執行 OTA 或修改設備。
