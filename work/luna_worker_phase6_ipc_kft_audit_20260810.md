# Phase 6 IPC/KFT 靜態稽核（2026-08-10）

## 範圍與判讀

本報告只讀既有本機 decompiled/JADX、findings、output tables/call-graphs 與已保存 ADB 原始證據；本輪未連接或修改設備，未執行 `service call`、未知 Binder transaction、root/提權 exploit，也未重做 priority、set-home-activity、Fire Launcher disable 或 KFT tx3 動態測試。既有動態結果僅作引用。

分類：`Confirmed` = 直接由靜態或保存結果證明；`Strong evidence` = 多個保存 artifact 一致支持但仍有 bounded scope；`Probable` = 有合理 data-flow 但存在未閉合分支；`Hypothesis` = 尚未由 artifact 證明的候選；`Disproved` = 既有證據與該狹義主張不相容；`Unknown` = 保存 corpus 無法判定。

## Executive conclusion

1. **Confirmed：** `IAmazonUserManager` 的 tx3 `enableKftLauncher(UserInfo)` 是唯一已保存、同時連到 Tahoe、Fire Launcher、Launcher3 package/component state sink 的 Amazon launcher writer。writer 使用傳入 `UserInfo.id`，不是硬編碼 User 0；既有 child lifecycle caller 與 User 10 runtime attribution 均支持 child/profile scope。
2. **Confirmed / Strong evidence：** tx3 AIDL/Stub 只可在 bounded recovered branch 中確認 `enforceInterface()`；未見 tx3 method-local `getCallingUid()`、`enforceCallingPermission()` 或 `enforceCallingOrSelfPermission()`。這是靜態 authorization gap，不能單獨升格為漏洞。普通 APK 的既有 6FJ/6FK 結果顯示可進入 tx3，但下游 PMS 仍拒絕 User 10 cross-user 與 User 0 component-state write。
3. **Confirmed：** Amazon private Binder services（package/activity/window/user manager 等）在 system-server/fosinit inventory 中有 publication 與 AIDL/Stub；服務名稱出現在 `service list` 不等於 shell 可取得 handle。既有 shell evidence 顯示 service-manager `find` 被 enforcing SELinux 擋住；不把 service name 當成可呼叫 route。
4. **Confirmed / Disproved（狹義主張）：** Amazon Package Manager private AIDL tx1–tx11 是 metadata/flags/proxy/query contract；reviewed contract 沒有 formal HOME、preferred-activity 或 package/component state setter。其 facade setter 會回到標準 PMS tx90/tx92，仍受 PMS caller/permission/protected-package gates。這不支持「private Amazon PM 可直接取代 User 0 HOME」。
5. **Confirmed / Disproved（狹義主張）：** User 0 `com.amazon.parentalcontrols` 是 Profile Owner（UID 10058），但其 inspected exported/receiver/provider/service surfaces 沒有 arbitrary Fire/HOME relay；Fire literal 在 restriction policy，不是 hidden/enabled 或 preferred-HOME sink。DPM tx100→PMS tx73 仍有 owner/admin 與 PMS UID gates。
6. **Unknown：** tx3 完整 inherited/generated authorization mapping、保存 corpus 外 runtime-loaded/private Amazon caller universe、OOBE helper 的 Context→實際 user mapping，以及所有 private service alias 的全映像完整性，仍沒有足夠證據。

## 1. Private Amazon Binder service / AIDL / Stub inventory

| Service / contract | 靜態 publication / AIDL / Stub 證據 | caller / permission 證據 | sink / scope 結論 |
|---|---|---|---|
| `AmazonUserManagerService` / `amazon.os.IAmazonUserManager` | `boot-fosframework/disassembly.log:370378-370428`：Proxy；`370637-370750`：Stub/onTransact；`fosservices/disassembly.log:55106-55118`：publish；client name `boot-fosframework/disassembly.log:369085-369095` | Stub 讀 nullable `UserInfo`、`enforceInterface`、dispatch tx3；`fosservices:54415-54440` 未見 tx3 local UID/permission check；general `checkManageUsersPermission()` 在 `54851-54875`，但未證明由 tx3 entry 呼叫 | tx3 為 supplied-user KFT writer；`Confirmed` sink/scope，`Unknown` tx3 local authorization；既有 6FH 普通 APK handle reachability 與 6FJ/6FK downstream rejection 見下節 |
| `AmazonPackageManagerService` / `IAmazonPackageManager` | interface `boot-fosframework/disassembly.log:58322-58352`；Proxy `402937-403367`；Stub `403368-403602`；publication `fosservices:95866-96036,96081-96086,96128-96137` | tx1/2/4/5 metadata mutators 檢查 `amazon.permission.ADD_RM_PKG_METADATA`：`fosservices:95955-96025`；selected service shell `find` denied | tx1–11 metadata/flags/proxy/query；沒有 formal HOME/package-state setter；facade setters delegate standard PMS tx90/tx92；`Confirmed` |
| `AmazonActivityManagerService` / `IAmazonActivityManager` | publication `fosservices/disassembly.log:39645-39655,40954-40959,41075-41084`；method signals 在 `artifacts/phase6j/.../method-signals.csv` | selected methods有 `APP_PREWARM`、`SEND_DATA_TO_ALEXA` 等 caller/target markers；完整 caller gate 以 method row 為準 | process/task/prewarm，不是 HOME/package writer；`Strong evidence` |
| `AmazonWindowManagerService` / `IAmazonWindowManager` | interface `boot-fosframework/disassembly.log:56535-56554`；Proxy `400032-400218`；service implementation `fosservices:56070-56244` | wrapper 鄰近視窗未見 permission marker，不能推論無授權；service-manager/SELinux boundary 仍適用 | PIP/window/lock/overscan surface，未見 HOME selector；`Confirmed` bounded negative |
| `AmazonProfileService` | service matrix `output/tables/phase6q-binder-service-matrix.csv`；`findings/phase-6mn-ipc-user-scope-closure.md:172-180` | `PROFILE_INTERACTION` 對 initiate path；private service，未建立 shell caller chain | profile picker/lifecycle explicit launch，非 formal HOME writer；`Strong evidence` |
| OTA/OOBE receiver path | `AmazonPackageManagerService.onBootPhase(550)`→protected `BOOT_AFTER_SYSTEM_OTA`→`BootAfterSystemOTAReceiver`→OOBE helper，`findings/phase-6mn-ipc-user-scope-closure.md:123-150` | broadcast 需 protected/signature permission；manual trigger 已因風險拒絕 | context-bound setup/component state；無 explicit `ForUser`，不能證成 User 0；`Strong evidence` route、`Unknown` exact user mapping |

主要靜態檔案 SHA-256：`boot-fosframework/disassembly.log` `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`；`fosservices/disassembly.log` `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`；`boot-framework-dis/disassembly.log` `5ef6a8c6edea903e3bf7e5298be02041dc46be06881438457e79cbf8501b76df`。既有 contract table：`output/tables/phase6l-binder-contract-summary.csv`、`output/tables/phase6q-binder-service-matrix.csv`。

## 2. KFT tx3：AIDL、caller provenance、identity 與 writer

### 2.1 AIDL/Stub/transaction

- Proxy `IAmazonUserManager.Stub.Proxy.enableKftLauncher(UserInfo)` 在 `boot-fosframework/disassembly.log:370378-370428`：寫 descriptor `amazon.os.IAmazonUserManager`、nullable `UserInfo` parcel，`IBinder.transact(3,...)`。
- Stub 在 `:370637-370750`：attach descriptor、`enforceInterface`、讀 `UserInfo.CREATOR`、tx3 dispatch、回傳 boolean。結果：**Confirmed tx3 contract**。
- `UserInfo` Android 9 parcel field order 來自 `boot-framework-dis/disassembly.log:562771-562801`；不是猜測 parcel。

### 2.2 唯一保存 static caller 與 child gate

`AmazonUserManagerImpl.createChildUser(String)` 在 `boot-fosframework/disassembly.log:369180-369255`：以 `createUser(name, 0x8000)` 建 child，成功後把同一 `UserInfo` 傳給 `enableKftLauncher(UserInfo)`（`369203-369217`），再呼叫 setup-complete。保存 corpus 的 reference scan 只找到這個 tx3 semantic caller：`work/luna_worker_kft_ipc_provenance_20260810.md:19-28`。這支持 **Strong evidence：trusted Amazon child-creation lifecycle caller**，但不能宣稱所有 runtime-loaded/private caller 已全部封閉。

system-server child predicate：`AmazonUserInfo.isChild()` flags `0x8000`/`0x8` 在 `boot-fosframework/disassembly.log:11682-11693`；wrapper `fosservices:54166-54174`；boot upgrade branch `fosservices:55053-55104` 只在 child branch 進入 KFT writer。此為 **Confirmed child gate**。

### 2.3 `UserInfo.id` 到 PackageManager state writer

`AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)`：`fosservices/disassembly.log:54297-54325`。

1. Tahoe `com.amazon.tahoe/.launcher.FreeTimeLauncherActivity`：`setComponentEnabledSetting(..., userId)`，userId 由 `UserInfo.id` 導入。
2. `com.amazon.firelauncher`：`setApplicationEnabledSetting(..., newState=2, ..., UserInfo.id)`。
3. `com.android.launcher3`：同樣 state 2，仍使用 `UserInfo.id`。

沒有 hard-coded user 0，亦沒有 `setHomeActivity`、`replacePreferredActivity`、`addPersistentPreferredActivity` 或 Role/HOME setter。故 **Confirmed：child/profile supplied-user package/component writer；Disproved（狹義）：KFT tx3 本身是 unconditional User 0 HOME selector**。

### 2.4 caller identity / permission / clear-restore

`fosservices:54415-54440` 的 tx3 bounded entry 未見 `Binder.getCallingUid()`、`checkCallingPermission`、`checkCallingOrSelfPermission` 或 `clearCallingIdentity`。`clearCallingIdentity` 出現在同方法後續 DPM/KFT path（`54415-54478`），並有 restore；不是證明 tx3 package writes 會以 system UID 執行。general `checkManageUsersPermission(String)`（`54851-54875`）放行 UID 0/1000 或要求 `MANAGE_USERS`，但保存 slice 沒有 tx3→helper edge。

結論：**Unknown：tx3 method-local / inherited authorization 完整閉合**；**Confirmed：general service helper 存在**；**Strong evidence：實際 shell/private-service boundary 阻止 shell 取得 handle**。不把「Stub 缺少可見 UID check」寫成「已證明可利用」。

### 2.5 Existing test IDs（只引用，不重做）

| Test ID / finding | 已保存結果 | 稽核判讀 |
|---|---|---|
| `F-6FH-01` / Phase 6FH | ordinary APK UID 10210、無 manifest permission，可取得 `amazonusermanagerservice` handle、descriptor `amazon.os.IAmazonUserManager`；未發 tx3。finding hash `findings/phase-6fh-amazon-user-manager-interface-boundary.md`（本輪未重算其原始 capture） | **Confirmed reachability only**；不能推出 tx3 authorization |
| `F-6FJ-01` / Phase 6FJ | ordinary UID 10212 tx3，target User 10 (`id=10`, flags `0x8010`, serial 13)，PMS 回 `INTERACT_ACROSS_USERS`，無 User 10 mutation；evidence manifest hash `adb/phase6fj/.../sha256sums.txt` = `4c3ae4ee0e58ddb4bdf6d2d0a637d1655bbb17cb61b1c6c4c9c4d0be01275e3f` | **Confirmed downstream gate；User 10 scope** |
| `F-6FK-01` / Phase 6FK | ordinary UID 10213 tx3，child-flag payload target User 0，PMS 回 `Attempt to change component state`，無 Tahoe/Fire/HOME mutation；manifest hash `adb/phase6fk/.../sha256sums.txt` = `28a5eaca012236e23c5b8af8314b6d7036c70af808a011d48c85eb8f1c18c408` | **Confirmed same-user PMS gate；不等於 User 0 writer** |
| `PHASE6EC-KFT-TX3-20260806-02` | shell lookup `amazonusermanagerservice: not found`、`dispatch_attempted=false`、`binder_transaction_sent=false`；manifest hash `3f509b00dffa484c088f43814e124af83caabd8aad7bfa8b3555ba32d6dcbe55` | **Confirmed shell reachability boundary；未執行 tx3 dispatch** |
| `PHASE6CZ-KFT-PROVENANCE-20260806-01` | read-only SELinux capture，shell UID 2000 / `u:r:shell:s0` / enforcing / AVC `find` denied；finding hash `8880cb4592c38c2f9f7b5cc65979e2d470d1ea1c2fa95690aaf4755147ca3403` | **Strong evidence service-manager boundary** |

## 3. PackageManager state writer chain與 User 0 / child scope

### 3.1 Standard PMS boundary

既有 `findings/phase-6j-ipc-deep-review.md:86-109,136-190` 證明 selected protected-package callback 會讀 `PackageManagerDenyList`、判斷 system app/deny-list、比較 calling UID 2000；shell service-manager `find` 對 Amazon service 被 SELinux deny。標準 framework transaction mapping（既有 `findings/phase-6ep-amazon-writer-reachability.md:71-86`）：tx89 `setHomeActivity`、tx90 `setComponentEnabledSetting`、tx92 `setApplicationEnabledSetting`、tx73 persistent preferred、tx81 restore preferred。

**Confirmed：** PMS 是實際 package/component/HOME state gate；Amazon facade/private contract 不是自動繞過。**Strong evidence：** selected indexed corpus 沒有新的 Amazon `setHomeActivity`/preferred-HOME writer（`findings/phase-6mn-ipc-user-scope-closure.md:152-170`）。

### 3.2 User 0

User 0 Fire HOME 的既有 baseline 是 `com.amazon.firelauncher/.Launcher` priority 50。KFT tx3 static sink 沒有常數 0；6FK supplied id=0 的 ordinary caller 在 PMS component gate 被拒絕，不能把「target 可填 0」誤寫成「User 0 可寫」。Parental Controls Profile Owner 亦維持 Fire HOME，見 `POLICY-T02` 與 6GA/6HW。故 **Confirmed：目前保存證據沒有 ordinary/private IPC 的 User 0 Fire HOME writer**；對未保存 runtime caller universe 仍為 **Unknown**。

### 3.3 Child/profile user

KFT intended lifecycle 使用新建 child `UserInfo`（flags `0x8000`），writer 以其 id 對 Tahoe/Fire/Launcher3 設置 child-local state。既有 child runtime attribution（`findings/phase-6er-kft-child-switch-attribution.md`、`PHASE6GP-CHILD-HOME-SWITCH-20260807-01`）觀察 User 10 Tahoe HOME、回 User 0 後 Fire priority/state unchanged。這是 **Confirmed/Strong evidence：child-local KFT effect，不是 User 0 restoration watchdog**。

## 4. ParentalControlService / User 0 Profile Owner

此名稱在保存 artifacts 中主要以 Parental Controls APK 的 `ParentalPolicyIntentService`、`ParentalAdminReceiver`、DPM path 呈現；未發現該 APK 自行 publish 一個可供普通 caller 呼叫的 Amazon private `onTransact` service。

### Static manifest / source

- Manifest `decompiled/jadx/parentalcontrols/resources/AndroidManifest.xml:296-424`：`ParentalAdminReceiver` 使用 `BIND_DEVICE_ADMIN`；policy service `exported=false`/`BIND_JOB_SERVICE`；protected receivers 使用 `com.amazon.permission.ParentalControl` (`signature|privileged`)；package-change receiver disabled by default；source SHA `276321f2246d5dce471e6e37b44aa3db920d032b3ed4e992cba7a6ad16afbd50`。
- `ParentalAdminUtils.java:99-114,488-528`：DPM `setApplicationHidden` / selected package list processing；SHA `317389e670d500c709445a9eac51af8f09cb56277a60a8aa910f69c907f516aa`。
- `PackageChangesReceiver.java:31-52,74-78`：`is3PApp()` filter，component writer 只切自身 receiver；SHA `66360ae060acbd0c09b028ab03de80cfc4a3d1d48025bbdf034f5c86f62d09f7`。
- `PolicyPrefMap.java:23-67` / `PolicyAppRestriction.java:39`：Fire Launcher literal 是 restriction target，不是 `PolicyAppHidden` 或 HOME target；`PolicyAppRestriction.java` SHA `5028a004bde72bf5ef4e7e2c5b7c6bd68f37f11be1e7819b639bae9093311106`。
- Framework DPM/PMS sink：`decompiled/jadx/ota-PS7331/systemui/sources/com/android/server/devicepolicy/DevicePolicyManagerService.java:6742-6761,7914-7932`；PMS `:13345-13361`。Owner/admin check 後才 clear identity，再 delegate PMS；不是 Parental APK 自帶 HOME writer。

### Caller identity / permission / scope

`findings/phase-6bu-parental-owner-reachability-closure.md:95-123`：effective Profile Owner UID 10058；shell UID 2000 只有 read-only inspection，不能繼承 UID 10058。無 APK `onTransact()`、private Amazon transaction 或 caller-controlled package extra 到 `processApps`。`findings/phase-6hw-parental-owner-home-boundary.md:112-127`：`clearCallingIdentity` 只在 DPM hidden-app path 的 admin check 後，用於 selected third-party content，不接受 caller-selected HOME component。

`PHASE6GA-PARENTAL-OWNER-HOME-RO-20260807-01` 是 read-only User 0 owner/HOME/package capture，manifest hash `63b3d260b19d8715dad232ff918ab3ee878b20b8dc958a315fa1f69971f5c8aa`；既有 `POLICY-T02` read-only manifest hash `a0404740fe15e7e05832c39848e799c1ccd9c035ec455db843a076f62bbc0d5c`。

結論：**Confirmed：User 0 Profile Owner / DPM boundary**；**Disproved（狹義）：Parental Controls 是 User 0 Fire/HOME relay**；**Strong evidence：Fire restriction policy 與 hidden/package/HOME sinks 分離**。

## 5. Cross-route status matrix

| 命題 | 結論 | 證據 |
|---|---|---|
| Amazon private services 在 system-server 發布 | **Confirmed** | Phase 6J lines 36-74, 111-134；`phase6q-binder-service-matrix.csv` |
| shell 可因 service-list 名稱直接呼叫 private service | **Disproved** | Phase 6J lines 136-158；6EC/6CZ SELinux evidence |
| ordinary APK 可 query User Manager descriptor | **Confirmed** | `F-6FH-01` / Phase 6FH lines 17-35, 74-84 |
| tx3 只有 interface token、無可見 local UID/permission check | **Confirmed（bounded recovered slice）** | 6CZ lines 95-104；6FI–FK lines 35-45, 114-127 |
| tx3 ordinary caller 能修改 User 10 | **Disproved** | `F-6FJ-01`：PMS `INTERACT_ACROSS_USERS` |
| tx3 ordinary caller 能修改 User 0 | **Disproved** | `F-6FK-01`：PMS component-state caller gate |
| KFT writer 使用 User 0 固定 scope | **Disproved** | `fosservices:54297-54325` 全部 sink 使用 `UserInfo.id` |
| KFT 是 child/profile trusted writer | **Confirmed** | child flags/predicate + createChildUser + writer chain |
| Amazon PM private tx1–11 是 formal HOME/package setter | **Disproved** | 6J lines 36-84；6IA lines 36-111 |
| Parental Controls Profile Owner 可 relay arbitrary Fire/HOME write | **Disproved（inspected PS7331 scope）** | 6GA lines 38-98；6HW lines 112-127；6BU lines 95-142 |
| OOBE helper 明確寫 User 0 | **Unknown** | 6MN lines 123-150；無 `ForUser` / explicit user id |
| preserved corpus 已封閉所有 private/runtime caller | **Unknown** | 6MN lines 239-250；corpus completeness gap |

## 6. Evidence gaps / 不得外推

1. **tx3 authorization inheritance gap（Unknown）：** 尚缺完整 generated Stub、service superclass/interface implementation 及 method-level caller mapping，不能由「未見 check」推出無 authorization，也不能因 ordinary APK 6FH handle reachability 直接推出 tx3 可利用。
2. **Caller-universe gap（Unknown）：** `createChildUser` 是保存 corpus 唯一 static tx3 caller，但未證明不存在保存範圍外 runtime-loaded/private client、alias 或 system component。
3. **OOBE user mapping gap（Unknown）：** helper 的 `Context`/`ContentResolver`/PackageManager handle 未閉合到 User 0/current user；不以 method suffix 或 broadcast 名稱推定 User 0。
4. **PMS parent callback gap（Unknown）：** protected-package callback 的完整 interface/initialization data-flow 與 deny-list writer provenance 尚未完全保存；既有 gate evidence 不授權讀寫 deny-list。
5. **No new dynamic proof requested：** 不重做 tx3、child switch/unlock/PIN、普通 PMS setter、HOME priority、Fire disable 或 private `service call`；這些操作要麼已有既有 Test ID closure，要麼會改變 package/user state。

## Final disposition

在目前保存 PS7331 corpus 內，最強可採用結論是：**KFT tx3 是 confirmed child/profile-scoped trusted package/component writer；PMS caller/protected-package gates 阻止既有 ordinary User 0/User 10 tx3 mutation；Amazon private PM contract 沒有 formal HOME setter；User 0 Parental Controls Profile Owner 沒有 arbitrary Fire/HOME relay。** User 0 writer、tx3 完整 inherited authorization、OOBE exact user mapping 仍分別標為 `Strong evidence negative within preserved scope` 或 `Unknown`，不應升格為全映像不存在或漏洞。
