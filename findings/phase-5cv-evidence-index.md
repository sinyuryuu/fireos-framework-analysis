# Phase 5CV evidence index

本輪只做 PS7331 exact source 的 host-side control-flow review；沒有編譯、
執行 kernel／userspace trigger、接觸裝置或產生 exploit payload。

| Evidence ID | Source | Location | Observation | Interpretation | Confidence |
|---|---|---|---|---|---|
| `P5CV-001` | PS7331 `rtmutex.c` | `rt_mutex_start_proxy_lock()` | `try_to_take_rt_mutex()` 成功時直接 return `1` | `ret=1` 不會落入後續 `remove_waiter()` | Confirmed, source scope |
| `P5CV-002` | PS7331 `rtmutex.c` | `task_blocks_on_rt_mutex()` | self-deadlock branch 回傳 `-EDEADLK`，早於 `waiter->task = task` | early return 改變 waiter 初始化狀態 | Confirmed, source scope |
| `P5CV-003` | PS7331 `rtmutex.c` | proxy wrapper | owner 已釋放時可將 nonzero `ret` reset 為 `0` | cleanup 是否發生取決於 owner／return state | Confirmed source scope; runtime unobserved |
| `P5CV-004` | PS7331 `rtmutex.c` | proxy wrapper | `if (unlikely(ret)) remove_waiter(...)` | 需按可達 return domain 解讀，不能只看語法 | Confirmed, control-flow scope |
| `P5CV-005` | PS7331 `futex.c` | `futex_requeue()` proxy callsite | `ret==1`、`ret==0`、negative result 進入不同 requeue state path | proxy outcome 是後續 state transition 的分流點 | Confirmed, source scope |
| `P5CV-006` | PS7331 `rtmutex.c` | `remove_waiter()` | cleanup 使用 implicit `current` | proxy caller／stored waiter identity 仍是核心 mismatch | Confirmed, source scope |
| `P5CV-D1` | existing Phase 5CP/5CK runtime captures | stock PS7331 | 沒有同一次 execution 的 cleanup trace、identity mismatch 或 residue | dynamic validation 未開始 | Unobserved |

## Exact source artifacts

- `artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`
- `artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c`

## Interpretation rule

`if (ret)` 不是獨立的 exploit proof。必須同時確認 return domain、early
return 前後 waiter state、owner-release reset、cleanup target，以及後續
consumer；目前只有前四項的 source mapping，沒有 runtime observation。
