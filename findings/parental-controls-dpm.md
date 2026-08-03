# DevicePolicy and Parental Controls Finding

Status: `PHASE_1_PRELIMINARY_RESULT`

## Runtime environment

`POLICY-T01` is a read-only capture. User 0 has `com.amazon.parentalcontrols/.receivers.ParentalAdminReceiver` as Profile Owner. The same capture reports no Device Owner, `Device managed: false`, and no effective user restrictions:

- `adb/probes/POLICY-T01/device_policy.txt:1-12,41-44`
- `adb/probes/POLICY-T01/user.txt:9-28`

This is an environment fact, not by itself a cause of the Launcher behavior.

## Parental-controls APK behavior

The pulled device APK is recorded in `firmware/manifests/ARTIFACT-20260803-08/sha256sums.txt` and decompiled under `decompiled/jadx/parentalcontrols/`.

- `ParentalControlsConstant.LAUNCHER_PACKAGE` is `com.amazon.firelauncher` (`sources/com/amazon/parentalcontrols/constant/ParentalControlsConstant.java:67-70`).
- `PolicyAppRestriction.enforcePolicy()` reads and writes an application-restriction bundle through `DevicePolicyManager.getApplicationRestrictions()` and `setApplicationRestrictions()` (`sources/com/amazon/parentalcontrols/policy/policyImpl/PolicyAppRestriction.java:33-48`).
- `ParentalAdminUtils.applyLauncherPolicyIfApplicable()` applies the video-playback policy to the Launcher (`sources/com/amazon/parentalcontrols/admin/ParentalAdminUtils.java:246-252`). Other policy maps also target Launcher content/UI policy keys (`sources/com/amazon/parentalcontrols/constant/PolicyPrefMap.java:23-40,49-67`).
- Package-change handling filters through `ApplicationMetadataUtils.is3PApp()` before calling `processApps()` (`sources/com/amazon/parentalcontrols/receivers/PackageChangesReceiver.java:22-77`); `processApps()` invokes DPM `setApplicationHidden()` for the selected package list (`sources/com/amazon/parentalcontrols/admin/ParentalAdminUtils.java:488-493`; `policy/policyImpl/PolicyAppHidden.java:19-33`).
- The package-change receiver is disabled in the manifest by default (`resources/AndroidManifest.xml:358-365`), and the boot receiver only updates notification/curfew state (`sources/com/amazon/parentalcontrols/receivers/ParentalBootBroadcastReceiver.java:15-22`).

## Separation from the tested disable failure

`PACKAGE-T01`, `PACKAGE-T03` and `PACKAGE-T05` fail synchronously with `Cannot disable a protected package: com.amazon.firelauncher`. The captured stack reaches `PackageManagerService.setEnabledSetting()` and the Amazon protected-package callback path; it does not show a DevicePolicy operation. Therefore:

- `Confirmed`: DevicePolicy is present in the test environment.
- `Confirmed`: parental controls can apply application-level restrictions to Fire Launcher.
- `Confirmed for the tested request`: the `pm`/`cmd package` rejection occurs at PackageManager protected-package enforcement.
- `Disproved for the tested request`: the active Profile Owner is the immediate cause of the disable exception.
- `Hypothesis`: parental controls may affect Launcher content or policy-gated UI when enabled; the live per-package restriction bundle was not exposed by the shell-only probe.

## Separate child-user path

Amazon's `AmazonUserManagerService.BinderService.enableKftLauncherComponent()` enables `com.amazon.tahoe/.launcher.FreeTimeLauncherActivity` and sets enabled state `2` for `com.amazon.firelauncher` and `com.android.launcher3` for the affected user (`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325`). The caller is used by the KFT child-user/upgrade path (`:54371-54414,55099-55100`). This is a FreeTime user switch, not evidence of a primary-user watchdog that re-enables Fire Launcher after a failed shell request.
