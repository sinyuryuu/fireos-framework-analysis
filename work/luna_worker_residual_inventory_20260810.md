# Phase 6ME 後殘餘盤點：Amazon Framework／OTA／User-0 HOME

日期：2026-08-10
角色：luna_worker；本檔僅整理既有公開 HEAD、工作樹中的 README／PROJECT_STATUS、findings、adb/ 與 artifacts/。

## 盤點界線與版本狀態

- 公開 HEAD：`b770afbbd78754ae4b0183bb8d1325dd045c3ce5`（`Close OOBE and package-state writer boundaries`）。
- 工作樹的 `README.md`、`PROJECT_STATUS.md`、`findings/evidence-index.md` 有既有未提交變更；本輪只讀取，未將其誤標成 HEAD，也未修改既有檔案。
- 本輪沒有執行 ADB、網路、Binder／`service call`、ioctl、Root／exploit、OTA／recovery／fastboot／reboot，也沒有套件、component、設定或分割區修改。

## 結論摘要

Phase 6ME 的 driver/control-plane 路線已收斂：選定 1,671 個 kernel source files、7,698 markers，沒有直接 framework／HOME／Fire Launcher source hit；這不是 kernel 安全性全域證明。Phase 6MF–6MH 之後，仍有價值且未閉合的 Framework 殘餘主要只有 OOBE helper 的 context-to-user mapping；package/component setter 的 callsite inventory 本身已完成，但不等於 shell 可達或 User-0 writer。Amazon KFT writer 已證實為 supplied `UserInfo.id` 的 child/profile 路徑，Product Policy、標準 PMS shell path、Backup/DPM preferred writer、private-service reachability 均已有邊界證據。

方向二（Amazon IPC）的最小 host-only 缺口，是對「仍有明確、文件化 read-only API 的 Amazon package」做 caller/context closure，並把 Binder interface、permission、caller UID、user mapping 與 state sink 對齊；不可用猜測 transaction 補洞。方向三（OTA）的最小 host-only 缺口，是完成現有 updater binary 中 canonicalization／symlink markers 到 extraction/write chain 的 indirect-call/data-flow closure，以及 recovery 外層簽章／版本／path 驗證的靜態 mapping；不可執行 updater、malformed OTA 或 recovery。

## A. 未閉合的 Amazon Framework／OTA／User-0 HOME 或 package/component writer

### A1. OOBE helper 的實際 user mapping — **待驗證**

- `findings/phase-6mg-oobe-helper-scope.md`：`SettingsDBUtils.java:51-64` 使用 `ContentResolver` 寫 Secure/Global；`PackageHelper.java:11-22` 使用 state `1/2`、flags `1` 的 component setter，但沒有明示 user ID；`OOBEActivationHelper.java:29-34,53-74` 寫 setup/OOBE keys，不是 preferred HOME API。
- `artifacts/phase6mg-oobe-helper-scope-20260810-01/summary.json`：29 signals、explicit user-scope signals `0`、`device_mutation=false`。
- `findings/phase-6mf-residual-candidates.md` 的 R1 將此列為「待驗證；因風險拒絕 live 驗證」。真正最小問題是追 `Context` 建立、`ContentResolver` user handle 與 framework `PackageManager` client 的 mapping；`FG` 方法後綴不能推成 User 0。
- `findings/phase-6mg-oobe-helper-scope.md` 已排除「OOBE helper 是普通 User-0 Fire restoration writer」的目前證據解讀，但沒有排除 OTA/OOBE lifecycle 本身的高風險 state transition。`BootAfterSystemOTAReceiver` 由 `fosservices/disassembly.log:96107-96126` 的 boot phase 550 + `isUpgrade()` sender guarded。

### A2. Package/component setter 的完整 inventory 已閉合；User-0 writer 仍未證實 — **已證實／高可信推論／待驗證**

- `findings/phase-6mh-package-state-writer-closure.md`、`findings/phase-6mh-evidence-index.md`、`artifacts/phase6mh-package-state-writers-20260810-01/summary.json`：21 callsites（11 component、10 application），host-only、無 Binder transaction/device mutation。
- 關鍵 Amazon KFT row：`fosservices/disassembly.log:54310-54324` 的 `enableKftLauncherComponent(UserInfo)` 含 Fire/Tahoe/Launcher3 literals，並使用 supplied `UserInfo.id`。既有 User 10 state correspondence 是強證據，但不證明最新 lifecycle 重新執行該 method：`findings/phase-6bk-kft-runtime.md`、`adb/phase6bk/PHASE6BK-KFT-PREFLIGHT-RO-20260810-01/`。
- Product Policy row：`fosservices/disassembly.log:293712-293738` 是 trusted policy-file/user-list action；`findings/phase-6ce-product-policy-firelauncher-boundary.md` 已確認 exact PS7331 policy inputs 沒有 `com.amazon.firelauncher`，且 service 只 publish local service。故作為正常 User-0 Fire restoration writer 已**已排除**。
- 標準 shell setter：`services/disassembly.log:500744-500765` 進入已知 PMS protected-package gate；Fire component/package disable 的已完成結果不應重跑。`README.md` 的 component probes 與 `findings/phase-6mh-package-state-writer-closure.md` 均記錄此停止點。
- 仍可保留的 bounded unknown 是 OOBE helper 的 exact user mapping，以及未來自然 trusted lifecycle 是否真的觸發某個 writer；不是可安全 replay 的 writer。

### A3. 其他 trusted preferred-HOME writers — **已證實／已排除／因風險拒絕**

- Backup restore `tx81` 與 DPM `tx100 -> PMS tx73` 是 system／active-admin gated writer；`findings/phase-6hu-user0-residual-writers-closure.md`、`findings/evidence-index.md` Phase 6KR/6KS；既有 DPM caller-gate captures 位於 `adb/phase6dt/`。不送 tx81/100/73，不建立或替換 owner。
- MigrationService 的 Fire literal 是 availability/data-refresh broadcast，不是 PackageManager enabled state、preferred HOME、Role 或 launcher start：`PROJECT_STATUS.md` Phase 6CD、`findings/phase-6gt-migration-service-boundary.md`。
- H2 household service 能在合法 profile lifecycle 中建立 child user，但 exported service 具有 signature bind permission；bounded APK scan 沒有 Fire/HOME writer：`findings/phase-6mc-permission-and-h2-audit.md`、`artifacts/phase6mc-alta-static-20260810-01/`。bind／`addUser`／create child 已因風險拒絕。
- Amazon private service names 雖在 `service list` 出現，shell lookup 對 focused services 為 `not found`；這是 reachability boundary，不是服務不存在，也不授權猜測 Binder：`findings/phase-6bk-report.md`、`adb/phase6bk/PHASE6BK-SERVICE-RO-20260810-01/`。

## B. 已完成測試、結果與明確停止／禁止重跑

### 已證實

- Phase 6ME host-only driver scan：`artifacts/phase6me-driver-control-edges-20260810-01/summary.json`；`direct_framework_or_launcher_files=0`、`file_count=1671`、`marker_count=7698`、mutation/ADB/ioctl/binary execution 全為 false。
- Phase 6MH setter inventory：21 callsites 全部有 source line/class/method/scope/literal/instruction callsite；callsite inventory 完成，但 setter 不等於 reachable writer。
- Phase 6BK：User 0 保持 `com.amazon.firelauncher/.Launcher` priority 50；User 10 Tahoe/Profile Owner 與 per-user Fire/Tahoe state correspondence 已保存；private Binder 未送；`otadexopt` 僅 read/precondition 行為：`findings/phase-6bk-report.md`、`artifacts/phase6bk/ipc-ota-closure-20260810-02/summary.json`。
- 6MA 的 PS7331 system-image deny-list resource 已直接找到 `com.amazon.firelauncher`：`findings/phase-6ma-denylist-fosinit-and-kft-closure.md`、`artifacts/phase6ap/denylist-resource-closure-20260805-01/res/raw/package_manager_deny_list.json:2-7`。這修正 6MF R3 的較早「內容尚未取得」狀態；shell writable/Arcus refresh reachability 仍未證實。

### 明確已排除（就目前 bounded evidence）

- selected Phase 6ME driver source 的 direct `driver -> PMS/AMS/ATMS/HOME -> Fire` edge。
- Product Policy 是正常 PS7331 User-0 Fire restoration writer。
- KFT child writer 可被解讀成 User-0 writer；User 10 switching/start-stop 也沒有形成 User-0 HOME replacement。
- 普通 shell 的 package/component disable family、preferred HOME ordinary path、DPM fake/live-owner caller impersonation、Role service（API 28 上 service 不存在）作為安全新入口。
- OTA updater 作為 HOME selector：`findings/phase-6md-native-updater-path-audit.md` 明確沒有 Fire Launcher/HOME/preferred sink。

### 因風險拒絕／禁止重跑

- 不重跑已證實 PMS protected-package component/package disable、uninstall/hide/suspend 等 Fire mutation family。
- 不送 guessed/unknown Amazon Binder transaction 或 `service call`；不 bind H2、呼叫 child-user APIs、DPM/Backup/PMS writer transactions。
- 不觸發 `BOOT_AFTER_SYSTEM_OTA`、手動 OOBE activation、OTA install、malformed/symlink OTA、recovery、fastboot、partition write、reboot。
- 不執行 driver node open、ioctl、DMA/race、debugfs/sysfs write、Root/exploit 或 kernel LPE；Phase 6ME 及 `findings/phase-6me-driver-control-closure.md` 已明確保留 Framework-first stop condition。

## C. 方向二：Amazon IPC 的下一個最小 host-only、可驗證缺口

**建議唯一下一步：做 caller/context closure，不做 live IPC。**

1. 以既有 PS7331 VDEX/JADX 與 framework client 為輸入，選一個已有明確 read-only contract 的 Amazon API；靜態對齊 `onStart` registration、AIDL Proxy/Stub transaction、interface/service permission、`Binder.getCallingUid()`／identity clear、caller APK 與 user handle。
2. 對每個候選建立一列可重現 table：`caller -> service lookup -> permission -> transaction -> implementation -> user scope -> state sink`，並把「setter callsite」和「實際可達」分開。
3. 優先回答 A1 的 context-to-user mapping，或證明某個 read-only API 的普通 caller closure；若只能得到 child/profile scope，標為已排除 User-0 writer。

可驗證輸出：host-only CSV/graph/summary，`device_contacted=false`、`binder_transaction_sent=false`、`device_mutation=false`，加上 source/artifact hashes。不可用 `service list` 存在性推導可呼叫性。

## D. 方向三：OTA 的下一個最小 host-only、可驗證缺口

**建議唯一下一步：完成既有 native updater 的靜態 canonicalization／verification data-flow closure。**

- 起點：`findings/phase-6md-native-updater-path-audit.md`、`artifacts/phase6md-native-updater-path-audit-20260810-02/`。已證實 `PackageExtractFileFn -> ExtractEntryToFile`、`PerformBlockImageUpdate -> ota_open/open/chown/rename`、`WriteToPartition -> ota_write -> write`；updater-script 觸及 system/vendor/boot 與 boot-chain targets。
- 尚未閉合：binary 有 `symlink_realpath`／`readlinkat`／`readlink` markers，但 selected direct-BL graph 沒有 canonicalization edge；需要 host-only indirect-call/function-pointer/error-path/data-flow tracing，並靜態對照 recovery 外層的 signature/version/canonical-path validation。
- 產出應只回答「guard 是否位於 extraction/write chain、其輸入與 sink 為何」，不可把 strings 當 traversal 證明，也不可執行 `update-binary`、製造 OTA、sideload 或進 recovery。

最小成功條件：補上 bounded call/data-flow table、明確標示 `direct edge / indirect unresolved / not in selected graph`，並保持 `ota_executed=false`、`partition_written=false`。

## E. 本輪變更與驗證

本輪唯一預期新增檔案是本檔：`work/luna_worker_residual_inventory_20260810.md`。未修改其他檔案，未執行任何裝置或網路操作；完成後僅檢查本檔內容、`git diff --check`，以及變更路徑是否只有本檔新增。
