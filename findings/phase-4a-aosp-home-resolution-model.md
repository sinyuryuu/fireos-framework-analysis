# Phase 4A — AOSP Android 9 HOME resolution model

## Scope

This report is generated from the checked-in AOSP `android-9.0.0_r1` and
`android-9.0.0_r61` sources. The model in
`tools/scripts/model_aosp9_home_resolution.py` implements the decision points
that determine whether an ordinary preferred record can be used. It is not a
replacement for the framework.

## Decision order

1. `queryIntentActivitiesInternal()` produces the candidate set and applies
   visibility, user, component and direct-boot filters (`aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java:6565-6635+`).
2. Resolver sorting compares `priority`, `preferredOrder`, `isDefault`,
   `match`, `system`, then package name (`aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java:13500-13535`).
3. `chooseBestActivity()` returns the only result immediately. With multiple
   results it compares only the first two candidates' `priority`,
   `preferredOrder`, and `isDefault` (`aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java:6149-6170`).
4. If any of those three fields differs, `query.get(0)` wins and the ordinary
   preferred lookup is not called.
5. If they tie, `findPreferredActivity()` first checks persistent preferred
   activities and then ordinary preferred activities
   (`aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java:6172-6177`, `6247-6302`, `6306-6323`).
6. An ordinary record must have the current best match category, satisfy the
   `mAlways` requirement, point to an exact current candidate, and pass the
   saved component-set check (`6306-6465`). A changed result set can cause an
   always record to be dropped and re-added as a last-chosen (`6421-6458`).

## Meaning of mAlways

`mAlways=true` asks the preferred resolver to treat the record as a durable
preference when the chooser is in the tie path. It does not promote the
record's component above a different `priority`, `preferredOrder`, or
`isDefault` winner. A persistent preferred record is consulted first inside
`findPreferredActivity()`, but it is still required to resolve to an exact
component in the current query (`6247-6302`).

## Priority normalization

`adjustPriority()` caps a positive priority from a non-privileged application
to zero (`aosp/android-9/android-9.0.0_r1/platform/frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java:12575-12596`). This explains the Phase 3A
effective priority of zero for sideloaded launchers. Fire's privileged system
package retains its manifest priority 50 in the captured device state.

## Replayed scenario

The model input is Fire priority 50 plus a priority-0 third-party candidate with
an exact `mAlways=true` preferred record. The expected and modeled result is
Fire, because the priority difference returns `query[0]` before preferred lookup.
The unit test also proves the control case: an ordinary preferred record wins
when the ranking fields are genuinely tied.

Evidence: `P4A-MODEL-001`, `P3C-PREF-001`, `P3C-REBOOT-001`.
