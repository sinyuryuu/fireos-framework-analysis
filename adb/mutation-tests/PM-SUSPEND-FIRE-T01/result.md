# PM-SUSPEND-FIRE-T01

## Command

```text
adb -s G001LT0511550CFT shell pm suspend --user 0 com.amazon.firelauncher
```

## Result

The command failed before package state mutation. PackageManager returned:

```text
Neither user 2000 nor current process has android.permission.SUSPEND_APPS.
```

The stack identifies `PackageManagerService.setPackagesSuspendedAsUser()` at
`PackageManagerService.java:14356`, called by
`PackageManagerShellCommand.runSuspend()` at line 1704.

## State comparison

- Fire Launcher remained `suspended=false`.
- HOME resolver remained `com.amazon.firelauncher/.Launcher`.
- HOME candidates remained Fire priority 50, Microsoft priority 0, and
  Settings fallback priority -1000.
- `mResumedActivity` and `mCurrentFocus` remained Fire Launcher.
- No restore command was needed because the mutation was rejected. The
  idempotent restore command is preserved in `restore.sh`.

## Classification

- Suspend API permission boundary: **Confirmed**
- Protected-package-specific rejection: **Not established**; the failure
  occurred earlier at the shell permission check.
- HOME change: **Disproved for this invocation**
- Device state changed: **Disproved**
