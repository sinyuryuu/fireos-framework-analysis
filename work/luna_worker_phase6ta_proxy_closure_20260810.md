# Phase 6TA — Amazon PM proxy follow-up closure audit

Date: 2026-08-10  
Scope: host-only consistency audit of the existing Amazon PM proxy follow-up, caller inventory, and Phase 6IP/6QE artifacts. No Binder call, probe replay, parcel reconstruction, or mutation was performed.

## Closure

The existing tx6/tx7 conclusions are internally consistent at the implementation level:

- `tx6 registerProxyReceiver`: the Binder Stub dispatches the optional `Intent` and `PendingIntent`; `BinderService` delegates to `ProxyReceiver`. The creator package must resolve to an application with `ApplicationInfo.FLAG_SYSTEM`; a new action also requires non-empty `queryBroadcastReceivers(PendingIntent.getIntent(), 0)`. Accepted state is held in `mOnTheFlyRegisteredIntents`; the later callback path reaches `PendingIntent.send()`.
- `tx7 deregisterProxyReceiver`: `ProxyReceiver` removes entries from `mOnTheFlyRegisteredIntents` only when stored `PendingIntent.getCreatorUid()` equals direct `Binder.getCallingUid()`. Empty action/map cleanup reaches `Context.unregisterReceiver`.
- Neither path shows `clearCallingIdentity()`/`restoreCallingIdentity()` in the cited slices. This matters for tx7 ownership: the Binder caller UID is used directly.
- The only non-generated source caller found is `ProxyReceiverGateProbeActivity`; it is a Phase 6IP test-only probe. No production caller or exact-build provenance for a system-created `PendingIntent` was found in the bounded corpus. Caller status remains `UNKNOWN`, not negative proof.
- The first sinks are the internal receiver/map and `PendingIntent.send()` (tx6), or internal map cleanup/`unregisterReceiver` (tx7). No HOME, Fire Launcher, preferred-activity, package enabled-state, or other PMS writer sink was found.

## Source, path, and hash audit

The following cited paths exist and their current hashes match the prior inventory:

| artifact | locator/use | SHA-256 |
|---|---|---|
| `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` | interface `:58318-58354`; Proxy/Stub tx7 `:402937-402982`, `:403487-403510`; tx6 `:403148-403190`, `:403505-403530` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` |
| `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | BinderService `:95877-95888`, `:95943-95954`; tx7 `:97828-97878`; tx6 `:97887-97986`; callback/send `:97704-97754`, `:97670-97699` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| `artifacts/phase6jd-fosinit-20260808-01/system/fireos/etc/init/amazonpackagemanager_fosinit.xml` | vendor service publication `:9-10` | `eb53e50cf72174eddcde25fd3538e4736d2cd4cb7866bab4e5bc2b70fc514286` |
| `tools/test-launcher-phase4/src/org/fireosresearch/phase6ip/proxy/ProxyReceiverGateProbeActivity.java` | test-only tx6/tx7 caller `:53-61`, `:80-124` | `334fd9a1c43a02403d2e440664ab6f675bd9b89738fa3c2b06590c9ee92c0df5` |
| `tools/test-launcher-phase4/config/AndroidManifest-phase6ip-amazon-proxy.xml` | test probe package/component declaration | `3808c97dd7acf95488bcca1938bca026c6d2614c71e0721190203206e63daa82` |

The prior caller inventory also records a `Phase6IP finding` hash `f26b8134…`, but no corresponding path or artifact with that hash was found. The existing run manifest identifies `adb/phase6ip/PHASE6IP-AMAZON-PROXY-GATE-20260807-125406/result.json` with SHA-256 `e3ea96f68cfd82b1fdf11159f24deef398e47fde58884bc8a58f453e64ef2907`. This is a stale/unresolved reference only; it does not change the recorded runtime boundary (`tx6=false`, `tx7=false`, no receiver hit, HOME unchanged).

## Boundary and remaining gap

`tx6` and `tx7` are static-implementation-confirmed, with the system-app creator gate, broadcast-query gate, direct Binder UID ownership gate, exact map state, and `PendingIntent.send()` locators reconciled. The production caller and system-created-token provenance remain unknown. There is no HOME/PMS sink in the audited path. Any closure beyond this requires a newly supplied offline exact-build artifact; do not synthesize payloads or replay the transactions.
