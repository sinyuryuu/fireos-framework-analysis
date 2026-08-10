# Phase 9 — broad privilege-route closure

Generated UTC: `2026-08-10T07:59:46.671671+00:00`

## Safety

All Phase 9 worker analyses are host-only. No device command, private Binder/service transaction, package/settings mutation, driver open/ioctl, OTA/recovery execution, reboot, root attempt, exploit payload, or partition write was performed.

The acceptance rule remains `caller → gate → Binder identity → user scope → exact sink → observed effect`. Missing edges are preserved as UNKNOWN.

Combined ledger rows: **341**; unique IDs: **341**. New Phase 9 rows: **33**.

| New surface | Rows |
|---|---:|
| KFT tx3 caller identity closure | 9 |
| broad non-Launcher privilege surfaces | 10 |
| prewarm caller/grant closure | 12 |
| residual IPC privilege-sink closure | 2 |

## Concrete results

- **Prewarm:** Alexa is joined to a saved UID/grant snapshot and the sink is `startProcessLocked(..., "prewarm", ...)`; this is process/resource prewarm, not a package-state, HOME, UID-0, or permission-grant sink. User mapping and complete caller universe remain UNKNOWN.
- **KFT tx3:** the recovered semantic caller is `AmazonUserManagerImpl.createChildUser()`. The `frameworksettings` and `h2settingsfortablet` packages are candidates based on privileges, not confirmed tx3 callers. The local upgrade `onBootPhase` path is separate from external Binder tx3, and writer scope follows `UserInfo.id` rather than User 0.
- **Residual IPC:** exported/system-facing DCPMS or profile/package-management surfaces remain bounded UNKNOWN when the production client, service-manager gate, or downstream privileged sink is missing. Exported AIDL, a permission declaration, or a missing method-local UID check is not promoted to a usable shell/app route.
- **Broad surfaces:** every new non-Launcher candidate is retained with its exact missing edge; no new route closes to Fire User-0 state, formal HOME, UID 0, or partition write.

## Verdict

This phase expands the search to any permission/control path that could theoretically change package state, users, settings, policy, update state, or privileged device behavior. It finds no new reproducible low-privilege privilege transition. The next evidence must be offline artifact completion or a documented, authorized API contract—not unknown Binder codes, driver ioctls, malformed OTA data, or root tooling.

## Reproduction

Run `python3 tools/scripts/build_phase9_surface.py --dry-run` to verify inputs, then `--force` to regenerate the host-only bundle. No device is required.
