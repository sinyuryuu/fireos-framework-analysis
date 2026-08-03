# Phase 4B — existing workaround families

This phase records design patterns without installing unverified binaries.

| Family | Typical API shape | Fire Launcher mutation required | Assessment |
|---|---|---:|---|
| Fire Toolbox / LauncherHijack-era tools | monitor current task and start explicit third-party launcher | historically often yes or accessibility | version- and build-dependent; inspect source before use |
| Launcher manager / package-state tools | `set-home-activity`, disable/hide, protected package operations | often yes | ordinary preferred path is disproved on this build |
| Accessibility redirect | user-enabled `AccessibilityService`, observe window changes, explicit start | no | closest reversible approximation; requires consent and may flash/lag |
| UsageStats observer | foreground observation then explicit start | no | weaker reliability and background limits |
| overlay/notification/quick tile | user-triggered explicit shortcut | no | stable entry point, not HOME replacement |

## Public-source review

### LauncherHijack (source reviewed; no binary installed)

The public [LauncherHijack repository](https://github.com/BaronKiko/LauncherHijack)
describes an Accessibility-based launcher redirection design and marks the
project deprecated. Its public [HELP.md](https://github.com/BaronKiko/LauncherHijack/blob/master/HELP.md)
documents manual Accessibility enablement and warns that a killed launcher
process can require a second Home press. It also documents an optional
"corrupt default launcher" path; that path is intentionally classified as
**因風險拒絕測試** here because it damages package state and may require a
new user or stronger recovery. No APK or binary from that repository was
installed, and its historical package-block assumptions were not applied to
this Fire OS build.

The design is relevant as a prior art comparison, not as proof of behavior on
KFTRWI. The local harness in `tools/phase4-accessibility/` is independently
source-built, has no network permission, does not automate consent, and is
only an explicit foreground redirect.

## Live device result — T03

After manual consent in Settings and a visible toggle, the corrected harness
ran 30 controlled cycles from `adb/phase4/PHASE4-ACCESSIBILITY-T03/`. Each
cycle sent `KEYCODE_HOME` while the test package was present. The service
logged 30 explicit redirect attempts, but the foreground snapshots recorded
`mResumedActivity=com.amazon.firelauncher/.Launcher` in all 30 cycles. The
alias appeared only as a task/last-paused record; it never became the resumed
or focused activity. Logcat includes the Android background-start boundary
`Activity start request ... stopped`.

Therefore this tested Accessibility implementation achieved **0/30 (0%)**
foreground redirects on the device. It is **已排除** as a reliable Home-key
workaround for this build and implementation, while the broader class of
user-consented accessibility designs remains **待驗證**. It did not alter the
HOME resolver. The service was manually disabled, both research APKs were
removed, and the final resolver/ADB checks passed; see
`adb/phase4/PHASE4-ACCESSIBILITY-T03/rollback-result-verified.md`.

No unknown APK or binary was installed. Any future public-project review must
record source URL, commit, permissions, digest, and whether it disables Fire
Launcher. A redirect must never be described as a true HOME replacement.
