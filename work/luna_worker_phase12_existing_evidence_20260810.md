# Phase 12 — existing evidence index (host-only, read-only)

日期：2026-08-10

## Scope and safety

本輪只在主機端讀取既有 `findings/`、`adb/`、`artifacts/`、`logs/`、`output/` 與 `work/` 檔案，並執行 `pwd`、`git rev-parse HEAD`、`git status`、`rg`、`sed`、`sha256sum -c`。未執行 adb、裝置修改、root、exploit、未知 Binder transaction、driver open/ioctl、OTA/recovery。未修改既有檔案，未 commit/push。

確認環境：

- `pwd`: `/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire`
- `git HEAD`: `aeb8709519ab4c4cb5b9fc3e835f5cf30a9f5568`
- 工作樹原已有大量 modified/untracked 檔案；本輪只新增本報告的 `.md` 與 `.csv`。

## Reading rule

下表的 `Confirmed` 僅表示檔案中有直接觀察或靜態結構已被保存；`Strong evidence` 表示證據強但仍有 caller/user/consumer 缺口；`Unknown` 保留未閉合欄位；`Disproved` 只否定所述廣泛路徑，不否定較窄的 source capability。報告、候選 caller、generated Proxy/Stub 或 source capability 沒有被升級成 runtime fact。

完整逐列索引在 [CSV](./luna_worker_phase12_existing_evidence_20260810.csv)。

## Findings by requested area

### KFT / child user

`9B-001` 是保存 corpus 中最清楚的 KFT 語義 caller edge：`createChildUser` 產生 child `UserInfo`，再送 `enableKftLauncher` tx3；writer 使用傳入 `UserInfo.id`，沒有固定 User 0 或 formal HOME setter。external APK package、UID、signature 與 tx3 method-local authorization 仍未知。`CHILD-TEST-20260805-01` 是歷史 UI/child-profile 測試；其 final guard 保存 User 0、Fire HOME 與 activity 狀態，但不能代替 tx3 invocation attribution，也不能當成普通 User-0 HOME route。

### DPM / profile

`10B-DPM-001` 的保存靜態分析顯示 calling UID、`MANAGE_USERS`/owner checks 與 DPM/UserManager policy sink；`PHASE10-BASELINE` 則直接保存 User 0 `com.amazon.parentalcontrols` 與 User 10 `com.amazon.tahoe` Profile Owner。這確認 profile-owner/policy 狀態與固定 policy sink，但沒有證明普通 caller 可藉此改 HOME 或 Amazon package state。`10B-PARENT-001` 同樣只支持固定輸入的 Profile Owner 能力。

### Amazon PM / package-state

`10A-PM-001` 與 `P9D-001` 確認 `setAmazonFlagsForUser` 等 Amazon metadata/flags writer 的靜態 sink 與 permission gate；caller、實際 grant、userId provenance、第一個敏感 consumer 未閉合。Phase 10 baseline 的 User 0 HOME 是 Fire Launcher priority 50，不能由 package-state writer 靜態推論出 HOME 變更。

### HOME / Accessibility

Phase 10 baseline 保存 User 0 `com.amazon.firelauncher/.Launcher` priority 50、User 10 `FallbackHome` priority -1000。Phase 11 T01/T02 的實際保存結果均是 foreground 與 formal HOME 不變、redirect package 未出現；T02 僅顯示 service 在 HOME 前及 poll 1 存在。兩次結果分類都是「foreground redirect observation only; formal HOME is not changed」，因此 Accessibility/ADB 行為不是 durable HOME replacement。

### OTA / OOBE

`10C-001/002` 保留 BOOT_AFTER_SYSTEM_OTA receiver、phase-550、upgrade/protected gate 與 OOBE/settings helper 的靜態 sink；沒有 post-OTA runtime effect。`10C-003/008` 保留 OTA controller/install/recovery handoff 的 signature|privileged 邊界與 capability，但沒有執行 transaction、install、recovery 或 partition write。`10C-012` 的 negative boundary 只表示保存 corpus 沒有普通 APK/shell 到 privileged OTA sink 的完整 caller chain。

### Kernel / driver

`10D2-001/003/004/010` 及 Phase 7C source/config index 列出 CMDQ、M4U、uinput、RPMB 等 source/config surfaces；共同觀察是未找到 exact shipped opener、UID/domain、node label/TE allow 與 end-to-end package/HOME sink。這些列保持 `Unknown`，不把 Kconfig/source capability 寫成 retail reachability，也未執行任何 driver open/ioctl。

## Phase 9–11 disposition

- Phase 9：KFT client identity、DCPMS residual IPC、Amazon PM broad surface；以 host-side static/data-flow evidence 為主，caller/user/consumer 缺口保留。
- Phase 10：Package Manager、DPM/profile、OTA/post-install、driver caller closure，以及保存的唯讀 baseline；baseline 的四個 manifest（Phase 10、Phase 11 T01/T02、CHILD-TEST-20260805-01）已在主機端用 `sha256sum -c` 驗證。
- Phase 11：兩個 Accessibility live test 只作既有結果索引；本輪沒有重播。其結果一致支持「foreground fallback/redirect observation」，不支持 formal HOME replacement。

## Hash status

`hash_verified=yes` 僅用於本輪實際以既有 manifest 執行 `sha256sum -c` 並通過的檔案集合。Phase 9/10 靜態 CSV 中的 `evidence_sha256` 多數是已列出的來源雜湊，但本輪未對每一個大型 disassembly/source artifact 逐一重算，因此 CSV 明確標成「evidence hash listed; not rehashed」。CHILD-TEST manifest 的前綴路徑需從 workspace root 驗證，已通過；從其子目錄執行會因路徑前綴而產生假性找不到，未把該現象誤報成 evidence 損壞。

## Open gaps

主要未閉合項目是 exact production caller/package/UID/signature、service-manager/SELinux tuple、cross-user/userId provenance、KFT fresh runtime attribution、OTA natural lifecycle/AVB handoff、driver final node/object/policy/native caller，以及 persistence across reboot/build。這些缺口不應以重新執行被禁止的 route 填補。
