# Phase 6C requeue-PI precondition model

## Purpose

This host-only model answers whether the proposed single-thread/single-call
Step 4 can observe the GhostLock identity condition. It reads the exact PS7331
7.3.3.1 `futex.c` and `rtmutex.c`; it does not construct syscall arguments,
compile or execute a test, contact the tablet, create threads, schedule a race,
access kernel memory, or emit a payload.

Artifact:

`artifacts/phase6c/phase6c-requeue-preconditions-20260804-02/`

## Source facts — Confirmed

- `futex.c:1775` rejects identical futex addresses for requeue-PI.
- `futex.c:1782` may refill the PI-state cache before waiter discovery.
- `futex.c:1794` requires `nr_wake == 1`.
- `futex.c:1713-1716` looks up `top_waiter` and returns 0 when no waiter exists.
- `futex.c:1849-1857` enters the proxy try-lock path only under the requeue-PI
  task-count condition.
- `futex.c:1932-1936` requires a matching `rt_waiter`; `futex.c:1950-1953`
  checks the requeue key.
- `futex.c:1963-1965` passes `this->rt_waiter` and `this->task` to
  `rt_mutex_start_proxy_lock()`.
- `futex.c:1971-1975` handles a nonzero proxy return.
- `rtmutex.c:1670-1684` performs proxy task blocking and cleanup.
- `rtmutex.c:972-977` performs the early owner/task check before assigning
  `waiter->task`; `rtmutex.c:986` assigns `task->pi_blocked_on`.
- `rtmutex.c:1089` clears `current->pi_blocked_on` in `remove_waiter()`.

## Abstract state matrix

| State | Required context | Proxy call | Identity condition observable | Side effect possible | Classification |
|---|---|---:|---:|---:|---|
| Single context, no waiter | One caller and no matching pre-existing `WAIT_REQUEUE_PI` waiter | No | No | Yes, PI-state preparation may occur | Not a proxy runtime test |
| Paired waiter/proxy candidate | Pre-existing matching waiter plus requeue caller | Yes | Yes | Yes | Stateful experiment; stock-device test rejected |

## Decision

### 已證實

A single-thread/single-call no-waiter test can at most classify the no-waiter
branch. It cannot observe `waiter->task != current`, because the proxy call is
not reached without a matching waiter.

### 高可信推論

The proposed Step 4 is not a harmless syscall-switch probe. Even the no-waiter
path is not strictly read-only because PI-state preparation occurs before the
waiter lookup. The identity question requires a paired waiter/proxy context.

### 待驗證

- Whether a stock Fire process can create the matching waiter under its actual
  policy.
- Whether the proxy error branch executes on the stock scheduler.
- Whether any cleanup residue is persistent or consumed later.

### 因風險拒絕測試

No single-call device harness, paired waiter, race, kernel panic test, memory
operation or root payload is run. The paired state is exactly the stateful
path under investigation, and a return code cannot certify absence of side
effects.

## Reproduction

```sh
python3 tools/scripts/model_phase6c_requeue_preconditions.py \
  --source-root firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4 \
  --output artifacts/phase6c/phase6c-requeue-preconditions-YYYYMMDD-NN
```

The script refuses to overwrite an existing output directory and supports
`--dry-run`. The first draft output from 2026-08-04 was not used because its
proxy-cleanup landmark search was too broad; the corrected run is
`phase6c-requeue-preconditions-20260804-02`.
