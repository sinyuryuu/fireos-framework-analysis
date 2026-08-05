# Reproduction boundary

The raw capture remains local under `adb/phase6at/PHASE6AT-ADB-HOME-MONITOR-PS7331-T02`.  This public artifact was
generated offline and contains only bounded, serial-redacted evidence.

```sh
python3 tools/scripts/run_adb_home_monitor.py \
  --serial DEVICE_SERIAL \
  --target org.fireosresearch.phase4.alias/.HomeActivity \
  --iterations 30 \
  --wait-after-home 2.0 \
  --test-id PHASE6AT-ADB-HOME-MONITOR-PS7331-T02 \
  --output adb/phase6at/PHASE6AT-ADB-HOME-MONITOR-PS7331-T02
```

The monitor uses `input keyevent 3`, observes ActivityManager log events, and
uses `am start -W -n` for the explicitly supplied research Activity.  It does
not disable, hide, suspend, uninstall, force-stop, or clear Fire Launcher; it
does not write Settings, reboot, call unknown Binder transactions, or write a
partition.

Verify the public artifact:

```sh
(cd "$(dirname this-file)" && shasum -a 256 -c sha256sums.txt)
```

This route requires an active ADB connection and is therefore temporary.  The
formal HOME resolver remains the Fire Launcher before and after the run.
