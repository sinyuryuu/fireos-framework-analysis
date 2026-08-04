# Phase 5CG：PS7331 early-return／`ret` cleanup 抽象決策模型

日期：2026-08-04

範圍：PS7331 exact `futex.c`／`rtmutex.c` 的 host-only abstract model。沒有
執行 futex syscall、race、POC、root、裝置 I/O 或 image/partition 操作。

## 直接回答

### 已證實：early return 是未完整 waiter 邊界

`task_blocks_on_rt_mutex()` 的 `owner == task` 分支先回傳 `-EDEADLK`，而
`waiter->task = task` 在後面才執行。這表示該分支返回時，不能假設 waiter
已完成 task assignment。

### 已證實：PS7331 的 broad `if (ret)` 會把錯誤返回送進 cleanup

`rt_mutex_start_proxy_lock()` 先可能把無 owner 時的非零結果正規化為 0，
接著仍使用 `if (unlikely(ret)) remove_waiter(...)`。在 owner 存在且返回值
仍為非零的抽象情況下，cleanup branch 會被選取。

`futex_requeue()` 另外區分 `ret == 1` 的成功喚醒分支與其他非零錯誤分支。
因此 `if (ret)` 是 follow-up patch chain 的 cleanup gate，但不是 primary
`current`／explicit-task identity defect 的唯一條件。

### 高可信推論：若 mismatch 狀態已存在，錯誤 cleanup 可能保留 target 欄位

在抽象模型的 `current != explicit_task` 且 target task 已有
`pi_blocked_on` 情況下：

- cleanup 寫入對象是 `current`；
- explicit target 的 `pi_blocked_on` 沒有被該 cleanup 直接清除；
- 後續是否真的保留、被讀取或被另一條路徑修復，仍取決於 runtime state。

這是條件式 source implication，不是 runtime invariant violation 證明。

## Decision matrix

| Abstract case | Waiter assignment before return | Cleanup selected | Interpretation |
|---|---:|---:|---|
| `try_to_take` success | no proxy enqueue | no | success/wake branch |
| ordinary block | yes | no | normal requeue path |
| early deadlock, owner present | no | yes | null/unqueued waiter guard is relevant |
| negative chain result, owner present | yes | yes | broad nonzero cleanup gate |
| negative result, owner absent | source normalizes to zero | no | requeue path continues |
| identity mismatch + target state present | yes, assumed | yes | target residue is conditional model result |

## Status boundary

| Claim | Status |
|---|---|
| early return precedes `waiter->task` assignment | 已證實 |
| broad nonzero cleanup guard exists | 已證實 |
| cleanup writes `current->pi_blocked_on` | 已證實 |
| source interface permits different task roles | 已證實／source scope |
| real PS7331 runtime mismatch | 待驗證 |
| persistent target-state violation | 待驗證 |
| second consumer actually observes it | 待驗證 |
| crash, controlled memory effect, root | 未證明 |

## Safety boundary

本模型不接受 futex 操作參數，不產生 race timing、kernel address、offset、
gadget、payload 或 root stage，也不會將抽象表格轉成可執行 POC。它的用途是
把 exact source 的 branch 語意與 runtime 尚未證明的部分分開。
