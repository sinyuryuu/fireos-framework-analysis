# Phase 6C：proxy waiter identity state model

## Scope

這是 host-only source-order model，不執行 kernel、建立 thread、安排 race、
產生 futex 參數、操作 memory 或嘗試 root。

## Source-order observations

| Landmark | PS7331 line | Result |
|---|---:|---|
| `owner == task` early return | `rtmutex.c:972-973` | 早於 waiter identity assignment |
| `waiter->task = task` | `rtmutex.c:977` | enqueue preparation |
| `waiter->lock = lock` | `rtmutex.c:978` | waiter metadata assignment |
| `task->pi_blocked_on = waiter` | `rtmutex.c:986` | task-side PI link |
| local `rt_waiter` | `futex.c:2844` | local waiter object |
| `q.rt_waiter = &rt_waiter` | `futex.c:2880` | futex queue stores waiter pointer |
| proxy call | `futex.c:1963-1965` | passes `this->rt_waiter` and `this->task` |
| cleanup gate | `rtmutex.c:1683-1684` | broad nonzero return calls `remove_waiter()` |
| cleanup target | `rtmutex.c:1087-1089` | uses `current->pi_lock` and `current->pi_blocked_on` |

## Classification

- **已證實：** source ordering and dataflow landmarks listed above.
- **高可信推論：** the inspected code maintains separate stored waiter/task and
  current-task concepts on the proxy cleanup route.
- **待驗證：** whether the identities differ in stock runtime, whether cleanup
  leaves a persistent invariant violation, and whether a later consumer exists.
- **因風險拒絕測試：** device-side requeue-PI, multi-thread scheduling, race,
  panic, memory operation, or root payload.

The model deliberately does not infer `waiter->task != current` from the mere
presence of two source variables.

## Reproducibility

- Script: `tools/scripts/model_phase6c_identity_state.py`
- Artifact: `artifacts/phase6c/phase6c-identity-model-20260804-01/`
- Manifest: `sha256sums.txt`
