# Phase 5CD evidence index

Scope: PS7331 exact `rtmutex.c`; host-only cleanup/consumer mapping.

| Evidence ID | File/method | Observation | Confidence |
|---|---|---|---|
| P5CD-001 | `remove_waiter()` | current blocked state is cleared; waiter task/lock fields are not directly cleared | Confirmed, exact source |
| P5CD-002 | `rt_mutex_dequeue()` / `rt_mutex_dequeue_pi()` | lock and owner PI tree nodes are conditionally removed/cleared | Confirmed, exact source |
| P5CD-003 | `task_blocked_on_lock()`, `rt_mutex_adjust_prio_chain()`, `rt_mutex_adjust_pi()`, `mark_wakeup_next_waiter()` | candidate later readers/uses of related state | Confirmed as references; runtime unproven |
| P5CD-004 | `task_blocks_on_rt_mutex()` / `rt_mutex_start_proxy_lock()` | early return precedes assignment; PS7331 wrapper uses nonzero cleanup gate | Confirmed, exact source |
| P5CD-005 | generated artifact | reproducible mapping and safety boundary | Confirmed |

Exact hashes, line spans and matched text are in
`artifacts/phase5/phase5cd-ps7331-cleanup-consumers-20260804-01/cleanup-consumer-audit.json`.
