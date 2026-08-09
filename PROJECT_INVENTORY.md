# Project Inventory

Updated: 2026-08-10

This inventory describes the local Fire OS 7 / PS7331 analysis workspace. It
does not contain device credentials, unlock secrets, or private user data.

## Repository state

- Workspace: `2026-08-03-fire-os-7-framework-amazon-fire`
- Public branch: `main`
- Public HEAD at inventory time: `4c379ae7f1b7cb779bfa0c63e2b6faa781fdbad8`
- Remote: `git@github.com:sinyuryuu/fireos-framework-analysis.git`
- Original files are kept under `firmware/original/`; extracted and generated
  material is stored elsewhere.
- The worktree contains additional local, not-yet-published evidence. Do not
  infer that every local file is present on GitHub.

## Top-level layout

| Directory | Purpose |
|---|---|
| `adb/` | Raw device captures, mutation snapshots, logs, and rollback evidence. |
| `firmware/original/` | Immutable downloaded OTA/source archives. |
| `firmware/extracted/` | Read-only extracted images and expanded source archives. |
| `firmware/partitions/` | Partition-oriented working area; no writable system mount is used. |
| `firmware/manifests/` | Pull manifests, command manifests, and SHA-256 records. |
| `artifacts/` | Pulled APK/JAR/ELF/XML artifacts and static-audit outputs. |
| `decompiled/` | JADX, apktool, baksmali, VDEX, and normalized outputs. |
| `aosp/` | Android 9 AOSP r1/r61 and init-source baselines. |
| `findings/` | Phase reports, evidence indexes, and conclusions. |
| `output/` | Tables, call graphs, timelines, and generated summaries. |
| `tools/` | Reproducible scripts, test APK sources, and build helpers. |
| `kernel/` | Project notes, source manifest, lab-only patches, and layout assertions. |
| `poc/`, `preload/`, `reference_ghostlock/` | Research notes and bounded reference material; no live exploit is stored or run. |

## Firmware and source of record

### Original archives

- `firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2`
- `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2`
- `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`

### PS7331 extracted firmware

- `firmware/extracted/PS7331/boot.img`
- `firmware/extracted/PS7331/system.img`
- `firmware/extracted/PS7331/vendor.img`
- `firmware/extracted/PS7331/ota.prop`
- `firmware/extracted/PS7331/target_mt8183.h`
- `firmware/extracted/PS7331/META-INF/com/google/android/update-binary`
- `firmware/extracted/PS7331/META-INF/com/google/android/updater-script`

### PS7331 GPL/source package

- `firmware/extracted/PS7331-SOURCE-20250617/README.txt`
- `firmware/extracted/PS7331-SOURCE-20250617/build_kernel.sh`
- `firmware/extracted/PS7331-SOURCE-20250617/build_kernel_config.sh`
- `firmware/extracted/PS7331-SOURCE-20250617/fireos.tar`
- `firmware/extracted/PS7331-SOURCE-20250617/platform.tar`
- Expanded Android/AOSP-like sources:
  `firmware/extracted/PS7331-SOURCE-20250617/fireos/`
- Expanded Amazon/MediaTek platform and kernel sources:
  `firmware/extracted/PS7331-SOURCE-20250617/platform/`
  - `platform/kernel/mediatek/`
  - `platform/device/amazon/`
  - `platform/system/core/`
  - `platform/vendor/mediatek/`
- Fire Launcher source subtree:
  `firmware/extracted/PS7331-SOURCE-20250617/apps/com.amazon.firelauncher/`

The small `kernel/` directory is not the full GPL tree; the expanded PS7331
kernel tree is under the source-package path above.

## Framework and application artifacts

- `artifacts/framework/framework.jar`
- `artifacts/framework/framework-res.apk`
- `artifacts/services/services.jar`
- `artifacts/systemui/`
- `artifacts/launcher/`
- `artifacts/settings/`
- `artifacts/amazon-services/`
- `firmware/manifests/ARTIFACT-20260803-01/`
- `firmware/manifests/ARTIFACT-20260803-02/`
- `firmware/manifests/ARTIFACT-20260803-03/`
- `firmware/manifests/ARTIFACT-20260803-05/`
- `firmware/manifests/ARTIFACT-20260803-06/`

The principal PS7331 VDEX/DEX disassembly is:

- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`
- `decompiled/baksmali/vdexExtractor/services/disassembly.log`
- `decompiled/baksmali/vdexExtractor/boot-framework-dis/`

JADX and resource-normalized trees are under:

- `decompiled/jadx/ota-PS7331/`
- `decompiled/jadx/firelauncher/`
- `decompiled/jadx/settings/`
- `decompiled/jadx/systemui/`
- `decompiled/apktool/`
- `decompiled/normalized/`

## AOSP baselines

- `aosp/android-9/android-9.0.0_r1/platform/`
- `aosp/android-9/android-9.0.0_r61/platform/`
- `aosp/android-9/init-source-20260804-01/`
- `aosp/references/aosp-baseline.md`

Important AOSP comparison paths include PackageManagerService,
PreferredActivity, PersistentPreferredIntentResolver, ProtectedPackages,
ActivityStackSupervisor, ActivityStarter, PhoneWindowManager, and the Android
9 Settings default-home implementation.

## Latest analysis records

### Phase 6N — kernel/vendor surface

- `findings/phase-6n-report.md`
- `findings/phase-6n-kernel-surface-index.md`
- `findings/phase-6n-ipc-provenance.md`
- `output/tables/phase6n-kernel-user-surfaces.csv`
- `adb/phase6n/`

### Phase 6O — per-user KFT and OTA boundary

- `findings/phase-6o-control-boundary.md`
- `findings/phase-6o-launcher-control-and-ota-boundary.md`
- `output/tables/phase6o-launcher-control-surfaces.csv`
- `adb/phase6o/`
- `artifacts/phase6o/`

### Phase 6P — native updater closure

- `findings/phase-6p-native-updater-closure.md`
- `findings/phase-6p-native-updater-evidence-index.md`
- `findings/phase-6p-callback-and-ota-audit.md`
- `adb/phase6p/`
- `artifacts/phase6p/`

### Phase 6IP — AmazonPackageManager ProxyReceiver

- `findings/phase-6ip-amazon-proxy-receiver-gate.md`
- `output/call-graphs/phase6ip-amazon-proxy-gate-class.mmd`
- `output/call-graphs/phase6ip-amazon-proxy-gate-flow.mmd`
- `output/call-graphs/phase6ip-amazon-proxy-gate-sequence.mmd`
- `output/tables/phase6ip-amazon-proxy-gate.csv`
- `adb/phase6ip/`

This phase has already tested the ordinary-app ProxyReceiver boundary and did
not demonstrate a launcher writer or a usable confused-deputy path.

### Phase 6BK — child-profile/KFT and service closure

- `findings/phase-6bk-report.md`
- `findings/phase-6bk-evidence-index.md`
- `findings/phase-6bk-kft-runtime.md`
- `findings/phase-6bk-followup-20260810.md`
- `output/call-graphs/phase6bk-ipc-ota-kft.mmd`
- `adb/phase6bk/`
- `artifacts/phase6bk/`

At inventory time, these Phase 6BK additions are present locally and must be
checked with `git status` before describing them as publicly pushed.

## Reproduction and integrity rules

- Use `tools/scripts/` for repeatable collection and analysis.
- Preserve raw ADB output; generate summaries separately.
- Verify each capture with its adjacent `sha256sums.txt` or manifest.
- Never use the original archive as an extraction destination.
- No root exploit, unknown Binder transaction, malformed ioctl, recovery/OTA
  execution, partition write, or Fire Launcher state mutation is part of the
  current safe analysis boundary.
