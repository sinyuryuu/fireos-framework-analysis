# Phase 5CV：PS7331 `ret`／early-return／cleanup control-flow audit

日期：2026-08-04

## 核心結論

你指出的 `if (ret)` 與 early return 確實是修補語意鏈的重要分叉，但要
精確區分三件事：

1. `ret == 1` 的成功路徑會在 proxy wrapper 的最前段直接返回；它不會走
   `remove_waiter()`。
2. `task_blocks_on_rt_mutex()` 的 self-deadlock early return 在寫入
   `waiter->task` 前發生；這是另一個初始化／cleanup 邊界。
3. 只有在 owner 沒有被釋放、且後續 return state 仍為 nonzero 時，wrapper
   的 `if (unlikely(ret))` 才會呼叫 `remove_waiter()`。在這個可達範圍內，
   `ret` 主要是負錯誤；不能把文字上的 `if (ret)` 解讀成所有正值都會
   進 cleanup。

因此，真正的 static control-flow chain 是：

```text
try_to_take success
  → return 1

not acquired
  → task_blocks_on_rt_mutex
  → owner == task ? -EDEADLK (before waiter->task assignment)
  → otherwise assign waiter->task and continue
  → owner released ? reset ret to 0
  → remaining nonzero ret ? remove_waiter(lock, waiter)
```

`futex_requeue()` 再依 proxy result 分成 success／queue／failure state path。

## 1. PS7331 source facts

Exact source path：

`artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/`

### `task_blocks_on_rt_mutex()`

- self-deadlock check：source lines 972–973；
- `waiter->task = task`：source line 977；
- `task->pi_blocked_on = waiter`：source line 986。

The early branch therefore returns before the normal waiter binding and PI
blocked-on assignment. This is a source-level fact; it is not evidence that a
stock device reaches that branch through an externally controllable sequence.

### `rt_mutex_start_proxy_lock()`

- direct lock acquisition returns `1` before `task_blocks_on_rt_mutex()`;
- owner-release condition can turn a nonzero result into `0`;
- remaining `ret` invokes `remove_waiter()`;
- PS7331 `remove_waiter()` uses `current` for PI cleanup.

The key point is dataflow: the same source method has a direct success return,
an early deadlock return and a later cleanup branch. A text search for
`if (ret)` cannot distinguish these paths.

### `futex_requeue()`

The proxy call passes the stored waiter task to
`rt_mutex_start_proxy_lock()`. Its result then selects the wake, requeue or
failure handling path. That is why the return value matters for the later
state machine, but the source still does not demonstrate a runtime identity
mismatch or persistent state damage.

## 2. Relation to GhostLock

### 已證實

- PS7331 has the early-return-before-waiter-assignment branch.
- PS7331 has the owner-release return reset.
- PS7331 has the proxy cleanup callsite and current-based cleanup.
- PS7331 futex source passes a stored waiter task into the proxy API.

### 高可信推論

- The `ret` domain and early-return ordering are necessary to classify which
  cleanup paths are even reachable.
- A proxy mismatch analysis must separate an initialized waiter from the
  early-return-before-assignment case.

### 待驗證

- Whether a stock Fire userspace sequence reaches the proxy error branch.
- Whether a same-execution `waiter->task != current` state reaches cleanup.
- What state remains after cleanup and which later path consumes it.

### 因風險拒絕測試

- Driving the PI-requeue self-deadlock sequence on the tablet.
- Building/running a futex race or adapting Emerald's trigger.
- Inspecting or modifying kernel memory to confirm a dangling state.

## 3. Reproducibility

The source mapping is reproducible from the exact PS7331 source artifacts and
the public Phase 5 reports. The sanitized table and call graph are:

- `output/tables/phase5cv-ret-early-return.csv`
- `output/call-graphs/phase5cv-ret-early-return.mmd`

This phase intentionally does not emit a runnable trigger or root payload.
