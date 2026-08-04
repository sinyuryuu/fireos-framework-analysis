# PHASE5BD-ACCESSIBILITY-PENDINGINTENT-T01 result

## Scope

This was a user-consented, reversible foreground-redirect measurement on the
existing research APKs. The Accessibility service was already enabled in
Settings before the test. The visible app-local redirect toggle was changed
from off to on for the measurement and then restored to off.

No Settings provider key was written. `com.amazon.firelauncher` was not
stopped, disabled, hidden, suspended, uninstalled, force-stopped, or cleared.
No reboot, unknown Binder call, root payload, kernel trigger, ioctl, or boot
operation was performed.

## Observed result

| Metric | Result |
|---|---:|
| Iterations | 30 |
| PendingIntent dispatch log entries | 30 |
| Samples with alias package resumed/focused | 0/30 |
| Samples with alias window/task present | 30/30 |
| Final formal HOME resolver | `com.amazon.firelauncher/.Launcher` |
| Final toggle | `Redirect stopped` |
| Final Accessibility service setting | unchanged; service remained user-enabled as at baseline |

The dispatches were triggered by the observed Fire Launcher window event. The
log contains `Activity start request from 10189 stopped` for the redirect UID;
the later shell-launched probe activity is a separate UID-2000 start. In the
sampled state, Fire Launcher remained `mResumedActivity` and `mCurrentFocus`.

## Classification

- Formal HOME replacement: **No**.
- Stable Home-key workaround: **Disproved for this PendingIntent variant**
  under the recorded PS7330 conditions (0/30 stable handoffs).
- Transient task/window side effect: **Observed**, but not a usable launcher
  replacement.
- Rollback: **Completed**; the visible toggle returned to its original off
  state and the resolver remained Fire Launcher.

Raw before/after snapshots, all per-iteration dumps, logcat, commands, exit
codes and SHA-256 manifests are preserved in this directory.
