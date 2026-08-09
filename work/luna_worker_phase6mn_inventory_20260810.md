# Phase 6MN 唯讀盤點（2026-08-10）

本檔是共享工作區的 host-only inventory。盤點前工作樹已有大量 modified／untracked 使用者內容；本輪只新增本檔，未修改其他檔案，未執行 ADB、網路、Binder/service call、ioctl、Root/exploit、OTA/recovery/reboot 或任何裝置 mutation。

## 1. HEAD、工作樹與 Phase 6MK/6MM 後內容

- `HEAD`：`89b5942ae Add Phase 6MM block image updater closure`（`origin/main` 同一 commit）。
- HEAD 內已納入 Phase 6MM 的 findings、selected disassembly、registration/call-edge tables、summary、call graph 與 `tools/scripts/audit_phase6mm_updater_blockimage_closure.py`。
- 工作樹仍 dirty：既有 modified 檔包括 `PROJECT_STATUS.md`、`README.md`、`findings/evidence-index.md`、phase4 工具與 launcher 工具；另有大量未追蹤 `ADB_HISTORY.md`、`PROJECT.md`、`KNOWN_FINDINGS.md`、`SERVICE_MAP.md`、`TARGETS.md`、`TODO.md`、`adb/`、`artifacts/`、`findings/`、`scripts/`、`tools/`、`work/` 等。這些均視為既有使用者內容，不作清理或重置。
- 目前與本盤點最相關、可辨識的新增／未追蹤 corpus：
  - Phase 6ME：`artifacts/phase6me-driver-control-edges-20260810-01/`、`output/tables/phase6me-driver-control-closure.csv`、`output/call-graphs/phase6me-driver-control-closure.mmd`、`findings/phase-6me-driver-control-closure.md`、`findings/phase-6me-evidence-index.md`、`tools/scripts/audit_phase6me_driver_control_edges.py`。
  - Phase 6MK：`artifacts/phase6mk-updater-dispatch-20260810-01/` 至 `-04/`、`output/tables/phase6mk-updater-dispatch-20260810-04.csv`、`output/call-graphs/phase6mk-dispatch-canonicalization-20260810-04.mmd`、`findings/phase-6mk-*`、`tools/scripts/audit_phase6mk_updater_dispatch_closure.py`。
  - Phase 6MM：HEAD 所收錄的 `artifacts/phase6mm-updater-blockimage-20260810-01/`、`output/tables/phase6mm-updater-blockimage-20260810-01.csv`、`output/call-graphs/phase6mm-blockimage-canonicalization-20260810-01.mmd`、`findings/phase-6mm-*`、`tools/scripts/audit_phase6mm_updater_blockimage_closure.py`。
  - OOBE／Amazon IPC／permission 前置證據：`artifacts/phase6bk-*`、`phase6mc-*`、`phase6mg-*`、`phase6kv-*`、`phase6ky-*`、`phase6lz-*`，及對應 `findings/phase-6bk-*`、`phase-6mc-*`、`phase-6mg-*`、`phase-6kv-*`、`phase-6ky-*`、`phase-6lz-*`。
  - 先前 worker 盤點：`work/luna_worker_phase6ml_inventory_20260810.md`、`work/luna_worker_phase6mj_residual_inventory_20260810.md`；6ML 的 residual 仍適用，6MM 只新增 block-image registration/canonicalization call-site closure。

## 2. 尚未閉合的 Amazon IPC／OOBE user-scope、permission、sink evidence

### OOBE user scope

已證實的 bounded chain 是：

```text
AmazonPackageManagerService.onBootPhase
  [boot phase 550 + isUpgrade()]
  -> protected BOOT_AFTER_SYSTEM_OTA broadcast
  -> BootAfterSystemOTAReceiver
  -> PackageHelper.enableComponent(OobeHomeActivity)
  -> OOBEActivationHelper
  -> context-bound Settings／PackageManager state
```

`findings/phase-6mg-oobe-helper-scope.md` 與 `artifacts/phase6mg-oobe-helper-scope-20260810-01/` 已確認 helper 的 settings/component writer shape，但 `Context`、`ContentResolver` user handle、PackageManager client 到實際 User 0／current user 的 mapping 尚未證明。沒有 `ForUser` call 不能推出 User 0；`OobeHomeActivity` 也不是普通 HOME writer。`OobeHomeActivity` 的 enable、OOBE preference/provisioning state、OTA sender/receiver lifecycle 仍不可由人工 broadcast 補測。

### Amazon IPC／permission

- `BOOT_AFTER_SYSTEM_OTA` 在指定 45 APK union 中只確認到 `android.amazon.perm` 的 protected-broadcast 宣告；這是 scanned-set confirmed，不是全映像 global proof。
- `H2ClientService` 是 exported 但受 signature-level `BIND_SERVICE` 保護；靜態 chain 可到 `AmazonUserManager.createChildUser()`，但不是 shell 可用路徑，也沒有 bounded APK scan 中的 Fire Launcher/HOME writer。
- permission census 已確認多個 system/priv-app 持有 `CHANGE_COMPONENT_ENABLED_STATE`、`MANAGE_USERS`、`WRITE_SECURE_SETTINGS` 等 signature/privileged 權限；holder presence 不等於繞過 PMS protected-package gate。
- 尚未閉合的是 unified caller→service lookup→binding/transaction permission→Binder identity→user argument→state sink matrix，尤其 H2 child caller、KFT/AmazonUserManager transaction、prewarm、post-OTA OOBE sender 與 PMS/package-state sink 的跨 artifact provenance。完整 Amazon private Binder caller universe 仍待驗證。

### Sink boundary

已有 evidence 將「正式 User-0 HOME writer」與「child/profile scoped writer」、「OOBE setup-state writer」、「OTA/recovery write capability」分開；目前沒有新的無 Root User-0 Fire Launcher replacement。尚缺的是每條 Amazon IPC/OOBE 分支的精確 user-scope 與 sink provenance，而不是再做一次 HOME resolve 或 component mutation。

## 3. MediaTek／Amazon driver static surfaces

`findings/phase-6me-driver-control-closure.md`、`artifacts/phase6me-driver-control-edges-20260810-01/summary.json` 的 host-only scan：1,671 個選定 C/C++/header 檔，7,698 個 bounded markers，0 個直接 Framework/PMS/AMS/ATMS/HOME/`com.amazon.firelauncher` literal/call hits。

主要 scope：`drivers/misc/mediatek`、`drivers/staging/amazon`、`drivers/staging/android/ion`、`drivers/input`、`drivers/power/mediatek`、`drivers/usb`、`drivers/char`。marker 統計包括 ioctl 1,726、user-copy 957、proc/sysfs/debugfs registration 703、device registration 509、secure-world 3,274、trusted-execution 3；均是 surface markers，不是漏洞數。

- MediaTek：CMDQ、ION、GED、M4U、connectivity drivers 有 ioctl/user-copy/DMA/proc/sysfs/debug surface；source scan 沒有直接 HOME/PMS edge。具體 node mode、init registration、SELinux domain、下游 hardware effect 仍是獨立 gate。
- Amazon：IDME、logger、sign-of-life、driver test／telemetry surfaces；既有 runtime capture 顯示相關 production boundary（read-only、root:log、SELinux）但不構成 launcher/root primitive。
- `findings/phase-6n-kernel-surface-index.md` 的較早 source index（4,278 markers／343 files）與 6ME 的較窄 control-plane scan 互相一致；6ME 已把「driver→Framework/HOME direct source edge」縮到 bounded negative。
- 尚未驗證：每個 shipped binary function 與 source function 的 exact correspondence、所有 device node 的 production SELinux reachability、CMDQ metadata arithmetic/downstream use、secure-world command effect。這些不應轉成 launcher hypothesis 或 ioctl 測試授權。

## 4. 已完成／禁止重做的測試

### 已完成（只引用保存 evidence，不在本輪重跑）

- Phase 6MK host-only：native updater install command registry、24/24 function-pointer resolution、`package_extract_file`→`ota_open/open` selected chain、canonicalization markers；未執行 updater/recovery/OTA。
- Phase 6MM host-only：5 個 block-image registry entries（`block_image_verify`、`block_image_update`、`block_image_recover`、`check_first_block`、`range_sha1`）與 `MakeFreeSpaceOnCache→__readlink_chk` direct call-site；selected 818 direct edges 中沒有 direct canonicalization→write sink，但 `CacheSizeCheck` body/間接 flow 仍未閉合。
- Phase 6ME host-only driver source scan；0 direct Framework/HOME hits，且 summary 明確標記 `adb=false`、`ioctl=false`、`mutation=false`。
- 既有 read-only ADB captures：`adb/phase6bk/PHASE6BK-KFT-PREFLIGHT-RO-20260810-01/`、`PHASE6BK-SERVICE-RO-20260810-01/`、`PHASE6BK-STATE-RO-20260810-01/`、`adb/phase6mc-permission-holders-20260810-01/`、`adb/phase6n/PHASE6N-KERNEL-RO-20260810-01/`，以及 child-profile post-readonly captures `CHILD-TEST-20260810-05-POST-RO/`、`-06-POST-RO/`。它們只作既有證據，不是本輪裝置操作。
- 既有 bounded runtime 結果：User 0 HOME 仍為 Fire Launcher；child UI submission 後沒有新增可見 Android user；GED 僅 query/read-only；SELinux enforcing、verified boot green；沒有證明第三方 HOME replacement。

### 明確禁止重做

- 不重做 ordinary HOME resolver、preferred activity、Fire Launcher enable/disable/uninstall/suspend、PMS priority、child-profile runtime/UI submission、KFT transaction 或既有 rollback/restore。
- 不人工發送 `BOOT_AFTER_SYSTEM_OTA`，不啟用 OOBE component，不寫 provisioning/setup/settings state，不 bind/call H2 或 Amazon private Binder，不做 service fuzz/replay。
- 不執行任何 `update-binary`、Recovery、OTA/sideload、crafted/malformed/symlink/traversal path、fastboot、partition write、Root/exploit 或 reboot。
- 不開啟 device node，不送 CMDQ/ION/M4U/GED ioctl，不寫 proc/sysfs/debugfs/module parameter，不做 DMA/readback、kernel race、panic 或 secure-world operation。

## 5. 最小、host-only、可重現的下一個分析候選

首選：**Amazon IPC/OOBE caller→permission→user-scope→sink provenance matrix**。

理由是它直接處理目前對研究問題仍有意義的未閉合 evidence，且不重做已完成的 HOME、child UI、permission-holder census 或 6MK/6MM updater registry。只讀保存的 JADX APK、AIDL Stub/Proxy、system-server VDEX/disassembly、fosinit/service registration、permission manifests 與既有 capture metadata，產出一張固定欄位表：

```text
caller class/package | lookup/registration | exported/bind/transaction permission
| Binder calling identity | user argument/context handle | state sink
| User-0/profile/OOBE scope | evidence file/hash | status
```

最小輸入／工具候選：`tools/scripts/audit_phase6ky_amazon_ipc_boundaries.py`、`tools/scripts/audit_phase6kv_pms_home_callers.py`、`tools/scripts/audit_phase6mg_oobe_helper_scope.py` 與既有 `artifacts/phase6bk/ipc-ota-closure-20260810-02/`、`artifacts/phase6kv/pms-home-caller-closure-20260810-01/`、`artifacts/phase6mg-oobe-helper-scope-20260810-01/`、`artifacts/phase6mc-caller-provenance-20260810-01/`。以新 output directory 或 dry-run 方式執行，避免覆寫既有 artifacts；若工具預設會寫既有路徑，改為只讀 input review，不執行。

次選（僅在需要決定 OTA 路線是否結案時）：擴大 6MM selected static graph，加入 `CacheSizeCheck`、`MakeFreeSpaceOnCache` callers、function-pointer/return-value provenance 與 recovery verifier ordering，分為 direct／indirect-resolved／indirect-unresolved；仍不可執行 updater、OTA 或 crafted path。

不建議下一步做 driver ioctl 或 live Binder/ADB 驗證：這些不是目前 HOME/user-scope evidence 的最小缺口，且明確跨越本輪禁止的裝置 mutation／高風險邊界。

## 6. 盤點結論

6MM 已把 updater 的 block-image registration gap 關閉，6ME 已把選定 MediaTek/Amazon driver source 的 direct HOME/Framework edge 縮為 bounded negative；兩者都沒有建立可安全重播的 launcher route。研究主線目前最小且未重複的候選是離線完成 Amazon IPC/OOBE 的 caller、permission、user-scope、sink provenance，並保留「scanned/selected corpus」限制，不把 bounded negative 升格成 binary-wide absence。
