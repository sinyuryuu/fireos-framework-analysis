# Phase 6NF：IPC／KFT／OTA 證據整合

日期：2026-08-10  
範圍：整理兩份 `luna_worker` 只讀 inventory、既有 Phase 6 證據，以及
Phase 6NE host-only updater closure。未執行新的裝置變更。

## Executive result

目前沒有新的安全、可逆、低權限路徑能在 User 0 停用或替代
`com.amazon.firelauncher`。最接近的兩條高權限路徑分別是：

- KFT child lifecycle：可對傳入的 `UserInfo.id` 寫入 Fire/Tahoe/Launcher3
  component state，但保存的 runtime attribution 是 User 10；不是 User 0
  HOME selector。
- OTA/recovery updater：具備抽取檔案與 named-partition write capability，但
  未建立 shell／ordinary-app caller，也沒有執行 recovery、updater 或 OTA。

## 已證實

| Finding | 證據 | 信心度 |
|---|---|---|
| KFT tx3 是 child/profile-scoped trusted writer | `LUNA-KFT-STATIC-001`、`LUNA-KFT-RUNTIME-001`，詳見 [`luna_worker_ipc_kft_inventory_20260810.md`](../work/luna_worker_ipc_kft_inventory_20260810.md) | Confirmed |
| User 0 Fire state 沒有新的低權限 writer | `LUNA-PMS-GATE-001`、`LUNA-SHELL-REACH-001`、`LUNA-AMZ-PM-001` | Strong evidence |
| Amazon private PackageManager surface 沒有 formal HOME/package-state setter | `LUNA-AMZ-PM-001` | Confirmed, bounded |
| OOBE/BootAfterSystemOTA 是受保護的 lifecycle path，不是普通 HOME API | `6Q-OOBE-001..002`、`6R-OOBE-001..010`、`6MY-001` | Confirmed, bounded |
| updater 具備高權限 capability，但 reachability 未建立 | `6P-OTA-001..004`、`6KT-001`、`6MK-001` | Strong evidence |
| cache-size decision flow 已由 Phase 6NE 閉合到 selected direct edges | `6NE-CACHE-001..004` | Confirmed, scope-limited |
| 官方 PS7331 Image 沒有觀察到 `amzn_drv_test` 的 unique literals | Phase 6ND report/artifact | Strong bounded negative |

## 高可信推論

`KFTUserManager`、Amazon package metadata service、OOBE receiver 與 native OTA
updater 不應被合併成一條「shell 可呼叫的 launcher replacement chain」：它們的
user scope、permission、service publication、lifecycle trigger 與 privilege
boundary 不同。現有資料支持「child lifecycle writer」與「recovery capability」
兩個分離的控制面，而不是 User 0 的通用 confused deputy。

## 已排除／不應重複

- User 0 Fire 的普通 `pm`／`cmd package` enabled-state mutation。
- 普通 `set-home-activity` 與相同 priority/priority-cap 測試。
- KFT tx3 replay、private Binder parcel guessing、service injection。
- OOBE protected broadcast replay、OTA/recovery/updater 執行、crafted/symlink OTA。
- Fire Launcher disable/hide/suspend/uninstall/clear-data。

## 尚未閉合

1. KFT tx3 完整 caller provenance、authorization 與 `UserInfo.id` data-flow。
2. Home callback return/data-flow 是否能改寫最終 component；目前沒有直接證據。
3. recovery verifier 到 native updater 的完整 handoff；不能以真機 OTA 補足。
4. `MakeFreeSpaceOnCache` 的所有 indirect callers 與不透明 function-pointer data-flow。

這些都可先做主機端靜態分析；若只能靠 recovery、partition write、Root 或未知
Binder transaction 才能繼續，該路徑應列為「因風險拒絕測試」。

## Worker provenance

| Worker report | SHA-256 |
|---|---|
| `work/luna_worker_ipc_kft_inventory_20260810.md` | `44939b46b18131ae446bc765b05f0789d1a51acc74b67be92db0e35721274537` |
| `work/luna_worker_ota_inventory_20260810.md` | `25922c6658e9fcdcdb6fe1753af6805611ae62deb05863ae5f14e2f74e3bf764` |

## 安全狀態

本輪未連接設備、未使用密碼、未發送 Binder/service call、未讀寫 driver/ioctl
node、未執行 OTA/Recovery/updater、未 reboot、未 root，且未改變 Fire Launcher
狀態。原始 worker 報告與 Phase 6NE artifact 均保留。
