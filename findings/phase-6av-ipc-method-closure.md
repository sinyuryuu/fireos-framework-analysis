# Phase 6AV：Amazon IPC method closure

## 範圍

本階段只使用 PS7331 已保存的 VDEX disassembly、Binder method inventory、
`fosinit`／service-context 證據及既有 enforcing SELinux capture。沒有取得
Binder handle、沒有猜測 transaction code、沒有發送 transaction、沒有啟動
process、沒有修改 package／settings／overlay，也沒有重啟設備。

可重產工具與輸出：

- `tools/scripts/audit_phase6av_ipc_method_closure.py`
- `artifacts/phase6av/ipc-method-closure-20260805-02/`
- `output/tables/phase6av-ipc-method-closure.csv`
- `output/call-graphs/phase6av-ipc-method-closure.mmd`

## Executive result

### 已證實

1. `AmazonInputManagerService.BinderService.registerKeyEventInterceptor()` 的
   bounded instruction path 先檢查 `GET_KEYEVENTS`，再取得 calling UID 對應的
   package，檢查 package whitelist，並在需要時要求該 package 為前景 package：
   `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:19829-19999`。
   這是最接近 Home-key interception 的 Amazon IPC 表面，但不是普通 shell 可用
   的 HOME setter。

2. `setInputLockingMode()` 使用
   `com.amazon.amazoninputmanager.permission.INPUT_LOCKING`，並驗證 mode 值域後
   更新 input-locking state：同檔案 `:20679-20713`。

3. `AmazonProfileService.BinderService.initiateLauncher()` 的 guard 會檢查
   `com.amazon.device.permission.PROFILE_INTERACTION`；方法本身只進入內部
   profile flow、記錄並回傳 `SUCCESS`，沒有 bounded preferred-activity 或 Fire
   component write：`:76246-76256,78949-78966`。

4. `startProfilePicker()` 以服務內 configuration map 組成 explicit
   profile-picker component，再以 `startActivityAsUser()` 啟動；這是 profile UI
   啟動，不是 HOME resolver mutation：`:77222-77266`。

5. `enableKftLauncherComponent()` 的靜態路徑明確要求啟用
   `com.amazon.tahoe/.launcher.FreeTimeLauncherActivity`，並對
   `com.amazon.firelauncher` 與 `com.android.launcher3` 寫入 disabled state 2：
   `:54297-54325`。這是 KFT child-user lifecycle 行為，不是可採用的 workaround；
   裝置測試被安全邊界拒絕。

6. 保存的 enforcing-policy live capture 已證明 shell UID 2000 對相關 Amazon
   private service 的 service-manager `find` 被拒絕。`service list` 中出現名稱
   不等於 shell 可取得 Binder handle。證據在
   `artifacts/phase6aq/public-summary-20260805-05/service-check-results.txt` 與
   `amazon-service-avc.txt`。

### 高可信推論

- Amazon 的 key-interceptor 路徑是「permission + UID/package + whitelist +
  foreground」的受控 system service，而不是可由普通 ADB shell 注入的 Home-key
  替換入口。
- Profile picker 與 KFT launcher 是 user/profile lifecycle 控制面；名稱含有
  `launcher` 不代表它們會改寫 User 0 的普通 HOME resolver。
- 在目前保存的 retail SELinux 條件下，沒有可安全採用的 shell Binder route 能
  取代 Fire Launcher。

### 待驗證

- `setInputFilter()` 呼叫的 synthetic `access$600` helper 不在目前 bounded
  disassembly excerpt；其 method-local authorization 需以更完整的 DEX method
  table 或同版 source 進一步閉合。這不是缺少授權的證明。
- 每一個 Amazon private Binder method 的完整 caller policy 尚未全部人工回看。

### 已排除／因風險拒絕

- 已排除：普通 shell 可直接取得 Amazon input/profile/user service 並正式寫入
  HOME selector。
- 已排除：`initiateLauncher()` 本身是普通 HOME setter。
- 因風險拒絕：`enableKftLauncherComponent()` 實機執行，因為其明確效果包含
  停用 Fire Launcher；也拒絕未知 Binder transaction、caller spoofing、權限
  修改與 service injection。

## 最小呼叫圖

```text
shell uid=2000
  -> service_manager find
  -> SELinux enforcing deny
  -> no private Binder handle

trusted Amazon client
  -> Amazon private Binder service
  -> method-local permission / package / profile checks
  -> input interceptor, profile UI, KFT lifecycle, or prewarm action
  -> (no bounded ordinary HOME resolver write)
```

## Reproduction

```sh
python3 tools/scripts/audit_phase6av_ipc_method_closure.py --dry-run \
  --output /tmp/phase6av-ipc-dry-run
python3 tools/scripts/audit_phase6av_ipc_method_closure.py \
  --output artifacts/phase6av/ipc-method-closure-YYYYMMDD-01
(cd artifacts/phase6av/ipc-method-closure-YYYYMMDD-01 && \
  shasum -a 256 -c sha256sums.txt)
```

## 判定

本階段把「Amazon 有高影響 IPC method」收斂成「哪些方法是 profile／input／
prewarm lifecycle，哪些有 method-local gate，以及 shell 目前在哪一層被擋住」。
它沒有發現新的正式 HOME replacement，也沒有產生 root 或提權證據。
