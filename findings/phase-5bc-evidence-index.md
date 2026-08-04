# Phase 5BC evidence index

| Evidence ID | File | SHA-256 | Observation | Confidence |
|---|---|---|---|---|
| P5BC-001 | `artifacts/phase5/ghostlock-source-semantics-20260804-01/mt8183.json` | `3a02f57d3aeb548948666d7feda4e9121cdc3dff67998f637db6257e67225ba2` | Build-selected PS7331 source is `PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN`; proxy rollback call present | 已證實（source scope） |
| P5BC-002 | `artifacts/phase5/ghostlock-source-semantics-20260804-01/legacy.json` | `16edbad42503398ac7f683817ac0c5370592ce550f3b5aa53aa93171961d0f85` | Legacy PS7331 source has the same old pattern | 已證實（source scope） |
| P5BC-003 | `tools/scripts/check_phase5_ghostlock_source_semantics.py` | `9dd218d7d3f86288ea045edf72f4efecb7096d8b3daf7a3fdbe2f31237601503` | Deterministic host-only semantic checker | 已證實 |
| P5BC-004 | `artifacts/phase5/android-implementation-public-review-20260804-01/derived/android-implementation-matrix.csv` | `d709d3f0d6b5d5aedc5598d4e1fe353185e3c7536336febce3264563e99f5db3` | Public route matrix has no exact trona/KFTRWI validated target; pinned mtk-su route already failed | 高可信推論 |
| P5BC-005 | `adb/phase5/PHASE5BB-DEVICE-POSTCHECK-20260804-01/` | see per-file manifest | Device remains PS7330 and HOME remains Fire Launcher after host-only work | 已證實 |
| P5BC-006 | `artifacts/phase5/exact-kernel-source-review-7331-trona-defconfig-index-20260804-01/relevant-paths.txt` | `24c0a3513c7344335b542898f46026b96dd9274fae843334467c8ef10496cc7c` | Nested platform index identifies the exact build-selected `trona_defconfig` path | 已證實 |
| P5BC-007 | `artifacts/phase5/exact-kernel-source-review-7331-trona-defconfig-member-20260804-01/metadata.tsv` | `47edfdb7eb149c3a4004a1b080a9089bc42f54ea9e61708a18194033b4d95fc6` | Official PS7331 source member exists; member SHA-256 is `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac`; it is build input, not a final signed Image | 已證實（source scope） |
| P5BC-008 | `artifacts/phase5/phase5bc-defconfig-focus-20260804-01/summary.json` | `fb6a455fc42d736b277072828739d8a78fae7f80a6e4d9146429f6fe70a82d31` | PS7330 live and PS7331 boot-embedded focus configs are equal; partial defconfig omissions are not treated as `n` | 已證實（config provenance） |
| P5BC-009 | `tools/scripts/compare_phase5_defconfig_focus.py` | `27c54dbf43ca8a9ade416478b83e9bb00355b2719b4bc3121bc13762db4dc823` | Deterministic host-only comparison of runtime and build-input config evidence | 已證實 |
| P5BC-010 | `adb/phase5/PHASE5BC-DEVICE-POSTCHECK-20260804-01/` | `6441d01ce186866e761f986653580b0e3d82e591cf6ba10f6703fa2f5fbde7f0` | Read-only postcheck: ADB `device`, PS7330 fingerprint, security patch `2024-02-01`, Fire Launcher at `/system/priv-app`, HOME resolver priority 50, and Fire Launcher resumed | 已證實（device snapshot） |

All entries are host-only or read-only device evidence. No exploit, kernel
trigger, ioctl, bootloader, image write, OTA upgrade, or partition operation was
performed.
