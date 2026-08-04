# Phase 6H：Framework IPC 與系統服務控制面稽核

## 範圍

本輪使用已保存的 Fire OS VDEX/ODEX disassembly、JADX output、manifest 與
Amazon `fosinit` 設定，在主機端做 marker、manifest component 與 service-edge
索引。未呼叫未知 Binder transaction、未發送 crafted broadcast/intent、未改寫
package/settings/AppOps，也未停用或 kill 核心服務。

Canonical artifact：`artifacts/phase6h/phase6h-framework-ipc-20260804-01/`。
掃描 5,884 個檔案，保留 8,000 筆受上限控制的 line findings，另計算所有
marker matches；manifest component 529，`fosinit` edges 40。

## Executive summary

### 已證實

1. Fire OS 在 PackageManager state mutation 上註冊 Amazon callback。`ControlProtectedPackagesCallback`
   從 device-protected shared preferences 讀取 `PackageManagerDenyList`／
   `DenyListKeyPackages`，並以 system-app、deny-list membership 與 caller UID
   2000 作為保護條件。這與既有 Fire Launcher `pm`/`cmd package` 拒絕結果
   對齊。
2. Home key 有 Amazon key-policy 與 WindowManager vendor callback 邊界。
   `PhoneWindowManager.handleShortPressOnHome()` 可由 `KeyPolicyManager` 提前
   consume；`startDockOrHome()` 也在標準 `startActivityAsUser` 前呼叫 vendor
   callback。
3. 選定的 `PackageManagerService.resolveIntentInternal()` 仍查詢候選並呼叫
   `chooseBestActivity()`；選定的 preferred 路徑先檢查 persistent record，再
   處理 ordinary preferred record。掃描沒有在這些方法中找到明文
   `com.amazon.firelauncher` 特判。

### 高可信推論

- enabled-state 拒絕是 PackageManager 服務端 gate 的直接結果，不需要以
  watchdog 「改回狀態」解釋。
- Amazon callback 具備改變 Home flow 的位置，但目前證據只證明 callback
  boundary，不證明 callback 回傳或硬編碼 Fire Launcher。
- 大量 `home_control`、`intent_dispatch` 或 `settings_write` markers 不能單獨
  證明低權限 caller 可達；父方法、Binder stub、permission、SELinux 與 manifest
  仍可能在別處限制。

### 待驗證

- `fosinit` 中每個 callback 的完整 caller/return-value data flow。
- Home callback 是否在某些情況明確改寫 component。
- deny-list 的實際檔案 membership；shell 無法讀取其內容，因此不把檔案內容
  猜成證據。

### 已排除

- 「掃描到一個 Binder/setting 字串，所以存在可利用 IPC」：此命題沒有通過
  reachability 與 authorization 證據，不成立。
- 「缺少相鄰 permission check 就等於權限漏洞」：掃描器明確將此列為限制，
  不作此推論。

## 關鍵控制流

### PackageManager protection

```text
pm/cmd package (shell UID 2000)
  -> PackageManagerService.setEnabledSetting()
  -> ProtectedPackages.isPackageStateProtected()
  -> VendorProtectedPackagesCallback
  -> ControlProtectedPackagesCallback.shouldProtectPackage()
  -> system app && deny-list membership && UID == 2000
  -> SecurityException
```

主要 VDEX 位置：

- `decompiled/baksmali/vdexExtractor/services/disassembly.log:953377-953546`
  （state mutation gate 與 exception）。
- `.../services/disassembly.log:505771-505837`（vendor callback path）。
- `.../services/disassembly.log:539225-539250`（callback aggregation）。
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96950-97049`
  （Amazon deny-list callback）。
- `artifacts/amazon-services/amazonpackagemanager_fosinit.xml:22-24`
  （callback registration）。

### Home key

- `.../services/disassembly.log:977415`：`handleShortPressOnHome()` 呼叫
  `mKeyPolicyManager.handleShortPressOnHome():Z`；若回傳 true，標準後續路徑
  可被提前結束。
- `.../services/disassembly.log:988383-988450`：`startDockOrHome(ZZ)` 在
  `createHomeDockIntent`、`callCustomDockOrHome`、`callOnStartDockOrHome` 後，
  才以 `mHomeIntent` / `UserHandle.CURRENT` 啟動。
- `.../services/disassembly.log:951258-951310`：`resolveIntentInternal()` 取
  calling UID、查詢候選、呼叫 `chooseBestActivity()`。
- `.../services/disassembly.log:959804+`：`findPreferredActivity` 與
  `findPersistentPreferredActivityLP` 的 preferred 查詢區域。

### LauncherHijackPreventer

`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:136857+` 顯示
`canSeeHomeTask` 使用 SELinux `amazon_policies/see_home_task`，並以 Android
signature 做 fallback。這是 Home-task visibility/protection 層；本次檢查沒有
看到它直接啟動 Fire Launcher。

## 可重現輸出

- `summary.json`：掃描限制、各 marker 的 all-match count、host-only 狀態。
- `ipc-findings.csv`：受上限控制的原始 line findings。
- `manifest-components.csv`：529 個 manifest components。
- `fosinit-edges.csv`：40 個 Amazon service/callback edges。
- `ipc-edges.mmd`：文字化 IPC graph。
- `sha256sums.txt`：輸出雜湊。

重跑：

```text
python3 tools/scripts/audit_phase6h_framework_ipc_surface.py --help
```

掃描器只讀取主機檔案，遇到已存在的 output directory 會拒絕覆寫。

## 安全結論

本稽核沒有發現可直接支持 temporary root 的低權限 IPC。後續若要繼續，
最小安全目標是對已知 callback 做方法級 data-flow 與 authorization mapping，
而不是 fuzz Binder、猜 transaction code 或發送提權請求。
