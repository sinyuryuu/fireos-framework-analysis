# Phase 9C — residual IPC static closure (DCPMS)

日期：2026-08-10（Asia/Taipei）

## 範圍與安全界線

本輪只讀取既有 Phase 7B、8B、8C ledger、DCPMS exact-build JADX、AIDL、manifest/xmltree 與 permission artifact。沒有執行裝置命令、Binder/service transaction、APK 操作、settings/package mutation、broadcast、driver/root/exploit 或任何裝置接觸；沒有修改既有檔案。本輪只新增本報告及 CSV。

## 選擇的 residual 與結論

從 Phase 7B 的 `P7B-015 DCPMS local/AIDL boundary` 以及 Phase 8B/8C 的 caller-closure 缺口中，選取 DCPMS exported AIDL 作為最高價值、且未被既有 DCPMS consumer / ProductPolicy / SettingsProvider sink closure 重複的路徑。

靜態可閉合部分如下：

- `DCPMSService` 對 manifest service `com.amazon.dcpms.fos.service.DCPMSService` 實作 `onBind()`，回傳 `ServiceBinder.getBinderInstance()` 建立的 AIDL Stub。
- manifest 宣告 `exported=true`、`singleUser=true`，service permission 為 `com.amazon.dcpms.permission.GET_DEVICE_CDE_DECISION`。現有 permission artifact 未提供可接受 caller 的 package/UID 對應，因此「有 permission 名稱」不等於已找到 caller。
- `IDeviceChildExperienceModeDecisionManager` 只有 transaction 1–3；Stub 每條路徑只 `enforceInterface`，沒有 `getCallingUid`、`checkCallingPermission`、`UserHandle` 或 user argument。`DCPMSService.onBind`/`ServiceBinder` 也沒有 clear/restore identity。
- tx1 sink 是讀取/清除 DCPMS CDE decision 的 device-protected persistence；tx2/tx3 sink 是 process-local callback map 與 `IDCPMSServiceCallback.handleDecisionChange`。沒有接到 SettingsProvider、PMS、preferred activity、package state、user/profile mutation 或 device-policy setter。

## Bounded UNKNOWN

在完整的 recovered APK/source corpus 中，沒有找到任何 DCPMS client 的 `bindService`、service-manager lookup、AIDL `asInterface` 呼叫、callback implementation 或 caller package/UID。故不能建立 exact external caller → service-manager → bind → permission grant → Binder identity 的 closure；也不能從 exported/singleUser 或 permission holder inventory 推導普通 caller 可達。

對 tx1，結果是 `UNKNOWN_BOUNDED`：若存在合法 client，讀取結果的 user scope 仍是 singleUser/device-global API，沒有 caller-selected user argument；但 client identity、permission grant 與 service-manager/SELinux accepted edge 缺失。

對 tx2/tx3，結果同樣是 `UNKNOWN_BOUNDED`：回調註冊接受 non-null Binder 與非空字串，未見 callback ownership 或 caller UID binding；然而沒有 recovered client，且 downstream 僅是決策通知，不能升格為 settings/package/user/device-policy 影響。

## 與既有 ledger 的去重界線

本輪不重做 DCPMS receivers → CDE evaluator 的已閉合路徑，不重做 ProductPolicy local-service/package setter，也不重做 SettingsProvider 的 provider writer/HOME sink boundary。新增內容只針對 Phase 7B/8B 明確保留的 DCPMS external caller、service-manager bind、permission grant、Binder identity 與 callback client 缺口。

## 證據與限制

主要 artifact hashes：manifest xmltree `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`；DCPMSService `eeb1591145fafc1f5d84e4e801fa5648bd2cfae54b99b1437aad75ff396f5602`；ServiceBinder `8329e98d58a91b34331d147eac86551b384126af0ec539a7841f8cdf716b520d`；AIDL Stub/Proxy `1d02fba9cea813e9d20b1fbd6a515eeb152ff453e36c0ade56825aa685210c73`；callback AIDL `0b705c458b7dcc34deb7b39c10470b5f4d020f04d254209058fac35de3ca6fa4`。

逐列 caller / gate / Binder identity / user scope / sink / effect / status / missing edge 見 [CSV](./luna_worker_phase9c_residual_ipc_20260810.csv)。下一個必要證據是離線取得的完整 production client APK/source 與 service-manager/SELinux policy mapping；本輪不以 runtime probing 補洞。
