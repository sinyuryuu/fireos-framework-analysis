# Phase 6Y — permission anomaly residual

日期：2026-08-10（Asia/Taipei）

## 新差異

相對 Phase 6X/6WL/6U* corpus，本輪只保留四個未被既有 permission-semantics/exported-surface rows 覆蓋的 exact declaration：

- `com.amazon.tv.developer.sdk.personalization.USE_SDK`：`protectionLevel=0x0`（normal）。
- `com.amazon.tv.developer.sdk.content.USE_SDK`：`protectionLevel=0x0`（normal）。
- `com.amazon.mw.permission.PLUGIN`：`protectionLevel=0x1`（dangerous）。
- `com.amazon.mw.permission.PLUGIN_CONSUMER`：bounded XML declaration 沒有 `protectionLevel`，故保留 `UNKNOWN`，不自行解碼。

四者的定義者均為 `android.amazon.perm`；該 manifest 宣告 `sharedUserId=android.uid.system`、`coreApp=true`。這是 owner 身分證據，不是任意 caller 的授權證據。限定的 exact host corpus 沒有把這四個 permission 接到 `uses-permission` requester、已授予 holder、exported service/provider/receiver/activity，或 fosservices/boot-fosframework 的 caller gate 與 sink；CSV 因而明確記為 `unknown/no bounded requester`、`holder/grant not established` 和 `none joined`。

## Gate / identity / sink review

本輪追蹤 exact `fosservices/disassembly.log` 的 `hasCallerGotPermission`、`Context.checkCallingPermission`、`Binder.getCallingUid` 與 `Binder.clearCallingIdentity`。ASP 的 `hasCallerGotPermission` → `checkCallingPermission(com.amazon.permission.ASP_PERMISSION)` → `-EACCES`，以及既有 APP_PREWARM、GLOBAL_SYNC、OTA、HOME 與 settings/package writer rows 已在既有 corpus，故不重列。對四個新 permission 沒有匹配的 method-local check、caller UID、identity clear 或 downstream callsite。

因此本輪沒有「真正缺失 gate」或「protectionLevel 過低已形成 exploit」的閉合證據。`0x0`/`0x1` 僅支持靜態低 protection candidate；沒有 consumer、caller、holder/grant 或 sensitive sink，不能推導 package/user/settings/HOME/OTA/keyguard/root effect。

## Scope and integrity

只讀 exact PS7331 decompiled/apktool XML-tree、fosservices/framework disassembly、既有 findings/work corpus；未接觸裝置，未執行 adb/service call，未猜 Binder code，未修改既有檔案。CSV companion：[luna_worker_phase6y_permission_20260810.csv](./luna_worker_phase6y_permission_20260810.csv)。

主要 evidence：`artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt`，SHA-256 `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`。CSV 同時保存每列的證據路徑、雜湊與狀態。
