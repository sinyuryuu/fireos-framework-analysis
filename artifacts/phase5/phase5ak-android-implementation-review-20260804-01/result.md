# Phase 5AK result

- Device state capture: read-only and complete.
- Accessibility service: not enabled (`services:{}`).
- Formal HOME resolver: `com.amazon.firelauncher/.Launcher`, effective priority 50.
- Redirect APK: installed artifact hash matches the prepared key-event + PendingIntent build.
- PendingIntent measurement: not executed because the required Settings consent was absent.
- Root/CVE implementation: source-level applicability review only; no native payload or
  kernel trigger was run.
- Confidence: the Android API boundary and current state are confirmed; redirect success
  remains unmeasured.
