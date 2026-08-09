# Phase 6MK：PS7331 native updater dispatch／canonicalization closure

日期：2026-08-10
範圍：主機端、唯讀的 PS7331 官方 `update-binary` 控制流與資料指標分析。

本階段沒有執行 `update-binary`、Recovery、OTA、`service call`、fastboot、
sideload、Root、裝置重啟或任何分割區寫入。沒有製作 crafted／symlink／traversal
OTA，也沒有對真機發送測試命令。

## Executive result

本階段把前一階段仍未閉合的「註冊表／間接分派」縮小如下：

- **已證實：** `main` 在 `0x400cac` 呼叫
  `RegisterInstallFunctions`；同一段也在 `0x400cb0` 呼叫
  `RegisterBlockImageFunction`。證據位於
  `artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt:216-218`。
- **已證實：** `RegisterInstallFunctions` 在 24 個位置呼叫共同的
  `RegisterFunction`（目標 `0x41d528`）。每筆呼叫都有 command-name SSO／資料字串
  與 `0x5af000` data-cell；24/24 個 function-pointer cell 可由 ELF data 解析到
  已有 symbol。完整表在
  `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv`。
- **已證實：** 已復原的 install command 包含
  `package_extract_file`、`apply_patch`、`wipe_block_device`、`run_program`、
  `reboot_now` 等；這是 recovery updater 的命令分派表，不是 Android shell API。
- **已證實：** `PackageExtractFileFn` 的 direct edge 仍是
  `0x4021b4 → ota_open`、`0x4022cc → ExtractToMemory`、
  `0x40238c → ExtractEntryToFile`、`0x40243c → ota_fsync`、
  `0x40245c → ota_close`；`ota_open` 在 `0x426354` 進入 `open`。這些是既有
  symbolized direct-BL 證據，不是 runtime 執行結果。
- **已證實：** 輸入資料中存在 `readlink`／`readlinkat`／`realpath`／
  `symlink_realpath` markers；選定的 disassembly 也包含 `readlink` wrapper
  （`0x4cc3d8`）與 `readlinkat` wrapper（`0x4d48a8`）。
- **待驗證：** 在本次選定的 call-edge graph 中，沒有找到 canonicalization marker
  直接進入 extraction／partition-write chain 的 caller edge。`MakeFreeSpaceOnCache`
  雖然在 symbol index 中存在（`0x417778`），但不在本次 selected disassembly，
  所以不能把它的 `__readlink_chk` 分支映射到 extraction sink。
- **未證明：** traversal、symlink bypass、任意檔案覆寫、OTA 簽章繞過、Root 或
  Launcher replacement。marker 的存在不能替代控制流、參數來源與驗證順序證據。

## Inputs and hashes

| Input | SHA-256 |
|---|---|
| `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` |
| `firmware/extracted/PS7331/META-INF/com/google/android/updater-script` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` |
| `artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv` | `6a667275ea88bc33e3f2297077255a8f12a87f3e08318cf6d9704032e6024eca` |
| `artifacts/phase6s/ota-call-edges-20260805-01/call-edges.csv` | `ede44312f2f667adff552475866de0b17c06b96161854c35a17a3a1c361eaa75` |
| `artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt` | `0e780e51ced6f7b000bf0a821ffe6cfe81bc0108e6073174b7fa0cb0b94abdcd` |
| `artifacts/phase6p/callback-ota-audit-20260805-02/native/strings-matched.txt` | `172a57cdd82eb2891c585d8c9c31bd642ffa23733cda9a8c599b3c42e896a70e` |

> 注意：上表最后一列以 repository 中既有 evidence index 的輸入 hash 為準；
> 本次工具執行時也把實際讀取 hash 寫入
> `artifacts/phase6mk-updater-dispatch-20260810-04/summary.json`。若要逐字驗證，
> 以該 summary 與 artifact `sha256sums.txt` 為 canonical record。

## 1. Registration and indirect dispatch

`RegisterInstallFunctions` 在 disassembly 的第一個 registration block 以
`strb` 儲存 libc++ SSO length，再把 command name 放在 stack；例如
`mount` 位於 `focus-disassembly.txt:8229-8243`，`is_mounted` 位於
`:8248-8262`。每個 block 隨後把 `x1` 指向的 data-cell 讀入
`RegisterFunction`，例如第一筆 cell 是 `0x5af5a8`，其值解析為
`0x403268`（`MountFn`）。

主機端工具對整個 function 做 state-aware decoding，避免因下一筆 registration
重用前一筆的 SSO length register 而錯讀名稱。得到 24 筆：

```text
mount, is_mounted, unmount, format, show_progress, set_progress,
package_extract_file, getprop, file_getprop, apply_patch,
apply_patch_check, apply_patch_space, wipe_block_device, read_file,
sha1_check, write_value, wipe_cache, ui_print, run_program, reboot_now,
get_stage, set_stage, enable_reboot, tune2fs
```

這個結果表示「命令字串 → function-pointer registry → handler」的間接邊界已
具體化；它不表示任何 command 已被執行。`RegisterBlockImageFunction` 的
implementation body 尚未納入本次 selected disassembly，故 block-image
registration 的完整 registry mapping 仍是 **待驗證**。

## 2. Extraction／write sink correlation

既有 direct-BL evidence 將以下關係固定下來：

```text
main
 ├─ RegisterInstallFunctions
 │   └─ RegisterFunction(name, function-pointer cell)
 │       └─ package_extract_file → PackageExtractFileFn
 │           ├─ ota_open → open
 │           ├─ ExtractToMemory
 │           ├─ ExtractEntryToFile
 │           ├─ ota_fsync
 │           └─ ota_close
 └─ RegisterBlockImageFunction
     └─ [implementation body not selected in this audit]
```

`PackageExtractFileFn` 的具體指令位置可在
`focus-disassembly.txt:938-945,1008-1015,1056-1064,1100-1115` 及
`findings/phase-6md-native-updater-path-audit.md:44-66` 重現。這是 recovery
高權限檔案／映像處理能力的證據；它不是普通 ADB shell 可用的 HOME 控制面。

## 3. Canonicalization／verification boundary

| Observation | Status | Meaning |
|---|---|---|
| `readlink`／`readlinkat` symbols and wrappers present | **已證實** | binary 包含相關 syscall wrapper；不代表 extraction caller 一定使用它 |
| `realpath`／`symlink_realpath` markers present in supplied strings | **已證實** | binary／debug strings 含 path-handling marker |
| direct selected edge from extraction/write handler to canonicalization | **未觀察到** | bounded negative result；不等於 binary-wide absence |
| `MakeFreeSpaceOnCache` body mapped to the sink | **待驗證** | symbol exists, but body was not selected; no safe claim about its `readlink` use |
| OTA signature/version/canonical path verification fully traced | **待驗證** | recovery outer layer was not executed or fuzzed |

`ota_open` 本身在 `0x426354` 直接進入 `open`，並在後續使用
`strlen`／`strncmp` 及 fault/cache helper（`focus-disassembly.txt:7921-7969`）。
本次沒有看到 `readlink` 或 `realpath` 的直接 call edge 從 `ota_open` 出發；但
因為選定 graph 與 indirect dispatch 仍有限，這只能標示為 **待驗證**，不能標示
為缺少 guard 或漏洞。

## 4. Safety boundary and relation to Launcher research

官方 `updater-script` 已由 Phase 6MD 證實會指向 system/vendor、boot chain
及多個 protected block-device target。執行 updater/recovery 會跨越不可逆狀態，
因此本階段只做 host-only parsing。這條路線沒有出現
`com.amazon.firelauncher`、HOME resolver、preferred activity 或 User-0 package
state sink。

所以對原研究問題的判定是：

- **已排除於目前安全 scope：** native updater 不是可用的普通 shell Launcher
  selector，也不是可直接採用的無 Root workaround。
- **高可信推論：** 這條路線要求 recovery／更新交易的高權限上下文；即使後續
  找到 canonicalization 差異，也不能把它直接轉稱為 HOME replacement 或 Root。
- **因風險拒絕測試：** 執行 updater、recovery、crafted/symlink OTA、sideload、
  fastboot、partition write、boot-chain mutation 與任何需要 factory reset 的
  rollback。

## Reproduction

```sh
python3 -m py_compile tools/scripts/audit_phase6mk_updater_dispatch_closure.py
python3 tools/scripts/audit_phase6mk_updater_dispatch_closure.py --dry-run \\
  --binary firmware/extracted/PS7331/META-INF/com/google/android/update-binary \\
  --symbols artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv \\
  --edges artifacts/phase6s/ota-call-edges-20260805-01/call-edges.csv \\
  --disassembly artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt \\
  --strings artifacts/phase6p/callback-ota-audit-20260805-02/native/strings-matched.txt \\
  --updater-script firmware/extracted/PS7331/META-INF/com/google/android/updater-script \\
  --output artifacts/phase6mk-updater-dispatch-YYYYMMDD-01

python3 tools/scripts/audit_phase6mk_updater_dispatch_closure.py \\
  --binary firmware/extracted/PS7331/META-INF/com/google/android/update-binary \\
  --symbols artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv \\
  --edges artifacts/phase6s/ota-call-edges-20260805-01/call-edges.csv \\
  --disassembly artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt \\
  --strings artifacts/phase6p/callback-ota-audit-20260805-02/native/strings-matched.txt \\
  --updater-script firmware/extracted/PS7331/META-INF/com/google/android/updater-script \\
  --output artifacts/phase6mk-updater-dispatch-YYYYMMDD-01
```

Canonical output：

`artifacts/phase6mk-updater-dispatch-20260810-04/`，另有
`output/tables/phase6mk-updater-dispatch-20260810-04.csv` 與
`output/call-graphs/phase6mk-dispatch-canonicalization-20260810-04.mmd`。

## Remaining minimum host-only work

1. 擴充 selected disassembly，納入 `RegisterBlockImageFunction` 與
   `MakeFreeSpaceOnCache` 的完整 body，然後只做 symbol-guided indirect-call
   mapping；不執行 updater。
2. 對 recovery outer verifier 做 source／symbol／branch ordering provenance，
   只使用已保存的 framework/recovery artifacts；不製作 malformed OTA。
3. 若上述結果仍沒有 caller→canonicalization→write 的完整鏈，應把 OTA 路線
   正式標記為研究結案候選，回到尚未閉合的 OOBE user-scope 或 Amazon private
   Binder caller inventory，而不是進行 runtime mutation。
