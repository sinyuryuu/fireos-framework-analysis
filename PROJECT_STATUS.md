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
