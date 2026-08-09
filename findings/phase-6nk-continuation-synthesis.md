# Phase 6NK：IPC、OTA 與 Launcher 路徑續研整合

日期：2026-08-10
範圍：PS7331／Fire OS 7.3.3.1 的主機端靜態分析與既有測試結果整合。
本階段沒有執行 Root、提權 exploit、未知 Binder transaction、OTA／Recovery、ioctl、
分割區寫入、Fire Launcher 停用／隱藏／suspend／force-stop／clear，也沒有重做
priority APK、`set-home-activity`、KFT tx3 或既有 Accessibility 測試。

## Executive summary

### 已證實

1. 目前保存的 PS7331 corpus 中，唯一同時出現 Tahoe、Fire Launcher、Launcher3
   package/component state sink 的 Amazon writer 是
   `AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)`。
   三個 setter 都使用傳入的 `UserInfo.id`，不是硬編碼 User 0；既有 runtime 證據
   將它定位為 child/profile lifecycle writer。
2. `AmazonPackageManagerService` 的 tx1–tx11 是 metadata、flags、proxy 與 query
   contract；在已保存 contract 中沒有 formal HOME、preferred-activity 或一般
   package/component state setter。其 facade setter 仍落到標準 PMS gate。
3. Product Policy 的內部 action 具備 state-writing capability，但 PS7331 實際解析的
   policy inputs 沒有 `com.amazon.firelauncher`；該服務是 local/trusted path，沒有
   公開 shell-facing ProductPolicy Binder contract。
4. OTA／post-install／`otadexopt` 的能力分屬 recovery、system-server 或 dexopt
   context；目前沒有 shell／普通 APK 到 partition writer、HOME writer 或 root 的
   完整可達鏈。
5. 已驗證的 Accessibility／foreground redirect 是目前最接近實用的替代體驗，但
   resolver、Home key 的正式 HOME 選擇與 Fire package state 都沒有被改寫。

### 高可信推論

- 在已保存的 system-server、Amazon services、fosinit、Settings、OOBE、OTA 與
  driver/source 範圍內，沒有新的 ordinary-app／shell User 0 HOME writer。
- 目前 Fire Launcher 的 User 0 結果仍可由 privileged/system package 與標準 PMS
  protected-package／resolver 條件解釋；沒有證據需要把結果歸因於一個可由 shell
  呼叫的 Amazon confused-deputy service。
- 任何「Stub method 沒看到 UID check」的觀察都不足以證明漏洞；service-manager
  SELinux、下游 PMS caller gate、user scope 與輸入來源必須同時閉合。

### 待驗證

- KFT tx3 的完整 inherited/generated authorization 仍未從所有 runtime-loaded
  caller 與 superclass scope 完整閉合。
- OOBE sender／receiver 的實際 delivery user 尚未由保存資料直接證明為 User 0。
- 完整 runtime `fosinit`／class-loader 載入集合與保存 corpus 的一一對應仍是輸入
  完整性問題，不是 HOME writer 證據。
- OTA native stripped ELF 的完整 CFG、函式指標與 return-value data flow 仍可在
  host 上深化，但目前沒有安全理由將它轉成 crafted OTA 或 updater 測試。
- MediaTek/Amazon driver source 顯示 ioctl/proc/sysfs/debug surface；量產 node
  mode、SELinux label、caller reachability 與安全影響仍未證明。

### 已排除（狹義命題）

- 普通 sideloaded APK 以 manifest priority 超過 Fire Launcher。
- ordinary `set-home-activity` preferred record 取代 Fire 的 User 0 formal HOME。
- KFT tx3 作為 unconditional User 0 HOME selector。
- Product Policy 以 PS7331 實際 policy files 作為正常 User 0 Fire restoration writer。
- 只因 service name 出現在 `service list` 就能由 shell 取得 Amazon private Binder
  handle。
- OTA archive、`otadexopt` 或 source 中出現 writer／ioctl 字串，就等於存在普通
  caller 可用的 root 或 HOME bypass。

## 證據整合

| Evidence ID | 來源 | 觀察 | 判定 |
|---|---|---|---|
| 6NK-IPC-001 | `work/luna_worker_phase6_ipc_kft_audit_20260810.md`; `fosservices/disassembly.log:54297-54325` | KFT writer 對 Tahoe、Fire、Launcher3 使用 `UserInfo.id` | Confirmed |
| 6NK-IPC-002 | `boot-fosframework/disassembly.log:370378-370750`; `fosservices/disassembly.log:54415-54478` | tx3 contract 與 bounded method entry；完整 inherited authorization 未閉合 | Confirmed contract / Unknown authorization |
| 6NK-IPC-003 | `adb/phase6fj/`、`adb/phase6fk/`、`adb/phase6cz/` 既有 evidence | ordinary caller 的下游 cross-user/PMS gate 與 shell service-manager boundary | Confirmed |
| 6NK-IPC-004 | `work/luna_worker_phase6_ipc_kft_audit_20260810.md` | Amazon PM tx1–tx11 沒有 formal HOME/package-state setter | Confirmed, bounded |
| 6NK-POL-001 | `findings/phase-6ce-product-policy-firelauncher-boundary.md`; `adb/phase6ce/` | 四個 PS7331 policy inputs 沒有 Fire Launcher entry；服務為 local/trusted path | Confirmed |
| 6NK-OTA-001 | `work/luna_worker_phase6_ota_postinstall_audit_20260810.md`; `findings/phase-6p-native-updater-closure.md` | OTA writer capability 與 ordinary caller reachability 分離 | Strong evidence |
| 6NK-OTA-002 | `adb/phase6ae/`、`adb/phase6bk/` 既有 captures | `otadexopt` 只證明 adjacent shell-visible dexopt path，未證明 partition/HOME writer | Confirmed, bounded |
| 6NK-SRC-001 | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2`; `findings/phase-6an-gpl-scope.md` | 官方 source corpus 沒有 Android userspace `system/core/init`／`selinux.cpp` | Confirmed |
| 6NK-LAUNCH-001 | `work/luna_worker_phase6_launcher_options_20260810.md`; `findings/home-priority-experiment.md` | priority／ordinary preferred／child／Accessibility 既有結果的排除矩陣 | Confirmed, by existing evidence |
| 6NK-LAUNCH-002 | `findings/phase-6hb-ms-accessibility-reboot-persistence.md` | foreground fallback 可跨既有 reboot/rebind capture，但不是 formal HOME | Confirmed / Strong evidence |

Worker output SHA-256：

```text
93d6b39f721b1bd1e31f1d0423336f21343f8bca537147b437196827e3852755  work/luna_worker_phase6_ipc_kft_audit_20260810.md
7ee15036830b408152856c84dea8bd24050a8ff6a102de40383413e3d83f7629  work/luna_worker_phase6_ota_postinstall_audit_20260810.md
b4bef7a2b56d7378e0b293ff91b2db9c6f964a7fd4342189770492dd317fcad0  work/luna_worker_phase6_launcher_options_20260810.md
```

## Route disposition

```text
ordinary APK / shell
  ├─ standard PMS setter ───────────────► protected-package / caller gate ─► rejected
  ├─ ordinary preferred HOME ───────────► resolver priority/trust boundary ─► Fire
  ├─ Amazon private Binder name ────────► SELinux service-manager boundary ─► no handle
  ├─ KFT tx3 ───────────────────────────► supplied child/profile UserInfo.id ─► child HOME only
  ├─ Product Policy ────────────────────► fixed PS7331 policy inputs ───────► no Fire entry
  ├─ OTA/post-install ─────────────────► recovery/system lifecycle ───────► no ordinary route
  └─ Accessibility redirect ───────────► foreground Activity ──────────────► near-term fallback
```

The last branch is intentionally not labelled HOME replacement. It changes what is visible
after an event; it does not change PackageManager's formal `resolve-activity` result or Fire
Launcher enabled state.

## Best current practical result

**分類：D — Accessibility／foreground workaround。**

- 不需要 Root 或系統分割區修改。
- 需要研究者在 Settings 明確啟用服務。
- 既有 capture 顯示可在 Home/解鎖與服務重新綁定條件下將第三方 Activity 帶到前景。
- 仍可能先短暫顯示 Fire Launcher，且受 Android/Fire OS 背景限制、服務重啟與 timing
  影響。
- 不應宣稱為 default HOME、resolver replacement 或 package-state bypass。
- 關閉服務即可回到原生 Fire Launcher 行為；不需修改 Fire Launcher package state。

## 下一個最小安全目標

目前不應進行新的裝置 mutation。下一個資訊增益最高的步驟是 host-only：

1. 取得並核對所有 runtime `fosinit` registration／class-loader 來源，確認保存的
   callback/service corpus 是否完整。
2. 對 KFT tx3 補齊 inherited Stub/superclass authorization 與所有 caller reference，
   仍只做靜態 mapping。
3. 對 OTA native updater 僅做 selected `CacheSizeCheck`／`MakeFreeSpaceOnCache`
   caller 與 return-value data-flow；不執行 updater、不構造 OTA、不寫 recovery。
4. 對 driver source 只做 config、build object、node label/mode 的 provenance mapping；
   不開啟 `/dev`、不送 ioctl、不嘗試 root。

若上述三條 host-only closure 都沒有新增「ordinary caller → User 0 → Fire/HOME sink」
證據，則正式 HOME replacement 的下一步只剩系統簽章、Root 或 framework/partition
修改，均不屬於目前可安全驗證的路徑；Accessibility foreground fallback 仍是最接近的
可還原方案。

## 安全紀錄

本階段未連接裝置執行研究命令（僅確認既有 ADB 連線狀態），未發送 Binder、broadcast、
input injection、OTA、ioctl 或 package/settings mutation。未使用或保存任何裝置解鎖
憑證。
