# Phase 6TP：PS7331 OTA/update-binary/post-install 靜態安全稽核

日期：2026-08-10。範圍限於主機端既有的 OTA manifest、`updater-script`、`update-binary` 保存反組譯，以及 phase6MK/phase6NE artifacts。未下載、構造、修改或執行 OTA；未執行 recovery、sideload、flash、reboot、裝置命令或分割區寫入。

## 結論

保存證據支持的 capability 是：此 OTA script 宣告 system/vendor 與 boot/firmware block targets；native updater registry 靜態解析出 `package_extract_file`、`write_value`、`run_program` 等 handler；選定的 `WriteToPartition`、`ota_open`、`ota_write` 路徑包含原始 I/O 呼叫；cache helper 遍歷目錄並使用 `stat64`、`__readlink_chk`、`unlink`。這些是 LOCAL_ONLY 或 DERIVED_OUTPUT 的靜態能力，不能推論為可由不可信 caller 達成的提權。

輸入驗證方面，script 只直接保存了 build-date/device predicates；這不等同於完整的 package signature、AVB、recovery authentication 或 caller authorization 證明。`write_value` 僅在 registry 中出現，未在本保存 script 中被呼叫。symlink/TOCTOU 與 canonicalization 的完整資料流未閉合：selected graph 的 bounded negative 不是 binary-wide absence；亦沒有 runtime path test。因此相關項目標為 UNKNOWN。

## 證據分級與 claim boundary

CSV 是本稽核逐項索引；每列均含 path、SHA-256、line/offset、分類與 claim boundary。分類語意如下：

- `LOCAL_ONLY`：保存於主機端的 firmware/script 或主機端執行邊界紀錄。
- `DERIVED_OUTPUT`：既有 phase6MK/phase6NE 或保存反組譯產生的分析結果。
- `PUBLIC_CONFIRMED`：本輪沒有新增此類證據；未以公開資料替代本地保存證據。
- `UNKNOWN`：證據不足以確認，尤其是 symlink/TOCTOU、完整輸入驗證、caller/authentication 與 runtime reachability。

不報告以下未被證據支持的 claim：可利用 payload、任意檔案覆寫、symlink traversal、TOCTOU exploit、signature/AVB bypass、shell/ADB 可達更新入口、recovery 實際執行、root 或提權。

## 來源完整性

- `firmware/extracted/PS7331/META-INF/com/google/android/updater-script` — SHA-256 `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`
- `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` — SHA-256 `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`
- `artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt` — SHA-256 `0e780e51ced6f7b000bf0a821ffe6cfe81bc0108e6073174b7fa0cb0b94abdcd`
- `artifacts/phase6mk-updater-dispatch-20260810-04/summary.json` — SHA-256 `4cf463ec498b74e6460fb598f7ce5e5756418aaa5c2ac5767009c22e9c29b9fe`
- `artifacts/phase6ne-updater-cache-flow-20260810-02/direct-call-edges.csv` — SHA-256 `d653e4a84898509781a333c56502087a83981781fcf6612d7026bfd79602b477`

## 安全邊界

本報告僅描述保存證據中的靜態 capability 與缺口。沒有 OTA/recovery/sideload/flash/reboot 操作，沒有裝置接觸，沒有 payload，也沒有把任何 capability 宣告為可達提權。
