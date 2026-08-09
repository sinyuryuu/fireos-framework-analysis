# BootAfterSystemOTA / OOBE helper：user-scope data-flow host audit

日期：2026-08-10

## 範圍與安全界線

本報告只讀取保存的 PS7331 OOBE JADX/smali、services/fosservices disassembly、framework disassembly、manifest，以及既有 Phase 6MO、6NI、6R、6MY reports/evidence。未發送 broadcast、未啟動 OOBE、未修改 settings/package/user、未執行 OTA/recovery；本報告不提供 replay 指令。

## 結論

**靜態可證明的 sink scope：context/process-user-derived；不能靜態證明 numeric User 0。**

已閉合的資料流是：

```text
SystemServer.createSystemContext()
  -> ContextImpl.createSystemContext(..., UserHandle = null)
  -> ContextImpl.<init>: null => Process.myUserHandle() => mUser
  -> AmazonPackageManagerService.mContext
  -> onBootPhase(550) && PackageManagerService.isUpgrade()
  -> mContext.sendBroadcast(Intent, RECEIVE_BOOT_AFTER_SYSTEM_OTA)
  -> ContextImpl.sendBroadcast -> getUserId() -> IActivityManager.broadcastIntent(..., userId)
  -> ActivityThread.handleReceiver -> receiver ContextImpl / restricted Context
  -> BootAfterSystemOTAReceiver.onReceive(context, intent)
  -> PackageHelper.enableComponent(context, OobeHomeActivity.class)
  -> ApplicationPackageManager.setComponentEnabledSetting(..., ContextImpl.getUserId())
  -> IPackageManager/PMS component-state sink

  -> OOBEActivationHelper.activateOOBEIF(context)
  -> context.getContentResolver()
  -> SettingsDBUtils -> Settings.Secure.putInt(...)
```

因此，**不能由本 corpus 静态证明 `OobeHomeActivity` component sink 或 OOBE settings sink 的 numeric user 是 User 0**。保留结论：**Unknown（exact numeric delivery/sink user）**。`system-server process user`、通常所称的 `User0`、`current user` 与 `UserInfo`-derived user 不是同一个已证明事实。

## User identity 分层

| 层级 | 静态观察 | 判定 |
|---|---|---|
| system-server process user | `SystemServer.createSystemContext()` 取得 ActivityThread system context；其 ContextImpl 传入 null UserHandle，constructor 以 `Process.myUserHandle()` 填入 `mUser`。`Process.myUserHandle()` 是 `Process.myUid()` → `UserHandle.getUserId(uid)` → `UserHandle.of(id)`。 | **Confirmed / High**：来源是 process UID-derived，不是 OOBE 参数。 |
| sender Context user | `ContextImpl.sendBroadcast` 调 `ContextImpl.getUserId()`，再把结果放入 `IActivityManager.broadcastIntent` 的最後 userId 參數。 | **Confirmed / High**：broadcast user 取 sender Context。 |
| receiver/current user | `ActivityThread.handleReceiver` 由 `ReceiverData.info.applicationInfo` 建 application/base Context，傳 `getReceiverRestrictedContext()` 給 `onReceive`；app helper 未取得 `UserHandle.CURRENT`、`USER_SYSTEM`、`USER_ALL`，也沒有 current-user API。 | **Confirmed / High**：receiver 操作沿 delivered Context；**numeric current user Unknown**。 |
| User 0 | 選定 sender、receiver、helper、framework client callsite 沒有 `const/USER_SYSTEM/0` 作為 OOBE user argument；沒有將 `UserInfo.id` 帶入本流程。 | **Unknown / High**：不能把 system process user 推論升格成 numeric User 0。 |
| UserInfo-derived user | 本路徑沒有 `UserInfo` 參數或 `UserInfo.id` 讀取；這與 KFT/child lifecycle 的明確 UserInfo-derived 路徑不同。 | **Not observed / bounded negative**：不是本 OOBE helper 的已證明來源。 |

## 精確證據鏈

| Evidence ID | 精確位置（offset/line） | 觀察 | 信心 |
|---|---|---|---|
| 6NI-OOBE-001 | `decompiled/baksmali/vdexExtractor/services/disassembly.log:107206-107220`；SHA-256 `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53` | `SystemServer.createSystemContext()` 呼叫 `ActivityThread.systemMain()` / `getSystemContext()`，保存 system context。 | Confirmed / High |
| 6NI-OOBE-002 | `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log:449576-449604`；SHA-256 `5ef6a8c6edea903e3bf7e5298be02041dc46be06881438457e79cbf8501b76df` | `ContextImpl.createSystemContext()` new `ContextImpl` 時 UserHandle 參數為 null。 | Confirmed / High |
| 6NI-OOBE-003 | 同檔 `:449212-449262` | constructor 在 null user 時呼叫 `Process.myUserHandle()`，寫入 `ContextImpl.mUser`。 | Confirmed / High |
| 6NI-OOBE-004 | 同檔 `:1182027-1182037`（實際 smali offset `79ecf8-79ed10`） | `myUserHandle()` 由 `myUid()` 經 `UserHandle.getUserId()` 建立；不是常數 0。 | Confirmed / High |
| 6NI-OOBE-005 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96045-96061`；SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | `AmazonPackageManagerService.<init>(Context)` 將傳入 system-server Context 保存為 `mContext`。 | Confirmed / High |
| 6MO-E01 / 6NI-OOBE-006 | 同檔 `:96087-96126` | `onBootPhase(550)`、PMS `isUpgrade()` 後，使用 `mContext.sendBroadcast(intent, "com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA")`；不是 `sendBroadcastAsUser`。 | Confirmed / High |
| 6MO-E02 | `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log:452691-452721` | `ContextImpl.sendBroadcast` 將 `getUserId()` 結果傳入 `IActivityManager.broadcastIntent` 的 userId。 | Confirmed / High |
| 6MO-E03 | 同檔 `:435176-435236` | `ActivityThread.handleReceiver` 建立 receiver application/base Context，並用 receiver-restricted Context 呼叫 `onReceive`。 | Confirmed / High |
| 6MO-E05 | 同檔 `:449092-449185,452137-452150` | `ContentResolver` / provider acquisition 的 user resolution 取自 ContextImpl user。 | Strong / High |
| 6MY-001 / 6MO-E07 | `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:27-46,56-61`；SHA-256 `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90` | receiver guard 後呼叫 `PackageHelper.enableComponent(context, OobeHomeActivity.class)` 與 `OOBEActivationHelper.activateOOBEIF(context)`；catch path 只 disable receiver 自身。 | Confirmed / High |
| 6R-OOBE-007 / 6MO-E09 | `.../sources/com/amazon/oobe/commons/utils/PackageHelper.java:11-22`；SHA-256 `900f2dd69d349b3b4718b7f988b7d5bd153af2e2cb3c1586600e5b048e760ad8` | `enableComponent` 使用 supplied Context 的 PackageManager，state=1、flags=1；沒有 user argument。 | Confirmed / High |
| PM-CTX-001 | `decompiled/baksmali/vdexExtractor/boot-framework-dis/disassembly.log:451863-451888` | `ContextImpl.getPackageManager()` 建立 `ApplicationPackageManager(ContextImpl, IPackageManager)`，保留該 Context。 | Confirmed / High |
| PM-USER-001 | 同檔 `:445955-445963`（smali offset `01ddee-01ddfe`） | `ApplicationPackageManager.setComponentEnabledSetting` 從 `mContext` 呼叫 `getUserId()`，把 numeric user 傳到 `IPackageManager.setComponentEnabledSetting(ComponentName,state,flags,userId)`。 | Confirmed / High |
| 6MO-E08 / 6R-OOBE-006 | `.../sources/com/amazon/kindle/otter/oobe/commons/OOBEActivationHelper.java:29-34,53-56`；SHA-256 `6ebcb7eef7a03459a76b9c21cd59b61a30947f2b00a5624a4646825b8e3223d2` | IF path 以同一 Context 的 ContentResolver 寫 `user_setup_complete=0`、`isOOBEActive=1`；讀取 provisioning state 也用同一 Context resolver。 | Confirmed / High |
| 6MG-OOBE-SETTINGS | `.../sources/com/amazon/oobe/commons/utils/SettingsDBUtils.java:51-64`；SHA-256 `6ceb23853939c6905bf2de12a6969e7568a3bf2119588a6c1d4347f4ba089b31` | `FG` helper 只接受 ContentResolver/key/value，呼叫 `Settings.Secure/Global.put*`；沒有 `ForUser` 或 numeric user 參數。`FG` 是名稱，不是 User 0 證據。 | Confirmed / High |
| 6R-OOBE-003 | `artifacts/phase6j/ota-oobe-manifest-audit-20260805-01/manifest.txt:279-283,531-541`；SHA-256 `bcc51d83ee74bbc230b774a52684e3e4cdb5cbc6cff7be673e6e3979037275ff` | OOBE requests custom OTA permission；receiver enabled/directBootAware，intent filter matches action，未在 receiver manifest entry 設 receiver permission。 | Confirmed / High |

## Sink 與 HOME 邊界

`PackageHelper` 的 component sink 是 OOBE package/component state writer；`OOBEActivationHelper` 是 setup/provisioning settings writer。四個選定 OOBE source（receiver、activation helper、PackageHelper、SettingsDBUtils）沒有 `setHomeActivity`、`addPreferredActivity`、`replacePreferredActivity` 或 `com.amazon.firelauncher` reference。故可作 **bounded negative / Strong**：本 corpus 沒有證明它是 ordinary Fire Launcher HOME/preferred writer；不能外推成 binary-wide absence。

這也不能把 `OobeHomeActivity` 的 component enable 等同於 User-0 sink：component API 的 userId 確實來自 receiver Context，但該 Context 的 numeric user 仍只追到 sender process UID-derived `mUser`，而非 source-level User 0 常數、`UserHandle.CURRENT` 或 `UserInfo.id`。

## 最終判定

| 問題 | 判定 | 理由 |
|---|---|---|
| 是否能靜態證明 system-server process user-derived flow？ | **可以，Confirmed / High** | system context → null UserHandle → `Process.myUserHandle()` → `mUser` → sender/receiver/helper。 |
| 是否能靜態證明 `ContentResolver` 與 PackageManager component sink 沿同一 user scope？ | **可以，Confirmed / High** | framework `ContentResolver` user resolution 與 `ApplicationPackageManager.setComponentEnabledSetting` 都取 `ContextImpl.getUserId()`。 |
| 是否能靜態證明 sink 是 numeric User 0？ | **不能；Unknown / High** | 缺少 numeric User 0 常數或明確 `sendBroadcastAsUser(..., UserHandle.SYSTEM/0)`；process UID-derived user 不等於已證成的 User 0。 |
| 是否是 current-user 或 UserInfo-derived flow？ | **不能如此分類；Unknown / bounded negative** | 本路徑沒有 current-user selector 或 `UserInfo.id`；只可說 receiver Context-derived。 |
| 是否是 ordinary Fire Launcher HOME writer？ | **未證明；bounded negative / Strong** | OOBE source 未見 HOME/preferred writer 或 Fire Launcher reference。 |

## 既有報告交叉引用

- Phase 6MO：`findings/phase-6mo-oobe-context-user-scope.md`，SHA-256 `e962ba889cd93df672c9827a8411bdee6bc6c2bb2b75b7d2e5bf799002dc95d2`；其 6MO-E01–E10 保留 Context→broadcast→receiver→sink 證據，並將 exact user 留為待驗證。
- Phase 6NI：`findings/phase-6ni-oobe-system-context-scope.md`；其 6NI-OOBE-001–007 建立 system context 與 process-user-derived chain，未將通常 system user 推論升格為 numeric User 0。
- Phase 6R：`findings/phase-6r-evidence-index.md`，SHA-256 `fc51d7b8fe40f7c5eb8f89f40ef0bfe187f02b64637fdcc07168f7443e295b6c`；6R-OOBE-001–010 建立 protected OTA/OOBE lifecycle 與 side effects。
- Phase 6MY：`findings/phase-6my-ota-receiver-package-helper-closure.md`，SHA-256 `3977b4cef2d000c3b598b1d582719374ef8cb230055fcec6e98b36e0db4e15bb`；6MY-001 建立 receiver→PackageHelper→OobeHomeActivity bounded static path，並保留 exact numeric user Unknown。
