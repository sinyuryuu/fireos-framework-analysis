# Phase 6PV — broad privilege-route follow-up

日期：2026-08-10
裝置基線：`G001LT0511550CFT` / Amazon Fire HD 10 KFTRWI / `trona`
Build：`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`
公開基準：`f0c7ad38c412539307ba8fdb76e2596c309bb04c`

## 目的與安全範圍

本階段把研究從 Launcher 擴展到三個可能造成更廣泛權限效果的面：

1. PS7331 GPL kernel／MediaTek／Amazon driver source；
2. Amazon Framework／system-service Binder caller→gate→sink；
3. PS7331 OTA、native updater、post-install、OOBE 與 path/canonicalization。

檔案搜尋與既有結果整理由三個 `luna_worker` 平行完成，主 Agent 只整合和
驗收。所有 worker 均為 host-only：沒有 ADB、Binder/service call、broadcast、
provider write、package/settings mutation、ioctl、Root、exploit、OTA/recovery、
reboot、sideload、flash 或 partition write。原始 evidence 未覆寫。

## 結論摘要

### 已證實

- PS7331 GPL tree 的 Amazon driver 位於 `drivers/staging/amazon`，不是
  `drivers/amazon`；獨立的 `platform/vendor/mediatek` 目錄不能單憑存在性
  當作 booted kernel build provenance。
- kernel source 有 CMDQ、ION、GED、M4U、RPMB、evdev、USB 與 Amazon proc/sysfs
  surfaces，但已保存的 kernel→AMS/ATMS/PMS/HOME 搜尋沒有直接 edge。
- 唯一已保存的低權限 driver runtime 是 shell 對 `/proc/ged` 的 read-only
  query；沒有 package、HOME、system/root effect。
- `IAmazonActivityManager` tx1 與 `IAmazonUserManager` tx4 是已實機閉合的
  ordinary-app deputies，但效果分別限制在 process prewarm 與兩個 setup
  settings flags；兩者都沒有 package/HOME/root sink。
- KFT tx3 的 system-server code 具有 child-scoped Fire/Tahoe/Launcher3
  state writer；既有 User 10／User 0 runtime gate 結果已保存，本輪不重播。
- signed OTA/native updater 確實具有 recovery-context 的 extraction、
  block-image、`open`/`write`/`rename`/`chown` 能力，但沒有 untrusted
  shell/app caller route 證據。
- GPL source outer tar 已由 Phase 6MI 完整流到 EOF：35 members，未 extract、
  未 execute、未改 device。這項結果覆蓋並 supersede Phase 6FE 舊的 bounded
  listing limitation；不代表 signed OTA recovery writer 可以由 shell 觸發。

### 高可信推論

- 「持有 signature|privileged permission」不是「可接受 Fire protected target
  mutation」。Vending、KOR、ManagedProvisioning、H2、DPM 等 holder／service
  都仍要通過 caller、binding、user/profile、DCP、admin 或 lifecycle gate。
- `clearCallingIdentity()` 使 system-server 能執行後端操作，但不會把任意
  ordinary caller 變成 root；真正的 caller authorization 必須在 identity
  clear 前完成，或由下游 PMS／DPM 再檢查。
- 目前正式 HOME／Fire package replacement 的最短路徑仍是受保護的 PMS
  package/component state writer；driver、OTA 與 generic package writer
  尚未提供一條較低權限的替代路徑。

### 待驗證

- ION/RPMB/evdev/USB 的實際 product file-context、SELinux domain 與 native
  caller coverage仍可主機端補全，但目前沒有 framework/HOME edge。
- Play Store skipped DEX/native/resource regions 與 OTA updater 的 indirect
  CFG/dataflow 仍可離線加深；這不是進行 device exploit 的理由。
- OOBE `BOOT_AFTER_SYSTEM_OTA` 的 numeric user scope 仍依 system-server
  context propagation 佐證，沒有手動 replay。

### 已排除／因風險拒絕

- kernel source literal 或 userspace-facing ioctl 本身不能證明 LPE、root 或
  HOME control；CMDQ secure-metadata、ION、M4U、RPMB write、DMA/readback、
  GED bridge/reset 均不執行。
- KFT tx3、DPM owner/provisioning、H2 transaction、Play Store receiver／
  setter、KOR DCP broadcast、OOBE replay、OTA/recovery、symlink/traversal、
  malformed package、Root exploit 與 partition write 均不執行。

## 1. Kernel/GPL driver surface

### Source provenance

- Source archive：`firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2`，
  SHA-256 `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`。
- Build-selected source：
  `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4`。
- Boot image：`firmware/extracted/PS7331/boot.img`，SHA-256
  `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`。
- Source/config linkage：`kernel/source-manifest.json` 與
  `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config`。

### Decision

CMDQ 與 ION 的 `unlocked_ioctl`／compat／user-copy surfaces 是 source
capability；`copy_from_user()`、device registration、看似寬鬆的 mode 或缺少
local `capable()` 不足以證明 caller 可達或存在 memory primitive。GED query
已被實機觀察為 telemetry-only。Amazon `amzn_ld` 的 sysfs source store
handlers 沒有 live exposed node／shell write evidence。

因此 kernel 面目前的最小閉合為：

```text
ordinary/shell
  -> (only saved safe case) /proc/ged read query
  -> GED telemetry
  -X-> PackageManager / ActivityTaskManager / HOME / system UID / root
```

其餘 CMDQ、ION、M4U、RPMB、evdev、USB 只可做 host-only registration、config、
file-context、SELinux、native-caller join；不做 ioctl、DMA、debugfs、sysfs 或
module-parameter mutation。

## 2. Binder/IPC sink closure

完整 8-route machine table 在
`work/luna_worker_ipc_sink_inventory_followup_20260810.csv`。核心結果：

| Route | Result | 判定 |
|---|---|---|
| tx1 prewarm | ordinary APK 可建立 system-server prewarm process | 已證實 bounded deputy；無 package/HOME/root |
| tx4 User 0／User 10 | ordinary APK 可寫固定 setup flags，並可 rollback | 已證實 bounded settings deputy；無 package/HOME/root |
| KFT tx3 | static child-scoped Fire/Tahoe/Launcher3 writer；既有 PMS gates reject | static capability；ordinary accepted mutation 未證實 |
| H2 | signature `BIND_SERVICE`，profile lifecycle only | ordinary bind route closed；無 HOME sink |
| OOBE | system-server phase 550 + `isUpgrade()` lifecycle | trusted lifecycle；不等於 shell trigger |
| Vending | holder metadata + generic writers；無 bounded Fire/HOME target | provenance/caller unresolved；不視為 bypass |
| DPM | admin/owner/policy gate | trusted policy path；不建立 Device Owner |

這些結果直接回答「任何拿到權限是否就能關閉」：只有拿到被 PMS/DPM 接受的
trusted actor（例如 system/policy authority）才可能進入相應 writer；目前沒有
由 shell/ordinary app 取得該 actor 的證據。

## 3. OTA/post-install closure

signed PS7331 OTA 的 `updater-script:6-24` 與 native `update-binary` 可在
recovery/update context 寫 fixed block targets。Phase 6MD/6MM/6NE 也保存了
extraction、block-image、cache/canonicalization 與 direct-BL evidence。這些是
高權限 capability，不是普通 ADB caller route。

Phase 6MI 的 EOF-complete source archive audit：

- `artifacts/phase6mi-source-tar-eof-20260810-03/summary.json`
- `member_count=35`
- `reached_eof=true`
- `sensitive_hit_count=2`，僅 launcher/home 名稱分類
- `extracted=false`、`executed=false`、`device_mutation=false`
- summary SHA-256：`409ed81ede46db87a0ef8a05cc33b99df2b66e068d1edc1ac481a42e0606169b`

因此可把「source tar outer stream 未到 EOF」標為已修正的歷史限制；仍不能
把 recovery writer、symlink/canonicalization markers 或 OOBE receiver 當作
安全的 ADB launcher replacement。

## 4. Current device state

本輪沒有新的 mutating test。最新 Phase 6PT 唯讀 capture 已驗證：

- serial：`G001LT0511550CFT`，ADB `device`；
- caller：UID 2000 shell；SELinux Enforcing；
- fingerprint：`Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`；
- HOME：`com.amazon.firelauncher/.Launcher`，effective priority 50；
- candidates：Fire 50、Microsoft 0、FallbackHome -1000；
- capture：`adb/phase6pt/PHASE6PT-READONLY-20260810-01/`，其
  `sha256sum -c sha256sums.txt` 已通過。

## 5. 最佳下一步

### 安全且有研究價值

1. 只在 host 上補全 ION/RPMB/evdev/USB 的 product policy/caller join；
2. 只在 host 上解析 Play Store skipped DEX/native/resource 與 updater indirect
   edges；
3. 將 generic holder provenance 與 PMS protected-package acceptance 分開
   維護；
4. 若未來自然發生官方 OTA，只收集 build/HOME/package/OOBE/log 唯讀 evidence。

### 不應執行

Root exploit、未知 Binder transaction、crafted/malformed/downgrade OTA、
recovery/updater execution、symlink/traversal、driver ioctl/DMA/readback、
sysfs/debugfs/module writes、SELinux/init/boot property mutation、fastboot、
flash、partition write、factory reset、停用或清除 Fire Launcher。

## 6. 最終階段判定

**已證實：** 目前 broad privilege surface 沒有新增可由 shell／ordinary app
取得 system/root、正式替換 HOME 或接受 Fire protected package mutation 的
路徑。

**高可信推論：** 若只允許不 Root、不修改分割區、不停用 Fire Launcher，最接近
目標的仍是既有 Accessibility/foreground redirect 類近似方案，而非正式 HOME
replacement；kernel/OTA 路線在目前證據下不應再以真機 exploit 驗證。

**待驗證：** 少數 host-only indirect/native/permission-provenance 缺口。

**因風險拒絕測試：** 所有會把 source capability 轉成 kernel/recovery write 或
system/root identity 的實機操作。
