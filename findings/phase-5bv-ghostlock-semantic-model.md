# Phase 5BV：GhostLock proxy-waiter cleanup semantic model

日期：2026-08-04

## 目的

把 PS7331 source 中的核心差異轉成可重現的最小語意測試，不執行 kernel
code，也不建構或執行 exploit。模型只表達以下條件：

```text
current task != waiter->task
```

這正是 proxy-lock API「為另一個 task 準備 waiter」時需要檢查的語意邊界。

## 結果

### 已證實（模型層級）

- pre-fix cleanup 模擬 `current->pi_blocked_on = NULL`。
- 當 `current` 與 `waiter->task` 不同時，模型會清除 current 的狀態，
  但 waiter task 的 `pi_blocked_on` 仍保留。
- fixed cleanup 模擬 `waiter->task->pi_blocked_on = NULL`，會清除正確 task。
- 當 current 與 waiter task 相同時，pre-fix 與預期結果一致；因此普通
  lock path 不足以重現這個 proxy-task mismatch。

### 高可信推論

這個模型與 PS7331 source 的下列觀察一致：

- `rt_mutex_start_proxy_lock()` 的 API 文件描述為替另一個 task 開始取得
  lock，位置在 `rtmutex.c:1644-1658`。
- error path 在 `rtmutex.c:1684` 呼叫 `remove_waiter(lock, waiter)`。
- PS7331 `remove_waiter()` 在 `rtmutex.c:1087-1089` 使用 current task
  cleanup，而 fixed reference 使用 `waiter_task = waiter->task`。

模型因此重現了**語意 mismatch**，但沒有重現 kernel memory corruption、
control-flow hijack、任意讀寫或 UID 轉換。

### 未證明

- 在 PS7331 真機上的 race timing。
- dangling state 是否能轉成可控 memory effect。
- 任何 root／kernel privilege transition。

## Reproduction

```sh
python3 -B -m unittest discover -s tests \
  -p 'test_phase5bv_ghostlock_semantics.py'

python3 -B tools/scripts/model_phase5bv_ghostlock_semantics.py \
  --output artifacts/phase5/phase5bv-ghostlock-semantic-model-YYYYMMDD-NN
```

測試輸出：4 tests，全部通過。結果與 SHA-256 位於：

`artifacts/phase5/phase5bv-ghostlock-semantic-model-20260804-01/`

## 安全邊界

本模型沒有使用 ADB、fastboot、bootloader、kernel memory、device node、
unknown ioctl、address、offset、gadget 或 payload；它不能被標示為 live
PoC 或 root test。
