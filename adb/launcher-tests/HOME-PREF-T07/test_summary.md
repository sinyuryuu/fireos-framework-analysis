# Preferred HOME runtime probe summary

- Test ID: `HOME-PREF-T07`
- Serial: `G001LT0511550CFT`
- Preferred target: `com.microsoft.launcher/.Launcher`
- Restore target: `com.amazon.firelauncher/.Launcher`
- Preparation component: `com.android.settings/.Settings`
- Home action: `keyevent`
- `set-home-activity` target exit status: `0`
- Home action exit status: `0`
- `set-home-activity` restore exit status: `0`
- Causal status: `Hypothesis` until the resolver, foreground, and logcat snapshots are reviewed.

The final resolver state is authoritative for whether restoration completed.
