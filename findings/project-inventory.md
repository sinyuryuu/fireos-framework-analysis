# Project inventory

Inventory captured 2026-08-10 from the local worktree. Project root:

`/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire`

Public Git baseline at capture time: `b53de9c38957c90331584d658252f18a8ac9cfb1` (`main`). The worktree also contains many local, untracked experiment captures; they are not implicitly part of a commit.

## Directory map

| Directory | Purpose | Approx. local size | Public/raw status |
|---|---|---:|---|
| `adb/` | Device snapshots, logcat, mutation records and rollback evidence | 1.4G | Raw device evidence; much is local-only/ignored |
| `firmware/original/` | Original Amazon source archives and official OTA | 6.0G | Raw downloads are ignored; hashes are recorded in manifests |
| `firmware/extracted/` | Read-only extracted source, OTA images and selected files | 12G | Raw extraction is ignored; never written back to device |
| `firmware/partitions/` | Partition work area | 0B | Reserved; no flashing workflow |
| `firmware/manifests/` | Hashes, provenance and OTA metadata | 352K | Small provenance records |
| `artifacts/` | Analysis inputs, reports, manifests and selected APK/JAR/VDEX files | 8.3G | Mixed; selected summaries are public, raw artifacts mostly local |
| `decompiled/` | JADX/apktool/baksmali outputs and disassembly | 1.8G | Mostly local/ignored; source hashes are used in reports |
| `aosp/` | Android 9 AOSP reference sources and init baseline | 11M | Reference sources and manifests are tracked |
| `findings/` | Human-readable findings and evidence indexes | 5.6M | Reports are intended for publication |
| `output/` | Tables, call graphs, timelines and rendered outputs | 239M | Selected tables/graphs are tracked |
| `tools/scripts/` | Re-runnable host/device collection and analysis scripts | 17M | Scripts are tracked selectively |
| `reference_ghostlock/` | Local reference material for defensive kernel analysis | — | Do not execute exploit material |
| `poc/`, `tests/`, `work/` | Host-only models, tests and temporary analysis work | — | Preserve; not a device execution authorization |

## Firmware and source inputs

| Input | Local path | SHA-256 | Notes |
|---|---|---|---|
| Fire OS 7.3.3.0 source | `firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2` | `569eca7321910b095f7af8905592f92e47610d302e6930fd27a6a5dee9593665` | GPL/source provenance only |
| Fire OS 7.3.3.1 source | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` | PS7331 source; no system/core/init tree was found |
| PS7331 official OTA | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | Extracted/analyzed only; not sideloaded or flashed |
| PS7331 boot image | `firmware/extracted/PS7331/boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` | Local extracted artifact; not written to device |
| PS7331 system image | `firmware/extracted/PS7331/system.img` | `da8a935484de24251e890fbf4e7dd9155567ebe158fc255d43684ea14c62b1e5` | Read-only filesystem extraction |
| PS7331 vendor image | `firmware/extracted/PS7331/vendor.img` | `d1db5a5349d046361710bd6966adb7ef88dc4ddc550295e8c1926cb279f213eb` | Read-only filesystem extraction |

The 7.3.3.1 archive expands into `platform.tar` and `fireos.tar`; recorded hashes are `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` and `bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369` respectively.

## Important kernel-source paths

Under `firmware/extracted/PS7331-SOURCE-20250617/`:

- `platform/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig` — target configuration; SHA-256 `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac`.
- `platform/kernel/mediatek/mt8183/4.4/arch/arm64/boot/dts/mediatek/trona_evt.dts` — board/device-tree input; SHA-256 `19588549c3afb03b5c459f11f99b2d924c510103b3ff206040beb65e353cb957`.
- `platform/kernel/mediatek/mt8183/4.4/kernel/futex.c` and `kernel/locking/rtmutex.c` — futex/rtmutex static comparison inputs.
- `platform/kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/cmdq/v3/cmdq_driver.c` — CMDQ driver surface; no ioctl/fuzzing was run.
- `platform/device/amazon/kernel/driver/amzn_idme.c`, `amzn_logger.c`, `amzn_keycombo.c` — Amazon kernel drivers. Their recorded hashes are `ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e`, `9293b2f75e8e7760f961d5849b3fe3e666e8e2df0b2906b6fcdf4b2190d7afbd`, and `09e19712f177e0740a96964f420f74adda3412442b65d6df5cec8187e38e6071`.

This GPL drop is a kernel/vendor-source distribution, not a complete Amazon userspace/framework source tree. `platform/system/core/init/selinux.cpp` and source-tree `rootable_*_sepolicy.cil` were not present in the audited scope.

## Important Android/Amazon artifacts

- `artifacts/framework/framework.jar`, `artifacts/services/services.jar`, `artifacts/framework/fosframework.jar`, `artifacts/framework/framework-res.apk`, `artifacts/framework/boot-framework.vdex`, `artifacts/framework/boot-fosframework.vdex` — framework and system-server analysis inputs.
- `artifacts/launcher/com.amazon.firelauncher__0_com.amazon.firelauncher.apk` — Fire Launcher manifest/signature/component evidence.
- `artifacts/launcher/com.microsoft.launcher__0_base.apk` — test/third-party launcher reference.
- `artifacts/amazon-services/*_fosinit.xml` — Amazon callback/service registration evidence, including AppCompat, Eve, key-policy and launcher-hijack-preventer registrations.
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` — Amazon service VDEX disassembly; SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`.
- `decompiled/baksmali/vdexExtractor/services/disassembly.log` — Android services VDEX disassembly; SHA-256 `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`.
- `artifacts/phase6kw-vendor-home-callbacks/` — generated callback audit and graph from the two disassembly inputs.

## AOSP baseline

- `aosp/android-9/android-9.0.0_r1/` and `aosp/android-9/android-9.0.0_r61/` — selected Android 9 framework, PackageManager, ActivityManager, policy, Settings and init sources.
- `aosp/android-9/init-source-20260804-01/` — AOSP `init`/`selinux.cpp` baseline with `sha256sums.txt` and source manifest.
- `aosp/references/aosp-baseline.md` — tag, commit and provenance notes.

## Device evidence anchors

- Latest public read-only writer reachability capture: `adb/phase6ep/PHASE6EP-AMAZON-WRITER-REACHABILITY-20260809-191243/`.
- Phase 6KV public PMS/source-scope evidence: `findings/phase-6kv-pms-home-caller-closure.md`, `findings/phase-6kv-evidence-index.md`, `artifacts/phase6kv/`, `output/tables/phase6kv-*.csv`.
- The observed PS7331 fingerprint in the latest capture is `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`; User 0 HOME resolved to `com.amazon.firelauncher/.Launcher` with priority 50.

## Data-handling boundary

Original firmware, extracted images, large disassembly logs and raw ADB captures are kept locally and are generally ignored by Git. Public commits contain selected summaries, hashes, tables and re-runnable scripts—not raw credentials, device unlock codes, private account data, or an implicit authorization to flash or execute exploit material.
