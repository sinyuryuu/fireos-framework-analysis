# Phase 6PW — broad privilege and HOME follow-up

日期：2026-08-10
公開基準：`a86d013611fcb3c2c5279cbe9c2f74b4069dca2d`
裝置：`G001LT0511550CFT` / KFTRWI / `trona`

## Executive summary

本輪把研究範圍延伸到既有 Launcher 以外的 Amazon Binder、KFT/profile、kernel
driver、OTA/OOBE、SystemUI、Accessibility 與 Lock Task 證據，並由三個
`luna_worker` 做不重複的主機端檔案盤點。主 Agent 再以新的 live read-only
capture 交叉核對目前 User 0 狀態。

**已證實：** User 0 目前仍解析到 `com.amazon.firelauncher/.Launcher`
（priority 50）；Microsoft Launcher 仍在 candidate set，但 effective priority
為 0。shell 是 UID 2000、SELinux Enforcing。完整原始 capture 的每檔 hash 已驗證。

**已證實：** 既有普通 App→system service 的兩個 bounded deputy 仍只有：
`prewarm` 的 process/resource effect，以及 UserManager tx4 的 setup-settings
寫入。兩者都沒有 PackageManager、HOME 或 system/root sink。

**已證實／受限：** KFT/child lifecycle 可以在 child user 範圍寫入 Tahoe、Fire
Launcher、Launcher3 的 package/component state；保存的 User 0/User 10 測試在
下游 PMS/cross-user gate 收斂，沒有 User-0 HOME replacement。

**高可信推論：** 目前最接近「可用」的結果是 child profile 的 per-user Tahoe
HOME，以及需使用者明確授權的 Accessibility foreground redirect；前者不是
User 0 第三方 HOME，後者 resolver 不變且有 clean-reboot 0/3 的矛盾證據。

**未找到：** 新的普通 caller→Amazon service→PackageManager/HOME/system
權限閉合鏈，或不 Root、不停用 Fire Launcher、可跨重開機的 User-0 正式 HOME
replacement。

## Current device evidence

Capture：`adb/phase6pw/PHASE6PW-READONLY-20260810-01/`

| 項目 | 結果 | 狀態 |
|---|---|---|
| ADB / shell | `device`; UID 2000; `u:r:shell:s0` | 已證實 |
| SELinux | `Enforcing` | 已證實 |
| Foreground user | User 0 | 已證實 |
| Users | User 0 `sinyu` running；User 10 `test` | 已證實 |
| HOME resolver | `com.amazon.firelauncher/.Launcher` | 已證實 |
| HOME priority | Fire 50; Microsoft 0; FallbackHome -1000 | 已證實 |
| Package state mutation | 本輪未執行 | 已證實 |
| Binder transaction / reboot | 本輪未執行 | 已證實 |

## Route findings

### Binder / Amazon services

三份 worker IPC/evidence audit 對九條去重路徑均沒有新增可接受的 User-0
HOME/PackageManager/root 路徑：

- prewarm：可造成 system-server process/resource effect，但沒有 HOME 或 package
  state sink。
- UserManager tx4：可寫固定 setup flags；既有 User 0/User 10 rollback 完成，HOME
  不變。
- KFT tx3：靜態 sink 明確碰到 child-scoped Tahoe/Fire/Launcher3 state，但既有
  runtime caller/protected-component/cross-user gate 拒絕；未重播 transaction。
- H2、DPM、OOBE/OTA 與 Amazon PackageManager metadata routes 分別受
  signature、owner/admin、system lifecycle 或私有 permission 邊界約束；未發現
  ordinary caller 的 HOME setter。

判定：**已排除（在已保存邊界內）** ordinary caller 可直接把上述 bounded sink
升格成 User-0 Fire Launcher disable 或正式 HOME replacement。未宣稱完整映像
不存在任何未知 private API。

### Kernel/GPL driver surface

PS7331 GPL source 的 CMDQ、ION、GED、M4U、RPMB、input、USB、Amazon staging
driver 仍是 host-only source surfaces。既有 `/proc/ged` 只讀 query 是 telemetry
證據；kernel source literal search 沒有直接連到 PMS/ATMS/HOME/Fire Launcher 的
edge。ioctl、DMA、secure metadata、RPMB 與 partition/update 能力不能單獨推導
低權限可達、記憶體破壞或提權。

判定：**靜態／高可信負向**；沒有足夠 runtime caller、sink 或 memory-safety
證據，因此本輪不對實機發送 driver 指令。

### OTA / OOBE

Native updater 與 signed OTA 具備受信任的 extraction/block-write/recovery
capability，但沒有普通 App/shell→updater/recovery 的完整 caller provenance。
`BootAfterSystemOTAReceiver` 是 system-server phase-550 + `isUpgrade()` 的
OOBE lifecycle；它可影響 setup/OOBE component，但現有 source/data-flow 沒有
Fire Launcher 或 preferred-HOME writer。

判定：**因風險拒絕動態測試**；不送 broadcast、不構造 OTA、不執行 updater/recovery、
不寫 partition。

### HOME / workaround classification

| 路徑 | 結果 |
|---|---|
| User 0 ordinary preferred / `set-home-activity` | 已排除；record 可存在但 Fire 仍勝出 |
| Child profile Tahoe HOME | 已證實但僅限 child user；不是 User 0 替換 |
| Accessibility foreground redirect | 暫時方案；需使用者授權，resolver 不變，結果受時序影響 |
| Manifest Lock Task | 暫時 foreground retention；重開機後不持久，不是 HOME |
| SystemUI observer / `initiateLauncher` | 未證實是 HOME writer；不能以名稱或 observer 推論 |
| OOBE/OTA lifecycle | 高影響但 lifecycle-bound；未形成普通 caller 路線 |

## Evidence classification

- **已證實：** `PV-LIVE-RO-01`～`PV-LIVE-RO-05`；User 0 HOME、candidate set、
  shell/SELinux 與本輪無 mutation。
- **高可信推論：** kernel/OTA source capability 與既有 caller/gate 結果的負向
  收斂；不等於完整漏洞不存在。
- **待驗證：** deny-list literal membership、完整 protected-broadcast provenance、
  recovery verifier/handoff、Accessibility timing 的 exact-build 重現。
- **已排除：** Phase 3A～6PV 已做且本輪再次去重的 priority、普通 preferred、
  KFT User-0 state mutation、未知 Binder replay、OTA/recovery/driver write。
- **因風險拒絕測試：** Root/exploit、未知 transaction/ioctl、OOBE broadcast、
  crafted OTA、updater/recovery、partition/boot/system 寫入。

## 最佳可行結果

若目標限定為「不 Root、不停用 Fire Launcher、不修改分割區」，目前最佳可
重現結果是：

1. **Child-user HOME：** Tahoe 可在 child user 成為該 user 的 HOME；回到 User 0
   仍是 Fire Launcher。
2. **Foreground redirect：** Accessibility 可在明確使用者授權下嘗試將 Fire
   前景導向 Microsoft，但它不是正式 HOME，且既有 clean-reboot 測量不穩定。

沒有證據支持把任一方案描述成「停用官方 Launcher」或「User-0 永久 HOME 替換」。

## Reproducibility and safety

新的整理腳本只讀三份 worker CSV 與 live capture：
`tools/scripts/build_phase6pw_route_classification.py`。它拒絕覆寫輸出，且自身
不呼叫 ADB/Binder。40-row normalized table 與 input hash manifest 位於
`output/tables/phase6pw-route-classification.csv` 及同名 `.manifest.json`。

本輪裝置只做 read-only capture；沒有 Root、未知 Binder/service call、ioctl、
package/settings mutation、Accessibility enablement、user switch、reboot、OTA、
recovery、flash 或 partition 操作。工作樹中原有未提交變更仍保持原樣。

