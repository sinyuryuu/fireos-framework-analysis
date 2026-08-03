# Phase 4B — Amazon callback control surface

## Confirmed static boundaries

| Boundary | Location | What it can do | Current conclusion |
|---|---|---|---|
| `VendorActivityStackSupervisorCallback.callResolveIntent` | `decompiled/jadx/systemui/sources/com/android/server/am/ActivityStackSupervisor.java:745-772` | return non-null before `PackageManagerInternal.resolveIntent` | **待驗證** whether current HOME returns Fire |
| `VendorPackageManagerCallback.callFilterComponentIntent` | `decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java:8246-8272` | omit a filter from resolver registration/removal | **待驗證** HOME-specific return |
| `AmazonUserManagerService$BinderService.enableKftLauncherComponent` | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54404` | hardcodes Tahoe FreeTime, Fire Launcher, and launcher3 in KFT/free-time component state calls | **高可信推論** profile-specific path, not proof of main-user HOME |
| `MigrationService.appsAvailable` | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:~33650` | broadcasts external-app availability to `com.amazon.firelauncher` | lifecycle notification, not resolver selection |
| `AppAdapterHandler.lambda$goHome$3` | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:~25745-26095` | starts implicit MAIN+HOME for a network issue path | no Fire component hardcode; standard HOME route |

The static artifacts do contain Amazon package references outside the core
chooser. Therefore the global statement “Amazon has no Fire package references”
is **已排除**. The narrower statement “the inspected core chooser does not
need a Fire package hardcode to produce the observed result” remains
**高可信推論**.

No unknown Binder transaction was called and no critical service was killed.
An exported/documented, shell-writable control point that changes the main HOME
component was not found.
