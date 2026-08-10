# IAmazonPackageManager tx6/tx7 host-only IPC follow-up

Date: 2026-08-10  
Scope: PS7331 exact VDEX disassembly, fosinit, manifest/probe source, and existing Phase 6IP/6L/6MN/6PZ evidence. No device IPC or mutation was performed.

## Result

There are two rows in the companion CSV, one for tx6 and one for tx7. The static implementation is confirmed, but no production external caller was found. The only non-generated caller in the corpus is the Phase 6IP test-only probe; it must not be treated as a production caller. Any caller beyond the listed generated Stub dispatch and test probe is **unknown**.

The exact interface declarations are in `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:58318-58337`; the generated Proxy transact methods are in `:402937-403180`, and Stub dispatch is in `:403368-403530`. No independent `.smali` or `.vdex` file was present in the searched corpus, and no matching JADX Amazon PM/ProxyReceiver source was found; those source forms are therefore **unknown/not available**, not inferred.

## Service publication and callback context

`artifacts/phase6jd-fosinit-20260808-01/system/fireos/etc/init/amazonpackagemanager_fosinit.xml:9-10` publishes `com.amazon.android.service.pm.AmazonPackageManagerService` as a vendor service. The same fosinit registers PackageManager callback implementations, but those callback registrations do not statically call tx6 or tx7. Existing Phase 6JD inventory bounds the callback family to internal system-server/package-policy callbacks; no HOME writer was found.

## tx6 — registerProxyReceiver

The Stub reads an optional `Intent` and optional `PendingIntent`, then dispatches transaction 6 to `BinderService.registerProxyReceiver` (`boot-fosframework/disassembly.log:403505-403530`). The BinderService delegates directly to the singleton `ProxyReceiver` (`fosservices/disassembly.log:95943-95954`).

The decisive gate is not a Binder permission check: `ProxyReceiver` obtains `PendingIntent.getCreatorPackage()`, calls `getApplicationInfo(package, 128)`, and accepts only `ApplicationInfo.FLAG_SYSTEM` (`fosservices/disassembly.log:97887-97900`). A new action also requires `queryBroadcastReceivers(PendingIntent.getIntent(), 0)` to return a non-empty list; same-action duplicate handling compares PendingIntent creator UIDs (`:97901-97976`). No `clearCallingIdentity()` or `restoreCallingIdentity()` occurs in the tx6 method slices.

The first state consumer is `mOnTheFlyRegisteredIntents`, keyed by filter action. A new action creates an `IntentFilter`, calls `Context.registerReceiver`, and stores the PendingIntent (`fosservices/disassembly.log:97968-97986`). Later `ProxyReceiver$1.onReceive` looks up and clones the action list, starts `ProxyIntentThread`, and the thread invokes `PendingIntent.send()` (`:97704-97754`, `:97670-97699`). This is the complete static receiver/sink chain found; no package enabled-state, preferred activity, HOME, or Fire Launcher writer is present.

Existing Phase 6IP evidence recorded an ordinary self-created PendingIntent being rejected (`tx6=false`, `receiver_hits=0`), but this follow-up did not rerun or invoke that probe. The probe source and manifest are `tools/test-launcher-phase4/src/org/fireosresearch/phase6ip/proxy/ProxyReceiverGateProbeActivity.java` and `tools/test-launcher-phase4/config/AndroidManifest-phase6ip-amazon-proxy.xml`.

## tx7 — deregisterProxyReceiver

The Stub reads the optional `Intent` and dispatches transaction 7 (`boot-fosframework/disassembly.log:403487-403510`); BinderService delegates to `ProxyReceiver` (`fosservices/disassembly.log:95877-95888`). There is no separate permission marker in the tx7 path. Under the synchronized action map, each stored PendingIntent is removed only if `PendingIntent.getCreatorUid() == Binder.getCallingUid()` (`fosservices/disassembly.log:97828-97870`). Missing map/action/entry returns false. No identity clear/restore is present; the direct Binder calling UID is intentionally used for ownership.

The first state consumer is the action list in `mOnTheFlyRegisteredIntents`. When an action list becomes empty, the action key is removed; when the whole map is empty, `Context.unregisterReceiver(mProxyReceiver)` is called (`fosservices/disassembly.log:97842-97878`). No package/HOME state consumer follows. Existing Phase 6IP evidence recorded `tx7=false` because no caller-owned entry existed; no cross-UID removal was demonstrated or attempted here.

## Caller and payload boundary

The exact static search found generated interface/Proxy/Stub declarations and dispatch, the two BinderService implementation edges, and the Phase 6IP test-only source caller. It found no production callsite for either transaction. The CSV intentionally records this as unknown. It also records only the exact method signatures and implementation reads; it does not reconstruct or guess transaction payload fields beyond what the existing declaration/dispatch evidence explicitly shows.

## Existing evidence cross-check

Phase 6L confirms the interface-to-service mapping and `amazonpackagemanager` publication; Phase 6IP confirms the ordinary-app gate and receiver-hit negative result; Phase 6MN/6PZ broad-surface closures found no new User-0 HOME/package-state writer in the bounded corpus. Phase 6EY similarly bounds tx6/tx7 as ordinary-app negative gates. These are static/runtime-boundary conclusions, not proof of an undiscovered system-created PendingIntent caller.

## Artifacts and hashes

Companion CSV row count (excluding header): **2**.

The final SHA-256 values are reported with the handoff after file creation.
