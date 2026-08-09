# Phase 6ML inventory — HEAD 921179ff9（2026-08-10）

本報告是唯讀盤點；基準為 `921179ff9d7f12c7633becc1093f709b06b7b395`
（Phase 6MK）。工作樹在盤點前已有大量 modified／untracked 使用者內容；本輪只
新增本檔，未修改其他檔案，未 commit/push/reset/clean/checkout。

## 1. Phase 6MK 後新增或未追蹤內容

以檔案 mtime `2026-08-10 00:00:00`、`git status` 與檔案內容交叉比對：

### Reports / findings

- `reports/` 沒有該時間點後新檔。
- 新增的可讀報告／索引集中在：
  `findings/phase-6bk-followup-20260810.md`、
  `findings/phase-6bk-followup-evidence-index-20260810.md`、
  `findings/phase-6bk-*.md`、
  `findings/phase-6kt-*`、`phase-6ku-*`、`phase-6kv-*`、`phase-6kw-*`、
  `phase-6ky-*`、`phase-6lz-*`、`phase-6ma-*`、`phase-6mb-*`、
  `phase-6mc-*`、`phase-6md-*`、`phase-6me-*`、`phase-6mf-*`、
  `phase-6mg-*`、`phase-6mh-*`、`phase-6mi-*`、`phase-6mk-*`、
  `phase-6n-*`、`phase-6o-*`、`phase-6p-*`。
- 既有 worker context：`work/luna_worker_phase6mj_residual_inventory_20260810.md`。
  此檔不是本輪新增，且已先列出五個 residual；6MK 只完成其中 updater
  registration／dispatch 部分。

### Artifacts

目前可辨識的新增 artifact roots（皆為 dirty/untracked corpus 的一部分）如下：

- 6BK：`artifacts/phase6bk/ipc-ota-closure-20260810-01/02/`、
  `protected-broadcast-expanded-20260810-01/`、
  `protected-broadcast-union-20260810-02/`。
- 6KT–6KW：
  `artifacts/phase6kt/recovery-verifier-audit-20260810-01/`、
  `artifacts/phase6ku/boundary-20260810-01/`、
  `artifacts/phase6kv/pms-home-caller-closure-20260810-01/`、
  `artifacts/phase6kv/source-scope-20260810-01/`、
  `artifacts/phase6kw-vendor-home-callbacks/`。
- 6MB–6MC：Vending／Alta JADX、static、caller provenance、permission-holder
  audit（`artifacts/phase6mb-*`、`artifacts/phase6mc-*`）。這些是分析輸入／
  permission census，不是新的 HOME writer 證明。
- 6MD–6MI：native updater path、driver edges、OOBE helper scope、package-state
  writers、source-tar EOF（`artifacts/phase6md-*` 至 `artifacts/phase6mi-*`）。
- 6MK：四次相同 schema 的 canonical output：
  `artifacts/phase6mk-updater-dispatch-20260810-01/` 至 `-04/`，以及
  `output/tables/phase6mk-updater-dispatch-20260810-04.csv`、
  `output/call-graphs/phase6mk-dispatch-canonicalization-20260810-04.mmd`。

### Scripts

相應 host-only scripts 包含：

`tools/scripts/build_phase6bk_ipc_ota_closure.py`、
`capture_phase6bk_child_profile_submission.py`、
`audit_phase6kt_recovery_provenance.py`、
`build_phase6ku_boundary.py`、
`audit_phase6kv_pms_home_callers.py`、`audit_phase6kv_source_scope.py`、
`audit_phase6kw_vendor_home_callbacks.py`、
`audit_phase6ky_amazon_ipc_boundaries.py`、
`audit_phase6mg_oobe_helper_scope.py`、
`audit_phase6mc_permission_holders.py`、
`build_phase6mc_caller_provenance.py`、
`audit_phase6mk_updater_dispatch_closure.py`。

### ADB captures（只作既有檔案證據；本輪沒有讀取裝置）

- `adb/phase6bk/PHASE6BK-KFT-PREFLIGHT-RO-20260810-01/`
- `adb/phase6bk/PHASE6BK-KFT-RUNTIME-20260810-01/`
- `adb/phase6bk/PHASE6BK-SERVICE-RO-20260810-01/`
- `adb/phase6bk/PHASE6BK-STATE-RO-20260810-01/`
- `adb/child-profile-tests/CHILD-TEST-20260810-01/02/03-POST/05-POST-RO/06-POST-RO/`
- `adb/phase6mb-vending-20260810-01/`
- `adb/phase6mc-alta-static-20260810-01/`
- `adb/phase6mc-permission-holders-20260810-01/`
- `adb/phase6n/PHASE6N-KERNEL-RO-20260810-01/`

這些 capture 含唯讀 baseline、服務可見性、HOME/package state、child-profile
UI 後狀態及 permission census；它們不是本輪可重跑授權。報告中不把 capture
檔名內的 `adb` 當成本輪已執行裝置操作。

## 2. 6BK／6MJ／6MK 與既有 findings 的整合

| 結果 | Evidence ID／路徑 | 與既有 finding 的關係 | Confidence |
|---|---|---|---|
| Amazon IPC/OTA 仍是 system/Amazon permission、PackageManager gate 與 recovery boundary | `6BK-IPC-001/002/003`、`6BK-OTA-001/002`、`artifacts/phase6bk/ipc-ota-closure-20260810-02/result.md` | 與 Phase 6Q/6S/6X、6Y 一致；沒有普通 shell/app 到 HOME/package-state 或 recovery updater 的新可達鏈 | Strong evidence |
| Tahoe child-profile workflow 可到達，但 post-submit 沒有新增 Android user；User 0 HOME 仍 Fire Launcher | `6BK-FU-UI-001..005`、`adb/child-profile-tests/CHILD-TEST-20260810-06-POST-RO/` | 與既有 KFT finding 一致；不可把應用層 `CreateAndroidUserCommand` log 當成 system-server user 建立成功 | Confirmed／high-confidence inference |
| `BOOT_AFTER_SYSTEM_OTA` 在 45 個指定 APK 中只有 `android.amazon.perm` 命中 | `6BK-FU-BC-001..003`、`artifacts/phase6bk/protected-broadcast-union-20260810-02/summary.json` | 將 Phase 6W/6Z 的 protected-broadcast residual 收斂到「scanned-source confirmed」；scope limitation 仍與既有 bounded-negative 定義一致 | Confirmed in scanned set；非 global |
| PMS HOME caller sites 與 vendor callback 已做靜態 closure | `artifacts/phase6kv/pms-home-caller-closure-20260810-01/pms-home-callers.csv`、`artifacts/phase6kw-vendor-home-callbacks/result.md` | 與 Phase 6KY 一致：AppCompat delegate/標準 fallback，Eve callback null；沒有 Fire literal 或新的 User-0 HOME writer | Confirmed／strong evidence |
| OOBE helper 仍缺 context→ContentResolver/PackageManager 的實際 user mapping | `6MG`、`findings/phase-6mg-oobe-helper-scope.md`、`artifacts/phase6mg-oobe-helper-scope-20260810-01/` | 與 Phase 6MJ residual 一致；已證實 setup/OOBE side effect，但不能推成 User 0 或普通 HOME writer | Confirmed shape；scope pending |
| native updater registry 已具體化；`package_extract_file`→`ota_open/open` 與 partition-write capability 是 recovery path | `6MK-REG-001/002`、`6MK-ENTRY-001`、`6MK-SCRIPT-001`、`artifacts/phase6mk-updater-dispatch-20260810-04/summary.json` | 與 Phase 6P/6T/6MD/6KT 一致；6MK 關閉 registration gap，不關閉 verifier→canonicalization→write 的完整鏈，也不產生 HOME route | Confirmed／strong evidence |
| canonicalization marker 存在，但 selected graph 未見其直接進入 extraction/write sink | `6MK-CANON-001`、`6MK-MARK-001` | 與 6MJ 的 residual 完全一致：bounded negative，不可升格為無 traversal/symlink bypass | Probable bounded negative |

沒有發現互相矛盾的結果。最重要的語義界線是：`6BK` 的 live/capture 結果、
`6KV/6KW` 的 selected static closure 與 `6MK` 的 selected native graph 都是
bounded evidence；它們不能合併成「沒有任何 runtime path」的 binary-wide absence。

## 3. 尚未閉合的最小 host-only candidates

下列候選已排除已完成測試，不重做 ordinary HOME/PMS priority、Fire Launcher
component mutation、KFT runtime、已完成 source-tar EOF 或既有 shell Binder
boundary。

### C1 — OOBE context/user-scope data-flow closure

- Evidence：`6MG`；`findings/phase-6mg-oobe-helper-scope.md:22-69`；
  `artifacts/phase6mg-oobe-helper-scope-20260810-01/`。
- 最小操作：離線比對保存的 OOBE JADX、同版本 framework `Context`、
  `ContentResolver`、`PackageManager` client implementation，追蹤 context 建立、
  user handle、Binder identity 與 `PackageHelper`/Settings sink；只輸出
  user-scope mapping table。
- 命令（若重現）：`python3 tools/scripts/audit_phase6mg_oobe_helper_scope.py`
  （必要時依 script help 指定既有輸入與 output；不得以 live trigger 補洞）。
- Confidence：目前 shape **Confirmed**；User mapping **待驗證**。
- 明確禁止：不得發送 `BOOT_AFTER_SYSTEM_OTA`、啟用 `OobeHomeActivity`、寫
  provisioning/setup state、觸發 OOBE/OTA/recovery、未知 Binder/service call、
  package/settings mutation、reboot。

### C2 — Amazon private IPC caller→permission→user/sink inventory

- Evidence：`6BK-IPC-001..003`、`6X-PW-*`、`6KV`、`6KY`；
  `artifacts/phase6bk/ipc-ota-closure-20260810-02/`、
  `artifacts/phase6kv/pms-home-caller-closure-20260810-01/`。
- 最小操作：只對保存 APK/VDEX/JADX、AIDL/Stub/Proxy 與 fosinit registration
  做離線 caller inventory；每列固定 caller、service lookup、permission、UID/
  identity clear、user argument、state sink，將 `preWarmApplicationForUser` 的
  `startProcessLocked` 與 HOME/package sink 分開。
- 命令（若重現）：
  `python3 tools/scripts/audit_phase6ky_amazon_ipc_boundaries.py --output-dir output/tables/phase6ky-validation`
  或既有 `python3 tools/scripts/audit_phase6kv_pms_home_callers.py`。
- Confidence：selected corpus 對「沒有新增 User-0 formal HOME writer」為
  **Strong evidence**；完整 Amazon caller universe **待驗證**。
- 明確禁止：不得 `service call`、未知 Binder transaction、service fuzzing、
  process-start probe、ADB/device query、Root/exploit、package/settings mutation。

### C3 — Protected-broadcast membership completeness

- Evidence：`6BK-FU-BC-001..003`；
  `artifacts/phase6bk/protected-broadcast-union-20260810-02/summary.json`；
  `findings/phase-6w-exported-component-surface.md`。
- 最小操作：只對同版本且已有 provenance 的 framework-res、Amazon permission
  APK、resource overlay 與保存 manifest 做 input-union/hash completeness audit，
  明確輸出 scanned set、omitted set、action membership；不要擴張成 runtime global。
- 命令（若重現）：以既有 protected-broadcast source-audit 腳本／輸入重建 union；
  報告中未找到一個可安全重跑且不覆寫既有 artifact 的 canonical command，故此項
  應先做 command/input manifest review。
- Confidence：指定 45 APK 集合內 **Confirmed**；全映像 membership **待驗證**。
- 明確禁止：不得發送 broadcast、直接觸發 OTA lifecycle、Binder/service call、
  裝置 inventory、package/settings mutation、reboot。

### C4 — Native updater indirect verifier/canonicalization→sink closure

- Evidence：`6MK-REG-001/002`、`6MK-ENTRY-001`、`6MK-CANON-001`、
  `6MK-SAFETY-001`；`artifacts/phase6mk-updater-dispatch-20260810-04/`；
  `artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json`。
- 最小操作：擴大既有 `.text`/debugdata/disassembly selected window，僅用
  symbol-guided basic-block、function-pointer registry、argument provenance、
  return/error branch 把 `RegisterBlockImageFunction`、`MakeFreeSpaceOnCache`、
  verifier 與 extraction/write sink 分成 direct／indirect-unresolved／not-selected
  三態；不測試輸入。
- 命令（若重現）：
  `python3 tools/scripts/audit_phase6mk_updater_dispatch_closure.py --dry-run --binary firmware/extracted/PS7331/META-INF/com/google/android/update-binary --symbols artifacts/phase6s/ota-debugdata-audit-20260805-01/debugdata-function-symbols.csv --edges artifacts/phase6s/ota-call-edges-20260805-01/call-edges.csv --disassembly artifacts/phase6s/ota-cfg-focus-20260805-01/focus-disassembly.txt --strings artifacts/phase6p/callback-ota-audit-20260805-02/native/strings-matched.txt --updater-script firmware/extracted/PS7331/META-INF/com/google/android/updater-script --output artifacts/phase6mk-updater-dispatch-review/`
- Confidence：registration／handler mapping **Confirmed/strong evidence**；
  canonicalization→write complete chain **待驗證**。
- 明確禁止：不得執行 `update-binary`、Recovery、OTA/sideload、crafted/malformed/
  symlink/traversal OTA、`UpdateSystem.install`、partition write、fastboot、reboot、
  Root/exploit 或任何裝置接觸。

## 4. 結論與安全邊界

最小且不重複的後續順序是 C1（OOBE user scope）→ C2（Amazon caller inventory）→
C3（protected-broadcast completeness）；C4 只有在仍需決定 OTA 路線是否結案時才
做，並維持 host-only selected-graph 語義。現有證據支持「Fire Launcher/HOME 的
普通 shell 替換路線未建立」、「Amazon IPC 的可疑能力仍落在受權限／profile／
system lifecycle 的 bounded path」、「OTA/post-install 有高權限 capability 但
沒有安全的 shell route」。任何 bounded negative 都不得改寫成全域不存在。

