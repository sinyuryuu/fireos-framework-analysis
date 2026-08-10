# IPC boundary follow-up — 2026-08-10

本輪是 host-only 靜態搜尋與既有 artifact 整理。未接觸裝置，未執行 service call、未知 Binder transaction、root、exploit、payload 或任何 package/user/policy mutation。公開基準：`a86d01361`。

## 結論

在目前解包、反編譯、disassembly、findings、Phase6 tables 與既有保存結果中，沒有新增「普通 caller → Amazon 私有 Binder → clear identity/高權限 downstream → PackageManager/HOME/權限最終影響」的路徑。可保留的邊界如下：

- `IAmazonActivityManager` prewarm 是已確認的 process/resource confused-deputy effect，但沒有 HOME、preferred、package-state 或 permission-writer edge。
- `IAmazonUserManager` setup-state writer 可被既有普通 caller 結果觸達，且跨 User 10 的設定效果已保存；這是 settings sink，不是 PackageManager/HOME sink。
- KFT `enableKftLauncher(UserInfo)` 是唯一明確連到 Tahoe、Fire Launcher、Launcher3 component/application state 的 Amazon writer；其 scope 由 `UserInfo.id` 決定，保存的普通 caller 結果在 PMS caller/protected-component gate 被拒，故不構成已證明的 User-0 HOME 路徑。
- Amazon PackageManager flags/metadata mutators 有 `ADD_RM_PKG_METADATA` caller gate，且 bounded corpus 沒有到 HOME、preferred 或 generic package-state setter 的 downstream edge。
- H2、OTA/OOBE、DPM/preferred 都是 signature/lifecycle/admin-bound；普通 caller reachability 或 User-0 HOME relay 未建立。
- vending 的有限 preferred writer 僅對 `WEB_SEARCH`/`DEFAULT`，不等同 HOME/default launcher，也未形成 Amazon 私有 Binder relay。

## 去重規則

CSV 將 Phase6PV 的 IPC-01～IPC-08 依 semantic route 合併；同一 service、同一下游 sink、同一 caller gate 不重複列為新 finding。Phase6PV 既有 numeric transaction identifiers 不在本 follow-up 重述，也不提供任何 payload 或可利用呼叫方式。

## 掃描範圍與判讀

搜尋關鍵字包含 `onTransact`、`getCallingUid`、`clearCallingIdentity`、`hasCallerGotPermission`、`setApplicationEnabledSetting`、`setComponentEnabledSetting`、`setHomeActivity`、preferred-activity APIs、`createChildUser`。檢查對象為 `decompiled/`、`artifacts/`、`findings/`、`output/tables/`、`work/` 既有資料；命中只作為 static evidence，`holder metadata` 不視為 caller reachability，`clearCallingIdentity` 不視為對外授權。

## 交付物

詳細欄位（interface/service/package/UID/permission/caller gate/downstream effect/evidence/status/next safe verification）見 [CSV](luna_worker_ipc_boundary_followup_20260810.csv)。所有九條 bounded route 均標記 `closed`：其中數條是「已確認但非目標 sink」，其餘是「既有 gate 或缺乏普通 caller edge」而 closed；並非宣稱全映像不存在任何未保存 caller。

主要 reused evidence：`output/tables/phase6pv-broad-route-closure.csv`、`work/luna_worker_ipc_sink_inventory_followup_20260810.md/.csv`、`work/luna_worker_phase6_ipc_kft_audit_20260810.md`、`work/luna_worker_phase6_private_client_universe_20260810.md`、`artifacts/phase6mh-package-state-writers-20260810-01/writer-calls.csv`，以及各 row 所列的既有 disassembly/findings。

## 剩餘安全驗證

只允許 host-only：若日後新增解包類別或完整 superclass/interface slice，可重跑 caller/reference、permission、identity 與 downstream data-flow 搜尋；不執行 Binder dispatch、service call、broadcast injection、preferred setter、component/package setter 或任何裝置操作。
