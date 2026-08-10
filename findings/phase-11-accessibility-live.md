# Phase 11 — user-enabled Accessibility redirect observation

## Scope and safety

This phase tested only the already user-enabled research Accessibility service
`org.fireosresearch.phase4.redirect/org.fireosresearch.phase4.redirect.LauncherRedirectService`.
No Settings value, package state, permission, Fire Launcher data/state, Binder
transaction, driver I/O, reboot, or OTA operation was performed. Each probe
opened Settings, sent one `KEYCODE_HOME`, captured state/logcat, and explicitly
started the Fire Launcher as a foreground guard.

Raw evidence:

- `adb/phase11/PHASE11-ACCESSIBILITY-LIVE-T01/`
  - SHA-256 manifest: `b39c8a6af0e6c1f2ad67afff846743590d5db6b177211568de530503a56eda58`
- `adb/phase11/PHASE11-ACCESSIBILITY-LIVE-T02/`
  - SHA-256 manifest: `55425b27973d330dc72e0c08e19aa0a4df17018763a296f4db8ef73d8273ec88`
- Probe script SHA-256: `de34769ad49280898ea1a88344c18f40b6ef00dc8bf4e2054f5d94c4bfd5ba4f`

## Results

| Test | Service bound before HOME | Foreground after HOME | Formal HOME | Classification |
|---|---:|---|---|---|
| T01 | not stable at event time | Fire Launcher | Fire priority 50 | service lifecycle race; no redirect observed |
| T02 | yes | Fire Launcher | Fire priority 50 | redirect failed despite bound service |

T02 is the stronger result: the service was present in
`dumpsys accessibility` before the key event, but the resumed activity remained
`com.amazon.firelauncher/.Launcher`; the redirect package was not observed in
the foreground. The setting remained user-enabled after the probe, and the
service could rebind asynchronously, so this is not a claim that the service
was disabled by the probe.

## Verdict

**Confirmed:** the current research Accessibility implementation did not
provide a reliable Home-key redirect under the tested PS7331 state. The formal
HOME resolver was unchanged in both tests.

**Disproved for this APK/path:** a single user-enabled Accessibility service
can be treated as a reliable replacement for Fire Launcher.

**Not disproved:** every possible Accessibility implementation or future APK
variant. Any new variant would require separate user consent and its own
before/after evidence; it must not intercept passwords, read screen text, or
automatically grant itself access.
