# Phase 5DG evidence index

本輪 evidence 來自公開 reference repository 的 host-only source audit；
不代表 Fire OS runtime，也不包含可執行 payload。

| Evidence ID | Source | File / artifact | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| P5DG-001 | Git reference | datfooldive/ghostlock-emerald commit ebb355d302629a034d0959e5e579496559e8f84e | README/Makefile target MT6789, Linux 6.12, Android 16 | Reference target is not PS7331 | Confirmed |
| P5DG-002 | Reference source | src/core/slide.c | Explicit PI/requeue futex operation markers and multi-thread orchestration | Reference has a named userspace PI/requeue caller architecture | Confirmed |
| P5DG-003 | Reference source | src/core/fops.c, src/core/pipe_physrw.c | Later physrw/kernel-memory primitive markers | Reference has post-trigger stages beyond futex | Confirmed |
| P5DG-004 | Reference source | src/core/root.c, src/core/umh_root.c | Credential/usermode-helper transition markers | Reference includes a root stage; not a PS7331 result | Confirmed |
| P5DG-005 | Cross-phase comparison | Phase 5DD/5DE reports and Phase 5DF artifact | PS7331 preserved native/non-kernel inputs have no named requeue-PI caller; kernel dispatch exists | Bounded negative caller observation, not impossibility | Strong evidence |
| P5DG-006 | Safety boundary | findings/phase-6a-runtime-verification-boundary.md | No stock-device trigger, memory access, or root payload executed | Runtime gates remain unproven | Confirmed |

Confidence vocabulary: Confirmed, Strong evidence, Probable, Hypothesis,
Disproved.
