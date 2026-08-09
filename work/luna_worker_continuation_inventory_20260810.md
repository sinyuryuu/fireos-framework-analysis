# Continuation inventory — PS7331/GPL/OTA/Amazon services

日期：2026-08-10
Worktree HEAD：`09a0cb7a6214dd2d5e14a66d93935c08f49ea1b6`

## Scope and safety

本輪只做 host-only 檔案搜尋、雜湊核對、既有結果整理與 verifier dry-run。未執行
ADB、`service call`、Binder transaction、`ioctl`、reboot、Root/exploit、
OTA/recovery/flash；未停用、hide、suspend、force-stop 或清除 Fire Launcher；
未重做 Phase 6MV 的 ADB capture。只新增本報告。

分類：**Confirmed** = 檔案/既有結果/離線 verifier 直接支持；**Strong** = 多份
靜態或保存結果一致但不是 runtime proof；**Pending** = 尚未閉合；**Rejected** =
在本安全範圍內不應執行或已由保存結果排除。

## 1. Canonical PS7331 inputs and hash verification

| Input | SHA-256 | Result / classification |
|---|---|---|
| `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` | 官方 source outer archive，Phase 6MI EOF summary 一致；**Confirmed** |
| `firmware/extracted/PS7331-SOURCE-20250617/fireos.tar` | `bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369` | GPL nested archive，Phase 6AN scope 一致；**Confirmed** |
| `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` | GPL nested archive，Phase 6AN scope 一致；**Confirmed** |
| `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | 官方安裝包/JAR-format OTA container；**Confirmed** |
| `firmware/extracted/PS7331/boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` | Android boot image；**Confirmed** |
| `firmware/extracted/PS7331/system.img` | `da8a935484de24251e890fbf4e7dd9155567ebe158fc255d43684ea14c62b1e5` | system ext2/extents image；**Confirmed** |
| `firmware/extracted/PS7331/vendor.img` | `d1db5a5349d046361710bd6966adb7ef88dc4ddc550295e8c1926cb279f213eb` | vendor ext2/extents image；**Confirmed** |
| `firmware/extracted/PS7331/META-INF/com/google/android/update-binary` | `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b` | updater input only; not executed；**Confirmed / Rejected execution** |
| `firmware/extracted/PS7331/META-INF/com/google/android/updater-script` | `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` | fixed OTA command contract；**Confirmed / Rejected execution** |

Selected artifact hash checks also remain stable: `framework/fosservices.jar`
`364603c0228058973ed976ff1bef51c3cab2fa8fc163ec63c727157bb92dec96`, selected
Fire Launcher APK `ee8201f5499b9d01d2f6fe1685a3e756d7429990c68e6b490b2f38466d09b8d3`,
and `framework-res.apk` `7a405abe0f721719cb5d8a280ac551f86880a70227d923e04dd922109ce8a35e`.

## 2. Commands executed and results

All commands below were offline/read-only or explicit dry-run. Dry-run output paths
were `/tmp/...-continuation-no-write`; no repository output directory was used.

| Command | Result | Classification |
|---|---|---|
| `git rev-parse HEAD` | `09a0cb7a6214dd2d5e14a66d93935c08f49ea1b6` | **Confirmed** |
| `python3 -B tools/scripts/audit_phase6an_gpl_scope.py --dry-run` | `HOST_ONLY=TRUE`, `DEVICE_CONTACTED=FALSE`, `ARCHIVE_EXTRACTED=FALSE`; points to existing `fireos.tar`/`platform.tar` | **Confirmed** |
| `python3 -B tools/scripts/audit_phase6mi_source_tar_eof.py --input firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2 --output /tmp/... --dry-run` | `would_extract=false`, `would_execute=false`, `would_mutate_device=false`; size `2563328975` | **Confirmed** |
| `python3 -B tools/scripts/audit_phase6i_ota_postinstall_surface.py --ota ...bin --metadata-root ... --extracted-root ... --output /tmp/... --dry-run` | `dry_run=true`, `host_only=true`, `device_contacted=false` | **Confirmed** |
| `python3 -B tools/scripts/audit_phase6ah_update_binary_validation.py ... --dry-run` | `DRY_RUN: no output written`; only preserved binary/script/functions/edges/disassembly listed | **Confirmed** |
| `python3 -B tools/scripts/audit_phase6md_native_updater_paths.py ... --dry-run` | `host_only=true`, `updater_executed=false`, `partition_written=false` | **Confirmed** |
| `python3 -B tools/scripts/audit_phase6mk_updater_dispatch_closure.py ... --dry-run` | `host_only=true`, `updater_executed=false`, `partition_written=false` | **Confirmed** |
| `python3 -B tools/scripts/audit_phase6mm_updater_blockimage_closure.py ... --dry-run` | `host_only=true`, `updater_executed=false`, `partition_written=false`; focus lists registration/cache/readlink/write functions | **Confirmed** |
| `sha256sum -c artifacts/phase6an/gpl-scope-20260805-01/sha256sums.txt` | all listed files `OK` | **Confirmed** |
| `sha256sum -c artifacts/phase6i/phase6i-ota-postinstall-20260804-01/sha256sums.txt` | all listed files `OK` | **Confirmed** |
| `sha256sum -c artifacts/phase6mi-source-tar-eof-20260810-03/sha256sums.txt` | all listed files `OK` | **Confirmed** |

`scripts/verify_ps7331_source.sh` was inspected but not run: it writes a new
artifact directory and has no dry-run flag. Running it would exceed the requested
“no existing-file mutation” boundary. No test suite was invoked because repository
test runners may create caches or artifacts; the verifier dry-runs and manifest
checks above were the non-mutating available checks.

## 3. Existing GPL/source findings

| Finding | Evidence path / SHA-256 | Current result |
|---|---|---|
| Phase 6AN GPL scope | `findings/phase-6an-gpl-scope.md`, `b310fb2eb5e6024ec3426755db53782d1d2019ed61987f1b464969496620e342`; `output/tables/phase6an-gpl-scope.csv`, `16fc58fcfb0390896cadaabbb6a47769fd584c9bc0c8aa7335d24f3bdb5ca6e0` | `fireos.tar` 53,549 members; `platform.tar` 138,574; no complete `system/core/init`, `frameworks/base`, Amazon namespace or deny-list source member path；**Confirmed** |
| Phase 6C.5 source scope | `findings/phase-6c5-gpl-source-scope.md`, SHA-256 `54cf005f30ebf85ac4e8a592097f527cb2ef8f0d1d4f36fabbc049e79ae32786` | kernel/Amazon-device source provenance only；完整 Amazon `/init`/framework source remains absent；**Strong** |
| Phase 6MI outer EOF | `findings/phase-6mi-source-tar-eof.md`, SHA-256 `0b3d01e8264010320a2b504bceb249f7459bbe96072426e91fe1a42dc56f596f`; summary SHA-256 `409ed81ede46db87a0ef8a05cc33b99df2b66e068d1edc1ac481a42e0606169b` | 35 members, EOF true, 0 post-install/update hits, 2 launcher-name hits only；**Confirmed negative boundary** |
| Phase 5BT boot/source semantic audit | `findings/phase-5bt-ps7331-full-source-audit.md`, SHA-256 `3dbf2cb0601fee687350a6ddff1f42e732c44f225171a1227242d387d872ce00` | source/Image GhostLock comparison preserved；not a launcher or OTA execution proof；**Strong** |

## 4. Existing Phase 6MT / 6MU / 6MV and earlier findings

### Amazon Framework/System Services

* **Phase 6MT:** `findings/phase-6mt-amazon-ipc-candidate-closure.md`, SHA-256
  `f2e885601009b71692b59f1ac8a3a21a9e41e3663749a0c8997126c984d20c21`; evidence
  index SHA-256 `3c38093998ee532476025338a66e392fc4aeb63797f58bcd12b8a0c783094a91`.
  Five Amazon proxies map to 37 remote methods with service publication and bounded
  permission/identity/sink data. No bounded direct HOME/preferred/Fire Launcher writer;
  caller reachability for unmarked wrappers remains unresolved. **Confirmed static /
  Strong bounded negative.**
* **Phase 6MU:** `findings/phase-6mu-amazon-application-flags-closure.md`, SHA-256
  `e101fe8549ba1aa39b0bc6384d5a1613701f81924002020e1fd5eec4fb0280c6`; evidence index
  SHA-256 `37d46c862dfa958ff86da71308849a526e8110bdfdd081b5c04f9f7a12e58fcb`.
  Four mutators persist per-user flags/metadata to `/data/system/amazon_package_flags.xml`;
  first visible consumers are PackageRecency, GameMode bit 2, and AppCompat bit 1.
  No direct HOME/preferred/enabled-state writer. **Confirmed static / Strong bounded.**
* Existing table `output/tables/phase6mu-amazon-application-flags-20260810-01.csv`
  SHA-256 `0b86f79ce8ae336ed5de9f50ecf80d2bce2f01e3c11c121299aea2a46e111ebb` is
  preserved and was not regenerated.
* Earlier Phase 6MN/6KV/6BK/6R artifacts remain the user-scope, standard HOME caller,
  IPC/OTA-boundary and OTA/OOBE evidence. Their conclusions are not expanded here;
  6MT/6MU already close the requested private-interface and flags slices.

### Phase 6MV runtime and source/OTA evidence

* `findings/phase-6mv-runtime-readonly-report.md`, SHA-256
  `3ea8ff33c75fde654a3208a4c20015a44efe73309720759d259b52b0021eafc8`, and
  `findings/phase-6mv-evidence-index.md`, SHA-256
  `792f43ca6798b41ef6d9695a7924df6319ac0d7e574408c9ddf143b7e44018ba`, record an
  existing read-only capture: User 0 HOME resolves to Fire Launcher priority 50;
  three HOME candidates were listed; Fire has separate User 0/User 10 records; selected
  private service checks were not found for shell. **Existing evidence only; not rerun.**
* `output/tables/phase6mv-runtime-summary-20260810-02.csv`, SHA-256
  `5b974ced88721359d6905c5711481c5bc1fb8bcbf6a2fff0eb7a301e42485564`, is the
  preserved summary table. No new ADB capture was made.
* Prior OTA/post-install findings remain static: Phase 6I says `partition_written=false`
  and `updater_executed=false`; Phase 6AH/6MD/6MK/6MM establish static updater
  registration, extraction, block-image, partition-I/O and partial canonicalization
  edges. These prove capability in the binary, not execution or a launcher route.

## 5. Safe unresolved next analysis

The smallest non-overlapping safe task is a **host-only caller/handle provenance sweep
for `IAmazonPackageManager` only**:

1. Search preserved `fosservices`, `services`, `boot-fosframework` disassembly and
   selected framework/APK metadata for `ServiceManager.getService`/`getSystemService`
   and the literal `amazonpackagemanager`.
2. Correlate only static callers, declared permissions, and first local method use;
   stop at a native/absent/generated boundary.
3. Do not invoke the service, guess a transaction, read/write device state, or repeat
   the 6MT interface matrix/6MU flags writer trace.

This targets the one material gap left by 6MT/6MU/6MV: static service-handle and caller
provenance remains unresolved even though proxy methods, flags persistence, and the
runtime HOME outcome are already documented. A clean negative result would strengthen
the boundary that Amazon package metadata is not a shell-reachable HOME control path.

Other open questions are larger or already bounded: exact native updater indirect
dataflow remains **Pending** under 6MK/6MM, and GPL `/init` completeness is **Rejected**
as a source-package assumption, not a missing test to run.

## Final status

* **Confirmed:** canonical hashes, manifest checks, GPL scope, OTA/image presence,
  Phase 6MT/6MU static closures, and the existence of prior Phase 6MV read-only results.
* **Strong:** Fire Launcher User-0 HOME result and protected-package/OTA boundaries as
  preserved evidence; no direct Amazon flags→HOME writer in the bounded corpus.
* **Pending:** static AmazonPackageManager caller/handle provenance; updater indirect
  canonicalization dataflow; external/native/generated consumers.
* **Rejected:** repeating ADB capture, private Binder replay, OTA/recovery execution,
  package/launcher mutation, Root/exploit, or treating GPL source as complete Amazon
  framework/init provenance.

Only this report was added; existing files were not modified, committed, or pushed.
