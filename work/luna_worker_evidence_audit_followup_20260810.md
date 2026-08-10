# Evidence-audit follow-up：Phase 6K–6V

日期：2026-08-10  
公開基準：`a86d01361`  
比較基準：`findings/phase-6pv-broad-route-followup.md`

注意：既有 Phase 6PV 報告標頭另列 `f0c7ad38c412539307ba8fdb76e2596c309bb04c`；
本 follow-up 依委派指定的 `a86d01361` 作為公開基準，未將兩個基準混同。

## 範圍與方法

本次只搜尋主機端既有檔案：`adb/`、`artifacts/`、`findings/`、`output/`。
沒有接觸裝置、沒有執行 ADB、Binder、root、exploit、ioctl、OTA、reboot 或任何
寫入；沒有重做 Phase 6PV 已收斂的測試。以下只列出 Phase 6PV 未以相同粒度
明確收錄、或仍保留重要未知邊界的證據。

## 審計結論

1. 已實際觀察到的普通 App 邊界是 `AmazonActivityManager` prewarm：無權限 APK
   可使 system-server 出現 target process，但保存結果沒有 HOME、package 或
   component sink。這是 authorization anomaly／bounded deputy，不是權限提升
   或 root 證據（`findings/phase-6ku-low-privilege-boundary.md:11-18,57-66`）。
2. KFT tx3 與私有 Amazon PackageManager 的保存結果都在下游 PMS／service
   reachability gate 收斂：User 10 因 cross-user、User 0 因 component-state
   caller gate 被拒；五個候選 private service handle 亦為 `not found`，沒有送出
   transaction（`findings/phase-6ku-evidence-index.md:15-24`；
   `findings/phase-6kv-evidence-index.md:5-7`）。
3. Fire Launcher package/component state 的實際拒絕仍是最強的 runtime boundary：
   `Cannot disable a protected package` 且狀態不變；但 deny-list 內是否直接含
   `com.amazon.firelauncher` 仍未能讀檔確認，應標為 `unknown`，不可改寫成直接
   membership 觀察（`findings/phase-6v-evidence-index.md:16-18,21-25`）。
4. OOBE/OTA 是可能影響 HOME／setup state 的高影響 system lifecycle surface，
   但目前只有 system-server phase-550 + `isUpgrade()` 的靜態鏈；receiver
   permission 的 protected-broadcast membership 與自然 OTA 後時間線仍未知。
   不可把 priority-100 OOBE component 當成 shell 可寫 HOME selector
   （`artifacts/phase6u/bootafter-ota-scope-20260805-01/summary.json` 的
   `finding`、`authorization_status`、`limitations`、`risk_decision` 欄位；
   `findings/phase-6u-report.md:18-25,40-56,70-84`）。
5. updater 具備 partition-write capability 的靜態 callback／script evidence，
   但 recovery caller provenance 未閉合；此項只能是 `unknown` 的 host-only
   research gap，不能推導成 shell route（`artifacts/phase6ku/boundary-20260810-01/result.json` 的
   `execution_policy`、`findings`、`phase6kt_report` 欄位；
   `artifacts/phase6ku/boundary-20260810-01/updater-dispatch.csv:1-25`）。

## 逐項證據

### A. Ordinary App → system service：prewarm 的實際 sink

`findings/phase-6ku-evidence-index.md:5-9` 引用 Phase 6ER 的保存 runtime test：
無 permission ordinary APK 到達 tx1，permission result 被忽略，target process PID
出現；未觀察 HOME/package-state change。對應 host parser 的
`artifacts/phase6k/auth-anomaly-audit-20260805-01/summary.json` 欄位
`prewarm_permission_result_unconsumed_candidate=true`、
`prewarm_has_start_process_marker=true`、`mutation_performed=false`、
`device_contacted=false`，且 `method_line_markers.prewarm` 精確標出
`checkCallingPermission`、`clearCallingIdentity`、`startProcessLocked`。

判定：`closed`（已閉合為 process/resource sink；不是 HOME/package/root sink）。

### B. KFT tx3 與 private PackageManager 的 caller boundary

Phase 6KU index 的 `6KU-IPC-002` 記錄 User 10 cross-user rejection 與 User 0
component-state caller rejection，且沒有 Fire/Tahoe/HOME mutation
（`findings/phase-6ku-evidence-index.md:15-17`）。同一 index 的 `6KU-IPC-003`
記錄 `amazonpackagemanager` 對 shell `not found`，private tx1–tx11 為
metadata/proxy/query，沒有 private User-0 writer（同檔 `:18-20`）。

Phase 6KV 的 static caller inventory 雖有 25 個 invoke sites，報告明確限制為
static-only，沒有新的 `setHomeActivity`／preferred-activity／User-0 restoration
writer（`findings/phase-6kv-pms-home-caller-closure.md:7-18`；
`findings/phase-6kv-evidence-index.md:1-6`）。

判定：`rejected`（保存 runtime caller gate／service visibility 已拒絕）；
static inventory 本身不作 runtime reachability 宣稱。

### C. Fire Launcher state gate 與 deny-list membership 缺口

Phase 6V 將 application/component enabled APIs 收斂到同一
`setEnabledSetting`，在 state write 前呼叫 `isPackageStateProtected`，並由
Amazon callback 以 system app、deny-list、UID 2000 三條件形成 vendor gate
（`findings/phase-6v-evidence-index.md:8-14`；
`findings/phase-6v-pms-control-surface-review.md:21-46,59-76`）。

既有 raw runtime evidence 則是 Fire Launcher disable 回傳
`Cannot disable a protected package` 且狀態不變；同批唯讀 capture 仍是 Fire
priority 50（`findings/phase-6v-evidence-index.md:16-18`）。但是同一 index 的
negative-evidence boundary 明確說 deny-list contents 不可讀，
`com.amazon.firelauncher ∈ deny list` 不能當作 direct observation
（同檔 `:21-25`）。

判定：實際 mutation request 為 `rejected`；deny-list literal membership 為
`unknown`。安全關聯是保護 package/component state 與 HOME candidate，但沒有
新的替代 writer。

### D. Private service visibility：存在不等於 shell 可達

Phase 6T parser summary 的欄位記錄 46 個 interesting services、31 個具有
shell-find denial、455 筆 denial records，且 `binder_transaction_sent=false`
（`artifacts/phase6t/ipc-live-visibility-20260805-01/summary.json` 的同名欄位）。
Phase 6T report 同時保留 HOME resolver 為 Fire priority 50，並明確拒絕未知
`service call`／手寫 Binder transaction（`findings/phase-6t-ipc-live-visibility.md:12-28,39-45`）。

判定：`rejected`（shell service lookup boundary）；service registration 本身不
構成 ordinary App 或 shell 的 privileged route。

### E. OOBE `BOOT_AFTER_SYSTEM_OTA`：高影響但 caller／membership 未閉合

Phase 6U source/report 記錄：system-server boot phase 550 且 `isUpgrade()` 成立
後才建立 action；receiver 可 enable `OobeHomeActivity`，並寫
`user_setup_complete=0`、`isOOBEActive=1`；保存 User 0 dump 則顯示 OOBE HOME
priority 100 但目前在 `disabledComponents`（`findings/phase-6u-report.md:18-56`）。
同一階段把 receiver permission argument 與 permission definition 分開，並將
protected-broadcast membership、自然 OTA 後時間線列為待驗證；手動 broadcast／
enable component 被拒絕（同檔 `:70-84`）。

`artifacts/phase6u/bootafter-ota-scope-20260805-01/summary.json` 進一步以欄位
記錄 `broadcast_sent=false`、`device_contacted=false`、`settings_changed=false`、
`package_state_changed=false`、`recovery_executed=false`、`partition_written=false`。

判定：`unknown`（合法 system-server lifecycle 的後續 HOME 時序與 action
authorization 尚未由保存輸入閉合）；不是 shell HOME selector，也不是 root 證據。

### F. Native updater：capability 已觀察，低權限 caller 未觀察

Phase 6KU 的 `result.json` 將 updater 描述為 24 個 data-driven handlers、含
partition I/O，但 recovery caller provenance／verification 在 bounded audit 外；
`execution_policy` 中 `adb`、`binder`、`native_execution`、`ota_or_recovery`、
`partition_write` 全為 `false`。`updater-dispatch.csv:1-25` 列出 handlers，包含
`package_extract_file`、`write_value`、`run_program`、`reboot_now`；這是 source
capability inventory，不是執行結果。

判定：`unknown`（recovery-to-updater caller provenance 尚未閉合）。安全下一步只
能是主機端 verifier／handoff source review；不得執行 updater、recovery 或 OTA。

## 安全下一步

- 只在 host 上補 protected-broadcast membership、deny-list resource mapping、
  recovery verifier/handoff 與 static caller-to-sink join。
- 若未來自然發生官方 OTA，只做事後唯讀 capture：package/component state、HOME
  resolver、OOBE settings 與 activity timeline。
- 不送未知 Binder transaction，不觸發 OOBE，不讀寫 system-owned deny-list，
  不執行 updater/recovery，不做任何 partition 或 package state mutation。
