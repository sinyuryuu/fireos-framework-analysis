# Phase 5BG：PS7331 source-to-inspected-Image semantic comparison

日期：2026-08-04

## 目的

把既有三類證據放到同一個可重現結果中：

1. PS7331 build-selected `mt8183/4.4` source semantics。
2. 由官方 PS7331 boot Image 產生、且已刻意移除絕對地址的 instruction-pattern summary。
3. 使用 `waiter->task` cleanup 的 fixed reference source。

本分析不執行 Image、source 或任何 reproducer；不產生 kernel address、offset、
payload，也不連接裝置。

## 結果

### 已證實

三方結果為：

`PS7331 source pre-fix` + `PS7331 inspected Image current-task pattern` +
`fixed reference waiter-task cleanup`

因此 machine verdict 為：

`PS7331_INSPECTED_IMAGE_CONSISTENT_WITH_PRE_FIX_SOURCE`

這是 PS7331 版本範圍內的 function-semantic evidence。

| Layer | Observation | Result |
|---|---|---|
| PS7331 source | `remove_waiter()` 分類為 `PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN` | `true` |
| PS7331 source | proxy error path 呼叫 `remove_waiter()` | `true` |
| PS7331 inspected Image | `remove_waiter` 讀取 current-task source | `true` |
| PS7331 inspected Image | `remove_waiter` 清除 current-task blocked-on field | `true` |
| PS7331 inspected Image | proxy path 呼叫 `remove_waiter` | `true` |
| Fixed reference | `remove_waiter` 使用 `waiter->task`、沒有 current cleanup | `true` |

### 高可信推論

- PS7331 沒有被目前證據證明為 CVE-2026-43499 的修補版本。
- 僅因 PS7331 有 `boot.img` 與 source，不能推論「寫入 boot.img 就能取得修補後核心」；
  官方 OTA metadata 顯示它是包含多個分割區與 boot-chain firmware 的完整更新。

### 待驗證

- 目前仍沒有 PS7330 installed signed boot block 的同等 function inspection，因此
  不能把 PS7331 觀察直接當作 PS7330 signed binary proof。
- 本結果不測量 runtime race、kernel crash、code execution 或 privilege transition。

### 因風險拒絕測試

- futex/rtmutex race、kernel memory access、root payload、未知 ioctl。
- fastboot、BROM/DA、bootloader unlock、OTA sideload、任何分割區寫入。

## 輸入雜湊

| Input | SHA-256 |
|---|---|
| `artifacts/phase5/ghostlock-source-semantics-20260804-01/mt8183.json` | `3a02f57d3aeb548948666d7feda4e9121cdc3dff67998f637db6257e67225ba2` |
| `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/instruction-patterns.csv` | `0ee3da7513051f2fa32b221918c6e671bc78b2a8e192fa0ab7ad65cc6e53475d` |
| `artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c` | `c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a` |
| `firmware/extracted/PS7331/boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` |

## 可重現命令

```sh
python3 tools/scripts/compare_phase5bg_ps7331_semantics.py \\
  --source-summary artifacts/phase5/ghostlock-source-semantics-20260804-01/mt8183.json \\
  --binary-patterns artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/instruction-patterns.csv \\
  --fixed-reference artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c \\
  --output artifacts/phase5/ps7331-source-binary-semantic-new \\
  --dry-run
```

既有結果位於：
`artifacts/phase5/ps7331-source-binary-semantic-20260804-01/`。

| Output | SHA-256 |
|---|---|
| `semantic-comparison.json` | `c1b9e09cdc058f07776de2615491c38f4890cfbd5f2e526f02fd6a1a0d8156c3` |
| `semantic-comparison.csv` | `e8c56754c3a5fe9ad9946debe70c7c4a65b0b4228ff3998a46b9f6d444eaccbb` |
| `result.md` | `aa036e55c51f6ed8bc453cf558870dff0a2e44811c05c73cde4eff35a0e53d28` |

## 升級決策

這項三方證據使「為 GhostLock 單一目的升級 PS7331」更沒有必要；它不表示
PS7331 沒有其他 security fixes。若未來要做一般安全更新 A/B，必須以完整、
版本匹配的官方 OTA 作為研究對象，先建立 PS7330 baseline 與可驗證 recovery
路徑；本研究沒有執行升級。
