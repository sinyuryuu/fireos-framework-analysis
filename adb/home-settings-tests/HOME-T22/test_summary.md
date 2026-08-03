# Launcher App info Settings probe summary

- Test ID: `HOME-T22`
- Serial: `G001LT0511550CFT`
- Package: `com.amazon.firelauncher`
- App info open status: `0`
- Restore Home status: `0`
- Finding status: `Hypothesis` until activity/UI outputs are reviewed.

## Evidence

- [Command manifest](command_manifest.tsv)
- [App info UI dump](app_info_ui.xml)
- [State focus lines](state_focus_lines.txt)
- [Focused logcat](logcat_focus.txt)
- [SHA-256 manifest](sha256sums.txt)

The probe does not click or select the Home-app preference; it only opens App info and restores Home.
