# Phase 6UP — ASP / prewarm host-only static closure

Date: 2026-08-10  
Scope: exact-build host artifacts only; no new device or Binder activity.

## Conservative result

| Surface | Static result | Reachability result | Status |
|---|---|---|---|
| `AmazonAspService.BinderService.hasCallerGotPermission()` | On `tablet`, checks `com.amazon.permission.ASP_PERMISSION`; `command()` returns `-EACCES` before `nativeCommand()`. Non-tablet returns allowed. | Existing KFTRWI capture shows `audiosignalprocessor: found`, shell UID 2000, `Enforcing`, and transaction 3 result `-13`; no native execution or HOME/package/settings effect is evidenced. | Static policy anomaly is cross-build only; current tablet bypass closed. |
| `AmazonActivityManagerService.BinderService.preWarmApplicationForUser()` | Calls `checkCallingPermission(APP_PREWARM)` and ignores its result before `clearCallingIdentity()`, then resolves a package/user and invokes `startProcessLocked(...,"prewarm",...)`. | Existing capture shows `amazonactivitymanager: not found` and `service ... does not exist` for shell; no Stub dispatch. HOME, users, Fire package dump, and Fire PID stayed unchanged. | Static authorization anomaly candidate; ordinary-app/shell reachability closed in supplied evidence. |

This does not establish an exploit, privilege escalation, native/audio/input access, package-state change, settings write, window/HOME write, or cross-user process-start behavior. “Closed” is limited to the saved shell/ordinary reachability evidence and exact artifacts; it is not a claim about every privileged SELinux domain or another build.

## Anchored evidence

### ASP

- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:82014-82030`, code offsets `0x5ca9a-0x5caca`: `hasCallerGotPermission()` branches on `"tablet"`; tablet calls `Context.checkCallingPermission("com.amazon.permission.ASP_PERMISSION")`.
- `.../fosservices/disassembly.log:82031-82043`, offsets `0x5cad0-0x5caf2`: result is consumed; denial logs and returns false, while the allowed path returns true.
- `.../fosservices/disassembly.log:82063-82070`, offsets `0x5cba2-0x5cbb4`: `command(I[B[B)` calls the guard and returns negative `OsConstants.EACCES` before `access$500` (`nativeCommand`) when denied.
- `.../fosservices/disassembly.log:82737-82746`, offsets `0x5d3c2-0x5d3ea`: `onStart()` publishes `audiosignalprocessor`, publishes a local service, then opens/registers native ASP callbacks. Native sinks are downstream of the permission gate.
- `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:405900-406250` (contract block; transaction 3): Stub parcel decoding and `command` dispatch. No separate HOME, window, input, package, or settings sink was found in this ASP path.
- Saved runtime artifacts: `adb/phase6bv/PHASE6BV-ASP-RO-20260805-01/probe.txt` (Parcel result `-13`), `id.txt` (UID 2000/shell), `getenforce.txt` (`Enforcing`), `service_check.txt` (`found`), and `logcat_asp.txt` (permission-denial log). These are referenced, not newly executed.

### AmazonActivityManager prewarm

- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40474`, offsets `0x36f0c-0x36f5c`: method signature; `checkCallingPermission("com.amazon.permission.APP_PREWARM")` is immediately followed by `Binder.clearCallingIdentity()` with no visible result test.
- `.../fosservices/disassembly.log:40480-40503`, offsets `0x36f72-0x36fc8`: package/user propagation through `IPackageManager.getApplicationInfo(package, 1024, user)` and process sink `startProcessLocked(...,"prewarm",...)`.
- `.../fosservices/disassembly.log:40532-40534`, offsets `0x3702a-0x37036`: identity restore and return.
- `.../fosservices/disassembly.log:41077-41084`, offsets `0x3782c-0x3784c`, plus `artifacts/amazon-services/amazonactivitymanager_fosinit.xml:9-24`: Binder service construction/publication and vendor service registration.
- `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:394721-394739`, offsets `0x6454-0x648c`: Proxy writes descriptor, package string, two integers, and calls `transact(1)`.
- `.../boot-fosframework/disassembly.log:394892-395074`, offsets `0xa2980-0xa2b82`: Stub enforces descriptor, reads string/integers, dispatches transaction 1, and writes the result. No bounded caller UID/permission enforcement is visible in this Stub block.
- Existing known-caller evidence identifies privileged Alexa code and its `APP_PREWARM` request in `artifacts/phase6x/prewarm-authorization-20260805-01/prewarm-authorization-evidence.csv` rows `6X-PW-006`–`009`; this does not establish an ordinary-app caller.
- Existing reachability artifacts `adb/phase6em/PHASE6EM-AM-ACTIVITY-PREWARM-READONLY-20260806-01/service_check.stdout.txt`, `transaction_1_prewarm_firelauncher_user0.stderr.txt`, and `result.json` record shell denial/no dispatch and unchanged HOME/users/package/PID invariants.

## Sink review

ASP: native ASP/HAL operations are the only downstream sink identified, and the current tablet guard blocks shell. No audio capture/injection, input, window, package, settings, or HOME writer was invoked or statically connected to this method.

Prewarm: the only stateful downstream sink identified is system-server process prewarm. The package lookup is read-only. No `setHomeActivity`, preferred-activity, component/package enable, settings, window, input, audio, native, or launcher-restoration call appears in the reviewed method/contract path.

## Limitations and handling

The static anomaly remains reportable as a code-review issue: ASP’s non-tablet allow branch is build-dependent, and prewarm’s ignored permission result plus identity clear is a confused-deputy candidate. The supplied captures close shell reachability on KFTRWI but cannot prove universal unreachability. No Binder/service call, native method, input/audio injection, permission change, or exploit payload was performed in this phase.

## Evidence hashes

SHA-256 values for the exact-build sources and selected saved captures are listed in the companion CSV. The source hashes are used to bind the line/offset anchors to the inspected repository artifacts.
