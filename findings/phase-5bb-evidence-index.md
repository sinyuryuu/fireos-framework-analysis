# Phase 5BB evidence index

All evidence in this index is host-only or read-only device evidence. No Phase
5BB entry changed package state, settings, boot state, partitions, or HOME.

| Evidence ID | Source / file | SHA-256 | Test / time | Observation | Interpretation | Confidence |
|---|---|---|---|---|---|---|
| P5BB-001 | `adb/phase5/PHASE5BA-DEVICE-POSTCHECK-20260804-01/fingerprint.stdout.txt` | `c4ee28478556c78468716ded87b8d402aa83eb82a159ca121979323df4abffea` | `PHASE5BA-DEVICE-POSTCHECK-20260804-01`; `2026-08-04T01:26:41Z` | Device is `PS7330.4104N/0030099376128` | Current build remained PS7330 | 已證實 |
| P5BB-002 | `adb/phase5/PHASE5BA-DEVICE-POSTCHECK-20260804-01/resolver.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | same | HOME resolves to `com.amazon.firelauncher/.Launcher`, priority 50 | No HOME mutation occurred | 已證實 |
| P5BB-003 | `artifacts/phase5/ps7331-boot-image-inspection-20260804-01/boot-image-metadata.json` | `32831b97cd2af84897889a69b480c2c2af60dbb3598e444678c41cba3ec7305c` | host-only | PS7331 boot SHA, `trona`, header kernel offset/address, gzip ARM64 Image | Adjacent signed artifact provenance and image layout | 已證實 |
| P5BB-004 | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/summary.json` | `eede2b264a6a3a9934cc09b374ae9162e4196d2bdf68a07d6cd5fe2156148f2b2` | host-only | `remove_waiter` reads current-task source and clears current-task field; proxy path calls it | PS7331 inspected Image retains pre-fix semantic pattern | 已證實（inspected function） |
| P5BB-005 | `artifacts/phase5/phase5aq-config-comparison-20260804-01/summary.json` | `8b3412993baed3efb18f127da4538866ad247562cdb591375b1a02dfa4e29778` | host-only | 3,705 keys, only three unrelated differences; focus keys unchanged | Config does not show GhostLock remediation | 高可信推論 |
| P5BB-006 | `artifacts/phase5/exact-kernel-source-review-7331-build-scripts-20260804-01/extracted/build_kernel.sh` | `3b7804c62d8533e200c54f076de4e0382bb21c5e924bbc8ac34773ce98653e33` | host-only | Build path is `kernel/mediatek/mt8183/4.4` | Source archive has nested platform input layout | 已證實 |
| P5BB-007 | `artifacts/phase5/exact-kernel-source-review-7331-build-scripts-20260804-01/extracted/build_kernel_config.sh` | `fbf0f922fad86ac34d94a1c9c1587cb618516191b4e101b990d757e356b97cfa` | host-only | Config selects `trona_defconfig`, arm64, Image targets | Exact source member extraction target | 已證實 |
| P5BB-008 | `findings/phase-5ar-ps7331-compiled-rtmutex-review.md` | see report and artifact hashes | Phase 5AR | PS7331 compiled review explicitly excludes exploit execution | Static patch-status boundary | 已證實 |
| P5BB-009 | `findings/phase-5az-ghostlock-mtk-compatibility.md` | see linked evidence index | prior exact-target review | PS7330 source/config candidate; exact signed PS7330 binary still unavailable; mtk-su test failed at init step 3 | No new compatible root route established | 已證實（scope-bounded） |
| P5BB-010 | NVD, `https://nvd.nist.gov/vuln/detail/CVE-2026-43499` | external primary record | published vulnerability record | Describes `current` versus `waiter->task` and lists upstream fix | Semantic reference for patch comparison | 已證實（source attribution） |
| P5BB-011 | `artifacts/phase5/exact-kernel-source-review-7331-nested-platform-index-20260804-01/relevant-paths.txt` | `ea77dd33c5f4f97ca1ad03b19ef60e479f4e0391656f162c7a6fccef933acc41` | host-only; pipeline all zero | Nested `platform.tar` contains both `kernel/mediatek/mt8183/4.4` and legacy `kernel/mediatek/4.4` target paths | Exact source member paths are present | 已證實 |
| P5BB-012 | `adb/phase5/PHASE5BA-DEVICE-POSTCHECK-20260804-01/boot_pull.stderr.txt` | `fbb747a6c9ae46a39048871a905cc32f943d037b8410b02e5c5863fecd9ecfc6` | prior read-only boundary | Shell could not pull exact installed PS7330 boot block | PS7330 compiled binary not directly proven | 已證實 |
| P5BB-013 | `artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | host-only | Build-selected PS7331 source retains `current->pi_blocked_on` cleanup and proxy rollback call | Source-level pre-fix GhostLock semantic pattern | 已證實 |
| P5BB-014 | `artifacts/phase5/exact-kernel-source-review-7331-source-comparison-20260804-01/mt8183-rtmutex-vs-v4146.diff` | `a4151383bc8d2555569a54c821393a8719726250190db7944d18f4024b825cbd` | host-only | Diff against v4.4.146 old reference is limited to `rt_mutex_proxy_unlock()` signature change; no `waiter->task` fix | No source-level GhostLock remediation in build-selected tree | 高可信推論 |
| P5BB-015 | `artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/4.4/kernel/locking/rtmutex.c` | `c4ddac5fe820c7f07670bc332425be05b0df0400ae334a147b483f0ee9b07345` | host-only | Legacy PS7331 tree is byte-identical to pinned v4.4.146 old reference | Supporting but non-authoritative tree; build script points to mt8183 tree | 已證實 |
| P5BB-016 | `artifacts/phase5/exact-kernel-source-review-7331-source-comparison-20260804-01/legacy-vs-mt8183-futex.diff` | `eaa4c31c75c7958737e7838b7d49eed56e17aa75f78d24c03a357261860603b6` | host-only | mt8183 futex changes include key/refactoring and proxy-unlock call signature; no evidence of `remove_waiter` waiter-task fix | No observed GhostLock fix in compared futex source | Probable |
| P5BB-017 | `artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex_common.h` | `b3456f9e83a1919e41a88a6638ad1e26ed9966e800c6efc823940df1151919fc` | host-only | Proxy-unlock declaration changed, while waiter structure／proxy APIs remain | Source tree has unrelated vendor API delta and a consistency caveat | Probable |
| P5BB-018 | `tools/scripts/extract_phase5_nested_kernel_members.sh` | `daa6e84376a77ab6944163c9daee95ff44fe4b8304c9990f46bf6da9754ba5bc` | host-only reproduction script | Re-extracts the selected nested kernel members without device I/O | Reproducible source evidence workflow | 已證實 |

## Evidence rules

- “PS7331 is not demonstrated fixed” is supported by P5BB-004 and P5BB-005,
  not by release date alone.
- “PS7330 remains unconfirmed at signed-binary scope” is supported by P5BB-012;
  public source/config evidence is not silently promoted to binary evidence.
- P5BB-011 identifies the nested member paths; P5BB-013/P5BB-016 contain the
  selected source evidence and P5BB-014 contains the semantic diff boundary.
