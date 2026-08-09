# Phase 6NO：Private-service client universe 與 OOBE user-scope 整合

日期：2026-08-10
分類：主機端靜態分析；不包含 Binder replay 或裝置狀態修改。

## 結論

### 已證實

1. 在指定的 PS7331 decompiled/JADX、baksmali、fosinit 與既有 evidence corpus 中，
   已建立主要 Amazon private service 的 publication、Proxy/Stub、已知 client 與
   sink 索引。涉及 User、Profile、Package、Activity、Window、Input、Accessibility、
   DPM 與 `fosdebug`。
2. 最接近正式 HOME/package-state 的 private API 仍只有兩類：
   - KFT `enableKftLauncher(UserInfo)`：child/profile supplied-user writer。
   - Profile generic launcher helper：以 profile/current context 啟動 launcher，沒有
     preferred/HOME/package-state writer。
3. `IAmazonPackageManager` 的 flags/metadata mutators 會保存 package metadata，
   但已核對的 consumer 沒有連到 HOME、preferred 或 enabled-state sink。
4. `IAmazonActivityManager.preWarmApplicationForUser` 與 UserManager tx4 各自存在
   已保存的 ordinary-app confused-deputy／permission-result defect，但其 effect
   是 process 或 setup-state；沒有 Fire Launcher User 0 sink。
5. OOBE 路徑的 user scope 可靜態追到 system context 的 process-UID-derived
   `ContextImpl.mUser`，再到 broadcast、receiver Context、PackageManager 與
   Settings provider；不能由該鏈直接證明 numeric User 0。

### 高可信推論

- `service list` 中存在 Amazon service 不等於 shell 或普通 APK 可取得該 service；
  保存的 shell SELinux `service_manager find` denial 仍是主要邊界。
- 目前沒有「普通 caller → Amazon private service → User 0 → Fire HOME/preferred
  sink」的完整鏈。缺少 local permission marker 的 method 仍不可視為漏洞。
- OOBE `BootAfterSystemOTAReceiver` 是 OTA/setup lifecycle surface，不是已證實的
  ordinary HOME setter 或可安全 replay 的 launcher route。

### 待驗證

- 未保存的 native/reflective client、其他 APK alias、runtime-loaded class 與完整
  generated superclass authorization 仍不能被此 bounded corpus 全域排除。
- OOBE sender 使用 process-derived user 的實際 numeric 值，以及自然官方 OTA 後
  的 delivery user，仍沒有直接 runtime numeric evidence。
- `AmazonInputManager.inject*` 的 native permission enforcement 與所有 device-node
  policy 未閉合；這不構成可測試的 HOME 或提權候選。

### 已排除（狹義）

- 已索引 private service 直接提供 ordinary User 0 `setHomeActivity`、preferred
  activity 或 Fire package-state setter。
- Profile picker／generic profile launcher helper 可作 User 0 formal HOME replacement。
- Amazon package metadata/flags persistence 本身會改寫 HOME resolver。
- 只靠猜測 Binder transaction code、`service call` 或缺少 permission 字串即可取得
  system identity。

### 因風險拒絕測試

本輪沒有發送 private Binder transaction、OOBE/OTA broadcast、input injection、
ioctl、未知 service call、package/settings/user mutation、Root 或分割區操作。

## Private service route matrix

| Service | 已知 client／sink | HOME／Fire 判定 | 信心 |
|---|---|---|---|
| `amazonusermanagerservice` | `AmazonUserManagerImpl` → tx3/tx4/tx5/tx6；KFT writer 使用 `UserInfo.id` | child/profile state；非 unconditional User 0 HOME | Confirmed |
| `amazonprofileservice` | `AmazonProfileManager`；profile picker 與 launcher helper | profile lifecycle/explicit start；無 preferred writer | Confirmed / Strong evidence |
| `amazonpackagemanager` | `AmazonPackageManager`、`FtvSpecAssertionUtility` | flags/metadata/proxy/query；無 HOME/package-state consumer | Confirmed / Strong evidence |
| `amazonactivitymanager` | `AmazonActivityManagerImpl`、system callbacks、ordinary prewarm probe | process/task/prewarm；無 HOME/package sink | Confirmed / Strong evidence |
| `amazonwindowmanager` | window/PIP helpers | window/PIP only；無 HOME/package sink | Confirmed bounded |
| `amazon_input` | input framework/callback clients | listener/injection boundary；直接 HOME sink 未見，native enforcement pending | Strong evidence bounded |
| `amazonaccessibilitymanager` | accessibility/canvas service | magnification canvas；無 HOME/package sink | Confirmed bounded |
| `amazondevicepolicymanager` | DPM facade | restriction/backup state；非 HOME writer | Confirmed bounded |
| `fosdebug` | diagnostics/dump | read-only diagnostics in inspected surface | Strong evidence |

## OOBE user-scope decision tree

```text
SystemServer.createSystemContext()
  -> ContextImpl(UserHandle=null)
  -> Process.myUserHandle() -> ContextImpl.mUser
  -> AmazonPackageManagerService.mContext
  -> boot phase 550 + isUpgrade()
  -> sendBroadcast(action, receiver-permission)
  -> receiver Context derived from delivery
  -> PackageHelper.enableComponent(context, OobeHomeActivity)
  -> ApplicationPackageManager.getUserId(context)
  -> PMS component-state sink

same receiver Context
  -> OOBEActivationHelper
  -> ContentResolver
  -> Settings.Secure/Global writes
```

決策結果：

- process/context-derived：**Confirmed / High**；
- `UserInfo.id`-derived：**Not observed**；
- `UserHandle.SYSTEM`／numeric `0` explicit：**Not observed**；
- exact numeric sink user：**Unknown**；
- ordinary Fire Launcher HOME writer：**Bounded negative / Strong evidence**。

## 既有動態結果的正確定位

| Test／finding | 實際效果 | 不能外推為 |
|---|---|---|
| F-108 / UserManager tx4 | ordinary APK 影響 setup-state settings | User 0 Fire/HOME relay |
| PHASE6ER / ActivityManager tx1 | ordinary APK 觸發 prewarm/process effect | root 或 HOME selector |
| PHASE6GS | profile helper 啟動 Fire launcher | third-party formal HOME |
| PHASE6FH／6FJ／6FK | private UserManager handle/tx downstream boundary | arbitrary tx3 或 shell bypass |
| HOME priority／preferred tests | ordinary resolver/preferred 不勝 Fire | protected/system priority 可由 sideload APK取得 |

## 最佳可行方案與停止線

目前最接近可用的是既有 Accessibility foreground redirect：需要使用者在 Settings
明確同意、可關閉、可回到 Fire；但它不是 formal HOME replacement，可能有延遲、閃現與
背景服務限制。

若目標限定為「不 Root、不停用 Fire、不改分割區且正式 `resolve-activity` 變成第三方」：
目前沒有新的安全候選。繼續追 private Binder 的未知 transaction、OOBE replay、OTA
構造或 driver ioctl 不會增加可驗證性，反而跨入高風險操作。

下一個仍有研究價值的 host-only 目標是：

1. 對尚未保存的 native/reflective client 做 artifact completeness inventory；
2. 對 OOBE/OTA 做自然事件後的只讀 state correlation，而非手動觸發；
3. 對 `AmazonInputManager` native implementation 做 source/ELF permission mapping，
   不接觸 device node。

若這三項仍沒有 User 0 HOME sink，應把正式 HOME replacement 標為目前不可行，並把
Accessibility foreground fallback 作為唯一近似方案，而不是再猜測或重跑已排除測試。
