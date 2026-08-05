# Phase 6BI：PS7331 OTA updater 函式級寫入邊界

## 範圍與結論先行

本階段只對已保存的 PS7331 `update-binary` 做主機端 ELF／`.gnu_debugdata`／
AArch64 反組譯分析。沒有執行 updater、沒有進入 recovery、沒有送出 OTA、沒有
連接 ADB，也沒有寫入裝置或任何分割區。

目前最重要的結果是：官方 updater 內確實存在一條高權限的檔案／分割區寫入
程式結構，但現有證據沒有把它連到 shell、普通 app 或可偽造 OTA 輸入。因此這是
「高影響能力邊界」，不是已確認的提權或 path-traversal 漏洞。

## 輸入與可重現性

```sh
python3 -c 'import py_compile; py_compile.compile("tools/scripts/audit_phase6p_gnu_debugdata.py", doraise=True); py_compile.compile("tools/scripts/audit_phase6bi_ota_write_boundary.py", doraise=True)'

python3 tools/scripts/audit_phase6p_gnu_debugdata.py \
  --binary firmware/extracted/PS7331/META-INF/com/google/android/update-binary \
  --output artifacts/phase6bi/update-binary-debugdata-20260805-01

python3 tools/scripts/audit_phase6bi_ota_write_boundary.py \
  --disassembly artifacts/phase6p/callback-ota-audit-20260805-02/native/text-disassembly.txt \
  --symbols artifacts/phase6bi/update-binary-debugdata-20260805-01/symbols.csv \
  --output artifacts/phase6bi/write-boundary-20260805-01
```

分析腳本只解析檔案 bytes、符號與文字反組譯；其輸出明確記錄
`device_contacted=false`、`updater_executed=false`、`recovery_executed=false`、
`partition_written=false`（Evidence `PH6BI-OTA-008`）。

## 已證實

### 1. 輸入 provenance 與符號恢復

- `update-binary` 是 PS7331 OTA 中保存的 ELF64 AArch64 updater；原始檔 SHA-256
  為 `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`。
- `.gnu_debugdata` 可解壓成 AArch64 mini-ELF，包含 2,886 個符號；其中包括
  `PackageExtractFileFn`、`ExtractEntryToFile`、`WriteToPartition`、
  `PerformBlockImageUpdate`、`ota_open`、`ota_write`、`ota_fsync`、
  `MakeFreeSpaceOnCache` 與 `__readlink_chk`。
- 完整 `.text` 反組譯與 debugdata symbol address 能對應；函式級腳本共選出 20
  個 focus function，解析 851 個 direct `BL` call-site、246 個 unique direct
  edges。這些數字是分析覆蓋率，不是 runtime invocation 次數。

證據：`PH6BI-OTA-001`、`PH6BI-OTA-002`、`PH6BI-OTA-003`。

### 2. `package_extract_file` 有直接的輸出檔案寫入鏈

在 `PackageExtractFileFn`（`0x401fb8–0x402788`）中：

1. 先由 `ReadArgs`／`FindEntry` 取得 package entry 與輸出參數。
2. `0x4021b4` 呼叫 `_Z8ota_openPKcij`（`ota_open(const char*, int, int)`）。
3. 呼叫前 `w1 = 0x241`（十進位 577，即 `O_WRONLY | O_CREAT | O_TRUNC`），
   `w2 = 0x180`（0600 mode）；`x0` 是由函式參數／expression 取得的輸出路徑。
4. `0x40238c` 呼叫 `_Z18ExtractEntryToFilePvP8ZipEntryi`，把 ZIP entry 寫入已開啟
   的 descriptor。
5. 成功路徑在 `0x40243c` 呼叫 `ota_fsync`，並在 `0x40245c` 呼叫 `ota_close`。

這證實「若 recovery updater 已接受並執行一個合法 install script，該 script
可要求寫入它指定的輸出路徑」；它沒有證實攻擊者可控制 script 或能從 Android
shell 進入這條路徑。

證據：`PH6BI-OTA-004`、`PH6BI-OTA-005`。

### 3. `ota_open` 直接落到 libc `open`

`ota_open(const char*, int, int)`（`0x426338–0x426528`）在 `0x426354` 直接
呼叫符號 `open`（`0x4cc170`），並把 caller 提供的 path／flags／mode 傳入；其餘
邏輯包含 fault-injection/cache bookkeeping 與錯誤處理。

在本次 focus range 內沒有看到 `realpath`、`readlink` 或 `O_NOFOLLOW` 的直接
canonicalization／no-follow gate。這只能表述為「此函式範圍未觀察到」，不能推論
整個 recovery、檔案系統或上游 OTA 驗證沒有其他防護。

特別是 `0x241` 不包含 `O_NOFOLLOW`；這是值得保留給靜態安全 review 的訊號，
但官方 updater 的輸入來源與 recovery 驗證邊界仍是必要前提。

證據：`PH6BI-OTA-005`、`PH6BI-OTA-006`。

### 4. raw partition write 也有明確的函式級鏈

`WriteToPartition`（`0x413c40–0x4142f0`）從 `std::string` 路徑取得 target，於
`0x413dcc` 呼叫兩參數 `ota_open(const char*, int)`，`w1 = 2`（`O_RDWR`）；之後
在 `0x413e3c`、`0x413edc`、`0x413f08` 等位置呼叫 `ota_write`，並於
`0x413e7c` 呼叫 `ota_fsync`，最後關閉 descriptor。`PerformBlockImageUpdate`
另有 direct `open`／`__open_2`／`ota_open` edges。

這是「合法 recovery/update context 具備 raw write 能力」的直接證據；它同時說明
為何不應執行 updater 或傳入自製 script。它不是 shell API，也不是本研究已找到
的 caller-confusion exploit。

證據：`PH6BI-OTA-006`、`PH6BI-OTA-007`。

### 5. `readlink` 命中屬於獨立 cache 管理路徑

`MakeFreeSpaceOnCache`（`0x417778–0x417fc4`）在 `0x417bf0` 呼叫
`__readlink_chk`；wrapper `readlink`（`0x4cc3d8–0x4cc3fc`）再轉到
`readlinkat`，使用 `AT_FDCWD = -100`。在 direct call graph 中沒有從
`PackageExtractFileFn` 或 `ota_open` 到該 cache helper 的 edge。

因此，字串／symbol 中出現 `readlink` 不能被當成 package extraction 已做
canonicalization，也不能單獨推導 symlink bypass。

證據：`PH6BI-OTA-006`、`PH6BI-OTA-007`。

## 高可信推論

- OTA updater 的能力邊界是由 script interpreter、ZIP extraction、fault/cache
  wrapper、raw image update 與 I/O helper 組成，而不是單一殘留字串。
- `PackageExtractFileFn` 對輸出路徑的直接 `open(O_WRONLY|O_CREAT|O_TRUNC)` 值得
  進行 code provenance review；但在沒有合法 OTA script caller、recovery 啟動
  條件與輸入驗證資料流之前，不能標記為可利用漏洞。
- `readlink` 相關控制流目前更像 cache-space 管理，不是 HOME、OOBE 或普通
  Android app 的可達寫入入口。

## 待驗證

1. recovery 在把 OTA 交給 updater 前的簽章／包裝驗證，尚未由本 `update-binary`
   函式本身完整還原；需要對應 recovery binary／合法 OTA lifecycle 做 host-only
   provenance mapping。
2. install script 的實際 parser 是否對 `package_extract_file` 的輸出路徑另有
   canonicalization，尚未以完整 script-interpreter CFG 確認。
3. `ota_open` 的 fault/cache bookkeeping 對特定 path prefix 的語意仍需用
   rodata address mapping 補完；這不會改變目前「直接呼叫 libc open」的結論。
4. `PerformBlockImageUpdate` 的 device path、flags 與 verification branch 需要
   逐 basic-block 做參數追蹤；本階段只保留 direct edges。

## 已排除或不支持

- 沒有證據支持 shell／普通 app 可以直接執行 `update-binary`。
- 沒有證據支持 `readlink` 字串本身代表 symlink traversal、任意檔案寫入或 root。
- 沒有證據支持 OTA/OOBE updater 是可逆的 launcher replacement 路徑。
- 沒有執行、模擬或餵入 malformed、downgrade、symlink、traversal OTA。

## 因風險拒絕測試

以下操作仍拒絕：執行 `update-binary`、recovery／OTA sideload、偽造或修改 OTA、
傳入 traversal／symlink payload、手動觸發 OTA post-install、未知 Binder transaction、
partition write、remount、Root、bootloader 或任何需要 factory reset 的恢復方案。

理由是這些操作會跨越本研究的「主機端靜態證據」邊界，可能寫入 boot/system/vendor/
userdata 或使設備進入不可保證恢復的狀態。

## 目前判定

| 問題 | 判定 | 理由 |
|---|---|---|
| updater 是否具備高權限檔案／分割區寫入能力？ | **已證實** | `PackageExtractFileFn`、`WriteToPartition`、`ota_open`／`ota_write`／`ota_fsync` direct edges。 |
| 是否存在 shell 可達的 updater caller？ | **無法取得證據** | 目前只有 recovery／OTA artifact，沒有安全 caller trace。 |
| 是否已確認 path traversal／symlink bypass？ | **已排除／不支持** | 未完成完整 parser/input provenance，且未執行異常 OTA。 |
| 是否是無 Root launcher 或 root workaround？ | **已排除** | 入口屬 recovery／分割區寫入控制面，非可逆 Android app API。 |

## 下一個最小安全工作

只做 host-only：把 `RegisterInstallFunctions` 的 literal／function table 與
`updater-script` 的實際命令集合逐項配對，再把 recovery 驗證 caller 與 updater
entry 的 provenance 接起來。若該鏈仍只在 signed OTA／recovery context 成立，
OTA 路線即可正式標為「高影響但不可作為無 Root 入口」。
