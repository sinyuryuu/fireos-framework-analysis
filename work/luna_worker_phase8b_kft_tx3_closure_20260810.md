# Phase 8B：host-side closure — KFT tx3 / createChild / enableKftLauncher

日期：2026-08-10（Asia/Taipei）。本項為唯讀 host-side closure。未呼叫 private Binder、未送 service call、未建立或切換 user、未改 package、未 replay PMS setter，亦未使用 ADB mutation、root 或 exploit。

## 結論

`IAmazonUserManager` transaction **3** 的 exact method 是 `enableKftLauncher(UserInfo)`。Generated Proxy 將 nullable `UserInfo` parcel 後呼叫 `IBinder.transact(3, ...)`；Generated Stub 的 tx3 branch 只在 bounded slice 看到 interface-token enforcement、反序列化與 method dispatch，沒有看到 method-local `getCallingUid`、`checkCallingPermission`、`MANAGE_USERS` 或 cross-user check。

已恢復的 production caller 有兩條：

1. `AmazonUserManagerImpl.createChildUser(String)`：先以 `createUser(name, 0x8000)` 取得 child `UserInfo`，再將同一物件送入 `IAmazonUserManager.enableKftLauncher(UserInfo)`（tx3），隨後送 tx4 setup-complete。這是唯一閉合的 external-client-to-tx3 static edge；client 的 exact package、UID、signing certificate/signature gate 沒有在保存 corpus 中恢復，故不推定為任意 caller。
2. `AmazonUserManagerService.onBootPhase(500)`：這是 system-server 內部 local call，不是 Binder tx3。分支要求 `isUpgrade()` 且對 `UserManager.getUsers()` 結果套用 `isChildUser(UserInfo)`，才對每個 child entry 呼叫同一個 `BinderService.enableKftLauncher(UserInfo)`，並接 tx4。

`checkManageUsersPermission(String)` 確實存在，允許 UID 0/1000 或 `android.permission.MANAGE_USERS`，但保存的 direct callers 是 sorted-list/profile-policy 路徑；沒有證據把它接到 tx3。故 gate 結論是「internal child lifecycle gate confirmed；tx3 method-local authorization and complete external caller gate unresolved」，不是「無權限可利用」。

## UserInfo.id、sink 與 scope

`enableKftLauncherComponent(UserInfo)` 沒有 hard-coded User 0，三個 sink 都讀傳入的 `UserInfo.id`：

- `com.amazon.tahoe/.launcher.FreeTimeLauncherActivity`：`setComponentEnabledSetting(..., 1, 1, userId)`；
- `com.amazon.firelauncher`：`setApplicationEnabledSetting(..., 2, 0, userId)`；
- `com.android.launcher3`：`setApplicationEnabledSetting(..., 2, 0, userId)`。

因此 genuine child/profile path 是 child/profile-scoped package/component writer。它不是 `setHomeActivity`、`replacePreferredActivity` 或其他 formal preferred-HOME setter，也沒有恢復 User 0 Fire HOME 的 static edge。既有 child captures 顯示 child Tahoe HOME 與 owner User 0 Fire HOME 可並存；這些 captures 沒有被當成新 tx3 invocation attribution。

## Binder identity、publication 與 caller boundary

tx3 entry 到 writer 的 bounded slice 沒看到 `clearCallingIdentity`；另一路 DPM/profile-owner work 的 clear/restore identity 是後續分支，不能回填成 tx3 gate。Service 在 `onStart` 下以 `amazonusermanagerservice` 發布 `BinderService`，fosinit 路徑為 `/system/fireos/etc/init/amazonusermanager_fosinit.xml`。保存 runtime evidence 顯示 shell UID 2000 在 enforcing SELinux 下對 `amazonusermanagerservice` 的 service-manager `find` 被拒絕；這只關閉保存的 shell route，不足以證明所有 external package/UID/signature caller 都不可達。

## Evidence baseline

主要 evidence：

- `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log`：Proxy/Stub 與 `createChildUser`；SHA-256 `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`。
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`：service method、三個 PMS setters、helper、publication、boot-phase loop；SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`。
- Phase 7 baseline：`output/tables/phase7-control-surface.csv` rows P7-IPC-003/P7-IPC-004；SHA-256 `1d10e729806a748b77b52ce88449a9c0fa20315faa84e55948e30be16fb1dda8`。
- Phase 6UB/6UF saved analyses：caller scope、gate disposition、UNKNOWN ledger；各自 hash 已列於 CSV。
- fosinit/service boundary：`output/tables/phase6jd-fosinit-registration-audit.csv`；SHA-256 `6fe2fa8a27fd2e753fb34f7fd162f051ab9bae6d0667290d4f2af8fef40e1503`；saved AVC capture `adb/phase6cz/.../audit_logcat.stdout.txt`；SHA-256 `bbb8b23472b52720dd4ad2cba0ce327f8c528af2c29ad60f78b0f8793de6ff7f`。

逐 edge 的 `id,entry,transaction,client,caller_gate,binder_identity,user_scope,target,sink,effect,status,evidence,evidence_sha256,missing_edge` 已輸出至同名 CSV。所有未恢復欄位保留 `missing_edge`，沒有以推測補齊 package/UID/signature、service-context allow tuple、PMS downstream permission result 或 User-0 restoration caller。

## Status

**PARTIALLY CLOSED / STATIC AUTHORIZATION REVIEW POINT**：tx3、client callsite、child lifecycle predicates、`UserInfo.id` propagation、三個 PMS setter sinks 與 User-0 separation 已閉合；external caller package/UID/signature、service declaration permission、完整 cross-user/admin authorization、fresh tx3 runtime attribution 仍是明確 missing edges。後續不應透過 transaction replay 取得這些缺口。
