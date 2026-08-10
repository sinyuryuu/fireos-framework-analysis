# Phase 6AH legacy route reconciliation（host-only）

日期：2026-08-10（Asia/Taipei）

本表以 `output/tables/phase6x2-control-surface.csv` 的 126 rows（表頭除外）作為去重基準；新 companion [CSV](./luna_worker_phase6ah_legacy_route_reconciliation_20260810.csv) 只把既有 evidence 歸併成 route family，不宣稱新增測試結果。涵蓋 User 0、User 10/11 child/KFT、DPM/Profile Owner、HOME/preferred/priority、package-state、SystemUI/navigation、Accessibility、UsageStats/foreground、ADB monitor、OOBE/OTA、app/IPC、kernel/root。

## 總結判定

- 正式 User-0 `MAIN + HOME` 仍是 `com.amazon.firelauncher/.Launcher`（priority 50）。preferred/set-home、priority、package/component、force-stop 沒有形成可持續第三方 HOME；已測變更要麼被 gate 拒絕，要麼被 Fire/final guard 保留或回復。
- User 10/11 child/KFT 的 Tahoe launcher/package state 是真實但 per-user 的效果；切回 User 0 後 Fire 恢復。DPM/Profile Owner 是 owner/admin/UID gated，沒有普通 caller 的持續 User-0 writer 證據。
- Accessibility、foreground redirect、ADB monitor 只能作透明、使用者同意且可停止的 foreground assist。Accessibility 既有結果包含 direct 0/30、retry 的明確成功與 reboot/unlock 混合結果；這些不是 HOME，也不是解鎖 bypass。UsageStats 沒有成功率或 writer 證據。
- OOBE/OTA、private IPC、ProductPolicy/fosinit、ASP prewarm、driver/native、kernel/root 只保留靜態 capability、guard 或 evidence gap。沒有把 capability 升格為 caller reachability、真正權限變化或 bypass。

## 欄位語意

`evidence_success_rate` 僅填既有資料明確報出的比例；`not measured`/`unknown` 不代表失敗。`true_permission_change` 專指目標權限、身份或受保護狀態是否真的被提升/改變，不把前景顯示、child-scoped package state 或靜態 writer 當成權限變化。`disposition` 使用：已整合、已排除、待驗證、因風險拒絕。

## 去重與替代方案

已整合的替代方案只有「使用者明確啟用的 Accessibility foreground assist」及歷史上 5/5 的 ADB-connected foreground relay；後者已結案，不能當 resident HOME。可保留的 host-only 下一步是比對既有 source/manifest/permission/user/SELinux/DT/relocation 與 hash，或等待自然、正式且已授權的 lifecycle evidence。不能重播 setter、preferred、component、DPM、Binder transaction、broadcast、OTA/recovery、driver ioctl、root 或任何 package/settings mutation。

## 操作界線與驗證

本輪只搜尋既有 `adb/`、`findings/`、`output/`、`tools/`、`work/` 並新增本文件與 CSV；沒有重新執行測試、沒有連接或操作真機、沒有安裝 APK、沒有啟用 Accessibility、沒有改 settings/package。未改動其他檔案。
