# Phase 6C：PS7331 requeue-PI protocol analysis

## 範圍

本報告只分析保存的 PS7331 7.3.3.1 GPL source。分析器沒有編譯或執行
selftest，沒有建立 thread、安排 race、呼叫 futex、接觸平板、讀寫 kernel
memory 或產生 payload。

分析器與 artifact：

- `tools/scripts/analyze_phase6c_requeue_protocol.py`
- `artifacts/phase6c/phase6c-requeue-protocol-analysis-20260804-01/`

## 靜態結果

### 已證實

1. `futextest.h:181-207` 將 `FUTEX_WAIT_REQUEUE_PI` 與
   `FUTEX_CMP_REQUEUE_PI` 定義為成對的兩半；註解明確說明第一半必須與第二半
   配對。
2. `futex_requeue_pi.c:111-141` 的 waiter 路徑先執行
   `futex_wait_requeue_pi()`，並在後續對目標 PI futex 做處理。
3. 同一 selftest 的 waker 路徑位於 `:147-190` 與 `:195-230`，另行執行
   `futex_cmp_requeue_pi()`；它先等待 waiter 進度，再進行 requeue。
4. `futex_requeue_pi_mismatched_ops.c:82-126` 的錯誤路徑測試也先建立 child
   waiter，再測試不匹配的 requeue 操作；它不是單次、單執行緒 switch probe。
5. PS7331 `kernel/futex.c:1716` 有 no-waiter return，而
   `:1963-1975` 才進入 proxy call／return-cleanup 區段。

### 高可信推論

「單執行緒、單次 `FUTEX_CMP_REQUEUE_PI`」最多能觀察無 waiter 或參數驗證
邊界，不能證明 `waiter->task` 與 `current` 的 proxy identity condition，
也不能證明 cleanup residue。

### 待驗證

- untrusted app 是否能建立匹配的 `WAIT_REQUEUE_PI` waiter；
- PS7331 stock runtime 是否實際進入 proxy error branch；
- cleanup 後是否有持久狀態不一致、第二次 consumer、memory effect 或 privilege
  transition。

### 因風險拒絕測試

本專案不在 stock tablet 執行 paired waiter、race scheduling、single-shot
panic、heap shaping、ION／pipe 佔位、kernel memory access 或 privilege
payload。這些操作會把研究從可逆 API reachability 推進到 kernel fault／提權
驗證，且無可靠的無損回復保證。

## 結論

Phase 6A 的 ordinary PI lock/unlock 成功，只能證明一般 untrusted app 的
基本 PI futex 介面可達。新增的 selftest protocol 分析反而確認：GhostLock
關鍵的 proxy identity 問題需要有狀態的 paired protocol，不能由單次 harmless
call 取代。現階段仍沒有 runtime mismatch、residue、memory corruption 或
root 的證據。
