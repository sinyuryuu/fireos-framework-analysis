# Phase 6MD：PS7331 native updater path／write chain audit

日期：2026-08-10
範圍：Fire OS PS7331 官方 OTA `update-binary` 的主機端符號、direct-BL
call-edge、字串與 `updater-script` 對照。

本階段沒有執行 `update-binary`，沒有開啟 recovery、沒有送 OTA、沒有修改
封包、沒有測試 symlink/path traversal、沒有 fastboot、沒有分割區寫入，也沒有
接觸裝置。

## 結論摘要

- **已證實：** `updater-script` 明確把 `system`、`vendor`、`boot`、`preloader`、
  `lk`、TEE、SPM/SSPM、camera firmware 等映像寫入
  `/dev/block/platform/bootdevice/by-name/*`。
- **已證實：** symbolized direct-BL graph 連出 `PackageExtractFileFn → ota_open /
  ExtractEntryToFile`、`PerformBlockImageUpdate → ota_open/open/chown/rename`、
  `WriteToPartition → ota_open/ota_write`，並連出 `ota_open → open`、
  `ota_write → write`。
- **Strong evidence：** 這是 recovery／高權限 partition-writer boundary，不是
  ADB shell 可逆的 Launcher selector，也不是安全的提權入口。
- **待驗證：** binary 中雖有 `symlink_realpath`、`readlinkat`、`readlink` 等字串，
  本次選定的 direct-BL graph 沒有找到它們進入 extraction/write chain 的直接呼叫邊。
  這不能排除 indirect call、未選取函式或資料驅動 dispatch。
- **未找到：** 本次 updater path evidence 沒有 Fire Launcher、HOME resolver 或
  User-0 preferred-activity sink；不能把它當作替換官方 Launcher 的 route。

## 輸入與雜湊

Canonical host-only output：
`artifacts/phase6md-native-updater-path-audit-20260810-02/`。

| Input | SHA-256 |
|---|---|
| `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` |
| `firmware/extracted/PS7331/META-INF/com/google/android/updater-script` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` |
| `artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv` | `6a667275ea88bc33e3f2297077255a8f12a87f3e08318cf6d9704032e6024eca` |
| `artifacts/phase6s/ota-call-edges-20260805-01/call-edges.csv` | `ede44312f2f667adff552475866de0b17c06b96161854c35a17a3a1c361eaa75` |
| `artifacts/phase6p/callback-ota-audit-20260805-02/native/strings-matched.txt` | `172a57cdd82eb2891c585d8c9c31bd642ffa23733cda9a8c599b3c42e896a70e` |
| `artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt` | `0e780e51ced6f7b000bf0a821ffe6cfe81bc0108e6073174b7fa0cb0b94abdcd` |

## 實際控制流證據

### Extraction

| Caller | Direct callee | Instruction | 判定 |
|---|---|---:|---|
| `PackageExtractFileFn` | `ota_open` | `0x4021b4` | 開啟 OTA input/output wrapper |
| `PackageExtractFileFn` | `ExtractToMemory` | `0x4022cc` | ZIP extraction path |
| `PackageExtractFileFn` | `ExtractEntryToFile` | `0x40238c` | ZIP entry to file path |
| `ota_open` | `open`/`open64` | `0x426354` | native open sink |

### Block-image update and partition write

| Caller | Direct callee | Instruction | 判定 |
|---|---|---:|---|
| `PerformBlockImageUpdate` | `ota_open` | `0x409340`, `0x40a3a8` | image I/O wrapper |
| `PerformBlockImageUpdate` | `open`, `__open_2` | `0x40a2e0`, `0x409d48` | native open sinks |
| `PerformBlockImageUpdate` | `chown` | `0x409bdc`, `0x40a344` | metadata mutation |
| `PerformBlockImageUpdate` | `rename` | `0x40a378` | replacement/commit sink |
| `WriteToPartition` | `ota_open` | `0x413dcc`, `0x413e98`, `0x413ecc`, `0x414164` | partition target open |
| `WriteToPartition` | `ota_write` | `0x413e3c`, `0x413edc`, `0x413f08` | partition write wrapper |
| `ota_write` | `write` | `0x426e44` | native write sink |

這些是 static call edges，不是執行結果；輸出中的 `partition_written=false` 是
因為 updater 從未被執行。

## Path canonicalization 判定

字串輸入含有 `symlink_realpath`、`readlinkat`、`readlink`、`verify` 與 `sha256`
等 markers，這證明 binary 編入相關元件或診斷字串。但在本階段選定的
symbolized direct-BL edge 集合中：

```text
direct_canonicalization_edge_in_selected_graph = false
canonicalization_strings_present = true
```

因此目前最精確的結論是：

> 有 path-handling marker，但尚未證明 canonicalization / symlink check 位於
> `PackageExtractFileFn` 或 partition-write chain 的實際控制流上。

不能由此推導 traversal、symlink race 或可覆寫任意檔案。完整 indirect-call、
function-pointer 與 error-path dataflow 仍是 **待驗證**，且不應在量產裝置或真實
recovery 上驗證。

## Official updater-script scope

`updater-script` 的主要寫入行為：

```text
system, vendor
boot, preloader, lk, tee1, tee2
spmfw, sspm_1, cam_vpu1, cam_vpu2, cam_vpu3
```

另有把 `target.blocklist` 寫入 `/cache/recovery/last_blocklist`。這與 Launcher
替換沒有直接關係；執行該 script 將跨越 boot/system/vendor 等不可逆或高風險
邊界，因此不列入 ADB workaround。

## 研究判定

### 已證實

1. PS7331 updater 具有完整的 privileged extraction、block-image 與 partition
   write symbol/call-edge surface。
2. 官方更新腳本會觸及 boot chain 與多個 protected partitions。
3. 本階段沒有裝置或 OTA state mutation。

### 高可信推論

這條路線需要正常 recovery／更新交易的高權限上下文；現有證據不支持普通
shell、第三方 APK 或 HOME resolver 透過它取得可逆的 Launcher replacement。

### 待驗證

- `symlink_realpath` markers 對應的 indirect call 與實際 guard semantics。
- recovery 外層對 OTA 簽章、版本與 canonical path 的完整驗證鏈。

### 已排除於本階段目標

本次 evidence 沒有顯示 updater 是 Fire Launcher 的 HOME 選擇器，也沒有顯示
它能在不寫入受保護分割區的情況下改變 HOME。

### 因風險拒絕測試

執行 updater/recovery、製造 malformed 或 symlink OTA、sideload、fastboot、
partition write、boot chain mutation，以及任何需要 factory reset 才能恢復的
測試。

## Reproduction

```sh
python3 tools/scripts/audit_phase6md_native_updater_paths.py \
  --binary firmware/extracted/PS7331/META-INF/com/google/android/update-binary \
  --symbols artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv \
  --edges artifacts/phase6s/ota-call-edges-20260805-01/call-edges.csv \
  --strings artifacts/phase6p/callback-ota-audit-20260805-02/native/strings-matched.txt \
  --disassembly artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt \
  --updater-script firmware/extracted/PS7331/META-INF/com/google/android/updater-script \
  --output artifacts/phase6md-native-updater-path-audit-YYYYMMDD-01
```

所有輸出均為 host-only；腳本有 `--dry-run`，並拒絕覆寫既有 output。
