# Phase 5CP：PS7331 proxy-task context audit

日期：2026-08-04
範圍：Fire OS 7.3.3.1／PS7331／MT8183／Linux 4.4 source
方法：主機端 bounded source/dataflow audit
安全狀態：沒有編譯或執行 kernel，沒有呼叫 futex syscall，沒有裝置 I/O、競速器、地址、payload 或提權操作。

## Executive result

本輪釐清一個容易混淆的點：`waiter->task != current` 在 proxy API 的 source
介面中，不必依賴 scheduler race 才能「允許」成立。等待者與執行 requeue 的
caller 是兩個明確的角色；真正尚未證明的是 error path 是否在真實裝置上執行，
以及 cleanup 後是否留下可被消費的錯誤狀態。

| 判定 | 結果 | 證據 |
|---|---|---|
| futex queue 將等待 task 綁到等待執行緒的 `current` | 已證實，source scope | `P5CP-001`, `P5CP-002` |
| requeue-PI path 將 stored `this->task` 傳給 proxy API | 已證實，source scope | `P5CP-005`–`P5CP-007` |
| proxy API 的 implicit `current` 可與 explicit `task` 分離 | 已證實，source interface scope | `P5CP-008`, `P5CP-009` |
| proxy error branch 會呼叫 `remove_waiter()` | 已證實，source scope | `P5CP-012`, `P5CP-013` |
| PS7331 cleanup 使用 `current->pi_blocked_on` | 已證實，source scope | `P5CP-014` |
| error branch 在 runtime 實際執行 | 尚未觀察 | `P5CP-RUNTIME-001` |
| cleanup 後的 task/PI state 不一致 | 尚未觀察 | `P5CP-RUNTIME-002` |
| root 或任意 kernel control | 未證明 | `P5CP-SAFETY-001` |

## 1. 精確 dataflow

### 1.1 Waiting task

PS7331 的 `struct futex_q` 將 `task` 描述為等待 futex 的 task：

```text
kernel/futex.c:231-241
struct task_struct *task;
```

`queue_me()` 在等待執行緒的 context 執行：

```text
kernel/futex.c:2049-2068
q->task = current;
```

### 1.2 Proxy waiter

`futex_wait_requeue_pi()` 另建一個 stack-local `rt_mutex_waiter`，並把它掛到
queue entry；同一等待路徑之後可能睡眠，讓 requeue caller 操作這個 waiter：

```text
kernel/futex.c:2839-2997
struct rt_mutex_waiter rt_waiter;
q.rt_waiter = &rt_waiter;
futex_wait_queue_me(hb, &q, to);
```

這不是把 `waiter` 與 caller 的 `current` 混為同一個物件，而是跨 context 的
proxy protocol。

### 1.3 Requeue caller

`futex_requeue()` 的 proxy call site 使用：

```text
kernel/futex.c:1959-1965
rt_mutex_start_proxy_lock(&pi_state->pi_mutex,
                          this->rt_waiter,
                          this->task);
```

因此，呼叫 `futex_requeue()` 的執行緒是當下的 implicit `current`，但傳入
proxy API 的 task 是 queue 中保存的 `this->task`。source 沒有在 call site
把 stored task 改成 caller `current`。

Linux source 對這種用途的註解也明確把 requeue-PI 與條件變數 signal/broadcast
分開描述（`futex.c:1785-1792`）。這支持「不同執行緒角色」是設計上的 API
使用方式；它仍不是 Fire Android userspace 已執行的證據。

## 2. Error path 與 early return

`rt_mutex_start_proxy_lock()`：

```text
rtmutex.c:1656-1691
ret = task_blocks_on_rt_mutex(lock, waiter, task,
                              RT_MUTEX_FULL_CHAINWALK);
if (ret && !rt_mutex_owner(lock))
    ret = 0;
if (unlikely(ret))
    remove_waiter(lock, waiter);
```

所以「identity 分離存在」與「錯誤 cleanup 真的執行」是兩個不同 gate。

`task_blocks_on_rt_mutex()` 的兩條關鍵語意：

```text
rtmutex.c:972-973   if (owner == task) return -EDEADLK;
rtmutex.c:975-988   waiter->task = task; ... task->pi_blocked_on = waiter;
```

early return 在 `waiter->task = task` 之前。這帶出兩個不同問題：

1. 若在 assignment 後的 chain walk 由 deadlock detection 回傳 non-zero，
   proxy error branch 可能進入 cleanup，而此時 explicit task 與 caller
   `current` 可是不同 task。
2. 若 `owner == task` 的 early return 直接使 `ret` 保持錯誤，waiter 可能尚未
   完成 task assignment；這是後續 null/initialization guard 的獨立問題，不能
   和 primary `current` versus `waiter->task` cleanup 混為一談。

本輪只作 source control-flow 分析，沒有建立任何 deadlock、race 或 syscall
觸發條件。

## 3. 與 fixed reference 的對照

保存的 fixed reference `linux-stable-v6.1.175.c`（SHA-256
`c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a`）在
`remove_waiter():1517-1569` 直接寫出：

```text
When invoked from rt_mutex_start_proxy_lock() waiter::task != current !
```

並將 `waiter->task` 保存為 `waiter_task`，使用該 task 的 `pi_lock` 與
`pi_blocked_on`。這是對 source-level cross-context identity 的直接參考證據，
也說明 upstream fix 不只是風格更名。

因此目前最精確的判斷是：

- PS7331 source 已確認保留 pre-fix cleanup semantics；
- fixed reference 已確認 proxy invocation 預期 `waiter::task != current`；
- 這仍不等於 PS7331 stock runtime 已執行該 error cleanup。

## 4. D1 重新分層

原本的 D1 用語容易把「source 允許」與「runtime observation」混在一起。本輪
改用兩個標籤：

| 層級 | 定義 | 狀態 |
|---|---|---|
| D1-S | source/dataflow 證明 proxy task 與 caller current 可分離 | 已證實 |
| D1-R | 同一次 stock kernel execution 觀察到 `waiter->task != current` | 尚未觀察 |
| D2 | 觀察到 wrong cleanup 寫入了哪個 task/field | 尚未觀察 |
| D3 | 後續 kernel consumer 重複消費錯誤狀態 | 尚未觀察 |
| D4 | 可控 memory effect 或 privilege transition | 未證明、未執行 |

這個分層讓研究進度變得更準確：D1-S 已不再是未知，但 D1-R、D2、D3、D4
仍然沒有實機證據。

## 5. 裝置與安全界線

本輪沒有在 PS7331 平板上執行 futex、PI、requeue、race 或任何 root POC。
既有裝置 evidence 仍只有 feature/config 與 visibility boundary；沒有 kernel
trace 能同時記錄 proxy task、cleanup executor 與後續 state。

不執行下列操作：

- stock device 上的 futex race/reproducer；
- crash/panic 或 kernel memory corruption trigger；
- kernel address/offset/gadget/credential targeting；
- 未知 ioctl、ION/CMDQ request、BROM/DA 或 boot image 注入；
- root payload、SELinux 修改或分割區寫入。

## 6. 最佳下一步

若目標是取得 D1-R/D2，最小可信環境是與 stock tablet 分離的 instrumented
research kernel 或 emulator，並只記錄：

```text
proxy API explicit task
proxy caller current
remove_waiter invocation
cleanup target field
post-cleanup invariant
```

在沒有這種觀測環境前，對原廠平板重複執行普通 userspace/ADB 命令不會提供
相同證據，亦不應把 reboot、ADB 斷線或 panic 當成 mismatch。

## Bottom line

本輪得到的最佳結果是：**identity mismatch 的 source-context 條件已確認為
proxy API 的正常跨執行緒角色分離，不需要先假設 scheduler race；但
GhostLock 的錯誤 cleanup runtime path、後續 state effect 與 root 仍未驗證。**
