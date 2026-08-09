# Phase 6NH：HOME resolver callback 完整性稽核

日期：2026-08-10

## 範圍與安全界線

本階段只讀取已保存的 PS7331 `fosinit` XML 與 services/fosservices VDEX
反組譯結果。沒有執行 `adb`、Binder、`service call`、OTA/updater、ioctl、
root 或任何裝置狀態變更。

可重現腳本：

[`audit_phase6nh_home_callback_completeness.py`](../tools/scripts/audit_phase6nh_home_callback_completeness.py)

產物：

[`phase6nh-home-callback-completeness-20260810-02`](../artifacts/phase6nh-home-callback-completeness-20260810-02/)

## 結果

在已保存的 12 個 `*fosinit*.xml` 中，只有 2 筆註冊使用：

`com.android.server.am.VendorActivityStackSupervisorCallback`。

| Evidence ID | 註冊 | VDEX 結果 | HOME resolver 影響 | 信心 |
|---|---|---|---|---|
| 6NH-CB-001 | `appcompatsupport_fosinit.xml` → `AppCompatActivityStackSupervisorCallback` | 有具體 `resolveIntent`；呼叫 `IPackageManager.resolveIntent`，再套用 `isUninstalledApp` filter；例外路徑回傳 null | 不指定 Fire Launcher；非 null 時才短路，否則回標準 resolver | Confirmed |
| 6NH-CB-002 | `eve_launch_time_fosinit.xml` → `EveActivityStackSupervisorCallback` | class 存在，但沒有具體 `resolveIntent` override；沿用 base null path | 不指定 Fire Launcher | Confirmed |
| 6NH-CB-003 | 其餘 10 個 fosinit XML | 沒有匹配的 supervisor resolver callback 註冊 | 在此 artifact set 中沒有新增 callback selector | Strong evidence |

## 具體程式位置

- `decompiled/baksmali/vdexExtractor/services/disassembly.log:222444-222458`
  — `VendorActivityStackSupervisorCallback.callResolveIntent()` 依序呼叫
  callback，第一個非 null 結果才返回；全部為 null 時返回 null。
- `decompiled/baksmali/vdexExtractor/services/disassembly.log:796458-796504`
  — `ActivityStackSupervisor.resolveIntent()` 先呼叫 callback；callback
  結果為 null 時才呼叫 `PackageManagerInternal.resolveIntent()`。
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:41123-41144`
  — AppCompat resolver 直接呼叫 `IPackageManager.resolveIntent()`，再檢查
  `isUninstalledApp`。
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:204452-204476`
  — Eve callback class；未發現具體 `resolveIntent` override。

## 判定

### 已證實

1. 已保存設定中的 supervisor callback 註冊數為 2。
2. AppCompat callback 不包含 `com.amazon.firelauncher` 硬編碼，也沒有將
   Fire component 作為固定回傳值。
3. Eve callback 不提供具體 resolver 覆寫。
4. callback chain 全部回 null 時，Fire OS 會回到標準
   `PackageManagerInternal.resolveIntent()` 路徑。

### 高可信推論

在目前保存的 PS7331 framework artifact 範圍內，這個 callback 邊界不是
User 0 HOME 最終選中 Fire Launcher 的直接原因；已知 priority 50 與
AOSP-shaped PackageManager resolution 仍是較符合證據的解釋。

### 待驗證

仍無法僅靠本稽核證明：

- 裝置上是否存在未被保存的額外 `fosinit` 載入來源；
- native callback 或 runtime injection 是否存在於未取得的 artifact；
- 所有 build-time / runtime class-loader 載入內容是否完全等於本地保存集合。

這些未知不能被寫成「Fire OS 絕對沒有其他 callback」。

### 因風險拒絕測試

未知 Binder transaction、私有 service replay、OTA/updater 執行、driver
ioctl/DMA/race、停用或隱藏 Fire Launcher、root、分割區寫入均未執行。

## 最小結論

本階段沒有發現新的 User 0 HOME writer 或可由 shell 直接使用的 resolver
override。若繼續研究，下一個合理的主機端問題是確認 runtime `fosinit`
載入清單的來源完整性；不應再重做已完成的 priority、`set-home-activity`
或普通 package-state 測試。
