# Phase 6BB：AmazonActivityManager prewarm 呼叫者閉合

## 範圍與安全邊界

本階段是 **host-only** 靜態分析。輸入為 PS7331 的 FOS／boot-framework／OTA
VDEX disassembly、`fosinit` 註冊資料，以及已保存的 Alexa JADX source。沒有連接
裝置、沒有呼叫 Binder、沒有發起 process、沒有變更 package/settings，也沒有嘗試
root 或 HOME 替換。

Phase 6AY 已確認 KFT 路徑的靜態程式碼包含對 Fire Launcher 的停用動作；該路徑
仍不在本階段執行範圍內。

## 結論

| Finding | 判定 |
|---|---|
| `AmazonActivityManagerService.BinderService.preWarmApplicationForUser(String,int,int)` 存在於 FOS 與 PS7331 OTA VDEX | **已證實（Confirmed static）** |
| Framework proxy 以 descriptor `com.amazon.android.server.am.IAmazonActivityManager`、transaction `1` 傳送三個參數 | **已證實** |
| `amazonactivitymanager` 由 `AmazonActivityManagerService` 註冊，Framework manager 由 `AmazonActivityManagerImpl` 取得 | **已證實** |
| 保存的 Alexa source scope 中只有一個直接 caller，位於 `ExplicitIntentAction.prewarmApplicationProcess` | **高可信推論（Strong evidence；scope-limited）** |
| server method 讀取 `APP_PREWARM`，但在觀察到的指令區段中沒有消費 permission result，隨後清除 Binder identity | **高可信靜態異常候選；不是漏洞證明** |
| shell／一般 sideloaded app 可以安全呼叫此介面 | **未證實；目前證據反而不支持** |
| 此介面可改變 HOME resolver、Home key 或取得 root | **已排除於目前證據範圍** |

## 方法與呼叫鏈

```text
Alexa ExplicitIntentAction.prewarmApplicationProcess(target)
  → AmazonActivityManagerImpl.preWarmApplicationForUser(...)
  → IAmazonActivityManager.Stub.Proxy
  → Binder transaction 1
  → AmazonActivityManagerService.BinderService
  → checkCallingPermission(APP_PREWARM)
  → clearCallingIdentity()
  → IPackageManager.getApplicationInfo(target, flags=1024, user)
  → PreWarmCacheHelper.getKeepIfLargeValue(target)
  → ActivityManagerService.startProcessLocked(..., "prewarm", ...)
```

上述鏈中的每一段都只代表保存 artifact 的靜態對應；沒有宣稱在本機實際走過
Binder transaction。

## 關鍵證據

### Server method

FOS VDEX 的 `preWarmApplicationForUser` 位於
`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534`。
指令顯示：

1. 建立 trace label `preWarmApplication`。
2. 呼叫 `Context.checkCallingPermission("com.amazon.permission.APP_PREWARM")`。
3. 緊接呼叫 `Binder.clearCallingIdentity()`；在兩者之間未觀察到
   `move-result` 或拒絕分支。
4. 查詢 `ApplicationInfo`，再以 reason `prewarm` 呼叫
   `SystemJumpTable$ActivityManagerService.startProcessLocked`。
5. 最後恢復 calling identity 並回傳結果。

PS7331 OTA VDEX 對應區段為
`decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3642543-3642624`，
保留相同的控制流語意。

這只能支持「授權檢查可能未被方法內部真正 enforce」的靜態觀察。ServiceManager
可見性、SELinux、Binder service publication、呼叫者簽章與上游 caller filter
仍是獨立邊界；因此不能把它升格為可利用權限繞過。

### Proxy and registration

Framework VDEX 的 proxy 位於
`decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:394721-394751`：
它寫入 interface token、String 與兩個 int，設定 transaction code `1`，讀取 int
回傳值。PS7331 OTA proxy 對應區段為
`decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:4464666-4464696`。

`AmazonActivityManagerImpl` 在
`boot-fosframework/disassembly.log:553433-553446` 委派至介面；其初始化在
同一 VDEX 的 `553272-553277` 以 `ServiceManager.getService("amazonactivitymanager")`
取得 Binder。

`artifacts/amazon-services/amazonactivitymanager_fosinit.xml:8-28` 將
`AmazonActivityManagerService` 列為 vendor service，並把 `activity` manager
綁到 `amazon.app.AmazonActivityManagerImpl`。

### Saved caller

`artifacts/phase6j/ota-alexa-system-ota-jadx-20260805-01/sources/amazon/speech/sim/router/intentrouter/ExplicitIntentAction.java:268-282`
顯示唯一保存的直接 caller：它排除自身 package，確認 manager 與 target 非空，
再以 `foregroundProfileId` 呼叫 prewarm，非零回傳值只記錄失敗。

同一 APK manifest 宣告 `com.amazon.permission.APP_PREWARM`；device package dump
顯示 Alexa 是 `/system/priv-app`、`PRIVILEGED`，且該權限已授予。Phase 6K 另記錄
target 會經 Alexa endpoint／`SEND_DATA_TO_ALEXA` 過濾。這些條件說明保存的 caller
是受信任 system path，不是普通 sideloaded app。

## HOME 與 root 判定

在 server method、proxy、wrapper 與保存 caller 中，沒有觀察到
`CATEGORY_HOME`、`ACTION_MAIN`、`resolveActivity`、`setHomeActivity`、
`setPreferredActivity` 或 Fire Launcher component。server 的敏感動作是啟動
process，不是啟動 activity 或寫入 preferred state。

因此目前最小判定為：

- **已證實靜態：** 這是 Amazon 私有的 process prewarm IPC surface。
- **高可信推論：** 它服務於 Alexa／system app 的 process warm-up，而非 HOME 選擇。
- **待驗證：** 是否存在未納入保存 Alexa source scope 的其他 Amazon caller。
- **已排除於本階段：** shell 直接呼叫、未知 transaction fuzz、由此介面取得 root、
  由此介面正式替換 HOME。

## 不執行的測試

下列操作明確拒絕，因為會對 private Binder 產生未知副作用或啟動任意 process：

- `service call amazonactivitymanager 1 ...`
- 猜測 parcel 格式、transaction code 或 user id。
- 讓 shell 或 sideloaded APK 嘗試取得 private Binder handle。
- KFT/OOBE lifecycle invocation。

下一個安全的研究方向若仍要追 caller，應只擴大已取得的 Amazon APK source／DEX
範圍，並維持 host-only；不應以實機 Binder invocation 取代靜態授權證據。
