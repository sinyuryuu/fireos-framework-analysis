# Phase 6D：`/init` selector data-flow 複核

## 範圍

本 findings 只使用保存的 PS7331 `/init` ELF 與 host `objdump`。工具沒有執行
ELF、沒有接觸裝置、沒有修改 boot property、沒有載入 SELinux policy，也沒有
執行 root 或 kernel 操作。

輸入：

- `/init`：`artifacts/phase6c/phase6c-image-policy-extract-20260804-06/root/init`
- SHA-256：`e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd`
- 工具：`tools/scripts/audit_phase6d_init_selector_dataflow.py`
- artifact：`artifacts/phase6d/phase6d-init-selector-dataflow-20260804-02/`

## 結果

| Finding | 結論 | 信心 |
|---|---|---|
| Rootable／standard path literals 存在 | 完整 ELF 中有對應字串與 code/data marker；`0x41be00` 由 `w5=1` 與 `w5=0` 兩處呼叫。 | 已證實 |
| `0x41bd60` 的語意 | 指令形狀比較 `androidboot.selinux`／`permissive`，並在成功時寫入狀態欄位；與 AOSP `StatusFromCmdline()` 的 enforcing-status parser 相符。 | 高可信推論 |
| `0x41bd60` 是 rootable policy selector | 完整 `.text` 沒有 direct `bl` 到該位址；沒有資料流把它連到 rootable path-builder。 | 待驗證／目前不支持 |
| `w5` 分支的高階語意 | `0x41be48` 會依 `w5` branch 到 `0x41c30c`；stripped binary 的 helper／indirect path 尚未完全解析。 | 待驗證 |
| S4「只有無引用字串」 | 被 code/data reference 與 branch landmark 排除。 | 已排除 |

## Direct-call 結果

`summary.json` 記錄完整 `.text` 掃描：

```text
0x41ad00: 1 direct call
0x41b748: 3 direct calls
0x41bd60: 0 direct calls
0x41be00: 2 direct calls
0x41c30c: 0 direct calls (branch target, not a direct call)
0x41c30c: 6 branch references
```

兩個 `0x41be00` call site 分別為：

```text
0x41ae5c: w5=1 nearby; bl 0x41be00
0x41af80: w5=0 nearby; bl 0x41be00
```

這證明 common helper 的 mode/path 分支存在，不證明哪一條在零售開機中被選用。

## AOSP 語意校正

AOSP Android 9 r1 的 `init/selinux.cpp`：

- `StatusFromCmdline()` lines 78–89 將 `androidboot.selinux=permissive` 轉成
  enforcing status。
- `IsEnforcing()` lines 91–96 使用該 status。
- `LoadPolicy()` lines 378–380 先選 split/monolithic loader。
- `SelinuxInitialize()` lines 384–398 先 `LoadPolicy()`，再依 status 呼叫
  `security_setenforce`。

因此，`androidboot.selinux` parser candidate 不應被描述為
「rootable policy selector」。目前合理的最窄說法是：它可能是 enforcing 狀態
解析邏輯；rootable／standard policy path-builder 的選擇條件仍未還原。

## 證據限制

零 direct call 不排除 indirect call、function pointer、尾呼叫或 inline code。
同樣地，字串 reference 和保守 CFG edge 不代表 stock boot 一定到達該 edge。
沒有 symbolized `/init` 或 Amazon `system/core/init` source 時，不能把 stripped
address 改寫成未證實的函式名稱。

## 安全結論

目前沒有可安全、可重現的 temporary-root 路徑。為取得 root 而執行
alternate-policy injection、bootloader/property spoofing、AVB bypass、
`/init` execution 或 kernel-memory 操作，列為因風險拒絕測試。
