# Phase 6ME evidence index

All evidence in this index is host-only unless explicitly marked as prior
read-only device correlation. No file below was executed as code and no
hardware-facing ioctl or state mutation was performed in Phase 6ME.

| Evidence ID | Source | File | SHA-256 | Observed result | Classification |
|---|---|---|---|---|---|
| 6ME-SRC-001 | Official PS7331 GPL source archive | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` | Exact source package used as provenance input | 已證實 |
| 6ME-SRC-002 | Build-selected source manifest | `kernel/source-manifest.json` | `ada254be9c56572282704924eea66e2852889ec73c0a65be4558f36f77d8250a` | Selects the PS7331 MT8183 4.4 tree and records device/build metadata | 已證實 |
| 6ME-SCAN-001 | Reproducible host-only scanner | `tools/scripts/audit_phase6me_driver_control_edges.py` | `4ddb27e4d3a6684794b8a21d324c10c30fe0e4d5b60e76cca4dd8fa158e24c7f` | Seven bounded driver scopes; 1,671 source files | 已證實 |
| 6ME-SCAN-002 | Scanner summary | `artifacts/phase6me-driver-control-edges-20260810-01/summary.json` | `129bd9e929cad163652e6140a0c84248bcf16ef951ad6c2760ec0bf3e2da9669` | 7,698 markers; zero direct framework/launcher files | 已證實 |
| 6ME-SCAN-003 | Per-file closure table | `output/tables/phase6me-driver-control-closure.csv` | `360168945378dc42c96868339a3ed2a92fa4dfb819e9a9043286a453906218cb` | Registration/fops, user-copy, local-gate and sink columns | 已證實 |
| 6ME-SCAN-004 | Per-line marker detail | `artifacts/phase6me-driver-control-edges-20260810-01/driver-control-markers.csv` | `077a7cff0d60ae2329986382ef91118819045c3540ec76d0d9eeffb2c67230e3` | Reviewable source locations for every marker | 已證實 |
| 6ME-CFG-001 | Preserved shipped-kernel configuration | `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config` | `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04` | CMDQ, M4U, SMI, ION and Amazon options are enabled in the recovered config | 已證實 |
| 6ME-WORK-001 | Bounded worker path inventory | `work/luna_worker_kernel_surface_followup_20260810.md` | `031d77a3bc0ee40c66ab59c9d042af498f2282e21781274e4b5ccb2aa19c52a2` | Confirms Amazon path is `drivers/staging/amazon`; no launcher/HOME source hit | 高可信推論 |
| 6ME-RUNTIME-001 | Prior exact-build GED query-only capture | `adb/phase6bq/PHASE6BQ-GED-RO-20260807-04/` | See directory `sha256sums.txt` | Query telemetry was reachable; no package/Binder/HOME change | 已證實（既有證據） |
| 6ME-RUNTIME-002 | Prior exact-build node/HOME read-only capture | `adb/phase6n/PHASE6N-KERNEL-RO-20260810-01/` | See directory `sha256sums.txt` | Enforcing SELinux and Fire priority-50 HOME remained unchanged | 已證實（既有證據） |

## Interpretation rule

The zero-hit result is a bounded static negative: it applies to the selected
source scopes and deliberately narrow direct-sink patterns. It is not a claim
that no kernel-to-userspace event, property, file, secure-world, or native
binary path can ever exist. Such a claim would require additional provenance
and safe runtime evidence.
