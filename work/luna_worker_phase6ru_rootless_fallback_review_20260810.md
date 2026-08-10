# Phase 6RU：rootless launcher fallback review（host-only）

日期：2026-08-10。範圍限於本專案已保存的證據、已保存的本地 source，以及已固定版本的公開原始碼。沒有下載或執行未知 APK／二進位，沒有裝置測試、Accessibility 啟用、settings/package 寫入、Binder／OTA／root 操作。

## 結論

目前沒有可證實的第三方 formal HOME replacement。Fire OS 7 的 User 0 HOME resolver 仍選 `com.amazon.firelauncher/.Launcher`（priority 50）。可行的 rootless 近似只有兩類：

- 裝置端、需使用者明確授權的 Accessibility foreground redirect；Phase 6HB/6CY 保存結果為重開機後 service 可 rebind，明確 Fire start 1/1、HOME 3/3 轉到 Microsoft，但先由 resolver 選出 Fire，延遲 callback 再把 Microsoft 帶到前景。
- 需要持續 ADB 與 host monitor 的 foreground relay；Phase 6IQ 保存結果為 5/5，monitor 停止或下一次 HOME 後即回 Fire。此路徑已由使用者結案，不列為 Phase 6RU 操作候選。

兩者都是 foreground redirect，不是 formal HOME：它們不呼叫或改寫 HOME resolver、preferred HOME、Fire package state，也不阻止 Fire 在後續 HOME／重啟／monitor 停止後恢復。

## HOME resolver 與 foreground redirect 的正式區分

| 面向 | formal HOME | foreground redirect |
|---|---|---|
| 作用點 | `MAIN + CATEGORY_HOME` resolver／preferred candidate | resolver 已選出 Fire 後，再啟動指定 Activity |
| 本案結果 | Fire priority 50；Settings 沒有可用 Home picker | Microsoft 可在有限條件下成為最後 visible/resumed Activity |
| 所需授權 | 合法 HOME candidate 與可用的 Framework/Settings writer；普通 preferred record 不足 | Accessibility 使用者 consent，或活躍 ADB host shell；PendingIntent 只提供受控啟動，不提供 HOME writer |
| 持久性 | 應跨 HOME，通常需跨 reboot；本案未達成 | 依 service／monitor／task timing；不是 HOME preference |
| rollback | 恢復 preferred/package state 並驗證 resolver | 停止 sender/monitor、回 HOME；Accessibility 路徑另恢復 secure setting 並移除自建 APK |

## 路線摘要

完整逐列資料在 [CSV](luna_worker_phase6ru_rootless_fallback_review_20260810.csv)。

### Accessibility

歷史 direct-start 版本在保存的 Phase 4B/T03 實測為 0/30 foreground handoff，故不能當成可靠 fallback。較新的本地 source 以 window/key event 觀察 Fire，透過 `Handler` 在 350、1000、1800 ms 重試，並用明確 `PendingIntent.getActivity(...).send()` 啟動 Microsoft；Phase 6HB 顯示 service state 可在 reboot 後 rebind，但這只代表 Accessibility service 的設定持久，不代表 HOME 持久。

它的授權邊界是 `BIND_ACCESSIBILITY_SERVICE` 宣告加上使用者在 Settings 的啟用；這是高權限、明確同意的觀察能力，不是隱式 HOME 權限。本階段不啟用 Accessibility，也不新增測量。

### UsageStats

UsageStats observer 只能讀取／判斷 foreground，再嘗試顯式啟動 launcher；本專案保存的 Phase 4B 將它標為較弱、未測量候選，受 Usage Access/AppOps、polling 延遲與 background activity-start 限制。它沒有 formal HOME sink，不能因為能看到 resumed package 就宣稱能替換 HOME。

### PendingIntent

公開 LauncherHijack 固定 source 與本地 source 都顯示同一邊界：建立 explicit launcher Intent，透過 `PendingIntent.getActivity(...).send()` 觸發 Activity。這改變的是背景啟動／事件後的 foreground handoff，不是 PackageManager 的 HOME selection。自建 PendingIntent 的 creator／UID 也不會自動取得 Fire 的 system／protected writer 能力。

### Foreground monitor

ADB host monitor 觀察 `dumpsys activity` 的 resumed/focused Fire，再用公開 `am start -n` 把 Microsoft 帶回前景。保存的 Phase 6IQ 結果為 5/5，但 resolver before/after 仍是 Fire；monitor 停止、ADB 中斷或重啟後，redirect 不持久。因 Phase 6IQ 已明確結案，本階段只整理，不重跑。

### Settings／Home picker

`android.settings.HOME_SETTINGS` 在本機 Fire Settings 只顯示 assistant、browser、link-handling 等 Default apps 控制，沒有 Home/launcher selector。反編譯的 `DefaultHomePicker` 雖含 `replacePreferredActivity()`，但 `default_home` row 已從主要 XML 移除，外部 Settings 路徑也不能到達該 picker；因此沒有正常 GUI HOME writer。

### Fire Toolbox／LauncherHijack 歷史方法

LauncherHijack 固定 commit 的公開 source 是 Accessibility／system-dialog observation，加上 explicit launcher Activity 與 PendingIntent；它不是 formal HOME resolver replacement。其 HELP 也記載過「corrupt default launcher」類方法，可能破壞可操作性、依 user account 有效，或需要新 user／恢復流程。Fire Toolbox 類歷史路徑同樣版本依賴，常涉及 disable／hide／corrupt default package state；本案將其列為風險拒絕，不下載或執行二進位。

## 已排除／不採用原因

- ordinary `set-home-activity`：可留下 preferred record，但保存證據中有效 resolver、Home key 與前景仍為 Fire priority 50。
- Fire Launcher disable／component mutation：protected-package gate 拒絕；不是可安全重試的 rootless fallback。
- Settings Home picker：本 build 沒有公開 Home selector，App Info 的 Home row 也只返回同一 Default apps 頁面。
- UsageStats：只有未測量的 observation/redirect 候選，沒有可靠性、延遲或持久性證據。
- 舊 Accessibility direct-start：0/30；不能與後來需 consent、delayed retry 的 resident fallback 混為一談。
- LauncherHijack／Fire Toolbox default-launcher corruption：會改變或破壞裝置狀態，rollback 不具普通 reversible API 的保證；且歷史版本／blocked-app 假設不等於目前 Fire OS build。
- private Amazon Binder、OTA/OOBE、root、kernel/driver、未知 APK／binary：超出本 task scope，並明確排除。

## Rollback 與下一安全步驟

本 review 沒有產生裝置變更，故沒有 runtime rollback。對已保存方法的通用 rollback 是：停止 host monitor／foreground sender、回到 stock HOME；若未來有明確授權的 Accessibility run，先保存並於結束時恢復 `enabled_accessibility_services`／相關 toggle，移除同一個已知自建 APK，再驗證 resolver、Fire package state 與 foreground。不要把 `settings put`、package disable 或 default-launcher corruption 當作清理手段。

Phase 6RU 的下一安全步驟是保留此 host-only matrix，不啟用 Accessibility、不做 UsageStats/redirect device measurement、不改 settings/package；只有在出現新的可信 Framework/Amazon HOME writer source 時，才做額外的靜態 source review。

## 來源

- 本地：`findings/phase-6hb-ms-accessibility-reboot-persistence.md`、`findings/phase-6cy-ms-targeted-accessibility-retry.md`、`findings/phase-6iq-adb-foreground-fallback.md`、`findings/phase-6bw-adb-foreground-monitor-closure.md`、`findings/phase-6fo-gui-default-apps-home-boundary.md`、`findings/phase-6k-launcher-fallback-assessment.md`。
- 本地 source：`tools/phase4-accessibility/src/org/fireosresearch/phase4/redirect/LauncherRedirectService.java`。
- 公開固定 source：[LauncherHijack fixed repository](https://github.com/BaronKiko/LauncherHijack/tree/f79aee3ddd10c053d6d7c55d6f2fc29436001537)、[HomePress.java](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/app/src/main/java/com/baronkiko/launcherhijack/HomePress.java)、[AccServ.java](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/app/src/main/java/com/baronkiko/launcherhijack/AccServ.java)。
- Android API：[AccessibilityService](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService.html)、[PendingIntent](https://developer.android.com/reference/android/app/PendingIntent.html)。
