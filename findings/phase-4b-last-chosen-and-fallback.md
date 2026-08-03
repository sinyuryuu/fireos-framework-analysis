# Phase 4B — last-chosen and fallback boundary

AOSP Android 9 includes `setLastChosenActivity()` and
`getLastChosenActivity()` (`PackageManagerService.java:6025-6057`) and converts
an invalid always record to a last-chosen record when the saved candidate set
is no longer valid (`findPreferredActivity():6421-6458`). This is distinct from
the priority gate in `chooseBestActivity():6165-6175`.

The existing Fire evidence has an ordinary `mAlways=true` record that persists,
but Fire remains the resolver result. That is consistent with last-chosen and
ordinary preferred state being below a priority difference. A new shell history
mutation was not justified because the device did not expose a documented safe
HOME-specific last-chosen setter and Phase 3C already established the relevant
ordinary preferred behavior.

Controlled failure candidates were not made effective: making a priority-0
test candidate the real HOME would require changing or bypassing the Fire
candidate, which is outside the safety boundary. Deliberately inducing a
system-level HOME crash/fallback is **因風險拒絕測試**. Test-APK failure modes
remain available as source-only controls for future work.
