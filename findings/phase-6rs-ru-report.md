# Phase 6RS–RU — Settings/PMS、SystemUI callback 與 rootless fallback closure

日期：2026-08-10
公開基準：`224e126eb2cea75a7817bff34c2afbe63e35f1b1`
裝置基準：Phase 6RG exact-device snapshot，PS7331.4463N / `KFTRWI` / `trona`

## Executive summary

本輪由三個 `luna_worker` 進行 host-only 搜尋與既有測試整理：

| domain | rows |
|---|---:|
| SettingsProvider / PMS / Amazon PM writer | 10 |
| SystemUI / Amazon callback | 14 |
| rootless fallback | 11 |
| **合計** | **35** |

本輪沒有找到新的 system/root relay，也沒有 formal HOME replacement。最重要的結論是：

- **已證實**：SettingsProvider 的 global/secure/system mutation 先經 caller、user、
  permission/AppOps 檢查；保存切片沒有顯示可由 `clearCallingIdentity()` 繞過的路徑。
- **已證實**：PMS `setHomeActivity()` 可寫入 preferred-activity XML，但這只是
  preferred sink；HOME resolver 仍可依候選排序選 Fire priority 50。
- **已證實**：保存的 SystemUI resource arrays、AppCompat/Eve callback、WMS/AMS
  callback 沒有 `com.amazon.firelauncher/.Launcher` 的 explicit launch 或 package/
  component state writer。
- **高可信推論**：目前 Fire HOME 行為主要仍由標準 resolver/candidate ranking 與受保護
  package state 共同決定，而不是 SystemUI 硬編碼啟動 Fire。
- **已確認的近似方案**：需使用者明確同意的 Accessibility delayed foreground redirect；
  它可能在保存的測試中把第三方 Activity 帶到前景，但不是 HOME、不是 package state
  mutation，也不會給予 system/root 身份。
- **已排除（有界）**：UsageStats、PendingIntent、普通 `set-home-activity`、Settings
  Home picker、舊 direct-start Accessibility、ADB monitor 都不能被標記為持久正式
  HOME replacement。
- **待驗證**：AmazonApplicationFlags 的 permission holder/production caller、完整
  SystemUI resource overlay、自然 OTA 後的 OOBE writer，以及未取得的 native client。
- **因風險拒絕測試**：未知 Binder、settings/package mutation、Accessibility/UsageStats
  新啟用、OTA/recovery、driver、Root/exploit 與分割區操作。

## 1. SettingsProvider 與 PackageManager

### 1.1 SettingsProvider — 已證實

保存的 Android 9 `SettingsProvider.java` 切片顯示：

- global/secure/system write API 透過 `enforceWritePermission` 或相應的 secure/
  write-settings operation gate；
- calling user 會進入 `resolveCallingUserIdEnforcingPermissionsLocked`，跨 user 另經
  `ActivityManager.handleIncomingUser`；
- secure writes 受 `WRITE_SECURE_SETTINGS`、restricted-setting 與 owning-user 條件
  約束；
- bounded mutation path 沒有在 permission/user checks 之前 `clearCallingIdentity()`；
- first sink 是 `SettingsRegistry`/`SettingsState` 與 settings XML，不是 PMS Fire
  package state。

因此「shell 可以寫某個 settings namespace」不能直接推成「能寫 HOME 或取得 system
identity」。已存在的隨機 settings/overlay 測試不重做。

### 1.2 PMS HOME writer — 已證實／核心解釋

`setHomeActivity()` 會先驗證目標與指定 user 的 HOME candidates，再呼叫
`replacePreferredActivity()`；後者受 cross-user 與 `SET_PREFERRED_APPLICATIONS` gate，
並把 preferred record 寫入 per-user XML。

這解釋了 Phase 3C 的表面現象：`set-home-activity` 寫入 `mAlways=true` record 並不
保證 resolver 最後採用它。Fire priority 50 的候選仍可在有效選擇時勝出。這是
**高可信推論**，不是新的 Fire hardcode 證據。

### 1.3 Amazon PM metadata — 待驗證

四個 mutator（flags/metadata add/remove）受 `amazon.permission.ADD_RM_PKG_METADATA`
保護，接受 explicit user，進入 `AmazonApplicationFlags`。目前保存 corpus 沒有完整
permission holder、production caller 或第一個把 metadata 轉成 HOME/package state 的
consumer，也沒有 `clearCallingIdentity()` 的證據。

因此它是 **STATIC CAPABILITY / CALLER UNKNOWN**，不是 shell confused deputy。

## 2. SystemUI 與 Amazon callback

### 2.1 SystemUI arrays — 已證實

`amz_config_systemUIServiceComponents` 是 service bootstrap 清單；
`config_systemUIServiceComponentsPerUser` 在保存 resource slice 中為空。它不是 HOME
resolver，也沒有找到 Fire Launcher explicit component。

### 2.2 Callback closure — 高可信推論

- AppCompat/Eve 的 pre-resolution path 主要取得 PackageManager `ResolveInfo` 或 null；
  未見自行建立 Fire `ComponentName`。
- `LauncherHijackPreventer` 是 HOME-task visibility/permission gate，不是 package state
  writer。
- WMS/AMS callbacks 主要處理 window、visibility、PIP、activity event 或 observer。
- Profile callbacks 具 profile picker/metadata 作用，但沒有 preferred HOME setter。
- OOBE/OTA receiver 是明確 component/setup writer，但 sink 是 OOBE，不是 Fire Launcher。

保存 corpus 未找到 SystemUI 直接啟動 `com.amazon.firelauncher/.Launcher` 的證據。

## 3. Rootless fallback assessment

### 已確認可用但非正式 HOME

Accessibility delayed foreground redirect 是目前最好的近似方案：需要使用者在 Settings
明確啟用 Accessibility，保存測試有 service rebind 與 delayed explicit third-party
launch；重試延遲約 350/1000/1800 ms，可能先短暫看到 Fire。

它不修改 resolver、preferred record、Fire package state 或 system identity。停止 service、
移除已知自建 APK、恢復 secure setting 後可回到 Fire。

### 已排除或降級

- 舊 Accessibility direct-start：保存結果 0/30，不可靠。
- ADB foreground monitor：保存結果 5/5，但必須持續 host/ADB；停止後回 Fire，不能跨
  reboot 持久。
- UsageStats：需要 Usage Access/AppOps，僅能觀察 foreground，沒有 HOME writer。
- PendingIntent：只能送出 explicit Activity，不能提高 creator 權限或改 resolver。
- Settings/Home picker：本 build 沒有可達的正式 Home selector。
- LauncherHijack/Fire Toolbox 歷史 corruption/disable 路線：版本依賴、可能破壞可操作
  性，沒有一般 reversible API 保證；未下載或執行未知 binary。

## 4. 綜合判定

### 已證實

1. 普通 SettingsProvider write path 不等於 HOME/package writer。
2. `set-home-activity` 的 preferred persistence 不等於 effective resolver win。
3. 保存的 SystemUI/Amazon callback corpus 沒有 Fire explicit launch hardcode。
4. Accessibility redirect 是 foreground fallback，不是 formal HOME 或 privilege route。

### 高可信推論

Fire OS 7 User 0 的正式 HOME 結果目前最能由：

```text
HOME candidates
  → Fire privileged/system candidate priority 50
  → ordinary sideload candidate effective priority 0
  → resolver selection
  → Fire Launcher
```

加上 protected package state 解釋；本輪沒有發現需要額外 SystemUI Fire hardcode 的證據。

### 待驗證

- Amazon PM metadata exact permission holder、production caller、consumer。
- 完整 SystemUI overlay/resource array 與 native callback。
- 自然 OTA 後 OOBE writer 的 exact user mapping。
- 未取得的 native client/domain allow。

### 已排除（指定 build/scope）

- 普通 preferred activity 單獨跨越 priority 差距。
- Settings/Home picker 作為正常 GUI HOME writer。
- PendingIntent、UsageStats 或 foreground monitor 作為 formal HOME／system relay。
- service list / exported metadata 單獨作為 private Binder 可達性證據。

## 5. 安全界線與未執行項目

本輪沒有：

- 呼叫未知/private Binder 或 protected broadcast；
- 修改 settings、preferred activity、package/component、AppOps、overlay 或 user/profile；
- 新啟用 Accessibility/UsageStats、安裝 APK 或重跑已完成 redirect；
- 開啟 driver node、ioctl、OTA/recovery/updater、Root/exploit、remount、SELinux 或
  partition。

上述屬 **因風險拒絕測試**，不是 runtime negative。

## 6. 下一個最小研究目標

只剩下具體的 host-only provenance closure：

1. 找出 `AmazonApplicationFlags` 的 exact permission holder 與 production caller；
2. 完整解析 SystemUI overlay/resource array 對應的 callback class；
3. 補齊 OOBE/native client 的 exact user/domain mapping。

若仍無 ordinary caller 到高影響 sink 的閉合鏈，正式 HOME replacement 應結案為目前
不可行；可保留需明確使用者授權、可回復的 Accessibility foreground fallback。

## 7. Artifact index

- `findings/phase-6rs-ru-report.md`
- `findings/phase-6rs-ru-evidence-index.md`
- `output/tables/phase6rs-ru-privilege-surface.csv`
- `output/tables/phase6rs-ru-privilege-surface.csv.manifest.json`
- `output/call-graphs/phase6rs-ru-control-surfaces.mmd`
- `output/call-graphs/phase6rs-ru-control-surfaces.md`
- `tools/scripts/build_phase6rs_ru_surface.py`
- `work/luna_worker_phase6rs_settings_pm_closure_20260810.md/.csv`
- `work/luna_worker_phase6rt_systemui_callback_closure_20260810.md/.csv`
- `work/luna_worker_phase6ru_rootless_fallback_review_20260810.md/.csv`
