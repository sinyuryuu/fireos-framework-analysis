# Phase 9B — KFT tx3 client identity / authorization closure

日期：2026-08-10（Asia/Taipei）。本報告只做 host-only 靜態分析；未執行 adb、service call、Binder transaction、user/package mutation、driver ioctl、root 或 exploit。既有 runtime/ADB 結果只作引用，不視為本輪執行。

## 結論

`IAmazonUserManager` transaction 3 的 method 是 `enableKftLauncher(UserInfo)`。保存 corpus 中唯一閉合的 production **external Binder semantic caller** 是 `AmazonUserManagerImpl.createChildUser(String)`：它以 flags `0x8000` 建立 child，將同一 `UserInfo` 送入 framework proxy，proxy 以 descriptor `amazon.os.IAmazonUserManager` 呼叫 `transact(3, ...)`。

但 `AmazonUserManagerImpl` 位於 `boot-fosframework` 的公共 `amazon.os` framework manager，不是 APK package。現有 disassembly/JADX/manifest/UID corpus 沒有把 `createChildUser()` 的 callsite 再連到某個 APK。故「真正 external client package」目前不能安全寫成已證實值：

* `com.amazon.frameworksettings` 是最強 package candidate：保存 package dump 顯示 UID **10112**、`/system/priv-app`、privileged，manifest/privapp policy 具 `MANAGE_USERS`、`INTERACT_ACROSS_USERS`；但沒有 exact `createChildUser → tx3` APK callsite，故是 **candidate, not confirmed caller**。
* `com.amazon.h2settingsfortablet` 是同型候選：保存 package dump 顯示 UID **10130**，亦是 `/system/priv-app`，privapp policy 具 `MANAGE_USERS`、`INTERACT_ACROSS_USERS`；同樣沒有 tx3 callsite join。
* 不能把 ordinary APK、shell、`com.amazon.frameworksettings` 或 H2 package 單憑 service publication/manager API 推定為任意 tx3 caller。

`AmazonUserManagerService.onBootPhase(500)` 是另一條 **system-server local call**：在 `isUpgrade()` 與 `isChildUser(UserInfo)` 條件下，直接呼叫 `mBinderService.enableKftLauncher(UserInfo)`；它沒有 Binder tx3、沒有 external caller UID。這條路徑不能用來證明外部 Binder tx3 的 authorization。

## Caller → gate → identity → scope → sink → effect

### 1. External wrapper / tx3

`AmazonUserManagerImpl.createChildUser(String)` → `createUser(name, 0x8000)` → `getAmazonUserManager()` → `IAmazonUserManager.enableKftLauncher(UserInfo)` → Proxy `transact(3)` → Stub `enforceInterface`/nullable `UserInfo` decode → `BinderService.enableKftLauncher`。

Wrapper side 沒有 caller package/UID check；Stub bounded branch 只看到 interface-token enforcement、parcel decode 與 dispatch，沒有 method-local `getCallingUid`、`checkCallingPermission`、`MANAGE_USERS` 或 explicit cross-user check。服務中另有 `checkManageUsersPermission(String)`，允許 UID 0/1000 或 `android.permission.MANAGE_USERS`，但保存 call graph 沒有 tx3 → 該 helper edge，不能回填為 tx3 gate。

`enableKftLauncher` 前段 writer 在 `clearCallingIdentity()` 之前；後段 DPM/profile-owner path 才 clear/restore。不能把後段 clear identity 倒推成前段 PMS setter 以 system identity 執行。

### 2. Service declaration / service_manager / SELinux

`fosinit` 以 `com.amazon.android.server.pm.AmazonUserManagerService` 發布 `amazonusermanagerservice`，並以 vendor manager 將 `user` manager 映射到 `amazon.os.AmazonUserManagerImpl`。這證明 declaration/publication，不證明每一個 package 都能取得 handle。

保存 policy/runtime evidence 只支持 domain-specific boundary：shell UID 2000 在 enforcing policy 下的 service-manager `find` 被拒；ordinary-app handle reachability 曾有保存證據，但該證據只證明 lookup/interface reachability，不證明 tx3 authorization 或 writer success。service-manager allow tuple 對每個候選 client 的 exact package/domain 映射仍是 missing edge。

### 3. Cross-user / PMS downstream

writer 讀傳入 `UserInfo.id`，沒有常數 User 0，也沒有 `setHomeActivity`、`replacePreferredActivity` 或 formal HOME setter：

| sink | argument | effect |
|---|---|---|
| `setComponentEnabledSetting(com.amazon.tahoe/.launcher.FreeTimeLauncherActivity, 1, 1, userId)` | `UserInfo.id` | 對 supplied user 啟用 Tahoe FreeTime launcher component |
| `setApplicationEnabledSetting(com.amazon.firelauncher, 2, 0, userId)` | `UserInfo.id` | 對 supplied user 停用 Fire Launcher application |
| `setApplicationEnabledSetting(com.android.launcher3, 2, 0, userId)` | `UserInfo.id` | 對 supplied user 停用 Launcher3 application |

因此 genuine child lifecycle 的 effect 是 child/profile package/component state，並非固定 User-0 HOME replacement。既有 ordinary User 10 / User 0 attempts 的 PMS downstream rejection 只作既有 evidence；本輪沒有重做。

## Identity disposition

| path | caller identity | gate | user scope | disposition |
|---|---|---|---|---|
| `createChildUser` → Binder tx3 | exact APK package/UID unresolved; semantic caller is framework `AmazonUserManagerImpl` | child creation `0x8000` confirmed; tx3 local permission/UID and inherited gate unresolved | newly returned child `UserInfo.id` | confirmed static edge, external package missing |
| `onBootPhase(500)` → local method | system-server lifecycle, no Binder caller | `isUpgrade && isChildUser` | each child entry from `UserManager.getUsers()` | confirmed local path, not tx3 |
| `BinderService.enableKftLauncher` → PMS setters | incoming Binder identity remains relevant before downstream gates; no tx3 clear before setters | KFT/TV/existence helper plus PMS component/application gates | supplied `UserInfo.id` | confirmed writer, no User-0 constant |
| candidate `com.amazon.frameworksettings` | UID 10112; package join to tx3 absent | manifest/privapp grants positive, exact service-manager allow and exact callsite absent | would be caller-supplied | candidate only |
| candidate `com.amazon.h2settingsfortablet` | UID 10130; package join to tx3 absent | manifest/privapp grants positive, exact service-manager allow and exact callsite absent | would be caller-supplied | candidate only |

## Missing-edge ledger

1. Exact APK/native/runtime callsite that invokes `AmazonUserManagerImpl.createChildUser`.
2. Exact external package→UID→signing certificate join for the tx3 invocation; package candidates above are not proof.
3. Service-manager SELinux allow tuple for each candidate domain/package and exact declaration permission, if any. The fosinit XML has no method permission declaration.
4. Whether `checkManageUsersPermission` is inherited through an omitted superclass/interface/alias path; direct tx3 edge is absent in the bounded corpus.
5. Complete cross-user/admin validation between parcelled `UserInfo.id` and PMS setter gates.
6. Any runtime-loaded/native/alias caller outside retained JADX/disassembly corpus.

## Evidence and hashes

| evidence | location | SHA-256 |
|---|---|---|
| boot framework disassembly | `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:369180-369243,369080-369095,370378-370428,370637-370750` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` |
| fosservices disassembly | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54478,54847-54895,55053-55119` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| service declaration | `artifacts/phase6jd-fosinit-20260808-01/system/fireos/etc/init/amazonusermanager_fosinit.xml` | `14ccd432e6393ce1660ad51c10430c392a3562be3ef20ee2bdfe62a2240e8678` |
| frameworksettings manifest | `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/008_com.amazon.frameworksettings__0_com.amazon.frameworksettings.xmltree.txt:2-28` | `674c6aa94350761cf2a239f1ffd9099e8dcd3d1f9172a1480e6a5f8a6e2346bd` |
| frameworksettings UID/signature dump | `artifacts/phase6x/prewarm-authorization-20260805-02/com_amazon_permission_APP_PREWARM.block.txt:10774-10809` | `4a71d4d60cdb6c45233e270e3548f02c9ea77e9d3b3b4ed33a7aeb1e130bb798` |
| H2 manifest | `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/006_com.amazon.h2settingsfortablet.xmltree.txt` | `6e1edce5feb0eb638e04d569f4df9752234ac3c5fd6f33b8169a56c30781ee0c` |
| privapp grants | `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/permissions/privapp_permissions.xml:203-217` | `643cf114ed7d7b82a642fea650ed7d2f53b5dab2291e4f043c272cbe577df732` |

## Status

**PARTIALLY CLOSED — exact external APK client identity remains unresolved.** The tx3 contract, sole retained semantic caller, local onBootPhase distinction, service publication, candidate package/UID/permission facts, PMS setter sinks, and supplied-user scope are closed. No evidence supports treating tx3 as arbitrary caller or as a User-0 HOME selector.
