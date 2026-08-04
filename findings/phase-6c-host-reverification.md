# Phase 6C host-only re-verification of the PS7331 requeue-PI boundary

## Scope and safety

This run re-read the preserved PS7331 7.3.3.1 kernel source only. It did not
contact ADB, compile or boot a kernel, create futex arguments, create a waiter,
schedule threads, enable tracing, calculate a KASLR slide, access kernel
memory, generate a payload, or attempt root.

Inputs:

- Source root:
  `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4`
- `kernel/futex.c` SHA-256:
  `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`
- `kernel/locking/rtmutex.c` SHA-256:
  `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`
- `kernel/locking/rtmutex_common.h` SHA-256:
  `b3456f9e83a1919e41a88a6638ad1e26ed9966e800c6efc823940df1151919fc`

## Source landmarks — Confirmed

The fresh host-only audit found 29 landmark rows. The relevant chain is:

```text
futex syscall
  -> kernel/futex.c:3238, 3268-3269
  -> futex_requeue(..., requeue_pi=1)
  -> kernel/futex.c:1849-1856 proxy precondition / trylock
  -> kernel/futex.c:1963-1965
       rt_mutex_start_proxy_lock(..., this->rt_waiter, this->task)
  -> kernel/futex.c:1971 if (ret) cleanup
  -> kernel/locking/rtmutex.c:1656-1684
       proxy wrapper / remove_waiter()
  -> kernel/locking/rtmutex.c:1089
       current->pi_blocked_on = NULL
```

The identity model independently reports:

- early deadlock return precedes waiter-task assignment;
- `waiter->task = task` at line 977 precedes `task->pi_blocked_on = waiter` at
  line 986;
- the futex proxy call passes the stored task at line 1965;
- proxy cleanup uses a broad nonzero-return gate at line 1683;
- `remove_waiter()` clears the current task field at line 1089.

Evidence: `P6C-HOST-001`, `P6C-HOST-002`.

## Interpretation

### 已證實

The preserved PS7331 source contains the pre-fix-shaped dispatch, proxy
argument flow, and cleanup markers. The source is consistent with the earlier
PS7331-versus-legacy-v4.4.146 comparison.

### 高可信推論

The code path is structurally capable of carrying a stored waiter/task pair
separately from `current`. This is a source/dataflow property, not a proof that
the two task identities differ in a stock runtime.

### 待驗證

No source-only analysis can establish any of the following:

1. a non-privileged PS7331 process can form the required requeue waiter;
2. `waiter->task != current` occurs on the real scheduler;
3. cleanup leaves a persistent invariant violation;
4. a later kernel path consumes such a violation;
5. any memory safety effect or privilege transition follows.

### 因風險拒絕測試

The real-device single-thread Step 4 harness remains rejected. The syscall
dispatch itself can prepare PI state and can reach the proxy path; a return
value of `0` or an errno would not prove that no kernel state was changed.
The same boundary applies to `FUTEX_WAIT_REQUEUE_PI`, paired waiter creation,
race scheduling, heap/ION/pipe shaping, panic tests, kernel memory operations,
and root payloads.

## Reproducible offline commands

```sh
SRC=firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4

python3 tools/scripts/audit_phase5df_futex_dispatch_boundary.py \
  --kernel-root "$SRC" \
  --output artifacts/phase6c/phase6c-dispatch-audit-YYYYMMDD-NN

python3 tools/scripts/model_phase6c_identity_state.py \
  --source-root "$SRC" \
  --output artifacts/phase6c/phase6c-identity-model-YYYYMMDD-NN
```

Both scripts refuse to overwrite an existing output directory and support
`--dry-run`.

Artifacts for this run:

- `artifacts/phase6c/phase6c-dispatch-audit-20260804-01/`
- `artifacts/phase6c/phase6c-identity-model-20260804-02/`

Both SHA-256 manifests were verified after generation.
