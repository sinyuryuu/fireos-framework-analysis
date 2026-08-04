# Phase 6C：PS7331 `/init` policy-loader 靜態分析

## 範圍

本輪只對保存的 PS7331 7.3.3.1 `root/init` AArch64 stripped ELF 做主機端
反組譯、literal marker 與 ADRP/ADD 位址映射。輸入來自既有唯讀 image
抽取；沒有執行 ELF、載入 SELinux policy、修改 boot property、接觸平板、呼叫
futex、建立 race、讀寫 kernel memory 或產生 root payload。

分析器：`tools/scripts/analyze_phase6c_init_policy_loader.py`
Canonical artifact：
`artifacts/phase6c/phase6c-init-policy-loader-audit-20260804-02/`

## 輸入與完整性

| Input | SHA-256 |
|---|---|
| `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init` | `e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd` |
| `policy-loader-audit.json` | `37d77ceed1004aa76e3804fd365c286eade2abca112c89e0e5f7898e51e5235` |
| `policy-path-references.csv` | `e70c9fc26bf1f688579f8643d2a88bf79408dd7ff98cbb99b60948fe4bdd7d60` |
| `disassembly-windows.txt` | `3a8baaa32fefc4b3fa73ed32a7e470d580b500497d5e37bfbf62d88bf3e319bd` |

`disassembly-windows.txt` 的實際 SHA-256 以 artifact 內 `sha256sums.txt` 為準；
上表若與 manifest 不一致，應以 manifest 為 canonical record。

## 靜態觀察

### 1. Rootable 與 standard policy 都有 code-level reference

分析器從第一個 executable `LOAD` 的檔案 offset／VMA 映射，找到 12 個
literal marker，並將其中 10 個精確映射到 AArch64 `ADRP` + `ADD` 指令對：

| 區域 | 觀察 | 分類 |
|---|---|---|
| `0x41ad80–0x41ae54` | 建立 `/system`、`/vendor`、`/odm` 與 FireOS 的 `rootable_*` path record | **已證實**：code-level path references |
| `0x41ae5c` | 呼叫共用 helper `0x41be00`，當時 `w5=1` | **已證實**：call-site flag value；flag 語意待確認 |
| `0x41aea8–0x41af44` | 建立 standard `plat_pub_versioned`、`vendor_sepolicy`、`odm_sepolicy`、`fireos_sepolicy` path record | **已證實**：code-level path references |
| `0x41af80` | 呼叫共用 helper `0x41be00`，當時 `w5=0` | **已證實**：call-site flag value；flag 語意待確認 |
| `0x41be48` | `tbnz w5,#0`，在 helper 入口分支 | **已證實**：分支存在；**待驗證**：高階選擇意義 |

這比單純 `strings /init` 更強，因為 path literal 被實際載入到暫存器並傳入
共用處理區域。但它仍不能證明任一 variant 在目前 stock boot 中被選取。

### 2. `androidboot.selinux=permissive` 的解析候選

在 `0x41bd60` 的 stripped function 中可直接看到：

1. 讀取第一個 string-like object 的長度，要求 `0x13`（19 bytes）。
2. 將其與 VMA `0x5885b9` 的字串比較；該 literal 是
   `androidboot.selinux`。
3. 讀取第二個 object 的長度，要求 `0xa`（10 bytes）。
4. 將其與 VMA `0x5885cd` 的字串比較；該 literal 是 `permissive`。
5. 比較成功時，對 `[x19,#8]` 指向的欄位寫入 zero。

**已證實：** `/init` 有編譯進去的 boot-property key/value 比較邏輯。

**高可信推論：** 這是 policy／enforcement mode decision surface 的候選 helper。
**待驗證：** stripped binary 中 `[x19,#8]` 的欄位實際代表什麼，以及該 function
的 caller、回傳值與後續 policy selection 關係。不能只由一次 zero store 將其
命名成「啟用 permissive」或「取得 root」。

### 3. Call-site 關係

`0x4041fc` 直接呼叫 `0x41b748`，接著在 `0x404200` 直接呼叫
`0x41ad00`。`0x41ad00` 與 standard path 區域共同使用 `0x41be00`。
目前沒有符號，因此以下名稱是人工標註而非原始 class／method 名稱：

```text
0x4041fc
  ├─> 0x41b748                 [caller context unresolved]
  └─> 0x41ad00                 [rootable path-builder candidate]
        └─> 0x41be00 (w5=1)    [common policy-loader candidate]

0x41af80                         [standard path-builder candidate]
  └─> 0x41be00 (w5=0)           [common policy-loader candidate]

0x41bd60                         [androidboot.selinux/permissive parser candidate]
```

完整窗口在 `disassembly-windows.txt`；機器可讀關係在
`policy-path-references.csv`。

## 與目前 stock runtime 的交叉比對

既有唯讀 snapshot（`findings/phase-6c-runtime-capture-20260804-01.md`）記錄：

- Fire OS fingerprint：`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`；
- kernel：`4.4.146+` AArch64；
- SELinux：`Enforcing`；
- verified boot：`green`；
- `ro.boot.unlocked_kernel=false`。

這只能證明 snapshot 時的 boot properties／安全狀態。它不能把 `/init` 中的
alternate path reference 等同於 active `rootable_*` policy，也不能證明某個
policy blob 的 runtime hash。

## 判定

### 已證實

- PS7331 `/init` 不只是含有 rootable filename 字串；它有把 rootable 與
  standard policy path 載入 code path 的指令級 reference。
- 兩組 path 都流入同一個 stripped helper，且 call-site 的 `w5` 值不同。
- `androidboot.selinux`／`permissive` 的 key/value comparison 存在於 binary。

### 高可信推論

- image 內存在 policy-loader decision surface；rootable files 很可能是 build 或
  boot variant 的一部分，而非純粹未使用資料。

### 待驗證

- 目前 stock boot 實際載入哪一組 policy。
- `w5` 的準確語意與 branch predicate。
- `0x41bd60` 的 caller 與欄位寫入對 policy enforcement 的實際影響。
- precompiled policy hash 與 live kernel-loaded policy 的對應。

### 已排除

- 「檔案名稱含 `rootable`」即可推出目前裝置已 rootable。
- 「存在 permissive 字串比較」即可推出能以 shell 改變 SELinux mode。
- 目前有 GhostLock runtime mismatch、cleanup residue、kernel memory effect 或
  privilege transition。

### 因風險拒絕測試

不執行 boot-property mutation、policy variant selection、remount、bootloader／
fastboot／刷機、system image write、paired waiter、race、panic、heap shaping、
kernel memory operation 或提權 payload。這些操作都超出本輪無損靜態研究範圍。

## 可重現命令

```sh
python3 tools/scripts/analyze_phase6c_init_policy_loader.py --dry-run \
  --init artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init \
  --output artifacts/phase6c/phase6c-init-policy-loader-audit-YYYYMMDD-NN

python3 tools/scripts/analyze_phase6c_init_policy_loader.py \
  --init artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init \
  --output artifacts/phase6c/phase6c-init-policy-loader-audit-YYYYMMDD-NN
```

工具拒絕覆寫既有 output；`--dry-run` 不讀取 ELF 內容，也不接觸設備。
