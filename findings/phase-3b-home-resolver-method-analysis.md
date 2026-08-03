# Phase 3B HOME resolver method analysis

This file is the Phase 3B-specific companion to the existing Phase 3A method
analysis. It does not overwrite the Phase 3A report.

## Method inventory

| Method | Fire OS source | AOSP comparison | Result |
|---|---|---|---|
| `resolveIntent` | `PackageManagerService.java:3003-3004` | r1/r61 same method family | Standard entry |
| `resolveIntentInternal` | `PackageManagerService.java:3007-3022` | r1/r61 same method family | Query then choose |
| `chooseBestActivity` | `PackageManagerService.java:3120-3168` | r1/r61 priority/preferred structure | Priority first; preferred tie path |
| `findPersistentPreferredActivityLP` | `PackageManagerService.java:3197-3275` | r1/r61 same method family | Persistent branch exists |
| `findPreferredActivity` | `PackageManagerService.java:3288-3350` | r1/r61 same method family | Ordinary preferred branch |
| `queryIntentActivitiesInternal` | `PackageManagerService.java` around resolver query | r1/r61 same method family | Candidate set producer |
| `ActivityStackSupervisor.resolveIntent` | `ActivityStackSupervisor.java:745-772` | AOSP baseline has no observed equivalent vendor pre-hook | Amazon callback pre-hook |
| `PhoneWindowManager.startDockOrHome` | `services.disassembly.log:988383-988428` | AOSP baseline path | Vendor callback extension |

## Priority and preferred ordering

The candidate query proves that the runtime values are Fire `50`, Microsoft
`0`, and FallbackHome `-1000`. The Fire OS `chooseBestActivity()` implementation
compares the leading candidates' priority, preferred order, and default state.
Only when the leading comparison does not decide the result does it call
`findPreferredActivity()` with the candidate priority. Therefore a Microsoft
`mAlways=true` ordinary preferred record is stored state but is not an effective
winner while Fire is the stronger candidate.

The Phase 3A sideloaded priority values being normalized to zero are consistent
with the Android 9 non-privileged priority cap. Fire's manifest priority 50 is
not by itself proof that no preferred activity can ever override it; it is the
reason the preserved priority-0 preferred record does not override it.

## Microsoft preferred record

The record is valid stored state (`mAlways=true`) but it does not win the
candidate comparison. No evidence in the selected resolver methods indicates a
package-name special case for `com.amazon.firelauncher`. The exact runtime
callback ordering is retained as an open item because the callback aggregator
can return a non-null result before the PM fallback.

## Vendor callback findings

- `AppCompatActivityStackSupervisorCallback.resolveIntent()` calls the platform
  `IPackageManager.resolveIntent()` and filters an uninstalled-app result. It
  does not contain a Fire package target in the inspected disassembly
  (`fosservices.disassembly.log:41093-41138`).
- `LauncherHijackPreventerActivityStackCallback.canSeeHomeTask()` checks the
  SELinux `amazon_policies/see_home_task` permission. That controls task
  visibility, not the selected HOME component in the inspected method.
- `AlexaModeSwitchManagerPhoneWindowManagerCallback` can launch a multimodal
  home only when its mode is active (`fosservices.disassembly.log:196259-196276`).
  The captured baseline does not establish that mode as the current tablet HOME
  path, and no Fire component is present in that method.

## Classification

| Observation | Classification |
|---|---|
| Fire `chooseBestActivity` follows AOSP-shaped priority logic | `AOSP_STANDARD` / Strong evidence |
| Fire priority 50 comes from its privileged manifest | `AMAZON_ADDITION` as package data, not resolver patch |
| ActivityStackSupervisor vendor callback pre-hook | `AMAZON_ADDITION` |
| PhoneWindowManager key-policy/vendor callback hooks | `AMAZON_ADDITION` |
| Fire package-name ranking branch in inspected PM methods | Not found; `Probable absent in inspected scope` |
| Callback return that explicitly chooses Fire | `UNKNOWN` |
