# Phase 6MM：PS7331 native updater block-image／canonicalization closure

日期：2026-08-10
範圍：主機端、唯讀的 PS7331 官方 `update-binary` symbol-guided AArch64
disassembly 與 direct-`BL` edge correlation。

本階段沒有接觸裝置，沒有執行 `update-binary`、Recovery、OTA、sideload、
`service call`、fastboot、Root、重啟或任何分割區寫入。沒有製作 crafted、
symlink、traversal 或 malformed OTA。

## Executive result

- **已證實：** `main` 進入 `RegisterBlockImageFunction` 後，該函式以同一個
  `RegisterFunction` 目標 `0x41d528` 註冊五個 block-image handler：
  `block_image_verify`、`block_image_update`、`block_image_recover`、
  `check_first_block`、`range_sha1`。五個 data-cell pointer 都解析到已知
  function symbol。
- **已證實：** `block_image_update` 的 data-cell `0x5af678` 指向
  `BlockImageUpdateFn` `0x40b8b8`；其餘四個 handler 也各自有 symbol-level
  mapping。這閉合了 Phase 6MK 尚未選入的 block-image registration gap，
  但只代表靜態註冊，不代表 command 已執行。
- **已證實：** `MakeFreeSpaceOnCache` 在 `0x417bf0` 直接呼叫
  `__readlink_chk` `0x4ce4e8`。這是明確的 path/canonicalization-related
  call site；不能單憑此推論存在 traversal bypass 或安全漏洞。
- **未觀察到（bounded negative）：** 在本次選取的 13 個 function 與 direct-`BL`
  graph 中，沒有 `MakeFreeSpaceOnCache`／`__readlink_chk` 直接連到
  `PackageExtractFileFn`、`PerformBlockImageUpdate`、`BlockImageUpdateFn` 或
  `WriteToPartition` 的 edge。`PerformBlockImageUpdate` 確實呼叫
  `CacheSizeCheck`，但 `CacheSizeCheck` 的 body 未納入本階段，因此不能把
  cache helper 與寫入 sink 的間接關係判定為不存在。
- **仍待驗證：** verifier／cache-size／canonicalization／write 的完整間接
  data-flow、參數來源、錯誤分支順序與 recovery 外層驗證鏈。這些不能以
  runtime OTA 或 crafted path 測試補足，因為那會跨越高權限 recovery 與分割區
  寫入邊界。

## Inputs

| Input | SHA-256 |
|---|---|
| `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` |
| `artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv` | `6a667275ea88bc33e3f2297077255a8f12a87f3e08318cf6d9704032e6024eca` |

工具：`/opt/homebrew/opt/llvm/bin/llvm-objdump`。分析器：
`tools/scripts/audit_phase6mm_updater_blockimage_closure.py`。

## 1. Block-image registration

`RegisterBlockImageFunction` 的直接註冊區段如下：

| Registration | Instruction | Function pointer cell | Resolved target |
|---|---:|---:|---|
| `block_image_verify` | `0x40d0fc` | `0x5af670` | `BlockImageVerifyFn` `0x407c48` |
| `block_image_update` | `0x40d144` | `0x5af678` | `BlockImageUpdateFn` `0x40b8b8` |
| `block_image_recover` | `0x40d190` | `0x5af680` | `BlockImageRecoverFn` `0x40cbc0` |
| `check_first_block` | `0x40d1d8` | `0x5af688` | `CheckFirstBlockFn` `0x40c858` |
| `range_sha1` | `0x40d224` | `0x5af690` | `RangeSha1Fn` `0x40c328` |

每一列的 name／cell／target 都來自同一份 selected disassembly、ELF load
segment data 與 symbol CSV 的 correlation；不是依賴字串單獨推測。

靜態關係：

```text
main (0x400cb0)
  -> RegisterBlockImageFunction (0x40d0a8)
     -> RegisterFunction (0x41d528)
        -> block_image_* registry entries
           -> BlockImageVerifyFn / BlockImageUpdateFn / BlockImageRecoverFn
```

## 2. Canonicalization-related call site

`MakeFreeSpaceOnCache` 的 selected direct edge：

```text
MakeFreeSpaceOnCache + 0x478  (0x417bf0)
  -> __readlink_chk (0x4ce4e8)
```

在該 call 前，反組譯碼準備了 path、buffer、`0xfff` 及 `0x1000` 類型的
參數；本報告只把它記為 static call-site evidence，不把暫存器推導直接升格為
完整參數語意或可利用性結論。

同一 function 也包含 `stat64`、`strncmp`、`unlink`、directory traversal 與
cache bookkeeping calls。這說明 helper 具有檔案／cache 管理職責，但仍不能
證明它被不可信輸入控制，或其結果會繞過 OTA 驗證。

## 3. Relation to extraction and partition writes

Phase 6MD／6MK 已有的 static chain 仍成立：

```text
package_extract_file
  -> PackageExtractFileFn
     -> ota_open -> open

block_image_update
  -> BlockImageUpdateFn
     -> PerformBlockImageUpdate
        -> CacheSizeCheck          [body not selected here]
        -> ...
        -> WriteToPartition
           -> ota_open / ota_write / write
```

本階段新增的直接證據是 `MakeFreeSpaceOnCache -> __readlink_chk`；目前 selected
graph 沒有 `__readlink_chk -> write sink` 的直接 edge。這是範圍受限的負面結果，
因為 `CacheSizeCheck`、其他 function-pointer dispatch 或未選取的 caller 仍可能
連接兩個區域。

因此本階段不回答以下更強的問題：

- canonical path 是否可被 OTA 輸入控制；
- symlink 是否能繞過驗證；
- 是否能覆寫任意檔案或分割區；
- 是否能繞過簽章／版本檢查；
- 是否能取得 Root 或改變 HOME。

## 4. Safety classification

| Finding | Status |
|---|---|
| Block-image registry mapping | **已證實** |
| `MakeFreeSpaceOnCache` direct `__readlink_chk` call | **已證實** |
| Direct canonicalization-to-write edge in selected graph | **未觀察到；bounded negative** |
| Complete indirect verifier/canonicalization/write chain | **待驗證** |
| Ordinary ADB HOME selector | **已排除於本路徑** |
| Runtime OTA/path traversal test | **因風險拒絕測試** |

這個 updater 是 recovery／更新上下文的高權限路徑，不是普通 shell 的 Launcher
selector。任何執行 updater、Recovery、crafted OTA、symlink path、sideload、
fastboot 或 partition write 的測試都超出本階段安全範圍。

## Reproduction

```sh
python3 -m py_compile tools/scripts/audit_phase6mm_updater_blockimage_closure.py
python3 tools/scripts/audit_phase6mm_updater_blockimage_closure.py --dry-run \
  --binary firmware/extracted/PS7331/META-INF/com/google/android/update-binary \
  --symbols artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv \
  --output artifacts/phase6mm-updater-blockimage-YYYYMMDD-01

python3 tools/scripts/audit_phase6mm_updater_blockimage_closure.py \
  --binary firmware/extracted/PS7331/META-INF/com/google/android/update-binary \
  --symbols artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv \
  --output artifacts/phase6mm-updater-blockimage-YYYYMMDD-01

(cd artifacts/phase6mm-updater-blockimage-YYYYMMDD-01 && sha256sum -c sha256sums.txt)
```

Canonical artifact：
`artifacts/phase6mm-updater-blockimage-20260810-01/`。

## Next smallest safe analysis

若仍需閉合這條路線，下一步只能是主機端選取 `CacheSizeCheck`、
`MakeFreeSpaceOnCache` callers 及其 function-pointer／return-value data-flow，
並把結果分為 direct、indirect-resolved、indirect-unresolved。不得用真機
更新或 crafted OTA 補足靜態缺口。

