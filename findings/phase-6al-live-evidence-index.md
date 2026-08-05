# Phase 6AL live evidence index

| Evidence ID | Source file | Command / observation | Interpretation | Confidence |
|---|---|---|---|---|
| `6AL-LIVE-001` | `adb/phase6al/PHASE6AL-HOME-20260805-01/fingerprint.stdout.txt` | `adb -s G001LT0511550CFT shell getprop ro.build.fingerprint` → PS7331.4463N | Current device matches the analyzed Fire OS build | Confirmed |
| `6AL-LIVE-002` | `adb/phase6al/PHASE6AL-HOME-20260805-01/home_resolve.stdout.txt` | `cmd package resolve-activity --brief --user 0 -a MAIN -c HOME` → priority 50, Fire Launcher | Formal resolver still selects Fire | Confirmed |
| `6AL-LIVE-003` | `adb/phase6al/PHASE6AL-HOME-20260805-01/activity_state.stdout.txt`; `window_state.stdout.txt` | `mResumedActivity` and `mCurrentFocus` are Fire Launcher | Foreground state agrees with resolver result | Confirmed |
| `6AL-LIVE-004` | `adb/phase6al/PHASE6AL-LIVE-20260805-01/service_check_*.stdout.txt` | Standard `service check` found `fosdebug`, `amazonthermalservice`, `otadexopt` | Only standard dump surfaces were sampled; no private transaction was sent | Confirmed |
| `6AL-LIVE-005` | `adb/phase6al/PHASE6AL-HOME-20260805-01/metadata.json`; `PHASE6AL-LIVE-20260805-01/metadata.json` | `device_mutation=false`, `settings_changed=false`, `package_state_changed=false`, `unknown_binder_transaction=false` | Capture did not alter the device | Confirmed |

All raw files are retained; see each capture directory's `sha256sums.txt`.
