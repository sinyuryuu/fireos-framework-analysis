# Phase 6C：PS7331 GhostLock upstream patch-chain 稽核

## 範圍與安全界線

本輪只在主機上讀取保存的 PS7331 GPL source，將其與公開 upstream
patch-chain 的高階語意標記比對。沒有執行 PoC、沒有編譯或執行 kernel、沒有
呼叫 futex、沒有建立 waiter／thread、沒有安排 race、沒有接觸裝置、沒有讀寫
kernel memory，也沒有產生 exploit 或 root payload。

分析器：`tools/scripts/audit_phase6c_ghostlock_patch_chain.py`

Canonical artifact：
`artifacts/phase6c/phase6c-ghostlock-patch-chain-20260804-01/`

## 輸入完整性

| Input | SHA-256 |
|---|---|
| `kernel/futex.c` | `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96` |
| `kernel/locking/rtmutex.c` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` |
| `kernel/locking/rtmutex_common.h` | `b3456f9e83a1919e41a88a6638ad1e26ed9966e800c6efc823940df1151919fc` |

## 靜態結果

### 已證實（source scope）

PS7331 source 保留以下可定位的程式形狀：

| Landmark | Location | Observation |
|---|---|---|
| waiter task assignment | `kernel/locking/rtmutex.c:977` | `waiter->task = task` |
| primary cleanup target | `kernel/locking/rtmutex.c:1089` | `current->pi_blocked_on = NULL` |
| proxy wrapper | `kernel/locking/rtmutex.c:1656` | `rt_mutex_start_proxy_lock()` 存在 |
| wrapper cleanup branch | `kernel/locking/rtmutex.c:1683` | `if (unlikely(ret)) remove_waiter(lock, waiter)` |
| futex proxy call | `kernel/futex.c:1963` | 呼叫 `rt_mutex_start_proxy_lock()` |
| futex caller branch | `kernel/futex.c:1971` | `else if (ret)` 分支存在 |

自動化檢查的結果：

- primary fix 需要的 `waiter_task` local 未出現；
- wrapper 的 `ret < 0` 窄化條件未出現；
- later unenqueued-waiter guard 未出現；
- proxy call site 與 caller branch 存在。

### 高可信推論

相對於下列公開 upstream patch-chain，PS7331 source 呈現 pre-fix signature：

1. `3bfdc63936dd4773109b7b8c280c0f3b5ae7d349`：cleanup 以
   `waiter::task` 為目標，而非依賴 `current`；
2. `1a1fb985f2e2b85ec0d3dc2e519ee48389ec2434`：early-return cleanup 的條件與
   路徑被修正；
3. 後續討論的 enqueued／null waiter guard：避免在不適合 cleanup 的狀態使用
   waiter。

公開參考：

- <https://git.kernel.org/stable/c/3bfdc63936dd4773109b7b8c280c0f3b5ae7d349>
- <https://git.kernel.org/stable/c/1a1fb985f2e2b85ec0d3dc2e519ee48389ec2434>
- <https://lkml.iu.edu/2606.0/06468.html>

### 待驗證

這份 source-level 結果不能回答：

- stock userspace 是否能形成 proxy waiter；
- `waiter->task != current` 是否在實機成立；
- error branch／cleanup 是否曾在實機執行；
- cleanup 後是否留下 residue 或由後續路徑消費；
- 是否有 kernel crash、可控制 memory effect 或 privilege transition。

### 因風險拒絕測試

本專案不在 stock device 執行 requeue-PI 觸發、paired waiter、race scheduling、
single-shot panic、heap shaping、ION／pipe 佔位、KASLR live extraction、kernel
memory operation 或 privilege escalation。即使聲稱「單執行緒、單次、合法參數」，
該 syscall 仍進入正在研究的 PI proxy state machine，不能視為純 read-only probe。

## 結論

**已證實：** PS7331 source 在研究的 cleanup／proxy／futex dispatch 形狀上是
pre-fix-consistent。

**未證實：** 這不等於 GhostLock 在 PS7331 上可觸發，也不等於存在 temporary
root。現有證據仍停在 source/config/provenance 層，尚未跨過 runtime identity
mismatch、residue、memory effect 和 privilege transition 四道門檻。

## 重現

```sh
python3 tools/scripts/audit_phase6c_ghostlock_patch_chain.py --dry-run \
  --source-root firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4 \
  --output artifacts/phase6c/phase6c-ghostlock-patch-chain-YYYYMMDD-NN

python3 tools/scripts/audit_phase6c_ghostlock_patch_chain.py \
  --source-root firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4 \
  --output artifacts/phase6c/phase6c-ghostlock-patch-chain-YYYYMMDD-NN
```

工具拒絕覆寫既有 output；`--dry-run` 不讀取裝置、不執行 kernel，實際模式也只
讀取 host source。
