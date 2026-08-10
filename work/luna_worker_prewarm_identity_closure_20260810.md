# Phase 6QC-A worker — PS7331 prewarm / identity closure

Date: 2026-08-10. Scope is host-only exact static search over retained PS7331 disassembly, JADX/smali, manifests, fosinit, SELinux captures, and existing Phase 6AV/6BA/6BB results. No device contact, Binder/service call, broadcast, setting/package mutation, APK installation, root, OTA, or reboot was performed.

## Bottom line

`AmazonActivityManagerService.BinderService.preWarmApplicationForUser(String,int,int)` is present in both retained FOS and exact PS7331 OTA VDEX. The OTA `IAmazonActivityManager.Stub.Proxy` sends transaction `1` with `String + int + int`; the saved Alexa JADX call passes `(targetPackage, 0, foregroundProfileId)`. The server performs `getApplicationInfo(target, 1024, user)` and reaches `startProcessLocked(..., "prewarm", ...)` after `Binder.clearCallingIdentity()`, then restores identity.

The exact bounded instruction stream calls `Context.checkCallingPermission("com.amazon.permission.APP_PREWARM")` but has no observed `move-result` or denial branch before `clearCallingIdentity()`. This is a static authorization anomaly candidate, not proof of reachability or exploitability. Saved enforcing AVC evidence denies shell UID 2000 `service_manager find` for `amazonactivitymanager` and `amazonwindowmanager`; no Binder transaction was sent.

`setPipVisibility(boolean)` is not an AmazonActivityManagerService method. It is `AmazonWindowManagerService.BinderService.setPipVisibility`, and the exact FOS/OTA block writes through `AmazonWindowManagerService.access$202` to the private PIP state. Its bounded block has no local permission or identity marker; permission/caller contract is explicitly UNKNOWN pending full Stub/onTransact and holder/caller mapping. It has no bounded PMS, HOME resolver, package-state, or root sink.

## Caller and scope closure

The only direct `preWarmApplicationForUser` caller found by exact search in the retained JADX scope is Alexa `ExplicitIntentAction.prewarmApplicationProcess` (`ExplicitIntentAction.java:268-282`). The caller requires the Amazon ActivityManager feature/implementation, non-null manager and target, excludes self-package targets, passes user argument `0` plus `foregroundProfileId`, and logs nonzero failure. Its retained manifest requests `com.amazon.permission.APP_PREWARM`; existing Phase6BB package evidence classifies it as a system/privileged Amazon app.

No ordinary sideloaded-app or shell caller was established. Other Amazon apps/callers outside the retained JADX/DEX corpus are UNKNOWN, not negative. The proxy and fosinit registration prove a private IPC surface, not that an arbitrary app can obtain a handle. The saved SELinux boundary is strong evidence against the shell route under the captured enforcing policy.

## Identity, user, and sinks

For prewarm, incoming Binder identity exists at the permission call; the method then clears it at FOS `0x036f5c` / OTA `0x037004` and restores at FOS `0x03702a` / OTA `0x0370d2`. The exact numeric user is UNKNOWN: the caller passes `0` and a foreground profile ID, while the server forwards register `v24` to PMS `getApplicationInfo`. The first observable sink is `IPackageManager.getApplicationInfo`, followed by `PreWarmCacheHelper`, then `ActivityManagerService.startProcessLocked` with reason `prewarm`.

For PIP, the first observable sink in the bounded method is `AmazonWindowManagerService.access$202`, a private PIP state writer. No `clearCallingIdentity` or user/package argument is present in that block. The exact permission and caller identity are UNKNOWN.

Neither path is evidence of root or privilege escalation. Process prewarm starts the selected application process; it does not grant the caller system/root identity, alter HOME resolver state, write preferred activity, or mutate PMS/package state in the bounded evidence.

## Existing phase reconciliation

Phase 6AV correctly classifies prewarm as `STATIC_AUTH_ANOMALY_CANDIDATE_NOT_SHELL_REACHABLE` and records the shell service-visibility boundary. Phase 6BA correctly separates prewarm from KFT launcher lifecycle, OOBE/OTA, input, and HOME-control surfaces. Phase 6BB supplies the prior caller closure and explicitly forbids Binder invocation. This worker adds exact PS7331 OTA offsets, the PIP service distinction, explicit UNKNOWN labels, and row-level hashes.

## Evidence map

The accompanying CSV has required fields: method/offset, caller, gate, identity, user, sink, status, next_safe_step, and hash. Primary evidence includes:

- `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3642543-3642624` (server prewarm) and `:3658293-3658298` (PIP).
- `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:4464666-4464700` (prewarm proxy, descriptor, transaction 1).
- `artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/amazon/speech/sim/router/intentrouter/ExplicitIntentAction.java:268-282` and `resources/AndroidManifest.xml:78`.
- `artifacts/amazon-services/amazonactivitymanager_fosinit.xml:8-28` and `amazonwindowmanager_fosinit.xml`.
- `artifacts/phase6aq/public-summary-20260805-02/amazon-service-avc.txt` (saved enforcing shell find denials).
- Existing `findings/phase-6bb-prewarm-caller-closure.md`, `findings/phase-6av-ipc-method-closure.md`, and `findings/phase-6ba-control-surface-closure.md`.

All conclusions are static and scope-limited. The safe next step is further host-only exact caller/Stub/onTransact/permission-holder inventory; no device experiment is warranted by this closure.
