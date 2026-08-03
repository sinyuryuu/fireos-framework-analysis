# Phase 4 user-consented Accessibility redirect (source-only harness)

This is an optional approximation experiment, not a HOME replacement. It
requires the device owner to install the APK and manually enable the service in
Android Settings. It never requests or automates that consent.

The service observes only `TYPE_WINDOW_STATE_CHANGED` events whose package is
`com.amazon.firelauncher`. It does not read window text, input content, the
view tree, passwords, or notifications. It has an explicit in-app enable
toggle, a cooldown and loop guard, and starts only the explicitly named Phase
4 test activity. Remove the APK or disable the service to roll back.

No network permission, device-admin declaration, background service, overlay,
or private Binder call is present. The project intentionally does not ship an
APK in Git; build and sign locally with the same raw SDK toolchain as the Phase
4 alias probe, recording a SHA-256 and the signing key outside the repository.

The completed KFTRWI T03 run used the following staged runner:

```sh
tools/scripts/run_phase4_accessibility_experiment.sh --phase prepare \
  --serial SERIAL --test-id PHASE4-ACCESSIBILITY-T03 \
  --redirect-apk PATH_TO_REDIRECT_APK --alias-apk PATH_TO_ALIAS_APK \
  --output adb/phase4/PHASE4-ACCESSIBILITY-T03 \
  --approve-state-change \
  --approval-phrase 'APPROVE PHASE4-PHASE4-ACCESSIBILITY-T03'
```

After manually enabling the service and visible toggle in Settings, the
measurement command is:

```sh
tools/scripts/run_phase4_accessibility_experiment.sh --phase measure \
  --serial SERIAL --test-id PHASE4-ACCESSIBILITY-T03 \
  --redirect-apk PATH_TO_REDIRECT_APK --alias-apk PATH_TO_ALIAS_APK \
  --output adb/phase4/PHASE4-ACCESSIBILITY-T03 --iterations 30 \
  --manual-consent-confirmed \
  'CONFIRM MANUAL ACCESSIBILITY CONSENT FOR PHASE4-ACCESSIBILITY-T03'
```

The measured result was 0/30 foreground handoffs. Logcat recorded explicit
redirect attempts, but the target remained task history/last-paused while
`com.amazon.firelauncher/.Launcher` remained resumed. This implementation is
not a reliable workaround on this build.

Required manual sequence for a future run:

1. Install the locally built test APK.
2. Install the Phase 4 alias APK.
3. Open the redirect app and turn on its visible toggle.
4. Manually enable its Accessibility service in Settings.
5. Measure Home/unlock behavior with the Phase 4 runner.
6. Turn the toggle off, disable the service in Settings, remove both test APKs,
   and verify Fire resolver/foreground.

The service is never enabled automatically. For rollback, manually turn off
the visible toggle and disable the service in Settings, then run:

```sh
tools/scripts/run_phase4_accessibility_experiment.sh --phase rollback \
  --serial SERIAL --test-id PHASE4-ACCESSIBILITY-T03 \
  --output adb/phase4/PHASE4-ACCESSIBILITY-T03 \
  --approve-state-change \
  --approval-phrase 'APPROVE PHASE4-PHASE4-ACCESSIBILITY-T03'
```

The service must be disabled in Settings before rollback; the script refuses
to uninstall either research APK while the service remains enabled. The
verified rollback is recorded in
`adb/phase4/PHASE4-ACCESSIBILITY-T03/rollback-result-verified.md`.
