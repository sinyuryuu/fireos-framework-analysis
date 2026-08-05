# Phase 6AG：`BootAfterSystemOTAReceiver` 正式研究項目登錄

## 定位

本文件不是新的裝置能力宣稱，也不是新的 OOBE／OTA 測試結果。它把既有
Phase 6Q、6AC、6AD、6Z 的結果登錄成正式 backlog item：

> **HIGH_RISK_LIFECYCLE_ENTRY / STATIC_ONLY / NOT_ADOPTABLE**

`BootAfterSystemOTAReceiver` 是合法 system-server post-OTA lifecycle 的
OOBE／setup state surface。它可能啟用 priority-100 的 OOBE Home activity，
但目前沒有證據顯示它是普通 shell 可寫的 HOME selector、Fire Launcher
replacement 或 root route。

## 已證實

1. `AmazonPackageManagerService.onBootPhase(I)` 在 phase 550 且
   `PackageManagerService.isUpgrade()` 成立時，建立
   `amazon.intent.action.BOOT_AFTER_SYSTEM_OTA`，並以
   `com.amazon.permission.RECEIVE_BOOT_AFTER_SYSTEM_OTA` 發送。
2. `android.amazon.perm.apk` 的 manifest 宣告該 action 為
   `protected-broadcast`；同一來源宣告接收 permission，設備 package dump
   顯示 protection 為 `signature|amazon`、source UID 1000。
3. `BootAfterSystemOTAReceiver` 在 action、OOBE-running、demo-mode 與偏好狀態
   條件成立時，會進入 incremental flow，啟用 `OobeHomeActivity` 並呼叫
   `OOBEActivationHelper.activateOOBEIF()`。
4. `OOBEActivationHelper` 的 incremental flow 會寫入
   `user_setup_complete=0` 與 `isOOBEActive=1`；這不是普通 preferred
   activity 寫入。
5. `OobeHomeActivity` 宣告 `MAIN + SETUP_WIZARD + HOME + DEFAULT`、priority
   100，但保存的 User 0 baseline 將該 component 設為 disabled。
6. 同一 action 還有兩個 Alexa consumer，故它不是單一 launcher 事件。

## 證據鏈

```text
system_server phase 550 + PMS.isUpgrade()
  -> Intent(BOOT_AFTER_SYSTEM_OTA)
  -> protected-broadcast / signature|amazon permission
  -> BootAfterSystemOTAReceiver.onReceive()
  -> enable OobeHomeActivity
  -> activateOOBEIF()
     -> user_setup_complete=0
     -> isOOBEActive=1
```

主要來源與雜湊列在 `findings/phase-6ag-evidence-index.md`；既有 machine-
generated CFG 與 inventory 不被本文件複製或覆寫。

## 尚未閉合

| 問題 | 分級 | 最小安全研究目標 |
|---|---|---|
| 完整 runtime `mProtectedBroadcasts` 是否還有其他來源 | 待驗證 | 對匹配版本保存 manifests 做 host-only inventory |
| 自然官方 OTA 後 receiver、OOBE component、ATM/HOME 的時間順序 | 待驗證 | 研究者正常完成官方 OTA 後只讀收集 log/dumpsys |
| OOBE Home 啟用後由 resolver、明確 task 還是 callback 啟動 | 待驗證 | host-only call-site mapping；或自然事件事後觀察 |
| action 是否能由 shell 合法觸發 | 已排除目前安全路徑／不可採用 | 不重播 broadcast；維持 permission/caller closure |
| 是否是 root 或正式 HOME replacement | 已排除目前證據支持 | 不再把 OOBE state side effect 當成 launcher workaround |

## 安全邊界

本項目禁止：手動 `am broadcast`／`cmd activity broadcast`、enable OOBE
component、修改 `user_setup_complete`／`isOOBEActive`、清除 OOBE data、
呼叫 OTA Binder、執行 updater/recovery、crafted OTA、未知 Binder
transaction、partition write、reboot-to-test 或任何可能需要 factory reset
的操作。

允許的後續只有：

- 主機端反編譯、manifest、VDEX／AOSP 差異分析；
- 自然完成官方 OTA 之後的唯讀觀察；
- 保存證據的雜湊與報告產生。

## 最終判定

**已證實：** 這是高影響的 OTA/OOBE lifecycle entry，具 setup 與潛在 HOME
side effect。

**高可信推論：** 它的控制權在受保護的 system-server OTA lifecycle，而不是
普通 shell 可寫設定。

**因風險拒絕測試：** 任何主動觸發或模擬該 lifecycle 的操作。

**目前結論：** 正式納入研究項目，但不納入 launcher workaround、root 或
可操作控制面的候選集合。

## 既有可重現來源

- `findings/phase-6q-bootafter-system-ota.md`
- `findings/phase-6ac-protected-broadcast-source.md`
- `findings/phase-6ad-protected-broadcast-inventory.md`
- `findings/phase-6z-boot-after-system-ota-follow-up.md`
- `tools/scripts/audit_phase6q_ota_oobe.py`
- `tools/scripts/audit_phase6ac_android_amazon_perm.py`
- `tools/scripts/audit_phase6ac_protected_broadcast_inventory.py`
- `artifacts/phase6u/bootafter-ota-scope-20260805-01/`
- `artifacts/phase6ac/protected-broadcast-source-audit-20260805-02/`
- `artifacts/phase6ad/protected-broadcast-inventory-20260805-01/`
