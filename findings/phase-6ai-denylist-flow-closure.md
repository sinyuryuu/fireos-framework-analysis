# Phase 6AI：PackageManagerDenyList producer／consumer flow closure

## 範圍與安全界線

本階段只讀取既有 PS7331 VDEX disassembly、`fosinit` callback registration
和先前保存的 ADB 檔案 metadata。`tools/scripts/audit_phase6ai_denylist_flow.py`
是 host-only audit：不連接 ADB、不發送 broadcast、不呼叫 Binder、不修改
property、不讀取受限檔案內容，也不改變 package 或 HOME 狀態。

Canonical artifact：
`artifacts/phase6ai/denylist-flow-20260805-02/`。
較早的 `...-01/` 是同一工具修正前的歷史輸出，不作為本報告的 canonical
證據；所有結論以 `...-02/`、其 `sha256sums.txt`、以及本報告列出的輸入 hash
為準。

## Executive result

目前證據把「Amazon 如何把 deny-list 接到 PackageManager protection」閉合到
以下資料流：

```text
PackageManager state mutation
  → ProtectedPackages / VendorProtectedPackagesCallback
  → ControlProtectedPackagesCallback.shouldProtectPackage()
  → system/privileged check
  → PackageManagerDenyList:DenyListKeyPackages
  → caller UID == 2000
  → protected=true

AmazonPackageManagerService.onBootPhase(500)
  → DenyListArcusHelper
  → resource seed (only if key absent)
  → persist.sys.denylist_arcusid
  → Arcus sync/unmod receiver
  → JSON packages_deny_list
  → saveProtectedPackages()
  → same device-protected store
```

### 判定

- **已證實：** Fire OS 有一個在 AOSP-shaped `VendorProtectedPackagesCallback`
  fan-in 下註冊的 Amazon callback；其條件同時檢查 system/privileged app、deny
  list membership 和 caller UID 2000。證據：`6AI-DL-002`、`6AI-DL-003`、
  `6AI-DL-004`。
- **已證實：** backing store 是 device-protected 的
  `/data/system/PackageManagerDenyList`，使用 `DenyListKeyPackages` string set。
  先前 shell snapshot 可取得 `system:system`、mode `0660`、size 2645 bytes 的
  metadata，但不能讀取內容。證據：`6AI-DL-006`、`6AI-DL-007`、`6AI-DL-017`。
- **已證實：** 首次 seed 不是 Java 內嵌 package list；`processJSON()` 讀取
  system raw resource `0x7e05000a` 的 `packages_deny_list`，只有在
  `DenyListKeyPackages` 不存在時才 commit。證據：`6AI-DL-008`、`6AI-DL-009`。
- **已證實：** runtime replacement 由 Arcus configuration JSON 觸發；
  `saveProtectedPackages()` 會先將輸入轉成 `HashSet`，刪除舊 key，再
  `putStringSet(...).commit()`。保存的 direct call 只有
  `getDenyList()` → `saveProtectedPackages()`；初始 seed 是另一個內部寫入
  分支。證據：`6AI-DL-010` 至 `6AI-DL-015`。
- **高可信推論：** 先前 Fire Launcher 的 shell enabled-state rejection 與
  這個 callback 相符，因為既有實機測試已證實狀態在拒絕前後不變；但這份
  artifact scope 仍沒有讀到 deny-list literal set，因此不能把
  `com.amazon.firelauncher` 的 membership 寫成直接觀察到。證據：
  `6AI-DL-002`、`6AI-DL-017`，及既有 `6V-RUNTIME-001`。
- **已排除於本階段範圍：** 這條資料流本身是 package-state protection，沒有
  發現 HOME resolver、preferred activity 或 Home-key component selection。
  不能用它單獨解釋 HOME priority 50；它解釋的是 shell 對受保護 package 的
  enabled-state mutation 為何被拒絕。
- **待驗證：** `0x7e05000a` 對應的 resource 名稱與內容；Arcus 實際返回的
  JSON；以及現場 set 是否包含 Fire Launcher。這些需要 system UID／可讀
  artifact 或自然發生的受信任同步事件，不能由 shell snapshot 推出。

## 1. Consumer：精確保護 gate

`ControlProtectedPackagesCallback.shouldProtectPackage(int, String, Context)`
（`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:97034-97049`）
的控制流是：

1. `isSystemApp(packageName, context)` 以 `ApplicationInfo.flags` 檢查 system 或
   privileged bit。
2. `shouldDisableAmazonApp()` 取得
   `getSharedPrefPackages(context)`，再對 package name 執行 `Set.contains()`。
3. 呼叫 UID 與常數 `2000` 比較。
4. 三個條件成立時返回 `true`，否則返回 `false`。

`VendorProtectedPackagesCallback.callShouldProtectPackage()`
（`services/disassembly.log:539225-539239`）逐一呼叫 callback 並 OR 結果。保存的
`amazonpackagemanager_fosinit.xml` 以 `classLoader="SYSTEMSERVER"` 將
`ControlProtectedPackagesCallback` 註冊為該 base callback。

這比「Fire Launcher 只是 persistent」更具體：Amazon 的額外條件位於
PackageManager protection callback；但 membership literal 仍受檔案 ACL 保護。

## 2. Producer：初始 seed

`AmazonPackageManagerService.onBootPhase(int)` 在 boot phase 500 建立
`DenyListArcusHelper`。constructor：

```text
createDeviceProtectedStorageContext()
  → Environment.getDataSystemDirectory()
  → File("PackageManagerDenyList")
  → getSharedPreferences(file, 0)
  → extractListFromResorces()
  → handler.post(initializer)
```

`extractListFromResorces()` 先測試 `SharedPreferences.contains("DenyListKeyPackages")`。
只有 key 不存在才呼叫 `processJSON()`，建立 `HashSet`，並以
`putStringSet(...).commit()` 寫入。這意味著已存在的 persisted set 不會被每次
constructor 的 seed 分支盲目覆蓋。

`processJSON()` 的已知輸入是：

- `Resources.getSystem().openRawResource(0x7e05000a)`；
- JSON key `packages_deny_list`；
- JSONArray 每個元素轉成 package-name string。

目前保存的 readable resource scope 沒有足夠資料把 `0x7e05000a` 映射成
人類可讀名稱或列出內容；這是 **無法取得證據**，不是 resource 不存在。

## 3. Producer：Arcus runtime replacement

initializer 讀 `persist.sys.denylist_arcusid`，default value 來自 resource ID
`0x7e060058`。非空時呼叫：

```text
ArcusFwkManager.register(arcusId)
registerArcusBroadcastReceivers(arcusId)
ArcusFwkManager.syncId(arcusId)
```

`registerArcusBroadcastReceivers()` 建立兩個 data-derived action：

```text
amazon.arcus.sync.<id>
amazon.arcus.sync.unmod.<id>
```

並用 system-server-owned `Context.registerReceiver()` 註冊內部 receiver。
receiver 只在 action 等於其中一個值時把 worker post 到 handler；worker 再呼叫
`ArcusFwkManager.openConfiguration(arcusId)`，把回傳 JSON 送入 `getDenyList()`。

`getDenyList()`：

- 解析 JSON；
- 讀取 `packages_deny_list`；
- 逐項形成 `List<String>`；
- 呼叫 `saveProtectedPackages()`；
- 空 list、JSON exception 或 IO exception 都不形成成功寫入。

`saveProtectedPackages()`：

- `new HashSet(list)`；
- 若 key 已存在，先 `remove(DenyListKeyPackages)`；
- `putStringSet(DenyListKeyPackages, set)`；
- `commit()`。

因此可以確認「Arcus refresh 是 replacement set」，而不是單純 append 一筆
package。

## 4. Caller／writer inventory

host-only script 對保存的 fosservices disassembly 做了 symbol occurrence audit：

- constructor entry：`AmazonPackageManagerService.onBootPhase` line 96105；
- `getDenyList` definition：line 97252；
- `saveProtectedPackages` direct call：line 97283；
- `saveProtectedPackages` definition：line 97454；
- `DenyListKeyPackages` occurrences：lines 96993, 97236, 97247, 97461, 97468,
  97471, 97479；
- `packages_deny_list` occurrences：lines 97262, 97348。

保存 scope 內沒有找到 public Binder method、shell command 或獨立 exported
writer 直接呼叫 `saveProtectedPackages()`。這個 negative result 的信賴範圍只
到保存的 disassembly；它不是「整個 Fire OS 不存在其他影響 Arcus 的 binary」
之證明。證據：`6AI-DL-016`。

## 5. Live ACL evidence

既有 explicit-serial read-only capture：
`artifacts/phase6k/readonly-device-20260805-01/`。

可觀察到：

```text
-rw-rw---- system system 2645 ... /data/system/PackageManagerDenyList
```

`stat` 同樣顯示 UID/GID 1000、mode 660。對
`/data/system_de/0/shared_prefs/PackageManagerDenyList.xml` 的 `ls` 回覆
`Permission denied`。本階段沒有嘗試 `adb pull`、讀檔、改權限、繞過 SELinux
或使用 elevated caller。這保留了最重要的證據界線：

> shell 能證明 backing store 的存在與 ACL，不能從目前 capture 證明其中的
> literal package set。

## 6. 研究結論與下一個最小安全目標

### 已證實

`PackageManagerDenyList` 的 consumer、initial seed、Arcus refresh、persistent
writer 和 callback registration 已形成可重跑的靜態 control/data-flow。

### 高可信推論

Fire Launcher 的既有 shell rejection 很可能是這個 Amazon deny-list callback
在 AOSP protected-package layer 的實例化結果；這與 package 為 privileged/system
且 caller 為 shell 的現場條件一致。

### 待驗證

1. live set 是否確實含 `com.amazon.firelauncher`；
2. system raw resource `0x7e05000a` 的名稱與內容；
3. `persist.sys.denylist_arcusid` 在量產機的實際值；
4. Arcus configuration 的實際 JSON 與更新時間；
5. 是否存在保存 scope 外、但仍合法且非破壞性的受信任 producer。

### 因風險拒絕測試

不修改 `persist.sys.denylist_arcusid`、不重播 `amazon.arcus.sync.*`、不讀取或替換
`/data/system/PackageManagerDenyList`、不停止 AmazonPackageManagerService、不做
system UID／Root／SELinux／partition 操作。這些動作可能改變 package protection
或造成系統狀態不可逆，且不是回答目前資料流問題所必需。

## Reproduction

```sh
python3 tools/scripts/audit_phase6ai_denylist_flow.py --dry-run
python3 tools/scripts/audit_phase6ai_denylist_flow.py \
  --output artifacts/phase6ai/denylist-flow-20260805-02
(cd artifacts/phase6ai/denylist-flow-20260805-02 && sha256sum -c sha256sums.txt)
```

Canonical table and graph are generated at：

- `output/tables/phase6ai-denylist-flow.csv`
- `output/call-graphs/phase6ai-denylist-flow.mmd`
