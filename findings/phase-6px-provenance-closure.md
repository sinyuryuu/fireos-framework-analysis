# Phase 6PX — protected-package, OTA/OOBE and recovery provenance closure

日期：2026-08-10
公開基準：`a51db9cbb758785687312dc01888ebb9764140b2`
裝置 comparator：`G001LT0511550CFT` / KFTRWI / `trona` / PS7331

## Executive summary

本輪由三個 `luna_worker` 分別追蹤：

1. PackageManager deny-list 的資源來源與 Fire Launcher membership；
2. `BOOT_AFTER_SYSTEM_OTA` 的 protected-broadcast、system-server sender、receiver
   與 OOBE sink；
3. signed OTA/recovery verifier 到 native updater/partition writer 的 caller handoff。

**新的已證實結果：** PS7331 `fireos-res.apk` 的 raw resource
`amazon.fireos:raw/package_manager_deny_list` 明列 `com.amazon.firelauncher`。
這是 host artifact 的直接靜態 membership 證據，並與已觀察到的
`Cannot disable a protected package` 行為及 `ControlProtectedPackagesCallback`
資料流一致。

**仍須精確區分：** `/data/system/PackageManagerDenyList` 的 live persisted
內容受 system ACL 保護，本研究沒有讀取，因此「resource seed 包含 Fire」已證實，
「目前 persisted set 直接讀出 Fire」仍是未知；不能把兩者混為一談。

**未找到：** `BOOT_AFTER_SYSTEM_OTA` 普通 caller 路徑，或 shell/ordinary app
通往 signed updater/recovery handoff 的完整鏈。OTA/OOBE 仍是受信任 lifecycle，
不能當作可用的 Launcher replacement 或 Root 入口。

## Deny-list provenance

```text
PS7331 system image
  -> fireos-res.apk
  -> raw/package_manager_deny_list
  -> packages_deny_list includes com.amazon.firelauncher
  -> DenyListArcusHelper.processJSON()
  -> PackageManagerDenyList / DenyListKeyPackages
  -> ControlProtectedPackagesCallback
  -> PMS protected-package gate
  -> state mutation rejected before write
```

分類如下：

- **Confirmed static:** extracted JSON 直接包含 `com.amazon.firelauncher`；resource
  ID 與 `DenyListArcusHelper.processJSON()` 的 reader 對應。
- **Confirmed static:** callback 讀取 `DenyListKeyPackages`，並把 package flags、
  deny-list membership、caller UID 2000 等條件帶入 protected decision。
- **Confirmed runtime:** 既有 shell package/component disable 請求在 state write
  前回覆 `Cannot disable a protected package`，狀態不變。
- **Unknown:** live persisted set 的 literal contents，以及 Arcus refresh 後是否
  改變該 set；本輪不讀檔、不觸發 refresh、不改 property。
- **Not found in reviewed scope:** deny-list flow 本身沒有 Fire HOME resolver 或
  Fire restoration writer。

因此，Phase 6 的「Fire Launcher 如何進入 protected package 集合」現在可以
回答為：**量產 PS7331 的 framework resource seed 明列 Fire Launcher，並由
Amazon deny-list helper 載入/持久化到 PackageManager callback 使用的集合；
live set 內容仍未直接讀取。**

## BOOT_AFTER_SYSTEM_OTA provenance

保存的 source/data-flow 可閉合為：

```text
android.amazon.perm protected-broadcast declaration
  -> AmazonPackageManagerService.onBootPhase(550)
  -> PackageManagerService.isUpgrade()
  -> sendBroadcast(BOOT_AFTER_SYSTEM_OTA,
                   RECEIVE_BOOT_AFTER_SYSTEM_OTA)
  -> BootAfterSystemOTAReceiver + two Alexa consumers
  -> OobeHomeActivity / setup-state sinks
```

已證實它可以啟用 priority-100 的 OOBE Home component，並寫入
`user_setup_complete=0`、`isOOBEActive=1` 等 OOBE state；沒有在保存的
bounded source/data-flow 中找到普通 Fire Launcher preferred/HOME writer。
`sendBroadcast(..., permission)` 的 receiver-permission argument 不是單獨的
sender authentication；sender 仍受 system-server lifecycle 與 protected-broadcast
規則約束。receiver manifest 的 `uses-permission` 也不被誤作 receiver declaration
的 authentication。

**待驗證但不應人工補洞：** 自然官方 OTA 後的實際 delivery、numeric user scope、
OOBE component/settings timeline 與 Alexa side effects。人工 broadcast、手動啟用
OOBE component、設定寫入及 OTA replay 均不執行。

## OTA/recovery handoff

host-only evidence 可閉合 capability chain：

```text
OTA verifier / metadata checks
  -> basename staging
  -> UpdateSystem.install boundary
  -> recovery-accepted update-binary
  -> callback/block-image/cache helpers
  -> fixed by-name partition writers
```

但 caller chain 沒有閉合：

- verifier、signature/version/device/PVT checks 是 OTA app/recovery context；
- native `update-binary` 具備 extraction、block-image、`open/write/rename/chown`
  capability，但只證明受信任 updater capability；
- Java staging 的 `renameTo()` / copy fallback 與 path canonicalization 仍有
  bounded static unknown；沒有用 crafted path、symlink 或 traversal input 測試；
- 沒有 shell/ordinary app→recovery/updater 的合法 caller evidence。

判定：**因風險拒絕實機測試**。不執行 updater/recovery、異常 OTA、symlink payload、
partition write、flash 或 reboot。

## Current runtime comparator

最新安全 capture `adb/phase6pw/PHASE6PW-READONLY-20260810-01/` 與本輪唯讀
核對一致：User 0 HOME 仍為 `com.amazon.firelauncher/.Launcher` priority 50，
Microsoft candidate 為 priority 0；shell UID 2000、SELinux Enforcing。這只是
current comparator，不是 OTA/OOBE 已發生的證據。

## Final classification

| 問題 | 判定 |
|---|---|
| Fire Launcher 是否在 Amazon protected seed 中？ | **已證實（host static resource）** |
| live persisted deny-list 是否直接讀出 Fire？ | **未知** |
| deny-list 是否是 HOME resolver writer？ | **未找到；它是 package-state protection gate** |
| `BOOT_AFTER_SYSTEM_OTA` 是否普通 caller 可觸發？ | **未證實；高可信 lifecycle-bound** |
| OTA updater 是否可由 shell/ordinary app 呼叫？ | **未證實；caller handoff unknown** |
| User 0 是否取得正式第三方 HOME？ | **否；目前仍 Fire** |
| 是否找到新的無 Root Fire Launcher disable/HOME replacement？ | **否** |

## Reproducibility

33-row normalized matrix：`output/tables/phase6px-provenance-closure.csv`；
input hashes 與安全旗標：同名 `.manifest.json`。產生器
`tools/scripts/build_phase6px_provenance_closure.py` 只讀 worker CSV，不接觸
裝置或執行任何 privileged operation。

