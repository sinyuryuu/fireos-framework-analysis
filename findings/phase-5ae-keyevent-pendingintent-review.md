# Phase 5AE：Android `onKeyEvent(KEYCODE_HOME)` + `PendingIntent` 實作

## 範圍

本輪驗證一個與歷史 direct-`startActivity()` 不同的 Android 公開 API 實作：
`AccessibilityService.onKeyEvent()` 只接收 `KEYCODE_HOME`，在研究者手動啟用
Accessibility 服務及 app 內 toggle 後，以明確 `PendingIntent.getActivity().send()`
啟動本專案測試 Activity。

這是前景 redirect 實驗，不是 HOME resolver replacement。實作不修改
`com.amazon.firelauncher`，不寫 Settings／AppOps／preferred activity，不使用 overlay、
網路、device-admin、私有 Binder 或 Root。

## Exact-device boundary

| 欄位 | 值 |
|---|---|
| Device serial | `G001LT0511550CFT` |
| Fire package | `com.amazon.firelauncher` |
| Test redirect package | `org.fireosresearch.phase4.redirect` |
| Test target | `org.fireosresearch.phase4.alias/.HomeActivity` |
| HOME before preparation | `com.amazon.firelauncher/.Launcher`, effective priority 50 |
| Accessibility before preparation | `services:{}`；未啟用 |
| Redirect APK SHA-256 | `e6a5536d11ff6be5de557d751817af7de69d841f7cd0d03e028d5da2537b013a` |
| Alias APK SHA-256 | `ac87bf9fde1ea1d501ef2ff5ce4ebe5e062952432f990384a64cbe49f77aa68a` |

## Android implementation

來源：
`tools/phase4-accessibility/src/org/fireosresearch/phase4/redirect/LauncherRedirectService.java`
及 `res/xml/accessibility_service_config.xml`。

1. Manifest/XML 與 `onServiceConnected()` 請求公開的
   `FLAG_REQUEST_FILTER_KEY_EVENTS`。
2. `onKeyEvent()` 僅接受 `KEYCODE_HOME`；非 HOME 按鍵直接回傳 `false`。
3. app 內 toggle 未開啟時回傳 `false`，讓系統正常處理 HOME。
4. HOME `ACTION_DOWN` 建立 explicit `ComponentName`，以
   `PendingIntent.getActivity(...).send()` 啟動測試 Activity；只有派送成功才消費
   該按鍵，`ACTION_UP` 只在前一個 DOWN 被消費時回傳 `true`。
5. 事件路徑仍有 1500 ms cooldown；視窗事件路徑仍只接受 Fire Launcher 的
   `TYPE_WINDOW_STATE_CHANGED`，兩者共用同一個 guarded dispatcher。
6. 目標 Activity 不使用 `CATEGORY_HOME`，因此不會寫入或改變 PackageManager HOME
   resolver。

建置採用本地 raw SDK：Android platform API 35、Build Tools 35.0.0、JDK 17，沒有
使用 Gradle／AGP。產物的 v3 signature verification 為 true；APK 與 signing key 不
提交到 repository。

## Evidence

| Evidence ID | 證據 | 觀察 | 判定 |
|---|---|---|---|
| P5AE-STATIC-001 | local source SHA-256 `37ff8777f38c0a1f2c70adc4a28bc55cfb3cb9b4f07cb9052edb0846ddbc32a0` | 存在 `onKeyEvent`、`KEYCODE_HOME`、key-event filter 與 PendingIntent dispatcher | **已證實**：Android 實作邊界 |
| P5AE-BUILD-001 | `tools/phase4-accessibility/dist/20260804-keyevent-pendingintent-jdk17-01/build-manifest.tsv` | APK SHA 為 `e6a5536d...7b013a`，v3 signature verification 成功 | **已證實**：可重現建置 |
| P5AE-PREP-001 | `adb/phase5/PHASE5AE-KEYEVENT-PENDINGINTENT-T01/` | 只安裝兩個研究 APK；Accessibility `services:{}`，HOME 仍是 Fire Launcher | **已證實**：安裝不等於授權，正式 HOME 未改變 |
| P5AE-ROLLBACK-001 | `adb/phase5/PHASE5AB-PENDINGINTENT-ROLLBACK-T01/` | 先前 pending-intent variant 已獨立移除；ADB 保持 device，resolver 回 Fire Launcher | **已證實**：前一輪測試可回復 |
| P5AE-MEASURE-001 | 預定：`adb/phase5/PHASE5AE-KEYEVENT-PENDINGINTENT-T01/measure/` | 必須由研究者在 Settings 手動啟用服務後產生 | **待驗證** |

## 與歷史實測的差異

| 路徑 | 觸發 | 啟動 API | KFTRWI 結果 | 判定 |
|---|---|---|---:|---|
| PHASE4-ACCESSIBILITY-T03 | Fire window event | direct `startActivity()` | 0/30 foreground handoffs | **已排除：該實作在當時條件不可用** |
| Phase 5AE source variant | `onKeyEvent(KEYCODE_HOME)` | `PendingIntent.getActivity().send()` | 尚未完成人工授權測量 | **待驗證** |
| 正式 HOME | system HOME path | PackageManager／ActivityTaskManager | Fire Launcher | **已證實：本實作不改變 resolver** |

## 安全界線與 rollback

Preparation 唯一裝置變更是安裝 redirect APK 與 alias APK。沒有執行
`settings put`、Accessibility enable、Fire Launcher mutation、reboot、未知 Binder、
Root、kernel trigger 或 boot-chain 操作。

測量前必須由研究者：

1. 在 Settings 手動啟用服務；
2. 在控制頁打開 `Redirect enabled`；
3. 測量有限次數的 HOME key／foreground 結果。

Rollback 前必須關閉 app toggle 並在 Settings 手動停用服務，之後才可執行：

```sh
tools/scripts/run_phase4_accessibility_experiment.sh --phase rollback \
  --serial G001LT0511550CFT \
  --test-id KEYEVENT-PENDINGINTENT-ROLLBACK-T01 \
  --output adb/phase5/PHASE5AE-KEYEVENT-PENDINGINTENT-T01 \
  --approve-state-change \
  --approval-phrase 'APPROVE PHASE4-KEYEVENT-PENDINGINTENT-ROLLBACK-T01'
```

腳本只移除兩個研究 APK，並驗證 Fire Launcher resolver 及 ADB device state；不觸碰
Fire Launcher package state 或資料。若 Accessibility 仍顯示 enabled，腳本會拒絕移除。

## 目前結論

- **已證實：** 這是合法公開 Android API 的 key-event foreground redirect，不是 HOME
  resolver 改寫。
- **高可信推論：** 相較直接 `startActivity()`，PendingIntent 改變了背景啟動邊界，
  值得一次受控測量；但 source-level 差異不能推導裝置成功。
- **待驗證：** Fire OS 是否允許已人工授權的 Accessibility service 以此路徑在
  `KEYCODE_HOME` 後把測試 Activity 置為 resumed/focused，以及是否先短暫顯示 Fire
  Launcher。
- **已排除：** 此 APK 可永久成為 HOME、改變 `resolve-activity`、移除 Fire Launcher
  protection 或跨重啟保存正式 HOME。
- **因風險拒絕測試：** Root/CVE native trigger、futex race、AEE/ION/CMDQ ioctl、
  BROM/DA、preloader/LK、fastboot unlock、boot image 或分割區寫入。

## 重現

```sh
JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home \
PATH=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home/bin:$PATH \
tools/phase4-accessibility/build_redirect.sh \
  --output tools/phase4-accessibility/dist/20260804-keyevent-pendingintent-jdk17-01 \
  --keystore /tmp/phase5ab-local.keystore \
  --keystore-password phase5ab-local \
  --key-alias fireos-phase4
```

測量與 rollback 僅使用 `tools/scripts/run_phase4_accessibility_experiment.sh`，並使用
新的唯一 Test ID；不得覆寫 T03 或 T01 原始證據。
