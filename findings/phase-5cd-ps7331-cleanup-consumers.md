# Phase 5CD：PS7331 cleanup effect and second-consumer audit

日期：2026-08-04

範圍：PS7331 exact `kernel/locking/rtmutex.c`；host-only static dataflow。沒有
執行 futex、race、crash、PoC、root 或裝置操作。

## 直接回答

### 已證實：`if (ret)` 與 early return 都是修補鏈的一部分

- `task_blocks_on_rt_mutex()` 的 `owner == task` early return 位於
  `waiter->task = task` 之前；因此它是「waiter 尚未完整 enqueue/identity
  assignment」邊界的關鍵。
- `rt_mutex_start_proxy_lock()` 在 PS7331 使用 `if (unlikely(ret))` 進入
  `remove_waiter()`；因此任何尚未被前面邏輯正規化掉的非零返回，都會進入
  cleanup。這是 follow-up 修補鏈中的 cleanup gating 關鍵。
- 這兩者仍不是 primary `current`/explicit-task identity mismatch 的全部
  條件。即使把 cleanup gate 修好，仍需獨立證明 runtime proxy state 與後續
  consumer。

### 已證實：source 可描述 cleanup 後的欄位效果

在 `remove_waiter()` 內：

- 寫入的是 `current->pi_blocked_on = NULL`；
- 沒有看到 `waiter->task = NULL` 或 `waiter->lock = NULL`；
- 呼叫 `rt_mutex_dequeue(lock, waiter)`，該 helper 可能清除 waiter 的
  `tree_entry`；
- 在 top-waiter/owner 分支呼叫 `rt_mutex_dequeue_pi(owner, waiter)`，該 helper
  可能清除 `pi_tree_entry`；
- 這些 tree 清理是否真的在目標 runtime 狀態下發生，取決於 branch、node
  state 與 lock ownership，不能僅由 source mapping 宣稱。

若假設（尚未證明）當下存在 `current != waiter->task` 且 target task 已有
`pi_blocked_on`，則該 cleanup source 沒有直接清除 target task 的欄位。這是
條件式 source implication，不是已觀察到的持久 invariant violation。

### 高可信推論：存在可被正常路徑讀取的候選 consumer

Source 中下列路徑會讀取相關狀態：

- `task_blocked_on_lock(p)`：讀取 `p->pi_blocked_on`，再取 waiter 的 lock；
- `rt_mutex_adjust_prio_chain()`：讀取 task 的 `pi_blocked_on` 並沿 waiter/lock
  鏈處理；
- `rt_mutex_adjust_pi(task)`：重新檢查 task 的 blocked waiter；
- `mark_wakeup_next_waiter()`：選擇 waiter 後使用 `waiter->task` 作為 wake target。

另有可能改變或修復狀態的路徑：

- `try_to_take_rt_mutex()` 可以清除明確 task 的 `pi_blocked_on`；
- `rt_mutex_dequeue()` 與 `rt_mutex_dequeue_pi()` 可條件式清理 tree node。

這些是**候選 consumer／repair path**，不是 runtime 第二次消費證據。

## 尚未證明的層級

| 層級 | 本階段結果 |
|---|---|
| source pre-fix semantics | 已證實 |
| proxy API 可傳遞明確 task | 已證實 |
| `current != waiter->task` 真機成立 | 待驗證 |
| cleanup 後 target task 欄位持久殘留 | 待驗證 |
| 後續 consumer 實際讀到該殘留 | 待驗證 |
| 穩定 crash | 未證明 |
| controllable memory effect | 未證明 |
| kernel control/root | 未證明 |

## 安全邊界

本階段沒有提供或執行能建立 proxy waiter、安排 scheduler race、觸發 cleanup、
製造 crash、讀寫 kernel memory 或取得 root 的操作。若要跨越「source candidate」
到 runtime trigger，必須使用 exploit/reproducer；這超出本分析的安全執行範圍。
