# Phase 4B — assisted workaround assessment

## Candidate: user-consented Accessibility redirect

The proposed harness is source-only in this commit under
`tools/phase4-accessibility/` (or the documented Phase 4 test harness when
present). It must be manually enabled by the device owner, listens only for
`TYPE_WINDOW_STATE_CHANGED`, does not read window text or input, uses an
explicit Fire-package filter, cooldown, loop guard, visible stop control, and
starts a test launcher explicitly. It cannot change PackageManager's HOME
resolver.

## Classification after live measurement

* True HOME replacement: **否**.
* This implementation's Home-key workaround: **已排除** (0/30 foreground
  redirects).
* Unlock workaround: **待驗證**.
* Required authorization: user must enable Accessibility in Settings.
* Reboot persistence: **待驗證**; no reboot was run after the failed
  foreground-start result.
* Main observed failure boundary: background activity start was logged as
  stopped; the explicit target remained task history rather than resumed.
* Rollback: disable the service in Settings, uninstall the test APK, and verify
  Fire resolver/foreground; do not modify Fire Launcher.

The implementation was not auto-enabled and did not automate consent. The
manual consent and rollback were completed; no Fire package state was changed.
