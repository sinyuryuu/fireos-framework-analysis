# Phase 6D：PS7331 `/init` conservative CFG

## 範圍

使用保存的 PS7331 `/init` AArch64 ELF，在主機端以 `objdump` 解析
`0x41ad00–0x41d900`。未執行 ELF、未接觸裝置、未改寫 boot property、未載入
alternate policy，也未執行任何 kernel memory 或 root 操作。

Canonical artifact：
`artifacts/phase6d/phase6d-init-cfg-20260804-03/`。

## CFG 結果

- Parsed instructions：2816
- Conservative basic blocks：423
- Explicit branch/fall-through edges：663
- `/init` SHA-256：`e72ed4e90d73b88be341985ebd624725b67d67967d04157317456233e15f31fd`

## 關鍵邊

```text
block B41bdf4 (terminator 0x41be48: tbnz w5,#0)
  --branch-->    0x41c30c
  --fallthrough--> 0x41be4c
```

這與既有 call-site evidence 對齊：

```text
0x41ae44: orr w5, wzr, #0x1
0x41ae5c: bl  0x41be00       [rootable candidate]
0x41af78: mov w5, wzr
0x41af80: bl  0x41be00       [standard candidate]
```

## 判定

- **已證實：** the instruction at `0x41be48` (the terminator of conservative
  block `B41bdf4`) forms two explicit CFG edges;
  rootable/standard candidate 也確實以不同值呼叫相同 helper。
- **高可信推論：** `w5` 是會改變 helper 執行路徑的 mode/path flag。
- **待驗證：** `0x41c30c` 的高階語意、是否載入 rootable policy、caller 傳入
  `w5` 的來源，以及 stock boot 是否到達該 edge。
- **已排除：** 「只有無用字串、沒有 instruction-level split」的解釋。

CFG parser 的限制：indirect branch、stripped symbol、函式邊界與 runtime
reachability 仍需人工／更高階工具覆核；CFG edge 本身不等於實機執行證據。
