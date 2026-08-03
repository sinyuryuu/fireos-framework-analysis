# Phase 5 evidence index

All paths below are relative to the repository root. The read-only baseline
manifest is `adb/phase5/PHASE5-LOWLEVEL-BASELINE-20260803-01/sha256sums.txt`.

| Evidence ID | Source / file | Test ID / time | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| P5-BASE-001 | `adb/phase5/PHASE5-LOWLEVEL-BASELINE-20260803-01/summary.md`, `sha256sums.txt` | `PHASE5-LOWLEVEL-BASELINE-20260803-01`, 2026-08-03 10:13Z | Read-only inventory completed and manifest verified | Canonical Phase 5 baseline; no mutation was run | Confirmed |
| P5-BASE-002 | `device/getprop.stdout.txt`, individual property files | same | KFTRWI/trona, PS7330.4104N, Android 9/Fire OS 7.0, MT8183, patch 2024-02-01, green VB, flash locked, RPMB 2 | Exact current device/build identity | Confirmed |
| P5-BASE-003 | `adb/devices.stdout.txt`, `adb/get_state.stdout.txt` | same | Serial `G001LT0511550CFT` is `device` | ADB remained connected in normal mode | Confirmed |
| P5-BASE-004 | `paths/block_by_name.stdout.txt`, `storage/mount.stdout.txt` | same | Boot/system/vendor/userdata and other by-name links visible; no preloader link in shell listing; no remount issued | Shell-visible partition inventory only; no inference about hidden boot media | Confirmed |
| P5-BASE-005 | `device/firelauncher_path.stdout.txt`, `device/firelauncher_package.stdout.txt` | same | Fire APK is `/system/priv-app/com.amazon.firelauncher/...apk`, version `1.3.232663.0_82020310`, privileged/system flags, HOME priority 50 | Fire is a privileged system HOME candidate | Confirmed |
| P5-BASE-006 | `boot/proc_cmdline.stderr.txt`, `storage/proc_partitions.stderr.txt`, `boot/proc_bootconfig.stderr.txt` | same | Permission denied / absent files preserved | Shell cannot provide complete boot-chain metadata | Confirmed |
| P5-STATIC-001 | `artifacts/amazon-services/amazonpackagemanager_fosinit.xml:22-24`; SHA-256 `eb53e50cf72174eddcde25fd3538e4736d2cd4cb7866bab4e5bc2b70fc514286` | offline artifact | Vendor protected-package callback registered to Amazon implementation | Amazon callback is inserted into PackageManager protection path | Confirmed |
| P5-STATIC-002 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96950-97049`; SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | offline VDEX | Reads `/data/system/PackageManagerDenyList`, `DenyListKeyPackages`; requires system app and UID 2000 | Exact Amazon protected-package gate inputs | Confirmed |
| P5-STATIC-003 | `decompiled/baksmali/vdexExtractor/services/disassembly.log:953377-953546`, `505771-505837`, `539225-539250`; SHA-256 `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53` | offline VDEX | Package state mutation calls protected-package path before mutation | `pm`/`cmd package` rejection point | Confirmed |
| P5-STATIC-004 | `artifacts/amazon-services/launcherhijackpreventer_fosinit.xml:9-18`, `tabletlauncherhijackpreventer_fosinit.xml:9-16`; SHA-256 `026a1efce008ef99cc2afa32a9bc8913bf929e74256af67971f426a97c968eea`, `64ec345b123a53ac388104d13f3bf0a179c347fa248d3dd28b58c6e5c4aaf14e` | offline artifact | ActivityStack/AM/PM/permission callbacks are registered | Amazon adds framework callback boundaries | Confirmed |
| P5-STATIC-005 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:136880-136953` | offline VDEX | `canSeeHomeTask()` checks SELinux `amazon_policies/see_home_task` and signature fallback; no Fire start call | Inspected callback is visibility/protection, not direct Fire launch | Confirmed (scope-limited) |
| P5-STATIC-006 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:33638-33652` | offline VDEX | Migration service sends an external-applications broadcast scoped to `com.amazon.firelauncher` | Explicit Fire reference, not HOME selection | Confirmed |
| P5-STATIC-007 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54324` | offline VDEX | KFT launcher path enables FreeTime activity and changes Fire/Launcher3 state for a `UserInfo` | Literal Fire hardcode in child/KFT path; not User 0 HOME proof | Confirmed (scope-limited) |
| P5-WEB-001 | [MediaTek March 2022 bulletin](https://corp.mediatek.com/product-security-bulletin/March-2022), [April 2022 bulletin](https://corp.mediatek.com/product-security-bulletin/April-2022) | web review 2026-08-03 | Selected preloader bulletin rows include MT8183 but affected software families are Android 10/11/12 | Chipset/software-family relevance only; exact exploit applicability unknown | Strong evidence / not device proof |
| P5-WEB-002 | [mtkclient BROM configuration](https://raw.githubusercontent.com/bkerler/mtkclient/main/mtkclient/config/brom_config.py), [project README](https://github.com/bkerler/mtkclient) | web review 2026-08-03 | Checked snapshot has MT8168/MT6357 entry but no MT8183 entry; README describes DA/auth limitations | No exact public-tool compatibility established | Confirmed snapshot / not absolute incompatibility |
| P5-OTA-001 | `firmware/extracted/PS7331/images/preloader.img`, `lk.img`, `boot.img` | offline artifact | PS7331 artifacts have recorded hashes while device is PS7330.4104N | Version mismatch; cannot be used as recovery or flash evidence | Confirmed |
| P5-STATUS-001 | `findings/phase-5-level3-approval-report.md` | current phase | No bootloader, exploit, unlock, remount, write, or flash operation executed | Level 3 boundary remains intact | Confirmed |

## Evidence handling

The raw baseline files are immutable evidence for this phase. Any future
bootloader or low-level collection must use a new test ID and new directory;
the prior SHA-256 manifest must not be overwritten.
