# Phase 15 — AmazonActivityManager prewarm candidate closure

Date: 2026-08-10  
Scope: host-only static analysis. No adb, Binder/service call, device command, process start, package/settings mutation, updater/recovery, reboot, root/exploit, driver/ioctl, or partition action was performed.

## Closure result

`AmazonActivityManagerService.BinderService.preWarmApplicationForUser(String,int,int)` is a confirmed static process-prewarm surface and a strong static authorization-anomaly candidate. The method invokes `Context.checkCallingPermission("com.amazon.permission.APP_PREWARM")`, but the preserved DEX instruction sequence immediately invokes `Binder.clearCallingIdentity()`; there is no observed `move-result` or denial branch between those operations. This is not, by itself, evidence of exploitability or a permission bypass.

The generated Binder contract is `com.amazon.android.server.am.IAmazonActivityManager`, transaction 1, with parcel order `String packageName`, `int flags`, `int userId`; the Proxy writes the interface token and three arguments, and the Stub dispatches transaction 1 to the implementation. The framework wrapper is `AmazonActivityManagerImpl`, obtained through the `activity` manager registration.

The preserved direct caller is Alexa `ExplicitIntentAction.prewarmApplicationProcess`, which rejects a self-package target, requires a non-null manager and target, passes `str, 0, mBroadcaster.getForegroundProfileId()`, and records a nonzero return as failure. In the supplied caller scope, no other non-generated direct caller was found. Alexa’s manifest requests `com.amazon.permission.APP_PREWARM`; saved package evidence identifies `com.amazon.alexa.multimodal.gemini` (UID 10044) with that permission granted. The permission definition is `signature|amazon`.

Service wiring is preserved in `artifacts/amazon-services/amazonactivitymanager_fosinit.xml`: the vendor service implementation is `AmazonActivityManagerService`, and the `activity` vendor manager maps `AmazonActivityManagerImpl` to `android.app.ActivityManager`. Saved SELinux evidence records shell UID 2000 / `u:r:shell:s0` denied `service_manager find` for `amazonactivitymanager` under enforcing policy. This closes the saved shell route only; it does not prove that every SELinux domain or trusted internal caller is unreachable.

## Exact DEX semantics

Evidence: `artifacts/phase6x/prewarm-authorization-20260805-05/prewarm-service-method.snippet.txt` and source `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534`.

- `0000: move-object/from16 v1, v21`; `0002: move-object/from16 v2, v22`: receiver and package argument are moved into locals. The method signature is `(Ljava/lang/String;II)I`.
- `0021: const-string v6, "com.amazon.permission.APP_PREWARM"`; `0023: invoke-virtual {v0, v6}, Context.checkCallingPermission`; next instruction is `0026: invoke-static {}, Binder.clearCallingIdentity`; `move-result` between check and clear is false in the preserved snippet.
- After identity clear: `002a: if-eqz v2, 008b` rejects a null package; `002c: if-nez v23, 008b` rejects a nonzero second integer. The user argument is moved from `v24` into `v10` at `0037` and passed to `IPackageManager.getApplicationInfo(v2, 1024, v10)`.
- The method then calls `PreWarmCacheHelper.getKeepIfLargeValue(v2)` and `startProcessLocked(v12, v0, false, 0, "prewarm", null, false, false, false, v20)`, where `v12` is `ApplicationInfo.processName` and `v0` is the resolved `ApplicationInfo`.
- A non-null `ProcessRecord` changes return register `v5` from `-1` to `0`; identity is restored at `008d`, trace is ended, and `v5` is returned. Exception paths restore monitor state and rethrow/log as shown; they do not add an authorization branch before identity clearing.

## Caller, registration, and permission evidence

| Surface | Evidence and interpretation |
|---|---|
| Interface declaration | `boot-fosframework/disassembly.log:55411-55413`, method `preWarmApplicationForUser(Ljava/lang/String;II)I`. |
| Proxy | `boot-fosframework/disassembly.log:394721-394751`; transaction code `1`, interface token, String, two ints, returned int. |
| Stub | `boot-fosframework/disassembly.log:394892-395079`; transaction 1 reads the String and two ints, dispatches the method, and writes the result. No separate caller-UID or enforce-permission marker is observed in this bounded dispatch. |
| Wrapper | `boot-fosframework/disassembly.log:553433-553446`; `AmazonActivityManagerImpl` delegates to the interface. Manager acquisition is at `553272-553277` via `ServiceManager.getService("amazonactivitymanager")`. |
| Registration | `artifacts/amazon-services/amazonactivitymanager_fosinit.xml:8-28`; vendor service implementation and activity manager mapping. |
| Direct caller | `artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/amazon/speech/sim/router/intentrouter/ExplicitIntentAction.java:268-282`, especially line 274. |
| Permission holder | Alexa manifest line 78 requests `com.amazon.permission.APP_PREWARM`; saved package block lines 87/89 identify `com.amazon.alexa.multimodal.gemini` / UID 10044 and lines 11891 and 19650 show granted=true. The definition at line 16599 is `prot=signature|amazon`. |
| SELinux/service visibility | Saved `findings/phase-6es-selinux-service-reachability.md` and phase 6X evidence record shell `uid=2000`, `u:r:shell:s0`, enforcing denial of `service_manager find` for `amazonactivitymanager`. This is a route boundary, not universal non-reachability. |

## Downstream sink audit

The observed sink is process/resource prewarm only: `getApplicationInfo`, cache lookup, and `startProcessLocked`. The bounded Activity Manager service audit found no `CATEGORY_HOME`, `ACTION_MAIN`, `resolveActivity`, `setHomeActivity`, `replacePreferredActivity`, or preferred-activity writer in this method or the reviewed Activity Manager Binder surface. The separate writer inventory found no Amazon `fosservices` implementation of `setHomeActivity`, `replacePreferredActivity`, `addPersistentPreferredActivity`, or `restorePreferredActivities`; known package/component writers are separate paths (including child/profile-scoped KFT and fixed OOBE/Gemini/BOOT callbacks). Therefore no downstream HOME or package-state sink is established for prewarm.

The absence of a HOME/package-state sink does not prove that prewarm is harmless in every resource sense. It does establish that the supplied evidence does not connect this candidate to HOME selection, Fire Launcher enable/disable, preferred activity state, or package-state mutation.

## Final classification and safe continuation

The candidate is **Confirmed** as a static private Binder/process-prewarm surface; **Strong evidence** supports the ignored permission-result anomaly and the Alexa privileged caller; the HOME/package-state edge is **Disproved** for the reviewed bounded implementation and caller scope. No exploitability claim is made from the missing local check, and no claim is made that all possible callers were exhaustively enumerated.

The next safe step is limited to host-only expansion of the exact-build Amazon APK/DEX caller inventory or passive review of already-saved trusted lifecycle artifacts. Do not invoke the private Binder transaction or broaden into device mutation.
