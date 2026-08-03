# Phase 5 — additional ADB package-state surface test

## Test

`PM-SUSPEND-FIRE-T01` tested the previously untested shell route:

```text
adb -s G001LT0511550CFT shell pm suspend --user 0 com.amazon.firelauncher
```

The test used the existing Microsoft Launcher installation as a resolver
control candidate and captured a complete pre-state snapshot. Fire Launcher
was not disabled, hidden, uninstalled, cleared, or force-stopped.

## Result

The command returned exit code 255 and the PackageManager shell stack reported:

```text
Security exception: setPackagesSuspendedAsUser: Neither user 2000 nor current process has android.permission.SUSPEND_APPS.
```

The stack identifies:

```text
PackageManagerService.setPackagesSuspendedAsUser(PackageManagerService.java:14356)
PackageManagerShellCommand.runSuspend(PackageManagerShellCommand.java:1704)
```

## State comparison

After the rejected request:

- Fire Launcher: `installed=true hidden=false suspended=false stopped=false enabled=0`.
- HOME resolver: `com.amazon.firelauncher/.Launcher`, priority 50.
- HOME candidates: Fire priority 50, Microsoft priority 0, Settings fallback
  priority -1000.
- `mResumedActivity`: Fire Launcher.
- `mCurrentFocus`: Fire Launcher.

The separate after snapshot is in
`adb/mutation-tests/PM-SUSPEND-FIRE-T01-after/`.

## Verdict

- **已證實：** shell UID 2000 cannot invoke `setPackagesSuspendedAsUser()` on
  this build because it lacks `android.permission.SUSPEND_APPS`.
- **已證實：** this invocation did not reach a Fire-specific protected-package
  decision; it failed at the API permission check first.
- **已排除：** `pm suspend` as a shell-level route for changing Fire Launcher
  HOME state on the current build.
- **未知：** whether a privileged caller could suspend the package; testing
  that would require system/device-policy authority not available to ADB shell.

The idempotent rollback command is retained in the test directory, but was not
needed because the mutation was rejected before state change:

```text
adb -s G001LT0511550CFT shell pm unsuspend --user 0 com.amazon.firelauncher
```
