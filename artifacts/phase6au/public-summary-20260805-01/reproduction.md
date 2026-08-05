# Reproduction boundary

The raw capture remains local.  This public artifact was generated offline and
contains only selected markers and resolver output.

```sh
python3 tools/scripts/run_phase6au_shortcut_cache_test.py \
  --serial DEVICE_SERIAL \
  --output adb/phase6au/PHASE6AU-SHORTCUT-CACHE-PS7331-T02 \
  --test-id PHASE6AU-SHORTCUT-CACHE-PS7331-T02
```

The experiment clears only ShortcutService's cached launcher value, sends one
normal Home key, and conditionally restores the Fire HOME record only if the
post-Home resolver is not already the baseline.  It does not disable, hide,
suspend, uninstall, force-stop, or clear Fire Launcher.
