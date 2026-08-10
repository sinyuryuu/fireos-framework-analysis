# Phase 6QB-A — exact PS7331 IAmazonPackageManager tx6/tx7 caller inventory

Date: 2026-08-10. Scope is host-only static search and existing-result reconciliation for PS7331. No device access, Binder/service call, broadcast, Settings change, APK install, root/OTA/reboot, or mutation was performed.

## Result

The companion CSV has two transaction rows. Exact PS7331 disassembly contains the generated interface/Proxy/Stub contract and system-server BinderService implementation, but **no production caller** for either tx6 or tx7. The only non-generated source caller found is the Phase6IP probe; it is test-only and excluded from the production count. Any additional caller is `NOT_FOUND/UNKNOWN` in the bounded corpus.

No exact-build production provenance for a **system-created PendingIntent** was found in the searched JADX/smali/VDEX/disassembly, fosinit, or manifest artifacts. This is `NOT_FOUND`, not a claim that no such token can exist at runtime.

## Contract and caller evidence

* Interface declarations: `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:58318-58354`; tx7 is `deregisterProxyReceiver(Intent)` and tx6 is `registerProxyReceiver(Intent, PendingIntent)`.
* Generated client Proxy: same file, tx7 `:402937-402982` (offset `0x0a9b38`) and tx6 `:403148-403190` (`0x0a9cbc`). Generated code is not a production caller.
* Generated Stub dispatch: tx7 `:403487-403510` (`0x0aa100`) and tx6 `:403505-403530` (`0x0aa15c`). Dispatch is not a production caller.
* Server edges: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:95877-95888` (tx7) and `:95943-95954` (tx6), each delegating to `ProxyReceiver`.
* The only source-level caller outside generated code is `tools/test-launcher-phase4/src/org/fireosresearch/phase6ip/proxy/ProxyReceiverGateProbeActivity.java:53-61,80-124`; its manifest is `tools/test-launcher-phase4/config/AndroidManifest-phase6ip-amazon-proxy.xml`. It is TEST_ONLY.
* No matching production callsite was found in exact disassembly, JADX, standalone smali, VDEX inputs, fosinit registrations, or searched manifests. No JADX/standalone-smali implementation was available; record as `NOT_FOUND`, not inferred.

## tx6 — registerProxyReceiver

`ProxyReceiver.registerProxyReceiver` first reads `PendingIntent.getCreatorPackage()` and requires that package's `ApplicationInfo.FLAG_SYSTEM` via `checkCallerIsSystemApp()` (`fosservices/disassembly.log:97887-97900`; offsets `0x06b1a6-0x06b1ba`). No method-local Binder permission or direct caller-UID check occurs before this gate. A new action additionally requires `queryBroadcastReceivers(PendingIntent.getIntent(), 0)` to be non-empty; same-action duplicate handling compares creator UIDs (`:97901-97976`).

After acceptance, the first state consumer is `mOnTheFlyRegisteredIntents`, keyed by action. A new action creates an `IntentFilter`, calls `Context.registerReceiver`, and stores the token (`:97968-97986`). Later `ProxyReceiver$1` starts `ProxyIntentThread`, which invokes `PendingIntent.send()` (`:97704-97754`, `:97670-97699`). No edge to package enabled state, preferred activities, HOME resolution, or Fire Launcher state was found. No `clearCallingIdentity()`/`restoreCallingIdentity()` appears in the tx6 slices.

Existing Phase6IP evidence is only an ordinary-app negative boundary: `pm_handle=true`, `app_is_system=false`, `tx6=false`, `receiver_hits=0`. It does not establish system-token provenance.

## tx7 — deregisterProxyReceiver

`ProxyReceiver.deregisterProxyReceiver` synchronizes on `mOnTheFlyRegisteredIntents`; removal succeeds only when stored `PendingIntent.getCreatorUid()` equals `Binder.getCallingUid()` (`fosservices/disassembly.log:97828-97870`; offsets `0x06b0b0-0x06b17c`). Missing action/map/entry returns false. No separate permission marker or identity clear/restore appears in this path.

The first state consumer is the action list. Empty action lists remove the key; an empty map calls `Context.unregisterReceiver` (`:97842-97878`). No package-state or HOME sink follows. Existing Phase6IP `tx7=false` had no caller-owned entry; no cross-UID removal was attempted.

## Publication, SELinux, permission, manifest, and sink disposition

`artifacts/phase6jd-fosinit-20260808-01/system/fireos/etc/init/amazonpackagemanager_fosinit.xml:9-10` publishes `AmazonPackageManagerService`; its callback and `AmazonPackageManagerImpl` registrations are not tx6/tx7 callers. Phase6JD's complete fosinit audit found no new PackageManager/HOME writer edge.

SELinux labels the service `amazon_package_manager_service`. Existing Phase6ES/6AQ evidence shows shell UID 2000 `service_manager:find` denied while ordinary-app service lookup is allowed for the relevant app-API class. This is reachability only; it does not authorize tx6/tx7. The Java FLAG_SYSTEM and creator-UID gates remain decisive.

`amazon.permission.ADD_RM_PKG_METADATA` is declared `signature|amazon` (`artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt:1937`), but its check belongs to the four metadata mutators, not tx6/tx7.

The first sink is the internal receiver/map and then `PendingIntent.send()`; the first package/HOME/system sink is **NOT_FOUND**. Phase6MN/6PZ and Phase6JD likewise found no tx6/tx7 path to a User-0 Fire/HOME/package-state writer. Next safe step: inspect only newly supplied offline exact-build artifacts for legitimate system-created-token provenance and a production callsite. Do not synthesize a token, guess parcels, or replay tx6/tx7.

## Evidence hashes

`boot-fosframework/disassembly.log` `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`; `fosservices/disassembly.log` `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`; fosinit `eb53e50cf72174eddcde25fd3538e4736d2cd4cb7866bab4e5bc2b70fc514286`; Phase6IP finding `f26b81342c1554fada6eafd1e19cdd5f70fae5991d1337fbad6c807e7792208e`; Phase6PZ index `d11da287a94cb5c149aa2102cfca656a8e5641e15aea475814fb44a10dcb3028`; probe source `334fd9a1c43a02403d2e440664ab6f675bd9b89738fa3c2b06590c9ee92c0df5`; probe manifest `3808c97dd7acf95488bcca1938bca026c6d2614c71e0721190203206e63daa82`; SELinux AVC `d436542564947472c1b2481519312542d7d1053512b9cb47c68abbb981e0b0a4`; permission evidence `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`.

