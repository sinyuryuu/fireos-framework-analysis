# Settings Home picker probe summary

- Test ID: `SETTINGS-T01`
- Route: `subsettings`
- Activity: `com.android.settings/.SubSettings`
- Fragment: `com.android.settings.applications.defaultapps.DefaultHomePicker`
- Fragment start status: `255` (a rejection may be expected for an invalid fragment)
- Restore Home status: `0`
- Finding status: `Hypothesis` until raw activity/logcat/UI outputs are reviewed.

## Evidence

- [Command manifest](command_manifest.tsv)
- [Fragment start output](open_fragment.txt)
- [Fragment UI dump](fragment_ui.xml)
- [Focused state lines](state_focus_lines.txt)
- [Focused logcat](logcat_focus.txt)
- [SHA-256 manifest](sha256sums.txt)

The probe never selects a launcher, calls a package-state mutation, or writes default-app data.
