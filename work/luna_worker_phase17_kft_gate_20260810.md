# Phase 17, branch A — PS7331 KFT launcher gate

Scope: host-side review of existing PS7331 VDEX/smali and saved artifacts only.
No ADB, Binder transaction, driver access, exploit/root/OTA/recovery/flash, or
device-state mutation was performed.

## Result

The exact path is:

`AmazonUserManagerImpl.createChildUser(UserInfo)` or the upgrade branch of
`AmazonUserManagerService.onBootPhase(500)` →
`IAmazonUserManager.Proxy.enableKftLauncher(UserInfo)` (transaction 3, for the
first caller) → `IAmazonUserManager.Stub.onTransact()` →
`AmazonUserManagerService.BinderService.enableKftLauncher(UserInfo)` →
`tryEnableKftLauncherComponent` → private
`enableKftLauncherComponent(UserInfo)`.

The Proxy writes an optional `UserInfo` parcel and calls `IBinder.transact(3)`.
The Stub enforces only `amazon.os.IAmazonUserManager`, unmarshals the optional
`UserInfo`, and dispatches tx3. In the bounded tx3 Stub/implementation slice,
no `getCallingUid`, `checkCallingPermission`, `enforceCallingPermission`,
`MANAGE_USERS`, or current-user equality check is visible. A separate
`checkManageUsersPermission` helper exists for other service methods, but the
tx3 dispatch does not call it. This is a preserved static edge, not a finding
of vulnerability or exposure.

`enableKftLauncher` first checks Amazon Package Manager availability and
`isMMDevice`; it then calls `tryEnableKftLauncherComponent`. If successful,
it calls `Binder.clearCallingIdentity()`, performs KFT Device Policy work, and
restores identity on normal and exception paths. The package-state sink uses
the supplied `UserInfo.id`: it enables
`com.amazon.tahoe/.launcher.FreeTimeLauncherActivity` with component state 1,
sets `com.amazon.firelauncher` application state 2, and sets
`com.android.launcher3` application state 2. The adjacent KFT DPM path sets the
Free Time component active-admin/profile-owner state for the same user ID.

The known trusted callers are in-process lifecycle paths: child creation sets
the child flag `0x8000` before calling the interface, and upgrade boot
enumerates users and calls the writer only when `AmazonUserInfo.isChild()` is
true (`UserInfo.flags` bit `0x8000` or `0x8`). Neither caller proves that every
Binder client is trusted. No additional caller was inferred from absence of
references.

No current-user validation is visible in the exact `enableKftLauncher` path;
the user scope is the supplied `UserInfo.id`, with child validation present in
the two known lifecycle callers rather than in tx3 itself. Existing runtime
artifacts record the private service as unavailable/not found to shell and an
SELinux service-manager `find` denial; they do not show tx3 dispatch. Thus the
static missing-caller-check edge remains unresolved and must not be labeled a
vulnerability.

## Evidence index

- `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:079db8-079dea` — child predicate (`flags & 0x8000` or `flags & 0x8`).
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325` — exact package-state sink and `UserInfo.id` use.
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54415-54492` — wrapper, availability/MM checks, `clearCallingIdentity`, DPM path, restore paths.
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:55053-55104` — upgrade caller and child gate.
- `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:369180-369217` — child-creation caller.
- `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:370398-370421` — Proxy tx3 and optional `UserInfo` parcel.
- `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:370637-370740` — Stub descriptor enforcement, unmarshalling, tx3 dispatch.
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54847-54879` — separate `checkManageUsersPermission` helper; not called by tx3 in the bounded slice.
- `findings/phase-6cz-kft-child-gating.md` — prior bounded synthesis and saved runtime boundary.
- `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv` — sink callsites and hashes.

## Classification and next safe step

Classification: confirmed child-lifecycle KFT writer; static authorization edge
unknown; no demonstrated vulnerability and no missing caller treated as one.

The next safe step is host-side comparison against another already-present
same-build decompilation/artifact, if available, specifically for a tx3 caller
or a method-local permission/current-user check. Do not invoke tx3, forge a
`UserInfo`, or alter service-manager/SELinux state.

