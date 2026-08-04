# Phase 5BA evidence index

本輪以 host-only 方式分析 PS7331 OTA／boot image，並以既有 exact PS7330
evidence 作為對照。沒有升級、重開機、root、fastboot、partition 或 kernel
trigger。

| Evidence ID | Source | File | SHA-256 | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|---|
| P5BA-001 | exact device identity | `adb/phase5/PHASE5AU-OTA-RESIDUE-20260804-02/getprop_full.stdout.txt` | `cf9dd92b26eac1381e1e6a1936b19dc59900705690f136e1ff46b34ab4074f35` | Device is `PS7330.4104N`, `trona`, API 28 | PS7331 is not installed | 已證實 |
| P5BA-002 | PS7331 OTA metadata | `firmware/extracted/PS7331/ota.prop` | `f91b4c792339c605d81a2d6d5e819fee5d522a7514111daa1468717e07319ded` | `pre-device=trona`, `PS7331.4463N`, security patch 2024-08-01 | Official adjacent-version metadata is internally consistent | 已證實 |
| P5BA-003 | PS7331 boot image | `firmware/extracted/PS7331/boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` | Android boot image; kernel payload extracted offline | Valid host-only PS7331 reference | 已證實 |
| P5BA-004 | PS7331 decompressed Image | `artifacts/phase5/ps7331-boot-image-inspection-20260804-01/kernel.Image` | `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d` | ARM64 4.4.146+ kernel Image | Binary is tied to PS7331 artifact | 已證實 |
| P5BA-005 | compiled rtmutex review | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/summary.json` | `eede2b264a6a3a9934cc09b374ae9162e4196d2bdf68a07d6cd5fe2156148f2b2` | `remove_waiter` current-task clear pattern and proxy call observed | PS7331 inspected path is old GhostLock pattern | Strong evidence |
| P5BA-006 | PS7330／PS7331 config comparison | `artifacts/phase5/phase5aq-config-comparison-20260804-01/summary.json` | `8b3412993baed3efb18f127da4538866ad247562cdb591375b1a02dfa4e29778` | Only three of 3,705 config keys differ; focus keys equal | Config alone does not show remediation | 已證實 |
| P5BA-007 | exact PS7330 source | `artifacts/phase5/exact-kernel-source-review-20260804-02/metadata.tsv` | `83b28634628cb90b653c36ce4f5eb6d410622b9bfb905a52d1b023a1abbe4f6a` | exact 7.3.3.0 `rtmutex.c` normalized hash equals v4.4.146 old reference | Installed build source family has old semantics | Strong evidence |
| P5BA-008 | bounded PS7331 source recovery | `artifacts/phase5/exact-kernel-source-review-7331-members-20260804-02/member-extract/members/mt8183_defconfig.e1495a4e51db.txt` | `6c74fb54e5ffc9d9d0f10d3f46113b29eb4741dc0d31b6f68c9fe88d58b51fa0` | Recovered arm64 MT8183 defconfig hash equals preserved PS7330 source defconfig | Source/config family appears unchanged in this member | Strong evidence; bounded recovery |
| P5BA-009 | PS7331 source archive sample | `artifacts/phase5/exact-kernel-source-review-7331-tail-20260804-05/metadata.tsv` | `a64b106ed15fa4e733613102ecd2659f93355ef973dfb3afcd55602ca8af5c6b` | Official 7.3.3.1 source URL and bounded-range provenance recorded | Archive exists; not a full rtmutex source comparison | 已證實／待驗證 |
| P5BA-010 | exact PS7330 boot read boundary | `adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/boot_pull.stderr.txt` | `fbb747a6c9ae46a39048871a905cc32f943d037b8410b02e5c5863fecd9ecfc6` | Installed boot block is not shell-readable | PS7330 compiled binary remains unconfirmed | 已證實 |
| P5BA-011 | Phase 5BA device post-check | `adb/phase5/PHASE5BA-DEVICE-POSTCHECK-20260804-01/` (`resolver.stdout.txt` SHA `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6`) | see directory `sha256sums.txt` | ADB is `device`; fingerprint remains PS7330; HOME remains Fire Launcher priority 50; path is `/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk` | No device state change during host-only comparison | 已證實 |
| P5BA-012 | complete outer tar index | `artifacts/phase5/exact-kernel-source-review-7331-outer-index-20260804-01/relevant-paths.txt` | `f16acefd2eadfe3619474b8e366461ca8307f7976a354a220120d5790d240947` | Outer bundle contains `build_kernel.sh` and `build_kernel_config.sh`; direct `kernel/...` members were not listed | 7.3.3.1 source layout is build-script／nested-source based; exact `rtmutex.c` member still not extracted | 已證實／待驗證 |
| P5BA-013 | PS7331 build configuration | `artifacts/phase5/exact-kernel-source-review-7331-build-scripts-20260804-01/extracted/build_kernel_config.sh` | `fbf0f922fad86ac34d94a1c9c1587cb618516191b4e101b990d757e356b97cfa` | Build script selects `kernel/mediatek/mt8183/4.4`, `trona_defconfig`, ARM64 and Clang 6.0.2 recommendation | PS7331 source／boot build family is target-specific; script itself was not executed | 已證實 |

## Confidence rule

P5BA-005 is direct compiled evidence for PS7331 only. P5BA-007 is exact source
evidence for PS7330 only. Neither one by itself transfers the other version's
signed-binary conclusion.
