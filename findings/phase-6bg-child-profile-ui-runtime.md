# Phase 6BG — Stock Child-Profile UI Runtime Test

## Scope

This was a bounded test of the supported Fire tablet UI for creating a child
profile. It used only the explicitly selected device and normal Settings/H2 UI
navigation. No private Binder transaction, `service call`, package-state
mutation, Fire Launcher mutation, Device Owner provisioning, reboot, root,
recovery, OTA, or partition operation was used.

| Field | Value |
|---|---|
| Test ID | `PHASE6BG-KFT-UI-T01` |
| Device serial | `G001LT0511550CFT` |
| Build fingerprint | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` |
| User data | Researcher-supplied test values; not written into this report or metadata |
| UI language | Japanese on the device |

Raw evidence is retained locally under
`adb/phase6bg/PHASE6BG-KFT-UI-T01/`. The raw directory is intentionally not
part of a public commit because it contains device-linked dumps and logcat.

## Result

**已證實：** the supported Settings path reaches H2's Profiles & Family
Library page and displays the child-profile add control.

**已證實：** after the lock-screen PIN prerequisite was completed through the
visible Settings UI, clicking “add child profile” caused H2 to start this
explicit component:

```text
com.amazon.tahoe/.settings.household.HouseholdSettingsAddChildActivity
```

The stock PS7331 package could not resolve that component. The H2 process
crashed with `ActivityNotFoundException` from
`UsersFragment.onPreferenceTreeClick(UsersFragment.java:233)`. The same
failure was observed on the second UI attempt after the PIN step.

**已證實：** no child user was created. Both the post-test and final guard
contain only:

```text
UserInfo{0:sinyu:13} running
```

**已證實：** HOME and the foreground were restored to Fire Launcher:

```text
priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
com.amazon.firelauncher/.Launcher
```

The final guard shows `mResumedActivity` and `mCurrentFocus` at
`com.amazon.firelauncher/.Launcher`.

**已證實：** the test PIN was removed through the normal Security & Privacy
UI after the child flow failed. The post-rollback state is
`lockscreen.password_type=null`, `lockscreen.disabled=0`, and the lock-settings
dump reports `SID = 0`. No shell `settings put/delete` or `locksettings clear`
command was used.

## Exact observed failure

The preserved all-buffer logcat is
`adb/phase6bg/PHASE6BG-KFT-UI-T01/crash-log/logcat_all.stdout.txt`.
Relevant records include:

- line 5735: H2 starts the explicit Tahoe component from UID 10130;
- lines 5739 and 5752: `ActivityNotFoundException` for the component;
- line 6261: the same explicit start on the second attempt;
- lines 6264 and 6272: the second `ActivityNotFoundException` and
  `UsersFragment.onPreferenceTreeClick(UsersFragment.java:233)`;
- lines 6266–6267: H2 is force-finished and its process dies.

The direct shell probe of the same component independently returned:

```text
Error: Activity class {com.amazon.tahoe/com.amazon.tahoe.settings.household.HouseholdSettingsAddChildActivity} does not exist.
```

The standalone `com.amazon.tahoe.settings.ADD_CHILD` action did not resolve,
and the separately enumerated `MANAGE_CHILD_PROFILE` action also returned
`No activity found`. These were foreground/read-only entry-point probes; no
private or guessed Binder call followed them.

## Permission boundary observed

The H2 child-edit action resolved to
`com.amazon.h2settingsfortablet/.EditUserActivity`, but a shell launch was
rejected with:

```text
requires com.amazon.h2settingsfortablet.H2SETTINGS_PERMISSION
```

This is a signature permission boundary, not evidence of a usable shell or
confused-deputy path. No attempt was made to bypass it.

## State and rollback

The UI flow temporarily entered the lock-screen credential screen because the
child-profile page requires a lock-screen PIN. The PIN was entered only through
the visible fields and is not stored in repository files. After the child
workflow failed, the standard Security & Privacy page was used to authenticate
and turn the lock-screen PIN off. A final `input keyevent 3` returned the
foreground to Fire Launcher.

The final read-only guard confirms:

- ADB state: `device`;
- build fingerprint unchanged;
- only user 0 remains;
- HOME resolver remains Fire Launcher at priority 50;
- Fire Launcher package/component state was not changed;
- foreground activity is Fire Launcher;
- lock-screen credential state is back to the pre-test observable values.

## Findings classification

| Finding | Classification |
|---|---|
| Stock Settings exposes the child-profile UI | 已證實 |
| H2 invokes the missing Tahoe explicit component on this build | 已證實 |
| Current stock UI can complete child-profile creation on this PS7331 build | 已排除（for this tested build/path） |
| H2 direct shell launch is a viable alternative | 已排除；signature permission denial |
| The missing component is an Amazon packaging/version integration defect | 高可信推論；the runtime failure proves the mismatch, but source/build provenance is not yet proven |
| A private KFT Binder path could still create a child user | 待驗證；not invoked |
| This UI defect is a root or HOME-replacement mechanism | 已排除 |

## Reproduction

Read-only/foreground capture scripts:

```sh
python3 tools/scripts/capture_phase6ay_kft_device_preflight.py \
  --serial G001LT0511550CFT \
  --output adb/phase6bg/PHASE6BG-KFT-UI-T01/final-guard

python3 tools/scripts/capture_phase6bg_child_crash_log.py \
  --serial G001LT0511550CFT \
  --output adb/phase6bg/PHASE6BG-KFT-UI-T01/crash-log
```

The test-specific UI scripts refuse to overwrite an existing output directory,
record the explicit serial, and hash their output files. The PIN-entry helper
redacts the value from metadata and output.

## Conclusion

The supported Settings route is present, but this PS7331 build's H2 child
profile flow is not operational: it calls a Tahoe Activity that is absent from
the installed Tahoe package. The experiment therefore did not create `TEST`,
did not enter the KFT child-user lifecycle, and did not alter HOME selection.
The device was returned to its normal Fire Launcher and no-PIN state.

The next safe research step is host-side provenance analysis of the H2/Tahoe
manifest and the corresponding `UsersFragment` implementation. Replaying
private KFT Binder transactions, bypassing the signature permission, patching
the APK, or manually creating a profile owner remains outside this test.
