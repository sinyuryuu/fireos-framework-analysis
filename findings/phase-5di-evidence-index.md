# Phase 5DI evidence index

| Evidence ID | Source | File / artifact | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| P5DI-001 | Preserved ODEX | artifacts/services/services.odex | AArch64 ELF; no named futex/requeue/rtmutex/syscall marker | No visible caller marker in this ODEX | Strong evidence |
| P5DI-002 | Preserved ODEX | artifacts/services/fosservices.odex | AArch64 ELF; no named futex/requeue/rtmutex/syscall marker | No visible caller marker in this ODEX | Strong evidence |
| P5DI-003 | Reproducible scan | tools/scripts/audit_phase5dd_native_futex_surface.py | Metadata/string/symbol-only scan, no execution | Observation is bounded and repeatable | Confirmed |
| P5DI-004 | Cross-phase boundary | findings/phase-6a-runtime-verification-boundary.md | Runtime identity mismatch/residue/root remain unobserved | Static absence does not close runtime gate | Confirmed |
