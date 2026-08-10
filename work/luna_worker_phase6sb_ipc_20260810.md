# Phase 6SB IPC／權限證據整理（host-only）

日期：2026-08-10。僅讀取工作樹既有 framework/APK/JAR 反編譯、permission XML、Phase 6K/6R/6RY 及相關 caller/sink 產出；未執行 adb、service call、Binder transaction、裝置寫入、exploit，亦未修改既有檔案。本報告不把「未找到」升格為全映像不存在。

## 結論

### 1. `amazon.permission.ADD_RM_PKG_METADATA`

目前不能由本地證據閉合 declaration → protectionLevel → grant/holder → actual production caller。

- Exact saved permission XML `018_android.amazon.perm.xmltree.txt` 沒有該 permission；permission-holder census 也沒有 exact row。因此 declaration、`protectionLevel`、holder package、grant source 與 production caller 均為 **UNKNOWN**。XML/census 的缺失是 bounded evidence gap，不是「沒有 declaration/holder」的否定證明。
- 可確認的是 `AmazonPackageManagerService.BinderService` 的 tx1/tx2/tx4/tx5 metadata/flags mutators，在 `fosservices/disassembly.log:95866-96037` 檢查 `amazon.permission.ADD_RM_PKG_METADATA`，再寫入 `AmazonApplicationFlags`／`amazon_package_flags.xml`；沒有從該 metadata path 到 HOME、preferred-activity、`setApplicationEnabledSetting` 或 `setComponentEnabledSetting` 的保存證據。
- generated `IAmazonPackageManager` interface/Proxy/Stub 與 `AmazonPackageManagerImpl` facade callsites 可確認 Binder contract 和 framework facade edge；它們不是 production caller proof。現有 caller inventory 只到 facade，upstream production caller 仍 UNKNOWN。

判定：**metadata persistence sink = STATIC/CONFIRMED；declaration/protection/holder/actual caller = UNKNOWN**。

### 2. KFT／parent/profile/user-manager 到 package-state sink

- `IAmazonUserManager` tx3 `enableKftLauncher(UserInfo)` 是保存 corpus 中唯一已閉合至 package/component state sink 的 KFT writer：使用 supplied `UserInfo.id`，對 Tahoe FreeTime Launcher component、Fire Launcher 與 Launcher3 application/component state 呼叫 standard/Amazon package-manager setters。這是 child/profile-scoped writer；不是 formal preferred-HOME setter，也不是硬編碼 User 0 writer。
- 唯一保存的 framework caller chain 是 `AmazonUserManagerImpl.createChildUser(String)`／system-server child lifecycle → tx3；完整 runtime caller universe 仍 UNKNOWN。tx3 bounded entry 可見 interface-token enforcement，但沒有在該 slice 證明 method-local caller permission/UID gate；不能因此推導可利用。
- 既有 ordinary APK evidence：tx3 到 User 10 被 PMS `INTERACT_ACROSS_USERS` gate 擋下；target User 0 的 component-state mutation 被 PMS caller/protected-component gate 擋下。故在保存 build evidence 內，沒有「低權限 caller → accepted gate → User-0 Fire/HOME/package-state sink」閉合鏈。
- Parent/Profile Owner（`com.amazon.parentalcontrols`）的 inspected DPM/manifest/source path 沒有 arbitrary Fire/HOME relay；DPM persistent-preferred path 另受 active-admin/profile-owner 與 PMS system-UID gate。`setUserSetupComplete` tx4 的 ordinary-app identity clear 只落到 fixed setup settings，沒有 package/HOME sink。

判定：**KFT tx3 static sink = CONFIRMED/strong bounded；低權限 caller 通往目標 package-state sink = SAVED-ROUTE DISPROVEN for tested User 0/User 10 paths；完整 inherited authorization/runtime caller universe = UNKNOWN**。

### 3. shell／ordinary app 可達 Amazon 私有 Binder interface 與 identity relay

- Amazon private services 的 publication、AIDL、Proxy/Stub 在 host corpus 中存在；service name 出現不等於 shell 可取得 handle。
- 保存 shell UID 2000 enforcing SELinux/service-manager evidence 顯示對 Amazon private service 的 `find` 被拒；因此沒有 shell → private Binder → sink 的已證明 caller chain。未執行任何 service call。
- Ordinary APK 可達 `IAmazonUserManager` descriptor/tx3，且既有測試進入 service；但下游 PMS gates 阻止 User 10/User 0 package-state mutation。這不是 caller identity relay 的證明。
- 保存 corpus 中確有 `clearCallingIdentity`／`restoreCallingIdentity`，例如 KFT 後續 DPM path 與 tx4 setup-settings path；沒有證據顯示它們把 caller-controlled package/component/user data relay 到 User-0 HOME/package-state sink。對 ADD_RM metadata mutators，bounded service block 也沒有 relevant clear/restore identity edge。

判定：**Amazon private Binder interface 存在 = CONFIRMED；shell 可達目標 sink = NOT PROVEN／bounded blocked；ordinary app identity relay 到目標 package-state/HOME sink = NOT FOUND in preserved corpus；任何未保存 alias/runtime caller = UNKNOWN**。

## CSV 對應與分類規則

 companion CSV 以 row-level evidence 記錄 source path、source SHA-256、分類、confidence 與 exact line/range。`UNKNOWN` 僅表示本地 bounded corpus 未閉合，沒有填入推測性 declaration、holder、UID 或 caller。

主要 source hashes：

| source | SHA-256 |
|---|---|
| `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` |
| `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt` | `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed` |
| `artifacts/phase6mc-permission-holder-audit-20260810-05/permission-holders.csv` | `1f97fa825f8b7cd86f05653259ecf43359d496d15af4e21e0c53512274ebdb18` |
| `artifacts/phase6mx-amazon-pm-callers-20260810-01/caller-calls.csv` | `884b8636fd1baff3c1790cb4398e9cb83588dd68260643a4c660876c5269af82` |

安全邊界：不重播 tx3、tx1/2/4/5、private service call、component/package setter、HOME setter 或任何裝置操作。
