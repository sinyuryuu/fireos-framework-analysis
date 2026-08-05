# Phase 6AV — PS7331 Amazon IPC method closure

This is host-only analysis of preserved PS7331 VDEX and saved service-visibility evidence.
No Binder handle was obtained, no transaction was sent, and no device state was changed.

## Result

- **已證實：** `registerKeyEventInterceptor` has a method-local permission, UID-to-package, whitelist, and foreground-package chain.
- **已證實：** the saved enforcing-policy capture prevents shell discovery of the relevant Amazon private services.
- **已證實（靜態）：** KFT launcher provisioning contains an explicit Fire Launcher disabled-state request; it is not an approved test route.
- **Strong evidence：** `preWarmApplicationForUser` shows `checkCallingPermission(APP_PREWARM)` immediately followed by `clearCallingIdentity()` in the bounded method block, then resolves an application and calls `startProcessLocked`.
- **已排除目前安全範圍：** a shell-callable HOME setter, a safe input-filter bypass, or a root path. Service visibility and caller-contract evidence do not provide such a route.
- **待驗證：** helper bodies not present in the bounded disassembly and every private method's complete caller policy.

## Interpretation

The input service is the closest HOME-key control surface, but the inspected registration path is protected by Amazon permission and package/foreground checks. The profile and KFT methods are lifecycle/profile controls; they do not establish an ordinary HOME resolver replacement. The prewarm pattern remains a static authorization-review candidate only: no shell handle, Binder invocation, process start, or privilege transition was observed.

## Reproduction

```sh
python3 tools/scripts/audit_phase6av_ipc_method_closure.py --dry-run --output /tmp/phase6av-dry-run
python3 tools/scripts/audit_phase6av_ipc_method_closure.py --output artifacts/phase6av/ipc-method-closure-YYYYMMDD-01
shasum -a 256 -c artifacts/phase6av/ipc-method-closure-YYYYMMDD-01/sha256sums.txt
```
