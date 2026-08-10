# Phase 8A：host-side closure — Amazon prewarm caller/user

日期：2026-08-10。此報告只讀取 Phase 7 P7B-001、既有 FOS/PS7331 OTA disassembly、JADX/smali、fosinit、manifest、permission-holder 與已保存 capture。沒有執行 ADB、service call、Binder transaction、APK 建置/安裝、設定或 package mutation、driver/root/exploit。

## 結論

P7B-001 的 caller/reachability 需要修正為分層結論：

- ordinary app **可達且已有保存的成功證據**：Phase6ER 的無權限 probe（UID 10198）取得 `amazonactivitymanager` handle，tx1 回傳 0，target process 出現。這證明的是 process/resource prewarm confused deputy，不是 HOME、PMS preferred-activity、package/component-state、root 或 privilege-grant primitive。
- shell **在保存的 enforcing capture 中不可達**：UID 2000 的 `service_manager find` 被 `amazonactivitymanager_service` policy deny；沒有 shell Binder entry 或 sink evidence。這是 saved-policy bounded negative，不是對所有 SELinux domain/build 的 universal negative。
- Alexa 是 retained JADX corpus 中唯一 exact direct source caller：`ExplicitIntentAction.prewarmApplicationProcess` → `AmazonActivityManagerImpl` → `IAmazonActivityManager`，傳入 `(targetPackage, 0, foregroundProfileId)`。Alexa manifest request、system priv-app path 與 permission definition holder 均有證據；Alexa 的 effective installed APP_PREWARM grant 沒有在保存 bounded dump 中被單獨列出，故不補推。

## Exact call/bind/transaction chain

```text
Alexa ExplicitIntentAction.prewarmApplicationProcess
  → AmazonActivityManagerImpl
  → ServiceManager.getService("amazonactivitymanager")
  → IAmazonActivityManager.Stub.asInterface
  → IAmazonActivityManager.Stub.Proxy.preWarmApplicationForUser
  → IBinder.transact(code=1, String package, int flags, int user)
  → IAmazonActivityManager.Stub.onTransact
  → AmazonActivityManagerService.BinderService.preWarmApplicationForUser
  → Context.checkCallingPermission(APP_PREWARM)
  → Binder.clearCallingIdentity
  → IPackageManager.getApplicationInfo(package, 1024, user)
  → PreWarmCacheHelper.getKeepIfLargeValue
  → ActivityManagerService.startProcessLocked(..., "prewarm", ...)
  → Binder.restoreCallingIdentity (normal/exception cleanup path)
```

The host artifacts identify the bind/lookup site at boot-fosframework disassembly `553272-553277`, wrapper forwarding at `553433-553440`, OTA Proxy at `4464666-4464696`, and server method at OTA `3642543-3642624` (FOS equivalent `40453-40534`). The interface descriptor is `com.amazon.android.server.am.IAmazonActivityManager`; transaction code is `1`; parcel fields are `String + int + int`.

## Permission holder/grant closure

`com.amazon.permission.APP_PREWARM` is defined by `android.amazon.perm`, UID 1000, with `signature|amazon` protection. Alexa declares the permission in its manifest and the known Alexa implementation is under a system priv-app path. Those facts establish holder and requester declaration, not an independently enumerated effective grant record. The ordinary Phase6ER probe had no declared permissions, yet its saved result shows successful tx1/process effect. Therefore the result is not described merely as “permission result not consumed”: static defect plus independently saved ordinary-app effect are both recorded, while the missing Alexa grant join remains UNKNOWN.

## Identity and user scope

The server checks calling permission while the incoming Binder identity is present, immediately clears identity, and restores it after the process path. No caller UID/package is consumed after the clear. The explicit user integer reaches `getApplicationInfo`; no method-local target-user validation or cross-user restriction is recovered. Alexa passes `0` plus `foregroundProfileId`; the ordinary probe used user 0. Cross-user behavior and the exact foreground-profile-to-OS-user mapping remain UNKNOWN.

## Sink and effect boundary

The first stateful sink is `startProcessLocked(..., "prewarm", ...)`, after package lookup and `PreWarmCacheHelper`. The retained path contains no `setHomeActivity`, `replacePreferredActivity`, persistent preferred activity, component/package enable/disable, settings writer, root transition, or permission grant. Existing Phase6ER before/after state records Fire Launcher HOME and Fire package state unchanged.

## Search disposition and missing edges

Exact retained search finds the interface declaration, framework wrapper, Proxy, server implementation, Alexa source call, APP_PREWARM requester declaration, holder definition, and service publication. No second exact source caller is established in the retained JADX corpus; unindexed APK/native/dynamic callers remain outside scope. Remaining edges are: effective grant to Alexa/other accepted callers, complete Stub/onTransact method authorization, service-manager policy for non-shell domains, explicit target-user validation, full caller UID/package provenance after identity clear, and any downstream consumer outside the reviewed system_server slice.

The CSV companion records every closure row with the required schema and SHA-256 values. Status deliberately separates `confirmed-ordinary-app-reachable`, `bounded-negative-shell`, and `reconciled-P7B-001`; no permission-result omission is promoted to a vulnerability without the independent reachability/effect evidence.
