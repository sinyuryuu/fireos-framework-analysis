# Phase 6PR — KFT tx3 authorization and caller-to-sink closure

日期：2026-08-10

## 範圍與安全界線

本階段只讀取已保存的 PS7331 VDEX disassembly、既有 Phase 6 ordinary-app
實測結果，並執行一份新的主機端索引腳本。沒有連接裝置、沒有取得 Binder
handle、沒有送出 transaction、沒有建立 child user、沒有改變 package/settings
state，也沒有執行 exploit、ioctl、OTA 或 kernel 操作。

腳本：

`tools/scripts/audit_phase6pr_kft_tx3_authorization.py`

再現輸出：

`artifacts/phase6pr-kft-tx3-authz-20260810-06/`

腳本 SHA-256：`57e3b1664c7ef4a07cc10cef9cbf37cf4c2503cabd1222a2fa8e193509d01497`

輸出目錄內的 `sha256sums.txt` 已驗證三個產出檔案。

輸入 disassembly 的 SHA-256：

| 輸入 | SHA-256 |
|---|---|
| `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` |

## 結論

### 已證實

1. `IAmazonUserManager` 的 tx3 是 `enableKftLauncher(UserInfo)`；Stub 只看得到
   AIDL interface token、反序列化 `UserInfo` 及方法 dispatch，未看到
   `getCallingUid()`、`enforceCallingPermission()` 或 `MANAGE_USERS` 檢查。
2. `AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)`
   是實際 package/component state writer：
   - 啟用 `com.amazon.tahoe/.launcher.FreeTimeLauncherActivity`；
   - 以 state `2` 停用 `com.amazon.firelauncher`；
   - 以 state `2` 停用 `com.android.launcher3`；
   - 三個 setter 都使用傳入的 `UserInfo.id`。
3. `enableKftLauncher()` 先呼叫 `tryEnableKftLauncherComponent()`，該路徑在
   `clearCallingIdentity()` 前執行 package/component setters；清除 identity
   發生在後續 Device Policy／profile-owner empowerment path。
4. 同一服務確實存在 `checkManageUsersPermission(String)`，但在目前保存的
   class slice 中，直接呼叫者是 `getUserSortedListFromFile()`；tx3 路徑沒有
   呼叫它。
5. 既有 ordinary-app 實測證明「Binder 可達」不等於「writer authority」：
   - User 10 payload 在 PMS 以 `INTERACT_ACROSS_USERS` 拒絕；
   - User 0 child-flag payload 在第一次 Tahoe component setter 以
     `Attempt to change component state` 拒絕；
   - Fire HOME、Fire package state 與 Tahoe enabledComponents 均未變更。

### 高可信推論

- tx3 是一個高價值的靜態 confused-deputy review point，但目前不是已證實的
  privilege escalation。真正的安全邊界在 PMS downstream setter、跨使用者檢查、
  protected-package/component gate 與 service/SELinux reachability。
- 既有 KFT child lifecycle 的合法 caller 是 `AmazonUserManagerImpl.createChildUser()`
  與 system-server boot-phase child-user flow；它以 child/profile 的 `UserInfo.id`
  工作，不是已確認的 User-0 HOME restoration writer。

### 待驗證

- 保存 corpus 之外是否有未收錄的 runtime-loaded/native/alias caller。
- 未來 Fire build 是否把 service manager policy、PMS gate 或 KFT method body 改變。
- OOBE/OTA lifecycle helper 的 exact user mapping；該路徑因風險沒有 replay。

### 已排除（目前 build／既有前提）

- ordinary app 透過 tx3 直接改變 User 0 Fire/Tahoe package state；Phase 6FK
  已在第一個 setter 前被 PMS 拒絕。
- ordinary app 透過 tx3 改變 User 10 package state；Phase 6FJ 已被跨使用者
  gate 拒絕。
- tx3 是固定 User-0 HOME selector；writer 的 user selector 是傳入的
  `UserInfo.id`，而 User 0 mutation 未成功。

## 精確呼叫鏈

```text
AmazonUserManagerImpl.createChildUser(String)
  → IAmazonUserManager.Proxy.enableKftLauncher(UserInfo)
  → Binder.transact(code=3)
  → IAmazonUserManager.Stub.onTransact()
  → BinderService.enableKftLauncher(UserInfo)
  → tryEnableKftLauncherComponent(UserInfo)
  → enableKftLauncherComponent(UserInfo)
  → AmazonPackageManager setters using UserInfo.id
  → PackageManagerService gate / state mutation
```

`BinderService.enableKftLauncher()` 後半另有：

```text
tryEnableKftLauncherComponent()
  → Binder.clearCallingIdentity()
  → empowerKftUser(UserInfo)
  → DevicePolicy active-admin/profile-owner calls
  → Binder.restoreCallingIdentity()
```

這個後半段不能倒推前半段 setters 以 system identity 執行。

## 重要程式位置

| 層級 | 路徑與行號 | 觀察 |
|---|---|---|
| KFT state sink | `fosservices/disassembly.log:54297-54325` | Tahoe enable、Fire/Launcher3 state 2、`UserInfo.id` |
| KFT helper | `fosservices/disassembly.log:54371-54414` | `UserInfo.id`、TV/exists gate、呼叫 sink |
| Binder implementation | `fosservices/disassembly.log:54415-54478` | tx3 implementation；setter 前於 clear identity |
| permission helper | `fosservices/disassembly.log:54847-54875` | `MANAGE_USERS` check 本身存在 |
| helper caller | `fosservices/disassembly.log:54904-54906` | `checkManageUsersPermission()` 的 bounded direct caller |
| lifecycle | `fosservices/disassembly.log:55053-55105` | `isUpgrade()`、child-user predicate、KFT invocation |
| service publish | `fosservices/disassembly.log:55106-55119` | 發布 `amazonusermanagerservice` |
| child caller | `boot-fosframework/disassembly.log:369180-369243` | create child 後呼叫 tx3、再設定 setup complete |
| Proxy | `boot-fosframework/disassembly.log:370398-370443` | interface token、UserInfo、`transact(3,...)` |
| Stub | `boot-fosframework/disassembly.log:370674-370777` | interface enforcement、parcel read、tx3 dispatch |

## 實機證據（不重做）

### User 10：跨使用者 gate

來源：`adb/phase6fj/PHASE6FJ-USER10-TX3-20260807-01/command-output.txt:20-32`。

ordinary APK UID `10212` 確實取得 service handle 並送出 User 10 tx3；system
server 隨後在 `PackageManagerService.setEnabledSetting()` 回報：

```text
SecurityException: set enabled: Neither user 10212 nor current process has
android.permission.INTERACT_ACROSS_USERS.
```

回傳 `result=false`，User 0 HOME 與 User 10 baseline 未變更。

### User 0：component/protected gate

來源：`adb/phase6fk/PHASE6FK-USER0-TX3-20260807-01/command-output.txt:14-32`。

ordinary APK UID `10213` 的 structurally valid User 0 payload 在 Tahoe 第一個
component setter 被拒：

```text
SecurityException: Attempt to change component state; pid=27832, uid=10213,
component=com.amazon.tahoe/com.amazon.tahoe.launcher.FreeTimeLauncherActivity
```

因此没有 Fire disable call 的成功後效；HOME 仍為 priority 50 的 Fire Launcher。

## 判定

| 命題 | 判定 |
|---|---|
| tx3 有 package/component writer | **Confirmed** |
| tx3 Stub/implementation 顯示 method-local caller permission check | **Disproved in bounded slice** |
| 存在一般 `MANAGE_USERS` helper | **Confirmed** |
| tx3 會使用 system identity 執行前段 setter | **Disproved by code order and FJ/FK attribution** |
| ordinary app 可在目前 PS7331 直接以 tx3 改 User 0 | **Disproved by Phase 6FK** |
| tx3 是可交付的 root 或 system-UID escalation | **Unknown / not established** |

## 安全 disposition

本階段沒有新增可利用 payload，也沒有提出或執行未知 Binder transaction。
tx3 應保留為「靜態高影響 writer + downstream gate 已觀察」研究項目；若沒有
新 build、可驗證的 exported relay 或新的 caller provenance，不應重複既有 tx3
測試。
