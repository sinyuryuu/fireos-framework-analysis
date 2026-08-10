# Phase 10B — DevicePolicy/Profile IPC caller and user-scope closure

日期：2026-08-10。範圍依縮小要求，僅讀取既有 Phase 8B、9B、10A 產物與 exact-build `fosservices`/`boot-fosframework` disassembly、AmazonDevicePolicyManagerService、AmazonProfileService、KFT AIDL/Proxy/Stub、manifest/privapp/SELinux artifacts。沒有執行 adb、裝置命令、Binder/service call、user creation/switch、package/settings mutation、driver/root/exploit；只新增本報告與 CSV。

## 最小結論

在保留 UNKNOWN 的前提下，沒有閉合出普通 app 或 shell 可導向 User 0 package state、Fire HOME、device owner/policy 或 profile transition 的完整鏈。最接近的靜態高影響點是 KFT `IAmazonUserManager` tx3：Stub slice 只見 interface-token/parcel dispatch，實作把 caller-supplied `UserInfo.id` 傳到 Tahoe/Fire/Launcher3 package setters；但 external APK package/UID/signature、service-manager/SELinux client edge、完整 PMS gate 與 User-0 input 都未閉合。這不能僅因 missing `getCallingUid()` 或 service publication/export 而升格為漏洞。

`AmazonProfileService` tx41 的 ordinary caller boundary 已有下游 `INTERACT_ACROSS_USERS` gate；metadata receiver 的輸入 authenticity 較弱，但目前 sink 是 system-owned launch map，未閉合到 HOME/PMS。Amazon DPM tx1/tx2 有 MANAGE_USERS / active-admin-owner gate；DPM tx100 另有 owner/caller gate 與 PMS UID 1000 gate。Parental Controls 的 User-0 Profile Owner 真實存在，但保存 source 顯示固定政策/lock-task package list，沒有任意 launcher/package relay。

## Caller / identity / scope 判讀

- `AmazonUserManagerImpl.createChildUser(String) -> tx3` 是恢復的 semantic framework caller；它不是 APK package。Phase 9B 的 `com.amazon.frameworksettings` UID 10112、`com.amazon.h2settingsfortablet` UID 10130 只是權限/位置相符的 candidates，沒有 exact tx3 callsite，故 CSV 不將其寫成 caller。
- `AmazonUserManagerService.onBootPhase(500)` 是 system-server local lifecycle call：`isUpgrade()` 與 `isChildUser(UserInfo)` 成立後逐 child 呼叫同一 writer；無 Binder caller UID。這條 local edge 與 external tx3 必須分開。
- tx3 writer 讀 `UserInfo.id`，沒有 hard-coded User 0；後續 DPM `clearCallingIdentity()` 不能倒推成 package setters 之前已清除 identity。
- tx4 確認是 bounded settings-only deputy：clear/restore identity 後寫兩個 per-user setup settings，但沒有 HOME/PMS sink。
- tx41 的 ordinary caller 可到 Binder，但 execution 在 current-user/cross-user gate 停止；metadata `$13` 可將 system-app target 的 package/activity pair 寫入 persistent `launch_info_map_key`，其 downstream consumer 保留 UNKNOWN。

## User 0 優先判斷

目前最佳分類是 `NO_REACHABLE_ORDINARY_APP_OR_SHELL_USER0_HOME_POLICY_CHAIN_FOUND`。理由不是把 private/exported surface 當成安全證明，而是每條候選均缺少至少一個必要閉合邊：external caller package/UID/signature 或 SELinux/service-manager authorization、owner/admin gate、cross-user/PMS protected gate、或 downstream HOME/package sink。KFT tx3 是唯一仍需保留的高價值 static review point；它目前只能確定 child/profile-scoped writer semantics，不確定 ordinary external reachability與 User-0 acceptance。

## Evidence anchors / hashes

主要 exact disassembly：

- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` — `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`；DPM `45935–46108`，Profile metadata/tx41 `73714–73812`, `77222–77266`，KFT `54297–54566`, `55053–55119`。
- `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` — `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`；KFT client/Stub `369180–370777`，Profile tx41 Stub `378462–378525`。
- `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log` — `5ef6a8c6edea903e3bf7e5298be02041dc46be06881438457e79cbf8501b76df`；framework UserInfo parcel support.
- `artifacts/amazon-services/amazondevicepolicymanager_fosinit.xml` — `6fe0df7450551fb940f4169977d97b46bebb43bebef8a604ac77e0c40f91acee`；vendor service/callback/manager registration only, not caller authorization.
- `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/permissions/privapp_permissions.xml` — `643cf114ed7d7b82a642fea650ed7d2f53b5dab2291e4f043c272cbe577df732`；privapp grants are provenance evidence, not a tx3 callsite.
- `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/selinux/plat_service_contexts` — `73cc38daa6ea57b35889f05bea6d5258234f4982140eae0d0db0090c891fdf77`；service labels/context inventory does not by itself join an accepted client domain.
- `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/selinux/plat_sepolicy.cil` — `4056ed9140f6c201cb2dd55edf70041667a195e20233bb6a6a2468b40c9a872d`；per-domain allow tuple remains UNKNOWN where not explicitly joined.
- `artifacts/phase6ad/protected-broadcast-inventory-20260805-01/manifests/001_com.amazon.parentalcontrols__0_com.amazon.parentalcontrols.xmltree.txt` — `5ef89e517f53d6d3696df3a43df40502f651d57f0a27d62a445ddc518930c9db`；manifest/permissions/exported component evidence.

既有產物作為 bounded ledger：`work/luna_worker_phase8b_kft_tx3_closure_20260810.md`, `work/luna_worker_phase9b_kft_client_identity_20260810.csv`, `work/luna_worker_phase10a_package_manager_closure_20260810.csv`, 以及 parent/profile closure；CSV 逐列保留 evidence path、hash 與 missing edge。

## Row index

詳見 [phase10b CSV](./luna_worker_phase10b_dpm_profile_closure_20260810.csv)。共 8 rows，未閉合欄位均明確寫 `UNKNOWN`，沒有以 exported、publication、missing UID check 或 privileged declaration 單獨推論漏洞。
