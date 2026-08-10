# Phase 6PD — Accessibility PendingIntent package boundary

## Scope

This record documents one bounded, non-destructive package-update attempt on
the authorized PS7331 device. It does not claim a HOME replacement and does
not measure the PendingIntent variant at runtime.

Test ID: `PHASE6PD-ACCESSIBILITY-PENDINGINTENT-T01`

Device: `G001LT0511550CFT`  
Build: `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`  
Target user: `0`

## Observed result

The host attempted to update the already-installed research package
`org.fireosresearch.phase4.redirect` with the PendingIntent build from
`tools/phase4-accessibility/dist/20260804-pendingintent-jdk17-01/`.

The package manager returned:

`INSTALL_FAILED_UPDATE_INCOMPATIBLE: Package org.fireosresearch.phase4.redirect signatures do not match previously installed version; ignoring!`

The command exited with status `1`. No replacement occurred. The existing
package path, Accessibility service registration, HOME resolver, and resumed
activity remained unchanged in the captured post-attempt output.

## Safety boundary

The attempt did not uninstall a package, write Settings or DeviceConfig,
toggle Accessibility, install the alias APK, mutate Fire Launcher, reboot,
send a private Binder transaction, open a device node, or write a system
image. No rollback was required because PackageManager rejected the update
before changing package state.

The existing research APK must not be removed merely to bypass this signature
boundary. A future runtime measurement requires a separately named research
package, or the original signing key; it also requires explicit, manual
Accessibility consent on the device. The current source/build scripts use
hard-coded `phase4` package and component names, so renaming only the APK
file is insufficient.

## Evidence classification

- **Confirmed:** Android rejected the update before replacing the installed
  research package because the signing certificates differed.
- **Confirmed:** The existing package remained installed and the captured HOME
  result remained `com.amazon.firelauncher/.Launcher`.
- **Unknown:** The rejected PendingIntent build's runtime behavior on this
  device.
- **Not tested:** Any uninstall/reinstall route, because it would reset the
  manual-consent/package state boundary and was unnecessary for this result.

## Reproduction

The exact command and raw result are preserved in:

`adb/phase6pd/PHASE6PD-ACCESSIBILITY-PENDINGINTENT-T01/mutation-attempt.txt`

The pre-change snapshot and pulled installed APK are preserved in the same
test directory. The snapshot is read-only evidence; it is not a restoration
script and must not be used to blindly overwrite device settings.

