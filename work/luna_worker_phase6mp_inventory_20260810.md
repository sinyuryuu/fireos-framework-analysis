# Phase 6MP 主機端唯讀 inventory（2026-08-10）

## 範圍、基準與安全界線

本報告以目前公開 `HEAD` `36d354adf0f3b7ee54491f3f79cc84478632e5f4`
（`Add Phase 6MO OOBE context scope closure`）以及現有 Phase 6MO、6MN、
6MK、6MM、6R、6KV、6MG 證據為準。檢查只讀取 worktree 中已保存的文字、
CSV、JSON、VDEX/baksmali disassembly 與 source/archive metadata；未連接
設備，未執行 ADB、Binder/service call、未知 transaction、ioctl、OTA/
recovery、提權或任何設備/既有檔案修改。本輪只新增本報告。

Worktree 原本已有大量 modified/untracked 內容；本報告不把那些內容清理、
重置或覆寫。這是靜態 evidence inventory，不是 runtime reachability 或
漏洞結論。

## 1. 已有 coverage 與不重複範圍

| Phase | 已完成範圍 | 主要證據（SHA-256） | 證據等級 | 尚未覆蓋／限制 |
|---|---|---|---|---|
| 6MO | `AmazonPackageManagerService.onBootPhase(550)` → `Context.sendBroadcast` → receiver `Context` → OOBE settings/component sinks；已證實 context-derived user boundary | `findings/phase-6mo-oobe-context-user-scope.md` `e962ba889cd93df672c9827a8411bdee6bc6c2bb2b75b7d2e5bf799002dc95d2`; `artifacts/phase6mo-oobe-context-user-scope-20260810-01/summary.json` `c219719bbaca7c772a76721d55ad1a0ed0592771f90a6490c7b54403a6194708` | Confirmed / Strong | exact post-OTA delivery user 仍未證明為 User 0；四個 OOBE source 未見 ordinary Fire HOME writer，僅 corpus-bounded negative |
| 6MN | 42-row caller→permission→identity→sink→user-scope ledger：7 caller rows、25 PMS/package-state rows、2 vendor HOME callbacks、8 OOBE/helper signals | `artifacts/phase6mn-ipc-user-scope-20260810-01/route-matrix.csv` `a156538f89cff05e098a01fce169fda4e88f65b86fe4b06054d740cbd615e56b`; `findings/phase-6mn-evidence-index.md` `8942a6517043b3b9180b6ceecc394c26b1684130ce6b940219fee23b6667b9ee` | Strong / bounded negative | 未涵蓋完整 Amazon `I*Service.Stub.Proxy` caller universe；沒有把所有非-HOME Amazon system-service IPC 接到 permission/identity/sink |
| 6KV | 25 個精確 package/preferred/component state invoke sites；KFT launcher writer、OOBE/Gemini/Espresso/ProductPolicy、standard shell/DPM/PMS paths | `output/tables/phase6kv-pms-home-callers.csv` `dc1a86ea85904e3775704944fa86364a9a89033f6146eed0dac8b324b7028382`; `findings/phase-6kv-pms-home-caller-closure.md` `a3c3d90315895c8295c8cee73f889f020b96f31cded80fa9e1672dc9ae598ef1` | Strong / Confirmed static | 只索引 bounded HOME/package-state sinks，不是每個 Amazon service interface 的 caller map；不推導 UID、Binder 可達性或 execution |
| 6MG | 29 個 OOBE helper signals；`SettingsDBUtils`、`PackageHelper`、receiver guards | `findings/phase-6mg-oobe-helper-scope.md` `68c931fa0606d4b0fa4c094e0e63683b263caadcebae9b10f7ef5359adc49903`; `output/tables/phase6mg-oobe-helper-scope.csv`（artifact source 為 `artifacts/phase6mg-oobe-helper-scope-20260810-01/`） | Confirmed helper shape | 已由 6MO 接上 framework Context semantics；不應重做 OOBE helper scan 或 broadcast replay |
| 6MK | native `update-binary` install registry 24/24 pointer cells、13 script entrypoints、selected `package_extract_file`→`ota_open` | `artifacts/phase6mk-updater-dispatch-20260810-04/registration-dispatch.csv` `d88e35ec08d9ef0a55a3dbc17dc430b62d3b419810653542b6dd3077095cca24`; `summary.json` `4cf463ec498b74e6460fb598f7ce5e5756418aaa5c2ac5767009c22e9c29b9fe` | Confirmed / Strong | canonicalization indirect/unselected flow 未完全閉合；與 Android Framework IPC caller gap 不重疊 |
| 6MM | 5 個 block-image registrations；818 selected direct edges；`MakeFreeSpaceOnCache`→`__readlink_chk` 一個 call site | `artifacts/phase6mm-updater-blockimage-20260810-01/block-image-registration.csv` `778bc4774b4ade436bd979b366c1f3c8e9a1ce91fe6aa2d306040d32629cebcb`; `canonicalization-call-sites.csv` `8cc6d38c1e464b6b741b29bdee8aa253113e7aea286f368ffe1cf1c0cde5983d`; `summary.json` `a0186bb7d053d23f002dc663b9ee3f312255410b35ed997a74e864fc8f9229a6` | Confirmed / Probable | `CacheSizeCheck` body、indirect return/function-pointer flow 未閉合；與本報告的 Binder interface gap 不重疊 |
| 6R | OOBE/OTA authorization、27-method OTA interface、23 receiver query rows；高影響 OTA methods 受 `CONTROLLER` `signature|privileged` gate | `artifacts/phase6r/ota-ipc-static-audit-20260805-04/summary.json` `693c80e61dfc1994bf6ab80949f12d44373c107f1b3299b749a4896082cd5c59`; `ota-receiver-query-matrix.csv` `8c793682c38b20c60bb0d6f793217bda129669da12e35fd803d319b9cce29a34` | Strong / Confirmed static | 不執行 OTA、recovery、broadcast 或 Binder；OTA interface 與一般 Amazon Framework service IPC 分開處理 |

## 2. 尚未覆蓋的 Amazon Framework/System Services IPC caller→sink 路徑

### 2.1 首要、最小候選：`IAmazonInputManager`

這是目前最清楚、但尚未在 6MN/6KV ledger 中閉合的 Amazon IPC path：

```text
IAmazonInputManager.Stub.Proxy
  -> AmazonInputManagerService.publishBinderService
  -> BinderService method
  -> checkCallingOrSelfPermission
  -> nativeInject / nativeInjectSequence
  -> fd_keyboard / fd_mouse / fd_touchscreen input sink
```

已保存的靜態 anchors：

- `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log`，
  SHA-256 `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`：
  `IAmazonInputManager.Stub.Proxy` 在約 line 388887，宣告 28 virtual
  methods；proxy method 以 descriptor 與 `IBinder.transact` 呼叫（例如
  `createKeyboardDevice`、`createMouseDevice`）。
- 同一檔 `IAmazonKeyEventManager.Stub.Proxy` 約 line 395081，宣告 10
  virtual methods；這是相鄰的 callback/partner-app IPC candidate，不應與
  `IAmazonInputManager` 混為已閉合路徑。
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`，
  SHA-256 `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`：
  `AmazonInputManagerService.publishBinderService` 約 lines 22648–22652；
  BinderService 的 permission check 約 line 19498；`nativeInject` sinks
  約 lines 19555, 19574, 19623，`nativeInjectSequence` 約 lines 19653,
  19673, 19708；source-level method declarations 約 lines 22145–22148。
- 現有 `artifacts/phase6bk/ipc-ota-closure-20260810-02/method-map.csv`
  （`b487531c8ae8dbf55812feb463f666810eb63acca98d3ce57dbffddf37567acf`）只
  將 `AmazonInputManagerService.onBootPhase`（line 22521–22639）列入
  service method inventory，沒有把此 interface 的每一個 proxy method、
  service permission、calling identity、input/native sink 做成 caller ledger。

目前只能下的結論是 **Confirmed static IPC surface / unresolved caller-to-
permission-to-sink provenance**。`checkCallingOrSelfPermission` 的具體
permission string、每個 transaction code 到實作 method 的完整 mapping、
是否 clear calling identity、以及 shell/app caller provenance 均未在既有
6MN/6KV artifacts 中閉合。`nativeInject*` 是靜態 sink 名稱；本 inventory
沒有執行 native method、device node 或 ioctl。

### 2.2 次要候選：已見 proxy/publication、但沒有完整 caller→sink ledger

以下不是已證實漏洞，也不是建議逐一 runtime 測試；它們是應在後續 host
static pass 中分類的 interface candidates：

| Interface / service | 靜態 anchor | 目前狀態 | 與既有 coverage 的關係 |
|---|---|---|---|
| `IAmazonActivityManager` / `AmazonActivityManagerService` | `boot-fosframework` 約 line 394353；`fosservices` method map `preWarmApplicationForUser` 40453–40534 | `preWarmApplicationForUser` 已由 6BK/6MN 覆蓋為 permission + clear identity + process-start、無 HOME sink；proxy 中其餘約 16 methods 尚未形成完整 ledger | 不重做 prewarm；只可另做未索引 method 的 bounded scan |
| `IAmazonWindowManager` / `AmazonWindowManagerService` | proxy 約 line 400006；service publish 約 `fosservices:56244`；`setPipVisibility` 已出現在 6BK method map | `setPipVisibility` 有 service/proxy/static permission anchors，但沒有完整 caller identity/user/sink chain | 不重做既有 PIP runtime；host-only method/permission mapping 可分開 |
| `IAmazonProfileService` | proxy 約 line 376614；service publish `fosservices:80819`；`initiateLauncher`/`startProfilePicker` 6BK 已列出 | profile permissions、`startActivityAsUser` path 已有靜態 evidence；完整 external caller universe 未閉合 | 不做 profile UI、user creation 或 transaction replay |
| `IAmazonPackageManager` | proxy 約 line 402917；service publish `fosservices:96136`；wrapper 的 component/application setters 已在 6KV | package-state wrapper/PMS sink 已有 coverage；完整 Amazon-specific method set、permission、caller provenance 未閉合 | 不重做 HOME/PMS writer census；只補非已索引 methods |
| `IAmazonAccessibilityManager` | proxy 約 line 394117；service publish `fosservices:35432` | proxy methods（magnification canvas 等）與 service publication 可見，但未形成 caller→permission→identity→sink matrix | 不做 accessibility state mutation；只可靜態整理 |
| `IAmazonDevicePolicyManager` | proxy 約 line 397105；service publish `fosservices:46156` | `clearRestrictionForUser` 等 proxy methods 可見；DPM owner/policy rows 在 6KV 只覆蓋 HOME/package-state caller subset | 不做 DPM admin/transaction；先確認 permission/user argument/sink |

上述候選的共同 gap 是 **interface presence ≠ caller reachability**：
`Stub.Proxy`、`publishBinderService` 或 service-list 名稱本身不能證明 shell
或普通 APK 可以取得 handle，也不能推導 transaction authorization。

## 3. 已有測試、結果、雜湊與保存設備狀態

本節只引用已有保存結果；本輪沒有重新連接設備。

### 3.1 Phase 6MO/6MN/6KV 的 host-only 結果

- 6MO `summary.json` `c219719bbaca7c772a76721d55ad1a0ed0592771f90a6490c7b54403a6194708`
  記錄：`device_contacted=false`、`binder_or_service_call=false`、
  `ioctl=false`、`mutation=false`、`broadcast_sent=false`、
  `oobe_started=false`、`exact_user_id_proven=false`。結論是 context-derived
  user scope 已閉合，exact broadcast delivery user 未證明。
- 6MN `route-matrix.csv` hash `a156538f89cff05e098a01fce169fda4e88f65b86fe4b06054d740cbd615e56b`
  記錄 42 normalized rows；其 summary hash `36e2c71079b4482fbb64e4672a57a00d9a2d9e5b233395e3cce3fa4089dbe669`
  記錄無 device/Binder/ioctl/mutation。未發現 selected untrusted route 到已證實
  User-0 Fire HOME/package-state sink。
- 6KV `output/tables/phase6kv-pms-home-callers.csv` hash
  `dc1a86ea85904e3775704944fa86364a9a89033f6146eed0dac8b324b7028382`：25
  static invoke rows；6KV 的既有 read-only repeat `adb/phase6ep/PHASE6EP-AMAZON-WRITER-REACHABILITY-20260809-191243/result.json`
  hash `465be89b25ec6b731fd8d1f3de57636a8265a9a4ce5fdb61c69e3ba0bd73cd59`。

### 3.2 保存的設備狀態（僅引用，不是本輪操作）

6EP `result.json` 保存的狀態是：五個候選 private service names 在 inventory
中可見，但 shell handles 全部 `not found`；`any_candidate_shell_handle_found=false`。
User 0 HOME before/after 均為：

```text
priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
com.amazon.firelauncher/.Launcher
```

`home_unchanged=true`、`fire_user0_state_unchanged=true`，Fire package
User 0 為 installed、unsuspended、enabled=0。這是保存 capture 的結果，
不代表本輪訪問設備。

Phase 6BK 保存的 `artifacts/phase6bk/ipc-ota-closure-20260810-02/summary.json`
hash `410dcbbdfe562198f00c214ed9efe7b14494f902f2957bd6f3c9a96d318e4b6d` 也
記錄 `binder_invoked=false`、`ota_executed=false`、`package_or_settings_mutated=false`、
`partition_written=false`，並保存 PS7331 fingerprint 與 Fire HOME excerpt。
6BK service read-only hash manifest 為
`adb/phase6bk/PHASE6BK-SERVICE-RO-20260810-01/sha256sums.txt`
（`f7f3bbbec8d01e71e90634b9ad658a38259f68d92220fc59d98b0c8793237ff7`）。

### 3.3 6R/OTA 狀態

6R OTA static summary `693c80e61dfc1994bf6ab80949f12d44373c107f1b3299b749a4896082cd5c59`
記錄 `host_only=true`、`broadcast_sent=false`、`binder_transaction_sent=false`、
`ota_executed=false`、`partition_written=false`。高影響 methods 包含
`installSideload`、`resumeOSInstallation`、`startInstallUpdates` 等，但
`com.amazon.dcp.ota.permission.CONTROLLER` 為 `signature|privileged`，不構成
shell-writable route。

## 4. PS7331 GPL source 與安裝包的靜態候選

### 4.1 GPL/source package：已知 scope 與未檢查候選

- `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2`，SHA-256
  `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`。
  Phase 6MI 已完成 outer tar EOF：35 members、0 symlink/0 hardlink、沒有
  updater/recovery/post-install outer member；summary
  `artifacts/phase6mi-source-tar-eof-20260810-03/summary.json`
  `409ed81ede46db87a0ef8a05cc33b99df2b66e068d1edc1ac481a42e0606169b`。
- `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` extracted hash
  `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`，
  `fireos.tar` extracted hash
  `bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369`，
  `trona_defconfig` hash
  `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac`。
- `artifacts/phase6c5/gpl-source-scope-20260804-01/scope.json`
  `8ab20dd811f93b30163f0f5b5f8dadb75bb3e73cc8199571a0f62f9709963221`、
  `scope.csv` `99b4c831b30d2ffd5863b55480605426946568afdc4b5aab1e6b18525660e163`
  確認 GPL package 是 MT8183 4.4 kernel/Amazon device support，沒有完整
  Android framework service source、`system/core/init/selinux.cpp` 或
  `rootable_*_sepolicy.cil`。
- 可安全檢查、但尚未建立 IPC caller→sink provenance 的 source candidates：
  `firmware/extracted/PS7331-SOURCE-20250617/platform/device/amazon/kernel/driver/`
  中的 `amzn_idme.c`、`amzn_logger.c`、`amzn_keycombo.c`、sign-of-life/
  driver-test sources；以及
  `platform/kernel/mediatek/mt8183/4.4/drivers/` 的 input/power/char/USB/
  Amazon driver trees。它們只能做 source-to-binary/name/config/SELinux
  靜態對照；不能推導 userspace Binder reachability，也不能在本任務中開
  device node 或送 ioctl。

### 4.2 PS7331 installation package：安全的靜態候選

- `firmware/extracted/PS7331/META-INF/com/google/android/update-binary`，
  SHA-256 `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`。
- `firmware/extracted/PS7331/META-INF/com/google/android/updater-script`，
  SHA-256 `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248`。
  6MK/6MM 已閉合 command/block-image registration；不可執行 updater。
- 仍可做、但與 Framework IPC 不重複的 host-only candidates 是：
  `artifacts/phase6mm-updater-blockimage-20260810-01/focus-disassembly.txt`
  的 `CacheSizeCheck` body、function-pointer return value、以及
  `MakeFreeSpaceOnCache` canonicalization input/output data-flow。這些只可
  做 disassembly/edge/constant analysis，不能做 crafted path、symlink、
  recovery 或 partition test。
- Phase 6BP 的既有結論（固定 partition target、無 observed post-install
  executor）已使安裝包不再是最小 Framework IPC gap；不應以 OTA 執行來補
  caller evidence。

## 5. 最小、host-only、非重複的下一個任務

推薦只做一個 bounded task：

> **建立 `IAmazonInputManager` 的 static caller→permission→identity→sink
> matrix。**

固定輸入為：

1. `boot-fosframework/disassembly.log` 中 `IAmazonInputManager.Stub.Proxy`
   的 28 methods 與 transaction codes；
2. `fosservices/disassembly.log` 中
   `AmazonInputManagerService.publishBinderService`、BinderService method
   headers、permission checks、`clearCallingIdentity`/restore markers；
3. 同 service 的 `nativeInject`/`nativeInjectSequence`、fd field 與
   callback sinks；
4. existing service publication/permission manifests（如有），只做
   source/hash correlation。

輸出欄位應為：

```text
interface/proxy method | transaction code | published service name
| implementation method | permission check/string | Binder identity handling
| user/package argument | native/input sink | caller evidence | confidence
```

成功標準是把「proxy 存在」與「可證實 caller/sink」分開；若 permission
string、caller 或 transaction mapping 缺資料，明確標成 `unresolved`，不把
`checkCallingOrSelfPermission` 或 `nativeInject` 名稱升格成可達性或 exploit。
此 task 不應執行任何 proxy transaction、service call、native method、device
node/ioctl、ADB、reboot、OTA/recovery 或設備 mutation。

這個任務比再做一次 6MN OOBE/HOME ledger、6R OTA authorization、6MK/6MM
updater graph 或 6MG/6MO context mapping 更小，且直接填補目前最明確的
Amazon Framework/System Services IPC caller→sink evidence gap。
