# Host-only Accessibility / UsageStats / foreground redirect review

日期：2026-08-10  
範圍：既有 `tools/phase4-accessibility`、redirect 變體、既有 ADB evidence、log、findings 與 tables。此次沒有連接真機、沒有執行 ADB、沒有安裝 APK、沒有設定 Accessibility、沒有攔截輸入或讀取畫面。

## 結論

既有 evidence 沒有證明 User 0 的第三方「真正 HOME」。正式 `MAIN + HOME` resolver 在 User 0 仍選 `com.amazon.firelauncher/.Launcher`，priority 50；Accessibility 的效果是 resolver 已選 Fire 之後，另行把某個明確 Activity 推到可見 foreground。這兩者不可合併。

最初 Phase 4 harness 的 0/30 失敗，主因是 ActivityManager 在 Fire HOME transition 中把 direct activity start 記為 stopped，目標只留在 task history/last-paused；並非 HOME resolver 被改寫。後續 Microsoft-targeted retry 變體透過 350/1000/1800 ms 的明確 `PendingIntent` retry，在部分時序下成功，但仍是延遲且 event/timing-dependent 的 foreground redirect。

Accessibility 的「不穩定」有三個獨立邊界：

1. GUI consent 本身可能失敗：Phase 6CV 在確認對話框後仍是 `services:{}`、secure enabled service 為空，因此 runner 正確拒絕測量。
2. 即使 service 已經綁定，Fire 先贏得 HOME；callback、background-start gate、task transition 與 retry timing 決定目標是否在觀測窗口內 resumed。既有結果包含原始 0/30、retry 3/3、reboot/unlock 後 2/3 或 3/3，以及 timeout=50 ms 的 4/5，不能宣稱 deterministic。
3. reboot 後設定可 persistence/rebind，不等於 HOME persistence；冷啟動仍可能先顯示 Fire，且正式 resolver 不變。

## 明確分類

| 類別 | 判定 | 證據摘要 |
|---|---|---|
| 真正 HOME | **Fire，非第三方 replacement** | `findings/phase-6cy-*`、`output/tables/phase6cy-*-*.csv`：User 0 resolver 前後均 `com.amazon.firelauncher/.Launcher`, priority 50 |
| foreground redirect | **可行但不穩定/非 HOME** | Microsoft retry 變體在 `findings/phase-6cy-ms-targeted-accessibility-retry.md` 為 explicit 1/1、HOME 3/3；reboot/unlock 另有 2/3、3/3 與 clean/timing negative；Fire package/HOME state 未變 |
| unlock workaround | **不是解鎖繞過；只能稱 unlock 後 redirect** | 6HB/6CY 的 owner-authorized physical unlock 後才量測 foreground；沒有自動輸入 PIN、沒有 bypass keyguard 的證據。未解鎖或無 ADB 的物理 HOME 穩定性為 UNKNOWN |
| UNKNOWN | **不得當成功 workaround** | 無 service 的 GUI consent run、UsageStats third-party redirect、斷開 ADB 後純 Accessibility physical HOME 的 deterministic 結果、任何正式 HOME writer |

## 失敗原因與可改善範圍

### Accessibility / redirect service

目前 source（`tools/phase4-accessibility/src/.../LauncherRedirectService.java`）本身的透明邊界是合理的：只匹配 `com.amazon.firelauncher` 的 `TYPE_WINDOW_STATE_CHANGED`，`canRetrieveWindowContent=false`，不讀文字/視圖/密碼/通知；HOME 只在使用者已開啟 visible toggle 時處理；有 cooldown/loop guard；target component hard-coded；失敗時回傳 false，讓正常 HOME path 保留。README 也明確要求手動 consent、visible stop 與 rollback。

可改善的只是體驗與可觀測性，不是把它升格成 HOME：

- 保留原始 `notificationTimeout=250 ms` retry variant；A/B 已顯示 50 ms 雖降低部分 explicit latency，HOME 可靠性變差（4/5），不採用。
- UI 應明確顯示「Fire 先成為 HOME、稍後嘗試切換前景」、最近一次 dispatch/target observed/timeout 狀態，以及一鍵停止；停止應取消後續 retry，不保存或猜測使用者的 Accessibility 設定。
- 僅允許白名單 target、不要接受外部 intent/package；不加 window-content、overlay、input injection、screen reading 或隱藏自啟動。
- 若 service 未出現在 `dumpsys accessibility`，只顯示未啟用/待使用者處理，不重試寫 secure setting；rollback 只復原保存值並驗證 Fire resolver/foreground。

這樣的體驗是「可見、可停止、可回復的 foreground assist」，不是隱蔽攔截，也不會解決正式 HOME 選擇。

### UsageStats

既有 host evidence 只證明 Fire OS 有 system/privileged UsageStats 元件與 `usagestats` service；`PACKAGE_USAGE_STATS` 是 app-op/受限權限，Amazon 的 `com.amazon.AmazonUsageStats.permission.REPORT_EVENT` 是 signature permission。沒有證據證明普通第三方可用 UsageStats 取得足夠即時、可靠的 foreground signal，亦沒有證據它能寫 HOME 或繞過 ActivityManager 的 start gate。故 UsageStats route 應標為 **UNKNOWN/不可作為已驗證替代方案**，不應藉由新增權限、私有 Binder 或 privileged install 來「修好」。

### Host ADB monitor

既有 6IQ/6CU monitor 是 5/5 可重現的 host-side foreground relay，但 ADB/monitor 停止後即失效；使用者已明確結案、不再使用。它可作歷史對照，不能冒充 resident HOME 或解鎖 workaround。

## 建議決策

若目標是透明替代體驗，唯一有既有實測支持且符合停止/回復原則的方向，是「使用者明確啟用 + visible toggle + 只對明確 target 做延遲 foreground assist + 清楚顯示 Fire 先贏 HOME + 可隨時關閉」。它可改善回到熟悉 launcher 的感受，但必須接受：可能延遲、可能漏 redirect、reboot/first-unlock 需等待、Fire 仍是正式 HOME。

不建議把 UsageStats、Accessibility 的 key interception、unlock automation、Lock Task、preferred record 或任何 private Amazon service 當成真正 HOME workaround；本 review 沒有發現可在不增加權限/風險下把它們變成 deterministic User-0 HOME。

## 主要 evidence

- `tools/phase4-accessibility/README.md`、`src/.../LauncherRedirectService.java`、`res/xml/accessibility_service_config.xml`
- `findings/phase-4b-assisted-workarounds.md`：原始 0/30、stopped/last-paused boundary
- `findings/phase-6cx-adb-accessibility-foreground-redirect.md`：explicit foreground 與 HOME boundary
- `findings/phase-6cv-accessibility-pendingintent-gui-boundary.md`：GUI consent 失敗，未測量
- `findings/phase-6cy-ms-targeted-accessibility-retry.md`：retry foreground result
- `findings/phase-6cy-accessibility-reboot-unlock-result.md`、`findings/phase-6hb-ms-accessibility-reboot-persistence.md`：reboot/rebind/unlock 與 resolver 分離
- `findings/phase-6cy-accessibility-timeout-ab-boundary.md`：50 ms A/B negative optimization
- `findings/phase-6iq-adb-foreground-fallback.md`：5/5 ADB relay，已結案不使用
- `output/tables/phase6cv-accessibility-pendingintent-gui-boundary.csv`、`phase6cy-ms-targeted-accessibility-retry.csv`、`phase6cy-reboot-unlock-result.csv`、`phase6cy-accessibility-reboot-persistence.csv`
- `adb/phase4/PHASE4-ACCESSIBILITY-T01/measure/summary.tsv`、`adb/phase6cy/PHASE6CY-LATENCY-AB-20260807-02/`、`adb/phase6cy/PHASE6CY-MS-ACCESSIBILITY-20260806-08/`、`adb/phase6cy/PHASE6CY-MS-ACCESSIBILITY-20260807-02/`
- UsageStats read-only inventory：`adb/phase6ac/PHASE6AC-RO-20260805-01/pm_dump.stdout.txt`、`adb/phase6ao/PHASE6AO-RO-20260805-01/package_dump_full.stdout.txt`

