# Phase 6BD：PS7331 IPC、輸入控制與 KFT 路徑閉合

## 範圍與安全狀態

本階段的目的，是確認先前留下的兩個邊界：`setInputFilter()` 的實際授權鏈，以及 KFT launcher state mutation 是否真的包含停用 Fire Launcher 的操作。

本階段使用保存的 PS7331 VDEX disassembly、permission dump，以及一次新的唯讀 service visibility capture。沒有執行 `service call`、未知 Binder transaction、輸入 filter 安裝、KFT provisioning、OTA/OOBE replay、package mutation、重開機或資料清除。

原始裝置 capture 含設備識別資料，保留在本機但不納入公開 commit：

`adb/phase6bd/PHASE6BD-SERVICE-RO-20260805-01/`

主機端可重現 audit：

`tools/scripts/audit_phase6bd_ipc_service_closure.py`

## Executive summary

### 已證實

1. `AmazonInputManagerService.BinderService.setInputFilter(IInputFilter)` 並不是未授權的普通 shell input 入口。它呼叫 synthetic `access$600`，再進入 `validateInputFilterAccessPermission()`。
2. `validateInputFilterAccessPermission()` 先接受 system/updated-system app；其他 caller 必須通過 `com.amazon.input.permission.FILTER_INPUT_EVENTS`。裝置與 permission manifest 都把這項權限定義為 `signature|amazon`。
3. KFT 靜態 helper `enableKftLauncherComponent(UserInfo)` 確實會：
   - 啟用 `com.amazon.tahoe.launcher.FreeTimeLauncherActivity`；
   - 對指定 user 要求 `com.amazon.firelauncher` 的 application enabled state `2`；
   - 對指定 user 要求 `com.android.launcher3` 的 application enabled state `2`。
4. 因此，**KFT 程式碼具有停用 Fire Launcher 的能力**。這是對指定 KFT/child user 的靜態程式碼能力判定，不等於普通 shell 能呼叫，也不等於該路徑已在本機 User 0 執行。
5. 新的唯讀 service check 中，選定的 Amazon private services 對 shell 都回報 `not found`；`fosdebug` 與 `otadexopt` 可被診斷查詢。沒有發送任何 private method transaction。

### 高可信推論

- `setInputFilter()` 不是目前可用的 shell HOME-key 旁路：service visibility 受 Enforcing policy 限制，且 method-local authorization 另有 system-app／Amazon signature gate。
- KFT mutation 是特殊 user lifecycle 的 package-state controller，而非一般 HOME resolver setter。若直接對 User 0 重播，會偏離原始 KFT 條件並可能切斷主桌面；這不符合無損驗證。
- `dumpsys fosdebug` 是 DUMP-gated diagnostic inventory。它列出 vendor services/managers/callbacks/instances，尚未提供可驗證的 HOME selector 或寫入介面。

### 待驗證

- Amazon 正常 UI 的 child-profile provisioning 是否會在特定帳戶／家長流程建立符合 KFT `UserInfo` 條件的 user。
- 所有 private Binder method 的完整 caller matrix；本階段只閉合與研究問題直接相關的 method。

### 已排除／因風險拒絕

- **已排除於目前安全範圍：** shell 可直接安裝 input filter、呼叫 KFT launcher mutation、透過 `fosdebug` 選擇 HOME，或由 `otadexopt` 取得 root/HOME replacement。
- **因風險拒絕：** 直接對 User 0 呼叫 KFT、建立或變更 child/profile owner、未知 `service call`、OOBE/OTA broadcast replay、OTA/recovery 執行，以及任何 Fire Launcher disable/hide/suspend/uninstall/force-stop/clear。

## 1. `setInputFilter()` 精確呼叫鏈

保存的 VDEX disassembly 顯示：

```text
AmazonInputManagerService.BinderService.setInputFilter(IInputFilter)
  → AmazonInputManagerService.access$600()
  → validateInputFilterAccessPermission()
      → isCallerSystemApp()
          → Binder.getCallingUid()
          → PackageManager.getPackagesForUid()
          → ApplicationInfo.isSystemApp()
          → ApplicationInfo.isUpdatedSystemApp()
      → 若不是 system/updated-system app：
          Context.enforceCallingPermission(
              "com.amazon.input.permission.FILTER_INPUT_EVENTS", ...)
  → InputManagerService.registerSecondaryInputFilter(...)
```

證據位置：

- Binder entry：`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:20112-20122`
- synthetic helper：同檔 `:21687-21692`
- caller identity predicate：同檔 `:21874-21904`（含 `getCallingUid`、UID package lookup、system/updated-system checks）
- permission validator：同檔 `:22437-22448`
- permission declaration：`artifacts/phase6ac/protected-broadcast-source-audit-20260805-02/manifest-aapt.xmltree.txt:1431-1433`
- device permission state：`artifacts/phase6k/readonly-device-20260805-01/preferred_activities.stdout.txt:9897-9901`

這裡的結論是 **Confirmed**，但只代表靜態授權鏈與既有裝置 permission state 已對上；沒有把 input filter 實際裝到設備，也沒有測試任何繞過方式。

## 2. KFT launcher state mutation

`AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)` 的保存指令流為：

```text
enableKftLauncherComponent(UserInfo user)
  → AmazonPackageManager.setComponentEnabledSetting(
        com.amazon.tahoe/
        com.amazon.tahoe.launcher.FreeTimeLauncherActivity,
        state=1, userId=user.id)
  → AmazonPackageManager.setApplicationEnabledSetting(
        com.amazon.firelauncher, state=2, userId=user.id)
  → AmazonPackageManager.setApplicationEnabledSetting(
        com.android.launcher3, state=2, userId=user.id)
```

精確位置：`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325`。

上層 `enableKftLauncher(UserInfo)` 還會先經過 KFT／MM device、FreeTime launcher 與 DevicePolicy/profile-owner 相關條件；保存位置：同檔 `:54415-54478` 及既有 KFT report。這不是一個可用來證明「任意 shell UID 可以停用 Fire Launcher」的簡單 wrapper。

### 實機狀態

既有的 read-only KFT preflight（`KFT-PREFLIGHT-20260805-01`）確認：

- 目前只有 User 0，沒有 child/KFT user；
- device owner 為空；
- `amazonusermanagerservice` 對 shell `service check` 為 `not found`；
- HOME 仍為 `com.amazon.firelauncher/.Launcher`；
- KFT mutation 沒有呼叫。

所以本階段對使用者提出的判定是：

> **Confirmed：KFT 程式碼具有停用 Fire Launcher 的能力。**
>
> **Confirmed：本研究階段未呼叫該路徑，未修改設備。**

## 3. FireOSDebugService 與 `fosdebug`

`FireOSDebugService.BinderService.dump(FileDescriptor, PrintWriter, String[])`：

- 在 `fosservices/disassembly.log:196-222` 檢查 `android.permission.DUMP`；
- 通過後才 `Binder.clearCallingIdentity()`；
- 輸出 `Vendor Services`、`VendorManagers`、`VendorCallbacks`、`Instances`；
- 呼叫 `FireOSDebugService.native_dump_vendor_callbacks()`；
- 沒有在該 dump method 中看到 HOME component、preferred activity 或 package-state setter。

本次 `dumpsys fosdebug` 只作讀取，結果是 vendor inventory。`native_dump_vendor_callbacks()` 的存在本身不能推論 shell 可以任意呼叫 callback，也不能推論其能改寫 HOME。

## 4. 新的 service visibility capture

Test ID：`PHASE6BD-SERVICE-RO-20260805-01`

使用的工具：`tools/scripts/capture_phase6aq_service_visibility.py`。雖然 script 名稱沿用 6AQ，這次 output 已隔離到 Phase 6BD 目錄；該 script 只執行 service-manager lookup、標準 dumpsys、getprop/id/getenforce 與 `logcat -d`。

| Service name | shell `service check` | 判定 |
|---|---|---|
| `amazonpackagemanager` | `not found` | shell 不可見 |
| `amazonactivitymanager` | `not found` | shell 不可見 |
| `amazonwindowmanager` | `not found` | shell 不可見 |
| `amazondevicepolicymanager` | `not found` | shell 不可見 |
| `amazonprofileservice` | `not found` | shell 不可見 |
| `amazonusermanagerservice` | `not found` | shell 不可見 |
| `amazon_input` | `not found` | shell 不可見 |
| `amazon_keyevent` | `not found` | shell 不可見 |
| `fosdebug` | `found` | 僅診斷可見；未發送私有 method |
| `otadexopt` | `found` | 可見性不是控制權證明；未發送命令 |

這裡的「不可見」是對本次 shell service-manager capture 的描述，不宣稱該服務在 system_server 中不存在。

## 5. 安全邊界與未執行清單

本階段沒有：

- 停用、隱藏、suspend、解除安裝、force-stop 或清除 Fire Launcher；
- 呼叫 `enableKftLauncherComponent` 或任何已知 KFT Binder method；
- 建立 child user、Device Owner 或 profile-owner；
- 發送 `service call`、未知 Binder transaction 或 native callback；
- 修改 settings、AppOps、Overlay、preferred activity 或 package state；
- 執行 OTA、recovery、sideload、root、GhostLock race、kernel trigger 或 reboot。

## 6. 可重現步驟

主機端 audit（不接觸設備）：

```sh
python3 tools/scripts/audit_phase6bd_ipc_service_closure.py \
  --dry-run \
  --output /tmp/phase6bd-dry-run

python3 tools/scripts/audit_phase6bd_ipc_service_closure.py \
  --output artifacts/phase6bd/ipc-service-closure-YYYYMMDD-NN \
  --public-table output/tables/phase6bd-ipc-control-surface.csv \
  --public-graph output/call-graphs/phase6bd-ipc-control-surface.mmd
```

裝置端唯讀 capture（需要研究者明確指定 serial）：

```sh
python3 tools/scripts/capture_phase6aq_service_visibility.py \
  --serial DEVICE_SERIAL \
  --output adb/phase6bd/PHASE6BD-SERVICE-RO-YYYYMMDD-NN
```

不得把 `service call`、KFT lifecycle replay 或 package-state mutation 加入上述 read-only capture。

## 最終判定

本階段成功閉合了 `setInputFilter` 的權限疑點，並以精確 instruction evidence 確認 KFT 對指定 user 的 Fire Launcher state mutation。這支持「Amazon 有特殊 user-lifecycle 控制器」的結論，但沒有形成普通 ADB shell 可用的 HOME replacement，也沒有提供安全理由去對 User 0 實際呼叫該 mutation。
