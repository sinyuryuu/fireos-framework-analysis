# Phase 6AT：ADB-connected HOME foreground monitor

## Scope

This is a new, bounded runtime measurement on PS7331. It does not repeat the
Phase 3A priority matrix or the earlier Accessibility/PendingIntent result.
The monitor keeps an ADB connection open, sends `KEYCODE_HOME`, watches the
ActivityManager log for Fire Launcher becoming resumed, and then starts an
explicit research Activity with `am start -W -n`.

The test never disabled, hid, suspended, uninstalled, force-stopped, or cleared
Fire Launcher. It did not write Settings, call an unknown Binder transaction,
reboot, remount a partition, or write a system image.

## Result

| Evidence ID | Observation | Classification |
|---|---|---|
| `PHASE6AT-ADB-MONITOR-001` | 30/30 iterations observed a Fire Launcher foreground event. | 已證實 |
| `PHASE6AT-ADB-MONITOR-002` | 30/30 iterations sent the explicit research Activity after that event. | 已證實 |
| `PHASE6AT-ADB-MONITOR-003` | 30/30 final foreground dumps contained `org.fireosresearch.phase4.alias/.HomeActivity`. | 已證實 |
| `PHASE6AT-ADB-MONITOR-004` | HOME resolver before and after remained `priority=50 ... com.amazon.firelauncher/.Launcher`. | 已證實 |
| `PHASE6AT-ADB-MONITOR-005` | The measured path requires the host-side monitor and an active ADB connection; reboot persistence was not established. | 已證實 |
| `PHASE6AT-ADB-MONITOR-006` | ActivityManager evidence shows Fire Launcher is resumed first and the test Activity is started afterward. This implies visible foreground handoff/flicker is possible. | 高可信推論 |

The public, serial-redacted evidence is in
`artifacts/phase6at/public-summary-20260805-01/`. The complete raw capture is
kept locally under
`adb/phase6at/PHASE6AT-ADB-HOME-MONITOR-PS7331-T02/` and is not committed.

## Interpretation

This is a **temporary ADB foreground workaround**, not a formal HOME
replacement:

```text
KEYCODE_HOME
    -> standard resolver selects Fire Launcher (priority 50)
    -> ActivityManager reports Fire Launcher resumed
    -> host monitor observes the event
    -> ADB shell starts the research Activity explicitly
    -> research Activity is foreground in the final snapshot
```

The unchanged resolver proves that the monitor does not alter the selected
HOME component. It also does not prove that the route is reliable after ADB
disconnect, process death, SystemUI restart, lock/unlock, or reboot; those are
separate measurements.

## Reproduction

The host-side implementation is
`tools/scripts/run_adb_home_monitor.py`. It requires an explicit serial and
refuses a Fire Launcher target:

```sh
python3 tools/scripts/run_adb_home_monitor.py \
  --serial DEVICE_SERIAL \
  --target org.fireosresearch.phase4.alias/.HomeActivity \
  --iterations 30 \
  --wait-after-home 2.0 \
  --test-id PHASE6AT-ADB-HOME-MONITOR-PS7331-T02 \
  --output adb/phase6at/PHASE6AT-ADB-HOME-MONITOR-PS7331-T02
```

The public exporter is offline and has a dry-run mode:

```sh
python3 tools/scripts/build_phase6at_public_summary.py --dry-run \
  --source adb/phase6at/PHASE6AT-ADB-HOME-MONITOR-PS7331-T02 \
  --output artifacts/phase6at/public-summary-20260805-01
```

The artifact manifest was verified with `shasum -a 256 -c sha256sums.txt`.

## Rollback and current state

The monitor process has stopped. A normal `KEYCODE_HOME` was sent afterward;
the device returned to `com.amazon.firelauncher/.Launcher`, ADB remained in
`device` state, and the resolver remained unchanged. This foreground restore
does not claim that the separate, previously enabled Accessibility service and
research packages have been manually rolled back; that state is tracked by
the earlier Phase 5CQ artifact.

## Assessment

- **Viable:** only as a host-connected, temporary foreground redirect.
- **Not viable:** as a persistent HOME resolver replacement.
- **Not demonstrated:** reboot persistence, ADB-disconnect behavior, or a
  no-flicker handoff.
- **Safety boundary:** no Fire Launcher mutation and no partition/framework
  write occurred.
