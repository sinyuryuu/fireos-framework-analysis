# Fire Launcher Home Component Protection

Status: `CONFIRMED` for the tested User 0 component-disable requests.

## Test target

The target was the declared HOME activity:

```text
com.amazon.firelauncher/com.amazon.firelauncher.Launcher
```

The activity declares `MAIN` + `HOME` + `DEFAULT` with priority `50` in `decompiled/jadx/firelauncher/resources/AndroidManifest.xml:316-340`.

## Runtime evidence

Both shell entry points were tested with explicit approval:

- `adb/component-tests/COMPONENT-T01/` — `pm disable-user`
- `adb/component-tests/COMPONENT-T02/` — `cmd package disable-user`

Both return:

```text
Security exception: Cannot disable a protected package: com.amazon.firelauncher
```

Both stacks reach:

```text
PackageManagerService.setEnabledSetting()
PackageManagerService.setComponentEnabledSetting()
PackageManagerShellCommand.runSetEnabledSetting()
```

The before/after/final package dumps show no new `disabledComponents` entry for `.Launcher`; the existing unrelated component entries are unchanged. At every snapshot, HOME resolution remains `com.amazon.firelauncher/.Launcher` with priority `50`, and `mResumedActivity`/`mCurrentFocus` remain Fire Launcher. The SHA-256 manifest for each test passed.

## Determination

- `Confirmed`: shell cannot disable the Fire Launcher Home component through `pm`.
- `Confirmed`: `cmd package` does not bypass the same protection.
- `Confirmed`: the component state was not mutated, so no component watchdog is needed to explain the result.
- `Disproved`: disabling only the Home component is not an observed no-root ADB workaround on this build.

The result strengthens the existing PackageManager finding: Amazon's protected-package decision is applied to component and package state changes through the same service gate.
