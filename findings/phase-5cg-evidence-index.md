# Phase 5CG evidence index

Test ID: `PHASE5CG-STATIC-20260804-01`

Scope: host-only inspection of exact PS7331 source and an abstract branch model.

Device mutation: none.

| Evidence ID | Source | File / location | Observation | Confidence | Related question |
|---|---|---|---|---|---|
| P5CG-001 | Exact PS7331 source | `.../kernel/locking/rtmutex.c`, `task_blocks_on_rt_mutex()` lines 972–977 | `owner == task` returns `-EDEADLK` before `waiter->task = task` | Confirmed | Does early return precede waiter initialization? |
| P5CG-002 | Exact PS7331 source | `.../kernel/locking/rtmutex.c`, `rt_mutex_start_proxy_lock()` lines 1673–1684 | nonzero result is normalized only when no owner is present; otherwise broad `if (unlikely(ret))` selects cleanup | Confirmed | What does `if (ret)` gate? |
| P5CG-003 | Exact PS7331 source | `.../kernel/locking/rtmutex.c`, `remove_waiter()` line 1089 | cleanup writes `current->pi_blocked_on = NULL` | Confirmed | Which task is directly written? |
| P5CG-004 | Exact PS7331 source | `.../kernel/mediatek/mt8183/4.4/kernel/futex.c`, `futex_requeue()` lines 1966–1971 | `ret == 1` is the wake branch; another nonzero result is the error branch | Confirmed | How is the proxy result consumed by futex requeue? |
| P5CG-005 | Exact-source host model | `artifacts/phase5/phase5cg-ps7331-cleanup-semantics-20260804-01/cleanup-semantics.json` | model reproduces the source branch predicates and records no runtime observation | Confirmed | Does the model match exact source? |
| P5CG-006 | Exact-source host model | same artifact, `identity_different_task_target_state_present` row | if identity mismatch and target state are assumed, current is cleared while target state is not directly cleared | Strong evidence | What conditional residue follows from the source write target? |
| P5CG-007 | Test | `tests/test_model_phase5cg_ps7331_cleanup_semantics.py` | fixture test passes for early return, broad cleanup, current write and conditional target residue | Confirmed | Is the model reproducible? |
| P5CG-008 | Source hashes | exact source SHA-256 recorded in `cleanup-semantics.json` | futex source `ca9140...ca7a96`; rtmutex source `6cb544...75dde` | Confirmed | Is the analyzed source pinned? |
| P5CG-009 | Safety boundary | model result and README | no futex syscall, race trigger, unknown ioctl, address, payload, device I/O or root transition | Confirmed | Was runtime exploitability tested? |

## Reproduction

```sh
python3 tools/scripts/model_phase5cg_ps7331_cleanup_semantics.py \
  --futex artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c \
  --rtmutex artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c \
  --output artifacts/phase5/phase5cg-ps7331-cleanup-semantics-REPRODUCTION
python3 -m unittest tests.test_model_phase5cg_ps7331_cleanup_semantics
```

The reproduction output must be a new directory; the script refuses to
overwrite an existing output directory.

## Evidence limitation

The model proves source predicates and conditional consequences only. It does
not prove that Android userspace can form a proxy waiter with
`current != waiter->task`, that the state persists after cleanup, that a later
consumer observes it, or that any crash, memory effect or privilege change
occurs.
