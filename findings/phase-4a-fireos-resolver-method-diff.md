# Phase 4A — Fire OS resolver method diff

## Method-level result

The selected Fire OS PackageManagerService methods are AOSP-shaped for the
central chooser. The Fire Java output is partly decompiler-generated; where a
method contains an unsupported/dead block, the report leaves the conclusion
bounded instead of filling in missing logic.

| Method | Fire location | AOSP comparison | Classification |
|---|---|---|---|
| `chooseBestActivity` | `decompiled/jadx/systemui/sources/com/android/server/pm/PackageManagerService.java:3120-3180` | r1 `6149-6227`; r61 corresponding method | `AOSP_STANDARD` |
| `findPersistentPreferredActivityLP` | same file `3197-3252` | r1 `6247-6302` | `AOSP_STANDARD` |
| `findPreferredActivity` | same file `3288-~3500` | r1 `6306-6475` | `AOSP_STANDARD` for visible branches; Java decompiler caveat |
| `queryIntentActivitiesInternal` | same file `3724-3729` has unsupported block | r1 `6565-6635+` | `UNKNOWN` for the missing block |
| `adjustPriority` | same file `8166-8244` | r1 `12575-12630+` | `AOSP_STANDARD` shape |
| `ActivityIntentResolver.addActivity` | same file `8246-8262` | no AOSP vendor callback | `AMAZON_ADDITION` |
| `ActivityStackSupervisor.resolveIntent` | `decompiled/jadx/systemui/sources/com/android/server/am/ActivityStackSupervisor.java:745-772` | AOSP PM-internal call path | `AMAZON_ADDITION` |

## Important Amazon boundaries

`addActivity()` calls `VendorPackageManagerCallback.callFilterComponentIntent`
before adding an activity filter to the resolver index
(`PackageManagerService.java:8259-8261`). A `true` callback return would omit
that filter. No checked-in dynamic evidence identifies a HOME-specific return
value, and no Fire Launcher-specific branch was found in the selected chooser
body. This is therefore an Amazon candidate-filtering surface, not proof of a
Fire override.

`ActivityStackSupervisor.resolveIntent()` calls
`VendorActivityStackSupervisorCallback.callResolveIntent()` before the normal
PackageManagerInternal resolver (`ActivityStackSupervisor.java:745-772`). A
non-null return would short-circuit the normal path. The inspected callback
implementation and Phase 3 event evidence do not establish a non-null Fire
result.

## Hard-coded package search boundary

The selected core `PackageManagerService` chooser and `adjustPriority` regions
contain no literal `com.amazon.firelauncher`. That is strong negative evidence
for a direct package-name branch in those methods only. Amazon private services
do contain Fire package references in lifecycle and KFT/free-time paths; those
are catalogued in `findings/phase-4b-amazon-callback-control-surface.md` and do
not, by themselves, prove current main-user HOME selection.

Evidence: `P4A-METHOD-001` through `P4A-METHOD-008`, `P3C-CALLBACK-001`.
