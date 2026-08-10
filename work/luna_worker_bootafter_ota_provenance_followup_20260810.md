# BOOT_AFTER_SYSTEM_OTA provenance follow-up — 2026-08-10

公開基準：`a51db9cbb758785687312dc01888ebb9764140b2`。本輸出只做 host-only 靜態搜尋與既有 artifact 整理；沒有執行 adb、broadcast、activity/settings mutation、Binder transaction、OTA/recovery、root/exploit、reboot 或 partition 操作。

## 結論

保存證據閉合了這條靜態鏈：

```text
android.amazon.perm protected-broadcast declaration
  -> AmazonPackageManagerService.onBootPhase(550)
  -> PMS.isUpgrade()
  -> sendBroadcast(BOOT_AFTER_SYSTEM_OTA, RECEIVE_BOOT_AFTER_SYSTEM_OTA)
  -> BootAfterSystemOTAReceiver + two Alexa consumers
  -> OOBE component/settings sinks
```

`BootAfterSystemOTAReceiver` 的 sink 是啟用 `OobeHomeActivity` 及寫入 OOBE setup state；沒有在保存的 bounded source/dataflow 中找到普通 Fire Launcher preferred/HOME writer。`OobeHomeActivity` 目前為 User 0 disabled，Phase 6PV/6PW 保存的唯讀基線仍解析 `com.amazon.firelauncher/.Launcher` priority 50。

這不支持「普通 caller 可觸發」。`sendBroadcast(..., permission)` 的 receiver-permission argument 不單獨證明 sender authorization；真正 sender 還受 system-server lifecycle 與 protected-broadcast gate 約束。也沒有把 receiver manifest 的 `uses-permission` 誤寫成 receiver declaration authentication。

## Phase 去重對照

| Phase | 保留的 provenance | 去重判定 | 缺少的 runtime evidence |
|---|---|---|---|
| 6Q | sender phase 550 + `isUpgrade`、OOBE receiver、OOBE HOME baseline | 核心 source/sink | 自然 OTA 的 delivery、settings/component timeline |
| 6R | protected-broadcast authorization correction、兩個 Alexa consumers | 補 authorization 語意，不重複 sender | 完整 runtime `mProtectedBroadcasts` 與自然 delivery |
| 6U | 安全 scope register、明確禁止 replay | scope/negative boundary | 官方 OTA 後實際 resolver/user timeline |
| 6MY | `PackageHelper.setComponentEnabledSetting` 與 OOBE-only sink | component edge closure | exact runtime user/component transition |
| 6NI | SystemServer context 建立、`ContextImpl.mUser` 傳播 | system-context provenance | exact delivered numeric user |
| 6PV | broad route normalized closure | 只保留 OOBE lifecycle cross-reference | 未新增 OTA runtime evidence |
| 6PW | broad privilege/current read-only HOME baseline | 只保留 Fire comparator；不引入新 OTA edge | 未發生 OTA/OOBE event |

## 保存 evidence

詳細 machine-readable edge matrix 在 [CSV](luna_worker_bootafter_ota_provenance_followup_20260810.csv)。主要 source/hash：

- system-server sender：`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` — `ecbe62fe…151c`
- OOBE receiver：`BootAfterSystemOTAReceiver.java` — `c29b32bf…cb90`
- protected source APK inventory：Phase 6AC `manifest-aapt.xmltree.txt` — `89e141fb…efed`
- OOBE component/settings：Phase 6MY/6MO normalized tables — `1136d481…07c52`, `a35623b…2484b`
- system-context scope：Phase 6NI `evidence.csv` — `df647a49…6996a`
- current comparison only: Phase 6PV/6PW normalized outputs — `25ab02e4…0ba49`, `d79ec8eb…9968b`

## Runtime evidence gap and safe next step

目前缺少的不是「再發一次 action」；缺少的是自然官方 OTA 後的唯讀 observation：實際 broadcast delivery、數字 user scope、OOBE component state、`user_setup_complete`/`isOOBEActive`、Alexa consumer side effects 與 HOME resolver 時序。下一步只能是 host-only exact-build protected-broadcast inventory，或在自然官方 OTA 已發生後做 read-only capture。不得人工 broadcast、改設定/元件、執行 OTA/recovery 或做 Binder replay。

狀態標籤在 CSV 中區分 `CONFIRMED_STATIC`、`STRONG_STATIC_CONTEXT`、`CURRENT_READONLY_BASELINE` 與 `DEDUPLICATED`；任何 `待驗證` 均不等同已否定，也不等同普通 caller 可達。
