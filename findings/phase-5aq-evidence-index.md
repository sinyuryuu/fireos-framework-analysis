# Phase 5AQ evidence index

| Evidence ID | Source | File | Observation | Confidence |
|---|---|---|---|---|
| `P5AQ-001` | PS7331 IKCONFIG extraction | `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config` | PS7331 config is embedded between `IKCFG_ST` and `IKCFG_ED` | 已證實 |
| `P5AQ-002` | PS7330 device capture | `adb/phase5/PHASE5AQ-DEVICE-CONFIG-20260804-02/kernel.config` | exact live PS7330 config captured and gzip-validated | 已證實 |
| `P5AQ-003` | Config comparator | `artifacts/phase5/phase5aq-config-comparison-20260804-01/summary.json` | 3,705 keys; exactly three non-focus differences; zero focus differences | 已證實 |
| `P5AQ-004` | GhostLock focus matrix | `artifacts/phase5/phase5aq-config-comparison-20260804-01/config-diff.csv` | FUTEX, RT_MUTEXES, PREEMPT, KALLSYMS, ARM64/VA39, KASLR, SELinux and seccomp equal | 已證實 |
| `P5AQ-005` | Code-level boundary | `findings/phase-5ao-ps7331-boot-analysis.md`; `findings/phase-5n-exact-source-ghostlock-review.md` | same config does not prove same `rtmutex.c` code or compiled type layout | 高可信推論 |
| `P5AQ-006` | Safety boundary | `findings/phase-5aq-ps7331-ps7330-config-comparison.md` | no live trigger, root stage, memory write or partition operation | 因風險拒絕測試 |
