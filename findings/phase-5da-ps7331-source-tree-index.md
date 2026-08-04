# Phase 5DA — PS7331 source tree extraction and index

Status: **Completed (host-only, read-only)**

This phase fully extracts the official Fire HD 10 7.3.3.1 source archive into
new local directories and builds a reproducible source index. It does not
build, execute, modify, or install any source; it does not contact the tablet.

## Input and preservation

| Item | Value |
|---|---|
| Outer archive | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` |
| Outer archive SHA-256 | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` |
| Outer archive size | 2,563,328,975 bytes |
| Extraction root | `firmware/extracted/PS7331-SOURCE-20250617/` |
| Primary nested archive | `platform.tar`, SHA-256 `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` |
| FireOS nested archive | `fireos.tar`, SHA-256 `bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369` |

The original outer archive and both nested archives remain in place. The
primary archives were extracted to separate `platform/` and `fireos/`
directories. Third-party dependency archives such as Chromium remain as
archives; they are not needed for the PS7331 kernel index and were not
expanded without a separate scope decision.

## Extracted structure

The outer archive contains 23 files and 13 directories. The two primary source
trees contain:

- `platform/`: 124,234 files, approximately 1.7 GiB.
- `fireos/`: 49,301 files, approximately 729 MiB.
- Combined source-tree index: 173,535 files; 1,094 focus files were hashed.

The reproducible local index is:

`artifacts/phase5/phase5da-ps7331-source-tree-index-20260804-01/`

It contains `file-list.tsv`, `focus-paths.tsv`, `metadata.json`, and
`sha256sums.txt`. Its metadata records that the scan was offline-only, source
was not executed, and the device was not touched.

## Device-target evidence

**Confirmed:** the Amazon build recipe selects the device-specific kernel
without requiring a guessed board name:

- `build_kernel_config.sh:9` sets `KERNEL_SUBPATH="kernel/mediatek/mt8183/4.4"`.
- `build_kernel_config.sh:10` sets `DEFCONFIG_NAME="trona_defconfig"`.
- `build_kernel_config.sh:11` sets `TARGET_ARCH="arm64"`.
- `build_kernel_config.sh:18` names the expected `Image`, `Image.gz`, and
  `Image.gz-dtb` outputs.
- `build_kernel.sh:139` invokes the selected defconfig and
  `build_kernel.sh:130-131` builds the selected kernel subpath.

The selected source has the corresponding device material:

- `platform/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig`
  (SHA-256 `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac`).
- `trona_defconfig:15` enables `CONFIG_MACH_MT8183`.
- `trona_defconfig:22` enables `CONFIG_RANDOMIZE_BASE`.
- `trona_defconfig:26` selects the DVT, EVT, HVT, and prototype trona DTBs.
- `trona_defconfig:98` sets `CONFIG_ARCH_MTK_PROJECT="trona"`.
- `arch/arm64/boot/dts/mediatek/trona_{dvt,evt,hvt,proto}.dts` all include
  `mt8183.dts` and `trona/cust.dtsi`.

This is strong source provenance for the trona/MT8183 target. It is not by
itself a cryptographic proof that a newly built image equals the signed image
on the tablet; the signed-device and runtime evidence remains the authority
for that distinction.

## GhostLock-relevant source locations

The exact MT8183 source contains the already investigated futex/rtmutex path:

- `kernel/locking/rtmutex.c`, SHA-256
  `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`.
- `rtmutex.c:952-977`: `task_blocks_on_rt_mutex()` receives the target task
  and assigns `waiter->task` after the self-deadlock early return.
- `rtmutex.c:1079-1090`: `remove_waiter()` uses `current->pi_blocked_on`.
- `rtmutex.c:1656-1684`: `rt_mutex_start_proxy_lock()` calls the proxy path
  and uses the broad nonzero cleanup condition.
- `kernel/futex.c:1756`, `1963-1965`, and `3268-3269`: the requeue-PI path
  reaches `rt_mutex_start_proxy_lock()` through `FUTEX_CMP_REQUEUE_PI`.

The source also contains the futex selftests under the MT8183 kernel tree,
including `tools/testing/selftests/futex/functional/futex_requeue_pi.c` and
related requeue-PI tests. Their presence is source provenance only. No
selftest was copied to the tablet, built, or executed.

The standalone `trona_defconfig` is a device fragment and does not list every
effective Kconfig symbol. Therefore the absence of a symbol from that file is
not evidence that the running kernel lacks it. Effective device configuration
claims continue to use the prior signed-image/runtime configuration evidence.

## What this archive does not provide

**Confirmed:** `apps/com.amazon.firelauncher/` contains only
`javax.annotation-api-1.2.tar.gz`; it does not contain Fire Launcher Java or
smali source. This source package cannot replace the pulled APK or decompiled
artifact for Launcher implementation analysis.

**Confirmed:** the extracted `fireos/` tree contains AOSP/external and partial
FireOS material, but no `frameworks/` tree and no matching
`PackageManagerService`, `ActivityStarter`, `PhoneWindowManager`, Settings, or
SystemUI source paths. The PackageManager/Home conclusions therefore still
require the existing framework artifacts and AOSP comparison; this archive
does not prove that those components were unmodified.

## Safety and next step

No kernel build, compiler execution, selftest, futex call, exploit, native
payload, root operation, ADB mutation, bootloader operation, or partition write
was performed. The next safe step is focused offline comparison of the exact
MT8183 source and signed-image-derived evidence, not adapting or running a
GhostLock trigger. Runtime identity mismatch, cleanup residue, memory effect,
and privilege transition remain **unobserved**.

## Reproduction

```sh
python3 tools/scripts/index_phase5da_source_tree.py \
  --root firmware/extracted/PS7331-SOURCE-20250617 \
  --output artifacts/phase5/phase5da-ps7331-source-tree-index-20260804-01 \
  --archive-sha256 02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea
```

Evidence: `P5DA-E01` through `P5DA-E09` in
`findings/phase-5da-evidence-index.md`.
