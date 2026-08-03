# Home event test summary

- Test ID: `HOME-T18`
- Serial: `G001LT0511550CFT`
- Action: `keyevent`
- Foreground preparation: `com.microsoft.launcher/.Launcher`
- Wake screen before preparation: `1`
- Dismiss keyguard before preparation: `1`
- Duration after action: `5` seconds
- Logcat cleared: `0`
- Action command status: `0`
- Finding status: `Hypothesis` for causal interpretation; raw state changes are observations.

## Evidence

- [Command manifest](command_manifest.tsv)
- [Before/after state focus](state_focus_lines.txt)
- [Full logcat](logcat_full.txt)
- [Focused logcat](logcat_focus.txt)
- [SHA-256 manifest](sha256sums.txt)

No conclusion about PackageManager, SystemUI, Framework or watchdog behavior is generated automatically.
