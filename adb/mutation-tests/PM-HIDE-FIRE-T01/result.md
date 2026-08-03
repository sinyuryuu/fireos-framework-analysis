# PM-HIDE-FIRE-T01

## Command

```text
adb -s G001LT0511550CFT shell pm hide --user 0 com.amazon.firelauncher
```

## Result

The command failed before package state mutation. PackageManager returned:

```text
Neither user 2000 nor current process has android.permission.MANAGE_USERS.
```

The stack identifies `PackageManagerService.setApplicationHiddenSettingAsUser()`
at `PackageManagerService.java:14100`, called by
`PackageManagerShellCommand.runSetHiddenSetting()` at line 1644.

## Classification

- Hidden-state shell permission boundary: **Confirmed**
- Protected-package-specific rejection: **Not established**; the failure
  occurred at the API permission check first.
- HOME change: **Disproved for this invocation**
- Device state changed: **Disproved**

The after snapshot is in
`adb/mutation-tests/PM-HIDE-FIRE-T01-after/`. The idempotent rollback command
is preserved in `restore.sh`, but was not needed.
