# Phase 6C GhostLock patch-chain evidence index

## E6C-PC-01 — primary cleanup signature

- Source: PS7331 GPL tree
- File: `kernel/locking/rtmutex.c:1089`
- Artifact: `artifacts/phase6c/phase6c-ghostlock-patch-chain-20260804-01/patch-chain.csv`
- Observed: `current->pi_blocked_on = NULL` found; `waiter_task` local not found.
- Interpretation: source has the pre-fix cleanup-target shape represented by the cited primary upstream patch.
- Confidence: **已證實（source scope）**

## E6C-PC-02 — early-return wrapper signature

- Source: PS7331 GPL tree
- File: `kernel/locking/rtmutex.c:1683`
- Artifact: same `patch-chain.csv`
- Observed: `if (unlikely(ret)) remove_waiter(lock, waiter)` found; `ret < 0` form not found.
- Interpretation: wrapper retains the broad nonzero-return cleanup shape in the preserved source.
- Confidence: **已證實（source scope）**

## E6C-PC-03 — proxy path

- Source: PS7331 GPL tree
- Files: `kernel/locking/rtmutex.c:1656`, `kernel/futex.c:1963`, `kernel/futex.c:1971`
- Artifact: same `patch-chain.csv`
- Observed: proxy wrapper, futex-side proxy call and caller branch are present.
- Interpretation: static reachability candidate exists; branch execution is not shown.
- Confidence: **已證實（static scope）**

## E6C-PC-04 — upstream comparison

- Sources: public upstream commit references recorded in `patch-chain.json`
- URLs: `3bfdc63936dd4773109b7b8c280c0f3b5ae7d349`, `1a1fb985f2e2b85ec0d3dc2e519ee48389ec2434`, later guard discussion
- Observed: the comparison markers correspond to later cleanup-target, return-condition and waiter-state changes.
- Interpretation: PS7331 is strongly consistent with a pre-fix source relative to that chain.
- Confidence: **高可信推論**

## E6C-PC-05 — runtime boundary

- Source: Phase 6A/6B/6C records
- Files: `findings/phase-6a-untrusted-app-pi-smoke-test.md`, `findings/phase-6b-host-layout-model.md`, `findings/phase-6c-requeue-precondition-model.md`
- Observed: ordinary PI lock/unlock was reached; no requeue-PI proxy identity mismatch, residue, memory effect or privilege transition was preserved.
- Interpretation: the static patch-chain result is not a live exploit result.
- Confidence: **待驗證（runtime state）**

## E6C-PC-06 — safety boundary

- Source: tool safety fields and execution record
- Files: `patch-chain.json`, `result.md`
- Observed: host-only; no device contact, futex trigger, race, kernel memory access or payload.
- Interpretation: reproducible static audit only.
- Confidence: **已證實**
