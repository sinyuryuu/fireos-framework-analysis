# Phase 6AL — OTA indirect closure（host-only native static）

日期：2026-08-10。此文件只新增本輪 closure/negative；基準為 Phase6X3 的 6AF-OTA-001..008，以及保存的 phase6mk、phase6ne、phase6md、phase6mm、phase6kt artifacts。只讀解析 disassembly/debugdata/ELF/relocation/function-pointer table；未執行 `update-binary`、recovery、OTA/sideload/flash/reboot，未製作輸入，未接觸設備。

## 結論

保存的 AArch64 ELF 將 `PerformBlockImageUpdate` 的兩個 direct call site（`0x409cb4`、`0x409cdc`）閉合到 `CacheSizeCheck`（`0x414720`）。`CacheSizeCheck` 在 `0x414730` 將 size 參數傳給 `MakeFreeSpaceOnCache`（`0x417778`），以 `tbnz w0,#31` 將負值導向錯誤；成功時回傳 0，錯誤時回傳 1。兩個 caller 對結果使用 `cbz w0`：零值續行，非零值分支到錯誤/abort 路徑。

`MakeFreeSpaceOnCache` 內的 `0x417bf0 -> __readlink_chk(0x4ce4e8)`、`stat64`、directory iteration、`unlink` 與 `FreeSpaceForFile` 均是已解析的 direct edges。這證明 cache helper 具有 path/canonicalization-related native operations；不證明其輸入可由不可信 OTA 控制，也不證明它通往 partition writer。

間接 dispatch 方面，block-image 五個 function-pointer cell（`0x5af670..0x5af690`）解析為五個已命名 handler；install registry 的 24 個 cells 亦解析為 symbols。`RegisterFunction` 呼叫仍是 registry-mediated indirect dispatch。address-only target、cell address 或 capability 只作 provenance，不能當成 bypass、caller 或低權限 reachability。

archive/argument provenance 可閉合為保存的 updater-script 常量：`system/vendor` 的 `block_image_update` 使用 `system.transfer.list`/`vendor.transfer.list`、`.new.dat.br`、`.patch.dat`；`BlockImageUpdateFn` 在 `0x40b8b8` 設定 `x3=0x5a7b20`、`w4=0` 後 branch 到 `PerformBlockImageUpdate`。在其內部，`x0` 保存 target argument，並由解析後的 command/zip state 產生 archive/transfer-list 相關 arguments；`WriteToPartition` 的第三參數是 target string，經 `ota_open`、`ota_write`、`ota_fsync`/`ota_close` 進入保存的 native writer chain。這是 signed recovery updater capability 與 fixed-script argument closure，不是任意 archive 或任意 partition 的 caller closure。

`WriteToPartition` 的保存 edges（`0x413dcc/0x413e98/0x413ecc/0x414164 -> ota_open`，`0x413e3c/0x413edc/0x413f08 -> ota_write`，`ota_write -> write(0x4d4a10)`）確認 sink chain。選定 graph 沒有 `__readlink_chk`/`readlink`/`readlinkat`/`realpath` marker 到 `WriteToPartition` 的 direct edge；這是 bounded negative，不是 binary-wide absence，亦不是 traversal/symlink 結論。

AVB/rollback 僅能閉合到 handoff boundary：phase6kt 保存的 Java path 先做 metadata/sanity 與 `RecoverySystem` verification，再交給 native/recovery updater；保存 audit 沒有完整 platform verifier、AVB rollback index 或 exact native handoff implementation。故不得把 verified-boot/rollback marker、recovery wrapper、ELF writer capability 或 address-only target 解讀為 bypass。

## 新增 closure/negative（僅 6AL rows）

| ID | 類別 | 靜態結果 |
|---|---|---|
| 6AL-OTA-001 | closure | `PerformBlockImageUpdate 0x409cb4/0x409cdc -> CacheSizeCheck 0x414720`；兩個 caller edge 均為 symbol-resolved direct call。 |
| 6AL-OTA-002 | closure | `CacheSizeCheck 0x414730 -> MakeFreeSpaceOnCache 0x417778`；`x0` 保留 size argument，callee result 以 sign bit 判定。 |
| 6AL-OTA-003 | closure | `CacheSizeCheck` 負值走 `0x414740` error/log/return-1；非負值 return 0。兩個 `PerformBlockImageUpdate` caller 的 zero-result branch 續行，non-zero branch error/abort。 |
| 6AL-OTA-004 | closure | `MakeFreeSpaceOnCache` 的 `__readlink_chk`、directory/stat/unlink/free-space direct edges 已解析；canonicalization-related operation 存在，但 impact/input control 未閉合。 |
| 6AL-OTA-005 | closure | block-image registry 五個 cells 與 install registry 24 個 cells 均有 symbol resolution；`RegisterFunction` 仍是間接 dispatch boundary。 |
| 6AL-OTA-006 | closure | updater-script fixed archive/transfer-list arguments 對齊 `BlockImageUpdateFn` → `PerformBlockImageUpdate`；`WriteToPartition` target string 對齊 `ota_open`/`ota_write`/`write` sink chain。 |
| 6AL-OTA-007 | negative | selected graph 未觀察到 canonicalization/readlink marker → `WriteToPartition` direct edge；未解析的 indirect/unselected edges 不得被宣稱不存在。 |
| 6AL-OTA-008 | negative | AVB/rollback exact native verifier/handoff 未在保存輸入中閉合；RecoverySystem wrapper、signed-recovery capability、address-only/cell provenance 均不構成 bypass 或低權限 reachability。 |

## Evidence

- `artifacts/phase6ne-updater-cache-flow-20260810-03/focus-disassembly.txt`, `direct-call-edges.csv`, `return-branches.csv`, `summary.json`
- `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv`, `canonicalization-context.csv`, `canonicalization-marker-strings.csv`, `updater-script-entrypoints.csv`, `summary.json`
- `artifacts/phase6md-native-updater-path-audit-20260810-02/path-write-call-edges.csv`, `path-marker-strings.csv`, `updater-script-operations.csv`
- `artifacts/phase6mm-updater-blockimage-20260810-01/selected-call-edges.csv`, `canonicalization-call-sites.csv`, `block-image-registration.csv`, `focus-disassembly.txt`
- `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json`

以上均為既存保存 artifacts；本輪沒有修改它們。
