# Phase 3C startup-failure and fallback analysis

No crash, forced-stop, missing-activity, or intentionally failing Launcher was
executed. The p0 APK was a normal reversible test app. This avoids a crash
loop or a preferred component without a recovery Activity.

p0 was installed only for PHASE3C-PREFERRED-P0-02, removed with pm uninstall --user 0
exit 0, and absent from the final pm path. Fire remained installed, visible,
unsuspended, unstopped, and enabled. Final HOME resolver and foreground were
Fire.

待驗證: retry limits and fallback behavior after a test component fails. The
smallest safe next test is a dedicated recovery-first APK; it was deferred.
