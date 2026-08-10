# Phase 6TR：既有測試與結果 reconciliation

日期：2026-08-10（Asia/Taipei）  
範圍：Phase 3A–6TM；只讀目前 git tree、`findings/`、`adb/` raw/summary、`output/tables/`、`scripts/` 與既有 worker catalog。

本輪沒有執行 adb、沒有連接或修改裝置、沒有 reboot、沒有發送 Binder/driver/OTA/recovery payload，沒有修改既有報告或原始證據，也沒有新增 exploit。逐列矩陣見 [CSV](./luna_worker_phase6tr_test_reconciliation_20260810.csv)；CSV SHA-256：`04c49baf1fd96f32a5497022d43486b6651f4f1a0656c46ab52f4786cf728cd3`。

## Reconciliation 結論

- 已完成的既有測試可支持 bounded negative、受控 mutation 結果或 static boundary；沒有證據閉合 `ordinary app/shell → accepted privileged identity → User-0 HOME/package/root/partition sink`。
- 已確認的 mutation 路線包括 Phase 3C preferred HOME、Phase 4B/5 accessibility、Phase 5 package/OTA 邊界與 Phase 6 child/KFT、package/HOME、DPM/UI 等受控活動。其 restore/final guard 與必要的 reboot 觀察均只代表該次 build/user/state 的保存結果，不是可安全重播授權。
- 已完成的 host-only/static 路線包括 Phase 5 low-level/CVE/OTA source review、Phase 6 OTA/OOBE/updater、PMS/package-state/driver policy，以及 Phase 6TM-A H2、6TM-B ION loader、6TM-C OTA citation repair。靜態 declaration、permission、ELF edge、policy 或 updater writer 不等於 live caller、Binder reachability、runtime load 或 sink effect。
- 6TM-A 確認 H2 custom `BIND_SERVICE` 是 `signature` gate；custom holder/grant 與 external production caller 未確認，沒有 H2→HOME/package sink 證據。
- 6TM-B 確認若干 ION library/policy edges；service implementation load、process/domain ownership、`/dev/ion` runtime access 與 sensitive effect 未 join 完成。
- 6TM-C 修正 OTA citation/hash scope：official mapping 與 committed static records 可驗證；raw OTA、raw extracted `update-binary` 等路徑仍按 local-only/derived/public scope 分類，沒有 OTA execution 或 partition sink 證據。

## Mutation、restore、reboot 狀態規則

CSV 的 `mutation` 與 `restore_reboot_state` 欄位按以下規則解讀：

- `none`：該列在保存 corpus 中是 host-only/read-only；不表示裝置從未在其他相位被改動。
- `yes historical` 或 `historical bounded`：既有 run 曾有 package、HOME、Accessibility、profile/user 或 GUI 狀態變化；只接受保存的 before/after/rollback/final guard，不重做。
- `reboot observed`：既有證據包含 reboot 前後觀察；不表示本輪 reboot，也不表示 reboot-time writer 已找到。
- `no runtime replay`：即使已有 rollback，也不把它列為可安全重測；需要狀態變更、自然 lifecycle、使用者同意或高影響 writer 的路徑均排除。

## 重複與已排除路線

已標為 canonical/duplicate 或 excluded 的路線：

- HOME resolver、foreground、service visibility、Fire package state、rollback/final guards 的重複 captures；只保留一個相同 build/state 的 canonical evidence set。
- child/KFT/Tahoe/User-11、GUI profile switch、child PIN，以及 tx3 或等價 private transaction；既有結果只閉合 child scope，不是 User-0 writer。
- priority APK、ordinary `set-home`、preferred/force-stop、Fire disable/hide/suspend/uninstall/component mutation 的重測。
- Accessibility isolation/redirect、PendingIntent signing variant、未知 Amazon Binder transaction、driver open/ioctl、OOBE/OTA broadcast/replay、recovery/updater/partition、root/exploit/bootloader 路線。

「排除」是安全或重複分類，不是對未執行操作的漏洞不存在證明；CSV 保留這個 distinction。

## 仍缺的 caller→gate→sink 證據

目前最重要的缺口如下：

1. User-0 Fire restoration writer 的完整 production caller、UID/identity、user scope 與實際 package/HOME sink。
2. KFT tx3 的合法 production caller/provenance，以及 child-scoped writer 之外是否存在 User-0 side effect。
3. H2 custom `BIND_SERVICE` 的 owner、grant、requesting package/signature、Binder caller identity 與 downstream user/profile sink。
4. ION/native graph 的實際 process load、SELinux/domain/client、`/dev/ion` open/ioctl gate 與 sensitive effect。
5. OOBE/`BOOT_AFTER_SYSTEM_OTA` 的 exact numeric delivered user、自然 official OTA 後 handoff，以及 updater/fosinit caller-to-partition chain。
6. 完整 production caller universe、Vending/privapp grant provenance、native alias/decompiler gaps；這些不能由 service list、permission declaration、UID 或 static sink 單獨補出。

## 可安全重現的唯讀檢查

只建議在 host 上對既有檔案執行：

- path/existence、CSV schema、manifest 與 SHA-256 verification；分開 raw input hash、derived artifact hash、Git blob hash 與 output hash scope。
- report-to-raw/table-to-summary 引用完整性、before/after/rollback/final guard 對應檢查。
- 已保存的 device properties、user/package/HOME、service list/check/find、SELinux label/policy snapshot 比較；不取新的 device snapshot。
- 已保存 source/CFG/ELF/manifest 的 caller→gate→identity/user→sink join、H2 permission-owner search、ION DT_NEEDED/relocation graph、OTA archive EOF/provenance review。

任何 script 若預設會呼叫 adb、寫入 device、啟動 package、改 secure setting、發 Binder/driver/OTA payload 或 reboot，不能以「重測」名義執行；可重測性僅限其純 host-side parser、dry-run 或離線 hash/schema 模式。

## 證據與信心

每列均在 CSV 附有 evidence path 與 hash scope。`high` 表示保存的 raw、manifest、finding 或多個獨立 static artifact 足以支持該列的 bounded claim；不表示 caller/sink gap 已不存在。`medium` 僅用於 Phase 4A model scope。既有 source catalog 的 aggregate hash 不替代各 raw 檔案 hash，也不把 manifest hash 當作 runtime causality proof。
