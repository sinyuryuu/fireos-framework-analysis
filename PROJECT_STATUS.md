# Project Status

## Current phase

Phase 1 preliminary evidence collection is complete for the connected device. The current result is evidence-backed, but it is not yet a multi-version or OTA-complete Fire OS study.

Device run date: 2026-08-03  
ADB serial: `G001LT0511550CFT`  
Primary baseline: `BASELINE-20260803-04`
Final read-only verification before report refresh: `BASELINE-20260803-05`
Final read-only verification after component tests: `BASELINE-20260803-07` (complete; both manifests passed)

## Completed

- Created the complete project directory structure and safety-gated scripts.
- Recorded local tool versions in `tools/tool_versions.txt`.
- Collected and hashed device properties, package/service/process/mount/security state.
- Identified the launcher as `com.amazon.firelauncher/.Launcher`.
- Collected all currently visible HOME candidates and their priorities.
- Captured `input keyevent 3` from a non-launcher foreground activity.
- Captured explicit `ACTION_MAIN + CATEGORY_HOME` resolution.
- Tested `set-home-activity` with Microsoft Launcher and restored Fire Launcher.
- Tested `pm disable-user` with explicit approval; the command was rejected by PackageManager.
- Used Microsoft Launcher as a package-state control: `pm disable-user` succeeded and was restored; Fire Launcher remained protected under both `pm` and `cmd package`.
- Tested disabling only `com.amazon.firelauncher/.Launcher` with both `pm` and `cmd package`; both were rejected by the same protected-package gate and left component state unchanged.
- Rebooted once with explicit approval and verified the launcher after PackageManager became ready.
- Repeated Home-key tests after waking and dismissing keyguard, so locked-screen results are not mixed with unlocked Home behavior.
- Tested unlocked Settings and Firefox foreground states, explicit HOME, and Microsoft preferred-home state with unique test IDs `HOME-T14`, `HOME-T15`, `HOME-T16` and `HOME-PREF-T17`.
- Tested Microsoft Launcher as the directly foregrounded app before both `KEYCODE_HOME` and explicit HOME with unique test IDs `HOME-T18` and `HOME-T19`; both reached Fire while unlocked.
- Probed `android.settings.HOME_SETTINGS` and captured the live Default apps UI with `HOME-T20`/`HOME-T21`; the main page has no Home-app row.
- Opened Fire Launcher's App info with `HOME-T22`; its `Home app: Yes` row is visible. Tapped only that row in `HOME-T23`; it returned to `DefaultAppSettings` without exposing a launcher picker, then restored Fire Launcher.
- Compared the installed Settings `app_default_settings.xml` with official Android 9 r1/r61 references: Fire OS omits the `default_home` preference while retaining the controller/picker implementation and resources.
- Captured DevicePolicy state with read-only `POLICY-T01`: `com.amazon.parentalcontrols` is the User 0 Profile Owner, but there is no Device Owner, device-managed state or effective user restriction in the captured environment.
- Pulled and decompiled the installed parental-controls APK; it targets Fire Launcher with `DevicePolicyManager.setApplicationRestrictions()` for content/policy keys and hides only filtered third-party packages in the inspected package-change path.
- Tested retained Settings picker routes with `SETTINGS-T01`/`T02`/`T03`; the external `SubSettings` route is not exported, while the corrected `Settings$AdvancedAppsActivity` route falls back to the Home-less Default apps dashboard. No launcher was selected.
- Rebooted again with explicit approval (`REBOOT-T03`) and retained the boot-time FallbackHome-to-Fire resolver transition.
- Added a read-only Alexa mode-switch probe (`ALEXA-MODE-T01`) and documented its conditional multimodal-Home callback without treating it as a Fire Launcher launch.
- Pulled readable APKs, framework resources, VDEX/ODEX artifacts and Fire OS configuration XMLs without root.
- Decompiled the readable APKs and extracted VDEX disassembly for the framework/service paths.
- Downloaded and provenance-checked the official adjacent PS7331 OTA; decompressed its transfer-list images read-only, extracted selected ext4 paths and VDEX/ODEX artifacts, and marked it `VERSION_MISMATCH` against the installed PS7330.4104N build.
- Fetched official AOSP Android 9 reference files for `android-9.0.0_r1` and `android-9.0.0_r61` and recorded their source paths for structural comparison.
- Indexed HOME, package-protection and Amazon callback references.
- Indexed SystemUI's conditional Fire Launcher reference and distinguished it from its explicit Smart Genie launch target.
- Added deterministic parsers for HOME candidates, decompiled classes/methods, structural AOSP/Fire OS comparison, evidence manifests, call-graph edges and report rendering. All support --dry-run.
- Enhanced the AOSP/Fire OS comparator to emit class similarity, paired method-signature differences, a structural matching score and a manual-review queue; it explicitly labels those outputs as non-proof of OEM modification.
- Wrote `findings/phase-1-report.md`, the evidence index, the LauncherHijackPreventer finding and the preliminary call graph.

## Confirmed phase-1 results

| Question | Result | Confidence |
|---|---|---|
| Current HOME resolver result | `com.amazon.firelauncher/.Launcher`, priority 50 | Confirmed |
| HOME candidates | Fire Launcher 50, Microsoft Launcher 0, Settings FallbackHome -1000 | Confirmed |
| `set-home-activity` effect | Writes a preferred record and reports `Success`, but Fire remains selected because its candidate priority is higher | Confirmed |
| Home key framework hook | Android 9 `PhoneWindowManager.handleShortPressOnHome()` calls Amazon `KeyPolicyManager` before the normal home path | Confirmed |
| Normal tested Home path | When unlocked, `KEYCODE_HOME` from Settings or Firefox and explicit HOME all reach Fire through the standard resolver; earlier contrary runs were keyguard-blocked | Confirmed for tested unlocked paths |
| Package disable result | `Cannot disable a protected package: com.amazon.firelauncher` from `PackageManagerService.setEnabledSetting()` | Confirmed |
| Protection implementation | Android `ProtectedPackages` calls vendor callbacks; Amazon registers `ControlProtectedPackagesCallback`, which protects system apps in its deny list from shell UID 2000 | Strong evidence; deny-list membership itself is not shell-readable |
| Package-state restoration | Not the cause of the tested failure; state never changed because the call failed before mutation | Confirmed |
| Shell UID blanket restriction | Microsoft package can be disabled/restored by shell; Fire-only rejection is package protection | Disproved |
| Persistent package flag | No `PERSISTENT` or `CORE_APP` flag is shown in the captured package dump | Confirmed observation; separate preferred/policy state remains distinct |
| LauncherHijackPreventer | Amazon adds an ActivityStack callback that gates visibility of Home tasks using `amazon_policies:see_home_task` or Android signature checks | Confirmed code path; not proven to launch Fire |
| Settings Default apps UI | Main `default_home` preference is absent; live `HOME-T21` page has no Home row | Confirmed |
| Fire App info Home row | Visible as `Home app: Yes`; `HOME-T23` routes back to the Home-less Default apps page | Confirmed |
| Active DevicePolicy environment | `com.amazon.parentalcontrols` is Profile Owner; no Device Owner, device-managed state or effective user restrictions were captured | Confirmed observation |
| DevicePolicy as cause of `pm disable-user` failure | The tested request fails in PackageManager protected-package enforcement before a DevicePolicy path; parental APK uses application restrictions instead | Disproved for tested disable path |
| Component-only disable workaround | Both `pm` and `cmd package` reject the Fire Launcher HOME component; resolver/focus and `disabledComponents` remain unchanged | Disproved |
| Retained `DefaultHomePicker` reachability | Tested shell routes are blocked by exportedness or fall back to `DefaultAppSettings`; privileged/internal reachability remains open | Probable unavailable for tested routes |

## Important limitations

- Earlier differential runs `HOME-PREF-T02` and `HOME-PREF-T03` were collected while `mKeyguardShowing=true`; they are retained as lock-screen observations, not evidence that Microsoft bypasses the resolver. The valid unlocked preferred-state run is `HOME-PREF-T17`, and the direct-foreground controls are `HOME-T18`/`HOME-T19`; all launched Fire.
- `HOME-T01` is an ADB-generated `KEYCODE_HOME` event, not a manually pressed physical button. The physical-button path remains `Hypothesis` until separately sampled.
- `REBOOT-T01` captured the device before the PackageManager service was ready and is retained as a timing-invalid run. `REBOOT-T02` and `REBOOT-T03` are valid reboot verifications with readiness polling.
- The shell could not read `/data/system/PackageManagerDenyList`; the runtime exception plus Amazon callback code proves the effective protection path, but not the deny-list file contents.
- The readable `/system/framework/framework.jar` and `services.jar` are 183-byte stub JARs. Framework behavior was analyzed from matching VDEX/ODEX disassembly, not from those stub files.
- No exact matching OTA has yet been acquired. The official PS7331 OTA is retained under `firmware/manifests/OTA-20260803-01/` and `firmware/extracted/PS7331/` for adjacent-version analysis only; pulled PS7330 artifacts remain device-derived and are not to be labeled as OTA-derived.
- No root, DRM/account bypass, factory reset, data clear, sideload, flash or destructive package removal was performed.
- The current parental-controls application-restriction bundle was not read from the device; the APK proves capability and target package, not the exact live policy values.
- Amazon's KFT child-user path that enables FreeTime and disables Fire Launcher/Launcher3 was identified statically; it is a separate child-user/upgrade path, not evidence of a primary-user watchdog.

## Reproducible artifacts

- Baseline: `device/baseline/BASELINE-20260803-04/` and `adb/baseline/BASELINE-20260803-04/`
- Final read-only verification: `device/baseline/BASELINE-20260803-05/` and `adb/baseline/BASELINE-20260803-05/`
- Latest final read-only verification: `device/baseline/BASELINE-20260803-06/` and `adb/baseline/BASELINE-20260803-06/`
- Latest final read-only verification: `device/baseline/BASELINE-20260803-07/` and `adb/baseline/BASELINE-20260803-07/`
- Earlier baselines: `BASELINE-20260803-02` and `BASELINE-20260803-03` are retained and not overwritten.
- Home key: `adb/home-key-tests/HOME-T01/`
- Explicit HOME intent: `adb/home-key-tests/HOME-T02/`
- Unlocked Home matrix: `adb/home-key-tests/HOME-T14/`, `HOME-T15/`, `HOME-T16/`
- Preferred-home probe: `adb/launcher-tests/HOME-DEFAULT-T01/`, `HOME-PREF-T01/` and valid unlocked `HOME-PREF-T17/`
- Protected-package tests: `adb/package-tests/PACKAGE-T01/`, `PACKAGE-T02/`, `PACKAGE-T03/`, `PACKAGE-T04/`, `PACKAGE-T05/`
- Component protection tests: `adb/component-tests/COMPONENT-T01/`, `adb/component-tests/COMPONENT-T02/`
- Valid reboot verifications: `adb/logs/REBOOT-T02/` and `adb/logs/REBOOT-T03/`
- Alexa mode read-only probe: `adb/probes/ALEXA-MODE-T01/`
- Settings UI probes: `adb/home-settings-tests/HOME-T20/`, `HOME-T21/`, `HOME-T22/`, `HOME-T23/`
- DevicePolicy probe: `adb/probes/POLICY-T01/`
- Settings picker probes: `adb/settings-tests/SETTINGS-T01/`, `SETTINGS-T02/`, `SETTINGS-T03/`
- Device-derived artifacts: `artifacts/` and `decompiled/`
- Parental-controls APK: `firmware/manifests/ARTIFACT-20260803-08/sha256sums.txt`, `decompiled/jadx/parentalcontrols/`
- Adjacent OTA: `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`, extracted under `firmware/extracted/PS7331/`
- AOSP references: `aosp/android-9/`
- AOSP structural comparison: `diff/reports/aosp-r1-vs-fireos-jadx-phase3/` and `diff/reports/aosp-r61-vs-fireos-jadx-phase3/`
- Initial call graph: `output/call-graphs/home-flow-phase1.txt`
- Preliminary call graph: `output/call-graphs/home-flow-preliminary.txt`
- Home-task visibility finding: `findings/launcher-hijack-preventer.md`
- Main report: `findings/phase-1-report.md`

## Generated analysis outputs

- Edge index: output/call-graphs/home-framework-phase1.tsv
- Class/method tables: output/tables/class-index-phase1.tsv and output/tables/method-signatures-phase1.tsv
- HOME candidate table: output/tables/home-candidates-phase1.tsv
- Machine evidence table: output/tables/evidence-index-adb-phase1.tsv
- Preliminary machine evidence table: output/tables/evidence-index-adb-preliminary.tsv
- Full Phase 2 evidence index: `output/tables/evidence-index-phase2-final.tsv`
- Rendered report artifact: output/rendered/phase-1-report.md
- Preliminary rendered report: output/rendered/phase-1-report.preliminary.md
- Final preliminary rendered report: output/rendered/phase-1-report.preliminary-final.md
- Phase 2 rendered report: `output/rendered/phase-1-report.phase2.md`
- Phase 2 final rendered report: `output/rendered/phase-1-report.phase2-final.md`
- Latest Phase 2 rendered report: `output/rendered/phase-1-report.phase2-final4.md`
- Latest rendered report after Settings UI probes: `output/rendered/phase-1-report.phase2-final7.md`
- Phase 2 output hashes: `output/tables/phase2-artifact-sha256sums.txt`
- Current machine evidence index: `output/tables/evidence-index-20260803-04.tsv`
- This update's machine evidence index: `output/tables/evidence-index-20260803-07.tsv`
- DevicePolicy/Settings picker refresh machine evidence index: `output/tables/evidence-index-20260803-08.tsv` (`831af14ded69f4001982e3f09c5fb26abf29bd5eaa5ffdc213476757cbf5f7fd`)
- Parental-controls class index: `output/tables/parentalcontrols-class-index-20260803-01.tsv` (`b769563b43d1a12359c3d6eb2d6db7465a26c6c8080890a60f91c871964c7d7f`)
- Parental-controls method index: `output/tables/parentalcontrols-method-signatures-20260803-01.tsv` (`7ec9b7fd53dba637b7337e3e12dd77c222f39380fa61bead00ec9fbc3e51c80f`)
- Latest rendered report after DevicePolicy/Settings picker analysis: `output/rendered/phase-1-report.phase2-final8.md` (`2a233cf81351528f9af87996775396221361b5db8e56f32380a5840846c5c99b`)
- Current post-baseline machine evidence index: `output/tables/evidence-index-20260803-10.tsv` (`3908c243ce9d86acffb9698bbf9dfa6f1d7cddd780f83af557914542baa463ff`)
- Current post-baseline rendered report: `output/rendered/phase-1-report.phase2-final9.md` (`feb3c03d981b13f0eeda124a4f2fd1700649ee583cb92510a0a920d18d6b8762`)
- Current post-component-test machine evidence index: `output/tables/evidence-index-20260803-11.tsv` (`23b20e1351060271d74e6396d0f460b4891df239318374a4eee13acbb6d1c14d`)
- Current post-component-test rendered report: `output/rendered/phase-1-report.phase2-final10.md` (`fceb478a496783037c5236c6688ff123f0b8714e5b8469303d5d82ecd6e7ee41`)
- Preliminary generated edge index: output/call-graphs/home-framework-preliminary.tsv
- SystemUI launch-reference finding: `findings/systemui-launch-search.md`
- Settings Home UI finding: `findings/phase-1-report.md` section 8; evidence rows F-044–F-048
- Reproducible Settings resource/UI comparison: `tools/scripts/analyze_settings_home_ui.py` and `output/tables/settings-home-ui-analysis-20260803-05.md`
- DevicePolicy/parental-controls finding: `findings/phase-1-report.md` section 5 and evidence rows F-049–F-054
- Dedicated DevicePolicy finding: `findings/parental-controls-dpm.md`
- Dedicated component protection finding: `findings/component-protection.md`
- Component protection script: `tools/scripts/test_component_disable.sh`

## Phase 2 status

Phase 2 protected-package and HOME-resolution analysis is complete for the current evidence set. The exact PackageManager gate, Fire OS vendor callback, Amazon deny-list storage path, Fire Launcher manifest priority, candidate list, preferred-state mutation behavior, and normal Home-key flow are documented in `findings/phase-2-report.md`. The current deny-list file contents and physical hardware-button trace remain explicitly unknown.

Required Phase 2 outputs are present under `findings/`, `diff/reports/`, `output/tables/`, and `output/call-graphs/`. The read-only mutation snapshot framework is `tools/scripts/capture_mutation_snapshot.sh`; it requires an explicit serial and supports `--dry-run`.

No new Level 3 operation was executed. No new component-disable test was run because the existing T01/T02 conditions were unchanged and already disproved that workaround.

## Next phase

- Acquire and verify an exact-match official OTA (`VERSION_MISMATCH` until matched).
- Compare the installed-build framework/service code with the fetched Android 9 AOSP tags using normalized class/method evidence; keep AOSP structural differences separate from Amazon patches.
- Obtain a physical Home-button sample and, if available, a second Fire OS 7 build.
- Resolve the exact live `alexa_modeswitch` mode/service visibility if a safe system-server-facing observation becomes available.
- Inspect the remaining Amazon callback implementations and native components for explicit component launches and policy overrides.
- Evaluate non-root workarounds only after the mechanism report is stable.

## Phase 3A status

Phase 3A resolver static analysis and experiment infrastructure are now
implemented and executed for the normal ADB-installable app condition. The
static pass confirms the Fire VDEX priority comparison path, the AOSP-standard
non-privileged priority cap in `ActivityIntentResolver.adjustPriority()`, and
documents an Amazon ActivityStackSupervisor vendor callback boundary.

The read-only pre-snapshot `HOME-PRIORITY-PRE` is complete and hash-verified.
Five priority variants were built with local OpenJDK 26 and the pinned SDK
tools. P49/P50/P51/P100 completed the reversible mutation sequence; P0 was
interrupted after reboot and then recovered from its preserved restore script.
All final checks returned Fire Launcher, all research APKs were uninstalled,
and no Fire Launcher state/data or system partition was modified.

Runtime conclusion: declared APK priorities 49/50/51/100 are normalized to
effective priority 0 for non-privileged sideloaded apps, while privileged Fire
Launcher retains effective priority 50. Ordinary preferred records can be
written (`mAlways=true`) but do not override the effective Fire result.

Phase 3A outputs:

- `findings/home-resolver-method-analysis.md`
- `diff/reports/home-resolver-aosp-fireos-diff.md`
- `findings/home-priority-experiment.md`
- `findings/phase-3a-report.md`
- `tools/test-launcher/`
- `tools/scripts/run_home_priority_experiment.sh`
- `adb/mutation-tests/HOME-PRIORITY-PRE/`
- `adb/mutation-tests/HOME-PRIORITY-P0/`
- `adb/mutation-tests/HOME-PRIORITY-P49/`
- `adb/mutation-tests/HOME-PRIORITY-P50/`
- `adb/mutation-tests/HOME-PRIORITY-P51/`
- `adb/mutation-tests/HOME-PRIORITY-P100/`

## Phase 5BA status

Phase 5BA evaluates the newly available PS7331 source URL and local official
PS7331 `boot.img` as adjacent-version, host-only evidence. The PS7331 signed
kernel Image retains the inspected old `remove_waiter()` current-task cleanup
pattern, and PS7330/PS7331 focus kernel configs differ in only three unrelated
keys. The project therefore does not recommend upgrading solely as a
GhostLock remediation. The device remains PS7330.4104N and the upgrade was not
attempted.

Phase 5BA outputs:

- `findings/phase-5ba-ps7331-upgrade-assessment.md`
- `findings/phase-5ba-evidence-index.md`
- `output/tables/phase5ba-upgrade-matrix.csv`
- `output/call-graphs/phase5ba-upgrade-evidence.mmd`
- `tools/scripts/compare_phase5_ps7330_ps7331_kernel.py`
- `tools/scripts/capture_phase5ba_device_postcheck.sh`
- `adb/phase5/PHASE5BA-DEVICE-POSTCHECK-20260804-01/`

## Phase 5BB status

Phase 5BB follows the PS7331 source／boot evidence without changing the
device. The official adjacent PS7331 Image still contains the inspected
pre-fix `remove_waiter()` current-task pattern, and the PS7330／PS7331 focus
kernel configs differ only in three unrelated keys. The exact PS7331 nested
platform source member comparison remains a host-only follow-up; the outer
source package and build scripts prove the `mt8183/4.4` and `trona_defconfig`
layout but are not themselves `rtmutex.c` evidence.

Current decision: defer upgrading solely for GhostLock. Do not write the
standalone PS7331 boot image. If a general security-update A/B study is later
chosen, treat the complete official update as potentially non-reversible and
freeze the current PS7330 baseline first.

Phase 5BB outputs:

- `findings/phase-5bb-ghostlock-ps7331-followup.md`
- `findings/phase-5bb-evidence-index.md`
- `output/tables/phase5bb-ps7331-upgrade-decision.csv`
- `tools/scripts/index_phase5_nested_platform_members.sh`
- `tools/scripts/extract_phase5_nested_kernel_members.sh`

The nested source member scan subsequently found both `kernel/mediatek/mt8183/4.4`
and legacy `kernel/mediatek/4.4` trees. The build-selected `mt8183/4.4`
`rtmutex.c` still uses the pre-fix `current->pi_blocked_on` cleanup in
`remove_waiter()` and has no `waiter->task` fix. The legacy `4.4` file is
byte-identical to the old v4.4.146 reference but is not the build-script path.
This strengthens the decision to defer PS7331 as a GhostLock remediation; it
does not claim that no other PS7331 security changes exist.

## Phase 5BC status

The source-only semantics checker confirms the pre-fix `current->pi_blocked_on`
pattern in both the PS7331 build-selected `mt8183/4.4` source and the legacy
tree. The public Android route matrix still has no exact KFTRWI/trona/MT8183
GhostLock target, and the pinned mtk-su route remains a prior failed result.
The exact PS7331 build-selected `trona_defconfig` was subsequently extracted
from the official source archive. It is a partial Kconfig input, not a final
signed Image; its omissions are not interpreted as disabled symbols. The
PS7331 boot-embedded focus config remains equal to the preserved PS7330 runtime
focus config. No live exploit, upgrade, or low-level write was attempted.

Phase 5BC outputs:

- `findings/phase-5bc-ghostlock-semantic-boundary.md`
- `findings/phase-5bc-evidence-index.md`
- `tools/scripts/check_phase5_ghostlock_source_semantics.py`
- `tools/scripts/compare_phase5_defconfig_focus.py`
- `artifacts/phase5/exact-kernel-source-review-7331-trona-defconfig-member-20260804-01/metadata.tsv`
- `artifacts/phase5/phase5bc-defconfig-focus-20260804-01/`
- `adb/phase5/PHASE5BC-DEVICE-POSTCHECK-20260804-01/`

## Phase 5BD status

The preserved PS7331 package was inspected without installation. It is a full
block OTA whose updater writes system/vendor/boot plus preloader, LK, TEE,
SPMFW, SSPM and camera VPU partitions. The standalone boot image is not an
equivalent upgrade path. A user-consented PendingIntent Accessibility redirect
measurement produced 30 dispatch attempts but 0/30 stable foreground handoffs;
the research toggle was restored off and Fire Launcher remained the formal HOME.
No OTA, root, exploit, boot-chain or partition operation was attempted.

Phase 5BD outputs:

- `findings/phase-5bd-ota-and-redirect-followup.md`
- `findings/phase-5bd-evidence-index.md`
- `output/tables/phase5bd-ota-partition-risk.csv`
- `tools/scripts/inspect_phase5_ps7331_ota.py`
- `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/`
- `adb/phase5/PHASE5BD-ACCESSIBILITY-PENDINGINTENT-T01/`

## Phase 5BE status

Phase 5BE completed a full host-only nested `platform.tar` path inventory for
the official PS7331 source bundle. The exact `.patch`/`.diff`/`series` subset
contains only four Mali hrtimer patch paths; no rtmutex/futex/GhostLock patch
path was found. The preserved `build_kernel.sh` visibly performs extraction,
defconfig, make, output copy and validation, with no visible patch-apply or
overlay step. The build-selected PS7331 `rtmutex.c` and inspected signed Image
still show the pre-fix current-task cleanup pattern.

This strengthens the decision not to upgrade solely for GhostLock. A general
security-update A/B remains a separate possible study, but the official PS7331
package is a full block OTA touching boot-chain and firmware partitions; the
standalone boot image is not an equivalent or reversible upgrade operation.
No upgrade or device mutation was performed.

Phase 5BE outputs:

- `findings/phase-5be-ps7331-build-overlay-review.md`
- `findings/phase-5be-evidence-index.md`
- `tools/scripts/index_phase5_ps7331_nested_build_patches.sh`
- `artifacts/phase5/ps7331-nested-build-patch-index-20260804-01/`

## Phase 5BF status

Phase 5BF adds a deterministic host-only source/config reachability review. The
PS7331 build-selected `mt8183/4.4` `rtmutex.c` retains the pre-fix
`current->pi_blocked_on` cleanup in `remove_waiter()`, its proxy error path still
calls `remove_waiter()`, and the paired `futex.c` contains the PI requeue path.
The captured device config observes `CONFIG_FUTEX=y` and
`CONFIG_RT_MUTEXES=y`. A fixed reference uses `waiter->task` instead.

This is a source/config candidate only: no reproducer, compilation, kernel
execution, address/offset extraction, root attempt, ADB mutation, upgrade, or
partition operation was performed. The exact installed PS7330 signed boot
function remains unavailable. The project therefore still does not recommend
PS7331 solely as a GhostLock fix; general security A/B remains a separate
full-block-OTA decision.

Phase 5BF outputs:

- `findings/phase-5bf-ghostlock-reachability.md`
- `findings/phase-5bf-evidence-index.md`
- `tools/scripts/analyze_phase5bf_ghostlock_reachability.py`
- `artifacts/phase5/ghostlock-reachability-review-20260804-04/`

## Phase 5BG status

Phase 5BG combines three host-only evidence layers: PS7331 build-selected
source semantics, the address-sanitized PS7331 inspected-Image pattern summary,
and a fixed `waiter->task` reference. The machine result is
`PS7331_INSPECTED_IMAGE_CONSISTENT_WITH_PRE_FIX_SOURCE`. This strengthens the
version-scoped decision not to upgrade solely for GhostLock, without claiming
exact PS7330 signed-binary equivalence, runtime exploitability, or root.

Phase 5BG outputs:

- `findings/phase-5bg-ps7331-source-binary-semantic.md`
- `findings/phase-5bg-evidence-index.md`
- `tools/scripts/compare_phase5bg_ps7331_semantics.py`
- `artifacts/phase5/ps7331-source-binary-semantic-20260804-01/`

## Phase 5BH status

The official Amazon update page was checked against the preserved PS7331 OTA.
The page lists Fire HD 10 (11th Generation) at Fire OS 7.3.3.1 and resolves to
the same PS7331 archive filename; HTTP content length matches the local file.
This confirms the package as a legitimate general security A/B candidate, not
as a demonstrated GhostLock fix. Its updater scope remains a full-block update
touching system, vendor, boot and additional boot-chain/firmware members. No
OTA, reboot or device mutation was performed.

Phase 5BH outputs:

- `findings/phase-5bh-ps7331-official-ota-source.md`
- `findings/phase-5bh-evidence-index.md`
- `artifacts/phase5/ps7331-official-update-source-20260804-01/`

## Phase 5BI status

Phase 5BI performed a host-only recheck of public MTK routes and the PS7331
upgrade candidate. The pinned KoCleo `mtk-su64` LFS object matches the exact
payload already tested on the device; that route remains failed at critical
initialization step 3 and was not repeated. The reviewed public MTK material
does not provide an exact KFTRWI/trona/MT8183 Android 9 profile.

The official PS7331 OTA remains useful for a general security-update A/B study,
but the source/Image semantic comparison does not demonstrate a GhostLock fix.
The package is a full-block update touching system, vendor, boot and additional
boot-chain/firmware members, so the standalone boot image is not treated as an
equivalent upgrade. No OTA, reboot, boot-chain operation or device mutation was
performed; the device remains PS7330.4104N.

Phase 5BI outputs:

- `findings/phase-5bi-mtk-public-route-recheck.md`
- `findings/phase-5bi-evidence-index.md`
- `artifacts/phase5/mtk-public-route-recheck-20260804-01/`

## Phase 5BJ status

Phase 5BJ performed a host-only comparison of the upstream GhostLock fix marker
against the preserved Fire source inputs. Both the PS7330 source family and the
PS7331 build-selected MT8183 source retain the pre-fix `current->pi_blocked_on`
cleanup and `current` chain-walk argument. The fixed reference uses
`waiter->task`. This strengthens the conclusion that PS7331 is not a demonstrated
GhostLock remediation.

A new read-only device snapshot confirmed the device remains KFTRWI/trona/MT8183,
PS7330.4104N, green verified boot, SELinux Enforcing, shell UID 2000, and Fire
Launcher as HOME. No exploit, root, bootloader, OTA, reboot or partition write
was performed.

Phase 5BJ outputs:

- `findings/phase-5bj-ghostlock-fix-application.md`
- `findings/phase-5bj-evidence-index.md`
- `tools/scripts/compare_phase5bj_ghostlock_fix.py`
- `artifacts/phase5/phase5bj-ghostlock-fix-application-20260804-01/`
- `adb/phase5/PHASE5BJ-DEVICE-READONLY-20260804-01/`

## Phase 5BK status

Phase 5BK compared preserved PS7330 device properties with the extracted
official PS7331 OTA build metadata. The security patch level advances from
2024-02-01 to 2024-08-01 while the product remains `trona`. PS7331 is therefore
a credible general security-update A/B candidate, but Phase 5BJ still finds its
rtmutex function marker pre-fix for GhostLock. No OTA or device mutation was
performed.

Phase 5BK outputs:

- `findings/phase-5bk-ps7331-security-delta.md`
- `findings/phase-5bk-evidence-index.md`
- `output/tables/phase5bk-security-delta.csv`
- `tools/scripts/compare_phase5bk_security_delta.py`
- `artifacts/phase5/phase5bk-security-delta-20260804-02/`

## Phase 5BL status

Phase 5BL captured the exact PS7330 runtime gates relevant to a safe GhostLock
applicability review. The serial-qualified read-only capture confirms Linux
4.4.146+, Android 9, PS7330.4104N, SELinux Enforcing and shell UID 2000. Shell
cannot read `/proc/kallsyms` or most selected kernel sysctls. ION and CMDQ node
metadata was listed only; no node was opened and no ioctl was sent. No futex PI
trigger, exploit, reboot, OTA or device mutation was performed.

Phase 5BL outputs:

- `findings/phase-5bl-futex-runtime-gates.md`
- `findings/phase-5bl-evidence-index.md`
- `tools/scripts/analyze_phase5bl_futex_gates.py`
- `adb/phase5/PHASE5BL-FUTEX-GATES-20260804-01/`
- `artifacts/phase5/phase5bl-futex-gates-analysis-20260804-01/`
- `output/tables/phase5bl-runtime-gates.csv`

## Phase 5BM status

Phase 5BM built a host-only provenance ledger for exact PS7330 GhostLock binary
evidence. It confirms exact PS7330 runtime/source evidence but no verified exact
PS7330 signed boot/vmlinux or complete preloader/LK/recovery set in the
workspace. The complete local OTA and boot image are PS7331 and remain
`VERSION_MISMATCH`; the installed PS7330 boot read probe returned
`Permission denied`. No research files were deleted and no device operation was
run.

Phase 5BM outputs:

- `findings/phase-5bm-ps7330-artifact-provenance.md`
- `findings/phase-5bm-evidence-index.md`
- `tools/scripts/build_phase5bm_artifact_ledger.py`
- `artifacts/phase5/phase5bm-artifact-ledger-20260804-01/`

## Phase 5BO status

Phase 5BO verified the complete official PS7330 source archive and extracted
the actual `mt8183/4.4` build-selected kernel members. The exact PS7330 and
PS7331 `rtmutex.c`/`futex.c` source members are byte-identical and retain the
pre-fix GhostLock marker. No device operation, exploit, upgrade, or partition
mutation was run.

Phase 5BO outputs:

- `findings/phase-5bo-ps7330-full-source-build-path.md`
- `findings/phase-5bo-evidence-index.md`
- `tools/scripts/extract_phase5_ps7330_nested_members.py`
- `artifacts/phase5/ps7330-full-source-members-20260804-01/`
- `artifacts/phase5/phase5bo-exact-build-source-marker-20260804-01/`
- `adb/phase5/PHASE5BO-DEVICE-POSTCHECK-20260804-01/`

## Phase 5BP status

Phase 5BP preserved and analyzed the PS7330 kernel build scripts from the
official source archive. The exact build-selected path is
`kernel/mediatek/mt8183/4.4` with `trona_defconfig` and `arm64`; the scripts
reference the AOSP GCC prebuilt branch `llvm-r383902b` and recommend Clang
6.0.2/4691093. No visible patch, overlay, or signing command appears in the
two scripts. This is source/build provenance only, not signed-binary proof.
The scripts were not executed and the device was not modified.

Phase 5BP outputs:

- `findings/phase-5bp-ps7330-build-script-analysis.md`
- `findings/phase-5bp-evidence-index.md`
- `tools/scripts/analyze_phase5bp_build_scripts.py`
- `output/tables/phase5bp-build-script-controls.csv`
- `artifacts/phase5/ps7330-build-scripts-20260804-01/`

## Phase 5BQ status

Phase 5BQ refreshed the GhostLock and public MTK-route boundary with a new
serial-qualified, read-only device postcheck. The device remains PS7330.4104N
with the 2024-02-01 patch, ADB `device`, and Fire Launcher as HOME. Public
`mtk-easy-su` and LauncherHijack heads were pinned; no exact
KFTRWI/trona/MT8183 implementation was found in the reviewed route, and no
unknown APK was installed. Exact PS7330 source and inspected PS7331
source/Image evidence remain pre-fix-consistent for GhostLock. No exploit,
root, reboot, OTA, fastboot, boot write, ioctl, or partition operation was
performed.

Phase 5BQ outputs:

- `findings/phase-5bq-ghostlock-next-verdict.md`
- `findings/phase-5bq-evidence-index.md`
- `output/tables/phase5bq-route-matrix.csv`
- `adb/phase5/PHASE5BQ-DEVICE-POSTCHECK-20260804-01/`
- `artifacts/phase5/phase5bq-public-route-review-20260804-01/`

## Phase 5BR status

Phase 5BR ran a bounded public search for an exact
PS7330.4104N/KFTRWI/trona signed boot, Image, or vmlinux artifact. No matching
binary appeared in the returned results; this remains a bounded search miss,
not a global nonexistence proof. The device and boot-chain state were not
changed. PS7330 boot read remains denied and local PS7331 boot evidence remains
version-mismatched.

Phase 5BR outputs:

- `findings/phase-5br-exact-artifact-search.md`
- `findings/phase-5br-evidence-index.md`
- `artifacts/phase5/phase5br-exact-artifact-search-20260804-01/`

## Phase 5BS status

Phase 5BS is PS7331-only. It rechecked the exact `mt8183/4.4` source and
verified the preserved PS7331 boot-image hash, sanitized Image markers, source
classification, fixed-reference classification, and prior source-to-Image
comparison. All checks pass and remain pre-fix-consistent for GhostLock. This
does not prove runtime exploitability or root. No ELF/Image execution, ADB,
fastboot, OTA, exploit, or device operation was performed.

Phase 5BS outputs:

- `findings/phase-5bs-ps7331-ghostlock-verdict.md`
- `findings/phase-5bs-evidence-index.md`
- `tools/scripts/verify_phase5bs_ps7331_ghostlock_evidence.py`
- `artifacts/phase5/phase5bs-ps7331-source-semantic-recheck-20260804-01/`
- `artifacts/phase5/phase5bs-ps7331-evidence-verification-20260804-01/`

## Phase 5BN status

Phase 5BN independently rechecked the GhostLock `remove_waiter()` markers and
revalidated the official PS7330/PS7331 source archive headers. Both preserved
source families remain classified as pre-fix; the fixed reference uses
`waiter->task`. No device I/O, exploit, upgrade, bootloader operation, or
partition mutation was run.

Phase 5BN outputs:

- `findings/phase-5bn-ghostlock-current-verdict.md`
- `findings/phase-5bn-evidence-index.md`
- `artifacts/phase5/phase5bn-ghostlock-marker-recheck-20260804-01/`

## Phase 5BT status

Phase 5BT is PS7331-only and validates the complete official source archive
already downloaded to the workspace. The local archive size matches the
official Content-Length, its MD5 matches the preserved S3 ETag, and its
SHA-256 is `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`.

Top-level build scripts from the same archive select
`kernel/mediatek/mt8183/4.4`, `trona_defconfig`, and `arm64`. The extracted
build-selected source retains the pre-fix `current->pi_blocked_on` cleanup in
`remove_waiter()` and the paired futex PI proxy path. The existing sanitized
PS7331 Image review and host-only verifier remain pre-fix-consistent. The local
path inventory found four named Mali hrtimer patches and no named GhostLock
patch; absence of a path name is not proof against release-CI transformations.

Final Phase 5BT boundary: **static PS7331 pre-fix evidence is confirmed;
runtime exploitability and root are not proven**. No source or build script was
executed, and no exploit, OTA, fastboot, boot write, partition write, or device
mutation was performed. PS7331 is not recommended solely as a GhostLock fix.

Phase 5BT outputs:

- `findings/phase-5bt-ps7331-full-source-audit.md`
- `findings/phase-5bt-evidence-index.md`
- `tools/scripts/index_phase5_ps7331_local_nested_build_inputs.sh`
- `tools/scripts/extract_phase5_ps7331_nested_members.py`
- `tools/scripts/extract_phase5_ps7331_outer_members.py`
- `artifacts/phase5/phase5bt-ps7331-source-archive-validation-20260804-01/`
- `artifacts/phase5/ps7331-local-nested-build-index-20260804-02/`
- `artifacts/phase5/ps7331-full-source-members-20260804-01/`
- `artifacts/phase5/ps7331-top-level-build-members-20260804-01/`
- `artifacts/phase5/phase5bt-build-script-controls-20260804-01.csv`
- `output/tables/phase5bt-ps7331-source-binary-status.csv`
- `output/call-graphs/phase5bt-ghostlock-source-path.mmd`

## Phase 5BU status

Phase 5BU added the PS7331 boot-embedded `IKCONFIG` to the GhostLock
cross-check. It confirms `CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y`,
`CONFIG_PREEMPT=y`, ARM64 VA39/4K, `CONFIG_RANDOMIZE_BASE=y`, and
`CONFIG_KALLSYMS=y`. The selected `futex.c` still exposes the PI requeue and
proxy-lock path, and the sanitized Image still contains the corresponding
function and pre-fix cleanup markers.

The updated result is a **source/config/Image reachability candidate** with
high confidence, not a live exploit or root result. Runtime trigger,
memory-corruption effect, and privilege transition remain unverified. No
futex race, kernel memory access, exploit payload, ADB mutation, bootloader
operation, or partition write was performed.

Phase 5BU outputs:

- `findings/phase-5bu-ps7331-embedded-config-reachability.md`
- `findings/phase-5bu-evidence-index.md`
- `artifacts/phase5/phase5bu-ps7331-embedded-config-reachability-20260804-01/`
- `output/tables/phase5bu-ps7331-config-reachability.csv`
- `output/call-graphs/phase5bu-ps7331-reachability.mmd`

## Phase 5BV status

Phase 5BV adds a host-only semantic regression model for the proxy-waiter
cleanup mismatch. The model reproduces the distinction between
`current->pi_blocked_on` and `waiter->task->pi_blocked_on`, passes four unit
tests, and includes a same-task control. It does not execute kernel code or
claim a live exploit, root, or privilege transition.

Phase 5BV outputs:

- `findings/phase-5bv-ghostlock-semantic-model.md`
- `findings/phase-5bv-evidence-index.md`
- `tools/scripts/model_phase5bv_ghostlock_semantics.py`
- `tests/test_phase5bv_ghostlock_semantics.py`
- `artifacts/phase5/phase5bv-ghostlock-semantic-model-20260804-01/`

## Phase 5BW status

Phase 5BW cross-checks the PS7331 build-selected source against the public
GhostLock fix semantics. PS7331 remains pre-fix: `remove_waiter()` uses
`current->pi_blocked_on` and `current` for priority-chain adjustment, while the
fixed reference uses `waiter->task`. The reproducible host-only checker reports
`PS7331_SOURCE_MATCHES_PRE_FIX_SEMANTICS`.

This confirms static source/Image exposure status only. It does not establish a
live race, memory corruption, kernel control, root, or privilege transition.
No device I/O, exploit, unknown ioctl, bootloader, or partition operation was
performed.

Phase 5BW outputs:

- `findings/phase-5bw-ghostlock-fix-applicability.md`
- `findings/phase-5bw-evidence-index.md`
- `tools/scripts/compare_phase5bw_ghostlock_fix.py`
- `tests/test_phase5bw_ghostlock_fix.py`
- `artifacts/phase5/phase5bw-ghostlock-fix-applicability-20260804-01/`

## Phase 5BX status

Phase 5BX re-ran the host-only reachability analyzer against the build-selected
PS7331 source from the complete 7.3.3.1 archive. It confirms the source chain
`FUTEX_*_REQUEUE_PI` → `futex_requeue()` →
`rt_mutex_start_proxy_lock(..., this->task)` → `remove_waiter()` and the
pre-fix `current->pi_blocked_on` cleanup. The classification is
`SOURCE_AND_CONFIG_REACHABILITY_CANDIDATE`; runtime exploitability and root
remain unproven.

Phase 5BX outputs:

- `findings/phase-5bx-ps7331-ghostlock-path-audit.md`
- `findings/phase-5bx-evidence-index.md`
- `output/tables/phase5bx-ghostlock-path.csv`
- `output/call-graphs/phase5bx-ghostlock-path.mmd`
- `artifacts/phase5/phase5bx-ps7331-exact-path-audit-20260804-01/`

## Phase 5BY status

Phase 5BY adds the public follow-up fix review for CVE-2026-53163. The selected
PS7331 source returns early from `task_blocks_on_rt_mutex()` before assigning
`waiter->task`, and its proxy wrapper conditionally calls `remove_waiter()`.
PS7331 is still pre-primary-fix; the Phase 5BW v6.1.175 reference is now
explicitly treated as a primary-fix semantic reference, not a complete modern
remediation reference. The host-only checker reports
`PRE_PRIMARY_FIX_WITH_EARLY_RETURN_GUARD_REVIEW`.

Phase 5BY outputs:

- `findings/phase-5by-ghostlock-fix-chain.md`
- `findings/phase-5by-evidence-index.md`
- `output/tables/phase5by-ghostlock-fix-chain.csv`
- `output/call-graphs/phase5by-ghostlock-fix-chain.mmd`
- `tools/scripts/analyze_phase5by_ghostlock_fix_chain.py`
- `tests/test_phase5by_ghostlock_fix_chain.py`
- `artifacts/phase5/phase5by-ps7331-ghostlock-fix-chain-20260804-02/`

## Phase 5BZ status

Phase 5BZ is PS7331-only and host-only. It verifies the three preserved,
address-sanitized Image markers for the primary GhostLock pre-fix relationship
against the exact source control flow and extracted IKCONFIG. The primary
pre-fix marker set is confirmed. The follow-up guard is explicitly unresolved at
binary level because raw branch/return disassembly and the reconstructed ELF are
not retained; absence of that evidence is not a claim about the guard itself.

No device I/O, futex trigger, exploit, root attempt, boot image write,
bootloader operation, or partition mutation was performed.

Phase 5BZ outputs:

- `findings/phase-5bz-ps7331-binary-evidence-boundary.md`
- `findings/phase-5bz-evidence-index.md`
- `tools/scripts/analyze_phase5bz_ps7331_binary_boundary.py`
- `tests/test_phase5bz_ps7331_binary_boundary.py`
- `artifacts/phase5/phase5bz-ps7331-binary-evidence-boundary-20260804-01/`
- `output/tables/phase5bz-ps7331-binary-evidence.csv`
- `output/tables/phase5bz-ps7331-config-observations.csv`
- `output/call-graphs/phase5bz-ps7331-fix-boundary.mmd`

## Phase 5CA status

Phase 5CA maps the public CVE-2026-53163 follow-up patch onto the exact PS7331
4.4 source. The upstream requirements are independent: guard
`remove_waiter()` when the waiter is not enqueued, and use a negative-only
wrapper return check. PS7331 has neither shape in the inspected source: early
`-EDEADLK` is at line 973 before `waiter->task` assignment at line 977, while
the wrapper keeps `if (unlikely(ret))` at line 1683. The futex PI requeue path
calls the proxy API at lines 1963–1965.

This is source-level applicability evidence, not live exploit/root proof. No
device I/O, futex trigger, image write, bootloader operation, or partition
mutation was performed.

Phase 5CA outputs:

- `findings/phase-5ca-ps7331-followup-patch-mapping.md`
- `findings/phase-5ca-evidence-index.md`
- `tools/scripts/analyze_phase5ca_ps7331_followup_patch.py`
- `tests/test_phase5ca_ps7331_followup_patch.py`
- `artifacts/phase5/phase5ca-ps7331-followup-patch-mapping-20260804-01/`
- `output/tables/phase5ca-followup-patch-mapping.csv`
- `output/call-graphs/phase5ca-ghostlock-fix-chain.mmd`

## Phase 5CB status

Phase 5CB audits the exact PS7331 futex syscall-to-PI-requeue entry path. It
confirms the source chain from `SYSCALL_DEFINE6(futex)` through
`do_futex()`/`futex_requeue()` to `rt_mutex_start_proxy_lock()`, while finding no
direct capability/security hook in the bounded scoped functions. The result is
`SYSCALL_TO_PI_REQUEUE_PROXY_PATH_PRESENT`; Android userspace policy, runtime
reachability and exploitability remain unresolved. No device syscall or futex
trigger was executed.

Phase 5CB outputs:

- `findings/phase-5cb-ps7331-futex-entry-audit.md`
- `findings/phase-5cb-evidence-index.md`
- `tools/scripts/audit_phase5cb_ps7331_futex_entry.py`
- `tests/test_phase5cb_ps7331_futex_entry.py`
- `artifacts/phase5/phase5cb-ps7331-futex-entry-audit-20260804-01/`
- `output/tables/phase5cb-futex-entry-gate.csv`
- `output/call-graphs/phase5cb-futex-entry-path.mmd`

## Phase 5CC status

Phase 5CC audits the source-level task identity dataflow. It confirms that
`futex_q->task` is bound to the waiting `current`, that the PI requeue path has
a separate `rt_mutex_waiter`, that `futex_requeue()` passes `this->task` as an
explicit proxy parameter, and that PS7331 `remove_waiter()` clears
`current->pi_blocked_on`. No direct `current == task` assertion was observed in
the bounded proxy/task/cleanup functions. This establishes interface-level
identity separation, not a live scheduler mismatch or race.

Phase 5CC outputs:

- `findings/phase-5cc-ps7331-identity-invariant.md`
- `findings/phase-5cc-evidence-index.md`
- `tools/scripts/audit_phase5cc_ps7331_identity_invariant.py`
- `tests/test_phase5cc_ps7331_identity_invariant.py`
- `artifacts/phase5/phase5cc-ps7331-identity-invariant-20260804-01/`
- `output/tables/phase5cc-identity-invariant.csv`
- `output/call-graphs/phase5cc-identity-invariant.mmd`

## Phase 5CD status

Phase 5CD maps source-level cleanup effects and candidate later consumers. It
confirms that `remove_waiter()` does not directly clear `waiter->task` or
`waiter->lock`, while its helper calls can conditionally clear lock and PI-tree
nodes. It records candidate readers such as `task_blocked_on_lock()`,
`rt_mutex_adjust_prio_chain()` and `rt_mutex_adjust_pi()`, plus a possible state
transition in `try_to_take_rt_mutex()`. These are static references only:
runtime persistence, second consumption, crash, controlled memory effect and
root remain unproven. No race or device operation was performed.

Phase 5CD outputs:

- `findings/phase-5cd-ps7331-cleanup-consumers.md`
- `findings/phase-5cd-evidence-index.md`
- `tools/scripts/audit_phase5cd_ps7331_cleanup_consumers.py`
- `tests/test_phase5cd_ps7331_cleanup_consumers.py`
- `artifacts/phase5/phase5cd-ps7331-cleanup-consumers-20260804-01/`
- `output/tables/phase5cd-cleanup-consumers.csv`
- `output/call-graphs/phase5cd-cleanup-consumers.mmd`

## Phase 5CE status

Phase 5CE reviews the public `ghostlock-emerald` repository as a target-profile
reference only. Its README/Makefile/source metadata target Poco M6 Pro/MT6789,
Android 16 and kernel 6.12.30, with hard-coded build/layout data and root/
physical-RW-related components. Fire PS7331 is Android 9/MT8183/4.4-family and
has no shared target profile. The Emerald binary was not cloned, built, installed
or executed.

Phase 5CE outputs:

- `findings/phase-5ce-ghostlock-emerald-compatibility.md`
- `findings/phase-5ce-evidence-index.md`
- `output/tables/phase5ce-ghostlock-emerald-compatibility.csv`
- `artifacts/phase5/phase5ce-ghostlock-emerald-compatibility-20260804-01/`

## Phase 5CF status

Phase 5CF captured a new explicit-serial read-only device baseline. The actual
connected Fire tablet reports fingerprint `PS7330.4104N`, not PS7331, with
MT8183, verified boot green, flash-locked property `1`, SELinux Enforcing, and
Fire Launcher under `/system/priv-app`. PS7331 source/Image evidence therefore
remains offline applicability evidence until the device actually runs that build.
No GhostLock POC, root attempt, bootloader operation, or partition mutation was
performed.

Phase 5CF outputs:

- `findings/phase-5cf-device-version-boundary.md`
- `findings/phase-5cf-evidence-index.md`
- `output/tables/phase5cf-device-version-boundary.csv`
- `adb/phase5/PHASE5CF-READONLY-20260804-01/` (raw local evidence)

## Phase 5CG status

Phase 5CG models the exact PS7331 early-return and nonzero-cleanup semantics
without executing the kernel. The source evidence is pinned to the exact
futex/rtmutex files and line locations: `task_blocks_on_rt_mutex()` returns
`-EDEADLK` before assigning `waiter->task`; `rt_mutex_start_proxy_lock()` keeps
the broad `if (unlikely(ret))` cleanup gate; and `remove_waiter()` clears
`current->pi_blocked_on`. The model separately marks an identity-mismatch
residue as conditional on runtime state, so it does not promote source
semantics to a live exploit claim.

No futex trigger, race, unknown ioctl, root operation, bootloader operation,
image write or partition mutation was performed.

Phase 5CG outputs:

- `findings/phase-5cg-ps7331-cleanup-semantics-model.md`
- `findings/phase-5cg-evidence-index.md`
- `tools/scripts/model_phase5cg_ps7331_cleanup_semantics.py`
- `tests/test_model_phase5cg_ps7331_cleanup_semantics.py`
- `output/tables/phase5cg-cleanup-semantics.csv`
- `output/call-graphs/phase5cg-cleanup-semantics.mmd`
- `artifacts/phase5/phase5cg-ps7331-cleanup-semantics-20260804-01/`

## Phase 5CI status

Phase 5CI records the official Amazon manual-update instructions and the local
PS7331 package verification. The official path is desktop download → USB
Transfer files → Internal storage → Settings → Device Options → System Updates
→ Update. The local package matches `trona`, PS7331.4463N, API 28, the published
size and SHA-256, and an Amazon OTA certificate. It remains an offline artifact;
no sideload, Settings update, reboot or partition write was performed.

Phase 5CI output:

- `findings/phase-5ci-official-manual-update-procedure.md`

## Phase 5CJ status

Phase 5CJ records the actual result of applying the official Amazon PS7331 full
OTA through the native System Updates UI. The tablet now reports PS7331.4463N,
incremental `0031575863172`, security patch `2024-08-01`, Linux `4.4.146+`,
Verified Boot `green`, flash locked, and SELinux Enforcing. The OTA file was
accepted by Amazon's sideload installer and removed after installation. The
post-update resolver was temporarily OOBE because user setup was incomplete;
this is not treated as a HOME replacement result.

Phase 5CJ also records the target-profile mismatch between the public
`ghostlock-emerald` project (Poco/MT6789/Android 16/kernel 6.12.30) and Fire
PS7331 (MT8183/Android 9/kernel 4.4). No exploit binary was built or executed.

Output:

- `findings/phase-5cj-ps7331-update-and-ghostlock-boundary.md`

## Phase 5CK status

Phase 5CK captures a new PS7331 read-only futex/runtime gate snapshot. Shell has
zero capabilities in the captured process, SELinux is Enforcing, `/proc/kallsyms`
is denied, `/proc/kcore` and `/dev/kmem` are unavailable, and ION/CMDQ are only
recorded as device-node metadata. The capture did not open a device node, invoke
ioctl, trigger futex PI, change settings, reboot, or mutate package state. These
observations bound runtime visibility; they do not prove that futex/rtmutex is
absent or that GhostLock is exploitable.

Outputs:

- `findings/phase-5ck-ps7331-runtime-gates.md`
- `adb/phase5/PS7331-FUTEX-GATES-20260804-01/` (raw local evidence)

## Phase 5CL status

Phase 5CL formalizes the dynamic-validation gate: D0 source identity separation
is confirmed, while D1 runtime `waiter->task != current`, D2 wrong cleanup target,
D3 persistent consumer, and D4 controlled memory effect/root remain unobserved.
The stock PS7331 device was not used as an exploit target and no kernel
instrumentation, futex trigger, memory access, or root payload was executed.

Output:

- `findings/phase-5cl-identity-mismatch-validation-gate.md`

## Phase 5CM status

Phase 5CM captures `/proc/config.gz` and tracing mount/visibility state on the
actual PS7331 runtime. FUTEX, RT_MUTEX, seccomp, SELinux, debugfs, and kallsyms
config entries are present; ordinary shell enumeration of debugfs/tracefs is
denied. The capture is read-only and does not trigger futex, enable tracing,
open device nodes, invoke ioctl, or mutate the device.

Outputs:

- `findings/phase-5cm-ps7331-config-and-tracing-boundary.md`
- `tools/scripts/capture_phase5cm_config_gates.sh`
- `adb/phase5/PS7331-CONFIG-GATES-20260804-01/` (raw local evidence)

## Phase 5CN status

Phase 5CN separates the PS7331 futex/rtmutex feature gate from the dynamic
identity-mismatch gate. The build-selected source proves the PI command gate,
the proxy task wiring, and the `remove_waiter()` `current` cleanup semantics.
The actual PS7331 runtime config proves `CONFIG_FUTEX=y` and
`CONFIG_RT_MUTEXES=y`, but the available source subset does not include the
complete ARM64 futex header/Kconfig expansion. Therefore the final
`CONFIG_HAVE_FUTEX_CMPXCHG` state and the direct runtime value of
`futex_cmpxchg_enabled` remain unobserved.

Most importantly, no evidence in this phase observes
`waiter->task != current`. D0 remains confirmed; D1, D2, D3 and D4 remain
unobserved or unproven. No futex trigger, race, kernel instrumentation, ioctl,
kernel memory access, root payload or device mutation was performed.

Outputs:

- `findings/phase-5cn-futex-feature-gate.md`
- `findings/phase-5cn-evidence-index.md`
- `output/tables/phase5cn-futex-feature-gate.csv`
- `output/call-graphs/phase5cn-futex-feature-gate.mmd`

## Phase 5CO status

Phase 5CO extracts the official PS7331 ARM64 futex header and Kconfig members
that were missing from the earlier selected-source subset. It confirms, at
source scope, the `HAVE_FUTEX_CMPXCHG` feature definition, the MT8183 ARM64
atomic cmpxchg implementation and its `-EFAULT` invalid-address behavior. The
MT8183 ARM64 platform block has no direct `select HAVE_FUTEX_CMPXCHG`; the
MediaTek select found by the literal search belongs to the separate MT8167 ARM
block. The boot-embedded IKCONFIG and existing device capture confirm FUTEX and
RT_MUTEX support, so runtime PI-gate enablement is strongly supported but not
directly observed.

Phase 5CO does not observe `waiter->task != current`, post-cleanup invariant
damage, a memory-safety primitive or privilege escalation. It is host-only and
read-only; no futex PI opcode, race trigger, kernel instrumentation, ioctl,
kernel memory access, exploit payload or device mutation was performed.

Outputs:

- `findings/phase-5co-ps7331-futex-config-resolution.md`
- `findings/phase-5co-evidence-index.md`
- `output/tables/phase5co-futex-config-resolution.csv`
- `output/call-graphs/phase5co-futex-config-resolution.mmd`
- `tools/scripts/extract_phase5cn_futex_arch_members.py`
- `tools/scripts/search_phase5cn_source_literals.py`

## Phase 5CP status

Phase 5CP confirms the PS7331 source-context distinction behind the identity
question: `queue_me()` stores the waiting thread in `q->task`, the requeue path
passes that stored task to the proxy API, and `remove_waiter()` still cleans the
implicit caller `current`. The fixed reference explicitly documents that
proxy-lock invocation can have `waiter::task != current` and uses the waiter task
for cleanup. This is a stronger source/dataflow result than merely observing two
names in different functions, but it remains source scope.

No stock-device observation shows the proxy error branch executing,
`remove_waiter()` being called, a post-cleanup invariant violation, a memory
effect or privilege gain. No futex syscall, race trigger, kernel build or device
mutation was performed.

Outputs:

- `findings/phase-5cp-ps7331-proxy-context-audit.md`
- `findings/phase-5cp-evidence-index.md`
- `output/tables/phase5cp-proxy-context.csv`
- `output/call-graphs/phase5cp-proxy-context.mmd`
- `tools/scripts/audit_phase5cp_proxy_context.py`

## Phase 5CR status

Phase 5CR captured the exact PS7331 Fire native runtime artifacts with explicit
serial `G001LT0511550CFT` using read-only ADB pulls. The installed Fire libc
contains both a generic futex wait helper and a separate PI-lock helper.
`pthread_cond_wait` and timed condition-variable variants call the generic wait
helper; the PI mutex path calls the PI-lock helper. A bounded host-side
symbol/call-edge analysis did not establish a requeue-PI caller in this libc.

This upgrades the conclusion that ordinary Fire pthread condition variables are
not a demonstrated GhostLock requeue-PI entry, while leaving other vendor
libraries/services, Fire-specific policy, runtime identity mismatch, cleanup
residue, memory effect and privilege transition open. No ELF was executed and
no futex, race, ioctl, kernel memory, payload, boot or partition operation was
performed.

Outputs:

- `findings/phase-5cr-fire-libc-futex-analysis.md`
- `findings/phase-5cr-evidence-index.md`
- `output/tables/phase5cr-fire-libc-futex.csv`
- `output/call-graphs/phase5cr-fire-libc-futex.mmd`
- `tools/scripts/capture_phase5cr_fire_native.py`
- `tools/scripts/analyze_phase5cr_fire_libc.py`

## Phase 5CQ status

Phase 5CQ audits Android 9 userspace reachability using official AOSP
references. Android 9 r61 bionic pthread condition variables use ordinary
futex wait/wake helpers and do not establish a requeue-PI caller. The AOSP UAPI
header exposes PI/requeue-PI operation names, but the AOSP reference does not
prove a Fire-specific native caller or policy allowance. Fire PS7331 runtime
identity mismatch, wrong cleanup target, later consumer, memory effect and
privilege transition remain unobserved/unproven.

The phase is host-only/read-only. It does not execute futex, create a race,
build or execute kernel code, access kernel memory, generate an address/payload,
contact a device node, or perform a root operation.

Outputs:

- `findings/phase-5cq-android9-userspace-reachability.md`
- `findings/phase-5cq-evidence-index.md`
- `output/tables/phase5cq-userspace-reachability.csv`
- `output/call-graphs/phase5cq-userspace-reachability.mmd`
- `tools/scripts/audit_phase5cq_userspace_reachability.py`

## Phase 5CS status

Phase 5CS adds a bounded, host-only scan of Fire PS7331 native artifacts that
were already pulled or listed with read-only ADB. Fire `libart.so` contains the
ART compare-requeue diagnostic and `ThreadList::SuspendAllInternal`; the
identified method reaches the libc `syscall` boundary in host disassembly.
The AOSP ART reference maps the diagnostic to ordinary compare-requeue, not a
demonstrated requeue-PI proxy operation. `libandroid_runtime.so` contains
seccomp setup references, but the Fire app policy result is not exposed. The
selected Amazon libraries do not establish a named requeue-PI caller in a
bounded scan, which is only a negative observation.

The dynamic GhostLock gates remain open: no stock-runtime observation of
`waiter->task != current`, `remove_waiter()` execution, persistent residue,
later consumer, controlled memory effect or root. No native ELF was executed;
no futex, race, ioctl, device-node, kernel-memory, payload, boot or partition
operation was performed.

Outputs:

- `findings/phase-5cs-fire-art-futex-analysis.md`
- `findings/phase-5cs-evidence-index.md`
- `output/tables/phase5cs-native-inventory.csv`
- `output/call-graphs/phase5cs-native-futex-flow.mmd`
- `tools/scripts/analyze_phase5cs_native_inventory.py`

## Phase 5CT status

Phase 5CT deepens the host-only audit of the public `ghostlock-emerald`
implementation. Its source contains a build-specific target selector,
coordinated waiter/owner/consumer PI-requeue roles, and target-specific
post-trigger memory/root stages. Fire PS7331 source confirms the matching
defect-family path, but Fire userspace requeue-PI reachability, runtime
`waiter->task != current`, cleanup residue, a later consumer, memory effect and
privilege transition remain unobserved.

The Emerald profile targets Poco M6 Pro/MT6789/Android 16/6.12.30; the actual
tablet is PS7331/MT8183/Android 9/4.4. This is a target-profile mismatch, not a
single-offset gap. No exploit was adapted, compiled, installed or executed and
no futex, race, kernel memory, root, boot or partition operation was performed.

Outputs:

- `findings/phase-5ct-ghostlock-architecture-audit.md`
- `findings/phase-5ct-evidence-index.md`
- `output/tables/phase5ct-ghostlock-architecture.csv`
- `output/call-graphs/phase5ct-ghostlock-architecture.mmd`
- `tools/scripts/build_phase5ct_architecture_matrix.py`

## Phase 5CU status

Phase 5CU captures the PS7331 seccomp boundary with read-only process status,
policy listings and policy pulls. `system_server`, Microsoft Launcher,
SystemUI, OTA and research APK processes report `Seccomp: 2`; `adbd` reports
`Seccomp: 0` but remains UID 2000 with zero capabilities. Selected
media/configstore service policies contain `futex: 1`, while the ordinary
app-domain filter was not recovered.

This confirms a userspace policy gate without proving whether PI requeue is
allowed or reachable. No futex operation, exploit, native payload, security
policy change or device mutation was performed.

Outputs:

- `findings/phase-5cu-ps7331-seccomp-reachability.md`
- `findings/phase-5cu-evidence-index.md`
- `output/tables/phase5cu-seccomp-reachability.csv`
- `output/call-graphs/phase5cu-seccomp-reachability.mmd`
- `adb/phase5/PHASE5CT-SECCOMP-20260804-01/`

## Phase 5CV status

Phase 5CV separates the PS7331 return-value domains around proxy cleanup.
`ret=1` from initial lock acquisition returns before cleanup;
`task_blocks_on_rt_mutex()` can return before assigning `waiter->task`; an
owner-release condition can reset a nonzero result to zero; and only the
remaining nonzero path reaches `remove_waiter()`. The futex requeue caller then
branches on positive, zero and negative proxy results.

This confirms why `if (ret)` and early-return ordering matter, but no stock
runtime error branch, identity mismatch, cleanup residue, memory effect or root
was observed. No futex trigger, race, exploit or device mutation was performed.

Outputs:

- `findings/phase-5cv-ps7331-ret-early-return-audit.md`
- `findings/phase-5cv-evidence-index.md`
- `output/tables/phase5cv-ret-early-return.csv`
- `output/call-graphs/phase5cv-ret-early-return.mmd`

## Phase 5CW status

Phase 5CW compares the exact PS7331 `rtmutex.c` with a preserved upstream
primary-fix reference and records the upstream follow-up guard separately.
The exact PS7331 source retains `current->pi_blocked_on = NULL` in
`remove_waiter()` and `if (unlikely(ret)) remove_waiter(lock, waiter)` in the
proxy wrapper. Its self-deadlock `-EDEADLK` return precedes `waiter->task =
task`. The upstream primary fix uses `waiter->task` for PI cleanup and chain
adjustment; the later follow-up adds an un-enqueued waiter guard and changes
the wrapper test to `ret < 0`.

This is a source-level confirmation only. A stock PS7331 runtime identity
mismatch, cleanup residue, later consumer, controlled memory effect or root
has not been observed. No futex trigger, race, exploit, kernel-memory,
payload, boot or partition operation was performed.

Outputs:

- `findings/phase-5cw-upstream-followup-fix-diff.md`
- `findings/phase-5cw-evidence-index.md`
- `output/tables/phase5cw-upstream-fix-diff.csv`
- `output/call-graphs/phase5cw-upstream-fix-chain.mmd`
- `tools/scripts/compare_phase5cw_upstream_followup.py`
- `tests/test_phase5cw_upstream_followup.py`

## Phase 5CY status

Phase 5CY records a read-only PS7331 runtime observation boundary. The exact
device is PS7331/MT8183/Linux 4.4.146+ with enforcing SELinux and green
verified boot. The captured kernel config enables futex, rtmutex and generic
trace infrastructure, but no futex tracepoint is exposed to shell;
`/proc/kallsyms` is denied, `/proc/kcore` and `/dev/kmem` are absent, and
`perf_event_paranoid=3`. `system_server`, SystemUI, Microsoft Launcher and OTA
report Seccomp 2; `adbd` remains UID 2000 with zero effective capabilities.

The read-only HOME capture found OOBE/test residue (`user_setup_complete=0`,
OOBE resolver and Phase 4 alias foreground). Fire Launcher was explicitly
started to restore only the foreground, and the post-capture confirms it is
resumed/focused while the resolver state was not modified.

This provides stronger evidence for the stock observation boundary, not a
GhostLock dynamic mismatch. No futex/race trigger, trace enable, kernel memory,
root payload, reboot, package/settings mutation or partition operation was
performed.

Outputs:

- `findings/phase-5cy-ps7331-runtime-observation-boundary.md`
- `findings/phase-5cy-evidence-index.md`
- `output/tables/phase5cy-runtime-boundary.csv`
- `tools/scripts/capture_phase5cy_runtime_boundary.sh`
- `tools/scripts/capture_phase5cy_home_boundary.sh`
- local raw captures under `adb/phase5/PHASE5CY-*`

## Phase 5DA status

Phase 5DA completed a full host-side extraction of the official
`Fire_HD10-7.3.3.1-20250617.tar.bz2` archive. The original archive remains
unchanged and hashes to
`02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`.
`platform.tar` and `fireos.tar` were separately extracted into new local
directories. The Amazon build recipe selects the MT8183 4.4 kernel,
`trona_defconfig`, arm64, and the four trona DTBs. The exact MT8183 futex and
rtmutex source is now available in the extracted tree and matches the source
paths used by the previous Phase 5 static analysis.

The local source index covers 173,535 files and hashes 1,094 focus files. The
multi-gigabyte source tree is local-only; the repository publishes the
reproducible indexer, provenance report, evidence index, and summary table.
The source package contains neither Fire Launcher implementation source nor a
complete Android `frameworks/`/system-server tree, so it cannot by itself
resolve the remaining proprietary framework questions. No source was built or
executed, and no device, boot, partition, futex, exploit, or root operation
was performed.

Outputs:

- `findings/phase-5da-ps7331-source-tree-index.md`
- `findings/phase-5da-evidence-index.md`
- `output/tables/phase5da-source-tree-summary.csv`
- `tools/scripts/index_phase5da_source_tree.py`
- local index under `artifacts/phase5/phase5da-ps7331-source-tree-index-20260804-01/`

## Phase 5CZ status

Phase 5CZ records the futex selftest provenance boundary. The PS7331 source
contains functional requeue-PI selftests, and the kernel Makefile describes a
root-run workflow after a kernel build/install/boot. A bounded read-only search
of standard device paths found no matching selftest binary. No selftest was
copied, built, or executed, and the stock runtime identity mismatch remains
unobserved.

Outputs:

- `findings/phase-5cz-selftest-provenance.md`
- `findings/phase-5cz-evidence-index.md`
- `output/tables/phase5cz-selftest-provenance.csv`
- `tools/scripts/capture_phase5cz_selftest_presence.sh`
- local raw capture under `adb/phase5/PHASE5CZ-SELFTEST-PRESENCE-20260804-01/`

## Phase 5DB status

Phase 5DB records a fresh exact-target match for the connected tablet. The
device is `KFTRWI/trona/MT8183` on `PS7331.4463N/0031575863172`, and its
fingerprint, incremental, product, and security patch all match the official
PS7331 full OTA metadata. The exact build-selected MT8183 source and preserved
PS7331 boot Image markers are pre-fix-consistent for the GhostLock current-task
cleanup semantics.

This is a provenance/static result only. Runtime `waiter->task != current`,
wrong cleanup residue, a later consumer, a memory effect, and root remain
unobserved/unproven. No futex trigger, exploit, payload, kernel memory, boot,
partition, or device-state mutation was performed.

Outputs:

- `findings/phase-5db-ps7331-exact-target-ghostlock-chain.md`
- `findings/phase-5db-evidence-index.md`
- `output/tables/phase5db-ghostlock-gates.csv`
- `tools/scripts/capture_phase5db_exact_ps7331_match.sh`
- `tools/scripts/verify_phase5db_ps7331_exact_chain.py`
- local exact-target capture under `adb/phase5/PS7331-EXACT-MATCH-20260804-01/`

## Phase 5DC / Phase 6A boundary

Phase 5DC completed a host-only caller-role audit over the full locally
extracted PS7331 source roots and the preserved Fire native scan inputs. It
found 231 matching source rows in 34 files: 60 kernel implementation rows,
135 futex selftest rows, and 36 UAPI/documentation rows. No source row was a
Fire framework/app userspace candidate, and the bounded native scan found zero
named requeue-PI rows. The exact MT8183 kernel path and selftest wrappers remain
confirmed in their respective scopes; an installed Fire userspace caller is
not established.

This is not runtime validation. `waiter->task != current`, cleanup residue, a
later consumer, memory effect and privilege transition remain unobserved. No
futex trigger, race, native execution, kernel memory operation, payload, boot
write or partition operation was performed.

Outputs:

- `findings/phase-5dc-ps7331-requeue-pi-caller-audit.md`
- `findings/phase-6a-runtime-verification-boundary.md`
- `output/tables/phase5dc-requeue-pi-callers.csv`
- `output/call-graphs/phase5dc-userspace-boundary.mmd`
- `tools/scripts/audit_phase5dc_requeue_pi_callers.py`
- local audit artifact under `artifacts/phase5/phase5dc-requeue-pi-caller-audit-20260804-05/`

Phase 6A is currently limited to a safe observation schema and lab-only model.
It does not authorize a stock-device futex/race trigger; any isolated
instrumented environment result must be labeled `LAB_ONLY`.

## Phase 5DF status

Phase 5DF extracted the PS7331 futex dispatch and proxy cleanup boundary from
the exact MT8183 source. The source contains the requeue-PI syscall dispatch,
passes `this->rt_waiter` and `this->task` into the proxy lock API, and retains
the pre-fix cleanup landmarks. This remains source-only evidence; it does not
establish a shipped caller or stock runtime mismatch.

Outputs:

- `findings/phase-5df-futex-dispatch-boundary.md`
- `findings/phase-5df-evidence-index.md`
- `output/tables/phase5df-futex-dispatch.csv`
- `tools/scripts/audit_phase5df_futex_dispatch_boundary.py`
- local audit under `artifacts/phase5/phase5df-futex-dispatch-boundary-20260804-01/`

## Phase 5DD status

Phase 5DD extended the native caller audit to 16 preserved Fire ELF inputs.
No named `FUTEX_*_REQUEUE_PI` marker was found. Five files show ordinary
futex/PI-helper or ART compare-requeue markers, and one file shows only a
generic syscall boundary. No result establishes a shipped Fire requeue-PI
caller or stock runtime execution.

Outputs:

- `findings/phase-5dd-native-futex-surface.md`
- `findings/phase-5dd-evidence-index.md`
- `output/tables/phase5dd-native-futex-summary.csv`
- `tools/scripts/audit_phase5dd_native_futex_surface.py`
- local inventory under `artifacts/phase5/phase5dd-native-futex-surface-20260804-03/`

## Phase 5DI status

Phase 5DI added the preserved services.odex and fosservices.odex to the
native futex surface audit. Both are AArch64 ELF inputs with no visible
futex/rtmutex/requeue-PI or generic syscall marker. This remains bounded
negative evidence; runtime and stripped/indirect callers are unresolved.

Outputs:

- findings/phase-5di-additional-odex-futex-surface.md
- findings/phase-5di-evidence-index.md
- local inventory under artifacts/phase5/phase5di-additional-odex-futex-surface-20260804-01/

## Phase 5DH status

Phase 5DH compared the Emerald reference prerequisites with the exact PS7331
IKCONFIG and source. FUTEX, RT_MUTEXES, CONFIGFS_FS, SLUB, SECCOMP and
RANDOMIZE_BASE are enabled; CONFIG_USERFAULTFD is explicitly not set. This
does not establish a usable kernel primitive or root portability.

Outputs:

- findings/phase-5dh-ps7331-reference-surface-gates.md
- findings/phase-5dh-evidence-index.md
- output/tables/phase5dh-reference-surface-matrix.csv
- tools/scripts/audit_phase5dh_ps7331_reference_surfaces.py
- local audit under artifacts/phase5/phase5dh-ps7331-reference-surface-gates-20260804-01/

## Phase 5DG status

Phase 5DG audited the public datfooldive/ghostlock-emerald source at commit
ebb355d302629a034d0959e5e579496559e8f84e. The reference has named
PI/requeue userspace orchestration and later target-specific memory/credential
stages, but its MT6789/Linux 6.12/Android 16 target is not PS7331. No source
was compiled or executed and no offsets or payload were reused.

Outputs:

- findings/phase-5dg-ghostlock-emerald-architecture.md
- findings/phase-5dg-evidence-index.md
- tools/scripts/audit_ghostlock_reference_architecture.py
- local audit under artifacts/phase5/phase5dg-ghostlock-emerald-architecture-20260804-01/

## Phase 5DE status

Phase 5DE searched the non-kernel PS7331 source roots. It found 26 rows in two
external GLib files, including eight direct `syscall(__NR_futex, ...)` rows,
all using ordinary `FUTEX_WAIT`/`FUTEX_WAKE`. It found zero PI or requeue-PI
userspace source rows. This strengthens the ordinary-versus-proxy distinction,
but remains build-input evidence rather than stock runtime proof.

Outputs:

- `findings/phase-5de-userspace-futex-source.md`
- `findings/phase-5de-evidence-index.md`
- `output/tables/phase5de-userspace-futex-summary.csv`
- `tools/scripts/audit_phase5de_userspace_futex_source.py`
- local audit under `artifacts/phase5/phase5de-userspace-futex-source-audit-20260804-03/`

## Phase 6A PI smoke status

PHASE6A-PI-SMOKE-T01 的 benign single-thread PI lock/unlock source 只成功
編譯成 AArch64 relocatable object；host 缺少 ld.lld，未產生 Android ELF，
未 push、未執行、未改變裝置狀態。

Outputs:

- tools/test-phase6a/pi_lock_smoke.c
- tools/scripts/build_phase6a_pi_lock_smoke.sh
- findings/phase-6a-pi-lock-smoke-test.md
- local result under artifacts/phase6a/phase6a-pi-lock-smoke-T01/

## Phase 6A PI smoke T02

The exact PS7331 device completed one benign uncontended PI lock/unlock run
under shell UID 2000 with exit code 0. The temporary binary was removed,
ADB remained connected, and the build fingerprint was unchanged. This is
ordinary PI-futex reachability evidence only; it is not requeue-PI or
GhostLock exploitability evidence.

Outputs:

- findings/phase-6a-pi-lock-smoke-evidence-index.md
- local raw evidence under adb/phase6a/PHASE6A-PI-SMOKE-T02/
- local result under artifacts/phase6a/phase6a-pi-lock-smoke-T02/

## Phase 6PS — 全域特權面追蹤（2026-08-10）

Phase 6PS 把 Launcher 以外的 package/component、user、settings、HOME、
process、driver、OTA 與 `/init` 控制面放入同一個 caller→permission→identity→
sink 框架。Play Store 的 live package dump 確認它持有
`CHANGE_COMPONENT_ENABLED_STATE` 及多項高影響 permission rows，但它是
`/data/app` 且沒有 captured `PRIVATE_FLAG_PRIVILEGED`；主機端 bounded scan
沒有 Fire Launcher literal、HOME preferred writer 或直接 HOME launch path。
因此這是 provenance 待驗證線索，不是 protected-package bypass。

新增的主機端 closure 將 16 個 Binder/service surfaces 與 8 個 kernel/OTA/init
候選分為：已證實的受限 prewarm/settings deputies、KFT/DPM/OOBE/OTA 等
trusted 或下游受阻 writer、以及 query/resource/driver capability-only surfaces。
沒有新的 ordinary-app→system/root transition 或正式 HOME replacement。這輪
沒有送 Binder、未知 service transaction、ioctl、OTA/recovery、root 或任何
分割區操作。

Records:

- `findings/phase-6ps-privilege-surface-followup.md`
- `findings/phase-6ps-evidence-index.md`
- `output/tables/phase6ps-privilege-route-closure.csv`
- `output/call-graphs/phase6ps-privilege-surface.mmd`
- `tools/scripts/capture_phase6pr_vending_provenance.py`
- `adb/phase6pr/PHASE6PR-VENDING-READONLY-20260810-01/`
- `work/luna_worker_component_permission_provenance_20260810.md`
- `work/luna_worker_binder_sink_closure_20260810.md`
- `work/luna_worker_kernel_ota_unclosed_closure_20260810.md`

## Phase 6PT — 全域高權限路徑 closure（2026-08-10）

本輪把已保存的高影響 permission holder、Play Store exported launcher
receiver、KOR、ManagedProvisioning、H2、parent/profile、DPM 與 kernel/OTA
候選放入同一個 caller→gate→identity→sink 矩陣。結果確認 holder row 不等於
caller reachability；新增的 Play Store receiver 是 homescreen restore metadata
路徑，沒有 bounded Fire/HOME setter。沒有找到新的 ordinary-app→system/root
transition 或正式 HOME replacement。

既有兩個 ordinary-app deputy 仍然成立，但影響受限：prewarm 只建立
system-server process，tx4 只寫固定 setup flags。KFT static writer 仍被既有
cross-user/protected PMS gate 擋下。本輪未送 private Binder、broadcast、
ioctl、package/settings mutation、OTA/recovery、root 或 partition 操作。

Records:

- `findings/phase-6pt-broad-privilege-surface.md`
- `findings/phase-6pt-vending-receiver-analysis.md`
- `findings/phase-6pt-evidence-index.md`
- `output/tables/phase6pt-privilege-route-closure.csv`
- `output/call-graphs/phase6pt-privilege-route.mmd`
- `tools/scripts/audit_phase6ps_vending_launcher_receiver.py`
- `artifacts/phase6ps-vending-receiver-20260810-01/`
- `adb/phase6pt/PHASE6PT-READONLY-20260810-01/`
- `work/luna_worker_high_privilege_holder_inventory_20260810.md`
- `work/luna_worker_vending_unclosed_surface_20260810.md`
- `work/luna_worker_high_holder_kor_provisioning_closure_20260810.md`
- `work/luna_worker_parent_profile_dpm_sink_closure_20260810.md`
- `work/luna_worker_kernel_ota_unclosed_closure_20260810.md`

## Phase 6PV — 廣泛權限路徑 follow-up（2026-08-10）

本輪由三個 `luna_worker` 分別盤點 PS7331 GPL/kernel driver、Amazon IPC sink
與 OTA/post-install/recovery；主 Agent 將結果正規化成 29-row caller→gate→
identity→sink matrix。結果沒有新增 ordinary-app／ADB shell 到 system/root、
Fire protected-package mutation 或正式 HOME replacement 的閉合鏈。

Phase 6MI 的 source tar EOF-complete 證據已覆蓋 Phase 6FE 舊的外層 archive
未完成限制；但 recovery updater 的 privileged block-write capability 仍不是
shell caller route。CMDQ/ION/M4U/RPMB/ioctl、未知 Binder、OOBE replay、
malformed OTA、Root、recovery、flash 與 partition 操作均未執行。

Records:

- `findings/phase-6pv-broad-route-followup.md`
- `findings/phase-6pv-evidence-index.md`
- `output/tables/phase6pv-broad-route-closure.csv`
- `output/tables/phase6pv-broad-route-closure.csv.manifest.json`
- `output/call-graphs/phase6pv-broad-route.mmd`
- `tools/scripts/build_phase6pv_route_closure.py`
- `work/luna_worker_kernel_gpl_driver_surface_followup_20260810.md`
- `work/luna_worker_ipc_sink_inventory_followup_20260810.md`
- `work/luna_worker_ota_postinstall_followup_20260810.md`

## Phase 6PW — 廣泛權限與 HOME follow-up（2026-08-10）

三個 `luna_worker` 分別整理既有測試、Amazon IPC 邊界及 HOME/workaround
結果；主 Agent 以 `PHASE6PW-READONLY-20260810-01` 重新核對現況。User 0
HOME 仍為 Fire priority 50，Microsoft candidate 為 priority 0。沒有新增
ordinary-app／ADB shell 到 User-0 PackageManager、HOME 或 system/root 的閉合鏈。

Child profile 的 Tahoe HOME 是已證實的 per-user 結果；Accessibility redirect
只能列為需使用者授權、時序敏感的 foreground workaround。KFT、OOBE/OTA、kernel
driver 與 updater 仍分別受 child/PMS、system lifecycle、node/SELinux 或
recovery/partition 邊界約束。本輪未執行未知 Binder、ioctl、package/settings
mutation、user switch、reboot、OTA/recovery、Root 或分割區操作。

Records:

- `findings/phase-6pw-broad-privilege-followup.md`
- `findings/phase-6pw-evidence-index.md`
- `adb/phase6pw/PHASE6PW-READONLY-20260810-01/`
- `output/tables/phase6pw-route-classification.csv`
- `output/tables/phase6pw-route-classification.csv.manifest.json`
- `output/call-graphs/phase6pw-privilege-route.mmd`
- `tools/scripts/build_phase6pw_route_classification.py`
- `work/luna_worker_evidence_audit_followup_20260810.md/.csv`
- `work/luna_worker_ipc_boundary_followup_20260810.md/.csv`
- `work/luna_worker_workaround_audit_followup_20260810.md/.csv`

## Phase 6PX — provenance closure（2026-08-10）

本輪由三個 `luna_worker` 分別完成 deny-list、BOOT_AFTER_SYSTEM_OTA 與
OTA/recovery handoff 的 host-only provenance。新的關鍵證據是 PS7331
`fireos-res.apk` 的 `package_manager_deny_list.json` 直接包含
`com.amazon.firelauncher`；因此 protected seed membership 已有靜態直接證據。
但 `/data/system/PackageManagerDenyList` 的 live persisted 內容仍受 ACL 保護，
未被讀取，不能過度宣稱 literal live membership。

`BOOT_AFTER_SYSTEM_OTA` 已閉合為 `android.amazon.perm` protected broadcast →
system-server phase 550 + `isUpgrade()` → OOBE/Alexa sinks；沒有普通 caller 或
Fire HOME writer。OTA/recovery 只閉合到受信任的 updater/partition capability，
沒有 shell/ordinary-app handoff。未執行 broadcast、Binder、OTA/recovery、Root、
reboot、package/settings mutation 或分割區操作。

Records:

- `findings/phase-6px-provenance-closure.md`
- `findings/phase-6px-evidence-index.md`
- `output/tables/phase6px-provenance-closure.csv`
- `output/tables/phase6px-provenance-closure.csv.manifest.json`
- `output/call-graphs/phase6px-provenance-closure.mmd`
- `tools/scripts/build_phase6px_provenance_closure.py`
- `work/luna_worker_denylist_provenance_followup_20260810.md/.csv`
- `work/luna_worker_bootafter_ota_provenance_followup_20260810.md/.csv`
- `work/luna_worker_ota_recovery_handoff_followup_20260810.md/.csv`

## Phase 6PY — service permission、package-state writer 與 exported sink closure（2026-08-10）

本輪把研究範圍擴展到 Launcher 以外的 Amazon 高權限表面：ASP、SmartSuspend、
thermal、fosdebug、Activity/Window/Input service；Fire/Tahoe/KFT、PMS、DPM、
Arcus、OOBE/OTA package-state writer；以及 123 個 PS7331 fosinit XML 與 exported
component candidate。三份 worker CSV 正規化成 38-row caller→gate→identity→sink
矩陣。結果沒有新增 ordinary-app／ADB shell 到 User-0 HOME、PackageManager、
system/root 的閉合鏈。

ASP tablet branch 與 `preWarmApplicationForUser` 保留為靜態授權異常候選，但 sink
分別受限於 native audio 與 process/resource effect，沒有 HOME/package/root 證據。
KFT writer 只在 supplied child/profile `UserInfo.id` 寫 Fire/Tahoe state；
`BOOT_AFTER_SYSTEM_OTA` 仍是 system-server phase-550、upgrade-gated 的 OOBE
lifecycle。沒有猜測或重放未知 Binder transaction，沒有執行 package/settings
mutation、provisioning、reboot、OTA/recovery、Root、exploit、ioctl 或分割區操作。

Records:

- `findings/phase-6py-service-state-exported-closure.md`
- `findings/phase-6py-evidence-index.md`
- `output/tables/phase6py-service-state-exported-closure.csv`
- `output/tables/phase6py-service-state-exported-closure.csv.manifest.json`
- `output/call-graphs/phase6py-service-state-exported-closure.mmd`
- `tools/scripts/build_phase6py_service_state_closure.py`
- `work/luna_worker_amazon_service_permission_followup_20260810.md/.csv`
- `work/luna_worker_fire_state_writer_followup_20260810.md/.csv`
- `work/luna_worker_fosinit_exported_sink_followup_20260810.md/.csv`

## Phase 6PZ — kernel、IPC/OTA 與 workaround broad-surface closure（2026-08-10）

本輪把 kernel/driver、Amazon IPC/OTA/OOBE 與既有 HOME workaround 放在同一個
證據矩陣：13 個 kernel rows、6 個 bounded IPC/OTA unknowns、22 個 workaround rows，
共 41 rows。沒有新增 ordinary-app／ADB shell 到 User-0 package state、正式 HOME、
system/root 或 partition sink 的閉合鏈。GED 只有保存的 shell read-only telemetry；
CMDQ、ION、RPMB、USB、debugfs/sysfs 等仍是 source capability 或 risk-rejected
surface。

既有 Phase 6MI 已將 7.3.3.1 outer source archive 讀到 EOF（35 members），因此
worker 所列 archive-tail unknown 已 supersede，不重複解包。剩餘 IPC rows 仍保留為
bounded unknown，原因是 skipped code、caller provenance、identity relay 或 user
mapping 未完整恢復。child Tahoe 仍是 per-user HOME；Accessibility/ADB 仍是時序敏感
foreground fallback，不是 User-0 formal HOME replacement。

本輪未執行 device-node open、ioctl、Binder transaction、broadcast、OTA/recovery、
package/settings mutation、reboot、Root、exploit 或分割區操作。

Records:

- `findings/phase-6pz-broad-surface-closure.md`
- `findings/phase-6pz-evidence-index.md`
- `output/tables/phase6pz-broad-surface-closure.csv`
- `output/tables/phase6pz-broad-surface-closure.csv.manifest.json`
- `output/call-graphs/phase6pz-broad-surface-closure.mmd`
- `tools/scripts/build_phase6pz_broad_surface_closure.py`
- `work/luna_worker_kernel_driver_surface_followup2_20260810.md/.csv`
- `work/luna_worker_ipc_ota_unclosed_followup_20260810.md/.csv`
- `work/luna_worker_workaround_gap_followup_20260810.md/.csv`

## Phase 6QA — residual IPC、Vending 與 Settings closure（2026-08-10）

本輪以 Phase 6PZ 公開基準 `d34b2909f968d20496a0929822e36586a7e8729b` 整合三份
host-only follow-up。18-row matrix 沒有新增低權限 caller 到 User-0 HOME、Fire
Launcher package state、system/root 或 partition sink 的閉合鏈。Vending receiver
與 DSE 只達 Play restore、browser/search、secure-settings/install；Amazon PM
tx6/tx7 只達 system-created PendingIntent proxy receiver map；Settings 的
`default_home`/`config_show_default_home` 沒有形成新的 shell-writable HOME route。

本輪沒有接觸裝置、沒有 private Binder、broadcast、settings/overlay mutation、
APK、reboot、OTA/recovery、Root、ioctl 或分割區操作。未閉合的 production caller、
DSE decompiler warning branch 與 dormant picker reachability 仍標為 bounded
unknown，不升級為漏洞或 root 證據。

Records:

- `findings/phase-6qa-residual-control-closure.md`
- `findings/phase-6qa-evidence-index.md`
- `output/tables/phase6qa-residual-control-closure.csv`
- `output/tables/phase6qa-residual-control-closure.csv.manifest.json`
- `output/call-graphs/phase6qa-residual-control-closure.mmd`
- `tools/scripts/build_phase6qa_residual_control_closure.py`
- `work/luna_worker_vending_skipped_methods_followup_20260810.md/.csv`
- `work/luna_worker_amazonpm_proxy_followup_20260810.md/.csv`
- `work/luna_worker_settings_home_resource_followup_20260810.md/.csv`

## Phase 6QB — PS7331 residual caller、writer 與 runtime boundary（2026-08-10）

本輪由三個 `luna_worker` 完成 host-only 搜尋，再由主 Agent 以
`PHASE6QB-READONLY-20260810-01` 進行實機只讀交叉驗收。18-row matrix 包含
Amazon PM tx6/tx7 caller、Vending downstream 與 PS7331 Framework/OTA residual
writer。結果沒有新增低權限 caller 到 User-0 HOME、Fire package state、
system/root 或 partition sink 的閉合鏈。

只讀 baseline 確認 PS7331.4463N、SELinux Enforcing、Fire priority 50 HOME，
以及 shell 對 Amazon private service 的 `service_manager find` denial。沒有
執行 private Binder、broadcast、settings/package mutation、APK、reboot、
OTA/recovery、Root、ioctl 或分割區操作。tx6/tx7 production caller、DSE
injected writer、OOBE numeric-user mapping 與 OTA→recovery provenance 仍是
bounded UNKNOWN，不得升級為漏洞或 root 證據。

Records:

- `findings/phase-6qb-residual-inventory.md`
- `findings/phase-6qb-evidence-index.md`
- `adb/phase6qb/PHASE6QB-READONLY-20260810-01/`
- `output/tables/phase6qb-residual-inventory.csv`
- `output/tables/phase6qb-residual-inventory.csv.manifest.json`
- `output/call-graphs/phase6qb-residual-control-closure.mmd`
- `tools/scripts/build_phase6qb_residual_inventory.py`
- `work/luna_worker_amazonpm_caller_inventory_20260810.md/.csv`
- `work/luna_worker_vending_downstream_closure_20260810.md/.csv`
- `work/luna_worker_ps7331_residual_writer_inventory_20260810.md/.csv`

## Phase 6QC — privilege-surface closure beyond HOME（2026-08-10）

本輪把 prewarm identity、ASP/Audio permission-to-sink、OTA verifier/recovery/
canonicalization 三條線整合為 26-row host-only matrix。`preWarmApplicationForUser`
的 bounded sink 是 `startProcessLocked("prewarm")`；ASP tablet branch 的
`true` 是 static authorization anomaly candidate，但既有 shell runtime 仍為
`EACCES`；OTA 的 certificate/product/PVT/recovery/write chain 是 privileged
capability，沒有 shell/ordinary-app caller 閉合。

沒有執行 private Binder transaction、native audio/ASP operation、protected
broadcast、OTA/recovery、reboot、Root、exploit、settings/package mutation 或
partition write。所有未知 caller、PIP `Stub/onTransact`、OEM SELinux mapping
與 OTA indirect canonicalization data-flow 保留 `UNKNOWN`。

Records:

- `findings/phase-6qc-privilege-closure.md`
- `findings/phase-6qc-evidence-index.md`
- `output/tables/phase6qc-privilege-closure.csv`
- `output/tables/phase6qc-privilege-closure.csv.manifest.json`
- `output/call-graphs/phase6qc-privilege-closure.mmd`
- `tools/scripts/build_phase6qc_privilege_closure.py`
- `work/luna_worker_prewarm_identity_closure_20260810.md/.csv`
- `work/luna_worker_asp_permission_sink_closure_20260810.md/.csv`
- `work/luna_worker_ota_canonicalization_provenance_20260810.md/.csv`

## Phase 6QD — IPC、GPL driver 與高影響權限面審計（2026-08-10）

本輪整合 12 個未閉合 Amazon IPC、9 個 PS7331 GPL custom-driver/ioctl/
procfs/debugfs、12 個 residual high-impact rows，共 33-row host-only matrix。
CMDQ/MDP、M4U、perf、sensor factory、Amazon driver-test、IDME/lifecycle、
PM/DPM/Profile/WMS/Vending IPC 與 OTA/recovery 都已分類。

結果沒有 low-privilege app/shell → accepted gate → system/root →
PackageManager/HOME/package-state/credential/SELinux/partition 的閉合鏈。
`CONFIG_AMZN_DRV_TEST` 不在 `trona_defconfig`；M4U active source branch 是
`/proc/m4u` 而非 `/dev/m4u`；final node/SELinux/client mapping 仍是 evidence gap。

本輪未執行 device-node open、ioctl、private Binder、protected broadcast、
OTA/recovery、reboot、Root、exploit、settings/package mutation 或分割區寫入。

Records:

- `findings/phase-6qd-privilege-surface.md`
- `findings/phase-6qd-evidence-index.md`
- `adb/phase6qd/PHASE6QD-READONLY-20260810-01/`
- `output/tables/phase6qd-privilege-surface.csv`
- `output/tables/phase6qd-privilege-surface.csv.manifest.json`
- `output/call-graphs/phase6qd-privilege-surface.mmd`
- `tools/scripts/build_phase6qd_privilege_surface.py`
- `work/luna_worker_ipc_unclosed_sink_inventory_20260810.md/.csv`
- `work/luna_worker_gpl_driver_surface_inventory_20260810.md/.csv`
- `work/luna_worker_residual_high_impact_gap_audit_20260810.md/.csv`

## Phase 6QE — 廣域權限面與 exact-device policy 驗證（2026-08-10）

Phase 6QE 整合 15 個 Amazon IPC caller→sink、8 個 PS7331 GPL
driver/exact-image policy、14 個既有測試結果，共 37 rows。metadata-only
實機快照確認 HOME 仍是 `com.amazon.firelauncher/.Launcher` priority 50；
`/dev/mtk_cmdq` 是 `0644 system:system`、`/dev/gsensor` 是
`0660 radio:system`，shell 對 `/proc/m4u` 與 `/proc/life_cycle_reason` 無法讀取
metadata。未開啟 node、未執行 ioctl、Binder transaction、mutation、Root、OTA、
recovery、reboot 或分割區操作。

本輪仍未閉合 ordinary app/shell → accepted gate → system/root →
PackageManager/HOME/package-state/credential/SELinux/partition 的鏈；未知 caller
與 native/client mapping 保留 UNKNOWN，不視為漏洞。

Records:

- `findings/phase-6qe-report.md`
- `findings/phase-6qe-evidence-index.md`
- `adb/phase6qe/PHASE6QE-DEVICE-READONLY-20260810-02/`
- `output/tables/phase6qe-privilege-surface.csv`
- `output/tables/phase6qe-privilege-surface.csv.manifest.json`
- `output/call-graphs/phase6qe-privilege-surface.mmd`
- `tools/scripts/capture_phase6qe_device_readonly.py`
- `tools/scripts/build_phase6qe_privilege_surface.py`
- `work/luna_worker_phase6qe_ipc_caller_closure_20260810.md/.csv`
- `work/luna_worker_phase6qe_driver_policy_20260810.md/.csv`
- `work/luna_worker_phase6qe_existing_tests_20260810.md/.csv`

## Phase 6QF — 廣域權限面與 privilege-transition closure（2026-08-10）

本輪整合 Amazon IPC caller provenance、PS7331 exact-image policy/client mapping
與既有 runtime audit，共 26 rows。結果沒有閉合 ordinary app/shell → accepted
gate → system/root → PackageManager/HOME/package-state/credential/SELinux/OTA/
partition sink 的鏈。未知 caller、exact client、permission holder 與 first
consumer 保留 UNKNOWN；source capability、service list visibility、generic
SELinux type 或 child/profile writer 不被當作提權證據。

本輪僅做 host-only CSV/DEX/source/image-policy 交叉驗收，重用 Phase 6QE 的
metadata-only exact-device snapshot；未呼叫 private Binder、driver node/ioctl、
OTA/recovery、Root、reboot、Fire Launcher mutation 或分割區寫入。

Records:

- `findings/phase-6qf-report.md`
- `findings/phase-6qf-evidence-index.md`
- `output/tables/phase6qf-privilege-surface.csv`
- `output/tables/phase6qf-privilege-surface.csv.manifest.json`
- `output/call-graphs/phase6qf-privilege-surface.mmd`
- `output/call-graphs/phase6qf-privilege-surface.md`
- `tools/scripts/build_phase6qf_privilege_surface.py`
- `work/luna_worker_phase6qf_ipc_provenance_20260810.md/.csv`
- `work/luna_worker_phase6qf_exact_policy_client_20260810.md/.csv`
- `work/luna_worker_phase6qf_existing_runtime_audit_20260810.md/.csv`

## Phase 6RG — 廣域權限路徑與 7.3.3.1 資產交叉驗證（2026-08-10）

本輪由三個 luna_worker host-only ledger 與一個新的 serial-bound
metadata-only snapshot 組成，共 38 rows：14 Amazon IPC、12 source/package/
policy、10 existing runtime、1 exact-device、1 provenance boundary。

結果沒有閉合 ordinary app/shell → accepted gate → system/root →
PackageManager/HOME/package-state/credential/OTA/partition sink 的鏈。未知
caller、client、permission-holder、user propagation 與 first consumer 保留
UNKNOWN。GPL source 搜尋範圍沒有完整 `/init` tree；local boot_unpacked
exploit/root files 不屬於官方 OTA/GPL 證據，且未執行。

本輪未呼叫未知 Binder、driver ioctl、OTA/recovery、Root/exploit、Fire Launcher
mutation、reboot 或分割區寫入。

Records:

- `findings/phase-6rg-report.md`
- `findings/phase-6rg-evidence-index.md`
- `adb/phase6rg/PHASE6RG-DEVICE-READONLY-20260810-01/`
- `output/tables/phase6rg-privilege-surface.csv`
- `output/tables/phase6rg-privilege-surface.csv.manifest.json`
- `output/call-graphs/phase6rg-privilege-transition.mmd`
- `output/call-graphs/phase6rg-privilege-transition.md`
- `tools/scripts/build_phase6rg_privilege_surface.py`
- `work/luna_worker_phase6rg_ipc_residual_20260810.md/.csv`
- `work/luna_worker_phase6rh_source_package_20260810.md/.csv`
- `work/luna_worker_phase6ri_existing_results_20260810.md/.csv`
- `work/phase6rg_asset_scope_20260810.md`

## Phase 6RS–RU — Settings/PMS、SystemUI callback 與 rootless fallback closure（2026-08-10）

本輪整合三個 host-only worker ledger，共 35 rows：SettingsProvider/PMS/Amazon
PM writer 10、SystemUI/Amazon callback 14、rootless fallback 11。

SettingsProvider 的 caller/user/permission gates 已閉合到 SettingsState/XML；
PMS `setHomeActivity()` 的 preferred persistence 與有效 HOME resolver 勝出仍
是不同層。保存的 SystemUI callback/resource corpus 未找到 explicit Fire
component launch。Accessibility delayed foreground redirect 是最佳近似方案，
但不是 formal HOME 或 privilege transition。

本輪未啟用 Accessibility/UsageStats、未修改 settings/package/AppOps/overlay、
未呼叫 Binder/broadcast、未執行 OTA/recovery、Root、driver、reboot 或分割區寫入。

Records:

- `findings/phase-6rs-ru-report.md`
- `findings/phase-6rs-ru-evidence-index.md`
- `output/tables/phase6rs-ru-privilege-surface.csv`
- `output/tables/phase6rs-ru-privilege-surface.csv.manifest.json`
- `output/call-graphs/phase6rs-ru-control-surfaces.mmd`
- `output/call-graphs/phase6rs-ru-control-surfaces.md`
- `tools/scripts/build_phase6rs_ru_surface.py`
- `work/luna_worker_phase6rs_settings_pm_closure_20260810.md/.csv`
- `work/luna_worker_phase6rt_systemui_callback_closure_20260810.md/.csv`
- `work/luna_worker_phase6ru_rootless_fallback_review_20260810.md/.csv`

## Phase 6RV–RX — broad privilege-surface closure（2026-08-10）

本輪由 host-only ledger 擴大追蹤 Launcher 以外的特權面，共 48 rows：
Amazon package-metadata permission holder/caller 15、SystemUI/overlay/resource
20、OOBE/OTA/native sensitive-sink 13。`ADD_RM_PKG_METADATA` 的 declaration、
mutator、XML sink 已閉合，但 exact holder 與 production caller 仍為 `UNKNOWN`，
未找到通往 HOME、package state 或 privilege transition 的 join。

RX worker raw CSV 有 12 rows 含未 quoting 的逗號；normalized matrix 對受影響欄位
標為 `UNKNOWN_DUE_TO_UNQUOTED_RAW_CSV`，raw file 保留不覆寫。

保存的 SystemUI/Amazon callback corpus 未找到 explicit Fire Launcher launch；
OOBE/OTA/native writer 具備高權限 capability，但沒有 ordinary app/shell caller
鏈。具有足夠 system privilege 後可改變 protected package state 的結果仍成立，
但本輪沒有找到 shell/ordinary app 取得該 privilege 的路徑。最佳無 Root 方案仍是
使用者明確同意的 Accessibility foreground redirect，不是 formal HOME 或 root。

本輪未呼叫 private Binder/protected broadcast，未修改 settings/package/AppOps/
overlay/user，未執行 input/driver/OTA/recovery/Root/reboot/分割區操作。

Records:

- `findings/phase-6rv-rx-report.md`
- `findings/phase-6rv-rx-evidence-index.md`
- `output/tables/phase6rv-rx-privilege-surface.csv`
- `output/tables/phase6rv-rx-privilege-surface.csv.manifest.json`
- `output/call-graphs/phase6rv-rx-control-surfaces.mmd/.md`
- `tools/scripts/build_phase6rv_rx_surface.py`
- `work/luna_worker_phase6rv_20260810.md/.csv`
- `work/luna_worker_phase6rw_20260810.md/.csv`
- `work/luna_worker_phase6rx_20260810.md/.csv`

## Phase 6SN–SQ — 權限、native driver、OTA 與 HOME/PMS writer 收尾（2026-08-10）

本輪為 host-only static closure，四份 worker ledger 實際共 53 筆資料列：
SN permission-holder/caller 15、SO native driver 11、SP OTA/recovery native 17、
SQ HOME/PMS writer 10。ION 僅閉合到 shipped library 的 `/dev/ion` ABI caller；
其他 driver surface 的 exact shipped native caller 未建立。PS7331 updater 的
privileged write capability 已確認，但沒有 ordinary app/shell caller chain，且
沒有執行 updater/recovery 或寫分割區。

`ADD_RM_PKG_METADATA`、`PROFILE_INTERACTION` 的 declaration/gate 已確認，但
holder/grant/production caller 仍 UNKNOWN。KFT writer 的 component/application
state target 使用 supplied `UserInfo.id`，靜態證據只支持 child/profile scope；
沒有閉合 User-0 Fire HOME/PMS writer。未執行 ADB、Binder、driver ioctl、Root/
exploit、OTA/recovery、reboot 或任何裝置 mutation。

Records:

- `findings/phase-6sn-sq-report.md`
- `findings/phase-6sn-sq-evidence-index.md`
- `output/tables/phase6sn-sq-control-surface.csv`
- `output/tables/phase6sn-sq-input-manifest.sha256`
- `output/call-graphs/phase6sn-sq-control-surfaces.mmd/.md`
- `tools/scripts/build_phase6sn_sq_surface.py`
- `work/luna_worker_phase6sn_permission_caller_20260810.md/.csv`
- `work/luna_worker_phase6so_driver_native_20260810.md/.csv`
- `work/luna_worker_phase6sp_ota_native_20260810.md/.csv`
- `work/luna_worker_phase6sq_home_pms_writer_20260810.md/.csv`

## Phase 6SU–SX — IPC、exported component、kernel surface 與 evidence audit（2026-08-10）

本輪 host-only static/evidence closure 共 50 rows：SU IPC 8、SV DCPMS exported
surface 4、SW kernel surface 18、SX evidence audit 20。沒有新的 ordinary
app/shell 到 trusted identity、HOME/package/settings/credential/OTA sink 的
證據完整鏈。SV 四條新路徑只到 CDE profile/user policy persistence/evaluation；
SW 補齊 GED、PMIC、memcfg、thermal、USB/Type-C、Vcodec、camera、sensor/audio
與 Amazon driver surface，但沒有 exact shipped native caller positive join。

SX audit 保留既有 runtime 證據與限制：root transition 未證實、driver 未 open/ioctl、
private Binder 未成功呼叫、OTA/recovery 未執行；不可將 source capability 或
exported status 當成低權限可達性。本輪未修改裝置、未 reboot、未寫入分割區。

Records:

- `findings/phase-6su-sx-report.md`
- `findings/phase-6su-sx-evidence-index.md`
- `output/tables/phase6su-sx-control-surface.csv`
- `output/tables/phase6su-sx-input-manifest.sha256`
- `output/call-graphs/phase6su-sx-control-surfaces.mmd/.md`
- `tools/scripts/build_phase6su_sx_surface.py`
- `work/luna_worker_phase6su_ipc_residual_20260810.md/.csv`
- `work/luna_worker_phase6sv_exported_surface_20260810.md/.csv`
- `work/luna_worker_phase6sw_kernel_surface_20260810.md/.csv`
- `work/luna_worker_phase6sx_evidence_audit_20260810.md/.csv`

## Phase 6SY — 唯讀 current-state 核對（2026-08-10）

指定序號設備的新唯讀 snapshot 已完成，與 Phase 6SJ selected build/HOME/candidate/
users 輸出逐檔比較沒有差異。當前仍為 PS7331.4463N、KFTRWI/trona、verified boot
green，Fire Launcher priority 50 且為前景；User 0 package state `enabled=0` 為
default state，ActivityInfo 仍 enabled。這次沒有 package/settings/Binder/driver/
OTA/recovery/reboot 或 partition mutation。

Raw snapshot 因 settings 可能含帳號相關值而只留本機；公開 commit 僅包含 redacted
summary、state table 與 parser script。

Records:

- `findings/phase-6sy-readonly-snapshot.md`
- `output/tables/phase6sy-readonly-state.csv`
- `tools/scripts/summarize_phase6sy_readonly.py`
