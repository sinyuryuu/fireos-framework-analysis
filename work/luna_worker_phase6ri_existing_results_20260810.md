# Phase 6RI — 既有 launcher-independent privilege routes evidence ledger

日期：2026-08-10。這是既有測試與結果整理，不是新測試。

## 範圍與安全界線

只讀取保存於 `adb/`、`findings/`、`artifacts/`、`tools/scripts/` 及公開 Phase 6QF/更早報告的資料。未接觸裝置、未重跑測試、未執行 scripts/tools、未送 Binder 或廣播、未執行 root/exploit，也未修改既有 evidence。去重後的 10 rows 見 [CSV](./luna_worker_phase6ri_existing_results_20260810.csv)。

## 結論

目前沒有閉合的 `ordinary app/shell → accepted privilege gate → system/root identity → User-0 Fire HOME/package sink` 路徑。

- package/component gate、DPM/Profile Owner、service visibility、OOBE/OTA、driver metadata、Settings/Home picker、overlay 與 Amazon flags/metadata 均沒有證明普通 caller 可取得 User-0 Fire HOME writer。
- KFT 確認是 child/profile-scoped launcher state writer；切回 User 0 後 Fire 恢復，不能當成 User-0 workaround。
- Accessibility/foreground 是已確認的實用 fallback，但 formal HOME resolver 仍是 Fire priority 50；不可升級成 HOME replacement 或 privilege route。
- AppOps/role 的部分資料屬 availability gap：role-holder query/device_config 不可用不等於空集合，也沒有既有結果證明 HOME writer。
- driver source/metadata 只到 node label/context 與 bounded source negative edge；未開 node、未 ioctl、未證明 native client 或 Framework sink。

## 最小安全下一步

只做一項 host-only、read-only static correlation：把保存的 Settings/overlay/permission-holder/PackageManager writer corpus 對齊到 `Fire Launcher + User 0 + HOME` 三元 target，優先檢查尚未分類的 writer/callback caller provenance。若仍沒有同時成立的 caller gate、User-0 propagation 與 HOME sink，即關閉該候選。

若未來自然取得合法官方 OTA 或既有 profile lifecycle 後的 evidence，只能讀取 post-state；不得為此重播 OTA/OOBE、建立或切換 user、provision/remove owner、改 role/AppOps/settings、啟用 Accessibility、切 overlay、開 driver node、呼叫 Binder，或執行任何 root/exploit。

## 欄位說明

`classification` 用於區分已排除、已確認但非目標、以及證據缺口；`evidence_hash` 保留 raw evidence hash 或本 ledger 引用的既有報告 SHA-256。`repeat_status` 全部標示為既有 evidence，表示本輪沒有重跑。

## 交付

- `work/luna_worker_phase6ri_existing_results_20260810.md`
- `work/luna_worker_phase6ri_existing_results_20260810.csv`
