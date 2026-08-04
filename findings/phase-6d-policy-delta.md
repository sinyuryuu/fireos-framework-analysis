# Phase 6D：標準／`rootable_*` SELinux policy 差異

## 方法與安全界線

本次只對保存的 CIL 文字做 line-set 與聚焦 pattern 統計。沒有編譯、載入、
安裝、替換或套用 policy，也沒有接觸裝置。

工具：`tools/scripts/audit_phase6d_policy_delta.py`
artifact：`artifacts/phase6d/phase6d-policy-delta-20260804-01/`

## 輸入雜湊

| Pair | Standard SHA-256 | Rootable SHA-256 |
|---|---|---|
| plat | `4056ed9140f6c201cb2dd55edf70041667a195e20233bb6a6a2468b40c9a872d` | `51123eabcb7bbc36574ea90eb8c42b82677f5ffd35a40e1d48e61c58a6ec5d35` |
| plat_pub | `da53a898c9799e9922ccc0f952706e0977ced86061b20894ff33c6b4346a9350` | `74fbd09302aac0d7104435b4aed9acd39807eb4e64ae716f0fe097911620f163` |
| vendor | `82430dbe87b8a5f653110b635289489b99e82bdbe7bdc7a2e1ee5564e674e035` | `82559be062226861221c58fb33de39d2541d0a4b08a96ea10bea2b3acc2e5b7a` |

## 統計

| Pair | Rootable lines | Added unique | Removed unique | Rootable `typepermissive` | Rootable `su` token |
|---|---:|---:|---:|---:|---:|
| plat | 17,599 | 2,295 | 1,803 | 1 | 323 |
| plat_pub | 8,939 | 1,437 | 1,067 | 0 | 1 |
| vendor | 10,803 | 1,060 | 6 | 0 | 0 |

`focused-additions.txt` 保留上限 200 條／pair 的聚焦新增規則；完整可重現數值
在 `policy-delta.csv`。其中 `plat` 的新增規則包含：

```text
(allow adbd self (process (setcurrent)))
(allow adbd su (process (dyntransition)))
```

這些是「保存檔案內容」的證據，並非量產機 active policy 或 root 能力的證據。

## 判定

- **已證實：** `rootable_*` 與標準 CIL 並非同一檔案的別名；三組 pair 都有
  明顯差異。
- **高可信推論：** `rootable_plat_sepolicy.cil` 含較明顯的工程／debug-oriented
  規則，包含 `typepermissive` 與擴大的 `su`／transition 相關內容。
- **待驗證：** PS7331 retail boot 是否選用任何 `rootable_*` 檔案，以及選擇
  條件是否存在於 stripped `/init` 的 indirect／inline path。
- **已排除：** 「rootable 字串只是完全沒有內容差異的殘留」這個說法。
- **因風險拒絕測試：** policy replacement、boot property injection、AVB bypass、
  `/init` 執行與任何 root payload。

## 不可推論的事項

此差異分析不能回答：

1. 哪個 policy 在目前裝置上已載入；
2. 任一 shell-writable property 是否能選擇 rootable policy；
3. 是否可以在不改變 boot chain 的情況下取得 UID 0；
4. `rootable_*` 是否是工程映像、測試分支或其他非 retail 路徑的產物。
