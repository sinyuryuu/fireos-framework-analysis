# Phase 6X-reconcile：既有測試與結果去重矩陣

日期：2026-08-10（Asia/Taipei）

本輪只讀搜尋 `adb/`、`findings/`、`output/tables/`、`work/` 及其既有索引；沒有接觸裝置、沒有執行 adb 或任何測試、沒有重播 Binder/driver/OTA/root 路線，也沒有修改既有證據。逐列矩陣見 [CSV](./luna_worker_phase6x_reconcile_20260810.csv)。

## 去重結論

保存證據沒有閉合 `ordinary app/shell → accepted privileged identity → User-0 HOME/package/root/partition sink`。Fire Launcher 仍是保存的 User-0 HOME 結果；KFT 是實際存在但限 child/profile target user 的 writer。Accessibility/ADB 只達到有條件的 foreground fallback，不是正式 HOME writer。

已合併的重複族包括 HOME resolver/foreground/force-stop guards、preferred/set-home、Fire package/component guards、child/KFT/Tahoe lifecycle、service list/check/find、Accessibility iterations 與 rollback/final guards。不同檔名或相同 build/user/package topology 的 before/after 不視為新測試結果。

## 各路線目前證據

CSV 覆蓋 launcher/HOME、package state、KFT/child user、DPM、Settings/Overlay、private Binder、OTA/OOBE/updater、driver/ION、GhostLock/root、Accessibility/foreground、PendingIntent/cross-user 及 Amazon prewarm。`completed` 表示既有 bounded result；`static_gap` 表示只到靜態/host-side 或 caller-gate-sink 未閉合；`closed_no_retest` 表示重測不值得或明確越過安全邊界；`negative_bounded` 僅限保存測試 scope。

## 最小新證據缺口

1. User-0 Fire restoration writer 的 production caller、identity、user scope 與實際 sink。
2. KFT tx3 的合法 caller/provenance，以及 child writer 以外是否存在 User-0 side effect。
3. H2 permission holder/grant/requester、Binder caller identity 與 downstream user/profile sink。
4. ION/native 的實際 process/domain load、`/dev/ion` gate、caller 與 sensitive effect。
5. OOBE/`BOOT_AFTER_SYSTEM_OTA` exact numeric user、native updater/fosinit handoff、caller-to-partition chain。
6. 完整 production caller universe、Vending/privapp grant provenance，以及 GhostLock/root 路線的適用性與 sink；現有 corpus 不支持以 exploit 或裝置重播補洞。

所有建議 probe 都是 host-only：path/schema/hash/reference 檢查、既有 snapshot 比較、source/permission/caller/user/sink join、ELF/SELinux/OTA provenance review。不得重送 setter、切換或建立 child、provision/remove owner、改 Settings/Accessibility、呼叫未知 Binder、開 driver node/ioctl、送 OTA/OOBE、reboot、root 或 partition payload。
