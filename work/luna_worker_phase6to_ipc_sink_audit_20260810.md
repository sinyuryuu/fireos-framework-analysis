# Phase 6TO exact-build Amazon Framework/System Services IPC sink audit

日期：2026-08-10。此回合只使用主機端既有 decompiled/artifacts/phase6*、Phase 6TJ–TM 報告與 exact-build APK/manifest 證據；未接觸裝置，未執行 adb、Binder/service call、driver、root、exploit，也未構造 payload。完整列在 [CSV](luna_worker_phase6to_ipc_sink_audit_20260810.csv)。

## 結論

在 bounded exact-build corpus 中，未找到「其他 Amazon exported service/receiver/provider → 未證明的低權限 caller → PackageManager/HOME state sink」的 CONFIRMED 漏洞鏈。已確認的 Amazon writer 是固定 OOBE/Gemini/ProductPolicy 路徑，或 AmazonUserManager 的 child/KFT `UserInfo.id` 路徑；後者不是 User-0 HOME writer。AmazonPackageManager 的 IPC metadata writer 有 `amazon.permission.ADD_RM_PKG_METADATA` 檢查，但 sink 是 Amazon metadata/flags，不是 component-enabled 或 preferred HOME。AmazonActivityManager、AmazonDevicePolicyManager、AmazonWindowManager 的 bounded IPC slice 分別呈現明確 permission/helper、callback 或 unresolved caller gate；沒有 HOME/package-state sink。

Exported 或 signature permission 沒有被單獨視為漏洞。`com.amazon.firelauncher` exact-build APK 的 manifest inventory（SHA-256 `601c510d…`）包含多個 exported provider/receiver/service，但本次 bounded component inventory 未連到列出的 setter 或 preferred-HOME sink，因此標為 NOT_A_SINK。

## Caller → permission → identity/user → sink 判定

每列都含 source path、SHA-256、class/method、line 或 smali offset、分類與下一個安全步驟。分類只使用 `CONFIRMED`、`STRONG_STATIC`、`UNKNOWN`、`NOT_A_SINK`：

- `CONFIRMED`：靜態確認了 IPC/內部 entry、permission/helper gate 與 downstream effect；不代表可由普通 app 到達，也不代表漏洞。
- `STRONG_STATIC`：caller 或 permission/identity/user 的一段仍在 bounded slice 外，或 permission check 的消費需要完整方法確認；保留靜態強證據但不升級。
- `UNKNOWN`：存在 IPC/可能 sink，但 caller、permission 或 identity/user 連接未閉合。
- `NOT_A_SINK`：可見的是 callback、observer、metadata、固定 lifecycle、manifest exposure 或非 HOME/package-state effect。

`onTransact`/transaction：Phase 6MT 提供各 Amazon interface 的 proxy line 與 transaction code；本 audit 將其視為 IPC entry evidence，並以 fosservices implementation method 的 line/offset 連到 permission 與 effect。未在 bounded implementation slice 觀察到 `hasCallerGotPermission`；`Binder.getCallingUid` 只在既有 Phase 6TM/相關 caller-provenance 證據明確出現時記錄。未觀察到 `clearCallingIdentity` 的地方不補推 identity；出現 `clearCallingIdentity/restoreCallingIdentity` 也不把它當成 caller authorization。

## H2 exclusion

Phase 6TJ–TM 已處理 H2ClientService 的 exported/signature BIND_SERVICE、holder/grant/client UNKNOWN 與 profile/order chain。本檔排除 H2，避免重複 H2 已確認部分；TO-09 僅保留 AmazonUserManager 的 child/KFT setter 作為其他 Amazon service 的 scope 對照，不將它重標成 User-0/HOME。

## Exact-build inputs and limits

主要 evidence 是 exact-build `fosservices` disassembly（SHA-256 `ecbe62fe…`）、`services` disassembly（`373a5115…`）、boot-fosframework disassembly（`fc101d79…`）、Phase 6MT Amazon IPC candidate table（`0d630a29…`）、Phase 6JD fosinit extraction manifest（`0797a670…`）與 Phase 6H manifest component inventory（`4696984f…`）。已存在的 Amazon APK 也只用於 manifest/inventory provenance；未對 APK 執行裝置操作。這些材料不能證明未保留 caller source、完整 manifest permission owner/grant、跨 user gate 或 runtime reachability。

## 下一個安全步驟

只做主機端：補齊同一 exact-build 的 Amazon service manifest/permission-owner/signature-grant 與完整 `onTransact → implementation` source slice，優先 TO-01、TO-07、TO-08；重新計算每個輸入 SHA-256，並把 caller UID、permission check result consumption、`UserHandle`/cross-user gate 與 sink 呼叫放在同一列。若仍缺任一段，維持 UNKNOWN。不要呼叫 service、不要 replay transaction、不要發 broadcast、不要修改 package/component/HOME 狀態。
