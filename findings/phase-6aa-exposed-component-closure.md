# Phase 6AA：Exported component／低權限候選方法級閉合

## 範圍

Phase 6W 的 manifest inventory 將 6 個 row 標為
`EXPORTED_LOWER_OR_NONSTANDARD_PROTECTION`。本階段只對保存的 PS7331
manifest、JADX source、package dump 與候選 CSV 做 host-only closure，回答：

- `0x2` 是否其實是 Android 9 的 signature protection base；
- OOBE activity 是否存在普通 shell 可直接啟動的低權限入口；
- Fire Launcher 的 BadgingProvider 是否能把 caller 變成 system/HOME 控制者。

沒有啟動 activity、沒有 query/update ContentProvider、沒有送 broadcast、沒有
Binder transaction、沒有接觸設備，也沒有修改 package/settings。

## 結果摘要

Phase 6W 的 6 個 row 去除同一 manifest 的重複後為 5 個 unique component：

| 類別 | 數量 | 結果 |
|---|---:|---|
| `SIGNATURE_COMPONENT_GUARD` | 4 | OOBE activity 使用 package-defined `OOBE_PERMISSION`，manifest `protectionLevel=0x2` |
| `CUSTOM_CALLER_PACKAGE_GUARD` | 1 | BadgingProvider 只允許 caller UID 更新自己所屬 package 的 badge |

產物：

`artifacts/phase6aa/exposed-component-closure-20260805-01/`

## 已證實

### OOBE activities

`artifacts/phase6j/ota-oobe-manifest-audit-20260805-01/manifest.txt:144-146`
定義：

```text
com.amazon.kindle.otter.oobe.OOBE_PERMISSION
android:protectionLevel="0x2"
```

同一 permission 用於：

- `OOBELauncherV2`：manifest `:475-477`
- `SettingsLanguagePickerActivity`：`:599-602`
- `SettingsTimezoneActivity`：`:656-659`
- `ATSWiFiActivity`：`:926-930`

因此這 4 個「implicit exported」候選不是沒有授權的 activity；它們的
component-level permission 是 signature base。`OOBELauncherV2.onCreate()` 在
`:67-71` 會 enable `OobeHomeActivity`、啟用 OOBE flow 並啟動 OOBE Home，這是
高影響 setup-state side effect，不是普通 HOME default API。

### Fire Launcher BadgingProvider

Fire Launcher manifest `decompiled/jadx/firelauncher/resources/AndroidManifest.xml:13-17`
將 `com.amazon.firelauncher.permission.BADGING` 定義為 `normal`，並在
`:508-511` 將它作為 provider 的 write permission。

但 provider 的實際 update path 還有額外檢查：

```text
BadgingProvider.update():58-64
  → unsafeUpdate():67-92
  → badgeUpdateAllowed(pkgName, Binder.getCallingUid()):78
  → PackageManager.getPackagesForUid(uid):101-109
  → packagesForUid 必須包含目標 pkgName
```

所以一個 caller 若要更新 `com.amazon.firelauncher` 的 badge，還必須是該
package 所屬 UID。這個 provider 的影響範圍是 badge state；沒有觀察到 HOME
resolver、package enabled-state、system settings、system-server Binder 或 root
效果。

## 判定

### 高可信推論

- Phase 6W 的「低／非標準 protection」分類有部分是 parser 沒有把數值
  `0x2` 正規化成 signature 的 triage artifact；不能把這 4 個 OOBE activity
  當作 shell 可達入口。
- BadgingProvider 是一個可被其他 app 以正常 permission 觸碰的 badge surface，
  但 `getPackagesForUid()`／target-package equality 將它限制在 caller 自己的
  package。它不提供跨 package 的 Fire Launcher 控制能力。

### 已排除目前證據支持

- OOBE activity 候選可直接作為普通 shell 的 HOME replacement。
- OOBE activity 候選可直接把 setup-state 變更轉成 root 或 SELinux bypass。
- BadgingProvider 可透過 caller package 欄位讓 shell 更新 Fire Launcher 或取得
  system UID。
- 這 5 個 unique rows 提供了新的 Amazon Framework IPC／HOME 控制面。

### 待驗證

- 若要取得 runtime denial log，需實際啟動 OOBE activity 或更新 provider；前者
  會觸發 OOBE side effect，後者只驗證非關鍵 badge mutation，兩者都不會改善
  HOME/root 研究結果，因此目前不執行。
- 完整 PackageManager/ActivityManager 在同版本 device 上對自訂 permission
  的 runtime enforcement 細節，已由 manifest protection 與現有 Android policy
  邊界強力支持，但尚未以針對 OOBE 的人工啟動測試重現。

## 研究結論

這一輪把 Phase 6W 的主要低權限候選縮小為「4 個 signature-protected OOBE
activity + 1 個 badge-only provider」。沒有發現可合法由 shell 直接到達、又能
改變正式 HOME 或提升到 system/root 的新入口。下一個高價值方向仍是：

1. host-only 比對完整 matching framework/product protected-broadcast provenance；
2. 對 Amazon private Binder 只做已知 interface 的 source-level permission／
   caller closure；
3. 若未來自然完成官方 OTA，事後唯讀記錄 OOBE component、resolver、task 與
   setup settings 時序。

任何需要人工 broadcast、啟用 OOBE、未知 Binder transaction、OTA/recovery 或
   partition write 的驗證，維持風險拒絕。

