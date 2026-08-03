# Settings Home entrypoint probe summary

- Test ID: `HOME-T21`
- Serial: `G001LT0511550CFT`
- Settings intent: `android.settings.HOME_SETTINGS`
- Open command status: `0`
- Restore Home status: `0`
- Finding status: `Hypothesis` until activity/UI outputs are reviewed.

## Evidence

- [Command manifest](command_manifest.tsv)
- [Settings UI dump](settings_ui.xml)
- [State focus lines](state_focus_lines.txt)
- [Focused logcat](logcat_focus.txt)
- [SHA-256 manifest](sha256sums.txt)

The probe does not select a launcher or write default-home settings; it only opens the exported Settings entrypoint and restores Home.
