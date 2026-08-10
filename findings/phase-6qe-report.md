# Phase 6QE — 廣域權限面、IPC caller 與 7.3.3.1 driver policy 驗證

日期：2026-08-10
公開基準：`52c8b3f6bd376d87635ab76681f1290b29dac415`（Phase 6QD）
裝置：`G001LT0511550CFT` / `KFTRWI` / `trona` / PS7331

## Executive summary

本輪把研究範圍從 Launcher 擴展到三類可能影響系統控制權的面：

1. Amazon Framework/System Services IPC 的 caller → permission → identity →
   user scope → sink chain；
2. 7.3.3.1 GPL source 與 exact-image node/SELinux policy；
3. 既有 package/component、KFT、DPM/Profile、Accessibility、OOBE/OTA 與
   service visibility 實測結果。

合併矩陣共有 37 rows（15 IPC、8 driver/policy、14 existing tests）。截至本輪，
沒有閉合出以下鏈條：

```text
ordinary app / shell UID 2000
  → 缺失或可繞過的 caller gate
  → system/root identity
  → PackageManager/HOME/package-state/credential/SELinux/partition sink
```

這是針對已取得 artifacts、保存測試與本輪 exact-device metadata 的 bounded
結論，不是對所有未取得 Amazon native code、未保存的 caller universe 或未知
漏洞作全域不存在性證明。

目前最重要的直接答案：

- **已證實**：Fire Launcher 的 package/component disable、force-stop 與一般
  shell state mutation 仍在狀態變更前被保護；KFT 的 launcher-state writer 存在，
  但其保存的作用域是 child/profile 的 `UserInfo.id`，不是普通 shell 的 User 0
  HOME replacement。
- **已證實**：7.3.3.1 exact image 的 `/dev/mtk_cmdq` 為 `0644 system:system`、
  `/dev/gsensor` 為 `0660 radio:system`；shell metadata snapshot 中
  `/proc/m4u` 與 `/proc/life_cycle_reason` 回報 Permission denied，
  `/dev/m4u`、`/dev/M4U_device`、`/proc/amzn_drvs` 不存在；沒有開啟任何 node。
- **高可信推論**：driver source 的 `copy_from_user`、ioctl 或缺少 local
  `capable()` 不足以構成低權限漏洞；exact init mode、SELinux type/allow、
  build/config 與實際 client domain 必須同時成立。
- **待驗證**：少數 Amazon PM metadata、Vending、OOBE、WMS/Profile 與 native
  handoff 的 production caller provenance；這些 UNKNOWN 不得升格為漏洞。
- **已排除（本研究範圍）**：再次執行 priority APK 矩陣、普通 `set-home-activity`、
  Fire disable/hide/suspend/force-stop、未知 Binder、driver ioctl、OTA/recovery
  與 Root/exploit 不會增加目前證據，故本輪沒有重做。

## 1. Worker evidence

### IPC caller→sink（已完成）

`luna_worker` 整理 15 條 Amazon service publication、Stub/method、caller、gate、
identity、user scope 與 sink。重點是：

- KFT tx3 的保存 caller 是 `AmazonUserManagerImpl.createChildUser`；writer 使用
  supplied `UserInfo.id`，作用於 child/profile launcher state；沒有證據把它變成
  User 0 formal HOME setter。
- ProxyReceiver tx6/tx7 受 PendingIntent creator/UID ownership 邊界約束；
  ordinary self-created probe 已有 gate rejection。
- DPM restriction、DPM tx100 → PMS tx73、Profile tx21/tx41 均存在 owner/admin、
  permission、cross-user 或 downstream UID 邊界。
- `BootAfterSystemOTAReceiver` 是 system-server phase 550 + `isUpgrade()` 的
  protected OTA/OOBE lifecycle；能改 OOBE state，但沒有 ordinary caller delivery。
- PM flags/metadata、Vending writer、AMS observer、WMS PIP/overscan 與部分 Profile
  downstream 的 caller 或第一個 consumer 仍是 UNKNOWN；不能把 exported/public
  或 service list 名稱當成可呼叫權限。

Evidence：`work/luna_worker_phase6qe_ipc_caller_closure_20260810.md/.csv`。

### GPL driver / exact image policy（已完成）

Worker 將 source capability 與 shipped reachability 分離：

- CMDQ/MDP source 有 `/dev/mtk_cmdq` ioctl/job path；live metadata 是
  `crw-r--r-- system system u:object_r:mtk_cmdq_device:s0`，沒有 write bit 給
  shell/一般使用者。
- M4U source 在 `__M4U_USE_PROC_NODE` 下走 `/proc/m4u`；`/dev/m4u` misc branch
  不活躍。live shell metadata 對 `/proc/m4u` 是 Permission denied，且沒有
  `/dev/m4u` 或 `/dev/M4U_device`。
- performance source 是 `/proc/perfmgr/perf_ioctl`；live metadata 是
  `-rw-rw-r-- root root u:object_r:proc_perfmgr:s0`，不是 shell 可寫證據。
- gsensor normal path 是 `radio:system`、`0660`；factory init 的較寬 stanza 不能
  自動推論 retail runtime。
- `amzn_drv_test.c` 的 factory/RTC test index 仍是 conditional source；
  `trona_defconfig` 未啟用 `CONFIG_AMZN_DRV_TEST`，official boot Image 也未提供
  本輪可確認的 shipped test marker。
- IDME/lifecycle source 與 exact policy 都是 read-only/bounded read path；沒有
  package/HOME/root sink。

Evidence：`work/luna_worker_phase6qe_driver_policy_20260810.md/.csv`，以及
`artifacts/phase6c/phase6c-image-policy-extract-20260804-06/`。

## 2. Exact-device read-only verification

新快照：
`adb/phase6qe/PHASE6QE-DEVICE-READONLY-20260810-02/`。

腳本記錄 12 個只讀命令，metadata 明確標示：
`device_nodes_opened=false`、`driver_data_read=false`、
`binder_transactions_invoked=false`、`settings_or_package_mutation=false`、
`root_or_exploit=false`。

觀察結果：

```text
ADB state: device
HOME: priority=50 ... com.amazon.firelauncher/.Launcher
/dev/mtk_cmdq: crw-r--r-- system system, mtk_cmdq_device
/dev/gsensor:  crw-rw---- radio system, gsensor_device
/proc/perfmgr/perf_ioctl: -rw-rw-r-- root root, proc_perfmgr
/dev/m4u, /dev/M4U_device, /proc/amzn_drvs: not present
/proc/m4u, /proc/life_cycle_reason: shell Permission denied
```

SHA-256 anchors：

- `metadata.json`: `5afaf05e9d2bec715d9142250f053441b31383ffe9624cb3d80f03cff6e16a0d`
- `sha256sums.txt`: `355dd168ad1061f5f017fb24f0d5b6e102d0d17e58cf38710d777cd39c5facee`
- `node_metadata.stdout.txt`: `fd8a1b871b5e65e948b44a9d121a0e4368e0c702c07accc756c6bbff9eb28e82`
- `home_resolve.stdout.txt`: `d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6`
- `selinux.stdout.txt`: `4fefafd0dcddf54b31a0fef448083e7b77576d86a9ec97c14bfd92479c404290`

本次 HOME resolver 與 SELinux output 亦與 Phase 6QD 對應值一致；沒有觀察到
裝置狀態漂移。

## 3. Existing-test reconciliation

既有 14 rows 的整理顯示：

- Fire package/component disable 與 force-stop rejection 已有 raw evidence；不得
  在相同 caller/build 下重測。
- KFT 可以在合法 child/profile lifecycle 變更 per-user launcher state，但不等同
  User 0 shell 可達的 Fire disable。
- DPM/Profile Owner 與 persistent-preferred 相關路徑都有 owner/admin 或 trusted
  identity gate。
- Accessibility/ADB foreground redirect 是有限的替代體驗，不是 formal HOME；
  它不修改 resolver、package state 或 system identity。
- OOBE/OTA receiver、updater、recovery 與固定 partition writer 都是能力／生命週期
  邊界，沒有 ordinary caller chain。
- Amazon private service 名稱出現在 `service list` 不代表 shell 可取得 Binder
  handle；既有 AVC/service-check evidence 已記錄 denied/not found。

Evidence：`work/luna_worker_phase6qe_existing_tests_20260810.md/.csv`。

## 4. Decision graph

```text
source capability
  → exact image config / init mode / file label
  → SELinux domain allow + caller provenance
  → user/role/permission gate
  → sensitive sink

目前已閉合到：source、部分 exact-image policy、部分 safe runtime metadata。
尚未閉合：ordinary caller → accepted gate → system/root → sensitive sink。
```

## 5. Risk-rejected operations

本輪沒有執行：

- `/dev/mtk_cmdq`、`/dev/gsensor`、`/proc/m4u`、`/proc/perfmgr/perf_ioctl` 或
  `/proc/amzn_drvs` 的 open/read/write/ioctl；
- 任何 Amazon private Binder transaction、protected broadcast、DPM/KFT raw parcel；
- Fire Launcher disable/hide/suspend/uninstall/force-stop/clear；
- Root、kernel exploit、remount、SELinux 修改、OTA/recovery/updater、reboot 或
  partition write。

這些操作可能造成硬體狀態改變、SystemUI/HOME 失效、資料遺失或需要 factory
reset，不能以「只觀察 log」作為低風險理由。

## 6. Next safe value

下一步仍維持 host-only：

1. 對 exact PS7331 image 完成 `registration → init mode/owner → file_context →
   domain allow → exact client → sink` 的交叉索引；
2. 對 PM/Vending/OOBE/Profile 的 skipped DEX、Stub registration 與 Context/UserHandle
   propagation 做 caller provenance closure；
3. 若自然完成官方 OTA，僅做 post-OTA read-only snapshot；不 replay 或構造 OTA；
4. 只有在出現 low-privilege caller + sensitive sink 的完整、可安全驗證鏈時，才另
   行評估風險；目前沒有理由製作或部署 exploit。

## Reproduction

```sh
python3 tools/scripts/capture_phase6qe_device_readonly.py \
  --serial G001LT0511550CFT \
  --output adb/phase6qe/PHASE6QE-DEVICE-READONLY-YYYYMMDD-NN

python3 tools/scripts/build_phase6qe_privilege_surface.py --dry-run \
  --ipc work/luna_worker_phase6qe_ipc_caller_closure_20260810.csv \
  --drivers work/luna_worker_phase6qe_driver_policy_20260810.csv \
  --tests work/luna_worker_phase6qe_existing_tests_20260810.csv \
  --output output/tables/phase6qe-privilege-surface.csv \
  --manifest output/tables/phase6qe-privilege-surface.csv.manifest.json
```
