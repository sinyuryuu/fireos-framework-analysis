# Phase 4 evidence index

Phase 4 evidence is intentionally split into static, offline-model, and live
reversible experiment records.

| Evidence ID | Source | File | Observation | Confidence |
|---|---|---|---|---|
| P4A-MODEL-001 | offline AOSP model | `tools/scripts/model_aosp9_home_resolution.py`, `tests/test_aosp9_home_resolution.py` | priority 50 returns Fire before ordinary preferred; tie control uses preferred | 已證實 |
| P4A-METHOD-001–008 | AOSP/Fire method diff | `output/tables/phase-4a-method-diff.csv` | core chooser equivalent in visible branches; two Amazon callback boundaries | 已證實 / 待驗證 |
| P4A-DEVICE-001 | Phase 3C device evidence | `adb/phase3c/PHASE3C-PREFERRED-P0-03/` | preferred record persistence does not change Fire result | 已證實 |
| P4B-RANK-001 | ranking inventory | `output/tables/phase-4b-ranking-factors.csv` | only privileged/system path can retain positive priority | 高可信推論 |
| P4B-CALLBACK-001 | Amazon callback static scan | `findings/phase-4b-amazon-callback-control-surface.md` | callback can short-circuit or filter, but current return is unknown | 待驗證 |
| P4B-WA-001 | safety review | `findings/phase-4b-assisted-workarounds.md` | Accessibility redirect is approximation, not HOME replacement | 高可信推論 |
| P4B-ALIAS-001 | one reversible APK experiment | `adb/phase4/PHASE4-ALIAS-T04/` | aliases/filter composition left Fire resolver and Home key unchanged | 已證實 |
| P4B-ALIAS-ROLLBACK-001 | rollback snapshot | `adb/phase4/PHASE4-ALIAS-T04/after_rollback/`, `rollback-diff.md` | test package absent, resolver Fire, ADB device | 已證實 |
| P4B-ACCESS-001 | manual-consent Accessibility run | `adb/phase4/PHASE4-ACCESSIBILITY-T03/` | 30 explicit redirect attempts; 0/30 resumed/focused alias handoffs; Fire remained resumed | 已證實 |
| P4B-ACCESS-ROLLBACK-001 | manual disable and rollback | `adb/phase4/PHASE4-ACCESSIBILITY-T03/rollback-result-verified.md`, `after_rollback/` | service setting empty, test packages absent, resolver Fire, ADB device | 已證實 |
| P4B-RISK-001 | risk gate | `findings/phase-4-risk-register.md` | Device Owner, Fire state mutation, crash fallback rejected | 因風險拒絕測試 |

Live Phase 4B experiment IDs are added here by the controlled experiment
runner after each raw output directory is finalized. No generated summary
replaces the raw command output or SHA-256 manifest.
