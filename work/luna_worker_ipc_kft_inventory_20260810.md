# Luna worker：Framework/Amazon IPC、KFT child-user、PMS writer、Home callback inventory

日期：2026-08-10  
範圍：只讀工作樹整理；未連接設備、未發送 Binder/service call、未執行 exploit、ioctl、OTA、recovery、root，也未修改裝置狀態。  
信心度用語：Confirmed = 靜態與既有保存結果相互支持；Strong = 有明確 bounded/static 或 runtime 支持，但仍有範圍限制；Medium = 有局部證據，不能外推。

## Executive conclusion

1. 目前唯一同時具備「Fire package-state writer 靜態 sink」與「實機 child lifecycle attribution」的 caller 是 `AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)`。它啟用 Tahoe child launcher，並對 Fire/Launcher3 寫入 disabled state；實際 target 是傳入的 `UserInfo.id`，保存的 runtime trace 是 User 10。下游是受信任 Amazon/system lifecycle 呼叫 PMS，並非 shell/ordinary-app caller；shell 對 private service 的 `find` 被 SELinux 擋住。
2. 沒有確認可寫 User-0 Fire Launcher state 的低權限 caller。標準 shell PMS setter 進入 protected-package/cross-user gate；Amazon private `amazonpackagemanager` Binder 沒有 formal HOME/package-state setter；ProductPolicy、Espresso、OOBE 等 writer 不是已證實的 User-0 Fire writer。
3. 已確認不是 User-0 HOME selector 的路徑包括：KFT child/Tahoe lifecycle、AmazonProfileService AMS callback/profile picker、Fire Launcher app lifecycle、GUI Default Apps/Home route、非-child HOME candidate inventory，以及 private Amazon Package Manager metadata/query Binder。
4. 剩餘最小缺口應限於 host-only：完整化已知 callback 的 method-level return/data-flow、補齊 KFT tx3 的完整 static authorization/caller mapping、釐清 OOBE writer 的 user mapping、以及保存 deny-list provenance。不要重做已 closure 的裝置測試或猜測 transaction。

## 1. 已確認可寫 Fire Launcher state 的 caller / scope / permission / evidence

| Evidence ID | 檔案（含關鍵位置） | SHA-256 | 結論與信心度 | 建議 |
|---|---|---|---|---|
| `LUNA-KFT-STATIC-001` | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325`；同一 caller 在 `findings/phase-6mh-package-state-writer-closure.md`、`findings/phase-6er-kft-child-switch-attribution.md` | VDEX `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`; finding `926dd8158f664889dbae58a4d9980fed7f816f222dbbfbb03659c5422290f4af` | `enableKftLauncherComponent(UserInfo)` 含 Tahoe、Fire、Launcher3 literals；三個 setter 使用 `UserInfo.id`，因此是 child/profile-scoped writer，不是 unconditional User 0 writer。**Confirmed（caller/sink/scope）** | 只做 host-only 完整 method/stub/caller mapping；不要送 tx3。 |
| `LUNA-KFT-RUNTIME-001` | `adb/phase6gp/PHASE6GP-CHILD-HOME-SWITCH-20260807-01/sha256sums.txt`；`findings/phase-6gp-child-home-activation-runtime.md` | manifest `677501d4806b77e8a52adaab472d74bdfa36720aebb8fcda2b97a2a72cb6a32b`; finding `39d7916bb779346dd0779716d29f4a79595c0e55d3f5eaf7fb5f70b8aedbba24` | User 10 active 時 Tahoe HOME，User 10 Fire enabled state 為 child-local；回 User 0 後 Fire HOME priority 50、User 0 Fire state 未變。**Confirmed** | 視為既有 KFT positive attribution；不再以 User 0 假設重跑。 |
| `LUNA-KFT-ATTR-001` | `findings/phase-6er-kft-child-switch-attribution.md`；`adb/phase6dr/PHASE6DR-POST-UNLOCK-FINAL-GUARD-20260806-01/result.json` | finding `926dd8158f664889dbae58a4d9980fed7f816f222dbbfbb03659c5422290f4af`; result `2592110f136dffbd399c3c5a320f6fbcd2f3c6e7de4effede86b5487d52c70a9` | clean child switch/rollback trace：User 10 KFT/ProductPolicy activity，回 User 0 仍 Fire；沒有 `setHomeActivity`、`restorePreferredActivities` 或 User-0 package write。**Confirmed** | 用作排除「KFT 是 User-0 restoration watchdog」的主證據。 |
| `LUNA-KFT-GATE-001` | `findings/phase-6dr-child-lock-kft-revalidation.md`；`findings/phase-6el-kft-child-start-locked-boundary.md` | finding `phase-6dr` 本身未另列 canonical hash；`phase-6el` 檔案 SHA 未納入本報告計算 | 公開 `am switch-user` 只啟動既有 child；locked child 只到 FallbackHome，unlock 後才有 Tahoe child HOME。PMS setter 是 trusted internal lifecycle sink，非 shell mutation。**Strong** | 只補 host-only user-scope/authorization 文檔，不做 unlock、PIN、KFT 或 package mutation。 |
| `LUNA-PMS-GATE-001` | `decompiled/baksmali/vdexExtractor/services/disassembly.log:953377-953568`、`:505771-505837`、`findings/phase-6h-framework-ipc.md` | services VDEX `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`; finding `30a0e39e0b7b3b42c38ef799d04b55a80782eac7fd5ffb3857ab3befa3c17b1f` | PMS 取得 Binder caller UID，執行 cross-user/protected-package gate；Amazon callback 以 system-app、deny-list membership、shell UID 2000 條件保護。**Confirmed（gate）；不等於 caller 可寫** | 不重跑 Fire `pm/cmd package` disable/component test；保留既有拒絕結果。 |
| `LUNA-SHELL-REACH-001` | `adb/phase6ep/PHASE6EP-AMAZON-WRITER-REACHABILITY-20260809-191243/result.json`；`findings/phase-6kv-pms-home-caller-closure.md` | `465be89b25ec6b731fd8d1f3de57636a8265a9a4ce5fdb61c69e3ba0bd73cd59`; finding `a3c3d90315895c8295c8cee73f889f020b96f31cded80fa9e1672dc9ae598ef1` | 五個候選 Amazon private handles 均 `not found`；未送 transaction；HOME/Fire User 0 unchanged。**Confirmed（current reachability boundary）** | 不做 `service call`、parcel guessing、caller spoofing 或 service injection。 |

### Permission / caller interpretation

- KFT writer 的實際 caller 是 trusted Amazon child/profile lifecycle；保存資料沒有證明 ordinary caller 能呼叫 `IAmazonUserManager` tx3。其 downstream PMS calls 是 privileged/system-side，並以 `UserInfo.id` 作 user scope。
- `IAmazonPackageManager` private Binder 的 metadata/flag writers 受 `ADD_RM_PKG_METADATA` 等服務權限與 service-manager/SELinux 邊界；它不暴露 `setApplicationEnabledSetting`、`setComponentEnabledSetting` 或 formal HOME setter。Facade 的 setter 反而 delegate 到標準 `IPackageManager` tx90/tx92，仍受 PMS gates。
- `PackageManagerShellCommand` 是 setter front end，不是 permission bypass；其 Fire 測試已被 protected-package 邊界關閉。

## 2. 已確認不是 User-0 HOME selector 的路徑

| Evidence ID | 檔案 | SHA-256 | 結論與信心度 | 建議 |
|---|---|---|---|---|
| `LUNA-AMZ-PM-001` | `findings/phase-6ia-amazon-package-manager-closure.md` | `9169af04fe4ebee3e1645d4b097bd07c63cb6d5d3a1329bfc46c6f2421a3f500` | private Binder tx1–tx11 是 metadata/flags/proxy/query；service lookup 對 shell `not found`；facade setters 走標準 PMS。**Confirmed** | 不重做 private service lookup；更不要送 private metadata transaction。 |
| `LUNA-PMS-HOME-001` | `artifacts/phase6kv/pms-home-caller-closure-20260810-01/pms-home-callers.csv`、`findings/phase-6kv-pms-home-caller-closure.md` | CSV `dc1a86ea85904e3775704944fa86364a9a89033f6146eed0dac8b324b7028382`; finding `a3c3d90315895c8295c8cee73f889f020b96f31cded80fa9e1672dc9ae598ef1` | 25 static invoke rows；KFT 是唯一 launcher-specific Amazon writer；沒有新的 Amazon `setHomeActivity`/preferred-HOME writer。**Strong** | 只可擴展 host parser scope；不把 static row 當 runtime reachability。 |
| `LUNA-SINK-001` | `artifacts/phase6mw-home-state-sinks-20260810-01/summary.json`、`sink-calls.csv`；`findings/phase-6mw-home-state-sink-closure.md` | summary `e1320c614c5fc6a6c91d3871fa3be088197c319571bf0b25d2e24711822221bc`; CSV `51b924ec70b32c21d121f99b64ab997dace4bee805c52c86439808eaaf6a15e6`; finding `f7286718ac7a92f11c2d967a01052f2373189f495decb45d9940ddda646b8231` | 175 bounded sink/reference rows，59 HOME/preferred-related；Fire literal 只有 static reference，不能證明 User-0 writer。**Strong** | 依 review queue 做 host-only caller/permission/user mapping；不要由 literal 推導 exploit。 |
| `LUNA-CALLBACK-001` | `findings/phase-6er-ams-home-callback-boundary.md`；`adb/phase6er/PHASE6ER-AMS-CALLBACK-HOME-20260807-02/sha256sums.txt` | finding `0dec0755ccce0e2d644ac9395331bd2ded4ada90a4e4d00788638524b03b2d37`; manifest `1067d6a4554da6e122f8670c0b16ed44e58c4a2638b039b49acd5610f71a27b4` | Settings → normal HOME transition 觸發 profile lookups，但 Fire priority 50 正常勝出；未看到 HOME resolver/package re-enable write。**Strong** | 只做 callback return/data-flow host analysis；不做 profile-picker/KFT transition replay。 |
| `LUNA-LAUNCHER-001` | `findings/phase-6eg-firelauncher-lifecycle-writer-closure.md` | `63410418709e47ef059d86ff54c28e344d79318ef220523e430d134e985ff03a` | Fire Launcher app lifecycle review 找到低儲存 receiver disable，沒有 package state、preferred HOME 或 resolver writer；BackupAgent 也未成為 PMS HOME writer。**Strong** | 停止重複 package-event、global-sync、BackupAgent、ordinary launcher process 實驗。 |
| `LUNA-GUI-001` | `findings/phase-6fo-gui-default-apps-home-boundary.md` | 未另納入 hash；報告內容明確記錄 no Home row/selector | Fire Settings Default Apps 沒有 Home selector；內部 `DefaultHomePicker` 不在 exported fragment route；Microsoft Home row 回到同頁。**Strong** | 不再做 GUI Home picker 或 Fire App Info disable 重試。 |
| `LUNA-CANDIDATE-001` | `findings/phase-6ij-user0-home-candidate-closure.md` | `1d38d8aeaf37c5dfea4cce8e155c6e185c3df0b89a1eb7ae18db16cb2712f611` | exact-build non-child User-0 HOME candidate inventory negative；Fire priority 50、User-0 state unchanged。**Confirmed（inventory scope）** | 只在出現新 framework/Amazon lifecycle evidence 時更新候選，不重做普通 HOME setter。 |
| `LUNA-IPC-001` | `findings/phase-6t-ipc-live-evidence-index.md`；`adb/phase6t/PHASE6T-IPC-RO-20260805-01/service_list.stdout.txt`、`logcat_all_dump.stdout.txt`、`home_resolve.stdout.txt` | files：`1bed100e5cb128fed02bd197964792a6ecc1ea461818772747d1d543f334e6ba`、`6fd5d62c1d28a7412ada655c8dfb38edf40ea1c60f6700b9875ed24cfda91bcc`、`d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | service registration 可見不等於 shell Binder accessibility；shell UID 2000 `service_manager find` 被 deny；HOME 仍 Fire priority 50。**Confirmed/Strong** | 不把 service name 當 IPC route；不猜 transaction。 |

## 3. 可由主 Agent 進行的最小 host-only 缺口

以下是低風險、只讀、可獨立驗證的缺口；不需要設備或裝置變更：

1. **KFT tx3 authorization closure（最高價值）**：從完整 `IAmazonUserManager` Stub、`AmazonUserManagerService` Binder method、所有 static callers 建立 caller → permission/SELinux/service publication → `UserInfo.id` data-flow 表。目標是確認「trusted child lifecycle」的 caller provenance；不要把缺少 method-local check 自動判成漏洞。
2. **Home callback return/data-flow closure**：針對 `callCustomDockOrHome`、`callOnStartDockOrHome`、`AmazonProfileService` callback 及 `KeyPolicyManager`，只追蹤回傳值、explicit component、`startActivityAsUser` 參數與是否出現 PMS preferred/state sink。Phase 6H 已明確指出 callback boundary 尚未等於 Fire hard-code。
3. **OOBE / ProductPolicy user mapping**：對 `AppAdapterHandler.goToRegistration()` 與 `EnableDisableComponentAction`，補 static policy-file、user-list、`UserInfo`/userId flow；Phase 6MH 已確認 PS7331 policy input 沒有 Fire Launcher entry，但 OOBE helper 的 exact runtime user mapping 仍待驗證。
4. **Deny-list provenance inventory**：只讀 `PackageManagerDenyList` 的保存來源、registration edge、consumer methods 與 input hashes；不可讀取裝置私有檔案、不可修改 shared preferences，也不可用 deny-list literal 推導 caller。
5. **Corpus/scope cross-check**：以既有 parser 對 preserved `fosservices`/`services` disassembly 做 method signature、interface token、permission、call-site mapping，輸出新 hash manifest；不需 unpack/build/execute source tree。Phase 6KV/6MW 的 static labels 不可升級成 runtime claim。

## 4. 重複或不應再執行的測試

- KFT `IAmazonUserManager` tx3、Tahoe enable、child switch/unlock/PIN、User-10 stop/start：已有 child-local positive 與 User-0 rollback attribution；再跑不會回答新問題，且 writer 本身會改 child package state。
- 普通 `pm/cmd package set-component-enabled-setting`、`set-application-enabled-setting`、`set-home-activity`、Fire disable/hide/suspend/uninstall：PMS protected-package/permission boundary 與 Fire priority-50 resolver 已閉合。
- `service call` / raw Binder transaction / guessed parcel / caller spoofing / service injection：private Amazon service shell lookup 已被 SELinux 擋住，且明確禁止作為測試。
- Amazon private `amazonpackagemanager` metadata transaction：private Binder contract 已證明沒有 formal HOME/package-state setter；metadata writers 仍可能 mutating，不應為了 HOME 假設而發送。
- GUI Default Apps/Home picker、Microsoft App Info Home row、Settings Fire disable-button：已證明沒有可用 Home selector，且 protected Fire disable control 已關閉。
- Fire Launcher package-event/global-sync/BackupAgent/ordinary process lifecycle 實驗：Fire app review 未找到 PMS HOME/package writer；應把新工作移回 Framework/Amazon callback caller mapping。
- User-0 candidate re-enumeration、普通 HOME resolve/resume baseline、service-list 反覆查詢：只有在 build/artifact/device state 有新變化時才有價值；目前屬重複 baseline。

## 5. Source/evidence integrity notes

- `fosservices/disassembly.log` SHA-256：`ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`。
- `services/disassembly.log` SHA-256：`373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`。
- Phase 6MH canonical summary：`artifacts/phase6mh-package-state-writers-20260810-01/summary.json`，SHA-256 `c8bcd0cda741aa21534a5aebc7995c7daa007f669a14b1ec7b913b6bbf055cc4`；其 inventory 是 21 setter callsites，全部 `device_mutation=false`。
- Phase 6KV canonical table：`artifacts/phase6kv/pms-home-caller-closure-20260810-01/pms-home-callers.csv`，SHA-256 `dc1a86ea85904e3775704944fa86364a9a89033f6146eed0dac8b324b7028382`。
- Phase 6AV/6H 均明載 host-only、未取得 Binder handle、未發送 transaction；其用途是 static authorization/surface mapping，不是 runtime exploit evidence。

## Final disposition

可採用的工作結論是：**KFT 是已確認的 child-user trusted writer；User 0 Fire Launcher writer/selector 尚未被確認，且目前 ordinary/private IPC 路徑均有 permission、SELinux、user-scope 或 resolver boundary。** 主 Agent 下一步只應做上述 host-only closure；不要回到已關閉的 KFT、普通 setter、GUI selector、service call 或任何裝置變更。
