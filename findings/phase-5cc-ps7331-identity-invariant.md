# Phase 5CC：PS7331 task-identity invariant audit

日期：2026-08-04

範圍：Fire OS 7.3.3.1／PS7331 exact `mt8183/4.4` source；host-only。沒有
執行 futex syscall、race trigger、PoC、root、裝置 I/O 或映像修改。

## 結論

### 已證實：source-level identity separation

精確 source 顯示下列角色不是由同一個欄位或同一個隱含 task 來源表示：

1. `struct futex_q` 將 `task` 定義為等待該 futex 的 task。`queue_me()` 在等待
   執行緒中寫入 `q->task = current`。
2. `futex_wait_requeue_pi()` 另外建立 stack-local `struct rt_mutex_waiter`，並先
   設定 `rt_waiter.task = NULL`；該 waiter 經由 `q.rt_waiter` 交給 requeue 路徑。
3. `futex_requeue()` 將 `this->rt_waiter` 與 `this->task` 作為兩個明確參數傳入
   `rt_mutex_start_proxy_lock()`。
4. `rt_mutex_start_proxy_lock()` 再把明確的 `task` 參數傳給
   `task_blocks_on_rt_mutex()`。
5. `remove_waiter()` 的 inspected source 以 `current->pi_lock` 及
   `current->pi_blocked_on = NULL` 執行 cleanup；它沒有以 `waiter->task` 取代
   `current`。

這構成一個**source-level identity mismatch permitted by interface**：proxy API
可接收一個明確 task，而 cleanup 使用呼叫當下的 `current`。在這些 scoped
functions 中沒有找到 `current == task` 或相反方向的直接 equality assertion。

### 高可信推論：source 允許跨執行緒角色傳遞

`futex_requeue()` 的 call site 傳遞儲存在 queue entry 的 `this->task`，而不是
在 call site 以 `current` 取代它；proxy API 也把 task 作為獨立參數。這表示
source/dataflow 沒有要求「執行 requeue 的 caller 必須就是原等待執行緒」。

這是比單純看到 `remove_waiter()` 使用 `current` 更強的 evidence，但仍只是
介面與資料流結論；它不等於已觀察到真機 scheduler interleaving。

### 待驗證：runtime invariant

本階段沒有也不會用 exploit 或 race reproducer 去製造下列狀態：

```text
current != waiter->task
```

因此下列項目仍未證明：

- Fire OS 真實 Android userspace 是否能在合法流程中進入此 PI requeue path；
- 實際 runtime 是否形成 `current != waiter->task`；
- 該狀態是否與 `remove_waiter()` 的錯誤 cleanup 同時發生；
- cleanup 後是否有可觀察的 kernel state corruption、control 或 privilege effect。

## Source evidence

| Evidence ID | Source location | Observation | Confidence |
|---|---|---|---|
| P5CC-001 | `kernel/futex.c`, `struct futex_q` | queue entry stores the waiting task | Confirmed |
| P5CC-002 | `kernel/futex.c`, `queue_me()` | `q->task = current` at enqueue | Confirmed |
| P5CC-003 | `kernel/futex.c`, `futex_wait_queue_me()` | wait path calls `queue_me()` before sleep | Confirmed |
| P5CC-004 | `kernel/futex.c`, `futex_wait_requeue_pi()` | separate `rt_mutex_waiter` object is attached to q | Confirmed |
| P5CC-005 | `kernel/futex.c`, `futex_wait_requeue_pi()` | `rt_waiter.task = NULL` before handoff | Confirmed |
| P5CC-006 | `kernel/futex.c`, `futex_wait_requeue_pi()` | requeue code may manipulate waiter while wait path sleeps, per source comment/call sequence | Confirmed, source scope |
| P5CC-007 | `kernel/futex.c`, `futex_requeue()` | proxy call receives `this->rt_waiter` and `this->task` | Confirmed |
| P5CC-008 | `kernel/locking/rtmutex.c`, `rt_mutex_start_proxy_lock()` | task is an explicit API parameter | Confirmed |
| P5CC-009 | `kernel/locking/rtmutex.c`, `rt_mutex_start_proxy_lock()` | explicit task is forwarded to task-blocking helper | Confirmed |
| P5CC-010 | `kernel/locking/rtmutex.c`, `task_blocks_on_rt_mutex()` | early `owner == task` return precedes waiter task assignment | Confirmed |
| P5CC-011 | `kernel/locking/rtmutex.c`, `task_blocks_on_rt_mutex()` | `waiter->task = task` on enqueue path | Confirmed |
| P5CC-012 | `kernel/locking/rtmutex.c`, `remove_waiter()` | cleanup locks `current->pi_lock` | Confirmed |
| P5CC-013 | `kernel/locking/rtmutex.c`, `remove_waiter()` | cleanup clears `current->pi_blocked_on` | Confirmed |
| P5CC-014 | scoped proxy/task/cleanup functions | no direct current/task equality assertion observed | Confirmed, bounded search |

Exact source hashes and line spans are recorded in the generated JSON artifact,
CSV table and evidence index. The source files are the same build-selected
members used by prior Phase 5BY/5CA/5CB reviews.

## What this does not establish

The result is not a live GhostLock validation and is not a root or privilege
gain result. It does not establish Android userspace reachability, SELinux or
seccomp behavior, scheduler timing, a race window, memory corruption, kernel
control, or a reliable exploit. No futex arguments, race schedule, kernel
address, gadget, ioctl, payload, or device procedure is included.

## Safe next research boundary

The remaining evidence can be pursued only through non-triggering observation,
vendor/AOSP documentation, and source/config review. A runtime race reproducer or
privilege-escalation test would cross the project safety boundary and is not
performed here.
