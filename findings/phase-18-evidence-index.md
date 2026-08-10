# Phase 18 evidence index — broad privilege surface

Date: 2026-08-10 (Asia/Taipei)
Scope: host-only static analysis and reconciliation of existing device evidence.
No new ADB command, Binder transaction, driver operation, reboot, OTA/recovery operation, partition write, root action, or Fire Launcher state mutation was performed in Phase 18.

## Evidence rules

`Confirmed` means the cited artifact or prior test directly records the claimed fact. `Strong evidence` means the static chain is concrete but a caller, user scope, policy, or runtime edge remains open. `Probable` means the capability or lifecycle is plausible and bounded by evidence. `Hypothesis` means an evidence edge is missing; it is not a finding that the path exists. `Disproved` is always bounded by the listed corpus and test conditions.

## Provenance and input hashes

| Evidence ID | Source | File / artifact | SHA-256 | Observation | Confidence |
|---|---|---|---|---|---|
| P18-PROV-001 | PS7331 GPL source | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` | Exact PS7331 source archive retained | Confirmed |
| P18-PROV-002 | extracted source | `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` | Platform/kernel source container | Confirmed |
| P18-PROV-003 | extracted source | `firmware/extracted/PS7331-SOURCE-20250617/fireos.tar` | `bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369` | Fire OS source container | Confirmed |
| P18-PROV-004 | kernel source | `platform/kernel/mediatek/mt8183/4.4/kernel/futex.c` and `kernel/locking/rtmutex.c` | See `kernel/source-manifest.json` | PS7331 kernel source inputs | Confirmed |
| P18-PROV-005 | PS7331 OTA | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | Full signed OTA; PS7331.4463N/trona metadata | Confirmed |
| P18-PROV-006 | OTA metadata | `firmware/extracted/PS7331/ota.prop` | recorded in `firmware/manifests/OTA-20260803-01/README.md` | Fire OS 7.3.3.1 / PS7331.4463N | Confirmed |
| P18-PROV-007 | boot artifact | `firmware/extracted/PS7331/boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` | PS7331 boot member | Confirmed |
| P18-PROV-008 | kernel payload | `firmware/extracted/PS7331/boot_unpacked/kernel` | `a608a5f99c155dc8e8b12b308528cbd17175b47199985d017613f9e2fbb1edba` | boot-derived compressed kernel | Confirmed |
| P18-PROV-009 | kernel image | `firmware/extracted/PS7331/boot_unpacked/Image` | `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d` | boot-derived decompressed image | Confirmed |
| P18-PROV-010 | framework extraction | `firmware/extracted/PS7331/selected/manifest.sha256` and `compiled-02/manifest.sha256` | local file hashes recorded in Phase 18 manifest | Selected APK/JAR and VDEX/ODEX inputs | Confirmed |

The exact PS7330.4104N source, signed boot/kernel, full OTA and security-patch artifact are not present in this corpus. PS7331 provenance must not be silently applied to PS7330.

## Core runtime evidence reused without repetition

| Evidence ID | Source | File | Test ID | Observation | Interpretation | Confidence |
|---|---|---|---|---|---|---|
| P18-RUN-001 | existing device test | `adb/phase6fk/PHASE6FK-USER0-TX3-20260807-01/command-output.txt` | `PHASE6FK-USER0-TX3-20260807-01` | ordinary APK UID 10213 reached KFT tx3; PMS rejected `setComponentEnabledSetting` before mutation | ordinary User 0 KFT route is blocked at PMS | Confirmed |
| P18-RUN-002 | existing device test | `adb/phase6fj/PHASE6FJ-USER10-TX3-20260807-01/command-output.txt` | `PHASE6FJ-USER10-TX3-20260807-01` | ordinary APK UID 10212 supplied User 10; cross-user check rejected | user id in parcel is not an unrestricted relay | Confirmed |
| P18-RUN-003 | existing device test | `adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/result.json` | `PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346` | prewarm caused temporary process/resource effect only | bounded deputy, not package/HOME/UID0 | Confirmed |
| P18-PM-001 | static artifact | `decompiled/jadx/ota-PS7331/systemui-nores/sources/com/android/server/pm/PackageManagerService.java` | — | preferred and enabled-state paths remain PMS-gated | no evidence of ordinary bypass | Confirmed |
| P18-PM-002 | static artifact | `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log` | — | Amazon PM facade delegates without visible identity clear in setters | facade is not an identity relay | Strong evidence |
| P18-KFT-001 | static artifact | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325,54415-54492` | — | KFT writer targets Tahoe, Fire Launcher and Launcher3 states; later DPM work clears identity | real trusted-service writer; caller gate remains open | Strong evidence |

## Worker row-level integration

The five delegated workers were host-only. Their isolated raw files were not visible in the main worktree; the integrated CSV preserves their row-level conclusions and the evidence paths reported by each worker. No worker result is treated as runtime proof unless a saved runtime file is cited.

| Evidence IDs | Worker scope | Integrated result | Confidence |
|---|---|---|---|
| 18A-001…015 | Amazon IPC/AIDL/ServiceManager inventory | 12 `Hypothesis`, 3 `Probable` capability-only rows; no confirmed shipped private Binder implementation or runtime sink | Hypothesis / Probable |
| OTA-01…13 | OTA/post-install audit | signed full block OTA and recovery write capability are static; no ordinary app/shell recovery caller; no independent A/B postinstall in bounded member set | Strong evidence / Probable |
| 18C-001…012 | GPL/kernel/native caller closure | ION generic/MTK static caller entry closed; CMDQ/M4U/performance/uinput/AUXADC/RPMB/USB/Amazon diagnostic remain open or bounded negative | Strong evidence / Hypothesis |
| H01…H24 | existing-result reconciliation | prior HOME, disable, KFT, accessibility, OTA, CVE, GhostLock and boot/write findings reconciled; only trusted KFT caller, service edges, driver joins and native OTA handoff remain open | Confirmed / Hypothesis / Disproved (bounded) |

## Main findings and evidence mapping

| Finding | Evidence IDs | File / method | Confidence |
|---|---|---|---|
| KFT contains a real Fire-state writer | P18-KFT-001, P18-RUN-001 | `AmazonUserManagerService.enableKftLauncher` and PMS runtime rejection | Strong evidence + Confirmed boundary |
| Ordinary User 0 KFT relay does not change Fire state | P18-RUN-001 | `PHASE6FK` command output | Confirmed |
| Ordinary cross-user KFT relay is blocked | P18-RUN-002 | `PHASE6FJ` command output | Confirmed |
| Amazon PM facade does not launder identity | P18-PM-002 | AmazonPackageManager smali delegation | Strong evidence |
| Prewarm is limited to process/resource effect | P18-RUN-003 | prior Phase 6ER result | Confirmed |
| OTA has recovery-only partition write capability | OTA-02…05 | updater-script / update-binary audit | Strong evidence |
| OTA is not an ordinary app/shell route | OTA-11…13 | protected lifecycle and recovery boundary reports | Strong evidence |
| ION native entry exists but is not a root sink | 18C-001, 18C-002 | `ion.c`, `ion_drv.c`, `libion*.so` call sites | Strong evidence |
| Other driver paths lack caller/policy/runtime closure | 18C-003…012 | GPL source, config, image/policy inventories | Hypothesis |
| Reviewed GhostLock/CVE paths do not establish stock root | H19, H20 | Phase 5/9 reports | Disproved within reviewed corpus; runtime exploitability remains unproven |
