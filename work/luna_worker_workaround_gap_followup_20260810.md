# Host-only workaround gap follow-up — 2026-08-10

本次只讀既有 `adb/phase*`、`findings/`、README/PROJECT_STATUS 與既有 work/audit 輸出；沒有連接裝置、沒有執行 ADB、root、Binder、package/settings mutation、component-disable/priority/set-home 矩陣、reboot、OTA 或 OOBE replay。

## 結論

既有證據沒有證明 User 0 的第三方真正 HOME replacement：User 0 resolver 持續選 `com.amazon.firelauncher/.Launcher`、priority 50。真正 HOME 與 workaround 已分開：

- **真正 HOME**：Fire 是 User 0 winner；Tahoe priority 975 只在 child user（歷史記錄含 User 10/11/12，應以當次 capture 的 live user ID 為準）。
- **per-user HOME**：child Tahoe 是有效的 child-user HOME，不是 User-0 replacement；`set-home-activity`/preferred record 不能越過 child ranking 或 Fire winner。
- **foreground redirect**：Accessibility/ADB monitor 可把 Fire 事件後的可見 activity 導向 Microsoft；Lock Task 可保留 foreground。兩者都不改 resolver、Fire package state 或形成 persistent HOME。
- **static-only**：Settings Default Home、SystemUI observation、Amazon helper/prewarm、package-state writer closure 只證明 code/sink/permission 邊界，不能升格為 runtime HOME。
- **risk-rejected**：KFT/private Binder、DPM owner path、Settings Reset App Preferences、OTA/OOBE/BOOT_AFTER_SYSTEM_OTA 均已被 authority、rollback 或 lifecycle 風險限制；不得重播。

## 未重複且仍有最小安全價值的 gap

1. 對 exact-build PS7331 Settings resources/overlay 與既有 DefaultHome controller 做 host-only diff，確認 UI surface 是否存在 build-specific gate；不點擊、不 dispatch tx66。
2. 將 6CY/6HB 的 resolver、resumed activity、event trigger、post-boot sampling 以保存檔案的 timestamp 對齊，解開 3/3 與 0/3 的定義差異；不重做 reboot/Accessibility。
3. 統一 child User 10/11/12 的歷史別名與 `RUNNING_UNLOCKED` readiness gate，再比較 Tahoe/FallbackHome/Fire；不 switch-user、不 PIN、不刪 profile。
4. 對 OTA 與 DevicePolicy 靜態 call graph 補齊「第一個 persistence consumer」與 user-scope 欄位；不送 broadcast、不呼叫 Binder、不執行 updater/OTA。

完整矩陣見 [CSV](./luna_worker_workaround_gap_followup_20260810.csv)，欄位正是 `route,required_authority,changes_user0_home,fire_state_effect,persistence,rollback,runtime_evidence,status,next_safe_step`。CSV 共 22 rows（不含 header）；其中 4 rows 為 `gap-minimal-safe`，5 rows 為 `risk-rejected`。

## Hash

由 host 端對新輸出計算 SHA-256；hash 不代表裝置新證據，只代表本次整理檔案內容完整性。
