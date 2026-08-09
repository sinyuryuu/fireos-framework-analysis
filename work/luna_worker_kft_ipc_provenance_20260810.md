# KFT / Amazon IPC caller provenance（PS7331，2026-08-10）

範圍：僅檢查工作區已保存的 Fire OS PS7331 framework/services VDEX disassembly、JADX 與既有 Phase 6 報告。未執行 adb、裝置連線、Binder/service call、ioctl、root、OTA/updater、刷機或任何狀態修改；未重做 KFT tx3 replay 或 standard package-state tests。

## 結論摘要

目前最完整、可由 host artifact 支持的 provenance 是：`AmazonUserManagerImpl.createChildUser(String)` 建立 child `UserInfo` 後，唯一保存的 tx3 callsite 會把該 `UserInfo` 傳給 `IAmazonUserManager.enableKftLauncher(UserInfo)`；system_server 的 `AmazonUserManagerService.BinderService` 再以 `UserInfo.id` 對 Tahoe、Fire Launcher、Launcher3 寫入 component/application enabled state。這是 child/profile-scoped trusted lifecycle writer，不是已證實的 User-0 HOME writer。

信心：caller→tx3→supplied `UserInfo.id`→三個 package-state sink 為 **Confirmed/High**；「實際外部 caller 只有受信任 Amazon lifecycle」為 **Strong/Medium-High**（保存 corpus 沒有完整 caller universe 或 runtime UID）；tx3 的 method-local authorization 為 **Unknown/Medium**，因為 tx3 path 本身未見 `getCallingUid`、permission check 或 `clearCallingIdentity`，但 service publication、一般管理權限 helper 與 SELinux/private-service evidence 不能被忽略；User-0 HOME writer 為 **未發現，Strong/High negative within preserved scope**。

## 1. createChildUser → tx3 caller chain

### 1.1 API surface

* `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:11705-11734`：`AmazonUserManager` 是 public abstract API；`createChildUser(String)` 是 public abstract method，沒有 caller/permission body。
* 同檔 `:369050-369109`：`AmazonUserManagerImpl` 的 constructor 取得普通 `user` service；`getAmazonUserManager()` 以 `ServiceManager.getService("amazonusermanagerservice")` 取得 Binder，再呼叫 `IAmazonUserManager.Stub.asInterface`（約 `:369080-369095`）。
* `decompiled/jadx/systemui/sources/amazon/os/AmazonUserManager.java` 是保存的 JADX API facade（SHA-256 `42d3f0528619cd106ff09c5ca315f0b214328490e259ea33331c48ec18490cb0`）；它只保留抽象 public API，不能單獨證明 caller identity。

### 1.2 createChildUser implementation

`boot-fosframework/disassembly.log:369180-369255`（VDEX SHA-256 `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`）顯示：

1. `createChildUser(String)` 先以常數 `0x8000` 呼叫 `AmazonUserManagerImpl.createUser(String, int)`（`079ee0-079ee6`）；這是 child-type creation input。
2. 若建立失敗，直接記錄 `Failed to create user` 並回傳 null（`079eee-079f20`）。
3. 成功後取得 `mService`；若 service 不可用，對新 user 的 `id` 呼叫 `removeUser(id)`（`079f22-079f48`）。
4. service 可用時，唯一保存的 tx3 semantic call 是 `IAmazonUserManager.enableKftLauncher(UserInfo)`（`079f4a-079f54`），隨後呼叫 `setUserSetupComplete(UserInfo)`（`079f5a-079f66`）。成功才包成 `AmazonUserInfo`（`079f6e-079f78`）；例外分支以 `UserInfo.id` cleanup（`079f86-079fa0`）。

在保存的 disassembly 中，`AmazonUserManagerImpl.createChildUser` 沒有其他 static caller；對 `IAmazonUserManager.enableKftLauncher` 的完整 reference scan 也只找到這一個 caller：`boot-fosframework/disassembly.log:369217`。因此可確認的 caller provenance 是「Amazon framework facade 的 child-user creation lifecycle」，但不能從現有 corpus 宣稱所有上游 UI、app 或 runtime event 已全部封閉。

## 2. Binder interface、transaction 3 與 service publication

### 2.1 Proxy

`boot-fosframework/disassembly.log:370378-370428` 的 `IAmazonUserManager.Stub.Proxy.enableKftLauncher(UserInfo)`：

* 寫入 interface token `amazon.os.IAmazonUserManager`（`07b6c0-07b6c4`）。
* 將 nullable `UserInfo` 以 `writeToParcel` 寫入（`07b6ca-07b6e0`）。
* 明確呼叫 `IBinder.transact(3, data, reply, 0)`（`07b6e6-07b6f2`）。
* 讀取 exception 與 boolean return（`07b6f2-07b718`）。

### 2.2 Stub dispatch

`boot-fosframework/disassembly.log:370637-370750`：Stub attach token 在 `07bb12-07bb1c`；`onTransact` 先 `enforceInterface`，讀 nullable `UserInfo`，在 `07ba80-07ba8e` dispatch 到 `Stub.enableKftLauncher(UserInfo)` 並寫回 boolean。packed-switch/transaction mapping 因此與 Proxy 一致：**tx3**。

### 2.3 Service object and name

`fosservices/disassembly.log:54238-54247`：`AmazonUserManagerService.BinderService` constructor 呼叫 `IAmazonUserManager$Stub.<init>`。

`fosservices/disassembly.log:55106-55118`：`onStart()` 建立 BinderService，取得 `getSystemServiceName()`，呼叫 `publishBinderService(name, binder)`，並另外 publish local service。`boot-fosframework/disassembly.log:369085-369095` 保存的 client name 是 `amazonusermanagerservice`。既有 Phase 6T/6AV capture 只證明 service registration 可見、shell UID 2000 的 service-manager `find` 被 enforcing SELinux deny；不能把 service name 當成 ordinary-app/shell 可達性。

## 3. Service-side tx3 sink、UserInfo/userId data-flow

### 3.1 Entry and local guards

`fosservices/disassembly.log:54415-54440` 的 `BinderService.enableKftLauncher(UserInfo)`：

* 先取得 `mAmznPackageManager`；null 時回傳 false（`042dbe-042de2`）。
* 呼叫 `isMMDevice()`；若為 MM device，直接回傳 true（`042de4-042df2`）。
* 否則呼叫 `tryEnableKftLauncherComponent(UserInfo)`（`042df4-042dfc`），失敗回傳 false，再進入 DPM/KFT 後續流程（其餘 body 見同檔 `042e02` 起）。

這個 bounded tx3 method body 沒有看到 `Binder.getCallingUid`、`checkCallingPermission`、`checkCallingOrSelfPermission` 或 `clearCallingIdentity`。因此「tx3 method-local authorization 未封閉」是實際缺口；不能把它誤寫成「已證明無 authorization」，也不能僅由此推導可利用 caller。

### 3.2 Component/application writers

`fosservices/disassembly.log:54297-54325`（VDEX SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`）的 private `enableKftLauncherComponent(UserInfo)` 是直接 writer：

* `042dfe-043204`：建立 `com.amazon.tahoe/.launcher.FreeTimeLauncherActivity`，讀取傳入 `UserInfo.id`（`043204`），呼叫 `AmazonPackageManager.setComponentEnabledSetting(..., newState=1, flags=1, userId)`。
* `043210-04322e`：對 `com.amazon.firelauncher` 呼叫 `setApplicationEnabledSetting(..., newState=2, flags=0, userId=UserInfo.id)`。
* `04322e-043248`：對 `com.android.launcher3` 同樣寫入 new state 2，user argument 仍是 `UserInfo.id`。

這條 path 沒有常數 user 0；所有 package-state writes 都從 parcelled `UserInfo.id` 導入。其 scope 結論為 **Confirmed**：是 supplied-user/child profile writer。既有 `findings/phase-6bk-kft-component-state-boundary.md`（SHA-256 `8f88c97f80d3dfa015ae766359fe1cb16ca8a533e697a4f8ff3f81b2647e0394`）與 `findings/phase-6er-kft-child-switch-attribution.md`（SHA-256 `926dd8158f664889dbae58a4d9980fed7f816f222dbbfbb03659c5422290f4af`）已保存相同 sink/child attribution，故不重做 runtime replay。

### 3.3 General management gate is separate

`fosservices/disassembly.log:54851-54875` 的 `checkManageUsersPermission(String)` 會讀 `AmazonUserManagerHelper.getCallingUid()`；UID 1000 或 0 放行，其他 UID 必須通過 `android.permission.MANAGE_USERS`，否則 SecurityException。這證明 service 具有一般 user-management authorization helper，但保存的 tx3 bounded path 沒有證明它在 `enableKftLauncher` entry 被呼叫。結論：

* caller permission/UID for tx3：**Unknown/Medium**；
* general service user-management gate：**Confirmed/High**；
* ordinary shell/private-service reachability：**Strong negative**, 由既有 Phase 6T/6AV enforcing SELinux capture 支持。

## 4. Caller provenance interpretation

最小可證明 chain：

```text
AmazonUserManagerImpl.createChildUser(String)
  -> createUser(name, 0x8000)
  -> UserInfo (supplied object, later UserInfo.id)
  -> IAmazonUserManager.Proxy.enableKftLauncher(UserInfo)
  -> Binder tx=3
  -> AmazonUserManagerService.BinderService.enableKftLauncher(UserInfo)
  -> tryEnableKftLauncherComponent(UserInfo)
  -> AmazonPackageManager component/application state writes for UserInfo.id
```

The only static tx3 caller found is the framework implementation above. This is strong evidence against a preserved ordinary-app caller, but not a proof that no runtime-loaded/private Amazon client exists outside the retained VDEX/JADX corpus. Existing Phase 6 reports correctly label the actual runtime path as trusted Amazon child/profile lifecycle; the saved child-switch attribution observed User 10 and no User-0 package/HOME write.

## 5. UserInfo/userId, caller UID/permission matrix

| Edge | Evidence | Result | Confidence |
|---|---|---|---|
| Child creation type | `boot-fosframework/disassembly.log:369180-369186` | `createUser(name, 0x8000)` | Confirmed/High |
| Object to tx3 | `...:369203-369217` | Same returned `UserInfo` passed to tx3 | Confirmed/High |
| Parcel to service | `boot-fosframework/disassembly.log:370398-370428`; Stub `:370637-370750` | Nullable `UserInfo`, tx3, `enforceInterface` | Confirmed/High |
| Writer user scope | `fosservices/disassembly.log:54304-54325` | Every writer uses `UserInfo.id`; no hard-coded 0 | Confirmed/High |
| Method-local tx3 caller UID | `fosservices/disassembly.log:54415-54440` | No bounded UID/permission/identity call seen | Unknown/Medium |
| General service permission | `fosservices/disassembly.log:54851-54875` | UID 1000/0 or `MANAGE_USERS` helper | Confirmed/High, not proven tx3 edge |
| Service publication | `fosservices/disassembly.log:55106-55118` | system-service Binder + local service | Confirmed/High |
| Shell access | `findings/phase-6t-ipc-live-evidence-index.md`, `findings/phase-6av-ipc-method-closure.md` | service registration != handle; UID 2000 find denied | Confirmed/Strong |

## 6. 是否存在 User-0 HOME writer？

在保存 corpus 與既有 Phase 6 closure 範圍內，沒有找到由 KFT tx3 直接寫 User-0 HOME 的證據：

1. KFT direct sink 只寫 supplied `UserInfo.id` 的 Tahoe/Fire/Launcher3 package/component state；沒有 `setHomeActivity`、`replacePreferredActivity`、`addPersistentPreferredActivity` 或 Role/HOME setter call（`fosservices/disassembly.log:54297-54325`）。
2. `findings/phase-6ij-user0-home-candidate-closure.md`（SHA-256 `1d38d8aeaf37c5dfea4cce8e155c6e185c3df0b89a1eb7ae18db16cb2712f611`）保存 exact-build non-child User-0 HOME candidate inventory：Fire priority 50 remains selected；inventory scope 未產生新 User-0 writer。
3. `findings/phase-6fz-user0-writer-closure.md`（SHA-256 `40bd749e3f23f017304557f9ba073f6c85798f607746f826885fb03c2acaa663`）檢查 ProductPolicy、KOR demo、AMS.systemReady、generic DPM、WebView 等 residual writer，未找到新的 confirmed Fire/User-0 HOME/component writer；這些是 bounded negatives，不是全宇宙證明。
4. `findings/phase-6kv-pms-home-caller-closure.md` 與既有 25-row HOME caller inventory 已記錄沒有新的 Amazon `setHomeActivity`、preferred-HOME 或同類 static invoke site；KFT 是 launcher-specific package-state writer，而非 formal HOME setter。
5. `findings/phase-6er-kft-child-switch-attribution.md` 的保存 runtime attribution（User 10 child lifecycle；回 User 0 後 Fire HOME/priority/state unchanged）排除了「KFT tx3 是 User-0 restoration watchdog」這個已測路徑；本報告不重做該測試。

因此目前最準確的結論是：**未發現 User-0 HOME writer；KFT 是 child/profile component-state writer。** 信心對 preserved static/runtime scope 為 Strong/High；對未保存的 runtime-loaded Amazon caller universe 為 Medium，仍有 corpus completeness gap。

## 7. 剩餘缺口（host-only，禁止擴展成裝置測試）

* 讀取更完整同版 DEX method table/source，確認 `enableKftLauncher` 是否由 inherited/generated Stub 或 framework entry 間接套用 `MANAGE_USERS`；目前 bounded body 未證明。
* 建立所有保存 artifact 的 `createChildUser`、`enableKftLauncher`、`amazonusermanagerservice` reference inventory，並檢查 runtime-loaded `fosinit`/private Amazon client 是否在 preserved corpus 外；若無新 concrete caller，維持 Unknown/Medium，而非升格漏洞。
* 對 `UserInfo.id` 僅做 static taint/data-flow closure；不得把 child creation 參數或 runtime User 10 observation 推廣成 User 0。
* 不再送 tx3、猜 transaction、取得 private Binder handle、重跑 child switch/unlock/PIN 或 standard PMS package-state tests。

## Final disposition

**Caller provenance：** `AmazonUserManagerImpl.createChildUser` 是唯一保存的 tx3 caller，透過 `IAmazonUserManager.Proxy` transaction 3 將新建 child 的 `UserInfo` 傳入 system_server；service writer 使用 `UserInfo.id`，並啟用 Tahoe、停用 Fire/Launcher3，故是 trusted child/profile-scoped state transition。

**Authorization：** service 一般存在 UID 0/1000 或 `MANAGE_USERS` gate，但 tx3 bounded method 未見 local UID/permission/identity check；這是靜態缺口，不是 ordinary-app reachability 證明。既有 SELinux service-manager deny 與 Phase 6 runtime/static closure 支持 shell/private IPC boundary。

**User 0 HOME：** 在目前保存的 PS7331 VDEX/JADX 與 Phase 6 corpus 中沒有明確 User-0 HOME writer；KFT 沒有 formal preferred-HOME API，User-0 Fire HOME remains the resolver result. Remaining uncertainty is limited to completeness of preserved runtime-loaded/private Amazon caller artifacts and tx3 inherited authorization mapping.
