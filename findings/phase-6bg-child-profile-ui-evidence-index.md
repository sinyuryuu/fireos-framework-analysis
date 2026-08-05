# Phase 6BG Child-Profile UI Evidence Index

All paths below are local raw evidence paths. SHA-256 values are for the
individual referenced files, not a reconstructed or modified copy.

| Evidence ID | Source | File | SHA-256 | Observation | Confidence |
|---|---|---|---|---|---|
| E6BG-UI-BASE-01 | Initial device preflight | `adb/phase6bg/PHASE6BG-KFT-UI-T01/build_fingerprint.stdout.txt` | `15efeeb538e9463865e2851c32dc3142d71c8412b8b55447506b1d65db402e4b` | PS7331 fingerprint is unchanged and ADB is connected to the selected serial | Confirmed |
| E6BG-UI-BASE-02 | Initial device preflight | `adb/phase6bg/PHASE6BG-KFT-UI-T01/package_resolve_home.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | HOME resolves to Fire Launcher at effective priority 50 | Confirmed |
| E6BG-UI-BASE-03 | Initial device preflight | `adb/phase6bg/PHASE6BG-KFT-UI-T01/users.stdout.txt` | `4c915d71b79462e0a3ea4996f5882c5293afe47a963fca1a41856a47cb4c7b83` | Only user 0 was present before the UI experiment | Confirmed |
| E6BG-UI-H2-01 | Shell foreground probe | `adb/phase6bg/PHASE6BG-KFT-UI-T01/h2-child/launch_child_profile_ui.stderr.txt` | `81a6fe08ecb7c9003e3d23a09eef372f75f2165bd2597831c2566b4c52edbf0f` | Direct H2 child-edit launch is rejected by signature permission `H2SETTINGS_PERMISSION` | Confirmed |
| E6BG-UI-TAHOE-01 | Shell foreground probe | `adb/phase6bg/PHASE6BG-KFT-UI-T01/launch/launch_child_profile_ui.stderr.txt` | `3d3c1c0e8bb0cfe87ac746ec48211b0d84008d003ae15092d98e924aaa4a7139` | Explicit Tahoe child Activity does not exist | Confirmed |
| E6BG-UI-TAHOE-02 | Action probe | `adb/phase6bg/PHASE6BG-KFT-UI-T01/launch-action/launch_child_profile_ui.stderr.txt` | `40bceec925502e73151e25d5670efc7b5c50db8a3d587bc12ec7566e92bfbceb` | `com.amazon.tahoe.settings.ADD_CHILD` has no resolver result | Confirmed |
| E6BG-UI-TAHOE-03 | Public action probe | `adb/phase6bg/PHASE6BG-KFT-UI-T01/tahoe-manage-child/launch_child_profile_ui.stderr.txt` | `574771f14158bb22a3a1ee6a9227d674b113768bd7fd0abf399d9524c2e94194` | Enumerated `MANAGE_CHILD_PROFILE` action also has no resolver result on the device | Confirmed |
| E6BG-UI-CRASH-01 | All-buffer logcat | `adb/phase6bg/PHASE6BG-KFT-UI-T01/crash-log/logcat_all.stdout.txt` | `01e34509f8858e403619c3e9625889a2908d202d2c998ce0d1fe9a8f0010b45b` | H2 starts the explicit Tahoe component, then throws `ActivityNotFoundException`; second attempt reaches `UsersFragment.onPreferenceTreeClick(UsersFragment.java:233)` | Confirmed |
| E6BG-UI-STATE-01 | Post-PIN read-only state | `adb/phase6bg/PHASE6BG-KFT-UI-T01/pin-post/lock_settings.stdout.txt` | `2e18de0109588fa2d9289eabd76832e61bf2d41c241b4b8274d0b8feb80cadfe` | A synthetic-password handle/SID was observable after the PIN UI step; this was later reverted through the standard UI | Strong evidence |
| E6BG-UI-ROLLBACK-01 | Standard Security UI rollback | `adb/phase6bg/PHASE6BG-KFT-UI-T01/lockscreen-off-submit/password_type_after_submit.stdout.txt` | `38e0b9de817f645c4bec37c0d4a3e58baecccb040f5718dc069a72c7385a0bed` | `lockscreen.password_type` returned to `null` after UI rollback | Confirmed |
| E6BG-UI-ROLLBACK-02 | Standard Security UI rollback | `adb/phase6bg/PHASE6BG-KFT-UI-T01/lockscreen-off-submit/lock_settings_after_submit.stdout.txt` | `1c2273a7e0ce44e5fc623b3e373e7849c91cc1f96784ae2dfdaf6d89a2b75acb` | Lock-settings dump reports `SID = 0` after rollback | Confirmed |
| E6BG-UI-FINAL-01 | Final read-only guard | `adb/phase6bg/PHASE6BG-KFT-UI-T01/final-guard/users.stdout.txt` | `4c915d71b79462e0a3ea4996f5882c5293afe47a963fca1a41856a47cb4c7b83` | Only user 0 remains | Confirmed |
| E6BG-UI-FINAL-02 | Final read-only guard | `adb/phase6bg/PHASE6BG-KFT-UI-T01/final-guard/package_resolve_home.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | HOME remains Fire Launcher at priority 50 | Confirmed |
| E6BG-UI-FINAL-03 | Final read-only guard | `adb/phase6bg/PHASE6BG-KFT-UI-T01/final-guard/activity_state.stdout.txt` | `a581c7c2639628c4ed84736cbc8332e5b5f53d88ac644b0d0ad25feffa9a93cd` | `mResumedActivity` is `com.amazon.firelauncher/.Launcher` | Confirmed |
| E6BG-UI-FINAL-04 | Final read-only guard | `adb/phase6bg/PHASE6BG-KFT-UI-T01/final-guard/window_state.stdout.txt` | `f2455b1470b9613d7f81f58035bde7a91a8d54a615af4985a7f9e71aab32e7d1` | `mCurrentFocus` is Fire Launcher | Confirmed |

## Rejected or not performed

- No `service call` or guessed private Binder transaction was issued.
- No shell bypass of `H2SETTINGS_PERMISSION` was attempted.
- No `pm create-user` was used in this UI test; the earlier bounded restricted-
  user experiment is documented separately.
- No Fire Launcher disable/hide/suspend/uninstall/clear operation was issued.
- No Device Owner/Profile Owner provisioning, reboot, root, exploit, OTA, or
  partition operation was performed.
