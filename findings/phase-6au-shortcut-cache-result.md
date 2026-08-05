# Phase 6AU：ShortcutService default-launcher cache experiment

## Objective

Phase 6AU tests a state surface that is separate from the PackageManager
preferred-activity record: Android 9's shell command
`cmd shortcut clear-default-launcher --user 0`. The question is whether this
cache controls HOME selection, or merely remembers the result selected by the
normal resolver.

This experiment does not repeat the priority matrix or ordinary
`set-home-activity` experiment. It does not modify Fire Launcher package or
component state, Settings Provider values, permissions, overlays, or system
partitions.

## Evidence

| Evidence ID | Observation | Confidence |
|---|---|---|
| `PHASE6AU-SHORTCUT-001` | Before mutation, `Cached launcher` and `Last known launcher` were Fire Launcher. | 已證實 |
| `PHASE6AU-SHORTCUT-002` | `cmd shortcut clear-default-launcher --user 0` returned `Success`. Immediately afterward, `dumpsys shortcut` showed both `Cached launcher: null` and `Last known launcher: null`. | 已證實 |
| `PHASE6AU-SHORTCUT-003` | With the cache null, HOME resolver still returned `priority=50 ... com.amazon.firelauncher/.Launcher`. | 已證實 |
| `PHASE6AU-SHORTCUT-004` | With the cache null, the current activity snapshot still had Fire Launcher resumed. | 已證實 |
| `PHASE6AU-SHORTCUT-005` | After one normal `KEYCODE_HOME`, ShortcutService repopulated both cache fields with Fire Launcher. | 已證實 |
| `PHASE6AU-SHORTCUT-006` | After the Home key, resolver and foreground activity remained Fire Launcher. | 已證實 |

The public, bounded evidence is in
`artifacts/phase6au/public-summary-20260805-01/`. The raw capture remains local
under `adb/phase6au/PHASE6AU-SHORTCUT-CACHE-PS7331-T02/`.

## Decision flow

```text
cmd shortcut clear-default-launcher
    ↓
ShortcutService cache = null
    ├─ PackageManager HOME resolver: Fire Launcher (unchanged)
    └─ current foreground: Fire Launcher (unchanged)

KEYCODE_HOME
    ↓
standard HOME resolution
    ↓
ShortcutService cache repopulated with Fire Launcher
```

## Finding

The cache is shell-writable and reversible, but it is not the controlling
decision point. Clearing it does not make a third-party Launcher a candidate,
does not change the formal HOME resolver, and does not alter the Home key
result. It is therefore classified as:

- **已證實：** independent cache state exists;
- **已證實：** cache can be cleared with a standard shell command;
- **已排除：** cache clearing is a HOME replacement or preferred-activity
  bypass;
- **高可信推論：** after a HOME launch, the cache is repopulated from the
  resolver's selected Fire Launcher rather than serving as the selector.

## Reproduction and rollback

```sh
python3 tools/scripts/run_phase6au_shortcut_cache_test.py \
  --serial DEVICE_SERIAL \
  --output adb/phase6au/PHASE6AU-SHORTCUT-CACHE-PS7331-T02 \
  --test-id PHASE6AU-SHORTCUT-CACHE-PS7331-T02
```

The test's only state mutation is `clear-default-launcher`; the normal Home key
repopulates the cache. The conditional baseline restore was not needed in T02,
and the device was left with Fire Launcher as both resolver result and resumed
activity. No reboot was performed.

## Consequence for the launcher project

This closes one more shell-visible state surface. The remaining practical
non-root result is the previously measured ADB-connected foreground monitor;
it is not a formal HOME replacement. The next useful work remains host-only
method closure of Amazon service callers or a separately measured, explicitly
user-authorized foreground alternative—not more cache-clearing variants.
