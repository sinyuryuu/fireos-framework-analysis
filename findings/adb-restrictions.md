# ADB Restrictions

Status: `PHASE_1_PRELIMINARY_RESULT`.

## Observed shell boundary

- SELinux is `Enforcing`: `device/baseline/BASELINE-20260803-04/security_getenforce.txt:1`.
- ADB shell is UID 2000, context `u:r:shell:s0`: `security_id.txt:1`.
- Verified Boot is green and the bootloader state is locked: `device/baseline/BASELINE-20260803-04/device_properties.txt:202,221`.
- `device_config` is not available as a shell command: `device_config.txt:1`.
- `/data/system/PackageManagerDenyList` exists, but shell read/pull access was denied; the failed attempt is retained in the artifact logs.

## Findings

`Confirmed`: shell can invoke the PackageManager Binder command but Amazon's protected-package callback applies a UID-specific denial to Fire Launcher.  
`Confirmed`: `PACKAGE-T02` shows the same shell UID can disable and restore Microsoft Launcher, so the denial is package-specific rather than a blanket shell restriction. `PACKAGE-T05` shows `cmd package` does not bypass it.  
`Confirmed`: the standard `set-home-activity` shell command is accepted but does not overcome resolver priority.  
`Confirmed`: shell cannot bypass the same protection by naming only `com.amazon.firelauncher/.Launcher`; both `pm` and `cmd package` component requests are rejected by `setComponentEnabledSetting()`.  
`Hypothesis`: other shell-facing Binder commands may have additional Amazon restrictions; no broad bypass claim is made from these tests.  
`Disproved`: no evidence supports bypassing protection by using `cmd package` instead of `pm`; both are routed to PackageManager service, and the observed rejection is in the service-side call path.

## DevicePolicy environment

`POLICY-T01` shows an active User 0 Profile Owner, `com.amazon.parentalcontrols`, but no Device Owner, no device-managed state and no effective user restrictions (`adb/probes/POLICY-T01/device_policy.txt:1-12`; `user.txt:9-28`). The decompiled parental-controls APK can apply Fire Launcher application restrictions with `setApplicationRestrictions()`, and can hide filtered third-party packages with `setApplicationHidden()`. It does not provide evidence that it caused the synchronous Fire Launcher disable exception. That request fails in PackageManager protected-package enforcement before a DevicePolicy call is visible.

`Hypothesis`: parental controls may still alter Launcher content or policy-gated UI when enabled. The exact live per-package restriction bundle was not readable through the shell-only probe, so no broader DPM conclusion is made.

No access-control bypass, root attempt, DRM/account bypass or privileged file extraction was attempted.
