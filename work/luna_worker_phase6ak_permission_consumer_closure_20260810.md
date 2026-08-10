# Phase 6AK — permission consumer closure (host-only)

日期：2026-08-10（Asia/Taipei）。本輪只讀取已保存的 Phase6X3 `6AE-007` / Phase6X2 `6X2-ROUTES-005` ledger、exact permission manifests、APK/JADX/VDEX 與既有 H2 permission/grant records。沒有安裝或授權 permission、沒有啟動 component、沒有 bind/call service、沒有呼叫 Binder、沒有操作設備。

## 結論

`android.amazon.perm` 的四個目標 declaration 已確認：

- `com.amazon.tv.developer.sdk.personalization.USE_SDK`：raw `protectionLevel=0x0`，normal。
- `com.amazon.tv.developer.sdk.content.USE_SDK`：raw `protectionLevel=0x0`，normal。
- `com.amazon.mw.permission.PLUGIN`：raw `protectionLevel=0x1`，dangerous。
- `com.amazon.mw.permission.PLUGIN_CONSUMER`：bounded declaration 沒有 `protectionLevel` attribute，故為 `UNKNOWN`；不可自行解碼。

在保存的 exact manifest union、APK/JADX 與 VDEX corpus 中，四者均沒有可閉合的 requester → uses-permission → holder/grant → exported consumer → method-local check → identity → sensitive sink 鏈。四列均標為 `UNKNOWN_NOT_CLOSED`；bounded scan 可寫成 negative，但不是全映像不存在的證明。

H2 是獨立的正向靜態鏈：`com.amazon.alta.h2clientservice.permission.BIND_SERVICE` 的 effective owner 是 `android.amazon.perm` / UID 1000，permission record 為 `signature|amazon`；保存 manifests 顯示六個 exact requester package 的 `uses-permission`，另有十個 explicit grant candidates。H2 `H2ClientService` 是 exported、singleUser、directBootAware service，且服務端 Stub 將 AIDL methods 導向 household/profile workflow。`AbstractAPICall` 只記錄 `Binder.getCallingUid()`；沒有 recovered method-local accepted-UID/permission check。實際 bind client、caller signing identity 與 runtime accepted caller 仍為 `UNKNOWN`。

H2 可閉合的 downstream sink 是 profile lifecycle（例如 `addUser` → `CreateAndroidUserCommand` → `AndroidUserHelper` → `AmazonUserManager.createAdultUser/createChildUser`）。保存 JADX corpus 沒有 H2 → `setHomeActivity`、preferred HOME、`setComponentEnabledSetting` 或 `setApplicationEnabledSetting` 的 edge；此項是 bounded negative，不是 corpus 外的 universal absence claim。

完整逐列 ledger（每列包含 SHA、行號、caller、gate、identity 與 sink）見 [CSV](./luna_worker_phase6ak_permission_consumer_closure_20260810.csv)。

## Evidence anchors

1. `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`，SHA-256 `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`，lines 59, 65, 183, 1047：四個 permission declaration 與 raw protection values。
2. H2 exact expanded manifest `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/manifests/017_com.amazon.h2clientservice.xmltree.txt`，SHA-256 `f14670a78cdbddf4c46375d78e1607fe491c33fd4d807de57abfe5e2b5300242`，lines 69–74, 102–110：custom permission、exported service、singleUser/directBootAware 與 service permission。
3. H2 effective owner/grant record `artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt`，SHA-256 `4a71d4d60cdb6c45233e270e3548f02c9ea77e9d3b3b4ed33a7aeb1e130bb798`，lines 3329–3334, 7538, 8780, 11251, 11568, 13410, 15146, 15880, 17940, 18450, 19476, 21051：owner UID 1000、十個 explicit grant candidates 與 H2 service resolution。
4. H2 JADX `H2ClientService.java`，SHA-256 `f30c3b42ce45c1e7ef717b2deb5b0402dbc01fc70cb5a86480d8b4a54e7fa9e5`，lines 165–274：exported service 的 `onBind` / AIDL Stub dispatch。
5. H2 JADX `AbstractAPICall.java`，SHA-256 `9d843f825ae30e06e2e6d7598f8b49f90904bdd66c88660e18ce1f03d02421da`，line 43：`Binder.getCallingUid()` logging；不是 authorization gate。
6. H2 profile sink files：`HouseholdController.java` SHA `8ebf9b15185e298da784bb15918787fb0f37e805664ccbc780b6b5dca26ffcd2` lines 323–373；`CreateAndroidUserCommand.java` SHA `843d03e3aa01d59743dc8a5498975ff59f4930b35f6690ad3c7f5aa44fb594e2` lines 20–37；`AndroidUserHelper.java` SHA `31de59672ee1be20760377643c25f9f673c3c7ce336537a40eca24acca489566` lines 78–90。

## Scope boundary

`uses-permission` declaration is not proof of a bind call; a grant candidate is not proof of consumer behavior; exported is not proof of ordinary-app reachability; low protection level is not proof of a sensitive sink. No runtime operation was used to fill any missing edge. Any future closure requires additional preserved exact-build requester/consumer APK or source artifacts and a static caller-to-sink join only.
