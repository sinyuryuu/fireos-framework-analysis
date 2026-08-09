# Phase 6NE：PS7331 updater `CacheSizeCheck`／cache flow closure

日期：2026-08-10  
範圍：主機端、唯讀的官方 PS7331 `update-binary` symbol-guided AArch64
反組譯。沒有執行 updater、Recovery、OTA 或任何裝置操作。

## 結論

### 已證實

1. `PerformBlockImageUpdate` 在 `0x409cb4` 與 `0x409cdc` 兩個 direct call
   site 呼叫 `_Z14CacheSizeCheckm`（symbol address `0x414720`）。
2. `CacheSizeCheck` 在 `0x414730` 呼叫 `_Z20MakeFreeSpaceOnCachem`
   （symbol address `0x417778`），將輸入大小透過 `x0` 傳入。
3. `CacheSizeCheck` 在 `0x414734` 檢查 `w0` sign bit；負值走錯誤處理，否則
   回傳零。兩個 `PerformBlockImageUpdate` call site 隨後分別在 `0x409cb8`
   與 `0x409ce0` 以 `cbz w0` 分支。
4. `MakeFreeSpaceOnCache` 內有檔案／cache 管理呼叫，包括在 `0x417bf0`
   呼叫 `__readlink_chk`，以及 `stat64`、`unlink`、directory traversal 等
   direct edges。

### 高可信推論

這些 edges 形成「block-image update → cache-size check → free-space/cache
helper → return/error decision」的靜態資料流骨架。它們只證明官方 updater
binary 內的控制流與呼叫關係，不證明任何 OTA 輸入能控制 path，也不證明
存在 symlink traversal、任意檔案覆寫、簽章繞過或提權。

### 待驗證

- `MakeFreeSpaceOnCache` 的 path、buffer 與 return value 在所有 function-pointer
  或未選取 caller 中的完整資料流。
- recovery 外層如何把已驗證的 OTA metadata 傳給該 native path。
- `CacheSizeCheck` 的實際 cache policy 與 filesystem input 是否能由不可信來源
  影響。

### 因風險拒絕測試

未執行 malformed OTA、downgrade OTA、symlink/traversal path、`update-binary`、
Recovery、sideload、fastboot、partition write 或任何實機 updater 操作。

## 證據

| Evidence ID | 證據 | 結論 | 信心度 |
|---|---|---|---|
| `6NE-CACHE-001` | `artifacts/phase6ne-updater-cache-flow-20260810-03/direct-call-edges.csv`；`focus-disassembly.txt` | 兩個 `PerformBlockImageUpdate → CacheSizeCheck`，以及 `CacheSizeCheck → MakeFreeSpaceOnCache` | Confirmed |
| `6NE-CACHE-002` | `artifacts/phase6ne-updater-cache-flow-20260810-03/return-branches.csv` | `CacheSizeCheck` sign-bit error branch；兩個 caller 的 `cbz w0` continuation branch | Confirmed |
| `6NE-CACHE-003` | 同一 artifact 的 `summary.json` | 四項觀察均為 true；分析未接觸裝置、未執行 updater | Confirmed, scope-limited |
| `6NE-CACHE-004` | `findings/phase-6mm-updater-blockimage-closure.md` 與 `canonicalization-call-sites.csv` | `MakeFreeSpaceOnCache → __readlink_chk` 及 selected graph 的 bounded negative | Strong evidence |

## 輸入完整性

| Input | SHA-256 |
|---|---|
| `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` |
| `artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv` | `6a667275ea88bc33e3f2297077255a8f12a87f3e08318cf6d9704032e6024eca` |

## 重現

```sh
python3 -B -m py_compile tools/scripts/audit_phase6ne_updater_cache_flow.py
python3 tools/scripts/audit_phase6ne_updater_cache_flow.py --dry-run \
  --binary firmware/extracted/PS7331/META-INF/com/google/android/update-binary \
  --symbols artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv \
  --output artifacts/phase6ne-updater-cache-flow-YYYYMMDD-NN

python3 tools/scripts/audit_phase6ne_updater_cache_flow.py \
  --binary firmware/extracted/PS7331/META-INF/com/google/android/update-binary \
  --symbols artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv \
  --output artifacts/phase6ne-updater-cache-flow-YYYYMMDD-NN

(cd artifacts/phase6ne-updater-cache-flow-YYYYMMDD-NN && shasum -a 256 -c sha256sums.txt)
```

腳本拒絕覆寫既有輸出；所有結果為 host-only。
