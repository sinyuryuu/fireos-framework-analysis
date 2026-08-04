# Phase 5BE evidence index

| Evidence ID | Source | File | SHA-256 | Observation | Confidence |
|---|---|---|---|---|---|
| P5BE-INV-001 | Official PS7331 source URL; nested `platform.tar` path stream | `artifacts/phase5/ps7331-nested-build-patch-index-20260804-01/pipeline-status.tsv` | `68ed76506976936213a10c681bb28c7442625ccd52b8eae1c2ad24c89734d83c` | `curl=0`, `bzip2=0`, `outer_tar=0`, `nested_tar=0`, `filter=0` | 已證實，path-inventory scope |
| P5BE-INV-002 | Derived exact patch/diff/series filter | `artifacts/phase5/ps7331-nested-build-patch-index-20260804-01/patch-diff-series-paths.txt` | `0998103078a2b9897e8471b923e9e4e508e3a84e6eae52de1fac26e816447b2d` | Only four Mali hrtimer diff paths; no rtmutex/futex/GhostLock patch path | 已證實，path-name scope |
| P5BE-INV-003 | Inventory manifest | `artifacts/phase5/ps7331-nested-build-patch-index-20260804-01/sha256sums.txt` | `95bef8b841df2bff569b4de5776a674e995bd541f4f25bef21b4d0de99c6fa10` | Raw inventory outputs have recorded SHA-256 manifest | 已證實 |
| P5BE-BUILD-001 | Official source build scripts | `artifacts/phase5/exact-kernel-source-review-7331-build-scripts-20260804-01/extracted/build_kernel.sh` | `3b7804c62d8533e200c54f076de4e0382bb21c5e924bbc8ac34773ce98653e33` | Visible build flow extracts, defconfigs, makes, copies and validates; no visible patch application | 已證實，script scope |
| P5BE-BUILD-002 | Official source build config | `artifacts/phase5/exact-kernel-source-review-7331-build-scripts-20260804-01/extracted/build_kernel_config.sh` | `fbf0f922fad86ac34d94a1c9c1587cb618516191b4e101b990d757e356b97cfa` | Selects `kernel/mediatek/mt8183/4.4`, `trona_defconfig`, `arm64` | 已證實 |
| P5BE-SOURCE-001 | Build-selected PS7331 source | `artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | Source retains current-task cleanup and proxy rollback call | 已證實，source scope |
| P5BE-SOURCE-002 | Deterministic source semantics result | `artifacts/phase5/ghostlock-source-semantics-20260804-01/mt8183.json` | `3a02f57d3aeb548948666d7feda4e9121cdc3dff67998f637db6257e67225ba2` | `PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN`; no `waiter->task` reference | 已證實，source scope |
| P5BE-BINARY-001 | PS7331 reconstructed Image review | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/summary.json` | `eede2b264a6a3a9934cc09b374ae9162e4196d2bdf68a07d6cd5fe2156148f2b2` | Inspected signed Image pattern reads current-task source and proxy path calls `remove_waiter` | 已證實，inspected-function scope |
| P5BE-OTA-001 | Official PS7331 OTA metadata | `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/summary.json` | `54c59cfc445e1b7ff7d6be7dc21b02668260e24b66dbcd53c3c2cf256928395a` | Full `trona` OTA; archive SHA `9f50d2f3…e3cd5`; target patch 2024-08-01 | 已證實，OTA metadata scope |
| P5BE-OTA-002 | Official updater script | `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/updater-script.txt` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` | Update scope includes system/vendor/boot and boot-chain/vendor firmware partitions | 已證實 |
| P5BE-DEVICE-001 | Read-only device postcheck | `adb/phase5/PHASE5BD-DEVICE-POSTCHECK-20260804-01/` | Per-file hashes in artifact manifest | Device remains PS7330, ADB `device`, Fire Launcher priority 50/resumed | 已證實，snapshot scope |

## Safety boundary

No OTA, boot image, root exploit, futex trigger, kernel memory operation, unknown
ioctl, bootloader command, or partition write was performed.
