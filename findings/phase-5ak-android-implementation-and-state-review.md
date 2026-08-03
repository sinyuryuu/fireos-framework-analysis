# Phase 5AK：Android 實作邊界與目前裝置狀態

日期：2026-08-04
範圍：Fire HD 10 2021 / `KFTRWI` / `trona` / `PS7330.4104N`
安全界線：只讀 ADB、離線 source review；沒有啟用 Accessibility、root、CVE
trigger、kernel/device-node 操作、BROM/DA、fastboot 或分割區寫入。

## 摘要

**已證實：** 本機 Android redirect 實作是「使用者明確授權的
`AccessibilityService` + explicit Activity + `PendingIntent`」，不是 HOME resolver
替換。它只嘗試把研究用 Activity 帶到前景，不能改寫
`cmd package resolve-activity`、preferred activity、Fire Launcher package state 或
system UID 權限。

**已證實：** 本次只讀基線中，Accessibility 沒有啟用，HOME resolver 仍為：

```text
priority=50 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true
com.amazon.firelauncher/.Launcher
```

**待驗證：** PendingIntent variant 在研究者手動啟用 Accessibility 服務及應用程式
toggle 後，是否能在 `KEYCODE_HOME` 後形成穩定的前景 redirect。這次沒有執行測量，
因此沒有成功率或延遲數字。

**已排除：** 這個 APK 能成為正式 HOME、跨重開機改變 resolver、或解除 Fire Launcher
保護。source 中 explicit component 是研究用 alias，沒有 `CATEGORY_HOME`、preferred
API、Settings provider write 或私有 Binder。

## 1. 裝置基線與原始證據

只讀採集腳本：
`tools/scripts/capture_phase5ak_android_implementation_state.sh`

原始輸出：
`adb/phase5/PHASE5AK-ANDROID-IMPLEMENTATION-STATE-20260804-01/`

基線摘要：

| 欄位 | 觀察 | 證據 | 信心 |
|---|---|---|---|
| ADB state | `device` | `devices.stdout.txt` | 已證實 |
| ADB caller | UID 2000 / `u:r:shell:s0` | `id.stdout.txt` | 已證實 |
| Accessibility setting | 空值 | `accessibility_setting.stdout.txt` | 已證實 |
| Accessibility services | `services:{}` | `accessibility_dump.stdout.txt` | 已證實 |
| HOME resolver | Fire Launcher / effective priority 50 | `home_resolver.stdout.txt` | 已證實 |
| redirect APK | 已安裝；裝置端 SHA-256 `e6a5536d11ff6be5...7b013a` | `redirect_path.stdout.txt`、Phase 5AE build record | 已證實 |
| alias APK | 已安裝；裝置端 SHA-256 `ac87bf9fde1ea1...aa68a` | `alias_path.stdout.txt`、Phase 5AE metadata | 已證實 |
| 測量 | 未執行 | 本輪沒有 `measure/` 輸出 | 已證實 |

完整檔案雜湊保存在 `sha256sums.txt`；該檔案 SHA-256 為
`80a743ad0a527cd7ef6fd94092caec84dd5428f357825fff8e71361df631060a`。

## 2. 本機 Android 實作

### 2.1 Manifest 與使用者同意

`tools/phase4-accessibility/config/AndroidManifest.xml:17-26` 宣告
`AccessibilityService` 及 `BIND_ACCESSIBILITY_SERVICE`。這只使服務出現在系統
Accessibility 設定頁；它不會自行取得授權。

`res/xml/accessibility_service_config.xml:2-8` 設定：

- 只接收 `typeWindowStateChanged`；
- `canRetrieveWindowContent=false`；
- 要求 `flagRequestFilterKeyEvents`；
- 沒有 device-admin、overlay 或網路權限。

Android 官方 API 將 `onKeyEvent()` 定義為 Accessibility service 在事件交給其餘
系統前觀察事件的 callback，並以 boolean 決定是否消費；服務本身仍須經使用者在
Settings 啟用：[AccessibilityService API](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService.html)。

### 2.2 `KEYCODE_HOME` 路徑

`LauncherRedirectService.java:39-57`：

1. 忽略非 `KEYCODE_HOME`；
2. visible toggle 未開啟時回傳 `false`，交回正常 HOME 路徑；
3. `ACTION_DOWN` 嘗試 dispatch；只有 dispatch 成功才記錄為 consumed；
4. 對應 `ACTION_UP` 才回傳 `true`，避免只吃 down 不吃 up 的不完整事件流。

### 2.3 Fire Launcher 觀察路徑

`LauncherRedirectService.java:59-73` 只接受 package name 等於
`com.amazon.firelauncher` 的 `TYPE_WINDOW_STATE_CHANGED`。這是「觀察 Fire Launcher
已成為前景」的 callback，不是 PackageManager 或 ActivityTaskManager 的 resolver
hook。

### 2.4 啟動邊界

`LauncherRedirectService.java:75-101` 建立：

```text
ACTION_MAIN + CATEGORY_LAUNCHER
    + explicit ComponentName(org.fireosresearch.phase4.alias/.HomeActivity)
    + NEW_TASK | EXCLUDE_FROM_RECENTS | CLEAR_TOP | REORDER_TO_FRONT
    → PendingIntent.getActivity(...).send()
```

Android 官方 API 將 `PendingIntent` 描述為由系統代為執行已建立的 operation；它不會
把 explicit `CATEGORY_LAUNCHER` Activity 轉成 HOME resolver record：
[PendingIntent API](https://developer.android.com/reference/android/app/PendingIntent.html)。

因此 Android 端的實際分層是：

```mermaid
flowchart TD
    A[使用者在 Settings 啟用 Accessibility] --> B[AccessibilityManagerService]
    B --> C[LauncherRedirectService.onKeyEvent]
    B --> D[LauncherRedirectService.onAccessibilityEvent]
    C --> E{visible toggle}
    D --> F{package == com.amazon.firelauncher}
    E -->|yes| G[dispatchRedirect]
    F -->|yes| G
    G --> H[explicit ACTION_MAIN + CATEGORY_LAUNCHER]
    H --> I[PendingIntent.getActivity().send]
    I --> J[研究用 alias Activity 前景嘗試]
    K[PackageManager HOME resolver] -.未被呼叫或改寫.-> L[Fire Launcher priority 50]
```

## 3. 與正式 HOME 的差異

| 路徑 | 選擇者 | intent | 是否改變正式 HOME | 目前結果 |
|---|---|---|---|---|
| Home key（未授權） | system input/Activity path | system HOME | 否 | Fire Launcher |
| `am start MAIN + HOME` | PackageManager/Activity path | implicit HOME | 否 | Fire Launcher |
| redirect `onKeyEvent` | user-consented Accessibility service | explicit `CATEGORY_LAUNCHER` | 否 | 尚未測量 |
| redirect window observer | user-consented Accessibility service | explicit alias Activity | 否 | 尚未測量 |

歷史 direct `startActivity()` 版本在 `PHASE4-ACCESSIBILITY-T03` 已為 0/30 前景
handoff；那個結果排除的是該具體實作與測試條件，不可誇大成所有 Android foreground
API 都必然失敗。PendingIntent variant 仍須獨立測量。

## 4. GhostLock／CVE 與 Android 實作層

### `CVE-2026-3499`

**已排除：** 這個編號不是 Android kernel 漏洞；公開 NVD 記錄指向 WordPress
Product Feed PRO for WooCommerce CSRF。它不是本裝置的 root 或 Android implementation
候選。

### GhostLock／`CVE-2026-43499`

**已證實：** Android 端若有 implementation，邊界是 native process → Bionic/syscall
→ Linux futex/rtmutex kernel；不是 Java Framework、Launcher 或普通 APK 權限。

公開 Android 研究實作以裝置／build profile 為中心，包含 Android NDK native code、
target-specific headers 及離線 target-generation tooling；公開索引列出的目標是
Xiaomi、OnePlus、OPPO、Pixel 等其他 kernel/build，沒有本機
`KFTRWI/trona/MT8183/PS7330.4104N` profile：[Mallory GhostLock research index](https://www.mallory.ai/vulnerabilities/CVE-2026-43499)。

**高可信推論：** 其他 Android 5.10/6.12 或不同 SoC 的 target header、offset、KASLR
假設與 post-exploitation code 不能直接套用到本機 Linux 4.4.146+。

**因風險拒絕測試：** futex race、kernel memory write、credential/SELinux stage、
未知 native payload，以及任何需要 boot image 或分割區輸入的 exploit adaptation。

### `CVE-2026-43503`

**已證實：** 這是另一條 Linux networking／`skb`／XFRM/ESP 路徑，不是 GhostLock
也不是 Android APK implementation。既有 exact MT8183 defconfig review 沒有公開
DirtyClone route 使用的主要 duplicate/TEE symbols；這足以拒絕目前 documented
PoC 的 live Android test，但不宣稱所有未公開 network bug 都不存在。

## 5. 本輪判定

- **已證實：** redirect APK 只使用公開 Android Accessibility/PendingIntent API，且
  需要研究者在 Settings 明確同意。
- **已證實：** 安裝 APK 不等於啟用 service；目前 `services:{}`。
- **已證實：** 本輪沒有任何 Settings write、package mutation、Fire Launcher mutation、
  reboot 或 root/kernel 操作。
- **高可信推論：** 即使 foreground redirect 成功，也只能是近似替代方案；正式 HOME
  resolver、preferred record 與 Fire Launcher protected state 不會因此改變。
- **待驗證：** 在人工啟用服務及 visible toggle 後，PendingIntent 是否能置 alias 為
  resumed/focused，以及延遲、Fire Launcher 閃現、待機後可靠度。
- **已排除：** 以本 APK 宣稱正式 HOME replacement、跨重開機 HOME 持久化或 root。
- **因風險拒絕測試：** GhostLock/DirtyClone/CMDQ/ION/AEE/BROM/DA/fastboot/boot
  image/partition 操作。

## 6. 下一個最小測量

目前 Settings Accessibility 頁已被開到前景，但 shell 不會替研究者啟用服務。若要
繼續，研究者需在裝置上：

1. 手動啟用 `Phase 4 redirect control` service；
2. 回到 control Activity，打開 `Redirect enabled`；
3. 只執行既有 runner 的 `measure` phase，產生新的唯一 Test ID；
4. 關閉 toggle、在 Settings 停用 service；
5. 再執行 rollback，移除兩個研究 APK並驗證 HOME／ADB。

在第 1、2 步完成前，本專案不應以 shell `settings put` 代替使用者同意，也不應把
「未測量」寫成成功或失敗。

## 重現

```sh
tools/scripts/capture_phase5ak_android_implementation_state.sh \
  --serial G001LT0511550CFT \
  --output adb/phase5/PHASE5AK-ANDROID-IMPLEMENTATION-STATE-20260804-01

python3 tools/scripts/analyze_phase5ab_android_implementation.py --dry-run \
  --source tools/phase4-accessibility/src/org/fireosresearch/phase4/redirect/LauncherRedirectService.java \
  --output output/tables/phase5ak-android-implementation-matrix.csv
```

兩個命令都不會啟用 Accessibility、修改 Settings、安裝 APK、改變 Fire Launcher
狀態或執行 kernel/native payload。
