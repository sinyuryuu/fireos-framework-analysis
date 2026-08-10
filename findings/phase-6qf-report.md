# Phase 6QF — 廣域權限面與 privilege-transition closure

日期：2026-08-10
基準：公開 commit `aca16f12daa7807e435fcbc259e5af067cab6b12`
裝置：Amazon Fire HD 10 2021 / `KFTRWI` / `trona` / PS7331 / Android 9 API 28

## Executive summary

本輪把問題從「Fire Launcher 是否能被停用」擴展成更一般的權限邊界問題：是否
存在任何已取得證據的低權限 caller，可以穿過 Amazon IPC、PackageManager、DPM、
profile、OOBE/OTA、SELinux、custom driver 或 procfs 邊界，取得 system/root 等
受信任身份，最後觸及 PackageManager、HOME、package state、credential、SELinux、
OTA/recovery 或 partition sink。

在目前保存的 exact-build corpus 與既有實機證據中，沒有閉合出這條鏈：

```text
ordinary app / shell UID 2000
  → accepted caller gate
  → system/root identity
  → high-impact sink
```

這是對 26-row bounded matrix 的結論，不是「所有未知漏洞不存在」的證明。`UNKNOWN`
仍代表證據缺口；不能因為 service 已 publication、manifest 看似 exported、source
有 ioctl 或 permission holder 尚未定位，就宣稱存在提權。

目前最重要的答案：

- **已證實**：exact-device HOME 仍為 `com.amazon.firelauncher/.Launcher`，priority
  50；既有 Fire package/component gate 在狀態改變前拒絕；selected driver/node 的
  live metadata 與 SELinux labels 已保存。
- **高可信推論**：在已審計的 12 個 Amazon IPC、7 個 exact-image policy/client
  surface 與 7 個既有 runtime surface 中，沒有 ordinary app/shell → accepted
  trusted identity → high-impact sink 的完整閉包。
- **已證實但非漏洞**：KFT child/profile writer 具有 per-user launcher-state 作用域；
  它不是普通 shell 的 User-0 HOME replacement 證據。Source `copy_from_user`、
  ioctl、Binder Stub、service list visibility 也都不是 caller reachability 證明。
- **待驗證**：少數 PM metadata、Vending、OOBE、Profile/WMS/native client 的
  production caller、exact domain allow 或第一 consumer。這些不應升格為漏洞。
- **已排除（有界）**：單靠 service list 名稱、driver source capability、generic
  SELinux type、Accessibility foreground redirect、合法 child/profile state writer
  不能得到 system/root 或正式 HOME replacement。
- **因風險拒絕測試**：未知 Binder transaction/private broadcast、driver open/ioctl、
  OTA/recovery/updater、Root/exploit、remount/SELinux/partition mutation，以及
  Fire Launcher disable/hide/suspend/uninstall/force-stop/clear。

若真正取得 system/root，PackageManager/HOME/package state 等控制能力在抽象上當然
會增加；但本研究目前沒有證據顯示如何取得那個身份，不能把「root 後能做什麼」
倒推成「已找到 root 路徑」。

## 1. Scope and method

本輪由三個相互獨立的 host-only ledger 組成：

| domain | rows | purpose |
|---|---:|---|
| Amazon IPC provenance | 12 | registration → Stub/facade → caller → gate → user → sink |
| PS7331 exact-image policy/client | 7 | source → init/node/file context → SELinux/domain → client → sink |
| existing runtime audit | 7 | reconcile prior package/KFT/DPM/Accessibility/OOBE/driver evidence |

用 `tools/scripts/build_phase6qf_privilege_surface.py` 正規化成 26-row matrix。腳本
只讀 CSV，不接觸裝置，也不呼叫 ADB、Binder、settings、package、driver、OTA 或 root。

Phase 6QE 的 exact-device metadata-only snapshot 被作為 runtime anchor 重用；本輪
沒有新增裝置變更、重啟、安裝 APK、修改 HOME、建立 user/profile 或呼叫 private service。

## 2. Direct evidence

### 2.1 Exact device state — 已證實

保存於 `adb/phase6qe/PHASE6QE-DEVICE-READONLY-20260810-02/`：

- HOME resolve：`com.amazon.firelauncher/.Launcher`，priority 50。
- `/dev/mtk_cmdq`：`0644 system:system u:object_r:mtk_cmdq_device:s0`。
- `/dev/gsensor`：`0660 radio:system u:object_r:gsensor_device:s0`。
- `/proc/perfmgr/perf_ioctl`：root-owned `proc_perfmgr` metadata。
- `/dev/m4u`、`/dev/M4U_device`、`/proc/amzn_drvs` 不存在於該 snapshot。
- shell 對 `/proc/m4u` 與 `/proc/life_cycle_reason` 的 metadata 存取被拒絕。

這些只代表 metadata；沒有開啟任何 device node，也沒有讀寫 driver data。

### 2.2 Package and HOME protection — 已證實

既有 raw evidence 顯示：Fire Launcher package/component mutation 與 force-stop 在
狀態變更前被 protected-package gate 拒絕；HOME resolver 沒有因這些失敗而改變。
本輪只引用既有證據，未重送同一 writer。

### 2.3 Source and image policy — 已證實／待驗證分開

PS7331 source/config 與 extracted image 中可核對 CMDQ/MDP、M4U、perfmgr、gsensor、
IDME/lifecycle 與 `amzn_drv_test` 的部分 registration、file_context、CIL 或 init
markers。可是：

- `trona_defconfig` 未啟用 `CONFIG_AMZN_DRV_TEST`；conditional factory/RTC source
  不能當作 retail runtime control surface。
- exact client、compiled domain、final allow 與 runtime handoff 在多個 surface 尚未
  全部閉合。
- source 的 `copy_from_user`、ioctl 或沒有看到 local `capable()`，不等於 shell
  能到達，也不等於可造成 system/root identity transition。

## 3. IPC provenance closure

### 3.1 Amazon PM flags/metadata — 待驗證，不是漏洞

已找到 `AmazonPackageManagerImpl` facade 的 mutator call sites，並與
`IAmazonPackageManager` Stub/service contract 對上。可是 exact permission holder、
production caller、numeric target user，以及 metadata 何時被轉成 HOME/package-state
決策仍未完整閉合。保存的 consumer 主要是 per-user persistence、recency/game-mode/
compatibility 類讀者，沒有找到 formal HOME setter。

### 3.2 KFT child/profile writer — 已證實作用域，caller gate 待驗證

KFT tx3 的保存 caller 是 child-user provisioning `createChildUser` 與 system-server
child loop；sink 使用 caller-supplied `UserInfo.id` 寫 Tahoe/Fire/Launcher3 component
state。這證實了 child/profile state writer 的存在，但沒有證明 ordinary shell 可合法
觸發，也沒有證明它會修改 User 0 Fire HOME。User-0 restoration writer provenance
仍是 UNKNOWN。

### 3.3 DPM/Profile/AMS/WMS/Vending/OOBE/OTA — bounded closure

- DPM tx100 → PMS tx73 涉及 owner/profile-owner 與 trusted downstream identity。
- Profile tx21/tx41、AMS prewarm/observer、WMS PIP/overscan 各自閉合到 profile、
  process 或 window/status-bar sink；沒有恢復出 User-0 Fire HOME writer。
- Vending `LauncherConfigurationReceiver` 的 exported 或 receiver metadata 不等於
  任意 sender；verification token、creator/current-launcher/setup/package qualification
  是前置 gate，first consumer 是 restore bookkeeping。
- `BOOT_AFTER_SYSTEM_OTA` 是 system-server phase-550 + `PMS.isUpgrade()` 的 protected
  lifecycle；OOBE sink 不等於 ordinary caller 的 package/HOME writer。
- OTA controller 有 privileged capability，但沒有 ordinary caller → accepted writer
  的證據。

## 4. Exact-image policy/client closure

完整 7-row ledger 在 `work/luna_worker_phase6qf_exact_policy_client_20260810.csv`。
判定採用以下順序：

```text
source registration
  → shipped config / init mode and owner
  → file_context / SELinux type
  → domain allow
  → exact compiled client
  → caller identity and sink
```

任何一段缺失都保留 `UNKNOWN`。特別是：

- CMDQ/MDP：source 與部分 image labels 可見，但 exact client/domain allow 未全閉合。
- M4U：source active branch 是 `/proc/m4u`；不存在的 `/dev/m4u` 不能當作可用節點。
- perfmgr：init declaration 或 source ioctl 不等於 shell 可寫；live node metadata 是
  root-owned。
- gsensor：live node 是 radio/system `0660`；factory-init 寬鬆 stanza 不能推論 retail
  runtime。
- IDME/lifecycle：存在 source/policy markers，但沒有 package/HOME/root sink 閉包。
- `amzn_drv_test`：defconfig omission 使其不能直接當作 shipped test interface。

## 5. Privilege-transition decision

### 已證實

1. 既有 Fire Launcher protected-package gate 不是普通 enabled-state workaround 可繞過
   的證據。
2. service list visibility 不等於 shell 能取得 service handle，更不等於能呼叫高權限
   method。
3. child/profile、DPM、OTA/OOBE 等 writer 有作用域或生命週期限制。
4. exact-device driver metadata 目前沒有顯示 shell 可寫的高影響 node。

### 高可信推論

以目前 26 rows 的 caller/gate/identity/sink 交叉結果，沒有可直接提交為 root 或
privilege-escalation path 的完整鏈。這個推論受限於保存 corpus 和未做的風險拒絕操作。

### 待驗證

- Amazon PM metadata mutator 的 production permission holder/caller。
- exact compiled clients 與 SELinux final allow 對 CMDQ/MDP、M4U、perfmgr、IDME。
- KFT tx3 合法 caller 以及 User-0 restoration side effect。
- skipped DEX/native aliases、Context/user propagation、OOBE/OTA native handoff。

### 已排除（有界）

以下不能單獨形成權限提升或 HOME replacement：

- manifest `exported`、service publication、normal permission 或 `service list` 名稱；
- GPL source 中的 ioctl/copy path，而沒有 exact node + SELinux + caller chain；
- generic SELinux type 或 init stanza，而沒有 retail client/allow；
- Accessibility/foreground redirect；它是替代體驗，不是正式 HOME 或 system identity；
- 合法 child/profile per-user writer，當作 User-0 shell writer。

## 6. Operations not executed — 因風險拒絕測試

沒有執行以下操作：

- unknown/private Binder transaction、`service call` payload、protected broadcast；
- `/dev/mtk_cmdq`、`/dev/gsensor`、`/proc/m4u`、`/proc/perfmgr/perf_ioctl` 或
  `/proc/amzn_drvs` 的 open/read/write/ioctl；
- KFT user lifecycle replay、DPM owner/profile provisioning、OTA/recovery/updater；
- Root、kernel exploit、remount、SELinux mutation、partition write 或 bootloader 操作；
- Fire Launcher disable/hide/suspend/uninstall/force-stop/clear、其資料清除或任何
  需要 factory reset 才能保證回復的步驟。

這些是 **Risk-rejected**，不是「已在 runtime 證明無效」。

## 7. Reproduction

所有輸入、輸出與 hash 可用下列 host-only 命令重建：

```sh
python3 tools/scripts/build_phase6qf_privilege_surface.py --dry-run \
  --ipc work/luna_worker_phase6qf_ipc_provenance_20260810.csv \
  --policy work/luna_worker_phase6qf_exact_policy_client_20260810.csv \
  --runtime work/luna_worker_phase6qf_existing_runtime_audit_20260810.csv \
  --output output/tables/phase6qf-privilege-surface.csv \
  --manifest output/tables/phase6qf-privilege-surface.csv.manifest.json

python3 tools/scripts/build_phase6qf_privilege_surface.py \
  --ipc work/luna_worker_phase6qf_ipc_provenance_20260810.csv \
  --policy work/luna_worker_phase6qf_exact_policy_client_20260810.csv \
  --runtime work/luna_worker_phase6qf_existing_runtime_audit_20260810.csv \
  --output output/tables/phase6qf-privilege-surface.csv \
  --manifest output/tables/phase6qf-privilege-surface.csv.manifest.json
```

本腳本必須在 host 上執行；它的 manifest 明確宣告沒有 device contact、node open、
Binder/settings operation、mutation 或 root/exploit。

## 8. Next safe value

仍有研究價值的最小下一步是 host-only provenance closure：補齊 exact-build skipped
DEX/native aliases、PM metadata permission holder、KFT合法 caller、以及 compiled
client/domain mapping。若日後自然完成官方更新，只做 post-update read-only snapshot；
不 replay、不構造、不注入 OTA。

目前不應進入 exploit 或未知 Binder/driver 實驗。若未來要改變這個判定，至少需要一個
可重現、經授權的低權限 caller 加上明確 accepted gate、identity transition 與高影響
sink；在此之前，最嚴謹的結論是：

> **Phase 6QF 尚未發現可提交的低權限提權鏈；Fire Launcher 的高權限控制仍只在
> 受保護或受信任作用域中被觀察到。**

## 9. Artifact index

- `findings/phase-6qf-evidence-index.md`
- `output/tables/phase6qf-privilege-surface.csv`
- `output/tables/phase6qf-privilege-surface.csv.manifest.json`
- `output/call-graphs/phase6qf-privilege-surface.mmd`
- `output/call-graphs/phase6qf-privilege-surface.md`
- `tools/scripts/build_phase6qf_privilege_surface.py`
- `work/luna_worker_phase6qf_ipc_provenance_20260810.md/.csv`
- `work/luna_worker_phase6qf_exact_policy_client_20260810.md/.csv`
- `work/luna_worker_phase6qf_existing_runtime_audit_20260810.md/.csv`
