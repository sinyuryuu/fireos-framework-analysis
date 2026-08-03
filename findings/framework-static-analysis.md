# Framework and system-service static analysis

## Inputs

- Fire OS framework/services analysis uses the existing 183-byte shell JAR
  metadata plus VDEX/ODEX extraction outputs. The code-bearing references are
  `decompiled/baksmali/vdexExtractor/services/disassembly.log` and
  `fosservices/disassembly.log`.
- Fire OS JADX sources are retained as approximate Java only; key control-flow
  decisions are checked against the VDEX listings.
- AOSP Android 9 r1 and r61 sources are used for the selected resolver methods.

## ActivityManager and ActivityStackSupervisor

`ActivityManagerService.startHomeActivityLocked()` obtains a HOME intent,
resolves it if no explicit component is present, sets the resolved component,
and starts it. This explains why ActivityManager START logs show an explicit
Fire component even when the originating intent was implicit.

Fire's `ActivityStackSupervisor.resolveIntent()` invokes the vendor callback
aggregator before PackageManagerInternal. The aggregator returns the first
non-null callback result. This is the most important unresolved Amazon control
point. The inspected concrete `AppCompatActivityStackSupervisorCallback`
queries the normal PM service and only filters an uninstalled result; it does
not target Fire Launcher.

## PackageManager

The selected Fire OS methods retain the Android 9 method family:

- `resolveIntent` / `resolveIntentInternal`: `PackageManagerService.java:3003-3022`
- `chooseBestActivity`: `:3120-3168`
- `findPersistentPreferredActivityLP`: `:3197-3275`
- `findPreferredActivity`: `:3288-3350`

The method structure compares candidate priority before consulting the ordinary
preferred resolver on the tie path. No explicit `com.amazon.firelauncher`
condition was found in these selected methods. The runtime candidate list and
the Phase 3A stored Microsoft record agree with this explanation.

## PhoneWindowManager and Amazon key policy

The VDEX path is:

`handleShortPressOnHome` → `KeyPolicyManager.handleShortPressOnHome` →
`launchHomeFromHotKey` → `startDockOrHome`.

`startDockOrHome` has two vendor callback opportunities before the final
`startActivityAsUser(mHomeIntent, CURRENT)`. The Amazon tablet key policy
builds a normal `MAIN` + `HOME` intent when it launches Home. Its custom-home
handler targets the foreground application's permissioned receiver, not Fire.

## LauncherHijackPreventer

The inspected callback checks whether a caller may see the Home task using the
SELinux policy `amazon_policies/see_home_task`, with an Android-signature
fallback. It explains the observed SELinux denials in prior logs and is a
visibility/protection layer; the inspected method does not start Fire Launcher.

## Static-analysis limits

The current input does not include a clean, public source reconstruction for
every concrete FOS callback or the complete Amazon `SystemServer` initializer.
Therefore this report labels callback causality and boot-time preferred-record
rewrites as unknown rather than filling them with inferred behavior.
