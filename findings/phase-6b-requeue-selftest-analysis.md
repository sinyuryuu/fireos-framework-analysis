# Phase 6B：requeue-PI selftest role analysis

## Scope

本輪只讀取 PS7331 source archive 中的 futex functional selftests、Makefile
與 runner。沒有編譯、執行、安裝、推送 selftest，也沒有對平板發送 futex
操作。

## Observed roles

| Input | Static observations | Meaning |
|---|---|---|
| `futex_requeue_pi.c` | `pthread_create`、`pthread_join`、waiter/waker/third-party roles；`futex_wait_requeue_pi` 與 `futex_cmp_requeue_pi` | 建立 waiter，再由另一個角色 requeue/wake |
| `futex_requeue_pi_mismatched_ops.c` | child thread 先 blocking；parent 再呼叫 `futex_cmp_requeue_pi`；最後 wake/join | 驗證 mismatch requires an existing waiter |
| `futex_requeue_pi_signal_restart.c` | RT waiter、`pthread_kill`、多次 requeue、`pthread_join` | 需要 signal timing 與 waiter lifecycle |
| `functional/Makefile` | `-pthread`；三個 requeue-PI target | selftest build 不是 single-thread harness |
| `functional/run.sh` | 多個 lock/broadcast/timeout/owner scenarios | 完整測試不是單一 switch probe |

## 判定

- **已證實：** PS7331 source archive 的 functional selftests 使用多角色
  waiter/waker 或 child/signal coordination。
- **高可信推論：** 「單執行緒、單次 `FUTEX_CMP_REQUEUE_PI`」不能重現這些
  selftest 所需的 proxy waiter setup，也不能作為 GhostLock runtime mismatch
  的等價驗證。
- **待驗證：** Fire shipped userspace 是否有其他途徑建立相同 waiter pairing。
- **已排除：** ordinary private PI lock/unlock smoke test 作為 requeue-PI
  proxy evidence。
- **因風險拒絕測試：** 在 stock tablet build/run selftests，或把 selftest
  改造成 race、kernel crash 或 root trigger。

## Reproducible output

- Script: `tools/scripts/analyze_phase6b_requeue_selftests.py`
- Artifact: `artifacts/phase6b/phase6b-requeue-selftests-20260804-01/`
- Files: `inventory.csv`, `inventory.json`, `result.md`, `sha256sums.txt`

這是 source/build provenance，不是 runtime reachability、memory corruption
或 privilege escalation 證據。
