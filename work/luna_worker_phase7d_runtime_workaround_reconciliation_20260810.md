# Phase 7D：既有實機測試與 workaround 結果整理

本報告只整理既有 `adb/`、`findings/`、`output/tables/` 與 `tools/scripts/` 記錄；沒有重跑測試、連線設備、安裝／移除／停用 package、重啟或改寫既有證據。逐項去重結果見同名 CSV。

## 結論

真正的 User 0 HOME 仍是 `com.amazon.firelauncher/.Launcher`，resolver priority 50，Fire package user 0 為 enabled-by-default。`cmd package set-home-activity` 可以留下 preferred/mAlways 記錄，但不能勝過 Fire 的有效 priority；重啟後仍由 Fire resolve/resume。Settings GUI 沒有可用 Home-app picker，DPM、backup restore、私有 Amazon Binder 與 package/component disable 都沒有形成可用的 User 0 HOME writer。

唯一已實機驗證且可稱 workaround 的路徑是前景 redirect：

- Accessibility 服務可在 Fire HOME 事件後把研究 Activity/ Microsoft 帶到前景；某一 clean-reboot run 證實 service rebind，resolver 與 package state 不變。這是「可見前景」workaround，不是 HOME replacement；ADB/USB 斷線、process death、lock/unlock 後的完整 persistence 沒有閉合。
- ADB foreground monitor 在 30/30 iterations 於 Fire HOME 事件後把研究 Activity 帶到前景；需要持續 host monitor，不能宣稱斷線或重啟後持久。
- Accessibility `onKeyEvent()` consume HOME 變體在 3/3 次仍由 Fire 成為最終前景，故此 build 的 consume route 已排除。

## User 0、child、KFT 與 SystemUI

Stock Settings child flow 曾建立具 Tahoe Profile Owner 的 child user；切換到既有 child 後 Tahoe `FreeTimeLauncherActivity` priority 975 成為該 child 的 HOME，回到 User 0 則 Fire priority 50 恢復。這是 per-user HOME，不是 User 0 replacement。Shell restricted-user create/remove 只建立 stopped/unstarted user，沒有直接觀察到 private KFT provisioning call，且 rollback 成功；不可把它等同 Amazon trusted child provisioning。

SystemUI profile picker／public user switch 只改 active user。User 10/11/12 的 Tahoe 結果、child package state、DPM owner 都屬 child scope；child 內 Microsoft priority 0 也不能壓過 Tahoe 975。沒有證據顯示 SystemUI、ProductPolicy 或 child switch 寫入 User 0 preferred HOME。

## HOME resolver、set-home、preferred 與 package-state

Public `set-home-activity` 成功只代表 preferred record write path 被接受；Fire 的 resolver ranking 仍勝出。Force-stop Microsoft 只造成 temporary package state，最後 Fire preferred、foreground 與 package baseline 均已 guard。Fire package/component disable、User 0 uninstall 均在 protected-package boundary 被拒絕，沒有可利用的 package-state workaround。DPM tx100 的 fake admin 與現有 owner caller 都被拒絕；system-only PMS persistent preferred sink 與 backup `restorePreferredActivities` 只在可信 system lifecycle 中可達。

## Evidence gap / 未測試

下列「成功」不能擴大解讀：Accessibility 成功只證明 foreground redirect；ADB monitor 成功只證明 host-connected temporary redirect；child HOME 成功只證明 child user；set-home 成功只證明 preferred record。Accessibility 的斷線／process death／lock-unlock persistence、genuine Amazon child provisioning 的 private KFT tx3、official backup restore、自然 official OTA 後 OOBE 時序，均未完整測試。

其中任何既有成功若缺完整 before/after/rollback，CSV 以 scope/status 明確標示。特別是 ADB monitor 的外部 persistence 沒有 before/after/rollback closure；OOBE/OTA 與 backup 是未執行的高影響 lifecycle，沒有 rollback 證據，不能列為成功 workaround。沒有任何記錄支持 root，因此本整理不推論 root。

## 已排除

已排除或關閉的實機邊界包括：User 0 普通第三方 HOME 優先權 cap、Fire protected package/component state、Settings GUI default Home picker、DPM caller gate、child 內第三方 HOME 壓過 Tahoe、Accessibility HOME consume、私有 service 對 shell 的可達性，以及把 Activity foreground spoof 誤認為 HOME writer。SystemUI/user switch 也已證實是 active-user route，而非 User 0 HOME mutation。

## 最小安全下一步

目前不需要再做 mutation test。若必須延伸，最小且安全的順序是：

1. 只做 read-only current-user/HOME/package/accessibility foreground guard，確認既有 workaround 的當前狀態。
2. 只在自然、合法的官方 OTA 或 backup lifecycle 之後事後擷取 resolver/package/settings/logcat；不可人工 broadcast、猜 Binder transaction、啟用 OOBE、改 setup state、執行 updater/recovery。
3. 對 private KFT/DPM/backup/OTA 只做 host-side caller/permission/provenance closure；若沒有新授權與完整 rollback，維持未測試／不可操作分類。

CSV：[`luna_worker_phase7d_runtime_workaround_reconciliation_20260810.csv`](./luna_worker_phase7d_runtime_workaround_reconciliation_20260810.csv)
