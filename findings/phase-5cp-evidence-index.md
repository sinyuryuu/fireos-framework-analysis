# Phase 5CP evidence index

本輪只做 host-only source/dataflow audit，並引用已保存的 fixed-reference
source。沒有裝置操作或 kernel execution。

| Evidence ID | Source | Location | SHA-256 | Observation | Classification |
|---|---|---|---|---|---|
| `P5CP-001` | PS7331 `futex.c` | `struct futex_q`, lines 231-241 | `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96` | queue stores a waiting task pointer | Confirmed, source scope |
| `P5CP-002` | PS7331 `futex.c` | `queue_me()`, line 2066 | same as above | waiting path writes `q->task = current` | Confirmed, source scope |
| `P5CP-003` | PS7331 `futex.c` | `futex_wait_requeue_pi()`, lines 2839-2997 | same as above | separate stack-local proxy waiter is attached to q | Confirmed, source scope |
| `P5CP-004` | PS7331 `futex.c` | `futex_wait_requeue_pi()`, line 2902 | same as above | wait path hands q to sleep/requeue protocol | Confirmed, source scope |
| `P5CP-005` | PS7331 `futex.c` | `futex_requeue()`, line 1963 | same as above | proxy call is made from requeue path | Confirmed, source scope |
| `P5CP-006` | PS7331 `futex.c` | `futex_requeue()`, line 1964 | same as above | passes stored `this->rt_waiter` | Confirmed, source scope |
| `P5CP-007` | PS7331 `futex.c` | `futex_requeue()`, line 1965 | same as above | passes stored `this->task`, not a call-site substitution | Confirmed, source scope |
| `P5CP-008` | PS7331 `rtmutex.c` | `rt_mutex_start_proxy_lock()`, line 1658 | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | proxy API accepts explicit task parameter | Confirmed, source scope |
| `P5CP-009` | PS7331 `rtmutex.c` | `rt_mutex_start_proxy_lock()`, line 1670 | same as above | explicit task forwarded to task-blocking helper | Confirmed, source scope |
| `P5CP-010` | PS7331 `rtmutex.c` | `task_blocks_on_rt_mutex()`, line 972 | same as above | early owner==task return precedes assignment | Confirmed, source scope |
| `P5CP-011` | PS7331 `rtmutex.c` | `task_blocks_on_rt_mutex()`, line 977 | same as above | assigned waiter identity is explicit task | Confirmed, source scope |
| `P5CP-012` | PS7331 `rtmutex.c` | `rt_mutex_start_proxy_lock()`, line 1683 | same as above | non-zero return enters cleanup branch | Confirmed, source scope |
| `P5CP-013` | PS7331 `rtmutex.c` | `rt_mutex_start_proxy_lock()`, line 1684 | same as above | cleanup calls `remove_waiter(lock, waiter)` | Confirmed, source scope |
| `P5CP-014` | PS7331 `rtmutex.c` | `remove_waiter()`, line 1089 | same as above | cleanup clears `current->pi_blocked_on` | Confirmed, source scope |
| `P5CP-RET-001` | PS7331 `rtmutex.c` | `rt_mutex_adjust_prio_chain()`, lines 641-645 | same as above | scoped deadlock branch can return `-EDEADLK` after waiter setup | Confirmed, source scope |
| `P5CP-FIX-001` | fixed reference | `linux-stable-v6.1.175.c:1515-1530,1565-1566` | `c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a` | fixed source documents `waiter::task != current` and cleans waiter task | Confirmed, reference scope |
| `P5CP-RUNTIME-001` | PS7331 captures | no same-execution proxy trace | N/A | `remove_waiter()` invocation not observed on device | Runtime unobserved |
| `P5CP-RUNTIME-002` | PS7331 captures | no post-cleanup state trace | N/A | wrong cleanup target and later consumer not observed | Runtime unobserved |
| `P5CP-SAFETY-001` | Phase 5CP generated audit | `artifacts/phase5/phase5cp-proxy-context-20260804-01/proxy-context.json` | `fe22c23f160fcbe2fb2e56a1924e45b19e07595c613a0c0f35a7a372f327bce7` | source-only; no syscall, race, device contact, payload or address | Confirmed safety scope |

## Runtime interpretation

`P5CP-001`–`P5CP-RET-001` prove source roles and control flow. They do not prove
that PS7331 userspace reached the path, that the error branch ran, or that any
memory-safety effect exists. `P5CP-RUNTIME-*` remains unobserved.
