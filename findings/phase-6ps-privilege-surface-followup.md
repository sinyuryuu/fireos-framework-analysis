# Phase 6PS — 全域特權面追蹤與 closure follow-up

日期：2026-08-10  
裝置：`G001LT0511550CFT` / Amazon Fire HD 10 KFTRWI / `trona`  
Build：`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`  
基準公開 commit：`9a28b5acd43776ea09ac0e7861dd88cb82377bfe`

## 1. 結論摘要

本輪把研究範圍擴大到所有可能造成 package、component、user、HOME、設定、
process、driver 或 boot state 變更的控制面。結果沒有新增「低權限 caller →
可接受的高權限 sink → system/root 身分」的閉合鏈。

最重要的新線索是 `com.android.vending`：目前設備的 PackageManager dump
記錄它持有 `CHANGE_COMPONENT_ENABLED_STATE`，並同時記錄
`INSTALL_PACKAGES`、`DELETE_PACKAGES`、`MANAGE_USERS`、
`WRITE_SECURE_SETTINGS`、`REBOOT` 與 `FORCE_STOP_PACKAGES` 等高影響權限。
這個 holder 狀態是 **已證實**；但它的 grant provenance、實際呼叫者、目標
package，以及是否能通過 Fire Launcher 的 protected-package gate 仍是
**待驗證**。主機端 APK 掃描沒有找到 `com.amazon.firelauncher`、HOME
preferred writer 或 `startHomeActivity`，因此不能把這個 holder 當成 bypass。

目前能在實機閉合的低權限代理仍只有兩個受限結果：

* `IAmazonActivityManager` tx1：ordinary APK 可造成 system-server
  `startProcessLocked(..., "prewarm", ...)`，是已證實的 process/resource
  confused deputy，但不是 package、HOME 或 root writer。
* `IAmazonUserManager` tx4：ordinary APK 可造成固定的
  `user_setup_complete` / `tv_user_setup_complete` settings write，並已還原；
  不是 package、HOME 或 system-UID writer。

KFT tx3 雖然在 system-server 內有明確的 Fire Launcher state writer，但既有
User 10／User 0 測試分別在 cross-user 或 PMS component gate 被拒絕，不能重播
成一般 shell/ordinary-app 入口。kernel driver、updater、OOBE、`/init` 與
GhostLock 仍是 capability 或 lifecycle 候選，沒有低權限 runtime transition。

**總判定：** 目前沒有新的正式 HOME replacement，也沒有已證實的普通 app／
shell 提權至 system/root。若將來取得受信任 system UID、root 或合法 Device
Owner，當然可以改 package state；但「取得該身分」仍不是本研究已證實的結果。

## 2. 安全範圍與新證據

本輪主機端 worker 只讀取既有 PS7331 corpus，沒有使用 ADB、Binder/service
call、ioctl、root/exploit、OTA、recovery、flash 或 partition 操作。

新增的目前設備唯讀 capture：

`adb/phase6pr/PHASE6PR-VENDING-READONLY-20260810-01/`

腳本：

`tools/scripts/capture_phase6pr_vending_provenance.py`

capture metadata 明確記錄：

```text
mutating_commands=false
binder_transactions_invoked=false
package_state_changed=false
settings_changed=false
rebooted=false
ota_or_partition_operation=false
```

該目錄以 `sha256sum -c sha256sums.txt` 驗證通過。主要檔案雜湊：

| Evidence ID | 檔案 | SHA-256 | 判定 |
|---|---|---|---|
| PS-VEND-LIVE-01 | `vending_package.stdout.txt` | `d3075425f6980289611f8163858c9ff637901ccb4648ec482fb844973c50c361` | 已證實 package metadata |
| PS-VEND-LIVE-02 | `permission_definition.stdout.txt` | `62d133892d6488861e85bc7e9aeb9418e258e930e0cda507a695aac1e2e406cc` | 已證實 permission definition |
| PS-VEND-LIVE-03 | `home_resolve.stdout.txt` | `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6` | Fire HOME 未變 |
| PS-VEND-LIVE-04 | `home_candidates.stdout.txt` | `e868693c97bce5ec4c93c6e5e144225797c2219fafde54d46fdbd3bdf462442c` | candidate set |
| PS-VEND-LIVE-05 | `metadata.json` | `281f5bcd1399d91d67d7305682b23f6866a159067766f35607c330555e92a844` | 操作安全旗標 |

主機端新增的 worker closure：

* `work/luna_worker_component_permission_provenance_20260810.md`
* `work/luna_worker_component_permission_matrix_20260810.csv`
* `work/luna_worker_binder_sink_closure_20260810.md`
* `work/luna_worker_binder_sink_closure_20260810.csv`
* `work/luna_worker_kernel_ota_unclosed_closure_20260810.md`
* `work/luna_worker_kernel_ota_unclosed_closure_20260810.csv`

上述工作檔案的 SHA-256 及來源索引保留在本 commit 的 evidence manifest 中；
worker 沒有修改原始 evidence。

## 3. `com.android.vending` 高權限 holder 線

### 3.1 已證實的 metadata

目前 dump 顯示：

* package：`com.android.vending`，UID `10180`；
* code path：`/data/app/com.android.vending-InxWV-Nv8Fy8x5lSfSr0mQ==`；
* private flags 沒有 `PRIVATE_FLAG_PRIVILEGED`；
* `CHANGE_COMPONENT_ENABLED_STATE` 為 `granted=true`；
* 同時有 `INSTALL_PACKAGES`、`DELETE_PACKAGES`、`MANAGE_USERS`、
  `WRITE_SECURE_SETTINGS`、`REBOOT`、`FORCE_STOP_PACKAGES` 等 grant row；
* permission definition 為 `sourcePackage=android`、
  `prot=signature|privileged`。

這說明 Fire build 對 Play Store 保存了一組特殊 install-permission state，
但不說明其 grant 來源。已抽取的 PS7331 `privapp` XML 沒有
`<privapp-permissions package="com.android.vending">` block；因此 provenance
目前只能標為 **待驗證**，可能涉及 install-time 或歷史 package state，不能
從缺少 XML block 反推出不存在其他來源。

### 3.2 靜態 sink 審查

保存的 Play Store base APK／JADX corpus 找到通用：

* `setApplicationEnabledSetting()`；
* `setComponentEnabledSetting()`；
* verifier／enterprise policy 導出的 package/component target。

但 bounded scan 沒有找到：

* `com.amazon.firelauncher` literal；
* `setPreferredActivity`、`replacePreferredActivity`、
  `addPreferredActivity`；
* `startHomeActivity` 或 direct Fire HOME component launch。

這些 writer 的 target 來自內部 policy／verification input，且任何實際 PMS
呼叫仍要經過 system-server 的 protected-package gate。故：

* **已證實：** Play Store 是高權限 holder，且存在 generic writer callsites。
* **高可信推論：** 它不是目前 Fire Launcher controller；Home-key observation
  只記錄 Play Store inline-details event。
* **待驗證：** grant provenance、JADX 失敗區域、native/resource 路徑。
* **已排除（bounded）：** 直接由已掃描 Java/APK 字串控制 Fire Launcher HOME。
* **拒絕測試：** 不呼叫 Play Store exported component，不利用它嘗試 package
  setter，不 grant/revoke permission。

主要靜態來源：

* `findings/phase-6mb-vending-permission-and-state-writer-audit.md`；
* `artifacts/phase6mb-vending-static-20260810-01/static-search-summary.md`；
* `findings/phase-6lz-component-state-permission-audit.md`；
* `findings/phase-6ci-tahoe-user0-component-gate.md`。

## 4. Amazon Binder caller→sink closure

16 個保存的 service surfaces 被重新分成三類：

1. **已證實受限代理：** prewarm process sink、setup-state settings sink。
2. **高影響但未閉合／被下游拒絕：** KFT tx3、DPM restriction、OOBE、OTA
   metadata/proxy paths。
3. **query/resource/input/window/local callback：** 沒有 package/HOME/root sink，
   或 caller gate 尚未閉合；缺少 local check 不等於 vulnerability。

最重要的 package-state writer 仍是：

```text
KFT child/profile lifecycle
  -> enableKftLauncher(UserInfo)
  -> enableKftLauncherComponent(UserInfo)
  -> Tahoe FreeTimeLauncher = ENABLED
  -> Fire Launcher / Launcher3 = DISABLED for supplied user
  -> PMS cross-user / protected-component gate
```

既有 physical evidence 已證實 User 10 路徑被 cross-user gate 擋下，User 0
路徑被 component gate 擋下；因此不重放相同 transaction。KFT code capability
不能等同於 ordinary caller capability。

其他重要負面 closure：

* `registerKeyEventInterceptor` 有 permission、UID、package whitelist 與
  foreground checks，且沒有 HOME resolver writer；
* profile launcher helper 只啟動已解析的 HOME，沒有 preferred/package writer；
* Amazon PackageManager metadata/proxy path 沒有被證明寫入 HOME 或 component
  state；
* DPM sink 是 trusted policy path，不能建立 Device Owner；
* OOBE receiver 需要 system-server OTA lifecycle，不能手動 replay；
* local `fosinit` callbacks 不是 exported Binder caller surface。

## 5. Kernel / OTA / init closure

八個候選的共通結論是：source capability 或 trusted lifecycle 存在，但沒有
untrusted/shell caller 到 privileged sink 的證據。

| Candidate | 靜態 sink | 目前判定 | 動態處置 |
|---|---|---|---|
| CMDQ/ION/GED/MTK nodes | fops/user-copy/DMA/telemetry/secure-world candidates | source-only；GED query 已閉合 | 禁止 write/reset/DMA/malformed ioctl |
| Amazon staging drivers | telemetry/device state | 無 package/system-server sink | 不 open/write/ioctl |
| native updater | extraction/block image/partition write | privileged recovery capability | 不執行 updater/recovery/OTA |
| cache canonicalization | `readlink_chk`/cache bookkeeping | caller/dataflow 未閉合 | 不做 symlink/traversal OTA |
| outer OTA/postinstall | bounded archive listing | 非 EOF-complete negative | 不抽取/執行未知 tail |
| BootAfterSystemOTA/OOBE | enable OobeHome + secure setup writes | trusted system_server lifecycle | 不手動 broadcast/replay |
| `/init` policy loader | policy variant selection | boot-chain authority | 不改 boot property/policy |
| GhostLock | futex/rtmutex source path | 無 runtime mismatch/residue/memory effect | 不做 race/DoS/exploit |

## 6. 是否有值得執行的下一個實機測試？

目前沒有。唯一可安全補強的 Vending provenance capture 已完成；再往前的
測試都會變成至少一項下列操作：

* 讓 Play Store 呼叫 package/component mutator；
* 呼叫未知或私有 Binder transaction；
* 啟動 exported recovery/package-monitor component；
* 寫入 settings、package state、OTA 或 driver node；
* 觸發 OOBE、KFT child lifecycle、recovery 或 kernel race。

這些操作即使表面可還原，也會改變安全狀態或可能失去桌面／ADB；在沒有一個
明確、文件化、非破壞性的 API contract 前，本階段列為 **因風險拒絕測試**。

## 7. 最終判定

| Finding | Confidence |
|---|---|
| Play Store 持有高影響 package-management permission rows | **已證實** |
| Play Store 是 `/data/app` 且沒有 captured privileged private flag | **已證實** |
| Play Store grant provenance | **待驗證** |
| Play Store 已掃描 code 直接選擇 Fire Launcher | **已排除（bounded scan）** |
| KFT system-server code 能對 child/user lifecycle 改 Fire state | **已證實（static capability）** |
| ordinary shell/app 能重播 KFT 並通過 PMS gate | **已排除（目前 build/caller）** |
| 存在 ordinary-app → system/root 身分 transition | **未發現；尚未證實** |
| 存在新的正式 HOME replacement | **未發現；尚未證實** |
| kernel/OTA/init 候選可安全實機驗證 | **因風險拒絕測試** |

目前最準確的研究結論仍是：

```text
high-impact permission holder ≠ successful protected-target mutation
system-server clearCallingIdentity ≠ caller becomes system UID
static kernel/OTA capability ≠ reachable root
confirmed bounded deputy ≠ arbitrary privilege escalation
```

## 8. 重現

唯讀 Vending capture：

```sh
python3 tools/scripts/capture_phase6pr_vending_provenance.py \
  --serial G001LT0511550CFT \
  --output adb/phase6pr/PHASE6PR-VENDING-READONLY-20260810-01

(cd adb/phase6pr/PHASE6PR-VENDING-READONLY-20260810-01 && \
  sha256sum -c sha256sums.txt)
```

主機端 worker closure 的原始報告與 CSV 仍保留於 `work/`，本報告只整合其
有明確 evidence path、caller、sink 與 confidence 的結果；原始設備輸出沒有
被覆寫。
