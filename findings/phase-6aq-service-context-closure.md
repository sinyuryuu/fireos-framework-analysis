# Phase 6AQ：Amazon private service 可見性與授權邊界閉合

## 範圍

本階段把 PS7331 的 Amazon `fosinit` 註冊、VDEX method inventory、SELinux
service context、實機 `service list`／`service check` 與既有 AVC 記錄做 bounded
join。分析只在主機端進行；設備端只執行明確序號的唯讀查詢。

沒有發送 Binder transaction、沒有猜測 transaction code、沒有呼叫 OTA/OOBE
broadcast、沒有修改 settings／package state、沒有 reboot、沒有寫入分割區。

## 已證實

1. `fosinit` 對以下 system-server 元件建立了 Amazon vendor service 或 callback
   邊界：

   - `AmazonActivityManagerService`：
     `artifacts/amazon-services/amazonactivitymanager_fosinit.xml:10-25`
   - `AmazonDevicePolicyManagerService`：
     `artifacts/amazon-services/amazondevicepolicymanager_fosinit.xml:10-26`
   - `AmazonPackageManagerService`：
     `artifacts/amazon-services/amazonpackagemanager_fosinit.xml:10-30`
   - `AmazonWindowManagerService`：
     `artifacts/amazon-services/amazonwindowmanager_fosinit.xml:10-29`
   - `LauncherHijackPreventer` 的 ActivityStack／ActivityManager callback：
     `artifacts/amazon-services/launcherhijackpreventer_fosinit.xml:10-19`
   - tablet PackageManager／PermissionManager callback：
     `artifacts/amazon-services/tabletlauncherhijackpreventer_fosinit.xml:10-18`
   - tablet Home-key interceptor：
     `artifacts/amazon-services/tabletkeypolicymanager_fosinit.xml:10-20`
   - `FireOSDebugService` 與 system-server config callback：
     `artifacts/amazon-services/core_fosinit.xml:7-15`

2. 目前即時 `service list` 可見 private service name，但部分列出的 interface
   是空的；`fosdebug` 與 `otadexopt` 則有標準 interface。完整原始輸出保存在
   `adb/phase6aq/PHASE6AQ-SERVICE-RO-20260805-01/service_list.stdout.txt`。

3. `dumpsys fosdebug` 是 shell 可讀的標準 dumpsys 路徑，列出包括
   `amazon_keyevent`、`amazon_input`、`amazonprofileservice` 及多個 Amazon
   system-server service 的 vendor inventory。這證明服務被 Fire OS vendor
   framework 載入／登錄到該 inventory，不等於 shell 取得其 Binder handle。
   證據：
   `adb/phase6aq/PHASE6AQ-SERVICE-RO-20260805-01/dumpsys_fosdebug.stdout.txt:1-100`。

4. 在 SELinux enforcing、shell UID 2000 的實機上，對下列 service 做
   `service check` 時均回傳 `not found`：

   `amazon_input`、`amazon_keyevent`、`amazonactivitymanager`、
   `amazondevicepolicymanager`、`amazonpackagemanager`、`amazonprofileservice`、
   `amazonusermanagerservice`、`amazonwindowmanager`。

   同一批查詢留下明確的 `service_manager find` AVC deny，`scontext=u:r:shell:s0`，
   `uid=2000`，`permissive=0`。原始結果：

   - `adb/phase6aq/PHASE6AQ-SERVICE-RO-20260805-01/service_check_*.stdout.txt`
   - `artifacts/phase6aq/public-summary-20260805-04/amazon-service-avc.txt`

5. host-side context join 對關鍵 service 的結果如下。完整 201-row matrix 位於
   `artifacts/phase6aq/service-context-audit-20260805-06/service-context-matrix.csv`。

   | Service | SELinux context | shell `find` | method inventory | 判定 |
   |---|---|---:|---|---|
   | `amazonactivitymanager` | `amazonactivitymanager_service` | denied | no local auth marker in bounded row | service handle blocked; method review remains scoped |
   | `amazondevicepolicymanager` | `amazondevicepolicymanager_service` | denied | no local auth marker in bounded row | service handle blocked; no shell route shown |
   | `amazonpackagemanager` | `amazon_package_manager_service` | denied | `signature_or_privileged` | service handle and method class both protected |
   | `amazonwindowmanager` | `amazonwindowmanager_service` | denied | no local auth marker in bounded row | service handle blocked; method review remains scoped |
   | `amazon_input` / `amazon_keyevent` | `amazon_input_service` | denied | permission／UID／signature markers | no shell input-service handle |
   | `amazonprofileservice` | `amazon_profile_service` | denied | UID／permission／identity markers | no shell profile-service handle |
   | `amazonusermanagerservice` | `amazonusermanager_service` | denied | UID／component permission markers | no shell user-service handle |
   | `fosdebug` | not joined to extracted text context | found | inventory only | read-only debug inventory, not a HOME control API |

## HOME 相關結論

### 已證實

- `KeyPolicyManagerCommon.launchHomeFromHotKey()` 建立的是 implicit
  `MAIN + HOME` intent，加入 `0x10200000` flags，再以
  `Context.startActivityAsUser(..., UserHandle.CURRENT)` 啟動：
  `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3744886-3744901`。
  該 bounded path 沒有看到 `com.amazon.firelauncher` explicit component。

- `LauncherHijackPreventerActivityStackCallback.canSeeHomeTask()` 做的是
  Home task 可見性判斷：先用 `seInfo` 建立 app SELinux context，呼叫
  `SELinux.checkSELinuxAccess(..., "amazon_policies", "see_home_task")`，再以
  `PackageManager.checkSignatures(packageName, "android")` 作 fallback：
  `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3739892-3739925`。
  這是 task visibility gate，不是已證實的 HOME candidate 選擇器。

- `HomeEventHandler.handleCustomHome()` 只在前景 package 具備
  `com.amazon.permission.RECEIVE_CUSTOM_HOME` 且 custom receiver 存在時，建立
  explicit `com.amazon.tablet.action.CUSTOM_HOME` intent 並 broadcast 回前景 app：
  `decompiled/baksmali/ota-PS7331/vdex-extractor/disassembly.log:3744254-3744301`。
  該 permission 在 manifest 的 protection level 為 `0x80000002`，現場 package
  dump 對應為 `signature|amazon`：
  `artifacts/phase6ad/protected-broadcast-inventory-20260805-01/manifests/017_android.amazon.perm.xmltree.txt:512-514`；
  `artifacts/phase6x/prewarm-authorization-20260805-05/com_amazon_permission_APP_PREWARM.block.txt:151-155`。

## 方法級候選，但不是漏洞結論

`AmazonActivityManagerService.BinderService.preWarmApplicationForUser()` 在
`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40540`
出現 `Context.checkCallingPermission("com.amazon.permission.APP_PREWARM")`，緊接著
進入 `Binder.clearCallingIdentity()`，保存的 instruction stream 未顯示 denial
branch。這是需要 source／完整 control-flow 交叉驗證的 static authorization
anomaly candidate；目前沒有 shell 取得 service handle、呼叫 method、啟動任意
process 或取得權限的證據，因此不得稱為可利用路徑。

## 分類

### 高可信推論

- Amazon private service 的第一道實際邊界是 service-manager SELinux 可見性；
  第二道常見邊界是 signature／Amazon permission、system／privileged app、UID
  或 package／foreground allowlist。
- 目前 HOME key bounded path 仍是標準 implicit HOME intent；Amazon callback
  主要擴充 key handling、task visibility、custom broadcast 或 system-server
  callback，尚未證明它直接把 HOME component 改成 Fire Launcher。

### 待驗證

- 對 `AmazonActivityManagerService`、`AmazonDevicePolicyManagerService`、
  `AmazonWindowManagerService` 其他 Binder method 的逐 method caller contract
  仍需更窄的 source／smali 對照；本階段不會因 inventory row 缺 auth marker 就推定
  缺少授權。
- `fosdebug` 的所有 dump 子命令是否僅為診斷用途，仍應以 method-level inventory
  完成；目前沒有觀察到 HOME mutation API。

### 已排除

- 不是證據支持的「shell 可直接取得 Amazon private service 並呼叫 HOME setter」。
- 不是證據支持的「`HomeEventHandler` 的 custom broadcast 等於第三方 HOME
  replacement」。

### 因風險拒絕測試

- 未知 Binder transaction、直接呼叫被 SELinux 隱藏的 service、手動 replay
  Amazon broadcast、啟用 OOBE component、停用／hide／suspend／uninstall／
  force-stop／clear Fire Launcher、root、reboot-to-recovery 或 partition write。

## 可重現命令

```sh
python3 -m py_compile tools/scripts/audit_phase6aq_service_contexts.py
python3 tools/scripts/audit_phase6aq_service_contexts.py --dry-run \
  --output /tmp/phase6aq-service-context-dry-run
python3 tools/scripts/audit_phase6aq_service_contexts.py \
  --output artifacts/phase6aq/service-context-audit-20260805-06/service-context-matrix.csv

python3 -m py_compile tools/scripts/capture_phase6aq_service_visibility.py
python3 tools/scripts/capture_phase6aq_service_visibility.py --serial <DEVICE_SERIAL> \
  --output adb/phase6aq/PHASE6AQ-SERVICE-RO-20260805-01 --dry-run
python3 tools/scripts/capture_phase6aq_service_visibility.py --serial <DEVICE_SERIAL> \
  --output adb/phase6aq/PHASE6AQ-SERVICE-RO-20260805-01

python3 tools/scripts/export_phase6aq_public_summary.py --dry-run \
  --output /tmp/phase6aq-public-summary-dry-run
python3 tools/scripts/export_phase6aq_public_summary.py \
  --output artifacts/phase6aq/public-summary-20260805-05
```

腳本均拒絕在非 `--dry-run` 時覆寫既有輸出；設備腳本要求明確 `--serial`。
