# Phase 6SQ — HOME/PMS writer closure

Date: 2026-08-10. Host-only review of the requested Phase 3B–6 artifacts and
reports. No package, user, Binder, settings, policy, OTA/OOBE, or device
state was changed; no private API or adb test was run.

## Result

No existing candidate closes the User 0 Fire Launcher HOME gap under the
required proof standard: exact method, target, caller identity,
publication/authorization, and user/component scope must be shown together.

The strongest exact package-state writer is
AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)
(fosservices/disassembly.log:54310-54324). It invokes Amazon package/component
setters for Tahoe, com.amazon.firelauncher, and Launcher3. The user argument
is supplied UserInfo.id. Phase 6AK/6AY and parent/profile/DPM evidence place it
in child/profile provisioning and system lifecycle paths. It is not a proven
ordinary User-0 HOME selector. Its tx3 method-local authorization asymmetry is
a static review point, not a usable route; service publication is confirmed
but saved AVC evidence denies shell service-manager find.

Exact preferred-HOME sinks also exist: PMS setHomeActivity(ComponentName,int)
delegates to replacePreferredActivity, and Settings
DefaultHomePicker.setDefaultKey reaches PackageManagerWrapper's preferred
writer with an explicit user argument. These are genuine preferred-record
sinks, but reviewed caller/permission evidence does not prove an ordinary
caller can select Fire for User 0. Existing runtime evidence shows a
third-party preferred record can persist while Fire's priority-50 HOME result
remains effective. DPM persistent-preferred paths are owner/admin and
system-UID gated.

ProductPolicy has exact enabled-state setters but is trusted,
policy-file/user-list-driven, and the reviewed policy inputs do not establish
a Fire Launcher User-0 target. AmazonProfileService initiateLauncher only
checks PROFILE_INTERACTION, logs, and returns success; its separate profile
picker path is not HOME selection or package state. OOBE/OTA, Gemini,
Espresso, AMS, Bluetooth, IME, DPM, SystemImpl, and Vending rows likewise do
not prove a Fire+User-0+HOME edge. Vending residual caller/user details stay
UNKNOWN. Phase 6AL callbacks delegate to PM or return null and do not directly
select Fire or write preferred/package state.

## Disposition

**NO CLOSED USER-0 FIRE HOME/PMS WRITER.** Positive package-state evidence is
retained only for KFT with explicit child/profile scope. Positive
preferred-writer evidence is retained for PMS and Settings with explicit user
parameters but unresolved reachable caller, target, and effective-resolver
proof. Unpreserved native/generated/runtime-loaded paths remain UNKNOWN.

## Next minimal static check

Host-only close all production callers of enableKftLauncher(UserInfo),
setHomeActivity, and replacePreferredActivity: record caller package/UID or
signature gate, identity transitions, component target, and user argument.
Stop at skipped/injected/native boundaries and preserve UNKNOWN. Do not invoke
Binder, dispatch Settings UI, mutate package state, create/switch users,
replay OOBE/OTA, or test a private API.

Evidence reviewed includes findings phase6kv, phase6mw, phase6mh, phase6mq,
phase6ak, phase6al, phase6am, phase6ay, phase6bg; work reports phase6mf/mj/
ml/mn/mo/mp/ms, launcher_options, parent_profile_dpm, settings_home_resource_
followup, and vending_downstream_closure; plus canonical Phase 6KV/6MH/6MN/
6MQ/6MW artifacts.
