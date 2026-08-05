# CHILD-TEST-20260805-01

## Result

`FAILED_NO_CHILD_USER` — the native Settings route did not create a child user/profile.

## Observed failure

The Settings UI reached **Profiles & Family Library → Add child profile**. After the required lock-screen PIN form was submitted, the second attempt produced this system-server sequence in `after/relevant-logcat.txt`:

```text
START u0 {act=com.amazon.tahoe.settings.ADD_CHILD cmp=com.amazon.tahoe/.settings.household.HouseholdSettingsAddChildActivity ...}
ActivityNotFoundException: Unable to find explicit activity class {com.amazon.tahoe/com.amazon.tahoe.settings.household.HouseholdSettingsAddChildActivity}
Force finishing activity com.amazon.h2settingsfortablet/.UsersActivity
```

The Settings activity then returned to `com.android.settings/.Settings`.

## State verification

- `pm list users`: only `UserInfo{0:sinyu:13} running` before and after.
- HOME resolver: `com.amazon.firelauncher/.Launcher` before and after.
- Fire Launcher was not disabled, hidden, suspended, uninstalled, force-stopped, or cleared.
- Build fingerprint was unchanged.
- `settings get secure lockscreen.password_type`: `null` after the attempt.
- `dumpsys device_policy`: `passwordQuality=0x0` after the attempt.
- `settings get secure lockscreen.disabled`: `0` after the attempt.
- No reboot, private Binder call, `pm create-user`, or unknown `service call` was executed.

The supplied PIN was not written into this report or command artifact. The lock-screen PIN form did not leave a detectable credential state in the captured post-state.

## Technical interpretation

The UI path is present in the H2 Settings application, but its target component cannot be launched on this user/device state. The installed `com.amazon.tahoe` package is present at `/system/priv-app/com.amazon.tahoe/com.amazon.tahoe.apk`, and its package dump contains an intent-table entry for `HouseholdSettingsAddChildActivity`; nevertheless, the actual launch attempt raised `ActivityNotFoundException`. This is evidence of a package/component resolution or availability mismatch, not evidence that child-user creation succeeded.

Confidence: **Confirmed** for the observed failure and unchanged device state; **Unknown** for the underlying reason the target could not be resolved.

## Rollback

No child user/profile was created. No package-state rollback was required. The only possible credential-side mutation was the temporary Settings PIN form; post-state checks show no persisted lock-screen password type and no password-quality change.
