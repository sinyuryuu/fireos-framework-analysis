# Phase 6MQ — AmazonProfileService launcher-helper closure

Date: 2026-08-10
Schema: `phase6mq-profile-launcher-helper-v1`

## Scope and safety

This is **host-only static analysis** of preserved PS7331 artifacts. The audit
did not contact the tablet, invoke `service call`, replay a private Binder
transaction, send an intent, change settings or package state, run an ioctl,
reboot, use an exploit, or write any partition. The exact source artifact is
`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`.

## Executive result

**已證實：** `AmazonProfileService.BinderService.initiateLauncher()` is a
misleadingly named helper in this disassembly. Its body calls the synthetic
`access$6400()` permission bridge, writes the `Initiate launcher` log message,
and returns `AmazonProfileManager.SUCCESS`. It contains no `Intent`,
`startActivityAsUser`, HOME resolver API, preferred-activity API, or package
component-state mutation.

**已證實：** `access$6400()` invokes
`enforceProfileInteractionPermissions()`. That method checks
`com.amazon.device.permission.PROFILE_INTERACTION` with
`Context.checkPermission(permission, processId, userId)` and throws a
`SecurityException` on denial.

**已證實：** `startProfilePicker(int)` constructs an explicit Intent from
the configured `KEY_PROFILE_PICKER_PACKAGE_NAME` and
`KEY_PROFILE_PICKER_ACTIVITY_NAME`, obtains `ActivityManager.getCurrentUser()`,
and calls `Context.startActivityAsUser()` for that current user. This is a
profile-picker UI path, not a HOME resolver selection or a Fire Launcher
package-state writer.

**高可信推論（bounded）：** within the preserved
`AmazonProfileService.BinderService` class slice (`74942-77607`), no direct HOME/preferred/package-state writer token was found. This does not claim that no other Amazon service can write HOME state.

**已排除（bounded）：** `initiateLauncher()` itself is a direct HOME launch,
preferred-activity writer, or Fire Launcher enable/disable sink.

**待驗證：** the source and complete caller graph for the profile-picker
configuration map; whether any authorized caller reaches `startProfilePicker`
under a particular profile lifecycle. Neither question changes the bounded
finding that the shown sink is an explicit profile picker, not HOME selection.

**因風險拒絕測試：** no attempt was made to call `amazonprofileservice`, to
guess a Binder transaction code, or to replay `startProfilePicker`; such calls
would exercise a private service and could change foreground/profile state.

## Exact evidence windows

| Evidence | Location | Observation | Classification |
|---|---|---|---|
| 6MQ-E01 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:76246-76256` | `initiateLauncher()` → permission bridge → log → `SUCCESS` | 已證實 |
| 6MQ-E02 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:78685-78691` | `access$6400()` → `enforceProfileInteractionPermissions()` | 已證實 |
| 6MQ-E03 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:78949-78966` | `PROFILE_INTERACTION` check using process/user IDs; denial throws | 已證實 |
| 6MQ-E04 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:77222-77280` | configured explicit profile picker → current-user `startActivityAsUser` | 已證實 |
| 6MQ-E05 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:80813-80823` | Binder/local service publication and package receiver registration | 已證實 |
| 6MQ-E06 | `BinderService class slice 74942-77607` | no bounded HOME/package-state writer token; one `startActivityAsUser` hit belongs to profile picker | 高可信推論（bounded） |

## Minimal call paths

```text
BinderService.initiateLauncher()
  → AmazonProfileService.access$6400()
  → enforceProfileInteractionPermissions()
  → Context.checkPermission(PROFILE_INTERACTION, processId, userId)
  → SecurityException or return
  → Slog("Initiate launcher")
  → return AmazonProfileManager.SUCCESS
```

```text
BinderService.startProfilePicker(wakeUpSource)
  → read profile-picker package/activity configuration
  → Intent.setClassName(package, activity)
  → ActivityManager.getCurrentUser()
  → Context.startActivityAsUser(intent, UserHandle.of(currentUser))
  → profile-picker UI
```

The first path has no launch sink. The second path has an explicit launch sink,
but its target is supplied by profile-picker configuration and its observed
operation is not `ACTION_MAIN` + `CATEGORY_HOME`, `resolveActivity`,
`setHomeActivity`, or a preferred-activity write.

## Bounded token scan

The following scan was performed only over the `BinderService` class slice;
line numbers are absolute disassembly line numbers:

- `setHomeActivity`: no hit
- `replacePreferredActivity`: no hit
- `addPreferredActivity`: no hit
- `setComponentEnabledSetting`: no hit
- `setApplicationEnabledSetting`: no hit
- `com.amazon.firelauncher`: no hit
- `CATEGORY_HOME`: no hit
- `ACTION_MAIN`: no hit

The only `startActivityAsUser` hit in this bounded slice is the one at
`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:77222-77280`. Absence from this slice is not a
binary-wide proof about every Amazon service.

## Service publication

`onStart()` publishes the Binder service name `amazonprofileservice`, publishes
the local `AmazonProfileService`, and registers a package-installed receiver
(`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:80813-80823`). The audit does not infer the service
process UID or caller permissions beyond the exact permission check shown in
the method windows.

## Relationship to the HOME question

This closure removes one named candidate from the direct HOME-selection path:
the `initiateLauncher` method does not implement that behavior in PS7331.
`startProfilePicker` remains a profile lifecycle/UI path that could affect the
visible foreground during profile selection, but no evidence here shows it
overriding the User 0 HOME resolver or writing Fire Launcher preferred state.
The exact HOME enforcement evidence remains the AOSP-shaped resolver ordering
plus the PS7331 PackageManager deny-list resource; see the earlier Phase 6AP
and Phase 4A reports.

## Input hashes

```text
{
  "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log": "ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c",
  "findings/phase-6bj-binder-caller-closure.md": "33b174a57e0889c4c74d0fcf4898f70c4d5e679b7488d60aa40f3ad6d49ef3a6",
  "findings/phase-6mn-ipc-user-scope-closure.md": "2adc3dd733dbc310da2706a14e9e7f12759198c09f37a63970f35c97855f383e",
  "findings/phase-6s-ipc-focus-review.md": "14f4004ea55333cf201f85bebab1258346f755f25fb340c2323a53d191fcfe42"
}
```

## Reproduction

```sh
python3 tools/scripts/audit_phase6mq_profile_launcher_helper.py --dry-run
python3 tools/scripts/audit_phase6mq_profile_launcher_helper.py
```

Generated artifact: `artifacts/phase6mq-profile-launcher-helper-20260810-01`.
