# Phase 6PD evidence index

All paths below are relative to the project root. Hashes are SHA-256.

| Evidence ID | Source | File | Test ID | Observed result | Confidence |
|---|---|---|---|---|---|
| `E6PD-001` | ADB package update attempt | `adb/phase6pd/PHASE6PD-ACCESSIBILITY-PENDINGINTENT-T01/mutation-attempt.txt` | `PHASE6PD-ACCESSIBILITY-PENDINGINTENT-T01` | Update rejected with `INSTALL_FAILED_UPDATE_INCOMPATIBLE`; exit code 1. | Confirmed |
| `E6PD-002` | Post-attempt package/HOME capture | `adb/phase6pd/PHASE6PD-ACCESSIBILITY-PENDINGINTENT-T01/after-failed-install.txt` | `PHASE6PD-ACCESSIBILITY-PENDINGINTENT-T01` | Existing research package remained; Accessibility service entry remained; HOME remained Fire Launcher at priority 50. | Confirmed |
| `E6PD-003` | Read-only pre-change capture | `adb/phase6pd/PHASE6PD-ACCESSIBILITY-PENDINGINTENT-T01/before-state/` | `PHASE6PD-ACCESSIBILITY-PENDINGINTENT-T01-BEFORE` | Baseline snapshot retained before the package update attempt. | Confirmed |
| `E6PD-004` | Pulled installed APK | `adb/phase6pd/PHASE6PD-ACCESSIBILITY-PENDINGINTENT-T01/before/redirect-current.apk` | `PHASE6PD-ACCESSIBILITY-PENDINGINTENT-T01` | Installed APK preserved for provenance; SHA-256 `8a2393edac8338f30bf856c8a7e0f3a8fe5a0e7a383a75db29a121129f421c57`. | Confirmed |
| `E6PD-005` | Test result and safety record | `adb/phase6pd/PHASE6PD-ACCESSIBILITY-PENDINGINTENT-T01/result.md` | `PHASE6PD-ACCESSIBILITY-PENDINGINTENT-T01` | Records that no rollback was required and no Fire/system state mutation was performed. | Confirmed |

## Evidence-file hashes

| File | SHA-256 |
|---|---|
| `mutation-attempt.txt` | `ef883a3e17422af0dfed9ef95402c9fef8c32c10286313a163d86ae5325269ac` |
| `after-failed-install.txt` | `fe0008571a461c8b2f1ff6f12745e1562ebe228b5897636d42c66b5f3d836c4f` |
| `result.md` | `1d055bfc07e19b05e5ebf6ec8218e518d1e4cfa1c05c27863af86aa2cc587794` |
| `before/redirect-current.apk` | `8a2393edac8338f30bf856c8a7e0f3a8fe5a0e7a383a75db29a121129f421c57` |

