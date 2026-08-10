# 支線 B：Amazon Framework/System Services IPC 廣域靜態搜尋

日期：2026-08-10。輸入限於工作區既有 `decompiled/`、`artifacts/`、`firmware/` 落盤資料；沒有重跑 runtime，沒有發 service call、transaction、broadcast、payload，也沒有做任何裝置或 package state 變更。工作區沒有 `artifacts/decompiled/`，因此沿用實際存在的 `decompiled/` 與既有 artifacts 路徑。

## 結論

最接近 package/component state 的 Amazon Binder surface 是 `AmazonUserManagerService.BinderService.enableKftLauncher` → `enableKftLauncherComponent`，其靜態 sink 會以 supplied `UserInfo.id` 觸及 Tahoe/Fire Launcher/Launcher3 enabled state；證據同時顯示它是 child/profile/KFT lifecycle 路徑，且明確會 disable Fire Launcher，不是普通 HOME preferred-activity setter，故不可視為 workaround。

`AmazonProfileService` 的 `initiateLauncher` 只看到 `PROFILE_INTERACTION` gate 與 acknowledgement；`startProfilePicker` 只看到以 current user 啟動設定好的 picker，沒有 bounded `setHomeActivity`、`addPreferredActivity` 或 `replacePreferredActivity` sink。Amazon input Binder 會管理 key interceptor/filter/locking，但 bounded source 沒有 HOME resolver write。

PMS 是最後的 package/component enabled-state sink：既有 method map 明確標出 `checkCallingOrSelfPermission`、`getCallingUid`、`getCallingPid`、`clearCallingIdentity`、`restoreCallingIdentity` 與 `setEnabledSetting`；Amazon callers 包括 KFT、OOBE、ProductPolicy。這些是 sink/authorization review points，不代表任何 caller 已被證明可達。

OTA/OOBE surface 包含 `IOTAControlService.Stub/Proxy`、`OTAControllerImpl`、`BootAfterSystemOTAReceiver`、`SettingsDBUtils` 與 OOBE component helper。既有 evidence 顯示 OTA controller 有 `com.amazon.dcp.ota.permission.CONTROLLER`，OOBE receiver 受 OTA lifecycle/protected broadcast 條件約束；OOBE helper 可寫 Secure/Global settings、啟用 OobeHomeActivity。這些均只作靜態/既有 runtime evidence 引用。

## 欄位說明

CSV 的固定欄位依要求為：`id,service_or_class,entrypoint,caller_or_client,permission_or_gate,binder_identity,user_scope,sink_or_effect,observed_runtime,evidence,confidence,missing_edge,next_safe_step`。

- `permission_or_gate`：只記錄 source 或既有 artifact 明示的 permission/gate；缺失時不推測。
- `binder_identity`：區分 calling identity、server identity、`clearCallingIdentity`/restore、或未知；不把 system_server 內部路徑誤當成外部 caller 可達。
- `user_scope`：只在證據明示 `UserInfo.id`、current user、child/profile、或 provider per-user semantics 時記錄；其餘標為未證明。
- `observed_runtime`：只引用既有 capture，例如 saved service list/SELinux denial；本輪沒有重新執行。

## 主要風險與 reachability

1. `amazonusermanagerservice`、`amazonprofileservice`、`amazonactivitymanager` 與 Amazon input service 的既有 capture 顯示 shell UID 2000 的 service-manager find boundary；因此 Stub/Proxy 存在不等於 shell 可取得 handle。
2. `IAmazonUserManager.Stub.onTransact` 的 interface token/dispatch 不能取代 server method authorization；`enableKftLauncher` 的完整 caller gate 仍是 missing edge。
3. `clearCallingIdentity` 在 KFT DPM 路徑及 Amazon Activity prewarm path 會改變後續 privileged operation 的 identity interpretation；不能從 static call 單獨推出可利用性。
4. `SettingsDBUtils` 與 `SettingsProvider` 只證明 settings sink 存在；provider caller/user enforcement、具體 Amazon caller 與可達 Binder edge 尚未完整 join。
5. `BootAfterSystemOTAReceiver` 是 lifecycle sink，不是可任意 replay 的 broadcast route；既有 evidence 已將其列為 protected OTA/OOBE 條件，沒有在本輪重送。

## HOME 特定負結果

在已審核的 Amazon User/Profile/Input bounded blocks 及既有 caller closure 中，沒有找到已證明的 Amazon Binder 方法直接呼叫 `setHomeActivity`、`addPreferredActivity` 或 `replacePreferredActivity`。找到的是 profile picker launch、KFT child-user launcher state、input callback/filter 與 PMS enabled-state sinks。這是 bounded static negative result，不外推到未反編譯或 missing helper/class。

## 證據索引

- `artifacts/phase6av/ipc-method-closure-20260805-05/ipc-method-closure.csv`
- `artifacts/phase6ak/launcher-user-service-20260805-02/launcher-user-service.csv`
- `artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv`
- `artifacts/phase6kv/pms-home-caller-closure-20260810-01/pms-home-callers.csv`
- `artifacts/phase6bk/ipc-ota-closure-20260810-01/method-map.csv`
- `artifacts/phase6bk/ipc-ota-closure-20260810-02/references.csv`
- `artifacts/phase6r/ota-ipc-static-audit-20260805-01/ota-ipc-method-matrix.csv`
- `artifacts/phase6m/oobe-ota-control-surface-20260805-02/ota-contract-transactions.csv`
- `artifacts/phase6n/oobe-ipc-ota-audit-20260804-191216/oobe-helper-state.csv`
- `artifacts/phase6aq/service-context-audit-20260805-03/service-context-matrix.csv`
- `artifacts/phase6aj/input-home-boundary-20260805-03/input-home-boundary.csv`
- `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/042_SettingsProvider.xmltree.txt`
- `device/baseline/BASELINE-20260803-05/settings_secure.txt`

## QA

CSV 共 19 筆資料列，header 與要求固定欄位完全一致。已做 parser-level malformed 檢查：每列欄數一致、引號可解析、無未閉合 quote；`id` 無重複，且以完整 row tuple 檢查無 duplicate。CSV 內 intentional comma-containing fields 均以 RFC 4180 quote 形式保存。

QA 結果：malformed=0；duplicate id=0；duplicate row=0。尚未發現需要修正的格式問題。
