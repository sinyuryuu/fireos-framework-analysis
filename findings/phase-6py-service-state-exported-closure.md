# Phase 6PY — service permission、package-state writer 與 exported sink closure

日期：2026-08-10
公開基準：`77c076b7624ce44f33a7107d7860db991ea57de1`
裝置 comparator：`G001LT0511550CFT` / `KFTRWI` / `trona` / `PS7331`

## Executive summary

本輪把三條仍可能被誤認為「拿到權限即可關閉 Fire Launcher」的路徑放入同一個
`caller → gate → identity → sink` closure：

1. Amazon 私有 service 的權限異常候選（ASP、prewarm、window/input、thermal、
   SmartSuspend、fosdebug）；
2. Fire/Tahoe package/component state 的實際 writer（KFT、PMS、DPM、Arcus、
   OOBE/OTA、PackageInstaller/Play metadata）；
3. 123 個 PS7331 `fosinit` XML 及 exported-component candidate 到 HOME、preferred、
   PackageManager、SettingsProvider、DevicePolicy 的 sink join。

**本輪最重要結論：** 沒有找到新的 ordinary-app／ADB-shell → User-0
PackageManager、HOME 或 UID 0/system sink 的閉合鏈。ASP tablet branch 與
`AmazonActivityManager.preWarmApplicationForUser` 是值得保留的**靜態授權異常候選**，
但現有證據只到 audio/process/resource effect；沒有證據能將它們轉成 Fire Launcher
state mutation、HOME replacement 或 root。未知 Binder transaction 沒有被猜測或重放。

PS7331 的 Fire Launcher protected membership 則已有前一輪的直接 host evidence：
`fireos-res.apk` 的 `raw/package_manager_deny_list.json` 明列
`com.amazon.firelauncher`。本輪的新矩陣確認：KFT writer 只在 child/profile
`UserInfo.id` 作用，並非 User 0 restoration writer；PMS protected gate 在 state
write 前拒絕；`fosinit`/exported surface 沒有新增普通 caller 到 HOME 或設定 writer 的路徑。

本輪 worker 與正規化腳本均為 host-only。沒有執行 Binder transaction、`service call`、
ioctl、package/settings mutation、user provisioning、reboot、OTA/recovery、Root、
exploit 或分割區操作。既有 Phase 6PW 的 PS7331 read-only capture 是 runtime comparator，
不是本輪新增的 mutation evidence。

## 判定摘要

| 問題 | 判定 | Evidence |
|---|---|---|
| Fire Launcher 如何進入 protected 集合？ | **已證實（Confirmed）**：PS7331 `fireos-res.apk` resource seed 直接列出 Fire；既有 PMS callback 將 deny-list membership 帶入 pre-write gate。live persisted file literal 未直接讀取。 | `PX-DENY-01`, `PX-DENY-02`, `PY-WRITER-01` |
| shell／ordinary app 是否取得新的 User-0 package/HOME writer？ | **未找到（Strong evidence）**；本輪 38-row closure 沒有閉合鏈。 | `PY-NORM-01`, `PY-FOS-01`, `PY-STATE-01` |
| KFT 是否能在可信 child lifecycle 內寫 Fire state？ | **已證實（Confirmed static）**：`enableKftLauncherComponent(UserInfo)` 可對 supplied child/profile user 寫 Tahoe/Fire/Launcher3 state；不是 User 0 路徑，shell reachability 仍被既有 gate 擋住。 | `PY-STATE-01`, `PY-STATE-02` |
| ASP tablet `hasCallerGotPermission()` 是否是可直接提權入口？ | **待驗證／僅靜態異常（Hypothesis）**：tablet branch 先 allow，但 service-manager lookup 與低權限 method reachability 未閉合，sink 也不是 HOME/package/root。 | `PY-SERVICE-01`, `PY-SERVICE-02` |
| `preWarmApplicationForUser` 的未消費 permission result 是否能取得 system 權限？ | **高可信推論（Probable bounded deputy）**：可解釋既有普通 APK process/resource effect；目前沒有 package/HOME/root sink。 | `PY-SERVICE-01`, `PY-SERVICE-02` |
| exported/fosinit inventory 是否存在新的 HOME writer？ | **已排除（Disproved within reviewed corpus）**：123 XML 與高影響 exported candidates 的 join 沒找到 qualifying sink；OTA/OOBE 例外是受保護 system lifecycle。 | `PY-FOS-01`, `PY-FOS-02` |
| 本輪是否有可安全實測的未知私有 Binder route？ | **因風險拒絕測試（Risk-rejected）**：沒有明確文件化、可驗證 transaction 與 rollback 的 route；不猜 code、不重放 payload。 | `PY-SERVICE-02`, `PY-FOS-02` |

## 1. Amazon service permission surface

### ASP / `AmazonAspService`

`hasCallerGotPermission()` 的 bounded disassembly 顯示 tablet device-family branch
在檢查 `com.amazon.permission.ASP_PERMISSION` 前回傳 allow；非 tablet branch 才走
permission check。command/capture/injection entry points 會呼叫該 helper，這是**靜態
permission anomaly candidate**，不是已證實的 shell-to-native invocation。

保存的 runtime boundary 只有 service-manager/dumpsys 層級可見性與 ASP dump header；
沒有執行 method invocation、audio injection 或 native command。既有 enforcing capture
中，shell UID 2000 對 private service 的 `find` 受 SELinux/service-manager policy
阻擋。即使 tablet branch 對某個合法 caller allow，現有 source join 也沒有連到
`setApplicationEnabledSetting`、preferred activity、HOME resolver 或 UID 0 sink。

**判定：** permission anomaly = **已證實（Confirmed static）**；低權限可達性與
可造成高權限狀態改變 = **待驗證（Hypothesis）**；不可宣稱為 exploit。

### `AmazonActivityManager.preWarmApplicationForUser`

bounded disassembly 顯示 `checkCallingPermission(APP_PREWARM)` 的結果未在該方法中被
消費，隨後 `clearCallingIdentity()` 並進入 package lookup / `startProcessLocked`。
保存的 ordinary APK evidence 支持 process/resource prewarm effect；但這條 sink 是
system-server process 建立，不是 package state、HOME 或 root writer。

**判定：** **高可信推論（Probable, bounded process deputy）**；完整呼叫者、user、
package與後續 process policy 仍需 host-only source join 才能繼續，不能把它升級成
通用 system UID 代理。

### SmartSuspend、thermal、fosdebug、Window、Input

- SmartSuspend setter 在 `SMARTSUSPEND_SETTINGS` permission 後寫入
  `smartsuspend_enabled`／schedule state；沒有低權限 setter evidence，也沒有 HOME
  或 package sink。
- `amazonthermalservice` 的本輪 bounded corpus 只確認 publication/visibility，
  method-level authorization 未恢復；分類為 visibility-only residual。
- `fosdebug` 的 dump 路徑受 `android.permission.DUMP` 保護，作用是 diagnostic inventory。
- `AmazonWindowManager.setPipVisibility` 與 `AmazonInputManager` injection helper
  的 authorization 尚未完全恢復，但已知 sink 是 PiP/window/input；shell service
  lookup denied，沒有 HOME/package/root edge。

這些項目應以**待驗證（Hypothesis）**或**已關閉的 read-only boundary**記錄，不能因
service name 可列出或 `dumpsys` 可見就推論 shell 已取得 service handle。

## 2. Fire package-state writer provenance

### PMS protected gate

既有 Phase 6PX 已把 static resource seed 與 runtime rejection 分開保存：

```text
fireos-res.apk/raw/package_manager_deny_list.json
  -> DenyListArcusHelper.processJSON()
  -> PackageManagerDenyList / DenyListKeyPackages
  -> ControlProtectedPackagesCallback
  -> PackageManagerService protected gate
  -> reject before enabled-state persistence
```

`com.amazon.firelauncher` 在 extracted resource 中的 membership 是**已證實的 host
static evidence**。但 `/data/system/PackageManagerDenyList` 的 live persisted literal
contents 受 ACL 保護，研究沒有讀取；因此只宣稱 resource seed membership，不宣稱已
直接讀出 live file。

### KFT child/profile writer

`AmazonUserManagerService$BinderService.enableKftLauncherComponent(UserInfo)` 是本輪
確認的唯一 Fire-specific package/component state writer family：

- enable `com.amazon.tahoe/.launcher.FreeTimeLauncherActivity`；
- disable `com.amazon.firelauncher` 與 `com.android.launcher3`；
- user scope 來自 supplied `UserInfo.id`，即 child/profile lifecycle；
- 授權後才 `clearCallingIdentity()`，再由 system identity 呼叫下游 package manager；
- 既有 shell-induced KFT tx3 測試在 protected/cross-user gate 前停止，沒有到達 writer。

因此它說明 Amazon 在可信 child profile 內可以改桌面 state，但**不是** User-0 的
ordinary caller bypass，也不是可直接採用的 shell route。

### 其他 writers

DPM/Profile Owner、Backup restore、OOBE/OTA 與 Arcus 都有受信任 lifecycle capability，
但本輪沒有找到可由普通 app/shell 使用的 User-0 Fire disable 或正式 HOME setter：

- DPM/Profile Owner：owner-gated policy/preferred state；沒有 Fire-specific input；
- Backup restore：trusted restore lifecycle，可恢復 preferred data，但不是 shell sink；
- OOBE/OTA：可改 OOBE component/setup flags，sender 是 system-server lifecycle；
- Arcus：deny-list seed/refresh writer，作用是保護 gate，不是 HOME writer；
- Play/PackageInstaller：只找到 generic package/component metadata writers，沒有
  bounded Fire literal 或 preferred-HOME bypass。

## 3. fosinit 與 exported-component sink closure

本輪納入 PS7331 `artifacts/phase6jd-fosinit-20260808-01` 的 123 個 XML，並與既有
registration audit、exported high-impact candidate、manifest permissions 及 source
setter inventory 做去重 join。

沒有找到 ordinary-app 或 shell-legitimate path 會收斂到：

- User-0 HOME resolver / `setHome` / preferred activity；
- `setApplicationEnabledSetting` / `setComponentEnabledSetting`；
- Settings/SettingsProvider writer；
- DevicePolicy writer。

唯一保留的高影響 edge 是 `BootAfterSystemOTAReceiver`：

```text
android.amazon.perm protected broadcast
  -> AmazonPackageManagerService.onBootPhase(550)
  -> PackageManagerService.isUpgrade()
  -> BOOT_AFTER_SYSTEM_OTA delivery
  -> OOBE/Alexa receiver
  -> OobeHomeActivity / setup flags
```

這是 system-server phase-550 + upgrade lifecycle，並非可由 shell/普通 app 手動替代的
HOME writer。沒有手動 broadcast、OOBE replay 或 OTA replay。

`LauncherHijackPreventer` 仍是 in-process AMS/PM callback，作用是 HOME-task visibility/
log filtering；本輪沒有找到 remote exported entry 或 package/preferred writer。Fire
Launcher 的 exported HOME activity/providers/services 代表 resolver exposure，不代表
state mutation capability。

## 4. New closure matrix

正規化矩陣共 38 rows：service permission 11、Fire state writers 16、fosinit/exported
sink 11。每一列保留 caller gate、identity boundary、sink、既有 runtime boundary、
status 與下一個安全步驟：

`output/tables/phase6py-service-state-exported-closure.csv`

產生器：`tools/scripts/build_phase6py_service_state_closure.py`

產生器具備：

- `--dry-run`；
- 不接觸裝置、不送 Binder、不執行 mutation；
- 輸入檔缺失即停止；
- 輸出與 manifest 已存在時拒絕覆寫；
- manifest 保存 input hashes、row counts、output hash 與安全旗標。

## 5. Call graph（文字版）

```text
ordinary app / shell
  -> ServiceManager.find(private Amazon service)
  -> SELinux/service-manager boundary
  -> [saved boundary: denied or visibility-only]

ASP tablet branch
  -> AmazonAspService.hasCallerGotPermission()
  -> command/capture/injection native sink
  -> [no HOME/package/root edge found]

preWarmApplicationForUser
  -> checkCallingPermission(APP_PREWARM) [result not consumed in bounded method]
  -> clearCallingIdentity()
  -> startProcessLocked()
  -> [process/resource effect only]

KFT child lifecycle / trusted tx3
  -> enableKftLauncherComponent(UserInfo.id)
  -> clearCallingIdentity()
  -> PMS setComponent/setApplicationEnabledSetting
  -> protected + cross-user gate
  -> [User-0 shell attempt rejected before write]

fireos-res.apk raw deny-list
  -> DenyListArcusHelper.processJSON()
  -> ControlProtectedPackagesCallback
  -> PMS protected-package gate
  -> [Fire state mutation rejected before persistence]

system-server phase 550 + PMS.isUpgrade()
  -> BOOT_AFTER_SYSTEM_OTA protected delivery
  -> OOBE Home/setup state
  -> [not ordinary HOME/preferred writer]
```

圖形版本：`output/call-graphs/phase6py-service-state-exported-closure.mmd`

## 6. Security and risk disposition

### 已證實

- Fire resource seed 直接列出 `com.amazon.firelauncher`；
- PMS protected gate 在 enabled-state persistence 前拒絕既有 shell disable；
- KFT writer 的 Fire/Tahoe state scope 是 supplied child/profile user；
- 123 fosinit XML join 沒有新增 ordinary caller → User-0 HOME/package/settings/DPM sink；
- 本輪產生器是 host-only，未對設備做 mutation。

### 高可信推論

- prewarm 的有效影響被限制在 process/resource start，而不是任意 system UID delegate；
- `BootAfterSystemOTAReceiver` 是 protected OTA/OOBE lifecycle，不是可用的 ordinary app
  HOME route；
- service list/dumpsys visibility 不能推導 shell 已取得 private Binder handle。

### 待驗證

- ASP tablet branch 在每一個 interface implementation 的實際 caller reachability；
- `AmazonInputManager` injection helper 的完整 permission/native SELinux boundary；
- thermal service method-level permission；
- live `/data/system/PackageManagerDenyList` 的 literal contents；
- trusted child lifecycle 在自然 profile event 中的完整 runtime timeline。

### 已排除（reviewed corpus）

- 本輪沒有找到新的 User-0 Fire disable writer；
- 本輪沒有找到 ordinary caller 可寫 preferred HOME 的新 route；
- exported component registration 本身不能作為 privileged deputy 證據；
- static permission anomaly 不能直接等同 root 或 launcher control。

### 因風險拒絕測試

- 未猜測或重放私有 Binder transaction；
- 未發送 protected broadcast；
- 未執行 KFT lifecycle、DPM provisioning、OOBE replay；
- 未調用 ASP/native input/thermal mutation；
- 未停用、隱藏、suspend、卸載或清除 Fire Launcher；
- 未執行 Root、exploit、ioctl、OTA/recovery、reboot 或分割區操作。

## 7. Recommended next step

下一步若仍要保持無損，優先順序是 host-only：

1. 以 exact-build decompile 補齊 ASP、Input、thermal interface 的 implementation→
   permission→SELinux sink mapping；
2. 只觀察自然發生的 trusted child/OTA lifecycle，不手動 replay；
3. 把每一個 permission anomaly 與「可達性、state writer、User-0 scope、可還原性」
   分開評分；
4. 只有取得明確、文件化且可恢復的公開 API，才考慮後續低風險 read-only probe。

目前沒有足夠證據把任何一條新路線標為可用 root、Fire Launcher disable 或 User-0
正式 HOME replacement。
