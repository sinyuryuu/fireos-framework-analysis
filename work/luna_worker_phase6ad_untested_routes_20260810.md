# Phase 6AD — host-only untested-route probe/analysis matrix

日期：2026-08-10（Asia/Taipei）

## 結論

既有 Phase 6X/6Y/6Z 已覆蓋或否定一般 HOME resolver、priority／set-home、
Fire component state、KFT child/profile runtime、Accessibility foreground、
unknown Binder、driver ioctl、OTA/recovery execution、以及 root exploit。
以下只保留尚未閉合、可由保存的 APK/VDEX/JADX、manifest、ELF、SELinux、
resource、archive 與既有 snapshot 做離線分析的安全入口。它們不是已證明的
可達漏洞或 privilege transition。

矩陣欄位完整版本見 [CSV](./luna_worker_phase6ad_untested_routes_20260810.csv)。

| route | evidence | missing link | safe next step | stop condition | status |
|---|---|---|---|---|---|
| OOBE receiver → exact numeric user → setup/component sink | `findings/phase-6z-evidence-index.md`; `work/luna_worker_phase6z_components_20260810.csv` rows 6Z-001/002; `artifacts/phase6mg-oobe-helper-scope-20260810-01/` | Context 建立、user handle 傳遞、ContentResolver/PMS client 的 numeric user 尚未閉合；不能由 component enable 推成 User 0 HOME writer | 離線追蹤同版本 OOBE source、framework Context/ContentResolver/PMS implementation 與 user-handle callsites，輸出 context→user→sink table；只讀既有檔案與 hash | 任一步需要 broadcast、OOBE trigger、setup-state/component mutation、Binder/service call、OTA/recovery、reboot 或裝置接觸 | untested_host_only |
| DCPMS exported lifecycle receiver → producer/permission → profile-policy sink | `work/luna_worker_phase6z_components_20260810.csv` rows 6Z-003/005/006; `artifacts/phase6bk/protected-broadcast-expanded-20260810-01/` | ACTIVE_PROFILE_UPDATED、account-property 與 SYNC 的實際 producer、permission holder/protection、cross-user acceptance 尚未對上；sink 已是 CDE policy，不是 HOME/PMS | 離線 union manifest/resource/permission definitions、`uses-permission`、caller APK/VDEX 與 receiver code，建立 producer→gate→identity/user→sink provenance rows | 需要發送 action、廣播重播、service/Binder call、跨 user mutation、帳號/profile mutation 或 live inventory | untested_host_only |
| ProductPolicy fosinit registration → Binder publication → caller gate | `work/luna_worker_phase6z_components_20260810.csv` row 6Z-007; `artifacts/phase6bg-product-policy-readonly-20260805-01/`; `findings/phase-6x-report.md` | 已知 system-server/in-process registration，但 publication descriptor、SELinux/service-manager rule、caller permission/UID、user scope 與 sensitive sink 未形成完整鏈 | 只讀比對 fosinit、service registration strings、AIDL/Stub/Proxy、permission XML、SELinux allow/find AVC 與 downstream callsites；不呼叫 service | 需要 `service call`、未知 transaction、取得 live handle、反射/模糊測試、settings/package/user mutation 或任何 device query | untested_host_only |
| AmazonActivityManager `preWarmApplicationForUser` → identity/user propagation → process/state sink | `findings/phase-6x-prewarm-authorization.md`; `work/luna_worker_phase6up_asp_prewarm_closure_20260810.csv`; `artifacts/phase6bk/ipc-ota-closure-20260810-02/` | APP_PREWARM check result consumption、clearCallingIdentity 後的 caller provenance、user argument propagation 與 downstream effect 尚未完整對上；已知 Alexa caller 不是普通 shell proof | 離線擴大保存 Amazon APK/VDEX/JADX、AIDL proxy、permission grant/UID、`startProcessLocked` user flow 與 sink inventory；將 process prewarm 與 HOME/package sink 分列 | 需要 Binder invocation、process launch、service lookup、package/settings mutation、未知 transaction 或裝置接觸 | untested_host_only |
| `USE_SDK` / `PLUGIN` / `PLUGIN_CONSUMER` declaration → consumer/holder/grant → sensitive sink | `work/luna_worker_phase6y_permission_20260810.csv`; `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt` | declaration 已找到，但 requester、holder/grant、exported consumer、method-local gate 與 downstream sink 均未 joined；低 protection 不等於可達 | 對保存 exact manifest、APK/VDEX/JADX 做 permission name union、requester/holder/grant、exported component、checkCallingPermission 與 sink mapping；保留 UNKNOWN，不自行解碼缺失 protection level | 需要安裝/授權 permission、啟動 component、Binder/service call、runtime grant、settings/package mutation 或 live device check | untested_host_only |
| OTA verifier/canonicalization → indirect extraction/write sink | `findings/phase-6y-ota-staging-boundary.md`; `artifacts/phase6mk-updater-dispatch-20260810-04/`; `artifacts/phase6kt/recovery-verifier-audit-20260810-01/` | registry/handler 與 canonicalization marker 已見，但 verifier→canonicalization→extraction/write 的 indirect function-pointer、argument provenance、error branch 尚未完整閉合 | 只讀擴大 selected native disassembly/debugdata/ELF symbols/relocations 與 updater-script mapping，標註 direct／indirect-unresolved／not-selected；不餵輸入 | 需要執行 update-binary、recovery、UpdateSystem.install、crafted/malformed/symlink/traversal OTA、partition write、fastboot、reboot 或 device contact | untested_host_only |

## 明確排除的重複路線

不新增 component-disable、priority、set-home、unknown Binder transaction、
driver node/ioctl、OTA execution/recovery、root exploit，也不把保存的 ADB
capture 當成本輪新 runtime probe。所有 `UNKNOWN` 僅代表 host-side evidence
缺口，不代表可達性或漏洞。

## 本輪操作界線

本輪只讀搜尋既有 `adb/`、`findings/`、`output/`、`work/`、`tools/` 並新增本
文件與 companion CSV；未執行 adb，未連接或修改裝置，未修改既有檔案。
