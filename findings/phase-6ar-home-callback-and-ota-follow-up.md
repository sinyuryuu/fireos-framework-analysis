# Phase 6AR：HOME callback 與 OTA／OOBE 後續邊界

## 目的

本文件把 Phase 6AQ 的即時 service visibility 證據，與已完成的 HOME key、
OTA staging、`BootAfterSystemOTAReceiver` 及 OOBE 靜態分析串接。重點是區分：

1. 標準 HOME resolver／Home key 路徑；
2. Amazon 的 task visibility、custom-home broadcast 與 system-server callback；
3. 合法 system OTA 後才可能發生的 OOBE lifecycle；
4. 不可安全 replay 的高影響控制面。

## HOME callback path

### 已證實

```text
Home key
  -> TabletKeyPolicyManager / KeyInterceptorCallback boundary
  -> KeyPolicyManagerCommon.launchHomeFromHotKey()
  -> implicit MAIN + CATEGORY_HOME + flags 0x10200000
  -> Context.startActivityAsUser(..., UserHandle.CURRENT)
  -> Android Activity/PackageManager HOME resolution
  -> current Fire OS HOME result: com.amazon.firelauncher/.Launcher
```

`launchHomeFromHotKey()` 的 instruction-level evidence 位於
`decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3744886-3744901`。
在此 bounded method 中沒有 Fire Launcher explicit component。

`LauncherHijackPreventerActivityStackCallback.canSeeHomeTask()` 是另一條 callback
邊界：

```text
Activity/task visibility query
  -> ApplicationInfo.seInfo
  -> SELinux.getAppContext()
  -> SELinux.checkSELinuxAccess(..., amazon_policies, see_home_task)
  -> Android-signature fallback
  -> allow/deny Home task visibility
```

證據：`decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3739892-3739925`。
這段程式碼可影響某些 caller 看到 Home task 的能力，但不等於已證明它在
`resolveIntent` 之後替換 component。

### Custom Home event

`HomeEventHandler.handleCustomHome()` 是前景 app 的 custom event：

```text
foreground ComponentName
  -> getCustomHomeReceiver(package)
  -> AmazonPackageManager.checkPermission(RECEIVE_CUSTOM_HOME, package)
  -> explicit com.amazon.tablet.action.CUSTOM_HOME to that package/receiver
  -> sendBroadcastAsUser(..., RECEIVE_CUSTOM_HOME)
```

證據：`decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3744254-3744301`。
`RECEIVE_CUSTOM_HOME` 是 `signature|amazon`，不是普通第三方 APK 可以取得的
公開 launcher selector：
`artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt:151-155,16609`。

## OTA／OOBE path

### 已證實

既有 Phase 6Y／6Z 證據顯示，正常 OTA dataflow 是：

```text
external storage candidate
  -> filename/readiness check
  -> metadata/package/device checks
  -> RecoverySystemWrapper.verifyPackage (verification path)
  -> basename-based staging mover
  -> FileHelper.renameTo or copy+delete
  -> UpdateSystemWrapper.install
  -> UpdateSystem.install (high-impact update boundary)
  -> natural post-system-OTA boot lifecycle
  -> BootAfterSystemOTAReceiver
  -> OOBE/setup-state branch
```

`BootAfterSystemOTAReceiver` 的 sender gate 是 system-server boot phase 550 加上
`PackageManagerService.isUpgrade()`；它使用
`com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA`。現有詳細分析：
`findings/phase-6z-boot-after-system-ota-follow-up.md`。

OOBE branch 可啟用 priority-100 的 `OobeHomeActivity` 並寫 setup-state；保存的
User 0 狀態中該 component 是 disabled。這是 OTA 後 setup lifecycle，不是普通
preferred activity，也不是已證實的 shell HOME setter。

### 分類

#### 已排除

- `BootAfterSystemOTAReceiver` 不是目前證據支持的普通 shell HOME selector。
- `HomeEventHandler` custom broadcast 不是第三方可直接使用的 HOME replacement。
- `AmazonActivityManagerService.isOnHomeStack()` 只是讀取 focused stack 的
  activity type 2，沒有 component mutation：
  `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40336-40373`。
- `notifyActivitySwitch()` 是將 activity resume 事件通知註冊 observer，沒有在
  bounded body 中看到 Fire Launcher selection：
  `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40374-40400`。

#### 高可信推論

- 如果合法 OTA 後 OOBE flow 被啟用，它可能暫時改變 setup 前景與 task flow；
  不能把這個特殊 lifecycle 結果外推成一般使用者可設定的 HOME replacement。
- 目前 Fire Launcher 結果最保守的解釋仍是：標準 implicit HOME path + Fire
  Launcher 的 system/privileged candidate 狀態與 effective priority 50，再加上
  Amazon 的 task visibility／package protection 邊界；尚未證明 Amazon callback
  直接回傳 Fire Launcher component。

#### 待驗證

- 完全匹配 PS7331 的 protected-broadcast runtime closure 與自然官方 OTA 後的
  event ordering。
- OOBE Home 啟用後由 resolver、明確 task flow 或其他 callback 啟動的精確順序。
- `UpdateSystem`／recovery native 層的 canonicalization、symlink handling 與
  atomicity；Java staging source 本身不能代表 native implementation。

#### 因風險拒絕測試

- 手動 `am broadcast` `BOOT_AFTER_SYSTEM_OTA`。
- 手動 enable `OobeHomeActivity`。
- 修改 `user_setup_complete`、`isOOBEActive`、OOBE data 或 provisioning state。
- 執行 updater／recovery、crafted OTA、symlink/traversal payload、未知 Binder
  transaction、partition write 或任何需要 factory reset 的復原路徑。

## 現況交叉證據

最新唯讀基線 `adb/phase6aq/PHASE6AQ-RO-20260805-01/` 顯示：

```text
priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
com.amazon.firelauncher/.Launcher
```

`preferred-xml` 是 `<preferred-activities />`；`cmd role` 回傳
`Can't find service: role`；前景仍是 `com.amazon.firelauncher/.Launcher`。
因此本階段沒有發現新的 shell-writable HOME control surface，也沒有改變設備
目前狀態。

## 下一個最小研究目標

只在 host-only 或自然官方 OTA 完成後做事後 snapshot：

1. 對 matching framework-res／system/product/system_ext 保存輸入完成
   `RECEIVE_BOOT_AFTER_SYSTEM_OTA` protected-broadcast closure；
2. 對自然 OTA 後的 OOBE component state、resolver、task 與 logcat 做時間序列
   比對；
3. 若沒有新的合法 caller 或可逆控制面，將 OTA/OOBE 路線結案為高影響 lifecycle
   boundary，而不是無 Root launcher workaround。
