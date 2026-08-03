# Final Report

Status: `PHASE_1_HANDOFF` — the complete multi-version/OTA final report is not yet complete.

The evidence-backed first-round result is in [phase-1-report.md](phase-1-report.md). It currently establishes:

- `com.amazon.firelauncher/.Launcher` is the selected HOME activity on the tested Fire OS 7.3.3.0 build.
- Fire Launcher declares HOME priority 50, which outranks the observed Microsoft Launcher priority 0.
- Android framework `PhoneWindowManager` contains an Amazon `KeyPolicyManager` hook before the normal Home path.
- In unlocked tests, the ADB Home event and explicit HOME intent both reach ActivityManager with Fire Launcher as the selected component; earlier contrary runs were keyguard-locked.
- `pm disable-user` is rejected by `PackageManagerService` protected-package enforcement, with Amazon's vendor callback providing the package-protection decision.
- The Microsoft control package can be disabled/restored by shell, while both `pm` and `cmd package` reject Fire Launcher at the same protected-package gate.
- Naming only `com.amazon.firelauncher/.Launcher` does not bypass the gate: both package-manager shell entry points reject component state changes through `setComponentEnabledSetting()`.
- User 0 currently has `com.amazon.parentalcontrols` as a Profile Owner, but the captured environment has no Device Owner, device-managed state or effective user restrictions; its inspected Fire Launcher policy is `setApplicationRestrictions()`, not the package-disable operation.
- Amazon also contains a separate KFT child-user path that enables FreeTime Launcher and disables Fire Launcher/Launcher3 for that user; this is not evidence of a primary-user watchdog restoring Fire Launcher.
- A standard preferred-home update is accepted but does not overcome Fire Launcher's higher candidate priority.
- The main Settings Default apps screen omits the `default_home` preference even though the default-home controller, picker and resources remain; the omission is confirmed against AOSP Android 9 r1/r61 and by live UI test `HOME-T21`.
- Fire Launcher's App info page still shows `Home app: Yes`, but its row only returns to the same Home-less Default apps page in `HOME-T23`; no tested Settings route exposed a launcher selector.
- Directly foregrounding Microsoft Launcher while unlocked does not change either `KEYCODE_HOME` or explicit HOME behavior (`HOME-T18`/`HOME-T19`).
- Amazon also has a `LauncherHijackPreventer` ActivityStack callback that gates Home-task visibility with SELinux/signature policy; this is confirmed as a framework modification but is not proven to launch Fire.

Still required before this file can be promoted to the final report:

- exact official OTA acquisition and provenance match for PS7330.4104N;
- method-level Fire OS/AOSP Android 9 multi-tag comparison, beyond the current structural reference index;
- physical Home-button capture;
- at least one additional Fire OS build for version timeline analysis;
- deeper review of Amazon callback branches and native components;
- classification of the conditional Alexa multimodal-Home callback and its shell-invisible mode service;
- exact live parental-controls application-restriction values and any policy effect outside the tested package-disable path;
- final no-root workaround assessment.

The Settings UI result above narrows the no-root assessment: the standard visible Settings route is not currently a usable launcher-selection route on this build. `SETTINGS-T01` could not launch non-exported `SubSettings`, and corrected `SETTINGS-T03` fell back to the metadata-selected Default apps dashboard. The retained `DefaultHomePicker` remains an open privileged/internal alternate-entry-point question, not evidence that a workaround exists.

An official adjacent PS7331 OTA and AOSP `android-9.0.0_r1`/`r61` references have been acquired and are documented, but neither is treated as exact PS7330.4104N evidence.
