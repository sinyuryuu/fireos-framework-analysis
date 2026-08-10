# Phase 6UF — host-only KFT tx3 authorization / cross-user gate closure

## Scope and safety

Host-only, bounded static review of the recovered PS7331 VDEX disassembly and existing saved capture references. No tx3 was sent; no user was created or switched; no setter replay or reboot was performed.

## Result

`IAmazonUserManager` transaction 3 is confirmed as `enableKftLauncher(UserInfo)`. The generated Stub enforces the interface descriptor and unmarshals an optional `UserInfo`, then dispatches tx3; no method-local UID, `MANAGE_USERS`, or cross-user check is visible in the bounded Stub or service method. The sink consumes caller-supplied `UserInfo.id` and writes Tahoe component state plus Fire/Launcher3 application state.

The effective lifecycle gate is present for the internal paths:

* `onBootPhase(500)` requires the literal phase, `isUpgrade() == true`, and `isChildUser(UserInfo) == true` before calling `BinderService.enableKftLauncher`; it then calls `setUserSetupComplete` for the same child. This is an internal system-server lifecycle caller, not an external Binder caller.
* `AmazonUserManagerImpl.createChildUser(String)` calls `createUser(..., 0x8000)`, obtains the private service, calls `IAmazonUserManager.enableKftLauncher(UserInfo)` through generated Proxy tx3, then calls tx4 setup completion. Failure removes the newly-created user. This is a framework child-creation caller, not an arbitrary external caller.

Therefore tx3 is genuinely applied to the child lifecycle paths, but the gate is not enforced at the generated Stub/service method boundary. A caller that obtains the private Binder handle and reaches tx3 would be able to supply a `UserInfo.id` as far as the static method body; downstream/package checks and runtime reachability are separate boundaries. The saved capture shows shell `find`/service lookup denied, and no tx3 was invoked in this phase.

## Exact bounded call/branch inventory

| Surface | Evidence | Branch / permission result |
|---|---|---|
| Proxy | `boot-fosframework/disassembly.log:370398-370443` | writes descriptor; optional `UserInfo`; `transact(3, ...)`; reads boolean result |
| Stub | `boot-fosframework/disassembly.log:370674-370777` | `enforceInterface`; tx3 reads optional `UserInfo`; dispatches `enableKftLauncher`; no visible method-local permission check |
| Internal creator caller | `boot-fosframework/disassembly.log:369180-369243` | create child with `0x8000`; tx3; tx4; remove on failure |
| Service method | `fosservices/disassembly.log:54415-54478` | package-manager availability; MM-device early return; `tryEnableKftLauncherComponent`; DPM path after `Binder.clearCallingIdentity`, with restore |
| Static sink | `fosservices/disassembly.log:54297-54325` | Tahoe `FreeTimeLauncherActivity` enabled for `UserInfo.id`; Fire Launcher and Launcher3 application state set to disabled/state 2 for same id |
| Internal boot caller | `fosservices/disassembly.log:55053-55105` | phase 500 → setup services → `isUpgrade()` → enumerate users → child predicate → tx3 + tx4; non-upgrade and non-child branches skip |
| Child predicate | `fosservices/disassembly.log:55053-55105`; existing helper inventory | child classification is applied before the boot caller; exact helper implementation is outside the bounded service slice: preserve UNKNOWN for any alternate alias |
| `checkManageUsersPermission` | `fosservices/disassembly.log:54847-54875` | UID 0/1000 allow; otherwise helper `checkComponentPermission(MANAGE_USERS, uid, -1, true)`; nonzero result throws `SecurityException` |
| Its callers | `fosservices/disassembly.log:54809-54820`, `54904-54906` | bounded direct caller is `getUserSortedListFromFile`; synthetic accessor forwards to same helper. No tx3/tx4 call edge |
| user-manager `checkComponentPermission` | `fosservices/disassembly.log:54111-54119` | thin delegate to `ActivityManager.checkComponentPermission` |
| other same-named caller | `fosservices/disassembly.log:45957` | separate `AmazonDevicePolicyManagerService.checkPermission` path; not a tx3 caller |
| service publication | `fosservices/disassembly.log:54894-54899`, `55106-55119` | name `amazonusermanagerservice`; `onStart` publishes BinderService |

## Permission declarations and external Binder separation

The explicit `MANAGE_USERS` check is proven for the sorted-list/profile-policy path only. It is not called from tx3 in the bounded corpus. The service publication has no recovered `android:permission`/Binder descriptor declaration tied to tx3, and the generated Stub has no visible method-local permission gate beyond interface-token enforcement.

The host corpus contains saved runtime evidence that shell UID 2000 cannot obtain the service handle under enforcing SELinux (`service check ...: not found` / `service_manager find` denial), but this does not prove every external Binder caller is impossible. Existing ordinary-app descriptor/other-transaction probes do not establish tx3 authorization. No manifest or service-registration permission declaration that directly gates `amazonusermanagerservice` was found in the bounded search.

## UNKNOWN ledger

1. `UNKNOWN`: complete external Binder caller universe, including native/JNI/reflection/aliased interface references outside the two recovered VDEX logs.
2. `UNKNOWN`: any service-manager registration permission or SELinux rule beyond the saved service-context and shell-denial evidence; no direct tx3-specific declaration was recovered.
3. `UNKNOWN`: exact implementation/branches of `AmazonUserManagerHelper.isChildUser` outside the call site; the observed boot branch is child-gated, but alternate callers/aliases are not inferred.
4. `UNKNOWN`: whether a non-shell external caller can obtain a valid handle on another build/runtime state. Do not infer exploitability from the missing method-local check.
5. `UNKNOWN`: downstream PMS/package-manager authorization outcome for a newly forged or externally supplied `UserInfo`; no tx3 or setter replay is permitted by scope.

## Closure

The host-only conclusion is **partially closed**: tx3 is lifecycle-gated for the two confirmed internal callers and clearly reaches a cross-user-capable package-state sink, but there is no proven tx3-local caller/permission gate in the recovered Stub/service method. The external Binder boundary remains UNKNOWN beyond the saved shell SELinux denial. Preserve this as a static authorization review point, not as a demonstrated exploit.
