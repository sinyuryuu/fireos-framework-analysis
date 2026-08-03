# Launcher App info Settings probe summary

- Test ID: `HOME-T23`
- Serial: `G001LT0511550CFT`
- Package: `com.amazon.firelauncher`
- App info open status: `0`
- Home-app row tap requested: `1`
- Home-app row tap status: `0`
- Restore Home status: `0`
- Finding status: `Hypothesis` until activity/UI outputs are reviewed.

## Evidence

- [Command manifest](command_manifest.tsv)
- [App info UI dump](app_info_ui.xml)
- [State focus lines](state_focus_lines.txt)
- [Focused logcat](logcat_focus.txt)
- [SHA-256 manifest](sha256sums.txt)

The probe tapped only the visible Home-app row and recorded the resulting screen; it did not select a launcher or write the default.
