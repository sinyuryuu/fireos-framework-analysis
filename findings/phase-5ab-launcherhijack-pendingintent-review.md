# Phase 5AB：Android 實作邊界與 PendingIntent redirect variant

## 範圍與安全界線

本輪補充「Android 的實作」分析，但不把 Android APK、native wrapper 或公開 root
PoC 混稱為同一種能力。分析分成兩條邊界：

1. Android HOME 的正式 resolver 路徑；
2. 具有明確使用者同意的 Accessibility foreground redirect 路徑。

本輪沒有執行 root payload、CVE trigger、futex race、AEE/ION/CMDQ ioctl、BROM/DA
handshake、fastboot、bootloader、分割區寫入、重開機或裝置狀態修改。沒有下載或安裝
來源不明 APK。現有 PHASE4-ACCESSIBILITY-T03 的原始結果保持不變。

## Exact device boundary

既有 exact-device evidence（P5M-BASE-001、P5E-CMDQ-007）仍是本輪的裝置基線：

| 欄位 | 值 |
|---|---|
| Device | Amazon Fire HD 10 11th Gen / KFTRWI |
| Product / SoC | trona / MediaTek MT8183 |
| Android | 9 / API 28 |
| Build | PS7330.4104N/0030099376128 |
| Kernel | Linux 4.4.146+ |
| Security patch | 2024-02-01 |
| HOME | com.amazon.firelauncher/.Launcher, effective priority 50 |
| Previous direct Accessibility route | 0/30 foreground handoffs |
| Exact pinned mtk-su route | exit 1, Failed critical init step 3, no UID 0 |

**已證實：** Android 端的公開實作必須按層分類。普通 APK 可使用公開
AccessibilityService、PendingIntent 與 Intent API；這不等於取得 PackageManager、
ActivityTaskManager 或 system UID 權限，也不會改變 HOME resolver。

## 公開 LauncherHijack 的 Android 實作

審查固定 commit
[f79aee3ddd10c053d6d7c55d6f2fc29436001537](https://github.com/BaronKiko/LauncherHijack/tree/f79aee3ddd10c053d6d7c55d6f2fc29436001537)，不使用 repository 的漂移 branch。

### 1. 目標 Intent 的建立

HomePress.GetDesiredIntent() 在固定 source 的第 20–33 行：

- 從 app 自己的 SharedPreferences 讀取目標 package/class；
- 建立 ACTION_MAIN；
- 加入 CATEGORY_LAUNCHER，不是 CATEGORY_HOME；
- 指定 explicit ComponentName；
- 使用 NEW_TASK | EXCLUDE_FROM_RECENTS | CLEAR_TOP | REORDER_TO_FRONT。

因此它不是請 PackageManager 重新選 HOME，也不是建立新的 preferred activity；它是
明確啟動已選目標 Activity。

來源：[固定版 HomePress.java](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/app/src/main/java/com/baronkiko/launcherhijack/HomePress.java)。

### 2. PendingIntent 跨背景啟動邊界

同一檔案第 36–50 行先做 200 ms debounce，再呼叫：

~~~java
PendingIntent pendingIntent = PendingIntent.getActivity(c, 0, i, 0);
pendingIntent.send();
~~~

這是本輪最重要的 Android implementation 差異。它仍然是普通 app 的公開 API，並
不會讓 app 成為 HOME；但在某些 Android 版本／OEM 的背景啟動限制下，系統派送
PendingIntent 的語意可能不同於 AccessibilityService 直接呼叫 startActivity()。

**高可信推論：** 這個差異足以構成一個新的、低風險的 source experiment；不能由
公開 source 直接推論它在 Fire OS PS7330 上一定成功。

### 3. 事件來源

AccServ.java 固定 source 第 23–33 行只在 Accessibility event 的 package 是
com.amazon.firelauncher 時呼叫 HomePress.Perform()。第 41–67 行另有可選的
onKeyEvent()／KEYCODE_HOME 路徑；第 80–102 行註冊 HomeWatcher，其 onHomePressed()
也會呼叫相同方法。

HomeWatcher.java 第 23–63 行監聽 ACTION_CLOSE_SYSTEM_DIALOGS，以 reason=homekey／
recentapps 區分事件。這是 event observation，不是改寫 system_server 的 Home resolver。

來源：[固定版 AccServ.java](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/app/src/main/java/com/baronkiko/launcherhijack/AccServ.java)、[固定版 HomeWatcher.java](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/app/src/main/java/com/baronkiko/launcherhijack/HomeWatcher.java)。

### 4. Manifest 能力與本專案的差異

公開 Manifest 第 6–9 行宣告 BIND_ACCESSIBILITY_SERVICE、RECEIVE_BOOT_COMPLETED、
SYSTEM_ALERT_WINDOW 與 INSTALL_PACKAGES；後兩者並不表示普通 sideloaded APK 自動
取得相應特權。公開專案另有 overlay service 與 boot/package receiver。該 repository
自己標示 deprecated，且其文件警告更新／被 kill 後可能需要重新處理。

本專案的 tools/phase4-accessibility 刻意不宣告 overlay、device-admin、network 或
私有 Binder。它只使用人工開啟的 Accessibility service、可見 toggle、事件 package
filter、cooldown 與 loop guard，避免把 legacy overlay 或安裝權限宣告帶入研究測試。

來源：[固定版 AndroidManifest.xml](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/app/src/main/AndroidManifest.xml)、[官方 repository 說明](https://github.com/BaronKiko/LauncherHijack/tree/f79aee3ddd10c053d6d7c55d6f2fc29436001537)。

## 本專案 Android source variant

已將 tools/phase4-accessibility/src/.../LauncherRedirectService.java 改為一個透明的
PendingIntent variant：

~~~text
TYPE_WINDOW_STATE_CHANGED
  └─ package == com.amazon.firelauncher
      └─ visible toggle == enabled
          └─ cooldown / loop guard
              └─ explicit ACTION_MAIN + CATEGORY_LAUNCHER
                  └─ PendingIntent.getActivity(...).send()
~~~

它仍然：

- 不呼叫 CATEGORY_HOME resolver；
- 不寫 preferred activity、settings、AppOps 或 overlay；
- 不停用、hide、suspend、force-stop 或清除 Fire Launcher；
- 不讀取視窗文字、輸入、view tree、密碼或通知；
- 只指向本專案的 org.fireosresearch.phase4.alias/.HomeActivity；
- 需要研究者在 Settings 明確授權 Accessibility，且由 app 內 toggle 開啟。

歷史 APK 與 T03 結果沒有被覆寫。新 source 尚未安裝、尚未啟用、尚未在裝置上
測量，因此結果標記為 **待驗證**，不能稱為可用 workaround。

## 與歷史 0/30 路徑的區別

PHASE4-ACCESSIBILITY-T03 使用舊版直接 startActivity(intent)。原始 logcat 記錄了
redirect attempt，但 30 次中沒有一次把 alias 置為 resumed/focused；Fire Launcher
仍是 resumed。這證明「舊版直接啟動」在當時條件下不可用，不證明所有公開 Android
啟動邊界都失敗。

本輪的新 variant 使用 PendingIntent.getActivity().send()，是不同的 Android API
路徑；但目前只有 source/build-level evidence：

| 路徑 | 裝置結果 | 判定 |
|---|---:|---|
| Direct startActivity()（T03） | 0/30 | **已排除：此實作在此條件不可用** |
| PendingIntent.getActivity().send() source variant | 尚未執行 | **待驗證** |
| 正式 HOME resolver | Fire Launcher | **已證實：不受此 variant 改變** |

## Root/CVE Android implementation 的邊界

mtk-easy-su 的 Android source 是 UI／wrapper：解出 bundled executable、設定權限、
執行 shell/Magisk 流程，再用 /sbin/su 作粗略結果判定；固定 commit 的 mtk-su32/64
是 Git-LFS payload pointer，不是可針對 MT8183/PS7330 重新編譯的公開 exploit source。
exact pinned payload 已有失敗證據，不能用新的 APK wrapper 補足 kernel target 不匹配。

公開 CVE-2026-43499 Android ports 也各自綁定其他裝置／kernel profile：

- popsicle：Xiaomi 17 / Snapdragon / Android 16 / 6.12.23；
- aristotle：MediaTek XIG04 / Android 12 / 5.10.136；
- Android detector：未提供 trona/MT8183/PS7330 target，且文件警告可能 crash/reboot。

**已證實：** 這些公開 Android implementations 可作 source-level 方法參考，不能
直接當成 KFTRWI 的 payload，也不應安裝或執行以猜測相容性。

**因風險拒絕測試：** native trigger、kernel race、AEE/ION/CMDQ ioctl、未知 Binder、
BROM/DA、preloader/LK、fastboot unlock、boot image／分割區寫入。

## 建置與重現

離線分析器只讀本地 source，不連接裝置：

~~~sh
python3 tools/scripts/analyze_phase5ab_android_implementation.py \
  --source tools/phase4-accessibility/src/org/fireosresearch/phase4/redirect/LauncherRedirectService.java \
  --output output/tables/phase5ab-android-implementation-matrix.csv
~~~

安全 dry-run：

~~~sh
python3 tools/scripts/analyze_phase5ab_android_implementation.py \
  --source tools/phase4-accessibility/src/org/fireosresearch/phase4/redirect/LauncherRedirectService.java \
  --output /tmp/phase5ab-matrix.csv --dry-run

tools/phase4-accessibility/build_redirect.sh \
  --output /tmp/phase5ab-build --dry-run
~~~

編譯只應使用已驗證的本地 SDK 與研究者自己的 signing key；本輪沒有產生或安裝
新的 APK，也沒有自動處理 Accessibility consent。

## 結論標籤

- **已證實：** LauncherHijack 的 Android implementation 是事件觀察 + explicit
  launcher Activity + PendingIntent，不是 HOME resolver replacement。
- **已證實：** 本機舊版 direct-start route 在 T03 為 0/30。
- **高可信推論：** PendingIntent variant 是值得一次受控測量的低風險新路徑，因為
  它改變背景啟動邊界但不觸及 Fire package state。
- **待驗證：** PendingIntent variant 在 PS7330 上是否真的把目標置為 resumed/focused，
  以及是否會先短暫顯示 Fire Launcher。
- **已排除：** 這個 variant 能改變正式 HOME resolver、移除 Fire Launcher 保護或
  跨重開機成為真正 HOME 的說法。
- **因風險拒絕測試：** 任何 root／kernel／boot-chain implementation 的裝置執行。

## 下一個最小安全測量

若要測量新 variant，應建立新的唯一 run ID，不重用 T03：先保存 resolver、目前
Accessibility state、前景 task、package path 與 ADB 狀態；安裝自建 APK 後由研究者
手動授權 Accessibility，再手動開啟可見 toggle；只測量有限次數的 Home/unlock
事件；完成後關閉 toggle、在 Settings 關閉 service、移除研究 APK，並確認 Fire
resolver 與 package state 未變。任何「真正 HOME replacement」的結論仍須拒絕，除非
PackageManager resolver 本身被觀察到改變。
