# Phase 5CC evidence index

Scope: PS7331 exact source, host-only. No device execution.

| Evidence ID | Source | File | SHA-256 | Observation | Confidence |
|---|---|---|---|---|---|
| P5CC-001 | exact PS7331 source | `kernel/futex.c` `struct futex_q` | see generated artifact | queue entry declares task identity | Confirmed |
| P5CC-002 | exact PS7331 source | `kernel/futex.c` `queue_me()` | see generated artifact | q task is bound to current at enqueue | Confirmed |
| P5CC-003 | exact PS7331 source | `kernel/futex.c` `futex_wait_queue_me()` | see generated artifact | wait path reaches queue binding | Confirmed |
| P5CC-004 | exact PS7331 source | `kernel/futex.c` `futex_wait_requeue_pi()` | see generated artifact | separate PI waiter object | Confirmed |
| P5CC-005 | exact PS7331 source | `kernel/futex.c` `futex_wait_requeue_pi()` | see generated artifact | rt waiter task initialized separately | Confirmed |
| P5CC-006 | exact PS7331 source | `kernel/futex.c` `futex_wait_requeue_pi()` | see generated artifact | requeue handoff path | Confirmed, source scope |
| P5CC-007 | exact PS7331 source | `kernel/futex.c` `futex_requeue()` | see generated artifact | stored waiter task passed to proxy | Confirmed |
| P5CC-008 | exact PS7331 source | `kernel/locking/rtmutex.c` `rt_mutex_start_proxy_lock()` | see generated artifact | explicit task parameter | Confirmed |
| P5CC-009 | exact PS7331 source | `kernel/locking/rtmutex.c` `rt_mutex_start_proxy_lock()` | see generated artifact | explicit task forwarded | Confirmed |
| P5CC-010 | exact PS7331 source | `kernel/locking/rtmutex.c` `task_blocks_on_rt_mutex()` | see generated artifact | early deadlock branch | Confirmed |
| P5CC-011 | exact PS7331 source | `kernel/locking/rtmutex.c` `task_blocks_on_rt_mutex()` | see generated artifact | waiter task assignment | Confirmed |
| P5CC-012 | exact PS7331 source | `kernel/locking/rtmutex.c` `remove_waiter()` | see generated artifact | cleanup uses current pi lock | Confirmed |
| P5CC-013 | exact PS7331 source | `kernel/locking/rtmutex.c` `remove_waiter()` | see generated artifact | cleanup clears current blocked state | Confirmed |
| P5CC-014 | bounded source search | proxy/task/cleanup functions | see generated artifact | no direct current/task equality assertion | Confirmed, bounded search |
| P5CC-015 | execution record | `artifacts/phase5/phase5cc-ps7331-identity-invariant-20260804-01/` | generated manifest | host-only analyzer and safety boundary | Confirmed |

The generated `identity-audit.json` is authoritative for exact paths, hashes,
line numbers and matched source text. “See generated artifact” is intentional
to avoid duplicating long hashes in this human-maintained index.
