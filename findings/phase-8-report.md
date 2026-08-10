# Phase 8 — targeted caller, user-scope, and policy closure

Generated UTC: `2026-08-10T07:49:19.214788+00:00`

## Safety

All four audits are host-only. No device command, private Binder/service transaction, broadcast, package/settings mutation, driver open/ioctl, OTA/recovery execution, reboot, root attempt, or partition write was performed.

The acceptance rule remains `caller → gate → Binder identity → user scope → exact sink → observed effect`. Missing edges are preserved as UNKNOWN.

Combined ledger rows: **308**; unique IDs: **308**. New Phase 8 rows: **32**.

| New surface | Rows |
|---|---:|
| KFT tx3 caller/user-scope closure | 9 |
| SettingsProvider/HOME-key closure | 10 |
| driver final node/policy/caller closure | 6 |
| prewarm caller/user-scope closure | 7 |

## Concrete results

- **Prewarm:** the saved ordinary-app observation reaches transaction 1 and starts a target process, but the sink is process/resource prewarm only. No HOME selector, preferred-activity writer, package/component-state writer, permission grant, UID-0 transition, or partition sink is present. The saved enforcing-policy shell path is bounded-negative.
- **KFT tx3:** the recovered `enableKftLauncher(UserInfo)` path reaches three package/component setters, but each setter consumes the supplied `UserInfo.id` and is child/profile scoped. The static slice does not establish an accepted arbitrary external caller, a complete method-local cross-user gate, or a User-0 restoration writer; the shell service-manager boundary is separately blocked in saved enforcing evidence.
- **SettingsProvider:** the production provider persists system/secure/global values through `SettingsRegistry`/`SettingsState`. HOME-adjacent keys are card or personalization state, and the searched provider path has no bridge to `setHomeActivity`, `replacePreferredActivity`, or a package/component-state setter. The production caller for generic writes remains unknown.
- **Drivers:** CMDQ/MDP, ION, MTK ION, M4U, uinput, and AUXADC retain at least one missing final-artifact, node/policy, shipped-native-caller, or input-boundary edge. They remain UNKNOWN; no device node was opened and no ioctl was sent.

The Phase 8 evidence therefore expands the permission/control inventory without proving a new low-privilege privilege transition. A complete route still requires the full caller → gate → Binder identity → user scope → exact sink → observed effect chain.

## Closure questions

- **Prewarm:** only promote a permission anomaly if the exact requester, holder/grant, calling UID, target-user validation, and observed process sink all join. A boolean check whose return is not consumed is not by itself a bypass.
- **KFT tx3:** distinguish the child/profile `UserInfo.id` writer from a User-0 writer. A transaction code or Stub without an accepted external caller and cross-user gate is not a usable route.
- **SettingsProvider:** distinguish a real provider write implementation from a shell/App caller that can write a HOME-relevant key and then reach PMS/ATM. Key strings alone are not HOME control.
- **Drivers:** require final node/DT registration, mode/SELinux policy, shipped native caller, input boundary, and sensitive effect. Source ioctl capability without that join remains UNKNOWN.

## Verdict

This phase is designed to reduce the remaining uncertainty, not to manufacture a POC. It does not authorize or implement exploit payloads. Any row that lacks a complete chain remains a host-only research lead and must not be tested with unknown Binder codes, driver ioctls, malformed OTA data, or root tooling.

## Reproduction

Run `python3 tools/scripts/build_phase8_surface.py --dry-run` to verify inputs, then `--force` to regenerate the bundle after all four worker CSVs exist. No device is required.
