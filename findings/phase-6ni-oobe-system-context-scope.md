# Phase 6NI：OOBE sender 的 system-context user-scope closure

日期：2026-08-10

## 範圍

本階段只讀取保存的 PS7331 services/fosservices/boot-framework VDEX 與
`fosinit`。沒有執行 ADB、Binder、OTA、updater、recovery、ioctl、root 或
任何裝置狀態變更。

可重現腳本：

[`audit_phase6ni_system_context_oobe_scope.py`](../tools/scripts/audit_phase6ni_system_context_oobe_scope.py)

產物：

[`phase6ni-system-context-oobe-scope-20260810-01`](../artifacts/phase6ni-system-context-oobe-scope-20260810-01/)

## 靜態呼叫鏈

```text
SystemServer.createSystemContext()
  -> ActivityThread.systemMain()
  -> ActivityThread.getSystemContext()
  -> ContextImpl.createSystemContext()
  -> ContextImpl constructor with null UserHandle
  -> Process.myUserHandle()
  -> AmazonPackageManagerService.mContext
  -> onBootPhase(550) + PackageManagerService.isUpgrade()
  -> mContext.sendBroadcast(BOOT_AFTER_SYSTEM_OTA, permission)
  -> ContextImpl.getUserId() -> ActivityManager broadcast user argument
```

## 證據

| Evidence ID | 位置 | 觀察 | 信心 |
|---|---|---|---|
| 6NI-OOBE-001 | `services/disassembly.log:107206-107220` | `SystemServer.createSystemContext()` 使用 `ActivityThread.systemMain()` 與 `getSystemContext()` | Confirmed |
| 6NI-OOBE-002 | `boot-framework-disassembly.log:449576-449604` | `ContextImpl.createSystemContext()` 建立 system context，UserHandle 參數為 null | Confirmed |
| 6NI-OOBE-003 | `boot-framework-disassembly.log:449212-449262` | null UserHandle 由 constructor 以 `Process.myUserHandle()` 填入 `mUser` | Confirmed |
| 6NI-OOBE-004 | `boot-framework-disassembly.log:1182027-1182037` | `Process.myUserHandle()` 由 `Process.myUid()` 經 `UserHandle.getUserId()` 建立 | Confirmed |
| 6NI-OOBE-005 | `fosservices/disassembly.log:96045-96061` | AmazonPackageManagerService 保存傳入 system-server context 為 `mContext` | Confirmed |
| 6NI-OOBE-006 | `fosservices/disassembly.log:96087-96126` | phase 550、`isUpgrade()` 後以 permission-protected `sendBroadcast` 發送 OTA intent | Confirmed |
| 6NI-OOBE-007 | `boot-framework-disassembly.log:452691-452721` | framework broadcast 路徑使用 Context-derived user argument | Confirmed |

輸入 hash 已保存在產物的 `manifest.json` 與 `sha256sums.txt`；腳本執行結果
為 12/12 checks present，且標記 `device_contacted=false`、
`binder_called=false`、`updater_executed=false`、`partition_written=false`。

## 判定

### 已證實

- `BootAfterSystemOTA` sender 使用 system-server 建立的 Context，不是 child
  user UI 或普通 APK context。
- sender 的 user scope 預設沿著 system process user 傳遞；沒有從 `UserInfo`
  或外部 shell 參數取得 user。
- sender 受 `onBootPhase(550)` 與 `PackageManagerService.isUpgrade()` 保護，並
  使用專用 permission 發送 broadcast。

### 高可信推論

在 Android system-server 的正常執行模型中，該 process user 是 system user，
通常對應 User 0。因此 OOBE sender 很可能作用於 User 0 context scope；但本
報告不把「system process user」替換成無條件的 live numeric User 0 claim。

### 已排除（bounded）

這條 sender/context chain 沒有證明它是正式 HOME selector。已保存的
`BootAfterSystemOTAReceiver`、`PackageHelper`、`OOBEActivationHelper` 與
`SettingsDBUtils` source 中，沒有看到 `setHomeActivity`、
`replacePreferredActivity`、`addPersistentPreferredActivity` 或
`com.amazon.firelauncher` 的直接 HOME writer。

因此它是 OTA/OOBE lifecycle、component/setup/settings 路徑，不是已證實的
無 Root Launcher replacement 或 shell privilege relay。

### 待驗證

- 這個 build 在自然官方 OTA transition 中的實際 numeric broadcast user；
- runtime 載入的 `fosinit` 是否有本地未保存的額外來源；
- OOBE sink 是否由其他未取得的 native/generated consumer 延伸。

### 因風險拒絕測試

手動重播 protected `BOOT_AFTER_SYSTEM_OTA`、執行 OTA/recovery/updater、修改
settings/component、停用 Fire Launcher、root、分割區寫入均拒絕；原因是該路徑
本身會改變 OOBE 與設定狀態，且不具備無損 rollback 保證。
