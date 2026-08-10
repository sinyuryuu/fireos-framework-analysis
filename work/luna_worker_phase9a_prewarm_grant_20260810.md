# Phase 9A — `amazonactivitymanager` tx1 prewarm grant closure

日期：2026-08-10（Asia/Taipei）  
範圍：host-only 靜態分析；只讀 Phase 6/7/8 artifacts、保存的 package/SELinux capture、FOS/PS7331 disassembly 與 JADX/smali。未執行 adb、service call、Binder transaction、APK 安裝、driver open/ioctl、root、exploit 或任何裝置 mutation；未修改既有檔案。

## 結論

在保留的 production source/package artifacts 中，transaction 1 的 exact direct production caller 是：

```text
com.amazon.alexa.multimodal.gemini (UID/userId 10044; /system/priv-app)
  ExplicitIntentAction.prewarmApplicationProcess(String)
  -> AmazonActivityManagerImpl
  -> ServiceManager.getService("amazonactivitymanager")
  -> IAmazonActivityManager.Stub.Proxy.preWarmApplicationForUser
  -> IBinder.transact(1, String targetPackage, int flags=0, int user=foregroundProfileId)
  -> AmazonActivityManagerService.BinderService.preWarmApplicationForUser
  -> checkCallingPermission(APP_PREWARM)
  -> clearCallingIdentity()
  -> IPackageManager.getApplicationInfo(target, 1024, user)
  -> PreWarmCacheHelper.getKeepIfLargeValue(target)
  -> ActivityManagerService.startProcessLocked(..., reason="prewarm", ...)
  -> restoreCallingIdentity()
```

Alexa 的 effective grant 已由保存的 package dump 明確列出：`com.amazon.permission.APP_PREWARM: granted=true`。Permission definition holder 另由保存的 permission block 證實為 `android.amazon.perm`, UID 1000, `signature|amazon`。這閉合了 Alexa caller→package/UID→effective grant；但不把 declaration 或 holder 誤當成 grant。

## Caller、identity 與 grant

唯一在保留 JADX source 中找到的 exact direct caller 是 `ExplicitIntentAction.prewarmApplicationProcess`（source 268–282）。它在 target 非 null、manager 非 null、且 target 不等於自身 package 時呼叫 `(str, 0, mBroadcaster.getForegroundProfileId())`。保存 package dump 同時記錄 package `com.amazon.alexa.multimodal.gemini`、`userId=10044`、`codePath=/system/priv-app/...`，以及 `APP_PREWARM: granted=true`。

Server method 的 bounded instruction stream 在 incoming Binder identity 仍存在時呼叫 `Context.checkCallingPermission(APP_PREWARM)`；其後直接 `Binder.clearCallingIdentity()`，未觀察到 move-result、比較、拒絕分支或 `SecurityException`。因此「grant 對 Alexa 有效」與「method 是否正確消費 check 結果」是兩個分開的 edge。保存 Phase6ER evidence 另記錄無宣告 permission 的 ordinary APK UID 10198 成功到達 tx1/process effect；這是既有 evidence，不是本 Phase 的 runtime action。

## Service-manager / SELinux gate

`amazonactivitymanager_fosinit.xml` 證實 system-server vendor service 由 `AmazonActivityManagerService` 發布，且 activity manager fetcher 對應 `amazon.app.AmazonActivityManagerImpl`。保存 enforcing AVC capture 證實 shell UID 2000 / `u:r:shell:s0` 的 service-manager `find` 被 `amazonactivitymanager_service` policy deny，因此 shell 在該 capture 未進入 method。這是 saved-policy bounded negative；不能外推到其他 SELinux domain、alternate handle/wrapper 或 future build。對 Alexa domain 的 service-manager/SELinux allow tuple，本 corpus 沒有獨立 TE allow record，故標為 UNKNOWN；production call path 與已保存 package grant 是正證據，但不替代 domain-specific policy evidence。

## User validation 與 sink/effect

Proxy/Stub contract 已閉合為 tx1、parcel `String + int + int`。Alexa 傳入 `flags=0` 與 `foregroundProfileId`；server 將 user integer 原樣帶入 `IPackageManager.getApplicationInfo(target, 1024, user)`。在 reviewed method block 中沒有恢復出 explicit target-user validation、cross-user check、`UserHandle` normalization 或 foreground-profile-to-OS-user mapping，因此：

- user argument propagation：CONFIRMED；
- Alexa `foregroundProfileId` 的 exact numeric OS-user mapping：UNKNOWN；
- cross-user/target-user acceptance policy：UNKNOWN；
- caller UID/package 在 `clearCallingIdentity()` 後仍可供 downstream gate 使用：未觀察到，標為 UNKNOWN/NOT SHOWN。

第一個 stateful sink 是 `ActivityManagerService.startProcessLocked(..., "prewarm", ...)`；`getApplicationInfo` 與 `PreWarmCacheHelper` 是其前置 lookup/cache path。reviewed slice 沒有 `setHomeActivity`、`replacePreferredActivity`、persistent preferred activity、package/component enable/disable、Settings writer、permission grant、root 或 exploit sink。故 effect 是 selected application process/resource prewarm，不是 privilege escalation；Phase6ER 的保存 before/after invariants 也記錄 HOME、Fire package state 與 user state 未改變。

## Edge disposition

| Edge | Disposition |
|---|---|
| exact production caller | CONFIRMED: Alexa `ExplicitIntentAction.prewarmApplicationProcess` |
| caller package / UID | CONFIRMED: `com.amazon.alexa.multimodal.gemini`, UID 10044 |
| effective `APP_PREWARM` grant | CONFIRMED: saved package dump `granted=true` |
| permission holder/protection | CONFIRMED: `android.amazon.perm`, UID 1000, `signature|amazon` |
| service publication / tx1 | CONFIRMED statically |
| Alexa domain service-manager/SELinux allow | UNKNOWN |
| shell service-manager gate | BOUNDED NEGATIVE: saved enforcing AVC deny |
| user integer propagation | CONFIRMED |
| exact profile→OS user mapping | UNKNOWN |
| explicit target-user/cross-user validation | UNKNOWN |
| post-clear caller identity at sink | UNKNOWN / not shown in reviewed slice |
| sink | CONFIRMED: `startProcessLocked(..., "prewarm", ...)` |
| effect | Process/resource prewarm only; HOME/package/privilege effect not found |

## SHA-256 evidence manifest

```text
ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c  decompiled/baksmali/vdexExtractor/fosservices/disassembly.log
fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71  decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log
04d68d0bb562a14e9cbff3bdce63b66eb911ee4bb7e728ca77cd435a5b03c146  decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log
c1a8bcfc0952239a26b669f7bc227fcc01024ac5db26db7e6eed2ae5cb6a2dc2  artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/amazon/speech/sim/router/intentrouter/ExplicitIntentAction.java
cc0a7b0df71c627ce09849b573e44491db3c715d365b631e3325d28623638f0d  artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/resources/AndroidManifest.xml
fe5f1ddaab5c8c0ae3b1345f1dc92fa62cb409f1aaf5da8691563f12704d7809  artifacts/phase6j/ota-alexa-system-ota-device-20260805-01/dumpsys-package.stdout.txt
b26d2a7083c743893fc2dc382b2cf276c0dbe268517dac76039e3267d318d88b  artifacts/phase6j/ota-alexa-system-ota-device-20260805-01/pm-path.stdout.txt
4a71d4d60cdb6c45233e270e3548f02c9ea77e9d3b3b4ed33a7aeb1e130bb798  artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt
5d212c94f047aee7abc85ef6dc99aa92ca61e3e3d9318bb69db3c10d9e0da411  artifacts/amazon-services/amazonactivitymanager_fosinit.xml
d436542564947472c1b2481519312542d7d1053512b9cb47c68abbb981e0b0a4  artifacts/phase6aq/public-summary-20260805-01/amazon-service-avc.txt
230a59769bfed7ede022259295c2f034c05a5f044a8da8115b2ac1caacda49ae  adb/phase6er/PHASE6ER-UNTRUSTED-SERVICE-LOOKUP-20260806-134346/result.json
```
