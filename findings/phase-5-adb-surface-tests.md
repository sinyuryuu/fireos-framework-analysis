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

## PM-HIDE-FIRE-T01

The second previously untested shell route was:

```text
adb -s G001LT0511550CFT shell pm hide --user 0 com.amazon.firelauncher
```

It returned exit code 255 before changing state:

```text
Neither user 2000 nor current process has android.permission.MANAGE_USERS.
```

The relevant stack is:

```text
PackageManagerService.setApplicationHiddenSettingAsUser(PackageManagerService.java:14100)
PackageManagerShellCommand.runSetHiddenSetting(PackageManagerShellCommand.java:1644)
```

After the rejected call, `hidden=false`, the resolver remained
`com.amazon.firelauncher/.Launcher`, and Fire remained the resumed/focused
activity. The complete before/after records are under
`adb/mutation-tests/PM-HIDE-FIRE-T01/` and
`adb/mutation-tests/PM-HIDE-FIRE-T01-after/`.

Classification:

- **已證實：** shell UID 2000 lacks `MANAGE_USERS` for this hidden-state API.
- **已證實：** the request failed before a Fire-specific hidden/protected
  package decision.
- **已排除：** `pm hide` as a shell-level HOME bypass on this build.
- **未知：** behavior from a privileged/device-policy caller; that is outside
  current ADB authority.

## PM-UNINSTALL-FIRE-T01

The next distinct user-state route was tested once:

```text
adb -s G001LT0511550CFT shell pm uninstall --user 0 com.amazon.firelauncher
```

The command returned exit code `1`:

```text
Failure [DELETE_FAILED_INTERNAL_ERROR]
```

The complete pre/post snapshots and the raw mutation output are under
`adb/mutation-tests/PM-UNINSTALL-FIRE-T01/` and
`adb/mutation-tests/PM-UNINSTALL-FIRE-T01-after/`. The post-state remained:

```text
installed=true hidden=false suspended=false stopped=false enabled=0
HOME=com.amazon.firelauncher/.Launcher priority=50
```

The corresponding PackageManager log is:

```text
PackageManager: Attempted to delete protected package: com.amazon.firelauncher
```

Rollback was verified with:

```text
adb -s G001LT0511550CFT shell pm install-existing --user 0 com.amazon.firelauncher
```

It returned `Package com.amazon.firelauncher installed for user: 0`; the
package was already installed because the uninstall request was rejected.

Classification:

- **已證實：** the user-0 uninstall route is rejected for Fire Launcher on
  this build and logs an explicit protected-package deletion warning.
- **已證實：** no package state, HOME resolver state, or foreground state
  changed.
- **已排除：** `pm uninstall --user 0` as a shell-level route for removing
  Fire Launcher from HOME on this build.
- **未知：** whether a privileged caller could remove the package; that is
  outside the current ADB authority and is not a safe next experiment.
