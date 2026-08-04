# Phase 5CW evidence index

本輪證據均為 host-side source review；沒有執行 futex、race、kernel memory
操作或 root payload。

| Evidence ID | Source | File／位置 | Observation | Interpretation | Confidence |
|---|---|---|---|---|---|
| P5CW-001 | PS7331 exact source | `rtmutex.c:1079-1129`, `:1089` | `remove_waiter()` 使用 `current->pi_blocked_on = NULL` | primary waiter-task cleanup fix 尚未出現在此 source | Confirmed／source scope |
| P5CW-002 | PS7331 exact source | `rtmutex.c:1656-1691`, `:1683-1684` | `if (unlikely(ret)) remove_waiter(lock, waiter)` | wrapper 仍是 broad-return cleanup shape | Confirmed／source scope |
| P5CW-003 | PS7331 exact source | `rtmutex.c:952-1032`, `:973`, `:977` | `-EDEADLK` 早於 `waiter->task = task` | early-return／未完成 binding 邊界存在於 source | Confirmed／source scope |
| P5CW-004 | PS7331 exact source | `futex.c:1963` 附近 | proxy call 傳入保存的 `this->task` | proxy API 的 task argument 與呼叫者 context 在 source 上分離 | Confirmed／source scope |
| P5CW-005 | Linux upstream | `3bfdc63936dd` | primary fix 改用 `waiter->task` 做 PI cleanup／chain adjustment | upstream 修補直接對應 identity-cleanup 缺陷 | Confirmed／upstream source |
| P5CW-006 | Linux upstream follow-up | commit `40a25d59e85b3c8709ac2424d44f65610467871e` | un-enqueued waiter guard + `ret < 0` | early-return 與正值成功路徑另有修補需求 | Confirmed／upstream patch |
| P5CW-007 | Host marker audit | `artifacts/phase5/phase5cw-upstream-followup-markers-20260804-01/summary.json` | PS7331=`PRE_PRIMARY_FIX_SHAPE` + `BROAD_RET_CLEANUP_SHAPE` | exact source 與上游兩層修補形狀可重現比對 | Confirmed／host-only |
| P5CW-D1 | Device/runtime evidence boundary | existing Phase 5 captures | 沒有同次 execution 的 `waiter->task != current` observation | dynamic identity mismatch 尚未捕獲 | Unobserved |
| P5CW-D2 | Safety boundary | this phase execution log | 沒有 trigger、race、kernel memory、crash 或 root test | 不可據此宣稱 runtime exploitability | Confirmed |

## Confidence vocabulary

- **Confirmed／source scope**：由 exact source marker 或 upstream patch 直接支持。
- **High-confidence inference**：由多個 source path 一致指向，但尚未有 stock
  runtime observation。
- **Unobserved**：現有資料沒有觀察到，不能解讀為不存在。
- **Disallowed test**：會直接觸發核心漏洞或提權路徑，因此不執行。
