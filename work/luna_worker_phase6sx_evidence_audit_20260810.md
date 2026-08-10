# Phase 6SX：既有 runtime／experiment／evidence completeness audit

日期：2026-08-10（Asia/Taipei）  
角色：主機端 evidence worker；本輪只讀工作目錄既有內容。

## 範圍與安全邊界

盤點對象為目前 repo 內的 `adb/` snapshots、mutation／HOME／component tests、
Phase 3A–6SQ findings/reports、`sha256sums.txt`／command manifests、
`tools/scripts/`、`README.md` 與 `PROJECT_STATUS.md`。本輪沒有連裝置、沒有執行
adb、沒有發送 Binder/driver payload、沒有改變任何 device state，也沒有覆寫其他
worker 檔案。逐列 catalog 在同名 CSV。

本 audit 的「已做」只表示 repo 有足夠 raw output／manifest／report 支持曾經發生；
「已確認」仍只限 raw evidence 直接支持的 scope。靜態 source、service 名稱、
permission 宣告、driver node metadata 或 updater writer 不等於 live caller、root、
Binder reachability 或 OTA execution。

## 結論摘要

- **Device state：已做且有保存**。目前權威狀態是 PS7331.4463N／KFTRWI／trona、
  Android 9、kernel 4.4.146+；read-only snapshots 顯示 ADB `device`、User 0、
  Fire Launcher 為有效 HOME（priority 50）。Phase 6QE exact-device metadata
  明確記錄未開 device node、未讀 driver data、未呼叫 Binder、未做 package/settings
  mutation、未 reboot、未 OTA/recovery、未 root/exploit。
- **HOME／package／component experiments：已做，但屬受控歷史 mutation**。
  Phase 3C／Phase 5／Phase 6 的 preferred HOME、候選 APK、Fire/Tahoe package 或
  component gate、force-stop、Settings GUI、child lifecycle 等均有 raw evidence；
  結果沒有閉合普通 shell／第三方 APK 到 User-0 Fire package-state writer 或 durable
  third-party HOME 的鏈。
- **Root：沒有成功取得**。`mtk-easy-su` APK 曾安裝／啟動；Root control 停在
  warning/preflight，沒有按 Accept、沒有 `su -c id`、沒有 UID 0、沒有 Magisk 或
  partition/root mutation。這是「前置流程曾執行、root transition 未執行／未證實」，
  不是 root proof。
- **Private Binder：沒有實際重做或成功呼叫**。`service list` 可見不代表 shell
  可取得 private handle；既有 `service check/find` denial 與 report 將未知 transaction
  列為風險拒絕。DPM/PM/KFT/Backup 的部分結果是既有受控或被 gate 拒絕的實驗，不能
  外推成 private Binder 可達。
- **Driver：只做過 metadata／policy／source review，沒有 open/ioctl**。現有證據
  可確認 node owner/label/SELinux metadata 與部分 exact-image policy；driver caller、
  active branch、ioctl effect、native handoff 仍是 UNKNOWN。
- **OTA／recovery／private updater：沒有人工執行**。repo 有 OTA APK、receiver、
  post-install、update-binary／block-image 的 static evidence，亦有 protected
  broadcast 或 partition writer；沒有 replay、crafted payload、recovery、partition
  write 或自然 OTA 後 runtime handoff 的完整觀測。
- **可安全重現的項目限 host-only／既有資料讀取**：SHA/schema/path 驗證、report-to-
  raw existence、保存 snapshot 比較、source-to-caller/policy/data-flow join、
  archive EOF/provenance review。需要 writer、user lifecycle、secure setting、
  Accessibility enable、unknown Binder、driver node、OTA/recovery、root 或 reboot
  才能產生新 runtime evidence 的項目，不可由本輪重做。

## 分類規則

| 分類 | 意義 |
|---|---|
| 已做 | 既有 raw output、result、manifest 或 report 足以證明該活動曾執行；不代表所有 caller/sink 已閉合。 |
| 未做 | repo 只保存 static/準備/negative boundary，沒有該 runtime action 的成功或完整觀測。 |
| 不可重做 | 既有活動需要狀態前提、自然 lifecycle 或不可安全回復的條件；本輪不重新觸發。 |
| 因風險拒絕 | report 明確列出未做，原因是 private Binder、driver、OTA/recovery、root、partition 或其他高影響操作。 |
| 引用缺口 | 既有結論存在，但缺 exact raw line、caller/UID、user scope、hash 對應或 post-state，不能升級結論。 |

## 主要引用與缺口

完整逐列資料見 [Phase 6SX CSV](./luna_worker_phase6sx_evidence_audit_20260810.csv)。
核心引用如下：

- 狀態與操作邊界：[README.md](../README.md)、[PROJECT_STATUS.md](../PROJECT_STATUS.md)。
- Phase 3A–3C：[phase-3a-report.md](../findings/phase-3a-report.md)、
  [phase-3b-report.md](../findings/phase-3b-report.md)、
  [phase-3c-report.md](../findings/phase-3c-report.md)。
- Phase 5 root 邊界：[phase-5-mtk-easy-su-apk-test.md](../findings/phase-5-mtk-easy-su-apk-test.md)、
  [phase-5-mtk-easy-su-root-test.md](../findings/phase-5-mtk-easy-su-root-test.md)、
  [phase-5-mtk-easy-su-root-followup.md](../findings/phase-5-mtk-easy-su-root-followup.md)。
- Phase 6QE/QF/RS–SQ：[phase-6qe-report.md](../findings/phase-6qe-report.md)、
  [phase-6qf-report.md](../findings/phase-6qf-report.md)、
  [phase-6rs-ru-report.md](../findings/phase-6rs-ru-report.md)、
  [phase-6rv-rx-report.md](../findings/phase-6rv-rx-report.md)、
  [phase-6sb-se-report.md](../findings/phase-6sb-se-report.md)、
  [phase-6sf-si-report.md](../findings/phase-6sf-si-report.md)、
  [phase-6sj-sm-report.md](../findings/phase-6sj-sm-report.md)、
  [phase-6sn-sq-report.md](../findings/phase-6sn-sq-report.md)。
- 已有 worker audit 作交叉索引：[Phase 6QF runtime audit](./luna_worker_phase6qf_existing_runtime_audit_20260810.md)、
  [Phase 6QE test catalog](./luna_worker_phase6qe_existing_tests_20260810.md)、
  [Phase 6SI test catalog](./luna_worker_phase6si_test_catalog_20260810.md)、
  [Phase 6SM test catalog](./luna_worker_phase6sm_test_catalog_20260810.md)、
  [Phase 6SQ HOME/PMS closure](./luna_worker_phase6sq_home_pms_writer_20260810.md)。

### Completeness 判定

目前可提交的結論是 bounded negative／evidence boundary：沒有保存證據閉合
ordinary app/shell → accepted privileged identity → User-0 HOME/package sink、
driver sensitive effect、OTA partition writer 或 root chain。主要引用缺口不是授權
去做高風險實驗的理由；它們只能透過 host-side source/caller join，或未來自然且
合法取得的 read-only snapshot 補足。

## 本輪交付

只新增：

1. `work/luna_worker_phase6sx_evidence_audit_20260810.md`
2. `work/luna_worker_phase6sx_evidence_audit_20260810.csv`

