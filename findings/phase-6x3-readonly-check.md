# Phase 6X3 post-synthesis read-only device check

Timestamp: 2026-08-10 (local run; exact command output preserved below)  
Serial: `G001LT0511550CFT`  
Classification: **已證實／read-only observation**

## Commands

```sh
adb -s G001LT0511550CFT get-state
adb -s G001LT0511550CFT shell cmd package resolve-activity --brief --user 0 -a android.intent.action.MAIN -c android.intent.category.HOME
adb -s G001LT0511550CFT shell cmd package query-activities --brief --user 0 -a android.intent.action.MAIN -c android.intent.category.HOME
adb -s G001LT0511550CFT shell dumpsys package com.amazon.firelauncher
```

The final command was locally filtered only for `Preferred Activities User 0`,
`User 0`, `User 10`, and `enabled=` lines for display; no device-side filtering
changed state.

## Observed output

```text
device
priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
com.amazon.firelauncher/.Launcher
3 activities found:
  Activity #0:
    priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
    com.amazon.firelauncher/.Launcher
  Activity #1:
    priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
    com.microsoft.launcher/.Launcher
  Activity #2:
    priority=-1000 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
    com.android.settings/.FallbackHome
339:Preferred Activities User 0:
857:    User 0: ceDataInode=852182 installed=true hidden=false suspended=false stopped=false notLaunched=false enabled=0 instant=false virtual=false
868:    User 10: ceDataInode=827498 installed=true hidden=false suspended=false stopped=false notLaunched=false enabled=2 instant=false virtual=false
877:  User 0:
```

## Interpretation

The current User 0 resolver still selects Fire Launcher. Microsoft Launcher
remains a candidate at effective priority 0, and FallbackHome remains at -1000.
The User 10 state is separate and does not demonstrate a User 0 permission or
package-state change.

No `set`, `disable`, `enable`, `install`, `uninstall`, `clear`, `suspend`,
`settings put`, private Binder transaction, driver access, reboot, or partition
operation was executed in this check.
