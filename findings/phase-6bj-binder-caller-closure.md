# Phase 6BJ：Amazon 私有 Binder caller closure 稽核

## 範圍與安全界線

本階段只對已保存的 PS7331 DEX/VDEX 反編譯輸出做主機端文字與方法呼叫索引，並對設備執行唯讀的 service-manager lookup。沒有送出 `service call`、未知 Binder transaction、反射呼叫、進程啟動、套件狀態變更或設定修改。

設備唯讀核對使用明確序號 `G001LT0511550CFT`；結果仍為 `uid=2000(shell)`、SELinux `Enforcing`、PS7331 fingerprint，且只有 user 0。原始設備輸出位於 `adb/phase6bj/PHASE6BJ-READONLY-20260805-01/`。

## 結論摘要

| Finding | 結論 | 證據 | 信心 |
|---|---|---|---|
| 目標方法的框架內部呼叫者 | 在保存的四份 disassembly 中找到 19 個 invoke；主要是 Stub、wrapper 或 system-server 內部 callback | `caller-summary.csv`、`caller-map.csv` | 已證實 |
| `preWarmApplicationForUser` | 服務方法在權限檢查後才清除 calling identity 並進入 `getApplicationInfo`／`startProcessLocked`；既有 caller closure 只找到受限的 Alexa 路徑，不能由本 scan 推導 shell 可用 | `fosservices/disassembly.log:40453`；`findings/phase-6bb-prewarm-caller-closure.md` | 高可信推論 |
| `registerKeyEventInterceptor` | 先檢查 `GET_KEYEVENTS`，再讀 `Binder.getCallingUid()`、套件名、白名單及 foreground 條件；不是一般 shell 可用的 Home key setter | `fosservices/disassembly.log:19829`、`024c42–024eb4` | 已證實 |
| `setPipVisibility` | 只寫入 Amazon WindowManager 的 PIP visibility state；沒有 HOME component、preferred record 或 package state 寫入 | `fosservices/disassembly.log:56150`、`044926–044930` | 已證實 |
| KFT launcher state path | `enableKftLauncherComponent(UserInfo)` 內硬編碼啟用 Tahoe FreeTime launcher，並以 user id 停用 `com.amazon.firelauncher` 與 `com.android.launcher3`；由 `enableKftLauncher`／`tryEnableKftLauncherComponent` 內部呼叫 | `fosservices/disassembly.log:54297–54325`、`54371–54404` | 已證實 |
| KFT 是否為普通 shell HOME 旁路 | 沒有證據支持；目前設備的 Amazon 私有 service 名稱雖出現在 `service list`，shell 的 `service check` 對目標名稱均回報 `not found` | `adb/phase6bj/PHASE6BJ-READONLY-20260805-01/`、`findings/phase-6l-binder-contract-audit.md` | 已排除（在目前 shell/SELinux 前提下） |
| 正式 HOME replacement | 本階段沒有找到新的 shell-writable 正式 HOME 控制面 | Phase 3A–6BJ 證據鏈 | 待驗證／目前未發現 |

## 方法與可重現輸出

使用腳本：

```text
tools/scripts/audit_phase6bj_binder_caller_closure.py
```

輸入檔案與 SHA-256：

| Label | File | SHA-256 |
|---|---|---|
| fosservices | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| services | `decompiled/baksmali/vdexExtractor/services/disassembly.log` | `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53` |
| boot-fosframework | `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` | `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71` |
| ota-PS7331 | `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log` | `04d68d0bb562a14e9cbff3bdce63b66eb911ee4bb7e728ca77cd435a5b03c146` |

重現命令：

```sh
python3 tools/scripts/audit_phase6bj_binder_caller_closure.py \
  --source fosservices=decompiled/baksmali/vdexExtractor/fosservices/disassembly.log \
  --source services=decompiled/baksmali/vdexExtractor/services/disassembly.log \
  --source boot-fosframework=decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log \
  --source ota-PS7331=decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log \
  --output artifacts/phase6bj/binder-caller-closure-20260805-01
```

產出雜湊：

| File | SHA-256 |
|---|---|
| `caller-map.csv` | `ff9f4e43a0deb572dacc8c16fde35041e44dcad5ca5aecf079a8fafd36bd7689` |
| `caller-summary.csv` | `cc4e3d2608d14827214d2e13915b8b2aabc186301ac5b9a6172a4880fe716ddc` |
| `caller-closure.mmd` | `c440e50015cfe396f1ceacb9e4f33501e8a7bfc427afb9defc7fc3f213516008` |
| `summary.json` | `bc61044b98073f5c45c37a21c5040f19777d12ed56c3ca9a7a0eacff6545b77c` |

## Caller closure

### `preWarmApplicationForUser`

保存輸出中的呼叫點可分成三類：

1. `IAmazonActivityManager.Stub.onTransact` 將 transaction 參數交給 service implementation。
2. `AmazonActivityManagerImpl.preWarmApplication` wrapper 呼叫 `preWarmApplicationForUser`。
3. `AmazonActivityManagerImpl.preWarmApplicationForUser` 透過 `IAmazonActivityManager` proxy 發出私有 IPC。

在 `AmazonActivityManagerService$BinderService.preWarmApplicationForUser`（`fosservices/disassembly.log:40453`）中，先有：

```text
Context.checkCallingPermission("com.amazon.permission.APP_PREWARM")
Binder.clearCallingIdentity()
IPackageManager.getApplicationInfo(...)
ActivityManagerService.startProcessLocked(..., "prewarm", ...)
```

`clearCallingIdentity()` 之後的 system-server 操作不能被解讀為「呼叫者已獲得 system UID」。權限判斷發生在清除 identity 之前；既有 `phase-6bb` caller closure 進一步只在 Alexa 的受限 caller scope 找到可到達的上層呼叫者。這是高權限 prewarm API 的授權邊界，不是 HOME 選擇器或套件停用 API。

### `registerKeyEventInterceptor`

`AmazonInputManagerService.BinderService.registerKeyEventInterceptor`（`fosservices/disassembly.log:19829`）的控制流包含：

```text
checkCallingOrSelfPermission("com.amazon.permission.GET_KEYEVENTS")
Binder.getCallingUid()
PackageManager.getPackagesForUid(callingUid)
package whitelist lookup
foreground package equality check
key whitelist / duplicate checks
```

失敗路徑會回傳 false 或丟出 `SecurityException("Requires GET_KEYEVENTS permission")`。即使有合法輸入攔截權限，該 API 的語意是註冊指定 key callback，不是改寫 PackageManager HOME resolver；本階段沒有把它當成 launcher replacement 入口。

### `setPipVisibility`

`AmazonWindowManagerService.BinderService.setPipVisibility`（`fosservices/disassembly.log:56150`）只將 boolean 寫入 `mPipState`（反編譯 offset `044926–044930`）。caller scan 找到 `AmazonWindowManagerPwmCallback.onSetPipVisibility` 及 Stub dispatch；沒有同一方法對 `com.amazon.firelauncher`、preferred activity、`setHomeActivity` 或 `startHomeActivity` 的存取。故它不是 HOME 控制面。

### KFT launcher state path

`enableKftLauncherComponent(UserInfo)`（`fosservices/disassembly.log:54297–54325`）是本次最明確的 package-state 變更點：

```text
new ComponentName(
  "com.amazon.tahoe",
  "com.amazon.tahoe.launcher.FreeTimeLauncherActivity")
AmazonPackageManager.setComponentEnabledSetting(..., state=1, ..., userId)
AmazonPackageManager.setApplicationEnabledSetting(
  "com.amazon.firelauncher", state=2, ..., userId)
AmazonPackageManager.setApplicationEnabledSetting(
  "com.android.launcher3", state=2, ..., userId)
```

它由 `tryEnableKftLauncherComponent(UserInfo)`（`54371–54404`）及 `enableKftLauncher(UserInfo)`（`54434` 附近）在 Amazon user-management lifecycle 內部呼叫。這確認 Amazon 具備「針對 child/KFT user 變更 launcher package state」的程式能力；不確認普通 user 0 可由 shell 觸發，也不授權以私有 Binder payload 重播。先前實機 child-profile UI 測試未建立 child user，且未執行此方法。

## 設備唯讀核對

Evidence `PH6BJ-RT-001` 對應 `adb/phase6bj/PHASE6BJ-READONLY-20260805-01/metadata.json`：

- serial：`G001LT0511550CFT`
- fingerprint：`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
- shell：`uid=2000(shell)`；SELinux：`Enforcing`
- `service list` 仍列出 `amazonpackagemanager`、`amazonwindowmanager`、`amazonusermanagerservice`、`amazonactivitymanager`、`amazon_input` 等名稱。
- 對上述私有名稱的 `service check` 均回報 `not found`；這表示目前 shell domain 無法取得可用 service handle，不能從名稱存在推論可呼叫性。
- 腳本 metadata 明確記錄 `binder_transactions=false`、`package_state_changed=false`、`settings_changed=false`、`reboot_requested=false`。

這些 lookup 是 service-manager 可見性證據，不是對所有可能的 system-server 內部呼叫者的數學完備證明；native、reflection、生成 Binder code 及未保存 artifact 仍屬範圍外。

## 最小呼叫圖（文字版）

```text
AmazonActivityManagerImpl.preWarmApplication
  -> AmazonActivityManagerImpl.preWarmApplicationForUser
  -> IAmazonActivityManager.Proxy / Binder transaction
  -> IAmazonActivityManager.Stub.onTransact
  -> AmazonActivityManagerService.BinderService.preWarmApplicationForUser
  -> checkCallingPermission(APP_PREWARM)
  -> clearCallingIdentity
  -> getApplicationInfo / startProcessLocked

AmazonInputManager.registerKeyEventInterceptor
  -> IAmazonInputManager.Proxy / Binder transaction
  -> IAmazonInputManager.Stub.onTransact
  -> AmazonInputManagerService.BinderService.registerKeyEventInterceptor
  -> GET_KEYEVENTS + UID/package/foreground/key whitelist checks

KFT internal user lifecycle
  -> enableKftLauncher(UserInfo)
  -> tryEnableKftLauncherComponent(UserInfo)
  -> enableKftLauncherComponent(UserInfo)
  -> Tahoe FreeTime enabled; Fire Launcher and Launcher3 disabled for that user
```

對應 Mermaid 圖：`output/call-graphs/phase6bj-binder-caller-closure.mmd`。

## 判定與後續最小目標

### 已證實

- Amazon framework 內存在 KFT child-user launcher state mutation；其程式碼明確包含 Fire Launcher 的停用呼叫。
- 私有 activity-manager、window-manager、input-manager contract 的 Stub/wrapper 呼叫關係可由保存的 DEX disassembly 重建。
- `registerKeyEventInterceptor` 有明確 caller permission、UID、package whitelist 與 foreground gate。
- 目前設備 shell 不能透過 `service check` 取得這些私有 service handle；本階段沒有送 transaction。

### 高可信推論

- KFT state path 不是 user 0 的一般 HOME replacement API，而是 child-user provisioning/lifecycle 專用路徑。
- `preWarmApplicationForUser` 即使在 system-server 內清除 identity，也不會把缺少 `APP_PREWARM` 的 shell 轉成被授權 caller；既有 caller closure 及 runtime service visibility 共同支持此判斷。
- PIP 與 key interceptor 路徑不會直接選擇或停用 HOME resolver 的 Fire Launcher。

### 待驗證

- 未保存的 native/reflection caller 是否還有其他合法 privileged caller。
- KFT 在真正存在的 child user 上由哪一個受信任 lifecycle 觸發，以及是否同時寫入 persistent preferred HOME。
- 若要確認 child-user 路徑的完整 runtime 行為，需使用正常受支援的 Amazon UI/帳戶流程；不應用 shell 重播私有 Binder。

### 已排除

- 以 `setPipVisibility` 作為 HOME selector。
- 以 `registerKeyEventInterceptor` 在目前 shell/SELinux 前提下直接取得 HOME 改寫能力。
- 以 service name 出現在 `service list` 作為可從 shell 呼叫私有 API 的證據。

### 因風險拒絕測試

- 未呼叫任何 `service call` 或未知 transaction code。
- 未建立 child user、未設定 Device Owner、未停用/隱藏/suspend/uninstall/force-stop/clear Fire Launcher。
- 未修改 framework、system/vendor/product 分割區或 SELinux。

## 目前研究結論

本階段沒有發現可安全驗證的新正式 HOME replacement，也沒有證據顯示 shell 能重播 KFT 的 child-user package-state mutation。最有價值的新結果是把「Amazon 具備停用 Fire Launcher 的能力」精確收斂到 KFT `UserInfo` lifecycle，而不是一個可由普通 user 0／shell 直接調用的通用入口。後續若繼續，最低風險方向是完善 KFT 正常 child-profile lifecycle 的靜態對照與受支援 UI 行為記錄；不應轉向私有 Binder payload 猜測。
