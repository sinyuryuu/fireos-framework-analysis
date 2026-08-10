# Phase 6AA — host-only IPC residual audit

日期：2026-08-10（Asia/Taipei）

## 範圍與安全界線

本輪只讀取工作區既有 PS7331 `decompiled/jadx`、`decompiled/baksmali`、manifest/XML-tree、AIDL/Stub、fosinit、既有 Phase 6X/6Y/6Z tables 與 reports。沒有執行 adb、service call、Binder transaction、broadcast、driver/ioctl、OTA/recovery、reboot、root 或 exploit，也沒有建立 exploit 或猜測 transaction。

## 結論

沒有找到一條新的、證據完整的「低保護/無保護 caller → accepted gate → identity/user scope → package/user/Settings/HOME/OTA/privilege sink」鏈。

本次補查的重點是把 exported surface、Binder method gate、permission protection-level 證據與既有 Phase 6X/6Z 覆蓋範圍重新 join：

- `FireOsDisplayPowerController`、`AlexaModeSwitchManager`、camera-cover callback 已在 Phase 6X/6WL 整合；它們是 Settings sink 的正靜態證據，但不是本輪新證據。
- `com.amazon.settings.OOBECompleteReceiver` 是 exported receiver，component permission 為 `com.amazon.kindle.otter.oobe.OOBE_PERMISSION`，其 protection level/holder 仍 UNKNOWN；manifest 只足以證明暴露面，不足以證明低權限 sender 或 Settings/HOME effect。
- DCPMS `AccountPropertyChangeReceiver`、Amazon PM proxy receiver、H2 service、Vending/DSE 與 OTA/OOBE lifecycle 均有既有 Phase 6Z/6RG/6TF/6QB 證據；本輪確認其 caller/holder/user scope 缺口，沒有新 sink join。
- 對 Settings APK 的 exported component inventory，`EXPORTED_TRUE` 或 component permission 缺失本身不是 sink 或 bypass 證據；對 `OOBECompleteReceiver` 的 permission protection 未在保存的 permission-definition corpus 中閉合，標為 UNKNOWN。

## Row-level disposition

CSV：[`luna_worker_phase6aa_ipc_residual_20260810.csv`](luna_worker_phase6aa_ipc_residual_20260810.csv)。

| ID | 靜態鏈與結果 |
|---|---|
| 6AA-001 | `FireOsDisplayPowerController` dump → `Settings.System.putInt(screen_brightness)`；`DUMP` gate 正證據，低權限/UID/SELinux UNKNOWN；重複 6WG/6WL，非新發現。 |
| 6AA-002 | `AlexaModeSwitchManager` Binder → `checkCallingOrSelfPermission(MODE_SWITCH)` → `putIntForUser(USER_CURRENT)`；正 Settings/user-scope 證據，permission protection/holder、service-manager/SELinux UNKNOWN；重複 6WG/6WL。 |
| 6AA-003 | Input monitor callback → `Settings.Secure.putInt(camera_shutter_state)`；callback publication、external caller、permission、user scope UNKNOWN；重複 6WG/6WL，不能外推 Binder caller。 |
| 6AA-004 | exported `com.amazon.settings.OOBECompleteReceiver` → source/receiver path；component permission 與 action 正證據，但 permission level/holder、sender UID、downstream Settings/HOME write UNKNOWN；和 Phase 6Z OOBE receiver family 重疊，未形成新鏈。 |
| 6AA-005 | DCPMS `AccountPropertyChangeReceiver` → CDE/profile persistence/evaluator；custom permission protection/holder、user scope UNKNOWN；無 HOME/PMS package-state/OTA sink，重複 6Z-005/6SV-003。 |
| 6AA-006 | Amazon PM `registerProxyReceiver`/`deregisterProxyReceiver` → PendingIntent ownership / receiver map；method-local permission absent，但 creator UID/system-app checks與 tx7 calling UID cleanup gate存在；first package/HOME/Settings sink NOT_FOUND，重複 6RG/6QB。 |
| 6AA-007 | H2 exported service → signature `BIND_SERVICE` → user workflow；user-management/settings relay sinks 正靜態證據，但 external caller/holder grant 未閉合，且無 HOME/package-state sink；重複 6TF。 |
| 6AA-008 | Vending `DseService` → secure-settings-class writer；caller/package/account/user binding 與 exact key UNKNOWN；非 HOME/Fire sink，重複 6QB，不能升級為 privilege route。 |

## 正／負證據規則

- **正證據：** manifest exported/component permission、AIDL/Stub publication、明確 `checkCallingPermission`/`checkCallingOrSelfPermission`/`getCallingUid`、`clearCallingIdentity`、明確 Settings/package/user/native OTA sink。
- **負證據：** 在 bounded method/source slices 未找到 Fire HOME selector、preferred activity、`setComponentEnabledSetting`、`setApplicationEnabledSetting` 或 OTA apply/write edge；這不是全 corpus 的形式化不存在證明。
- **UNKNOWN：** permission protection-level/holder、service-manager/SELinux gate、production caller、sender UID、user mapping、indirect consumer 或 omitted helper 未由保存 corpus 閉合。
- `clearCallingIdentity` 只記為 identity transition；不能取代其前置 caller authorization，也不能單獨證明 confused deputy。

## 既有證據重複與範圍限制

明確重複：`work/luna_worker_phase6wg_ipc_residual_20260810.csv`、`output/tables/phase6x-control-surface.csv`（WG-001/WG-003）、`output/tables/phase6wl-control-surface.csv`、`work/luna_worker_phase6sv_exported_surface_20260810.csv`（6SV-003）、`work/luna_worker_amazonpm_caller_inventory_20260810.csv`、`work/luna_worker_phase6tf_ipc_residual_20260810.md`、`output/tables/phase6qb-residual-inventory.csv`。

本報告不把 exported component、permission declaration、generic Settings writer、private service publication 或不明 transaction number 當成可達性或漏洞；也不補做任何 live trigger。下一步若要縮小 UNKNOWN，只能繼續補 matching exact-build manifest/permission holder、generated Stub caller、Context/user propagation 與 indirect consumer 的 host-only provenance。

## 安全結果

本輪只讀分析，未改動既有檔案；除本報告及 companion CSV 外沒有新增或修改檔案。結論是：**0 條新的證據完整低權限 IPC→目標 privilege sink 鏈；8 條 residual rows，其中 7 條既有路徑重複/邊界補強，1 條 OOBE Settings exported receiver 仍為 permission/user/sink UNKNOWN。**
