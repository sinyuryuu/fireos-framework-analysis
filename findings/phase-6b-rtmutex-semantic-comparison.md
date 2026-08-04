# Phase 6B：PS7331 rtmutex semantic comparison

## 方法

以 host-only parser 讀取三個 source input：

- PS7331 build-selected `kernel/locking/rtmutex.c`；
- preserved legacy Linux stable v4.4.146 reference；
- preserved fixed v6.1.175 `remove_waiter()` focused slice。

Parser 只抽取函式邊界、固定字串／條件 marker、行號與 SHA-256；不呼叫
ADB、不編譯 kernel、不產生 futex 參數、不建立 waiter，也不執行 race 或
root payload。

## 結果

| Finding | PS7331 | Legacy v4.4.146 | Fixed v6.1.175 slice |
|---|---:|---:|---:|
| `remove_waiter()` 清除 `current->pi_blocked_on` | true | true | false |
| `remove_waiter()` 綁定 `waiter_task = waiter->task` | false | false | true |
| `remove_waiter()` 清除 `waiter_task->pi_blocked_on` | false | false | true |
| proxy wrapper 呼叫 `remove_waiter()` | true | true | 不在 focused slice |
| broad `if (ret)` cleanup marker | true | true | 不在 focused slice |
| negative-only `ret < 0` marker | false | false | 不在 focused slice |

## 判定

- **已證實：** 在保存的 source scope 中，PS7331 marker set 與 legacy
  v4.4.146 的 pre-fix cleanup shape 一致。
- **高可信推論：** PS7331 inspected path 沒有 upstream primary
  `waiter->task` cleanup semantics，也沒有 follow-up 的 negative-only
  cleanup marker。
- **待驗證：** 真機是否形成 `waiter->task != current`、錯誤 cleanup 後的
  invariant violation、later consumer、memory effect 或 privilege transition。
- **因風險拒絕測試：** stock device requeue-PI trigger、配對 waiter、競態、
  kernel panic、memory operation 與提權鏈。

注意：fixed v6.1.175 input 是 focused `remove_waiter()` slice，沒有完整
`rt_mutex_start_proxy_lock()` 定義；parser 將其標示為 `UNAVAILABLE`，不把
focused slice 的缺失誤判成 fixed wrapper 的語意差異。

## 可重現輸出

- Script：`tools/scripts/compare_phase6b_rtmutex_semantics.py`
- Artifact：`artifacts/phase6b/phase6b-rtmutex-semantics-20260804-01/`
- Result：`result.md`、`comparison.csv`、`comparison.json`、`sha256sums.txt`

這項結果強化的是 source／patch provenance，不是 runtime exploitability
或暫時 root 證據。
