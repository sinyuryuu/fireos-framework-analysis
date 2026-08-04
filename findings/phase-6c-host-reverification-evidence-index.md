# Phase 6C host-only re-verification evidence index

## P6C-HOST-001

- Source: exact PS7331 futex/rtmutex source audit
- File: `artifacts/phase6c/phase6c-dispatch-audit-20260804-01/summary.json`
- SHA-256: recorded in `artifacts/phase6c/phase6c-dispatch-audit-20260804-01/sha256sums.txt`
- Test ID: `PHASE6C-HOST-REVERIFY-20260804-01`
- Timestamp: `2026-08-04T13:10:31Z`
- Command: `python3 tools/scripts/audit_phase5df_futex_dispatch_boundary.py --kernel-root firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4 --output artifacts/phase6c/phase6c-dispatch-audit-20260804-01`
- Observed result: 29 source landmark rows; source execution, device contact, futex trigger, kernel memory access and payload generation all recorded as false.
- Interpretation: dispatch/proxy/cleanup source chain is reproducibly present; no runtime reachability or exploitability follows.
- Confidence: **Confirmed**
- Related hypothesis: PS7331 retains the pre-fix-shaped GhostLock source path.

## P6C-HOST-002

- Source: exact PS7331 proxy identity state model
- File: `artifacts/phase6c/phase6c-identity-model-20260804-02/identity-model.json`
- SHA-256: recorded in `artifacts/phase6c/phase6c-identity-model-20260804-02/sha256sums.txt`
- Test ID: `PHASE6C-HOST-REVERIFY-20260804-02`
- Timestamp: `2026-08-04T13:10:31Z`
- Command: `python3 tools/scripts/model_phase6c_identity_state.py --source-root firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4 --output artifacts/phase6c/phase6c-identity-model-20260804-02`
- Observed result: all five source-order booleans are true: early return ordering, waiter identity setup, stored-task proxy argument, current cleanup, and broad nonzero cleanup gate.
- Interpretation: source preserves the separate identity dataflow; it does not show that identities differ at runtime.
- Confidence: **Confirmed** for source ordering; **待驗證** for runtime mismatch.
- Related hypothesis: `waiter->task != current` can occur on PS7331.

## P6C-HOST-003

- Source: prior Phase 6A and Phase 6B evidence
- File: `findings/phase-6a-pi-lock-smoke-evidence-index.md`, `findings/phase-6-step4-source-safety-analysis.md`
- SHA-256: each source file/artifact has its own preserved manifest
- Test ID: prior Phase 6A/6B IDs
- Timestamp: preserved in the referenced evidence indexes
- Command: prior ordinary private PI smoke and host-only source analysis
- Observed result: ordinary private PI lock/unlock succeeded in the bounded smoke test; requeue-PI was not executed; exact source shows requeue-PI is stateful and can enter proxy cleanup.
- Interpretation: Phase 6A does not substitute for the rejected Step 4 runtime trigger.
- Confidence: **Confirmed**
- Related hypothesis: ordinary PI syscall capability proves requeue-PI exploitability.
