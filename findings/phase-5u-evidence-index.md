# Phase 5U evidence index

| Evidence ID | Source | File／reference | Observation | Classification |
|---|---|---|---|---|
| `P5U-GHOST-001` | Linux upstream patch | `3bfdc63936dd4773109b7b8c280c0f3b5ae7d349` | Official fix changes `current` to `waiter->task` in `remove_waiter()` and related operations | 已證實 |
| `P5U-GHOST-002` | Amazon source comparison | `artifacts/phase5/exact-kernel-source-review-20260804-02/rtmutex-comparison.json` | Fire public `rtmutex.c` normalized content equals v4.4.146 reference | 已證實（source scope） |
| `P5U-GHOST-003` | Exact defconfig | `artifacts/phase5/exact-kernel-source-review-20260804-01/members/mt8183_defconfig.e1495a4e51db.txt` | `CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y` | 已證實（config scope） |
| `P5U-FRAG-001` | Exact defconfig | same defconfig, netfilter section | `NF_DUP_IPV4/6`, `XT_TARGET_TEE`, and `NF_TABLES` are unset | 已證實（defconfig scope） |
| `P5U-ANDROID-001` | Public Android review | `findings/phase-5o-android-public-poc-review.md` and `phase-5p-android-nearby-port-review.md` | Public ports are target/build-specific; no exact trona profile | 高可信推論／搜尋範圍限定 |
| `P5U-SAFETY-001` | Level 3 decision | `findings/phase-5u-ghostlock-level3-report.md` | No exploit, trigger, image write, or device mutation authorized or executed | 已證實 |
| `P5U-MATRIX-001` | Host-only generator | `artifacts/phase5/cve-2026-43499-43503-review-20260804-02/cve-surface-matrix.tsv` | Reproducibly records GhostLock source/config presence and the Fragnesia dup/TEE/nft config gate | 已證實（input scope） |
