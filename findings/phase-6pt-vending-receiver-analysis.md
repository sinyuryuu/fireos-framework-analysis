# Phase 6PT — Play Store launcher receiver analysis

## Scope

Host-only analysis of the preserved PS7331 Play Store base/split APK corpus. No
ADB command, broadcast, PendingIntent construction, package mutation, permission
mutation, install/start, or device-state change was performed.

## Evidence

- Base APK SHA-256: `a5f456832018bbf571f915e949ea9dcd707ad514c269899e916b9b25d5297a50`
- ARM64 split SHA-256: `b59980b4c8764f59c20289c19935fa4da497d799e2a4763ca163c5ef1928f90a`
- Japanese split SHA-256: `b55b5c31a778187abb394f169e95af79844ac93cfd4b242ea58383e6531df0ed`
- Recovered receiver SHA-256: `71d17a064272f88d02f4619a2f4fa6fedf0ae91a233c29e0ad6d4110643b6b47`
- Reproduction script: `tools/scripts/audit_phase6ps_vending_launcher_receiver.py`

## Findings

### Confirmed

The manifest exports `com.google.android.finsky.setup.LauncherConfigurationReceiver`
for `com.android.launcher3.action.FIRST_SCREEN_ACTIVE_INSTALLS` without a receiver
permission in the inspected block:
`artifacts/phase6mb-vending-static-20260810-01/manifest-print.txt:1470-1479`.

The recovered method first reads a `verificationToken` PendingIntent, identifies
its creator package, and checks that creator against the current `MAIN + HOME`
resolution. A mismatch is rejected unless the creator is independently verified
as a HOME candidate and setup state permits it. It then consumes launcher-layout
arrays and updates Play Store's `aoba` restore tracker before calling `aofc.y`.

### Strong evidence

The receiver is a Play Store homescreen-install/restore metadata path, not the
formal Android HOME resolver. The inspected method has no direct
`setComponentEnabledSetting`, `setApplicationEnabledSetting`,
`replacePreferredActivity`, Fire Launcher literal, or explicit Fire HOME launch.
The recovered `uez` preferred writer is limited to `WEB_SEARCH + DEFAULT`, not
`MAIN + HOME`.

### Unknown

JADX originally skipped the receiver body and the downstream `aofc` implementation
has partially unresolved regions. Native libraries, resources, and failed DEX
regions were not treated as negative evidence. Closing those regions needs a
host-only smali/DEX/native audit; invoking the exported receiver is out of scope.

## Decision

**Bounded negative for a Fire Launcher/HOME bypass.** This surface is retained as
an exported metadata-integrity research item, not as a privilege-escalation or
launcher-replacement candidate.

