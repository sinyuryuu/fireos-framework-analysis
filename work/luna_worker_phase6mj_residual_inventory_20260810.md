# Phase 6MJ residual inventory（2026-08-10）

本輪只讀取公開 HEAD、既有 findings、README／PROJECT_STATUS、adb、artifacts、
decompiled、firmware 與 tools/scripts。沒有重跑已完成的 Priority／HOME／
component-disable／外層 source-tar 審計；沒有 ADB、網路、Binder/service call、
ioctl、Root/exploit、OTA/recovery/fastboot/reboot，也沒有套件、設定、分割區或
其他裝置變更。

## 未閉合 residuals

| Residual / caller→permission→user scope→state sink | Evidence ID／檔案路徑 | 分類 | 最小 host-only 下一步 |
|---|---|---|---|
| `BootAfterSystemOTAReceiver` → system-server `boot phase 550` + `isUpgrade()` → `RECEIVE_BOOT_AFTER_SYSTEM_OTA` receiver-permission → `PackageHelper.enableComponent(context)`／`SettingsDBUtils`；`Context`、`ContentResolver` 與 PackageManager client 的實際 user scope 尚未落實 | `6MG`：`findings/phase-6mg-oobe-helper-scope.md:22-69`; `6N`：`findings/phase-6n-oobe-helper-analysis.md`; `6Z-001/002/004`：`findings/phase-6z-evidence-index.md:7-10`; `artifacts/phase6mg-oobe-helper-scope-20260810-01/` | 待驗證 | 只對保存的 OOBE JADX、framework client、`ContentResolver`／`PackageManager` 呼叫實作做 source／DEX data-flow，標出 context 建立、user handle、Binder identity 與 component/settings sink；不觸發 broadcast、OOBE 或寫 state。 |
| Amazon private Binder（尤以 `preWarmApplicationForUser()`、`AmazonProfileService.initiateLauncher()` 為焦點）→ service registration／Proxy-Stub → permission／caller UID → target user／sink；保存 corpus 只找到 Alexa caller，未完成所有 Amazon APK／native caller inventory | `6N`：`findings/phase-6n-ipc-provenance.md:43-62`; `6X-PW-001/002/006/010`：`findings/phase-6x-prewarm-authorization.md:19-72,109-132`; `6Q-BIND-001/003/006`：`findings/phase-6q-evidence-index.md:45-60` | 待驗證 | 對既有 APK／DEX、AIDL／Stub／Proxy、`fosinit` registration 做離線 caller inventory；每列固定記錄 caller、service lookup、permission、UID／identity clear、user argument、state sink，將 `startProcessLocked`／profile picker 與 HOME/package sink 分開。 |
| `BOOT_AFTER_SYSTEM_OTA` → OOBE receiver action；receiver declaration 與 sender permission argument 已見，但完整 matching Fire OS protected-broadcast membership 仍未由保存 decoded framework-res 證實 | `6W`：`findings/phase-6w-exported-component-surface.md:30-47,138-144`; `6Z-005/006`：`findings/phase-6z-evidence-index.md:11-12`; `artifacts/phase6w/oobe-protected-broadcast-20260805-01/` | 待驗證 | 只比對同版本、已有 provenance 的 framework-res／framework source／resource overlay 與 action membership，保留 bounded-negative 標記；不得以 `am broadcast` 或未知 Binder 取代靜態證據。 |
| PS7331 `update-binary` registration／parser → `PackageExtractFileFn`／`ExtractEntryToFile` → `ota_open`／`open`、以及 `WriteToPartition`／`PerformBlockImageUpdate` → `ota_write`／`write`／`rename`；verification 到 write 的完整 indirect edge 與 function-pointer registry 尚未全解 | `6P-ELF-001/6P-SYM-001/6P-CFG-001/6P-WRITE-001/6P-VERIFY-001`：`findings/phase-6p-native-updater-evidence-index.md`; `E6T-CALL-001/002/003`：`findings/phase-6t-call-graph-evidence-index.md`; `findings/phase-6md-native-updater-path-audit.md:42-85` | 已證實（能力）／待驗證（完整鏈） | 使用既有 `artifacts/phase6s/ota-debugdata-audit-20260805-01/`、`ota-cfg-focus-20260805-01/` 與 `ota-call-edges-20260805-01/`，host-only 解碼 registry、indirect call、error path，輸出 direct／indirect-unresolved／未在選定 graph 三態表；不執行 updater 或 recovery。 |
| native updater 的 `symlink_realpath`／`readlinkat`／`readlink` markers → extraction／partition-write guard 的實際 canonicalization 關係；目前 `__readlink_chk` 只定位到 `MakeFreeSpaceOnCache`，未證實 traversal 或 symlink bypass | `6P-PATH-001`：`findings/phase-6p-native-updater-evidence-index.md`; `findings/phase-6md-native-updater-path-audit.md:68-85,116-129`; `6Y-OTA-001..009`：`findings/phase-6y-evidence-index.md:5-13` | 待驗證 | 對保存 native `.text`／debugdata 以 symbol-guided basic-block、argument provenance 與 return/error branches 做 host-only trace，並與 Java staging 的 basename／rename／copy、verification-before-install 順序對齊；不製作 crafted、symlink 或 traversal OTA。 |

## 已完成、已排除與風險拒絕項目

| 項目 | Evidence ID／檔案路徑 | 分類 | 最小 host-only 下一步 |
|---|---|---|---|
| Phase 6MI outer source tar 已讀至 real EOF：35 members、23 regular files、12 directories、0 symlink／hardlink；只命中 launcher payload 名稱，沒有 OTA／post-install／partition control member | `6MI-SOURCE-001/002`、`6MI-OTA-001`、`6MI-GRAPH-001`：`findings/phase-6mi-evidence-index.md`; `findings/phase-6mi-source-tar-eof.md` | 已證實／已排除（外層 source tar 隱藏 updater 路線） | 不重跑外層 tar；若需延伸，只對已存在的 nested source index 做 host-only provenance，不把 source tar 當 installable OTA。 |
| OOBE receiver 的 guarded side effect（enable OOBE Home、setup-state writes）已靜態證實，但不是 ordinary shell HOME selector；live/manual activation 未做 | `6Q-OOBE-001/002`：`findings/phase-6q-evidence-index.md:76-83`; `6Z-001/002/004`：`findings/phase-6z-evidence-index.md:7-10` | 已證實（靜態 side effect）／已排除（普通 shell HOME route） | 只做上表的 context-to-user 與 protected-broadcast 靜態 closure；不人工 broadcast、enable component 或寫 provisioning state。 |
| selected private Amazon services 的 shell UID 2000 `service_manager find` denial；13 focus methods 的既有 host-only review 未形成 shell Binder execution 或 HOME/package sink | `6Q-IPC-001`、`6Q-BIND-006`：`findings/phase-6q-evidence-index.md:41-60`; `findings/phase-6s-ipc-focus-review.md:17-93` | 已證實（保存 capture）／已排除（目前 shell route） | 只擴大保存 corpus 的 caller／SELinux policy provenance；不猜 transaction code、不 fuzz service、不重跑已完成 Binder boundary。 |
| OTA Java staging 已確認 metadata／signature／product／PVT／recovery checks precede move and `UpdateSystem.install`；Java scope 未見 canonical/no-follow marker，不能升格為漏洞 | `6Y-OTA-004..008`、`6Y-SAFETY-001`：`findings/phase-6y-evidence-index.md`; `findings/phase-6y-ota-staging-boundary.md:39-67` | 已證實（Java ordering）／已排除（僅憑 marker 推導 traversal） | 只做 native/recovery 靜態 provenance 與 path data-flow closure；不得 crafted OTA、symlink/traversal/collision 測試。 |

## 明確因風險拒絕／不可重跑

- 不執行 `update-binary`、Recovery、`UpdateSystem.install`、sideload 或任何分割區寫入；不製作 malformed／downgrade／symlink／traversal OTA。
- 不人工發送 `BOOT_AFTER_SYSTEM_OTA`、啟用 `OobeHomeActivity`、寫 `user_setup_complete`／`isOOBEActive`，也不以未知 Binder transaction、service fuzzing 或 system-server injection 取得 caller／permission 結論。
- 不重跑已完成的 ordinary HOME／Priority、Fire component-disable／package-state mutation、KFT/profile-owner、外層 source-tar EOF 審計；不執行 ADB、網路、ioctl、Root/exploit、fastboot、reboot、package／settings／partition mutation。

## 既有 host-only 驗證結果

- Phase 6MI：`adb_used=false`、`ota_executed=false`、`recovery_used=false`、`binder_transaction_sent=false`、`device_mutation=false`；outer tar EOF 與 member classification 均完成。
- Phase 6P／6T：ELF／`.gnu_debugdata`／symbol-guided direct-call review、registration／verification／write boundary 已保存；`E6T-CALL-003` 明載 `device_contacted=false`、`updater_executed=false`、`partition_written=false`。
- Phase 6Q／6S／6X：Binder service inventory、permission/caller review、prewarm static authorization review 完成；沒有 Binder transaction、process start、OOBE activation 或 state mutation。
- Phase 6Y：staging audit summary `6Y-SAFETY-001` 明載沒有 device、OTA、recovery、updater 或 filesystem mutation。

本檔是本輪唯一新增檔案；未修改其他檔案，亦未 commit／push。
