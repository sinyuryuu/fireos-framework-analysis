# Phase 6MC：Package-management permission holders 與 H2 household service 稽核

日期：2026-08-10
範圍：PS7331 裝置唯讀採樣 + `com.amazon.alta.h2clientservice` 離線反編譯。
安全界線：沒有建立／刪除使用者、沒有切換使用者、沒有啟動 Service、沒有送
Binder transaction、沒有修改 package/component/settings/HOME、沒有 OTA、reboot、
Root 或分割區操作。

## Executive result

這一輪確認了兩個先前未被同一份證據連起來的事實：

1. 裝置上確實有一組 system/priv-app 取得
   `CHANGE_COMPONENT_ENABLED_STATE`、`MANAGE_USERS`、`WRITE_SECURE_SETTINGS` 等
   signature|privileged 權限；`com.android.vending` 是唯一在本次表中顯示為
   `/data/app` 且沒有 `PRIVILEGED` private flag 的 package-state permission holder。
2. Amazon H2 household service (`com.amazon.alta.h2clientservice`) 的 exported
   `H2ClientService` 具有明確的 signature-level bind permission，且其 API 可在
   合法 household/profile lifecycle 中呼叫 `AmazonUserManager.createChildUser()`。
   這解釋了「從 Amazon profile UI 建立 child user」的自然 caller chain，但不是
   shell 可用的 launcher replacement。

目前沒有新的 User-0 HOME writer，也沒有新的無 Root Fire Launcher replacement。

## Permission-holder inventory — 已證實

輸入是一次新的唯讀 `dumpsys package`／permission-definition capture；raw capture
保存在本機：

`adb/phase6mc-permission-holders-20260810-01/`

原始輸入雜湊：

| Input | SHA-256 |
|---|---|
| `package_dump.stdout.txt` | `c5c14346075ffc6054aa8696f7ff577c54ce97fd96dff8a8ec044a8bdda4fa37` |
| `permission_definitions.stdout.txt` | `62d133892d6488861e85bc7e9aeb9418e258e930e0cda507a695aac1e2e406cc` |

本次 permission definition 顯示：

| Permission | Protection level | Holder rows |
|---|---|---:|
| `CHANGE_COMPONENT_ENABLED_STATE` | `signature|privileged` | 12 |
| `MANAGE_USERS` | `signature|privileged` | 37 |
| `WRITE_SECURE_SETTINGS` | `signature|privileged|development` | 45 |
| `INSTALL_PACKAGES` | `signature|privileged` | 7 |
| `DELETE_PACKAGES` | `signature|privileged` | 8 |
| `FORCE_STOP_PACKAGES` | `signature|privileged` | 3 |

完整的去識別化 package-state table 位於
[`phase6mc-permission-holders.csv`](../output/tables/phase6mc-permission-holders.csv)。
它只表示「package state 顯示 granted」，不表示該 package 可以繞過
PackageManager protected-package gate。

值得注意的 holder：

- `com.amazon.tahoe`：system/priv-app，具有 component-state 與 user-management
  權限；這與既有 KFT child-user writer 證據一致。
- `com.android.managedprovisioning`、`com.amazon.kor.demo`：具有多項 package
  管理權限，但屬 provisioning／retail-demo 邊界；沒有因此得到可安全重播的
  HOME API。
- `com.amazon.alta.h2clientservice`：system/priv-app，具有
  `CHANGE_COMPONENT_ENABLED_STATE`、`MANAGE_USERS` 及 profile/device-owner 相關
  Amazon 權限；本輪對其做了離線 source review。
- `com.android.vending`：`/data/app`、無 captured `PRIVILEGED` private flag，卻
  顯示多項 package-management grants。Phase 6MB 已在 bounded APK scan 中找不到
  Fire/HOME writer；本輪不重做，也沒有呼叫其 exported component。

## H2 service — 靜態與唯讀 runtime 證據

### Manifest／runtime 邊界 — 已證實

裝置端 `cmd package query-services -a
com.amazon.alta.h2shared.aidl.IH2ClientService` 回報：

- `com.amazon.alta.h2clientservice.H2ClientService`
- `enabled=true`
- `exported=true`
- `directBootAware=true`
- `permission=com.amazon.alta.h2clientservice.permission.BIND_SERVICE`
- uid `10012`
- source `/system/priv-app/com.amazon.h2clientservice/...apk`

原始 output 保存在本機
`adb/phase6mc-alta-static-20260810-01/query_service.stdout.txt`；該命令是
PackageManager query，不是 service bind 或 transaction。`resolve-service` 在這個
Android 9 build 不支援，錯誤也被原樣保存，沒有改用猜測的 Binder 呼叫。

本機保存的 manifest 反編譯輸出，其雜湊與公開分析 metadata
[`phase6mc-alta-static-20260810-01/metadata.md`](../artifacts/phase6mc-alta-static-20260810-01/metadata.md)
的 service 宣告位於 local manifest-print lines 144–154：

```xml
<service
    android:name="com.amazon.alta.h2clientservice.H2ClientService"
    android:permission="com.amazon.alta.h2clientservice.permission.BIND_SERVICE"
    android:exported="true"
    android:singleUser="true"
    android:directBootAware="true">
```

該 permission 在 manifest 中是 signature protection level。因而
`exported=true` 不能被解讀成 shell 或任意 APK 可綁定。

### API chain — 已證實靜態流程

```text
authorized H2 client
  → H2ClientService.onBind()
  → IH2ClientService.addUser()
  → AddUserAPICall
  → HouseholdController.createUser()
  → CreateAndroidUserCommand
  → UserHelper.createAndroidUser()
  → AndroidUserHelper.addAndroidUser()
  → AmazonUserManager.createChildUser(name)
  → AmazonUserManagerService / child-user lifecycle
```

可核對的位置：

- `H2ClientService.java:105–107` 建立 `IH2ClientService.Stub`；`addUser()` 在
  `:124–127` 將參數交給 `AddUserAPICall`。
- `HouseholdController.java:323–372` 建立 user workflow。
- `CreateAndroidUserCommand.java:21–32` 呼叫 `UserHelper.createAndroidUser()`。
- `UserHelper.java:22–29` 委派至 `AndroidUserHelper.addAndroidUser()`。
- `AndroidUserHelper.java:78–81` 依 household role 呼叫
  `createAdultUser()` 或 `createChildUser()`。

### 沒有直接 HOME writer — Strong evidence / bounded

在本次 APK 的 JADX source 與 literal scan 中：

- `com.amazon.firelauncher` literal matches：0。
- 未找到 `setPreferredActivity`、`replacePreferredActivity`、
  `addPreferredActivity`、`setApplicationEnabledSetting`、
  `setComponentEnabledSetting`、`CATEGORY_HOME` 或 `ACTION_MAIN` writer。
- 找到的是 user/profile model、household database、account workflow 與
  `AmazonUserManager` 呼叫。

JADX 輸出是離線近似 source；APK hash 為
`b1def31c9b1ba2aa8064d31d18e294a9b60e5a98a06a1ec657ad115a08f1850b`，工具版本
JADX 1.5.6。此結果不排除 native／resource／failed-decompilation 路徑，因此
標記為 bounded Strong evidence，不是全域不存在證明。

### Caller identity 判定

`AbstractAPICall.execute()` 只把 `Binder.getCallingUid()` 寫入 metric log；在
recovered H2 Stub method body 沒看到額外的 method-local caller check。但真正的
入口邊界是 service binding 的 signature permission。這表示：

- **已證實：** H2 是高權限、可改變 Amazon household/profile user state 的服務。
- **高可信推論：** 只有具備 Amazon signature-level bind capability 的合法 client
  才能走到這個 Stub；shell 不應被 `exported=true` 迷惑。
- **未證實：** 完整的 `AmazonUserManager` framework implementation、所有
  signature-equivalent caller 與 child lifecycle 後續 package-state callback。
- **因風險拒絕測試：** bind H2、呼叫 `addUser`／`createChildUser`、建立或刪除
  child profile、切換 user、呼叫 reset/remove API。這些會改變使用者資料與
  foreground/HOME 狀態，且部分 error path 明確提示可能需要 factory reset。

## 與 Fire Launcher 目標的關係

| 問題 | 判定 |
|---|---|
| H2 是否直接選擇 `com.amazon.firelauncher`？ | **已排除於 bounded APK scan**：沒有 literal 或 HOME writer。 |
| H2 是否能建立 child user？ | **已證實靜態**：`createChildUser()` chain 存在，但只能由授權 service client 觸發。 |
| child lifecycle 是否可能導向 Tahoe／Fire per-user state？ | **高可信推論／既有證據支持**：與 Phase 6BK 的 child-scoped KFT writer 相接；不是 User-0 route。 |
| H2 是否提供無 Root User-0 HOME replacement？ | **未找到；目前否定性證據為 Strong evidence**。 |
| 是否應用 shell／service call 實測？ | **因風險拒絕**：需要 signature-bound bind、建立 profile 或未知 IPC，且不是必要的 HOME 證據。 |

## 最小後續研究包

下一個安全、非重複工作是使用
[`phase6mc-caller-provenance`](../artifacts/phase6mc-caller-provenance-20260810-01/)
中的 host-only matrix，將 H2 child caller、KFT tx3、IAmazonUserManager tx4、
prewarm 與 post-OTA OOBE sender 放到同一個 caller→sink→user-scope 表。它不會
呼叫任何 service，也不會新增 user。

若要繼續實機，僅允許同樣的 PackageManager read-only query；不允許用 H2 service
建立測試 child profile，也不允許重播 `BOOT_AFTER_SYSTEM_OTA` 或 KFT transaction。

## Reproducibility

```sh
python3 tools/scripts/capture_phase6mc_permission_holders.py \
  --serial DEVICE_SERIAL \
  --output adb/phase6mc-permission-holders-YYYYMMDD-01 --dry-run

python3 tools/scripts/audit_phase6mc_permission_holders.py \
  --package-dump adb/phase6mc-permission-holders-YYYYMMDD-01/package_dump.stdout.txt \
  --permission-dump adb/phase6mc-permission-holders-YYYYMMDD-01/permission_definitions.stdout.txt \
  --output artifacts/phase6mc-permission-holder-audit-YYYYMMDD-01
```

All commands in the capture script are ADB read-only queries and require an explicit
serial. Raw device captures are intentionally kept local; the public commit contains
the de-identified table, hashes, scripts and conclusions, not the full device dump or
proprietary APK.
