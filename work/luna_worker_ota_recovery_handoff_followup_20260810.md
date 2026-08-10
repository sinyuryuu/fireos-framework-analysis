# OTA/recovery handoff follow-up（host-only）

日期：2026-08-10 ；公開基準：`a51db9cbb758785687312dc01888ebb9764140b2`

本次只整理既有主機端靜態 artifact 與既有測試結果，未接觸裝置，未執行
OTA、recovery、updater、flash、reboot、partition、symlink/traversal payload、
root 或 exploit。Phase 6KU/6MD/6MM/6NE/6MI/PV/PW 的重複結果已合併；完整欄位
表在 [CSV](./luna_worker_ota_recovery_handoff_followup_20260810.csv)。

## 結論

PS7331 signed OTA 的靜態 capability 鏈可閉合到：

```text
OTA app verifier
  -> metadata/device/signature checks
  -> basename-based staging
  -> UpdateSystem.install boundary
  -> recovery-accepted native update-binary
  -> callback/block-image/cache helpers
  -> open/write/rename/chown and fixed by-name targets
```

但 caller reachability 沒有閉合：現有 Java 證據只證明驗證與 staging 的 source
flow；native artifact 只證明高權限 extraction/block-image/partition-writer
capability。沒有證據顯示 shell 或 ordinary app 能合法把輸入送進 recovery-to-
updater handoff。可寫 staging 也不是 ordinary-app 入口：目前只看到 OTA app 的
`SideloadMover`/`FileHelper` path，且 native/recovery 的 flags、SELinux context、
canonicalization 與 atomicity 仍未完整解析。

## 分層判定

- **Capability：** `update-binary` 註冊 24 個 install callback；block-image
  registration 的 5 個 handler 已由 Phase 6MM 對上 function symbols。direct-BL
  evidence 連到 `ota_open -> open`、`ota_write -> write`、`rename`、`chown`，而
  官方 script 使用 system/vendor/boot、preloader/LK/TEE 與多個 firmware
  `by-name` 目標。這是 recovery/high-privilege capability。
- **Verifier/metadata：** `OSUpdateValidator`/`SideloadVerifier` 先走 hash、
  recovery verification、版本/signature transition、product/device/PVT checks。
  `RecoverySystemWrapper` 是 delegation，不是 verifier implementation；平台
  recovery verifier 與 native handoff provenance 未在保存 slice 中出現。
- **Staging：** `SideloadMover` 只取 basename，移到 OTA external-data directory；
  `FileHelper` 先 `renameTo()`，失敗才 copy + source delete，copy 使用
  `FileOutputStream`。Java source 未見 canonicalization marker，但這是 bounded
  unknown，不足以推論 traversal/symlink bypass。
- **Caller：** 既有 ordinary-app IPC evidence（prewarm、KFT tx3）與 native OTA
  capability 是不同類型證據。prewarm 只有 process/resource sink；KFT tx3 在
  standard PMS cross-user/component gate 被拒，兩者都沒有 recovery/updater
  handoff。Phase 6PW 的既有唯讀狀態仍是 User 0 Fire Launcher priority 50，沒有
  新的 OTA caller 證據。
- **Source negative control：** Phase 6MI 的 PS7331 source tar 已讀到真實 EOF，
  35 members、無 symlink/hardlink，且沒有 `META-INF`、`update-binary`、
  `updater-script` 或 partition member；它不是隱藏 OTA 入口。

## 安全後續

只做 host-only：補齊平台 recovery verifier → certificate/AVB → native updater
的 artifact/caller provenance，以及 selected binary 之外的 indirect CFG/dataflow
與 staging flags/context。不得以執行 updater/recovery、crafted OTA、symlink/
traversal collision、private Binder、裝置寫入或 partition test 來補洞。

