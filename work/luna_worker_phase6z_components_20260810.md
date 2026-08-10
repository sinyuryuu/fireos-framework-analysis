# Phase 6Z — PS7331 exported OOBE/ProductPolicy/Settings residual

日期：2026-08-10（Asia/Taipei）

本輪只做 host-only 靜態搜尋與既有 evidence 去重：PS7331 OOBE JADX、framework disassembly、system/fireos/etc init/permissions/sysconfig/product-policy 清單及既有 Phase 6 reports。未接觸裝置、未發送 broadcast、未啟動 exported component、未改 Settings/package/user、未執行 OTA/recovery/reboot。

## 結論

CSV 盤點 8 條 bounded surfaces：

- `BootAfterSystemOTAReceiver` → `PackageHelper` / `OOBEActivationHelper` 是 protected OTA/OOBE lifecycle writer。component state 與 Secure/Global setup state 的 sink 已確認，但 receiver Context 的 numeric user 仍 UNKNOWN；不能推成 User 0，也不是已證明 Fire Launcher HOME setter。
- DCPMS 的四個 exported receivers (`PCAActiveProfileReceiver`, `DeviceUserSwitchReceiver`, `AccountPropertyChangeReceiver`, `GlobalContentSyncEventReceiver`) 會寫入或同步 CDE policy/profile state。前兩者分別受 action/protected-broadcast 邊界約束；後兩者的 custom permission holder/protection 或 producer route 未由 bounded corpus 閉合。這些 sink 不是 SettingsProvider、PMS HOME/package-state 或 OTA apply/recovery。
- `productpolicyservice_fosinit.xml` 只證明 system-server/in-process registration；沒有從該 init registration 推導 exported component、Binder caller gate 或 HOME/package/Settings/OTA sink。
- Settings/HOME 只保留既有 `default_home`、`config_show_default_home=true` 與 per-user PMS preferred-activities topology。沒有新增 shell-writable Settings/DeviceConfig key；`set-home-activity` 是已知 writer boundary，去重不重列為新 component。

## Caller → gate → user → sink 判定

每列的 `caller`、`gate`、`identity_scope`、`sink` 均以保存檔案為限。`UNKNOWN` 是 evidence 尚未閉合，不代表可達或漏洞。尤其：

1. `BOOT_AFTER_SYSTEM_OTA` 的 sender 是 `AmazonPackageManagerService.onBootPhase(550)` 且要求 `PMS.isUpgrade()`；framework `ContextImpl.sendBroadcast` 將 sender Context user 傳給 AMS，receiver/helper 再沿 Context user 使用 PMS/ContentResolver。source 沒有 `UserHandle.SYSTEM/0` 或 `UserInfo.id`，故 numeric User 仍 UNKNOWN。
2. OOBE source 沒有 `setHomeActivity`、`addPreferredActivity`、`replacePreferredActivity` 或 `com.amazon.firelauncher` reference；component enable 不等於 preferred HOME。
3. DCPMS exported 屬性不等於 ordinary caller accepted：`USER_SWITCHED` 是 protected action；custom permission 的 declaration/holder 與跨 user 接受度需分別驗證，不能以 manifest requested permissions 代替 caller provenance。
4. ProductPolicy fosinit 是 system-server loader evidence，不是 app manifest。沒有把 service registration 擴大成 external Binder route。

## 去重與 residual status

已去重既有 ProductPolicy readonly、BootAfterSystemOTA/OOBE user-scope、Phase 6SV exported-surface、Phase 6PZ Settings/Home resource、OTA controller/Vending/SystemUI/ordinary HOME findings。故 CSV 的 6Z-001/002 與既有 OOBE writer 僅保留 caller→gate→user→sink 的 residual user-scope；6Z-008 明確標為 existing boundary，不宣稱新發現。

## Evidence anchors

- OOBE receiver SHA-256 `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90`；activation helper `6ebcb7eef7a03459a76b9c21cd59b61a30947f2b00a5624a4646825b8e3223d2`；PackageHelper `900f2dd69d349b3b4718b7f988b7d5bd153af2e2cb3c1586600e5b048e760ad8`。
- DCPMS manifest tree SHA-256 `9e3446c250d89a274ddf9438742d04e04950c9ce7d5b1b48beb318449b120fd4`；helper/service hashes are recorded per row in the CSV.
- ProductPolicy init listing evidence is `artifacts/phase6bg-product-policy-readonly-20260805-01/`; its stderr file is empty (SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`), so it is only a bounded negative/registration inventory, not proof of implementation.

完整欄位 ledger 見 [`luna_worker_phase6z_components_20260810.csv`](./luna_worker_phase6z_components_20260810.csv)。

## Safety / validation

- device contacted: false
- broadcast/Binder/service/component dispatched: false
- Settings/package/user mutation: false
- OTA/recovery/reboot/partition write: false

